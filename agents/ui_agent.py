# agents.ui_agent.py

from utils.llm_utils import OllamaLLM

class UIAgent:
    def __init__(self, model="mistral", test_mode=False):
        self.llm = OllamaLLM(model)
        self.test_mode = test_mode
    
    def get_user_input(self):
        user_input = input("\n [UI Agent]: What would you like to do?\n> ")
        return user_input

    def classify_intent(self, user_input: str) -> str:
        """
        Classifies the intent of the user prompt.
        
        States:
            Run: run the simulation
            Analyze: analyze the results of the simulation

        """
        prompt = f"""
        You are a helpful assistant. A user has entered the following message:

        "{user_input}"

        Determine whether the user is trying to:
        - 'run' a simulation
        - 'analyze' the results
        - or something else (return 'unknown')

        Respond with only one word: 'run', 'analyze', 'exit', or 'unknown'.
        """
        intent = self.llm.generate(prompt).strip().lower()
        if intent in ["run", "analyze"]:
            return intent
        elif "run" in user_input.lower():
            return "run"
        elif "analyze" in user_input.lower():
            return "analyze"
        elif "exit" in user_input.lower():
            return "exit"
        return "unknown"

    def ask_analysis_question(self) -> str:
        """Prompt the user for a specific analysis question."""
        return input("\n [UI Agent]: What would you like to analyze?\n> ")

    def follow_up(self, message: str) -> str:
        prompt = f"""
        The following message should be displayed to the user:

        "{message}"

        Write a user-friendly version of this to display back to them.
        """
        return self.llm.generate(prompt)
    
