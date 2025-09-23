uneditable_prompt = """
You are Wingman, an AI Assistant created by AgentR. You are a creative, straight-forward and direct principal software engineer.

Your job is to answer the user's question or perform the task they ask for.
- Answer simple questions (which do not require you to write any code or access any external resources) directly. Note that any operation that involves using ONLY print functions should be answered directly.
- For task requiring operations or access to external resources, you should achieve the task by executing Python code snippets.
- You have access to `execute_ipython_cell` tool that allows you to execute Python code in an IPython notebook cell.
- In writing or natural language processing tasks DO NOT answer directly. Instead use `execute_ipython_cell` tool with the AI functions provided to you for tasks like summarizing, text generation, classification, data extraction from text or unstructured data, etc.
- The code you write will be executed in a sandbox environment, and you can use the output of previous executions in your code.
- Read and understand the output of the previous code snippet and use it to answer the user's request. Note that the code output is not visible to the user, so after the task is complete, you have to give the output to the user in a markdown format.
- If needed, feel free to ask for more information from the user (without using the execute_ipython_cell tool) to clarify the task.

GUIDELINES for writing code:
- Variables defined at the top level of previous code snippets can be referenced in your code.
- External functions which return a dict or list[dict] are ambiguous. Therefore, you MUST explore the structure of the returned data using `smart_print()` statements before using it, printing keys and values.
- Ensure to not print large amounts of data, use string truncation to limit the output to a few lines when checking the data structure.
- When an operation involves running a fixed set of steps on a list of items, run one run correctly and then use a for loop to run the steps on each item in the list.
- In a single code snippet, try to achieve as much as possible.
- You can only import libraries that come pre-installed with Python, and these have to be imported at the top of every code snippet where required.
- Wrap await calls in a function and call it using `asyncio.run` to use async functions.

NOTE: If any function throws an error requiring authentication, provide the user with a Markdown link to the authentication page and prompt them to authenticate.
"""
import inspect
import re
from collections.abc import Sequence
from datetime import datetime

from langchain_core.tools import StructuredTool


def make_safe_function_name(name: str) -> str:
    """Convert a tool name to a valid Python function name."""
    # Replace non-alphanumeric characters with underscores
    safe_name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    # Ensure the name doesn't start with a digit
    if safe_name and safe_name[0].isdigit():
        safe_name = f"tool_{safe_name}"
    # Handle empty name edge case
    if not safe_name:
        safe_name = "unnamed_tool"
    return safe_name


def dedent(text):
    """Remove any common leading whitespace from every line in `text`.

    This can be used to make triple-quoted strings line up with the left
    edge of the display, while still presenting them in the source code
    in indented form.

    Note that tabs and spaces are both treated as whitespace, but they
    are not equal: the lines "  hello" and "\\thello" are
    considered to have no common leading whitespace.

    Entirely blank lines are normalized to a newline character.
    """
    # Look for the longest leading string of spaces and tabs common to
    # all lines.
    margin = None
    _whitespace_only_re = re.compile("^[ \t]+$", re.MULTILINE)
    _leading_whitespace_re = re.compile("(^[ \t]*)(?:[^ \t\n])", re.MULTILINE)
    text = _whitespace_only_re.sub("", text)
    indents = _leading_whitespace_re.findall(text)
    for indent in indents:
        if margin is None:
            margin = indent

        # Current line more deeply indented than previous winner:
        # no change (previous winner is still on top).
        elif indent.startswith(margin):
            pass

        # Current line consistent with and no deeper than previous winner:
        # it's the new winner.
        elif margin.startswith(indent):
            margin = indent

        # Find the largest common whitespace between current line and previous
        # winner.
        else:
            for i, (x, y) in enumerate(zip(margin, indent)):
                if x != y:
                    margin = margin[:i]
                    break

    # sanity check (testing/debugging only)
    if 0 and margin:
        for line in text.split("\n"):
            assert not line or line.startswith(margin), f"line = {line!r}, margin = {margin!r}"

    if margin:
        text = re.sub(r"(?m)^" + margin, "", text)
    return text


def indent(text, prefix, predicate=None):
    """Adds 'prefix' to the beginning of selected lines in 'text'.

    If 'predicate' is provided, 'prefix' will only be added to the lines
    where 'predicate(line)' is True. If 'predicate' is not provided,
    it will default to adding 'prefix' to all non-empty lines that do not
    consist solely of whitespace characters.
    """
    if predicate is None:
        # str.splitlines(True) doesn't produce empty string.
        #  ''.splitlines(True) => []
        #  'foo\n'.splitlines(True) => ['foo\n']
        # So we can use just `not s.isspace()` here.
        def predicate(s):
            return not s.isspace()

    prefixed_lines = []
    for line in text.splitlines(True):
        if predicate(line):
            prefixed_lines.append(prefix)
        prefixed_lines.append(line)

    return "".join(prefixed_lines)


def create_default_prompt(
    tools: Sequence[StructuredTool],
    base_prompt: str | None = None,
):
    system_prompt = uneditable_prompt.strip() + (
        "\n\nIn addition to the Python Standard Library, you can use the following external functions:\n"
    )
    tools_context = {}
    for tool in tools:
        # Create a safe function name
        safe_name = make_safe_function_name(tool.name)
        # Use coroutine if it exists, otherwise use func
        if hasattr(tool, "coroutine") and tool.coroutine is not None:
            tool_callable = tool.coroutine
            signature = inspect.signature(tool_callable)
            is_async = True
        elif hasattr(tool, "func") and tool.func is not None:
            tool_callable = tool.func
            signature = inspect.signature(tool_callable)
            is_async = False
        else:
            raise ValueError(f"Tool {tool.name} does not have a callable coroutine or function.")
        tools_context[safe_name] = tool_callable
        system_prompt += f'''
{"async " if is_async else ""}def {safe_name}{str(signature)}:
    """
{indent(dedent(tool.description), "    ")}
    """
    ...
'''
    system_prompt += f"\n\nThe current time is {datetime.now().strftime('%H:%M:%S')}"
    if base_prompt and base_prompt.strip():
        system_prompt += f"Your goal is to perform the following task:\n\n{base_prompt}"

    return system_prompt, tools_context
