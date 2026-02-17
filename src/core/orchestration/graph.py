"""LangGraph builders for config-driven workflow assembly."""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, MutableMapping, Type

from langgraph.graph import StateGraph


NodeHandler = Callable[[MutableMapping[str, Any]], MutableMapping[str, Any]]


@dataclass
class ConditionalRoute:
    """Conditional intent router configuration."""

    source: str
    intent_key: str
    routes: Dict[str, str]


@dataclass
class GraphConfig:
    """Graph configuration loaded from external YAML."""

    entry_point: str
    finish_point: str
    conditional_routes: List[ConditionalRoute]
    edges: List[List[str]]


def _make_selector(intent_key: str) -> Callable[[MutableMapping[str, Any]], str]:
    def selector(state: MutableMapping[str, Any]) -> str:
        return state.get(intent_key, "unknown")

    return selector


def build_graph(
    state_type: Type[MutableMapping[str, Any]],
    node_handlers: Dict[str, NodeHandler],
    graph_config: GraphConfig,
):
    """Build and compile a LangGraph from configured nodes and edges."""
    graph_builder = StateGraph(state_type)

    for node_name, handler in node_handlers.items():
        graph_builder.add_node(node_name, handler)

    graph_builder.set_entry_point(graph_config.entry_point)

    for conditional in graph_config.conditional_routes:
        graph_builder.add_conditional_edges(
            conditional.source,
            _make_selector(conditional.intent_key),
            conditional.routes,
        )

    for edge in graph_config.edges:
        if len(edge) != 2:
            raise ValueError(f"Edge entries must be [from, to]. Got: {edge}")
        graph_builder.add_edge(edge[0], edge[1])

    graph_builder.set_finish_point(graph_config.finish_point)
    return graph_builder.compile()

