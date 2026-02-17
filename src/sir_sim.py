"""Compatibility wrapper for the SIR domain model runner.

The canonical implementation now lives at ``domains.sir.model.runner``.
"""

import yaml

from domains.sir.model.runner import Agent, Environment, Group, Model, main

__all__ = ["Environment", "Agent", "Group", "Model", "main"]


if __name__ == "__main__":
    default_params = {
        "seed": 42,
        "num_runs": 100,
        "num_agents": 1000,
        "num_steps": 28,
        "num_contacts": 10,
        "infection_prob": 0.3,
        "infection_duration": 3,
        "recovery_prob": 0.1,
    }

    try:
        with open("params.yaml", "r") as file:
            params = yaml.safe_load(file)
    except FileNotFoundError:
        params = default_params

    main(params)

