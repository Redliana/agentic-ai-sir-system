# src/agents/model_agent.py

"""
Model Agent is responsible for running the active domain model runner.
"""

# Import dependencies
import importlib

class ModelAgent:
    def __init__(self, domain_config=None):
        self.domain_config = domain_config or {}
        model_cfg = self.domain_config.get("model", {})
        self.runner_module = model_cfg.get("runner_module", "domains.sir.model.runner")
        self.runner_callable = model_cfg.get("runner_callable", "main")

        module = importlib.import_module(self.runner_module)
        self._runner_fn = getattr(module, self.runner_callable)

    def run(self, params):
        return self._runner_fn(params)
    
