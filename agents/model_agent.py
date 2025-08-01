# agents/model_agent.py

import os
from sir_sim import main

class ModelAgent:
    def __init__(self, memory):
        self.memory = memory
        
    def run(self):
        result = main()
        #self.memory.save("last_run_params", params)
        self.memory.save("output_directory", result)
        return result
    