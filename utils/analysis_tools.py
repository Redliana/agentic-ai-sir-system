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
    
    This calculation uses the agent state log data.
    
    For each simulation run_id:
        Filters the dataframe to just that run.
        Filters for all unique agents that were ever in state 'I'
        Stores the count of all those agents in a dictionary.
   
    Averages the total number of infected agents across all runs.
    """
    infected_counts = []
    for run_id in df["run_id"].unique():
        run_df = df[df["run_id"] == run_id]
        unique_infected = run_df[run_df["state"] == "I"]["agent_id"].unique()
        count = len(unique_infected)
        print(f"Run {run_id}: {count} agents were infected.")
        infected_counts.append(count)

    avg_infected = round(np.mean(infected_counts))
    print(f"Average infected agents across runs: {avg_infected}")
    return avg_infected

def calculate_peak_infection(df: pd.DataFrame) -> tuple:
    """
    Calculates the average number of infected agents and the average step at which peak infection events occur.
    This tells you how bad the worst infection spike was, and when it usually happened in a simulation.
    
    This calculation uses the agent state log data.
    
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
    
    This calculation uses the agent state log data.
    
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
        
        This calculation uses the agent state log data.

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

def calculate_infection_decline_rate(df: pd.DataFrame) -> float:
    """
    Calculates the average rate of decline in infections from the peak to the final step of the simulation.
    This is done per run and averaged across all runs.

    This calculation uses the agent state log data.
    """
    decline_rates = []

    for run_id in df["run_id"].unique():
        run_df = df[df["run_id"] == run_id]
        infected_per_step = (
            run_df[run_df["state"] == "I"]
            .groupby("step")["agent_id"]
            .nunique()
            .sort_index()
        )

        if infected_per_step.empty:
            continue

        peak_step = infected_per_step.idxmax()
        final_step = infected_per_step.index.max()

        peak_infected = infected_per_step.loc[peak_step]
        final_infected = infected_per_step.loc[final_step]

        # Avoid division by zero
        step_diff = final_step - peak_step
        if step_diff <= 0:
            continue

        rate_of_decline = (final_infected - peak_infected) / step_diff
        decline_rates.append(rate_of_decline)

    avg_decline = round(np.mean(decline_rates), 2) if decline_rates else None

    return round(avg_decline * 100, 1)
        

def calculate_time_to_half_infected(df: pd.DataFrame) -> dict:
    """
    Calculates when half the population becomes infected.
    Calculates per run and then averages across all runs, returning average result.
    This calculation explains how quickly the infection spreads throughout the population.

    This calculation uses the agent state log data.
    """
    results = {}
    for run_id, group in df[df["state"] == "I"].groupby("run_id"):
        total_agents = df[df["run_id"] == run_id]["agent_id"].nunique()
        infected_by_step = group.groupby("step")["agent_id"].nunique().cumsum()
        step_50 = infected_by_step[infected_by_step >= (0.5 * total_agents)].index.min()
        results[run_id] = step_50 if not pd.isna(step_50) else None
    avg_step = round(np.nanmean(list(results.values())))
    return avg_step

def calculate_recovery_rate_post_peak(df: pd.DataFrame) -> float:
    """
    Calculates the average recovery rate after peak infection step for each run.
    
    Recovery rate is defined as:
    (# of recovered agents after peak) / (# of infected agents after peak)
    
    This calculation uses the agent state log data.
    """
    recovery_rates = []

    for run_id in df["run_id"].unique():
        run_df = df[df["run_id"] == run_id]
        # Count infected per step and find peak
        infected_per_step = (
            run_df[run_df["state"] == "I"]
            .groupby("step")["agent_id"]
            .nunique()
            .sort_index()
        )

        if infected_per_step.empty:
            continue

        peak_step = infected_per_step.idxmax()
        # Infected and recovered agents after the peak
        infected_after_peak = run_df[(run_df["state"] == "I") & (run_df["step"] > peak_step)]["agent_id"].nunique()
        recovered_after_peak = run_df[(run_df["state"] == "R") & (run_df["step"] > peak_step)]["agent_id"].nunique()
        
        if infected_after_peak == 0:
            continue 

        rate = recovered_after_peak / infected_after_peak
        recovery_rates.append(rate)
        
        recovery_rates_post_infection = round(np.mean(recovery_rates), 3)

    return round(recovery_rates_post_infection * 100, 1)

def calculate_reinfection_count(df: pd.DataFrame) -> dict:
    """
    Calculates how many agents were infected more than once.
    Returns the average number of reinfected agents across all runs.

    This calculation uses the agent state log data.
    """
    infected_agents = df[df["state"] == "I"].groupby(["run_id", "agent_id"]).size()
    reinfected = infected_agents[infected_agents > 1]
    total_reinfected = reinfected.groupby("run_id").size()
    avg_reinfected = round(total_reinfected.mean())
    return avg_reinfected

def calculate_agents_never_recovered(df: pd.DataFrame) -> dict:
    """
    Calculates how many agents were infected during the duration of the simulation.
    That is, how many agents never recovered.

    This calculation uses the agent state log data.
    """
    recovered = df[df["state"] == "R"]["agent_id"].unique()
    infected = df[df["state"] == "I"]["agent_id"].unique()
    never_recovered = set(infected) - set(recovered)
    return len(never_recovered)

def calculate_final_state_distribution(df: pd.DataFrame) -> dict:
    """
    Calculates the average population distribution of S/I/R infection states at the final timestep across all runs.

    This calculation uses the agent state log data.
    """
    final_counts = []

    for run_id in df["run_id"].unique():
        run_df = df[df["run_id"] == run_id]
        final_step = run_df["step"].max()
        final_df = run_df[run_df["step"] == final_step]
        counts = final_df["state"].value_counts(normalize=False).to_dict()
        
        # Ensure S/I/R keys are always present
        for state in ["S", "I", "R"]:
            counts.setdefault(state, 0)

        final_counts.append(counts)

    # Average counts across all runs
    avg_counts = {
        "Susceptible": round(np.mean([run["S"] for run in final_counts])),
        "Infected": round(np.mean([run["I"] for run in final_counts])),
        "Recovered": round(np.mean([run["R"] for run in final_counts]))
    }
    return avg_counts

def calculate_infection_decrease_after_step(df: pd.DataFrame, step: int) -> dict:
    """
    Calculates the probability that the number of infected agents decreases after a specified step.
    Users must specify which step they want to analyze.

    This calculation uses the agent state log data.
    """
    infected = df[df["state"] == "I"]
    grouped = infected.groupby(["run_id", "step"])["agent_id"].nunique().unstack(fill_value=0)

    decrease_count = 0
    total_runs = 0

    for run_id, row in grouped.iterrows():
        if step in row and (step + 1) in row:
            total_runs += 1
            if row[step + 1] < row[step]:
                decrease_count += 1

    prob = decrease_count / total_runs if total_runs > 0 else 0

    return {
        "step_checked": step,
        "runs_with_decrease": decrease_count,
        "total_valid_runs": total_runs,
        "prob_decrease_after_step": round(prob, 3)
    }
