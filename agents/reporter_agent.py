# agents.reporter_agent.py

from utils.llm_utils import OllamaLLM

class ReporterAgent:
    def __init__(self, model="mistral"):
        self.llm = OllamaLLM(model)

    def report(self, user_question: str, analysis_results: dict) -> str:
        # Construct the LLM prompt
        prompt = f"""
        You are a helpful model analysis assistant.
        The user asked: "{user_question}"
        Based on the data analysis, here are the results: {analysis_results}
        Explain the results in plain language to the user.
        """
        return self.llm.generate(prompt)
