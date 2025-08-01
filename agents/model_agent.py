# agents/model_agent.py

import os
from sir_sim import main

class ModelAgent:
    def __init__(self, memory):
        self.memory = memory
        
    def run(self, output_path="logs"):
        os.makedirs(output_path, exist_ok=True)
        # TODO: update this path such that we are running the main.py script from model
        result = main()
        #self.memory.save("last_run_params", params)
        self.memory.save("output_directory", output_path)
        return result
    