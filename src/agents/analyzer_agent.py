# src/agents/analyzer_agent.py

"""
Analyzer Agent resolves analysis metrics from the active domain plugin.
"""

import importlib
from typing import Any, Dict, List

import pandas as pd


class AnalyzerAgent:
    def __init__(self, state_logs: str, domain_config: Dict[str, Any] = None):
        self.state_logs = state_logs
        self.state_data = pd.read_csv(self.state_logs)
        self.domain_config = domain_config or {}

        analysis_cfg = self.domain_config.get("analysis", {})
        self.metrics_module_path = analysis_cfg.get("metrics_module", "domains.sir.analysis.metrics")
        self.metric_rules: List[Dict[str, Any]] = analysis_cfg.get("metric_rules", [])
        self.metrics_module = importlib.import_module(self.metrics_module_path)

    def _matches(self, question: str, triggers: List[str]) -> bool:
        question_lower = question.lower()
        return any(trigger.lower() in question_lower for trigger in triggers)

    def _run_rule(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        function_name = rule["function"]
        fn = getattr(self.metrics_module, function_name)
        value = fn(self.state_data)

        if rule.get("plot_only", False):
            return {}

        output_key = rule.get("output_key", function_name)
        value_keys = rule.get("value_keys", [])
        description = rule.get("description", output_key)

        if value_keys and isinstance(value, tuple) and len(value_keys) == len(value):
            payload = {value_keys[i]: value[i] for i in range(len(value))}
            return {output_key: payload}

        return {output_key: {description: value}}

    def _analyze_with_rules(self, question: str) -> Dict[str, Any]:
        results: Dict[str, Any] = {}
        for rule in self.metric_rules:
            if self._matches(question, rule.get("triggers", [])):
                results.update(self._run_rule(rule))
        return results

    def analyze(self, question: str) -> dict:
        question = question.lower()

        if self.metric_rules:
            results = self._analyze_with_rules(question)
            if results:
                return results
            return {
                "message": (
                    "No analysis rule matched your question for the active domain. "
                    "Try asking for a supported metric."
                )
            }

        # Backward-compatible fallback for older configs without metric_rules.
        results = {}
        peak_fn = getattr(self.metrics_module, "calculate_peak_infection", None)
        avg_total_fn = getattr(self.metrics_module, "calculate_average_total_infected", None)
        peak_std_fn = getattr(self.metrics_module, "calculate_peak_infection_std", None)
        plot_fn = getattr(self.metrics_module, "plot_state_dynamics", None)
        decline_fn = getattr(self.metrics_module, "calculate_infection_decline_rate", None)
        half_fn = getattr(self.metrics_module, "calculate_time_to_half_infected", None)
        recovery_fn = getattr(self.metrics_module, "calculate_recovery_rate_post_peak", None)
        reinfect_fn = getattr(self.metrics_module, "calculate_reinfection_count", None)
        never_recovered_fn = getattr(self.metrics_module, "calculate_agents_never_recovered", None)
        final_dist_fn = getattr(self.metrics_module, "calculate_final_state_distribution", None)

        if avg_total_fn and (
            "agents infected" in question
            or "total infected population" in question
            or "population infected" in question
        ):
            avg_total = avg_total_fn(self.state_data)
            results["avg_total_infected"] = {"total number of infected": avg_total}

        if peak_fn and ("peak infected" in question or "peak infection" in question):
            peak, step = peak_fn(self.state_data)
            results["peak_infection"] = {"number of infected at peak infection step": peak}
            results["step_of_peak"] = {"peak infection step": step}

        if peak_std_fn and (
            ("peak infection" in question and "standard deviation" in question) or "std" in question
        ):
            std_peak = peak_std_fn(self.state_data)
            results["std_peak_infection"] = {"peak infection standard deviation": std_peak}

        if plot_fn and ("plot" in question or "graph" in question or "sir curve" in question):
            print("Generating state dynamics plot...")
            plot_fn(self.state_data)

        if decline_fn and (
            "infection decreases" in question
            or ("infection rate" in question and "after peak" in question)
        ):
            avg_decline = decline_fn(self.state_data)
            results["avg_infection_decline"] = {
                "the infection rate post peak infection (%)": avg_decline
            }

        if half_fn and (
            ("when will half population" in question and "be infected" in question)
            or ("how quickly" in question and "infection spreads" in question)
            or "infection rate" in question
        ):
            avg_step = half_fn(self.state_data)
            results["how_quickly_spreads"] = {"infection rate": avg_step}

        if recovery_fn and (
            ("after peak" in question and "recovery rate" in question)
            or "rate of recovery" in question
        ):
            recovery_rates = recovery_fn(self.state_data)
            results["recovery_rate"] = {"recovery rate post infection peak (%)": recovery_rates}

        if reinfect_fn and ("reinfection counts" in question or "reinfection probability" in question):
            avg_reinfected = reinfect_fn(self.state_data)
            results["reinfection_counts"] = {"number of agents reinfected": avg_reinfected}

        if never_recovered_fn and ("never recovered" in question or ("infected" in question and "forever" in question)):
            never_recovered = never_recovered_fn(self.state_data)
            results["never_recovered"] = {"number of agents that never recovered": never_recovered}

        if final_dist_fn and (
            ("distribution" in question and "infection states" in question) or "agent states" in question
        ):
            avg_counts = final_dist_fn(self.state_data)
            results["infection_state_distribution"] = {"final infection state distribution": avg_counts}

        return results

