# agents/control_agent.py

from agents.base_agent import OllamaLLM
from memory.json_memory import JSONMemory

class ControlAgent:
    def __init__(self, memory, model="mistral"):
        self.llm = OllamaLLM(model)
        self.memory = memory

    def get_user_input(self):
        prompt = "Ask the user for parameters to run the SIR model."
        response = self.llm.generate(prompt)
        self.memory.save("sir_user_input_prompt", response)
        return response

    def notify_sim_complete(self):
        msg = "The SIR model has completed. Ask the user if they'd like to analyze the results."
        response = self.llm.generate(msg)
        self.memory.save("sim_complete_msg", response)
        return response

    def ask_analysis_question(self, user_question):
        previous_qs = self.memory.get("analysis_questions", [])
        previous_qs.append(user_question)
        self.memory.save("analysis_questions", previous_qs)

        prompt = f"The user asked: '{user_question}'. Let's analyze the simulation data to answer."
        response = self.llm.generate(prompt)
        self.memory.save(f"response_to_{user_question}", response)
        return response
    