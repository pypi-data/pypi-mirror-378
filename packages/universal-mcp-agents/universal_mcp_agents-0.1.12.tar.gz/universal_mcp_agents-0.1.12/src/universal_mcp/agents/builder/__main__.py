import asyncio
import json
from uuid import uuid4

from langgraph.checkpoint.memory import MemorySaver
from loguru import logger
from universal_mcp.agentr.registry import AgentrRegistry

from universal_mcp.agents.builder.builder import BuilderAgent


async def run_interactive_build():
    """Simulates a multi-turn conversation to build and then modify an agent."""
    logger.info("--- SCENARIO 1: INTERACTIVE AGENT BUILD & MODIFY ---")

    registry = AgentrRegistry()
    memory = MemorySaver()
    agent = BuilderAgent(
        name="Builder Agent",
        instructions="You are a builder agent that creates other agents.",
        model="anthropic/claude-4-sonnet-20250514",
        registry=registry,
        memory=memory,
    )

    thread_id = str(uuid4())

    conversation_script = [
        "Send an email to manoj@agentr.dev with the subject 'Hello' and body 'This is a test of the Gmail agent.' from my Gmail account.",
        "Use outlook instead of gmail",
    ]

    final_result = {}
    for i, user_input in enumerate(conversation_script):
        logger.info(f"\n--- Conversation Turn {i + 1} ---")
        logger.info(f"User Request: '{user_input}'")

        result = await agent.invoke(user_input=user_input, thread_id=thread_id)
        final_result.update(result)  # Keep updating the final result

        generated_agent = final_result.get("generated_agent")
        tool_config = final_result.get("tool_config")

        if generated_agent:
            logger.info("--- Generated/Modified Agent ---")
            logger.info(f"Name: {generated_agent.name}")
            logger.info(f"Description: {generated_agent.description}")
            logger.info(f"Expertise: {generated_agent.expertise}")
            logger.info(f"Instructions:\n{generated_agent.instructions}")

        if tool_config:
            logger.info("--- Selected Tools ---")
            tools_str = "\n".join(f"- {app}: {', '.join(tool_ids)}" for app, tool_ids in tool_config.items())
            logger.info(tools_str)
        else:
            logger.info("--- Selected Tools ---")
            logger.info("No tools selected for this agent yet.")


async def run_conversation_build():
    """Simulates a one-shot agent build from a conversation history payload."""
    logger.info("\n\n--- SCENARIO 2: AGENT BUILD FROM CONVERSATION HISTORY ---")

    registry = AgentrRegistry()
    agent = BuilderAgent(
        name="Builder Agent",
        instructions="You build agents from conversation transcripts.",
        model="anthropic/claude-4-sonnet-20250514",
        registry=registry,
    )

    sample_conversation_history = [
        {
            "type": "human",
            "content": "Hey, can you look at our main branch on the universal-mcp repo and tell me what the last 3 pull requests were?",
        },
        {
            "type": "ai",
            "content": "Of course. The last 3 pull requests are: #101 'Fix login bug', #102 'Update documentation', and #103 'Add new chart component'.",
        },
        {
            "type": "human",
            "content": "Awesome, thanks. Now can you draft a new Google Doc and put that list in there for me?",
        },
        {"type": "ai", "content": "Done. I have created a new Google Doc with the list of the last 3 pull requests."},
    ]
    sample_tool_config = {"github": ["get_pull_requests"], "google_docs": ["create_document"]}
    wingman_payload = {"conversation_history": sample_conversation_history, "tool_config": sample_tool_config}

    logger.info(f"Payload Conversation History Length: {len(sample_conversation_history)} messages")
    logger.info(f"Payload Tools Provided: {list(sample_tool_config.keys())}")

    # The payload must be passed as a JSON string in the 'user_input'
    payload_str = json.dumps(wingman_payload)
    thread_id = str(uuid4())
    result = await agent.invoke(user_input=payload_str, thread_id=thread_id)

    generated_agent = result.get("generated_agent")
    tool_config = result.get("tool_config")

    if generated_agent:
        logger.info("\n--- Generated Agent Profile ---")
        logger.info(f"Name: {generated_agent.name}")
        logger.info(f"Description: {generated_agent.description}")
        logger.info(f"Expertise: {generated_agent.expertise}")
        logger.info(f"Instructions:\n{generated_agent.instructions}")
        logger.info(f"Schedule: {generated_agent.schedule}")
    else:
        logger.error("Error: Agent profile was not generated.")

    if tool_config:
        logger.info("--- Final Tool Configuration ---")
        tools_str = "\n".join(f"- {app}: {', '.join(tool_ids)}" for app, tool_ids in tool_config.items())
        logger.info(tools_str)
    else:
        logger.error("Error: Tool configuration is missing.")


async def main():
    await run_interactive_build()
    await run_conversation_build()


if __name__ == "__main__":
    asyncio.run(main())
