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


def _resolve_domain_config_path(domains_path: str, domain_config_path: str) -> str:
    if not os.path.isabs(domain_config_path):
        candidate_from_config = os.path.normpath(
            os.path.join(os.path.dirname(domains_path), "..", domain_config_path)
        )
        candidate_from_cwd = os.path.normpath(os.path.join(os.getcwd(), domain_config_path))
        if os.path.exists(candidate_from_config):
            return candidate_from_config
        if os.path.exists(candidate_from_cwd):
            return candidate_from_cwd
        domain_config_path = candidate_from_config
    return domain_config_path


def load_domain(
    domain_name: str,
    domains_config_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Load domain metadata and expanded domain config by explicit domain name."""
    domains_path = domains_config_path or DEFAULT_DOMAINS_CONFIG
    if not os.path.exists(domains_path):
        raise FileNotFoundError(f"Domains config not found: {domains_path}")

    domains_config = _load_yaml(domains_path)
    domains = domains_config.get("domains", {})
    if not domain_name or domain_name not in domains:
        raise KeyError(f"Domain '{domain_name}' not found in {domains_path}")

    domain_entry = domains[domain_name]
    domain_config_path = domain_entry.get("config_path")
    if not domain_config_path:
        raise KeyError(f"Domain '{domain_name}' is missing config_path in {domains_path}")
    domain_config_path = _resolve_domain_config_path(domains_path, domain_config_path)

    domain_config = _load_yaml(domain_config_path)
    return {
        "name": domain_name,
        "package": domain_entry.get("package", ""),
        "config_path": domain_config_path,
        "config": domain_config,
    }


def load_active_domain(
    domains_config_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Load active domain metadata and expanded domain config."""
    domains_path = domains_config_path or DEFAULT_DOMAINS_CONFIG
    if not os.path.exists(domains_path):
        raise FileNotFoundError(f"Domains config not found: {domains_path}")

    domains_config = _load_yaml(domains_path)
    active_domain = domains_config.get("active_domain")
    return load_domain(domain_name=active_domain, domains_config_path=domains_path)
