import json
from collections import defaultdict

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from loguru import logger
from universal_mcp.tools.registry import ToolRegistry
from universal_mcp.types import ToolConfig

from universal_mcp.agents.base import BaseAgent
from universal_mcp.agents.builder.prompts import (
    AGENT_BUILDER_INSTRUCTIONS,
    AGENT_FROM_CONVERSATION_PROMPT,
    TASK_SYNTHESIS_PROMPT,
)
from universal_mcp.agents.builder.state import Agent, BuilderState
from universal_mcp.agents.llm import load_chat_model
from universal_mcp.agents.shared.tool_node import build_tool_node_graph


async def generate_agent(llm: BaseChatModel, task: str, old_agent: Agent | None = None) -> Agent:
    """Generates an agent from a task, optionally modifying an existing one."""
    prompt_parts = [AGENT_BUILDER_INSTRUCTIONS]
    if old_agent:
        prompt_parts.append(
            "\nThe user wants to modify the following agent design. "
            "Incorporate their feedback into a new design.\n\n"
            f"**User Feedback:** {task}\n\n"
            f"{old_agent.model_dump_json(indent=2)}"
        )
    else:
        prompt_parts.append(f"\n\n**Task:** {task}")

    prompt = "\n".join(prompt_parts)
    structured_llm = llm.with_structured_output(Agent)
    agent = await structured_llm.ainvoke(prompt)
    return agent


class BuilderAgent(BaseAgent):
    def __init__(
        self,
        name: str,
        instructions: str,
        model: str,
        registry: ToolRegistry,
        memory: BaseCheckpointSaver | None = None,
        **kwargs,
    ):
        super().__init__(
            name=name,
            instructions=instructions,
            model=model,
            memory=memory,
            **kwargs,
        )
        self.registry = registry
        self.llm: BaseChatModel = load_chat_model(model, thinking=False)

    def _entry_point_router(self, state: BuilderState):
        """
        Determines the entry point of the graph based on the input format and conversation history.
        - If input is a JSON with 'conversation_history', it builds from the conversation.
        - If an agent has already been generated, it assumes a modification is requested.
        - Otherwise, it starts a fresh build from a text prompt.
        """
        last_message_content = state["messages"][-1].content
        try:
            # Case 1: Input is a JSON for building from a conversation
            payload = json.loads(last_message_content)
            if isinstance(payload, dict) and "conversation_history" in payload and "tool_config" in payload:
                logger.info("Routing to: build from conversation history.")
                return "synthesize_from_conversation"
        except (json.JSONDecodeError, TypeError):
            # Input is not a valid JSON, proceed as an interactive build
            pass

        # Case 2: It's an interactive build, check for modification vs. new
        if state.get("generated_agent"):
            logger.info("Routing to: modify existing agent.")
            return "synthesize_new_task"
        else:
            logger.info("Routing to: new agent build.")
            return "prepare_for_build"

    async def _prepare_for_build(self, state: BuilderState):
        """Sets the initial user task to begin the build process."""
        last_message = state["messages"][-1]
        task = last_message.content
        yield {
            "user_task": task,
        }

    async def _create_agent(self, state: BuilderState):
        """Creates or updates the agent definition from a user_task."""
        task = state["user_task"]
        agent = state.get("generated_agent")

        generated_agent = await generate_agent(self.llm, task, agent)
        yield {
            "generated_agent": generated_agent,
        }

    async def _get_tool_config_for_task(self, task: str) -> ToolConfig:
        """Helper method to find and configure tools for a given task string."""
        tool_finder_graph = build_tool_node_graph(self.llm, self.registry)
        initial_state = {
            "original_task": task,
            "decomposition_attempts": 0,
        }
        final_state = await tool_finder_graph.ainvoke(initial_state)
        execution_plan = final_state.get("execution_plan")

        if not execution_plan:
            return {}

        apps_with_tools = defaultdict(list)
        for step in execution_plan:
            app_id = step.get("app_id")
            tool_ids = step.get("tool_ids")
            if app_id and tool_ids:
                apps_with_tools[app_id].extend(tool_ids)

        return {app_id: list(set(tools)) for app_id, tools in apps_with_tools.items()}

    async def _create_tool_config(self, state: BuilderState):
        """Creates the tool configuration for the agent."""
        task = state["user_task"]
        tool_config = await self._get_tool_config_for_task(task)
        yield {
            "tool_config": tool_config,
        }

    async def _synthesize_new_task_from_feedback(self, state: BuilderState):
        """Synthesizes a new user_task from the original task and subsequent user feedback."""
        original_task = next((msg.content for msg in state["messages"] if isinstance(msg, HumanMessage)), None)
        modification_request = state["messages"][-1].content

        if not original_task:
            raise ValueError("Could not find the original task in the conversation history.")

        synthesis_prompt = TASK_SYNTHESIS_PROMPT.format(
            original_task=original_task,
            modification_request=modification_request,
        )

        response = await self.llm.ainvoke(synthesis_prompt)
        new_synthesized_task = response.content.strip()
        logger.info(f"The new synthesized task is: {new_synthesized_task}")
        yield {
            "user_task": new_synthesized_task,
        }

    async def _synthesize_from_conversation(self, state: BuilderState):
        """
        Takes conversation history and used tools from input to synthesize a complete agent profile.
        This is a one-shot generation.
        """
        content_str = state["messages"][-1].content
        initial_input = json.loads(content_str)

        conversation_history = initial_input.get("conversation_history")
        tool_config = initial_input.get("tool_config")

        if not conversation_history or not tool_config:
            raise ValueError("Input must be a dictionary containing 'conversation_history' and 'tool_config'.")

        prompt = AGENT_FROM_CONVERSATION_PROMPT.format(
            conversation_history=json.dumps(conversation_history, indent=2),
            tool_config=json.dumps(tool_config, indent=2),
        )

        structured_llm = self.llm.with_structured_output(Agent)
        generated_agent_profile = await structured_llm.ainvoke(prompt)

        yield {
            "generated_agent": generated_agent_profile,
            "tool_config": tool_config,
            "messages": [
                AIMessage(
                    content=f"Successfully generated agent '{generated_agent_profile.name}' from the conversation history."
                )
            ],
        }

    async def _build_graph(self):
        """Builds the conversational agent graph."""
        builder = StateGraph(BuilderState)

        # Add nodes
        builder.add_node("prepare_for_build", self._prepare_for_build)
        builder.add_node("create_agent", self._create_agent)
        builder.add_node("create_tool_config", self._create_tool_config)
        builder.add_node("synthesize_new_task", self._synthesize_new_task_from_feedback)
        builder.add_node("synthesize_from_conversation", self._synthesize_from_conversation)

        # The conditional entry point decides the workflow
        builder.add_conditional_edges(
            START,
            self._entry_point_router,
            {
                "prepare_for_build": "prepare_for_build",
                "synthesize_new_task": "synthesize_new_task",
                "synthesize_from_conversation": "synthesize_from_conversation",
            },
        )

        # Path for a fresh interactive build
        builder.add_edge("prepare_for_build", "create_agent")
        builder.add_edge("prepare_for_build", "create_tool_config")

        # Path for modifying an existing build
        builder.add_edge("synthesize_new_task", "create_agent")
        builder.add_edge("synthesize_new_task", "create_tool_config")

        # Path for building from conversation ends after its single step
        builder.add_edge("synthesize_from_conversation", END)

        # Interactive creation nodes lead to the end of the run
        builder.add_edge("create_agent", END)
        builder.add_edge("create_tool_config", END)

        return builder.compile(checkpointer=self.memory)
