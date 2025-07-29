# agents/analyzer_agent.py

import os
import pandas as pd
from agents.base_agent import OllamaLLM


class AnalyzerAgent():
    def __init__(self, memory):
        self.memory = memory

    def analyze(self, question, output_dir="logs"):
        csv_files = [f for f in os.listdir(output_dir) if f.endswith(".csv")]
        dfs = [pd.read_csv(os.path.join(output_dir, f)) for f in csv_files]
        full_df = pd.concat(dfs)

        self.memory.save("last_analysis_question", question)

        if "peak" in question:
            peak = full_df["num_infected"].max()
            result = f"The peak number of infected agents was {peak}."
        else:
            result = "I'm not sure how to answer that yet."
        
        self.memory.save(f"analysis_result_for_{question}", result)
        return result
