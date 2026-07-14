from __future__ import annotations

from typing import Annotated, Any, TypedDict
from uuid import uuid4

from langgraph.graph.message import add_messages


class SessionState(TypedDict):
    """State shared between LangGraph nodes."""

    messages: Annotated[list[Any], add_messages]
    session_id: str
    current_agent: str
    tool_calls_budget: int
    memory_hits: list[Any]
    metadata: dict[str, Any]


def create_session_state(
    *,
    session_id: str | None = None,
    messages: list[Any] | None = None,
    current_agent: str = "",
    tool_calls_budget: int = 20,
    metadata: dict[str, Any] | None = None,
) -> SessionState:
    """Create a complete state object so graph nodes need no defensive defaults."""

    if tool_calls_budget < 0:
        raise ValueError("tool_calls_budget cannot be negative")
    return SessionState(
        messages=list(messages or []),
        session_id=session_id or f"session_{uuid4().hex[:12]}",
        current_agent=current_agent,
        tool_calls_budget=tool_calls_budget,
        memory_hits=[],
        metadata=dict(metadata or {}),
    )
