from collections.abc import AsyncIterator

import pytest

from src.agent_core.agent import AgentContext, BaseAgent
from src.agent_core.message import AgentMessage
from src.agent_core.types import SessionState, create_session_state

pytestmark = pytest.mark.unit


class StubAgent:
    name = "stub"
    description = "test agent"

    async def ainvoke(self, state: SessionState, context: AgentContext) -> SessionState:
        return state

    async def astream(
        self, state: SessionState, context: AgentContext
    ) -> AsyncIterator[AgentMessage]:
        if False:
            yield AgentMessage(role="assistant", content="unused")


def test_base_agent_is_runtime_checkable() -> None:
    assert isinstance(StubAgent(), BaseAgent)
    assert create_session_state()["tool_calls_budget"] == 20
