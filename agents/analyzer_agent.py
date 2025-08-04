# agents.analyzer_agent.py

import pandas as pd
from utils.analysis_tools import calculate_peak_infection, calculate_average_total_infected, calculate_peak_infection_std

class AnalyzerAgent:
    def __init__(self, logs_path):
        self.logs_path = logs_path

    def analyze(self, question: str) -> dict:
        df = pd.read_csv(self.logs_path)

        if "peak infection" in question.lower() and "standard deviation" in question.lower():
            return calculate_peak_infection_std(df)

        elif "when" in question.lower() and "peak infection" in question.lower():
            return calculate_peak_infection(df)

        elif "how many agents" in question.lower() and "infected" in question.lower():
            return calculate_average_total_infected(df)

        else:
            return {"error": "I don't know how to answer that question yet."}
        