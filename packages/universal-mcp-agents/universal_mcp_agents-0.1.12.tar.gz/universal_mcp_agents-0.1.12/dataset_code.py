import asyncio

from dotenv import load_dotenv
from langsmith import Client

from universal_mcp.agentr.registry import AgentrRegistry
from universal_mcp.agents.codeact0 import CodeActAgent

load_dotenv()

client = Client()

async def create_examples(user_input: str, tools_list: list[str]):
    """Run the agent and create a LangSmith dataset example"""

    # Create/get dataset
    dataset_name = "codeagent-tests"
    try:
        dataset = client.create_dataset(
            dataset_name,
            description="Dataset for the codeagent"
        )
    except Exception:
        dataset = client.read_dataset(dataset_name=dataset_name)


    # Define the input
    # user_input = "Send an email to Manoj from my google mail account, manoj@agentr.dev, with the subject 'Hello from auto agent' and the body 'testing'"

    # Capture initial state
    initial_state = {
        "messages": [{"role": "user", "content": user_input}],
        "tools": tools_list
    }
    #result = await agent.ainvoke(initial_state, context={"model": "anthropic/claude-4-sonnet-20250514", "system_time": system_time})

    # Extract the final state from the result
    # Note: Adjust these based on your actual result structure

    # Create the dataset example with actual results
    example = client.create_example(
        inputs=initial_state,
        outputs=None,
        dataset_id=dataset.id
    )

    print(f"✅ Created dataset example with ID: {example.id}")
    print(f"Dataset: {dataset_name}")
    print(f"Input: {user_input}")

    return example

import yaml
import os

if __name__ == "__main__":
    usecases_dir = os.path.join("src", "universal_mcp", "agents", "codeact0", "usecases")
    async def main():
        for name in sorted(os.listdir(usecases_dir)):
            if not name.endswith(".yaml"):
                continue
            path = os.path.join(usecases_dir, name)
            with open(path, encoding="utf-8") as f:
                content = f.read()
            data = yaml.safe_load(content) or {}
            base_prompt = data.get("base_prompt")
            tools = data.get("tools")
            if not base_prompt:
                continue
            # Normalize tools to a flat list[str]
            tools_list: list[str] = []
            if isinstance(tools, list):
                tools_list = tools
            elif isinstance(tools, dict):
                for v in tools.values():
                    if isinstance(v, list):
                        tools_list.extend(v)
                    elif isinstance(v, str):
                        tools_list.append(v)
            print(f"Creating example for {name} with {len(tools_list)} tools…")
            await create_examples(base_prompt, tools_list)

    asyncio.run(main())
