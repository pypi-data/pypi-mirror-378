import asyncio

from dotenv import load_dotenv
from langsmith import Client, aevaluate

from universal_mcp.agentr.registry import AgentrRegistry
from universal_mcp.agents.codeact0 import CodeActAgent
from universal_mcp.agents.codeact import CodeActAgent as MCodeActAgent

load_dotenv()
def convert_tools(tool_list: list[str]) -> dict[str, list[str]]:
    result = {}
    for tool in tool_list:
        if "__" in tool:
            prefix, suffix = tool.split("__", 1)
            result.setdefault(prefix, []).append(suffix)
    return result




async def target_function1(inputs: dict):
    with open('src/universal_mcp/agents/codeact0/llm_tool.py', 'r') as file:
        llm_tool_code = file.read()
    
    base_agent =  CodeActAgent(
        "CodeAct Agent",
        instructions="Be very concise in your answers. DO NOT STOP or ASK the user any questions. Assume details if required.",
        model="anthropic:claude-4-sonnet-20250514",
        tools=convert_tools(inputs["tools"]),
        registry=AgentrRegistry(),
        initial_code = llm_tool_code
    )
    agent = await base_agent._build_graph()
    result = await agent.ainvoke(inputs, config = {"recursion_limit": 100})
    return result


async def target_function2(inputs: dict):
    
    base_agent =  MCodeActAgent(
        "CodeAct Agent",
        instructions="Be very concise in your answers. DO NOT STOP or ASK the user any questions. Assume details if required.",
        model="anthropic:claude-4-sonnet-20250514",
        tools=convert_tools(inputs["tools"]),
        registry=AgentrRegistry(),
    )
    agent = await base_agent._build_graph()
    result = await agent.ainvoke(inputs, config = {"recursion_limit":100})
    return result


if __name__ == "__main__":
    client = Client()
    dataset_name = "codeagent-tests"
#     asyncio.run(aevaluate(
#     target_function1,
#     data=client.list_examples(
#         dataset_name=dataset_name,example_ids=["5425de13-58b0-44b3-802f-9e5e6b2e3a0c", "56bcf12f-2608-4ad7-8538-507ff0e22df1", "79ecefe9-3a13-428e-bdda-f3cc1eb03578", "c0a2e3cf-9bea-4cf3-90be-7ab8945094b3", "a73827d5-2c77-4d8b-a486-93b0e8ce6713"]
#     ),
#     evaluators=[],
#     experiment_prefix ="test-1-errors"
# ))

    asyncio.run(aevaluate(
    target_function1,
    data=client.list_examples(
        dataset_name=dataset_name,
        splits=["base"]
    ),
    evaluators=[],
    experiment_prefix ="Code0-agent",
    num_repetitions=1
    ))

# 49a34291-5907-4ae0-a582-8fc1fb5149f3
# a15e0d66-e6f6-4ad6-8e31-bd1711138dc2 - 5 github examples to 2
# e8505035-7878-4c58-9938-fc7d80767047
