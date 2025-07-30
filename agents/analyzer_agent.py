# agents/analyzer_agent.py

import os
import pandas as pd
from agents.base_agent import OllamaLLM


class AnalyzerAgent():
    def __init__(self, memory, model="mistral"):
        self.llm = OllamaLLM(model)
        self.memory = memory

    def analyze(self, question, output_dir="logs"):
        # Load all log csv files
        csv_files = [f for f in os.listdir(output_dir) if f.endswith(".csv")]
        dfs = [pd.read_csv(os.path.join(output_dir, f)) for f in csv_files]
        full_df = pd.concat(dfs)

        self.memory.save("last_analysis_question", question)

        # Summarize the data for context
        summary = self.summarize_data(full_df)

        system = (
            "You are an expert data analyst assistant for an epidemic simulation. "
            "You are given a dataset with the following columns: "
            "'timestep', 'num_susceptible', 'num_infected', 'num_recovered'. "
            "Use this data summary to answer the user's question as clearly and concisely as possible. "
            "If relevant, include key stats or describe trends. "
        )

        prompt = f"""User's Question: {question} Data Summary: {summary}""".strip()

        result = self.llm.generate(prompt=prompt, system=system)
        self.memory.save(f"analysis_result_for_{question}", result)
        return result
    
    def receive_message(self, message):
        # Message between agents
        print("Analyzer received:", message)

    def summarize_data(self, df):
        summary = {
            "total_rows": len(df),
            "num_runs": df["timestep"].nunique(),
            "peak_infected": df["num_infected"].max(),
            "avg_infected": round(df["num_infected"].mean(), 2),
            "total_recovered": int(df["num_recovered"].sum()),
            "avg_susceptible": round(df["num_susceptible"].mean(), 2),
        }
        return "\n".join(f"{k}: {v}" for k, v in summary.items())
