import asyncio

import pytest

from src.agent_core.message import AgentMessage, Role, ToolCall
from src.llm.echo_provider import EchoProvider
from src.llm.faux_provider import FauxLLMProvider
from src.llm.registry import get_provider

pytestmark = pytest.mark.unit


def test_faux_returns_messages_and_tracks_queue() -> None:
    tool_message = AgentMessage(
        role=Role.ASSISTANT,
        content="use tool",
        tool_calls=[ToolCall(name="read", arguments={"path": "a.py"})],
    )
    provider = FauxLLMProvider(["first", tool_message])

    first = asyncio.run(provider.ainvoke([]))
    second = asyncio.run(provider.ainvoke([]))

    assert first.content == "first"
    assert second.tool_calls[0].name == "read"
    assert provider.call_count == 2
    assert provider.pending_count == 0


def test_faux_raises_when_queue_is_empty() -> None:
    provider = FauxLLMProvider([])

    with pytest.raises(RuntimeError, match="No more faux responses"):
        asyncio.run(provider.ainvoke([]))


def test_faux_streams_one_response() -> None:
    provider = FauxLLMProvider(["hello"])

    async def collect() -> list[str]:
        return [chunk async for chunk in provider.astream([])]

    chunks = asyncio.run(collect())

    assert "".join(chunks) == "hello"


def test_echo_returns_last_user_message() -> None:
    provider = EchoProvider()
    messages = [
        AgentMessage(role=Role.USER, content="first"),
        AgentMessage(role=Role.ASSISTANT, content="reply"),
        AgentMessage(role=Role.USER, content="second"),
    ]

    response = asyncio.run(provider.ainvoke(messages))

    assert response.content == "second"
    assert get_provider("echo").name == "echo"
