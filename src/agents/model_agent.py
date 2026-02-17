# src/agents/model_agent.py

"""
Model Agent is resonsible for running the SIR model.
"""

# Import dependencies
from domains.sir.model.runner import main

class ModelAgent:
    def run(self, params):
        main(params)
    
