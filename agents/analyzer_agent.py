# agents/analyzer_agent.py

import pandas as pd
from agents.utils.llm_utils import OllamaLLM, summarize, build_prompt
import yaml
from pathlib import Path

from model.utils.config_loader import load_config
from agents.utils.calculations_utils import calculate_peak_infection, calculate_avg_days_infected, get_model_parameters

class AnalyzerAgent():
    def __init__(self, memory, model="mistral"):
        self.llm = OllamaLLM(model)
        self.memory = memory
        self.agent_logs = None
        self.infection_logs = None
        self.params_file = None
        self.column_desc = None

    def load_data(self, agent_log_path, infection_log_path, params_file):
        """
        Data loader function
        
        Loads in:
            agent_logs: tracks agent states per time step
            infection_event_logs: tracks infection events for infected and infector agent/group pairs per time step
            simulation_parameters: parameters (data assumptions) used for running the model
        """
        # Load in agent logs: tracking agent states per time step
        self.agent_logs = pd.read_csv(agent_log_path)
        # Load in infection event logs: tracking how infection spreads from agent/group to agent/group per time step
        self.infection_logs = pd.read_csv(infection_log_path)
        # Load in config file: get params for running simulation
        self.params_file = load_config(params_file)

    def load_column_descriptions(self, yaml_path):
        """
        Data loader function: loads the data description dictionary (columns from datasets)
        """
        with open(Path(yaml_path), "r") as file:
            self.column_desc = yaml.safe_load(file)

    def analyze(self, df_agents, df_infections, model_params, user_question):
        """
        Analyzer function (heavy lifter) that executes the summary, prompt, and response for the LLM Analyzer Agent based on 
        key words input by the user_question. Sometimes, a calculation is called to assist with answering the question.
            Args:
                df_agents: dataframe with agent/state logs across all time steps
                df_infections: dataframe with infection events logs across all time steps
                data_dict: data description dictionary 
                model_params: parameters used to run the model
                user_question   
        """
        summary_data = {}

        # Infection peak detection
        if "infection peak" in user_question.lower():
            summary_data["peak_infection_times"] = calculate_peak_infection(df_agents)

        # Average infection duration
        elif "average infection duration" in user_question.lower():
            summary_data["avg_infection_duration"] = calculate_avg_days_infected(df_infections)

        # Model parameters
        elif "model parameters" in user_question.lower():
            summary_data["model_parameters"] = get_model_parameters(model_params)

        else:
            summary_data["note"] = "Sorry, I didn't understand the question."

        # Use general utils to handle LLM logic
        summary = summarize(summary_data)
        prompt = build_prompt(user_question, summary)
        response = self.llm.generate(prompt, system="You are a helpful data analysis assistant.")

        return response

    def receive_message(self, message):
        # Message between agents
        print("Analyzer received:", message)

