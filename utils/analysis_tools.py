# utils.analysis_tools.py

"""
This is a toolkit used by the Analyzer Agent to perform math on the log data and return the results to the Reporter Agent.
The Analyzer Agent receives a user question and performs the correct calculation required to answer the question.
It then returns the result to the Reporter Agent.
"""

# Import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

def calculate_average_total_infected(df: pd.DataFrame) -> dict:
    """
    Calculate the average number of infected agents over the duration of a simulation.
    This gives you an idea of how widespread the infection was on average — regardless of when infection happened in the run.
    
    For each simulation run_id:
        Filters the dataframe to just that run.
        Filters for all unique agents that were ever in state 'I'
        Stores the count of all those agents in a dictionary.
   
    Averages the total number of infected agents across all runs.
    """
    infected_totals = defaultdict(int)
    run_ids = df["run_id"].unique()
    for run_id in run_ids:
        run_df = df[df["run_id"] == run_id]
        infected_agents = run_df[run_df["state"] == "I"]["agent_id"].unique()
        infected_totals[run_id] = len(infected_agents)
    avg_infected = round(np.mean(list(infected_totals.values())))
    return round(avg_infected)

def calculate_peak_infection(df: pd.DataFrame) -> tuple:
    """
    Calculates the average number of infected agents and the average step at which peak infection events occur.
    This tells you how bad the worst infection spike was, and when it usually happened in a simulation.
    
    Logic:
        Filters rows for where agents are in state 'I'
        Groups agents by run_id and step. 
        Counts the number of unique infected agents at each step.
    
    For each run:
        Peaks = the maximum number of infected agents across all steps.
        Steps = the step number where that peak happened.
    
    Averages both values across all runs.
    """
    grouped = df[df["state"] == "I"].groupby(["run_id", "step"])["agent_id"].nunique()
    peaks = grouped.groupby("run_id").max()
    steps = grouped.groupby("run_id").idxmax().apply(lambda x: x[1])
    return round(peaks.mean()), round(steps.mean())

def calculate_peak_infection_std(df: pd.DataFrame) -> dict:
    """
    Calculates the standard deviation (std) of peak infection events.
    A low standard deviation means the infection pattern is consistent across runs.
    A high standard deviation means infection peaks vary a lot from run to run — which might indicate instability or stochastic effects.

    Logic:
        Filters rows for where agents are in state 'I'
        Groups agents by run_id and step. 
        Counts the number of unique infected agents at each step.
        Calculates the max infected per run (peak infections).
        Returns the standard deviation of these peaks across all runs.
    """
    grouped = df[df["state"] == "I"].groupby(["run_id", "step"])["agent_id"].nunique()
    peaks = grouped.groupby("run_id").max()
    return round(peaks.std())

def plot_state_dynamics(df: pd.DataFrame):
        """
        Plots the SIR infection state curves for all simulation runs.

        Logic:
            For each run_id, find the agent infection states.

        """
        grouped = df.groupby(["run_id", "step", "state"]).size().reset_index(name="count")
        pivot_df = grouped.pivot_table(index=["run_id", "step"], columns="state", values="count", fill_value=0)

        # Makes the plots pretty
        color_map = {"S": "blue", "I": "red", "R": "green"}
        label_map = {"S": "Susceptible (S)", "I": "Infected (I)", "R": "Recovered (R)"}
        plotted_labels = set()

        # Plot for each run
        for run_id, run_data in pivot_df.groupby(level=0):
            run_data = run_data.droplevel(0)
            for state in ["S", "I", "R"]:
                label = label_map[state] if state not in plotted_labels else None
                plt.plot(
                    run_data.index,
                    run_data[state],
                    color=color_map[state],
                    alpha=0.6,
                    label=label
                )
                plotted_labels.add(state)

        plt.xlabel("Step")
        plt.ylabel("Agent Count")
        plt.title("Epidemic State Dynamics Per Run")
        plt.legend()
        plt.tight_layout()
        plt.show()
