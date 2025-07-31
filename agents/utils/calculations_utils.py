# utils/summary_utils.py

import pandas as pd

def calculate_peak_infection(df_agent_logs: pd.DataFrame) -> dict:
    df_agent_logs = pd.read_csv(df_agent_logs)
    grouped = df_agent_logs.groupby(["run_id", "step"])["state"].value_counts().unstack().fillna(0)
    result = {}
    for run_id, group in grouped.groupby(level=0):
        infected_series = group.loc[run_id]["I"]
        peak_step = infected_series.idxmax()
        peak_value = infected_series.max()
        result[run_id] = {"peak_step": int(peak_step), "peak_infection_times": int(peak_value)}
    return result

def calculate_avg_days_infected(df_agent_logs: pd.DataFrame) -> dict:
    infected_duration = df_agent_logs[df_agent_logs["state"] == "I"]
    durations = (
        infected_duration.groupby("agent_id")["step"]
        .agg(["min", "max"])
        .assign(duration=lambda x: x["max"] - x["min"] + 1)
    )
    return {
        "average_infected_duration": durations["duration"].mean(),
        "agent_count": len(durations)
    }

def get_model_parameters(config: dict) -> str:
    return "\n".join([f"- {k}: {v}" for k, v in config.items()])
