# utils.analysis_tools.py

import pandas as pd
import numpy as np
from collections import defaultdict

def calculate_average_total_infected(df: pd.DataFrame) -> dict:
    """Calculate the average number of infected agents over the duration of a simulation."""
    infected_totals = defaultdict(int)
    run_ids = df["run_id"].unique()

    for run_id in run_ids:
        run_df = df[df["run_id"] == run_id]
        infected_agents = run_df[run_df["state"] == "I"]["agent_id"].unique()
        infected_totals[run_id] = len(infected_agents)

    avg_infected = round(np.mean(list(infected_totals.values())))
    return {"average_total_infected": avg_infected}

def calculate_peak_infection(df: pd.DataFrame) -> dict:
    """Calculate the average peak infection event over the duration of a simulation."""
    run_ids = df["run_id"].unique()
    peak_values = []
    peak_steps = []

    for run_id in run_ids:
        run_df = df[df["run_id"] == run_id]
        grouped = run_df.groupby("step")["state"].value_counts().unstack().fillna(0)
        if "I" in grouped.columns:
            peak_step = grouped["I"].idxmax()
            peak_value = grouped["I"].max()
            peak_values.append(peak_value)
            peak_steps.append(peak_step)

    return {
        "average_peak_infected": round(np.mean(peak_values)),
        "average_peak_step": round(np.mean(peak_steps))
    }

def calculate_peak_infection_std(df: pd.DataFrame) -> dict:
    """Calculate the standard deviation of peak infection across all runs of a simulation."""
    run_ids = df["run_id"].unique()
    peak_values = []

    for run_id in run_ids:
        run_df = df[df["run_id"] == run_id]
        grouped = run_df.groupby("step")["state"].value_counts().unstack().fillna(0)
        if "I" in grouped.columns:
            peak_value = grouped["I"].max()
            peak_values.append(peak_value)

    std_dev = round(np.std(peak_values))
    return {
        "std_dev_peak_infected": std_dev,
        "mean_peak_infected": round(np.mean(peak_values))
    }

