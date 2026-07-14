from __future__ import annotations

from collections.abc import Callable, Hashable, Mapping
from typing import Any

from langgraph.graph import END, START, StateGraph

from src.agent_core.types import SessionState
from src.exceptions import AgentGraphError

Node = Callable[[SessionState], dict[str, Any] | SessionState]
Route = Callable[[SessionState], Hashable]


class GraphBuilder:
    """Validated facade over LangGraph's StateGraph."""

    def __init__(self) -> None:
        self._graph = StateGraph(SessionState)
        self._nodes: set[str] = set()
        self._has_entry = False
        self._has_exit = False

    def add_node(self, name: str, node: Node) -> GraphBuilder:
        if not name or name in {START, END}:
            raise AgentGraphError(f"invalid node name: {name!r}")
        if name in self._nodes:
            raise AgentGraphError(f"duplicate node: {name}")
        self._graph.add_node(name, node)
        self._nodes.add(name)
        return self

    def add_edge(self, source: str, target: str) -> GraphBuilder:
        self._require_known(source, allow_boundary=True)
        self._require_known(target, allow_boundary=True)
        self._graph.add_edge(source, target)
        self._has_entry |= source == START
        self._has_exit |= target == END
        return self

    def add_conditional_edges(
        self,
        source: str,
        router: Route,
        path_map: Mapping[Hashable, str],
    ) -> GraphBuilder:
        self._require_known(source)
        if not path_map:
            raise AgentGraphError("conditional edges require at least one route")
        for target in path_map.values():
            self._require_known(target, allow_boundary=True)
            self._has_exit |= target == END
        self._graph.add_conditional_edges(source, router, dict(path_map))
        return self

    def set_entry_point(self, name: str) -> GraphBuilder:
        self._require_known(name)
        self._graph.add_edge(START, name)
        self._has_entry = True
        return self

    def set_finish_point(self, name: str) -> GraphBuilder:
        self._require_known(name)
        self._graph.add_edge(name, END)
        self._has_exit = True
        return self

    def compile(self, *, checkpointer: Any | None = None) -> Any:
        if not self._nodes:
            raise AgentGraphError("cannot compile an empty graph")
        if not self._has_entry:
            raise AgentGraphError("graph has no entry point")
        if not self._has_exit:
            raise AgentGraphError("graph has no path to END")
        return self._graph.compile(checkpointer=checkpointer)

    def _require_known(self, name: str, *, allow_boundary: bool = False) -> None:
        if allow_boundary and name in {START, END}:
            return
        if name not in self._nodes:
            raise AgentGraphError(f"unknown node: {name}")


AgentGraph = GraphBuilder
