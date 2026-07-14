import pytest

from src.agent_core.types import create_session_state

pytestmark = pytest.mark.unit


def test_create_session_state_returns_independent_collections() -> None:
    first = create_session_state()
    second = create_session_state()

    first["metadata"]["changed"] = True

    assert first["session_id"] != second["session_id"]
    assert second["metadata"] == {}


def test_create_session_state_rejects_negative_budget() -> None:
    with pytest.raises(ValueError, match="cannot be negative"):
        create_session_state(tool_calls_budget=-1)
