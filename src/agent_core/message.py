from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Role(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ToolCall(BaseModel):
    """A tool call requested by an assistant message."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: f"tc_{uuid4().hex[:12]}")
    name: str = Field(min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)


class ToolResult(BaseModel):
    """A tool result returned to the model."""

    model_config = ConfigDict(extra="forbid")

    call_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    content: str
    is_error: bool = False


class AgentMessage(BaseModel):
    """A provider-neutral message exchanged by agents and tools."""

    model_config = ConfigDict(extra="forbid")

    role: Role
    content: str = ""
    name: str | None = None
    tool_calls: list[ToolCall] = Field(default_factory=list)
    tool_result: ToolResult | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _validate_role_payload(self) -> AgentMessage:
        if self.tool_result is not None and self.role is not Role.TOOL:
            raise ValueError("tool_result is only valid on tool messages")
        if self.role is Role.TOOL and self.tool_result is None:
            raise ValueError("tool messages require tool_result")
        if self.tool_calls and self.role is not Role.ASSISTANT:
            raise ValueError("tool_calls are only valid on assistant messages")
        return self
