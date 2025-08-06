# agents.analyzer_agent.py

import pandas as pd
from utils.analysis_tools import (
    calculate_peak_infection, 
    calculate_average_total_infected, 
    calculate_peak_infection_std, 
    plot_state_dynamics,
    calculate_infection_decline_rate,
    calculate_time_to_half_infected,
    calculate_recovery_rate_post_peak,
    calculate_reinfection_count,
    calculate_agents_never_recovered,
    calculate_final_state_distribution
)

class AnalyzerAgent:
    def __init__(self, state_logs: str):
        self.state_logs = state_logs
        self.state_data = pd.read_csv(self.state_logs)
    
    def analyze(self, question: str) -> dict:
        question = question.lower()
        results = {}

        # If user asks about how total infection numbers
        if "agents infected" in question or "total infected population" in question or "population infected" in question:
            avg_total = calculate_average_total_infected(self.state_data)
            results["avg_total_infected"] = {"total number of infected": (avg_total)}

        # If user asks about peak infection
        if "peak infected" in question or "peak infection" in question:
            peak, step = calculate_peak_infection(self.state_data)
            results["peak_infection"] = {"number of infected at peak infection step": (peak)}
            results["step_of_peak"] = {"peak infection step": (step)}

        # If user asks about peak infection standard deviation
        if "peak infection" in question and "standard deviation" in question or "std" in question:
            std_peak = calculate_peak_infection_std(self.state_data)
            results["std_peak_infection"] = {"peak infection standard deviation": (std_peak)}

        # If user asks to plot the SIR curves
        if "plot" in question or "graph" in question or "sir curve" in question:
            print("Generating state dynamics plot...")
            plot_state_dynamics(self.state_data)

        # If user asks about when the infection begins to decrease
        if "infection decreases" in question or "infection rate" in question and "after peak" in question:
            avg_decline = calculate_infection_decline_rate(self.state_data)
            results["avg_infection_decline"] = {"the infection rate post peak infection (%)": (avg_decline)}

        # If user asks about how quickly the infection spreads (infection rate)
        if "when will half population" in question and "be infected" in question or "how quickly" in question and "infection spreads" in question or "infection rate" in question:
            avg_step = calculate_time_to_half_infected(self.state_data)
            results["how_quickly_spreads"] = {"infection rate": (avg_step)}

        # If user asks about the recovery rate post infection peak
        if "after peak" in question and "recovery rate" in question or "rate of recovery" in question:
            recovery_rates = calculate_recovery_rate_post_peak(self.state_data)
            results["recovery_rate"] = {"recovery rate post infection peak (%)": (recovery_rates)}

        # If user asks about reinfection counts
        if "reinfection counts" in question or "reinfection probability" in question:
            avg_reinfected = calculate_reinfection_count(self.state_data)
            results["reinfection_counts"] = {"number of agents reinfected": (avg_reinfected)}

        # If user asks about number of agents that never recovered from infection
        if "never recovered" in question or "infected" in question and "forever":
            never_recovered = calculate_agents_never_recovered
            results["never_recovered"] = {"number of agents that never recovered": (never_recovered)}

        # If user asks about the final distribution of infection states at the end of the simulation
        if "distribution" in question and "infection states" in question or "agent states" in question:
            avg_counts = calculate_final_state_distribution(self.state_data)
            results["infection_state_distribution"] = {"final infection state distribution": (avg_counts)}

        return results