# agents/ui_agent.py

from utils.llm_utils import OllamaLLM
from memory.json_memory import JSONMemory

class UIAgent:
    def __init__(self, memory, model="mistral", test_mode=False):
        self.llm = OllamaLLM(model)
        self.memory = memory
        self.test_mode = test_mode

    def get_user_input(self):
        if self.test_mode:
            response = {
                "beta": 0.3,
                "gamma": 0.1,
                "initial_infected": 10,
                "population": 1000,
                "timesteps": 50,
                "runs": 5
            }
        else:
            prompt = "Ask the user for parameters to run the SIR model."
            response = self.llm.generate(prompt)

        self.memory.save("sir_user_input_prompt", response)
        return response


    def notify_sim_complete(self):
        msg = "The SIR model has completed. Ask the user if they'd like to analyze the results."
        response = self.llm.generate(msg)
        self.memory.save("sim_complete_msg", response)
        return response

    