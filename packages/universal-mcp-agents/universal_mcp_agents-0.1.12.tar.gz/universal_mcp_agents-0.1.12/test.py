import asyncio
import uuid

from langgraph.checkpoint.memory import MemorySaver
from universal_mcp.agentr.client import AgentrClient
from universal_mcp.agentr.registry import AgentrRegistry

from universal_mcp.agents import CodeActScript, CodeActRepl
from universal_mcp.agents.utils import get_message_text
from rich import print
from langchain_core.messages.base import BaseMessage


def display_messages(messages: list[BaseMessage]):
    for message in messages:
        text = get_message_text(message)
        print(f"{message.type}: {text}")


async def main():
    client = AgentrClient()
    registry = AgentrRegistry(client=client)
    repl = CodeActRepl(
        name="autoagent",
        instructions="You are a helpful assistant that can use tools to help the user.",
        model="anthropic/claude-4-sonnet-20250514",
        registry=registry,
        memory=MemorySaver(),
    )
    script = CodeActScript(
        name="autoagent",
        instructions="You are a helpful assistant that can use tools to help the user.",
        model="anthropic/claude-4-sonnet-20250514",
        registry=registry,
        memory=MemorySaver(),
    )

    task = "What is 49th fibonacci number?"
    thread_id = f"test-thread-{uuid.uuid4()}"
    result = await repl.invoke(task, thread_id=thread_id)
    print(f"Messages: {result['messages']}")
    messages = display_messages(result["messages"])
    result = await script.invoke(task, thread_id=thread_id)
    messages = display_messages(result["messages"])
    print(f"Messages: {messages}")


if __name__ == "__main__":
    asyncio.run(main())
