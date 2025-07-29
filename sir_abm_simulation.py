"""sir_abm_simulation.py"""

"""
SIR Agent-Based Model Simulation
Author: Argonne National Laboratory
Date: Updated June 7, 2025
"""

# --- Import libraries ---
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random
from datetime import datetime, date, timedelta
from itertools import chain

# --- Utility Functions ---
def bold_text(text):
    """Returns bolded text for terminal display."""
    bold_start = '\033[1m'
    bold_end = '\033[0m'
    return bold_start + text + bold_end

def flatten(nested_list):
    """Flattens a nested list."""
    return [item for sublist in nested_list for item in sublist]

# --- Classes ---
class Environment:
    """Defines the environment for the simulation."""
    def __init__(
            self, 
            infection_rate, 
            infection_dur
        ):
        self.infection_rate = infection_rate
        self.infection_dur = infection_dur

class Agent:
    """Defines an agent with a disease state."""
    def __init__(
            self, 
            dState
        ):
        self.dState = dState

class Model:
    """Defines the model parameters and log."""
    def __init__(
            self, 
            current_datetime, 
            num_agents, 
            num_steps,
            infection_dur,
            infection_rate, 
            group_size, 
            seed
        ):
        
        self.current_datetime = current_datetime
        self.num_agents = num_agents
        self.num_steps = num_steps
        self.infection_dur = infection_dur
        self.infection_rate = infection_rate
        self.group_size = group_size
        self.seed = seed
        self.log = []

# --- Creation Functions ---
def create_environment(infection_rate, infection_dur):
    """Creates an instance of the Environment class."""
    return Environment(infection_rate, infection_dur)

def create_agents_zero(num_agents, num_zeroes):
    """Creates agents with num_zeroes infectious agents."""
    return [Agent("I" if i < num_zeroes else "S") for i in range(num_agents)]

def create_groups(agents, size):
    """Creates groups of agents of specified size."""
    random.shuffle(agents)
    return [agents[i:i + size] for i in range(0, len(agents), size)]

# --- Update Logic ---
def update_group(group, environment):
    """Updates the states of agents in a group."""
    group_states = [agent.dState for agent in group]

    def update_state(agent, group_states):
        if agent.dState == "S":
            nI = group_states.count("I")
            if nI > 0 and random.random() < (1 - (1 - environment.infection_rate) ** nI):
                agent.dState = "I"
        elif agent.dState == "I":
            if random.random() < 1 / environment.infection_dur:
                agent.dState = "R"
        return agent.dState

    group_states = [agent.dState for agent in group]
    return [update_state(agent, group_states) for agent in group]

def update_agents(groups, environment):
    """Updates disease states of agents in all groups."""
    for group in groups:
        update_group(group, environment)

def update_model(model, groups):
    """Updates the model log based on the groups."""
    agent_states = flatten([get_agent_states(group) for group in groups])
    counts = [agent_states.count(state) for state in ["S", "I", "R"]]
    model.log.append(counts)

# --- Analysis Functions ---
def get_agent_states(agents):
    """Returns the disease states of all agents."""
    return [agent.dState for agent in agents]

def print_log_table(log):
    """Prints the simulation log in a tabular format."""
    log_array = np.array(log).T
    df = pd.DataFrame({"S": log_array[0], "I": log_array[1], "R": log_array[2]})
    print(df)

def plot_data(log, today, line_width=1.0):
    """Plots the SIR data."""
    log_array = np.array(log).T
    dates = pd.date_range(start=today, periods=len(log_array[0]), freq="D")
    labels = ["S", "I", "R"]
    colors = ["blue", "red", "green"]

    plt.figure(figsize=(10, 6))
    for data, label, color in zip(log_array, labels, colors):
        plt.plot(dates, data, label=label, color=color, linewidth=line_width)
    plt.xlabel("Date")
    plt.ylabel("Number of People")
    plt.title("SIR Simulation Results")
    plt.legend()
    plt.grid(True)
    plt.show()

# --- Simulation API ---
def run_simulation(num_runs, num_agents, num_steps, group_size, infection_rate, infection_dur):
    """Runs the SIR simulation for multiple runs."""
    model_logs = []
    for run in range(num_runs):
        random.seed(run)
        environment = create_environment(infection_rate, infection_dur)
        agents = create_agents_zero(num_agents, num_zeroes=10)
        groups = create_groups(agents, group_size)
        model = Model(datetime.now(), num_agents, num_steps, infection_dur, infection_rate, group_size, run)

        for step in range(num_steps):
            update_agents(groups, environment)
            update_model(model, groups)
            groups = create_groups(agents, group_size)

        model_logs.append(model.log)
    return model_logs

# --- Main Entry Point ---
if __name__ == "__main__":
    # Simulation Parameters
    num_runs = 30
    num_agents = 1000
    num_steps = 28
    group_size = 10
    infection_rate = 0.1
    infection_dur = 3.0

    # Run Simulation
    today = date.today()
    model_logs = run_simulation(num_runs, num_agents, num_steps, group_size, infection_rate, infection_dur)

    # Analyze Results
    print_log_table(model_logs[0])
    plot_data(model_logs[0], today)