"""SIR domain model runner."""

# === Import Libraries ===
import pandas as pd
import random
import yaml

# === Environment ===
class Environment:
    """Defines the environment parameters for the simulation."""

    def __init__(self, infection_prob, infection_duration, recovery_prob):
        """
        Initialize the environment.

        Args:
            infection_prob (float): Probability of infection.
            infection_duration (float): Duration of infection.
        """
        self.infection_prob = infection_prob
        self.infection_duration = infection_duration
        self.recovery_prob = recovery_prob

    def update(self, infection_prob_new, infection_duration_new, recovery_prob_new):
        """
        Update the environment parameters.

        Args:
            infection_prob_new (float): New probability of infection.
            infection_duration_new (float): New duration of infection.
        """
        self.infection_prob = infection_prob_new
        self.infection_duration = infection_duration_new
        self.recovery_prob = recovery_prob_new

# === Agent ===
class Agent:
    """Defines an agent in the simulation."""

    def __init__(self, unique_id, dState="S"):
        """
        Initialize the agent.

        Args:
            unique_id (int): Unique identifier for the agent.
            dState (str): Disease state of the agent ('S', 'I', or 'R').
        """
        self.unique_id = unique_id
        self.dState = dState
        self.infected_by = None     # agent_id of infectious agent
        self.infection_step = None  # step at which agent becomes infected

    def update_state(self, group_states, environment, infectious_agents, step):
        """
        Update the state of the agent based on group states and environment.

        Args:
            group_states (list): List of disease states in the group.
            environment (Environment): The environment instance.
            infectious_agents (list): Agents currently in state 'I' in the group.
            step(int): Current simulation step.
        """
        infection_prob = environment.infection_prob
        infection_duration = environment.infection_duration
        recovery_prob = environment.recovery_prob
        nI = group_states.count('I')

        if self.dState == 'S':
            if nI > 0 and random.random() < (1 - (1 - infection_prob) ** nI):
                # Pick a random infector from the infectious agents
                infector = random.choice(infectious_agents)
                self.dState = 'I'
                self.infected_by = infector.unique_id
                self.infection_step = step
        
        elif self.dState == 'I':
            if random.random() < recovery_prob:
                self.dState = 'R'

    def infection_duration(self, current_step):
        """Return how long this agent has been infected at the current step."""
        if self.dState == "I" and self.infection_step is not None:
            return current_step - self.infection_step
        return None

# === Group ===     
class Group:
    """Defines a group of agents in the simulation."""

    def __init__(self, agents, group_id):
        """
        Initialize the group.

        Args:
            agents (list): List of Agent objects in the group.
        """
        self.agents = agents
        self.group_id = group_id

        # Assign group_ids for agents
        for agent in self.agents:
            agent.group_id = group_id

    def update(self, environment, step):
        """
        Update all agents in the group.

        Args:
            environment (Environment): The environment instance.
            step (int): Current simulation step.
        """
        group_states = [agent.dState for agent in self.agents]
        infectious_agents = [agent for agent in self.agents if agent.dState == "I"]

        for agent in self.agents:
            agent.update_state(group_states, environment, infectious_agents, step)

# === Model ===
class Model:
    """Defines the simulation model."""

    def __init__(
            self, 
            num_agents, 
            num_steps, 
            num_contacts, 
            environment, 
            seed, 
            run_id):
        """
        Initialize the model.

        Args:
            num_agents (int): Number of agents.
            num_steps (int): Number of simulation steps.
            num_contacts (int): Size of groups.
            environment (Environment): The environment instance.
            seed (int): Random seed.
            run_id (int): Unique identifier for the simulation run.
        """
        self.num_agents = num_agents
        self.num_steps = num_steps
        self.num_contacts = num_contacts
        self.environment = environment
        self.seed = seed
        self.run_id = run_id
        
        self.agents = self._initialize_agents()
        self.groups = self._initialize_groups()

        self.agent_state_logs = []
        self.infection_event_logs = []

        self.agent_lookup = {agent.unique_id: agent for agent in self.agents}

    def _initialize_agents(self):
        """Initialize agents with unique IDs and one infectious agent."""
        agents = []
        infected_id = random.randint(0, self.num_agents - 1)
        for i in range(self.num_agents):
            agent = Agent(i, dState="I" if i == infected_id else "S")
            if i == infected_id:
                agent.infection_step = 0
            agents.append(agent)
        return agents

    def _initialize_groups(self, lambda_param=1/10, min_size=3, max_size=30):
        """
        Initialize groups with sizes drawn from an exponential distribution.

        Args:
            lambda_param (float): Rate parameter (1/mean) for the exponential distribution.
            min_size (int): Minimum group size.
            max_size (int): Maximum group size.

        Returns:
            list: List of Group objects.
        """
        agents = self.agents[:]
        random.shuffle(agents)
        groups, group_id = [], 0

        while agents:
            group_size = min(len(agents), max(min_size, min(int(random.expovariate(lambda_param)), max_size)))
            group_agents = agents[:group_size]
            group = Group(group_agents, group_id)
            groups.append(group)
            agents = agents[group_size:]
            group_id += 1
        return groups

    def log_agent_states(self, step):
        """
        Log agent states per times step.
        Logging to memory.
        """
        for agent in self.agents:
            self.agent_state_logs.append({
                "run_id": self.run_id,
                "step": step,
                "agent_id": agent.unique_id,
                "state": agent.dState
            })

    def log_infections(self, step):
        """
        Log infection events with infector agents and infected agents per time step
        Logging to memory.
        """
        for agent in self.agents:
            self.agent_state_logs.append({
                "run_id": self.run_id, "step": step,
                "agent_id": agent.unique_id, "state": agent.dState
            })

            if agent.dState == "I" and agent.infection_step == step:
                infector = self.agent_lookup.get(agent.infected_by)
                self.infection_event_logs.append({
                    "run_id": self.run_id,
                    "step": step,
                    "infected_id": infector.unique_id if infector else None,
                    "infected_group_id": getattr(infector, "group_id", None) if infector else None,
                    "infector_id": agent.unique_id,
                    "infector_group_id": getattr(agent, "group_id", None),
                    "duration": step - infector.infection_step if infector else None
                })
    
    def step(self, step):
        """
        Run a single simulation step and log agent states and infection events per step.
        """
        for group in self.groups:
            group.update(self.environment, step)
        self.log_agent_states(step)
        self.groups = self._initialize_groups()
    
    def run(self):
        """Run the simulation and log SIR counts."""
        for step in range(self.num_steps):
            self.step(step)

# === Main ===
def main(params):
    """
    Main function to run the simulation.
    Logging all agent states and infection events per run. 
    """
    
    all_agent_state_logs = []

    print("Starting main simulation loop")
    for run_id in range(params["num_runs"]):
        env = Environment(params["infection_prob"], params["infection_duration"], params["recovery_prob"])
        model = Model(params["num_agents"], params["num_steps"], params["num_contacts"], env, params["seed"] + run_id, run_id)
        model.run()
        all_agent_state_logs.extend(model.agent_state_logs)
        print(f"Run {run_id + 1} complete.")
    
    # Convert to DataFrames
    agent_df = pd.DataFrame(all_agent_state_logs)
    # Convert to csv
    agent_df.to_csv("src/logs/all_agent_logs.csv", index=False)

    return

if __name__ == "__main__":
    default_params = {
        "seed": 42,
        "num_runs": 100,
        "num_agents": 1000,
        "num_steps": 28,
        "num_contacts": 10,
        "infection_prob": 0.3,
        "infection_duration": 3,
        "recovery_prob": 0.1
    }

    try:
        with open("params.yaml", "r") as file:
            params = yaml.safe_load(file)
    except FileNotFoundError:
        params = default_params 
    main(params)
    
