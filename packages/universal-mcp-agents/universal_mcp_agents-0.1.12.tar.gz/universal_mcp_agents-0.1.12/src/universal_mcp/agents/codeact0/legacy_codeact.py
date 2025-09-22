import contextlib
import inspect
import io
import queue
import re
import socket
import threading
import types
from typing import Any

import yaml
from langchain.chat_models import init_chat_model
from langchain_anthropic import ChatAnthropic
from langchain_core.runnables import RunnableConfig
from langchain_google_vertexai.model_garden import ChatAnthropicVertex
from universal_mcp.agentr import Agentr
from universal_mcp.types import ToolFormat

from universal_mcp.agents.codeact0 import create_codeact
from universal_mcp.agents.codeact0.config import ContextSchema
from universal_mcp.agents.codeact0.utils import derive_context


def eval(code: str, _locals: dict[str, Any], add_context: dict[str, Any]) -> tuple[str, dict[str, Any], dict[str, Any]]:
    # print(_locals)
    EXCLUDE_TYPES = (
        types.ModuleType,  # modules
        type(re.match("", "")),
        type(threading.Lock()),  # instead of threading.Lock
        type(threading.RLock()),  # reentrant lock
        threading.Event,  # events
        threading.Condition,  # condition vars
        threading.Semaphore,  # semaphores
        queue.Queue,  # thread-safe queues
        socket.socket,  # network sockets
        io.IOBase,  # file handles (and StringIO/BytesIO)
    )
    try:
        with contextlib.redirect_stdout(io.StringIO()) as f:
            # Execute the code in the provided locals context
            # Using exec to allow dynamic code execution
            # This is a simplified version; in production, consider security implications
            exec(code, _locals, _locals)
        result = f.getvalue()
        if not result:
            result = "<code ran, no output printed to stdout>"
    except Exception as e:
        result = f"Error during execution: {repr(e)}"

    # Return all variables in locals except __builtins__ and unpicklable objects (including tools)
    all_vars = {}
    for key, value in _locals.items():
        if key == "__builtins__":
            continue

        # Skip coroutines, async generators, and coroutine functions
        if inspect.iscoroutine(value) or inspect.iscoroutinefunction(value):
            continue
        if inspect.isasyncgen(value) or inspect.isasyncgenfunction(value):
            continue

        # Skip "obviously unpicklable" types
        if isinstance(value, EXCLUDE_TYPES):
            continue

        # Keep if it's not a callable OR if it has no __name__ attribute
        if not callable(value) or not hasattr(value, "__name__"):
            all_vars[key] = value

    new_add_context = derive_context(code, add_context)
    return result, all_vars, new_add_context


async def agent(config: RunnableConfig):
    cfg = ContextSchema(**config.get("configurable", {}))

    if cfg.json_prompt_name and cfg.json_prompt_name.strip():
        with open(f"usecases/{cfg.json_prompt_name}.yaml", encoding="utf-8") as f:
            content = f.read()
            data = yaml.safe_load(content)
            if cfg.base_prompt and cfg.base_prompt.strip():
                pass
            else:
                cfg.base_prompt = data["base_prompt"]
            cfg.tool_names = data["tools"]
    agentr = Agentr()
    agentr.load_tools(cfg.tool_names)
    tools = []  # can add custom tools here like get_weather, get_simple_weather, etc.

    tools_agentr = agentr.list_tools(format=ToolFormat.NATIVE)
    tools.extend(tools_agentr)

    if cfg.model_provider == "google_anthropic_vertex":
        # For Google Anthropic Vertex, we need to use the specific model initialization due to location
        model = ChatAnthropicVertex(model=cfg.model, temperature=0.2, location="asia-east1")
    elif cfg.model == "claude-4-sonnet-20250514":
        model = ChatAnthropic(
            model=cfg.model, temperature=1, thinking={"type": "enabled", "budget_tokens": 2048}, max_tokens=4096
        )  # pyright: ignore[reportCallIssue]
    else:
        model = init_chat_model(model=cfg.model, model_provider=cfg.model_provider, temperature=0.2)

    code_act = create_codeact(model, cfg.base_prompt, tools, eval)
    return code_act.compile()
