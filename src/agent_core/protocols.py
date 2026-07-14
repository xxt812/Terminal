from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol

from src.agent_core.message import AgentMessage


class BaseChatModel(Protocol):
    """Provider-neutral LLM contract owned by the architecture layer."""

    name: str

    async def ainvoke(self, messages: list[AgentMessage], **kwargs: object) -> AgentMessage: ...

    def astream(self, messages: list[AgentMessage], **kwargs: object) -> AsyncIterator[str]: ...


class MemoryBackend(Protocol):
    """Minimal memory contract consumed by orchestration."""

    async def add(self, item: object) -> str: ...

    async def search(self, query: str, k: int = 5) -> list[object]: ...

    async def get(self, item_id: str) -> object | None: ...
