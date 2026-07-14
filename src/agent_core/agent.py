from __future__ import annotations

from collections.abc import AsyncIterator, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from src.agent_core.message import AgentMessage
from src.agent_core.types import SessionState


@dataclass(frozen=True, slots=True)
class AgentContext:
    """Immutable runtime context supplied by the orchestrator."""

    session_id: str
    project_id: str | None = None
    working_directory: Path | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@runtime_checkable
class BaseAgent(Protocol):
    """Contract implemented by every concrete agent role."""

    name: str
    description: str

    async def ainvoke(self, state: SessionState, context: AgentContext) -> SessionState: ...

    def astream(
        self, state: SessionState, context: AgentContext
    ) -> AsyncIterator[AgentMessage]: ...


Agent = BaseAgent
