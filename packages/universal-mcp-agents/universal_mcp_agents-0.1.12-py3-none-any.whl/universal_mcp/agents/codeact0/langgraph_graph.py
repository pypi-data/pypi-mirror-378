from langgraph.checkpoint.memory import MemorySaver
from universal_mcp.agentr.registry import AgentrRegistry

from universal_mcp.agents.codeact0.agent import CodeActAgent


async def agent():
    memory = MemorySaver()
    agent_object = await CodeActAgent(
        name="CodeAct Agent",
        instructions="Be very concise in your answers.",
        model="anthropic:claude-4-sonnet-20250514",
        tools={"google_mail": ["list_messages"]},
        registry=AgentrRegistry(),
        memory=memory,
    )._build_graph()
    return agent_object
