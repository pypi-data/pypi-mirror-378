from typing import Any

from langgraph.graph import MessagesState


class CodeActState(MessagesState):
    """State for CodeAct agent."""

    context: dict[str, Any]
    """Dictionary containing the execution context with available tools and variables."""
    add_context: dict[str, Any]
    """Dictionary containing the additional context (functions, classes, imports) to be added to the execution context."""
