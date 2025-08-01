# agents/analyzer_agent.py

import pandas as pd
from utils.llm_utils import OllamaLLM, summarize, build_prompt
import yaml
from pathlib import Path

from utils.config_loader import load_config
from utils.calculations_utils import calculate_peak_infection, calculate_avg_days_infected, get_model_parameters

class AnalyzerAgent():
    def __init__(self, memory, model="mistral"):
        self.llm = OllamaLLM(model)
        self.memory = memory
        self.agent_logs = None
        self.infection_logs = None
        self.params_file = None
        self.column_desc = None

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
            df_agents = pd.read_csv("path/to/agent_logs.csv")
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

