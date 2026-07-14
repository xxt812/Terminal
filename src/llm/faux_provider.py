from __future__ import annotations

import asyncio
from collections import deque
from collections.abc import AsyncIterator, Iterable

from src.agent_core.message import AgentMessage, Role


class FauxLLMProvider:
    """Deterministic offline provider backed by an explicit response queue."""

    name = "faux"

    def __init__(
        self,
        responses: Iterable[str | AgentMessage] | None = None,
        *,
        latency: float = 0.0,
        cycle: bool = False,
    ) -> None:
        if latency < 0:
            raise ValueError("latency cannot be negative")
        initial = list(responses) if responses is not None else ["faux-response"]
        self._responses: deque[AgentMessage] = deque(self._coerce(item) for item in initial)
        self._original = tuple(self._responses)
        self._latency = latency
        self._cycle = cycle
        self._call_count = 0

    async def ainvoke(self, messages: list[AgentMessage], **kwargs: object) -> AgentMessage:
        del messages, kwargs
        if self._latency:
            await asyncio.sleep(self._latency)
        return self._next()

    async def astream(self, messages: list[AgentMessage], **kwargs: object) -> AsyncIterator[str]:
        del messages, kwargs
        message = self._next()
        for character in message.content:
            if self._latency:
                await asyncio.sleep(self._latency / max(len(message.content), 1))
            yield character

    def enqueue(self, *responses: str | AgentMessage) -> None:
        self._responses.extend(self._coerce(item) for item in responses)

    def reset(self, responses: Iterable[str | AgentMessage] | None = None) -> None:
        self._call_count = 0
        values = (
            self._original if responses is None else tuple(self._coerce(item) for item in responses)
        )
        self._responses = deque(values)

    @property
    def call_count(self) -> int:
        return self._call_count

    @property
    def pending_count(self) -> int:
        return len(self._responses)

    def _next(self) -> AgentMessage:
        self._call_count += 1
        if not self._responses:
            if self._cycle and self._original:
                self._responses.extend(self._original)
            else:
                raise RuntimeError(f"No more faux responses queued (call #{self._call_count}).")
        response = self._responses.popleft()
        if self._cycle:
            self._responses.append(response)
        return response.model_copy(deep=True)

    @staticmethod
    def _coerce(response: str | AgentMessage) -> AgentMessage:
        if isinstance(response, AgentMessage):
            return response
        return AgentMessage(role=Role.ASSISTANT, content=response)


FauxLLM = FauxLLMProvider
