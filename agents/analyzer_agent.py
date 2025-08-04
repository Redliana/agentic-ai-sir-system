# agents.analyzer_agent.py

import pandas as pd
from utils.analysis_tools import calculate_peak_infection, calculate_average_total_infected, calculate_peak_infection_std

class AnalyzerAgent:
    def __init__(self, logs_path: str):
        self.logs_path = logs_path
        self.data = pd.read_csv(self.logs_path)
    
    def analyze(self, question: str) -> dict:
        question = question.lower()
        results = {}

        if "how many" in question or "total infected" in question:
            avg_total = calculate_average_total_infected(self.data)
            results["avg_total_infected"] = (avg_total)

        if "peak" in question:
            peak, step = calculate_peak_infection(self.data)
            results["peak_infection"] = (peak)
            results["step_of_peak"] = (step)

        if "standard deviation" in question or "std" in question:
            std_peak = calculate_peak_infection_std(self.data)
            results["std_peak_infection"] = (std_peak)

        return results