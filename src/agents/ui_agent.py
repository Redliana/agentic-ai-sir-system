# src/agents/ui_agent.py

"""
UI Agent is responsible for:
1. Prompting user input.
2. Classifying user intent.
3. Prompting analysis question.
4. Prompting user follow-up.
5. Classifying user follow-up.
6. Loading model params from the YAML file.
7. Saving model params.
8. Prompting user for model params.
9. Validating user model params.
"""

# Import libraries
import yaml
# Import dependencies
from utils.llm_utils import OllamaLLM


class UIAgent:
    def __init__(
            self, 
            model="mistral", 
            test_mode=False, 
            params_file="params.yaml"
        ):
        self.llm = OllamaLLM(model)
        self.test_mode = test_mode
        self.params_file = params_file
        self.params = self.load_params()
    
    def get_user_input(self):
        print("\n[UI Agent]: Hello I am a Virtual Interface Agent, how can I help you today?")
        user_input = input("[UI Agent]: You can request to run a series of simulations, analyze data, or learn about model assumptions and/or infectious disease spread\n>").lower()
        return user_input

    def classify_intent(self, user_input: str) -> str:
        """Classifies the intent of the user prompt."""
        prompt = f"""
        You are a assistant AI Agent, tasked with the goal of answer user questions in an empathetic and professional manner.
        You must determine the users needs based on their input message. 
        A user has entered the following message:

        "{user_input}"

        Determine whether the user is trying to:
        - 'run' a simulation
        - 'analyze' the results
        - 'learn' about model 'assumptions'
        - 'learn' about infectious disease spread
        - 'learn' about the history of infectious disease models
        - 'exit' the model
        - or something else

        If the user message is unclear, please prompt them to try another request.
        Your goal is to educate and expand understanding so please present your language in a way that aligns with this goal.

        Respond with only one word: 'run', 'analyze', 'exit', 'learn', or 'unknown'.
        """
        intent = self.llm.generate(prompt).strip().lower()
        if intent in ["run", "analyze", "learn", "model"]:
            return intent
        elif "run" in user_input.lower():
            return "run"
        elif "analyze" in user_input.lower():
            return "analyze"
        elif any(keyword in user_input.lower() for keyword in ["learn about model", "assumptions", "parameters", "how does", "how does the model", "explain the model"]):
            return "learn"
        elif "exit" in user_input.lower():
            return "exit"
        return "unknown"

    def ask_analysis_question(self) -> str:
        """Prompt the user for a specific analysis question."""
        return input("\n[UI Agent]: Sure, I can help with that. What would you like to know?\n> ")

    def follow_up(self):
        """Conditional edge function for directing user follow-up questions."""
        user_follow_up = input(f"\n[UI Agent]: Is there anything else I can help you with?\n> ")
        return user_follow_up
    
    def classify_followup(self, follow_up: str) -> str:
        """Classify the user's follow-up response. Used after the system asks: 'Is there anything else I can help you with?'"""
        prompt = f"""
        You are a assistant AI Agent, tasked with the goal of answer user questions in an empathetic and professional manner.
        You must determine the users needs based on their input message. 
        A user has entered the following message:

        "{follow_up}"

        Determine whether the user is trying to:
        - 'run' a simulation
        - 'analyze' the results
        - 'learn' about model 'assumptions'
        - 'exit' the model
        - or something else

        If the user message is unclear, please prompt them to try another request.
        Your goal is to educate and expand understanding so please present your language in a way that aligns with this goal.

        Respond with only one word: 'run', 'analyze', 'exit', 'learn', or 'unknown'.
        """
        
        followup_intent = self.llm.generate(prompt).strip().lower()
        if followup_intent in ["run", "analyze", "learn", "model"]:
            return followup_intent
        elif "run" in follow_up.lower():
            return "run"
        elif "analyze" in follow_up.lower():
            return "analyze"
        elif any(keyword in follow_up.lower() for keyword in ["learn about model", "assumptions", "parameters", "how does", "how does the model", "explain the model"]):
            return "learn"
        elif "exit" in follow_up.lower():
            return "exit"
        return "unknown"
    
    def load_params(self):
        """Load the parameters from YAML file if they exist."""
        try:
            with open(self.params_file, "r") as file:
                return yaml.safe_load(file) or {}
        except FileNotFoundError:
            return {}

    def save_params(self, new_params):
        """Save the parameters to the YAML file."""
        with open(self.params_file, "w") as file:
            yaml.dump(new_params, file, default_flow_style=False)

    def get_user_params(self, prompt, default_value, value_type):
        """Get user input and validate it."""
        model_params = input(f"{prompt}: ")
        if not model_params:
            return default_value
        try:
            return value_type(model_params)
        except ValueError:
            print(f"Invalid input, using default: {default_value}")
            return default_value

    def prompt_for_parameters(self, default_params):
        """Prompt the user for parameters, and return validated ones."""
        print("\n[UI Agent]: Sure, I can help you with that. Here are the default parameters:")
    
        for key, value in default_params.items():
            print(f"{key}: {value}")
        
        params_choice = input("\n[UI Agent]: Would you prefer to use the default parameters or enter your own?\n>").lower()

        if any(keyword in params_choice.lower() for keyword in ["default", "default parameters"]):
            print("\n[UI Agent]: Thanks, using the default parameters to run the simulation!")
            new_params = default_params
        else:
            # Prompt for each parameter
            print("[UI Agent]: Okay, please enter the following parameters:")
            num_runs = self.get_user_params("Number of runs", default_params["num_runs"], int)
            num_agents = self.get_user_params("Number of agents", default_params["num_agents"], int)
            num_steps = self.get_user_params("Number of steps", default_params["num_steps"], int)
            num_contacts = self.get_user_params("Number of contacts per step", default_params["num_contacts"], int)
            infection_prob = self.get_user_params("Infection probability", default_params["infection_prob"], float)
            infection_duration = self.get_user_params("Infection duration (in steps)", default_params["infection_duration"], int)
            recovery_prob = self.get_user_params("Recovery probability", default_params["recovery_prob"], float)

            # Create a dictionary of the parameters
            new_params = {
                "seed": 42,  # Fixed seed
                "num_runs": num_runs,
                "num_agents": num_agents,
                "num_steps": num_steps,
                "num_contacts": num_contacts,
                "infection_prob": infection_prob,
                "infection_duration": infection_duration,
                "recovery_prob": recovery_prob
            }

            # Save the new parameters to the file
            self.save_params(new_params)

        return new_params
