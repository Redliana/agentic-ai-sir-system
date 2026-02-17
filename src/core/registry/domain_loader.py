"""Load active domain settings for plugin-based workflows."""

import os
from typing import Any, Dict, Optional

import yaml


DEFAULT_DOMAINS_CONFIG = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "configs", "domains.yaml")
)


def _load_yaml(path: str) -> Dict[str, Any]:
    with open(path, "r") as file:
        return yaml.safe_load(file) or {}


def load_active_domain(
    domains_config_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Load active domain metadata and expanded domain config."""
    domains_path = domains_config_path or DEFAULT_DOMAINS_CONFIG
    if not os.path.exists(domains_path):
        raise FileNotFoundError(f"Domains config not found: {domains_path}")

    domains_config = _load_yaml(domains_path)
    active_domain = domains_config.get("active_domain")
    domains = domains_config.get("domains", {})
    if not active_domain or active_domain not in domains:
        raise KeyError(f"Active domain '{active_domain}' not found in {domains_path}")

    domain_entry = domains[active_domain]
    domain_config_path = domain_entry.get("config_path")
    if not domain_config_path:
        raise KeyError(f"Domain '{active_domain}' is missing config_path in {domains_path}")
    if not os.path.isabs(domain_config_path):
        domain_config_path = os.path.normpath(
            os.path.join(os.path.dirname(domains_path), "..", domain_config_path)
        )

    domain_config = _load_yaml(domain_config_path)
    return {
        "name": active_domain,
        "package": domain_entry.get("package", ""),
        "config_path": domain_config_path,
        "config": domain_config,
    }
