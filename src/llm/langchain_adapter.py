from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel as LangChainBaseChatModel

from src.agent_core.message import AgentMessage
from src.exceptions import LLMProviderError
from src.llm.message_adapter import from_langchain_message, to_langchain_message


class LangChainChatAdapter:
    """Expose a LangChain chat model through TCA's stable provider protocol."""

    def __init__(self, name: str, model: LangChainBaseChatModel) -> None:
        self.name = name
        self._model = model

    async def ainvoke(self, messages: list[AgentMessage], **kwargs: object) -> AgentMessage:
        try:
            response = await self._model.ainvoke(
                [to_langchain_message(message) for message in messages], **kwargs
            )
        except Exception as exc:
            raise LLMProviderError(f"provider {self.name!r} invocation failed") from exc
        return from_langchain_message(response)

    async def astream(self, messages: list[AgentMessage], **kwargs: object) -> AsyncIterator[str]:
        try:
            async for chunk in self._model.astream(
                [to_langchain_message(message) for message in messages], **kwargs
            ):
                if isinstance(chunk.content, str):
                    yield chunk.content
        except Exception as exc:
            raise LLMProviderError(f"provider {self.name!r} stream failed") from exc

    @property
    def model(self) -> Any:
        """Return the wrapped model for integrations that require LangChain directly."""

        return self._model
