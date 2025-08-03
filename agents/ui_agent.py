# agents.ui_agent.py

from utils.llm_utils import OllamaLLM

class UIAgent:
    def __init__(self, model="mistral", test_mode=False):
        self.llm = OllamaLLM(model)
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

        return response
