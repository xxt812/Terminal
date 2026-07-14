from __future__ import annotations

from collections.abc import Callable
from typing import Any

from src.config.settings import Settings, get_settings
from src.exceptions import ConfigError, LLMProviderError
from src.llm.base import LLMProvider
from src.llm.echo_provider import EchoProvider
from src.llm.faux_provider import FauxLLMProvider
from src.llm.langchain_adapter import LangChainChatAdapter

ProviderFactory = Callable[..., LLMProvider]

PROVIDERS: dict[str, ProviderFactory] = {
    "echo": EchoProvider,
    "faux": FauxLLMProvider,
}


def register_provider(name: str, factory: ProviderFactory, *, replace: bool = False) -> None:
    """Register a provider factory without modifying orchestration code."""

    normalized = name.strip().lower()
    if not normalized:
        raise ValueError("provider name cannot be empty")
    if normalized in PROVIDERS and not replace:
        raise ValueError(f"provider already registered: {normalized}")
    PROVIDERS[normalized] = factory


def get_provider(name: str, **kwargs: Any) -> LLMProvider:
    normalized = name.strip().lower()
    if normalized in PROVIDERS:
        return PROVIDERS[normalized](**kwargs)
    if normalized in {"anthropic", "openai"}:
        return _create_optional_provider(normalized, get_settings(), **kwargs)
    raise ConfigError(f"unknown provider {name!r}; available: {sorted(PROVIDERS)}")


def create_provider(settings: Settings | None = None, **kwargs: Any) -> LLMProvider:
    """Create the configured default provider."""

    current = settings or get_settings()
    name = current.llm.default_provider
    if name in PROVIDERS:
        return PROVIDERS[name](**kwargs)
    return _create_optional_provider(name, current, **kwargs)


def _create_optional_provider(name: str, settings: Settings, **kwargs: Any) -> LLMProvider:
    model_name = kwargs.pop("model", settings.llm.default_model)
    try:
        if name == "anthropic":
            from langchain_anthropic import ChatAnthropic

            model = ChatAnthropic(model=model_name, **kwargs)
        elif name == "openai":
            from langchain_openai import ChatOpenAI

            model = ChatOpenAI(model=model_name, **kwargs)
        else:
            raise ConfigError(f"unsupported provider: {name}")
    except ImportError as exc:
        raise LLMProviderError(
            f"provider {name!r} requires the optional dependency group {name!r}"
        ) from exc
    return LangChainChatAdapter(name, model)
