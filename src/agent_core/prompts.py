"""Prompt helpers shared by concrete agent implementations."""

from src.agent_core.message import AgentMessage, Role


def with_system_prompt(prompt: str, messages: list[AgentMessage]) -> list[AgentMessage]:
    """Prepend a system prompt without mutating the caller's message list."""

    return [AgentMessage(role=Role.SYSTEM, content=prompt), *messages]
