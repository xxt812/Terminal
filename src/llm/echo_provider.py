from __future__ import annotations

from collections.abc import AsyncIterator

from src.agent_core.message import AgentMessage, Role


class EchoProvider:
    """Offline provider that repeats the most recent user message."""

    name = "echo"

    async def ainvoke(self, messages: list[AgentMessage], **kwargs: object) -> AgentMessage:
        del kwargs
        content = next(
            (message.content for message in reversed(messages) if message.role is Role.USER),
            "",
        )
        return AgentMessage(role=Role.ASSISTANT, content=content)

    async def astream(self, messages: list[AgentMessage], **kwargs: object) -> AsyncIterator[str]:
        response = await self.ainvoke(messages, **kwargs)
        for character in response.content:
            yield character
