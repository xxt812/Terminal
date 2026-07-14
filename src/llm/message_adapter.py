from __future__ import annotations

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.messages import ToolMessage as LangChainToolMessage

from src.agent_core.message import AgentMessage, Role, ToolCall, ToolResult


def to_langchain_message(message: AgentMessage) -> BaseMessage:
    """Convert a core message at the provider boundary."""

    if message.role is Role.SYSTEM:
        return SystemMessage(content=message.content, name=message.name)
    if message.role is Role.USER:
        return HumanMessage(content=message.content, name=message.name)
    if message.role is Role.TOOL:
        assert message.tool_result is not None
        return LangChainToolMessage(
            content=message.tool_result.content,
            tool_call_id=message.tool_result.call_id,
            name=message.tool_result.name,
            status="error" if message.tool_result.is_error else "success",
        )
    return AIMessage(
        content=message.content,
        name=message.name,
        tool_calls=[
            {"id": call.id, "name": call.name, "args": call.arguments, "type": "tool_call"}
            for call in message.tool_calls
        ],
    )


def from_langchain_message(message: BaseMessage) -> AgentMessage:
    """Convert a provider message into the stable core model."""

    content = message.content if isinstance(message.content, str) else str(message.content)
    if isinstance(message, SystemMessage):
        return AgentMessage(role=Role.SYSTEM, content=content, name=message.name)
    if isinstance(message, HumanMessage):
        return AgentMessage(role=Role.USER, content=content, name=message.name)
    if isinstance(message, LangChainToolMessage):
        return AgentMessage(
            role=Role.TOOL,
            content=content,
            name=message.name,
            tool_result=ToolResult(
                call_id=message.tool_call_id,
                name=message.name or "tool",
                content=content,
                is_error=getattr(message, "status", "success") == "error",
            ),
        )
    tool_calls = [
        ToolCall(id=call["id"], name=call["name"], arguments=dict(call.get("args", {})))
        for call in getattr(message, "tool_calls", [])
    ]
    return AgentMessage(
        role=Role.ASSISTANT,
        content=content,
        name=message.name,
        tool_calls=tool_calls,
        metadata=dict(message.response_metadata),
    )
