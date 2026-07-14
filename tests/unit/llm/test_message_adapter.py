import pytest
from langchain_core.messages import AIMessage

from src.agent_core.message import AgentMessage, Role, ToolCall
from src.llm.message_adapter import from_langchain_message, to_langchain_message

pytestmark = pytest.mark.unit


def test_assistant_tool_calls_round_trip() -> None:
    original = AgentMessage(
        role=Role.ASSISTANT,
        content="reading",
        tool_calls=[ToolCall(id="tc_1", name="read", arguments={"path": "a.py"})],
    )

    converted = to_langchain_message(original)
    restored = from_langchain_message(converted)

    assert isinstance(converted, AIMessage)
    assert restored.tool_calls[0].arguments == {"path": "a.py"}
