"""Load and normalize workflow routing configuration from YAML files."""

import os
from typing import Any, Dict, Optional

import yaml

from .graph import ConditionalRoute, GraphConfig


DEFAULT_PLATFORM_CONFIG = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "configs", "platform.yaml")
)


def _load_yaml(path: str) -> Dict[str, Any]:
    with open(path, "r") as file:
        data = yaml.safe_load(file) or {}
    return data


def load_graph_config(config_path: Optional[str] = None, profile: str = "default") -> GraphConfig:
    """Load graph routing config for a named profile."""
    path = config_path or DEFAULT_PLATFORM_CONFIG
    if not os.path.exists(path):
        raise FileNotFoundError(f"Platform config not found: {path}")

    platform_config = _load_yaml(path)
    profile_config = platform_config.get("profiles", {}).get(profile)
    if not profile_config:
        raise KeyError(f"Profile '{profile}' not found in {path}")

    graph_data = profile_config.get("graph")
    if not graph_data:
        raise KeyError(f"Profile '{profile}' does not define a 'graph' section in {path}")

    conditional_routes = []
    for route in graph_data.get("conditional_routes", []):
        conditional_routes.append(
            ConditionalRoute(
                source=route["source"],
                intent_key=route.get("intent_key", "user_intent"),
                routes=route["routes"],
            )
        )

    return GraphConfig(
        entry_point=graph_data["entry_point"],
        finish_point=graph_data["finish_point"],
        conditional_routes=conditional_routes,
        edges=graph_data.get("edges", []),
    )

