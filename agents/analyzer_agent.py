# agents/analyzer_agent.py

import os
import pandas as pd
from agents.base_agent import OllamaLLM
import yaml
from pathlib import Path

class AnalyzerAgent():
    def __init__(self, memory, model="mistral"):
        self.llm = OllamaLLM(model)
        self.memory = memory
        self.agent_logs = None
        self.infection_logs = None
        self.column_desc = None

    def load_data(self, agent_log_path, infection_log_path):
        self.agent_logs = pd.read_csv(agent_log_path)
        self.infection_logs = pd.read_csv(infection_log_path)

    def load_column_descriptions(self, yaml_path):
        with open(Path(yaml_path), "r") as file:
            self.column_desc = yaml.safe_load(file)

    def summarize_data(self):
        peak_step = (
            self.agent_logs.groupby("step")["state"]
            .apply(lambda x: (x == "I").sum())
            .idxmax()
        )
        return {
            "peak_infection_step": int(peak_step),
            "total_infections": int((self.agent_logs["state"] == "I").sum()),
            "total_steps": int(self.agent_logs["step"].max())
        }

    def build_prompt(self, user_question, summary_data):
        desc_text = "\n".join([f"- `{col}`: {desc}" for col, desc in self.column_desc.items()])

        return f"""You are a data analysis agent. You have access to simulation data and its metadata. 
        Here is a description of each column in the data:
        {desc_text}

        Here are some summary statistics about the data:
        - Peak infection occurred at step: {summary_data['peak_infection_step']}
        - Total infections: {summary_data['total_infections']}
        - Total simulation steps: {summary_data['total_steps']}

        Now answer this user question using the information above:
        User: {user_question}
        """

    def analyze(self, user_question="How many agents recovered?"):
        summary = self.summarize_data()
        prompt = self.build_prompt(user_question, summary)
        response = self.llm.generate(prompt, system="You are a helpful data analysis assistant.")
        return response

    def receive_message(self, message):
        # Message between agents
        print("Analyzer received:", message)

