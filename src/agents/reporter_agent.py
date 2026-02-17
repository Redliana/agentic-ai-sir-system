# src/agents/reporter_agent.py

"""
Reporter Agent is responsible for reporting analyzed calculations.
"""

# Import dependencies
from core.providers.factory import create_llm_provider
from core.providers.llm.base import LLMProvider

class ReporterAgent:
    def __init__(self, model="mistral", domain_config=None, llm_provider: LLMProvider = None):
        self.domain_config = domain_config or {}
        provider_cfg = dict(self.domain_config.get("providers", {}).get("llm", {}))
        if not provider_cfg:
            provider_cfg = {"type": "ollama", "model": model}
        elif "model" not in provider_cfg:
            provider_cfg["model"] = model
        self.llm = llm_provider or create_llm_provider(provider_cfg)
        self.report_system_prompt = self.domain_config.get("prompts", {}).get(
            "report_system_prompt",
            "You are an expert analyst. Summarize results clearly for a general audience.",
        )

    def report(self, user_question, analysis_results):
        """Use an LLM to summarize the analysis results in a human-readable format."""
        prompt = f"""
        You are asked to generate a report from analysis results.

        The user asked: "{user_question}"

        Here are the analysis results (in dictionary format):
        {analysis_results}

        Please explain the results clearly and concisely in plain language for a general audience.
        Avoid repeating the dictionary format. Focus on summarizing key insights.
        If any values are missing, simply note that you couldn't determine the results.
        """

        return self.llm.generate(prompt=prompt, system=self.report_system_prompt)
