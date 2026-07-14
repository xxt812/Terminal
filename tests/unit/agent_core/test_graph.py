import pytest

from src.agent_core.graph import GraphBuilder
from src.agent_core.types import create_session_state
from src.exceptions import AgentGraphError

pytestmark = pytest.mark.unit


def test_graph_runs_single_node() -> None:
    graph = (
        GraphBuilder()
        .add_node("worker", lambda state: {"current_agent": "worker"})
        .set_entry_point("worker")
        .set_finish_point("worker")
        .compile()
    )

    result = graph.invoke(create_session_state())

    assert result["current_agent"] == "worker"


def test_graph_rejects_duplicate_node() -> None:
    builder = GraphBuilder().add_node("worker", lambda state: state)

    with pytest.raises(AgentGraphError, match="duplicate node"):
        builder.add_node("worker", lambda state: state)


def test_graph_requires_exit() -> None:
    builder = GraphBuilder().add_node("worker", lambda state: state).set_entry_point("worker")

    with pytest.raises(AgentGraphError, match="no path to END"):
        builder.compile()
