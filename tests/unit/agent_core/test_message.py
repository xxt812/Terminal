import pytest
from pydantic import ValidationError

from src.agent_core.message import AgentMessage, Role, ToolCall, ToolResult

pytestmark = pytest.mark.unit


def test_assistant_message_accepts_tool_calls() -> None:
    call = ToolCall(name="read_file", arguments={"path": "README.md"})
    message = AgentMessage(role=Role.ASSISTANT, tool_calls=[call])

    assert message.tool_calls[0].id.startswith("tc_")


def test_tool_message_requires_result() -> None:
    with pytest.raises(ValidationError, match="require tool_result"):
        AgentMessage(role=Role.TOOL, content="missing structured result")


def test_tool_result_rejected_on_user_message() -> None:
    result = ToolResult(call_id="tc_1", name="read_file", content="ok")

    with pytest.raises(ValidationError, match="only valid on tool messages"):
        AgentMessage(role=Role.USER, tool_result=result)
