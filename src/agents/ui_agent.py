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
from typing import Dict, List

import yaml
# Import dependencies
from core.providers.factory import create_llm_provider
from core.providers.llm.base import LLMProvider


class UIAgent:
    def __init__(
            self,
            model="mistral",
            test_mode=False,
            params_file="params.yaml",
            domain_config=None,
            llm_provider: LLMProvider = None,
        ):
        provider_cfg = dict((domain_config or {}).get("providers", {}).get("llm", {}))
        if not provider_cfg:
            provider_cfg = {"type": "ollama", "model": model}
        elif "model" not in provider_cfg:
            provider_cfg["model"] = model

        self.llm = llm_provider or create_llm_provider(provider_cfg)
        self.test_mode = test_mode
        self.params_file = params_file
        self.params = self.load_params()
        self.domain_config = domain_config or {}
        self.ui_config = self.domain_config.get("ui", {})
        self.allowed_intents = self.domain_config.get(
            "intents", ["run", "analyze", "learn", "exit", "unknown"]
        )
        self.keyword_rules = self.ui_config.get("keyword_rules", {})

    def get_user_input(self):
        greeting = self.ui_config.get(
            "greeting",
            "Hello I am a Virtual Interface Agent, how can I help you today?",
        )
        input_prompt = self.ui_config.get(
            "input_prompt",
            "You can request to run a series of simulations, analyze data, or learn about model assumptions and/or infectious disease spread",
        )
        print(f"\n[UI Agent]: {greeting}")
        user_input = input(f"[UI Agent]: {input_prompt}\n>").lower()
        return user_input

    def _keyword_classification(self, text: str) -> str:
        text_lower = text.lower()
        for intent, keywords in self.keyword_rules.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    return intent
        return "unknown"

    def _build_intent_prompt(self, text: str, include_followup: bool = False) -> str:
        intent_labels: Dict[str, str] = self.ui_config.get("intent_labels", {})
        options: List[str] = []
        for intent in self.allowed_intents:
            label = intent_labels.get(intent, intent)
            options.append(f"- '{intent}': {label}")
        options_text = "\n".join(options)
        context = "follow-up message" if include_followup else "message"

        prompt = f"""
        You are an assistant AI agent.
        Determine the user's intent from the following {context}:

        "{text}"

        Allowed intents:
        {options_text}

        Return exactly one intent label.
        """

        return prompt

    def classify_intent(self, user_input: str) -> str:
        """Classifies the intent of the user prompt."""
        keyword_intent = self._keyword_classification(user_input)
        if keyword_intent in self.allowed_intents and keyword_intent != "unknown":
            return keyword_intent

        if self.test_mode:
            return keyword_intent

        intent = self.llm.generate(self._build_intent_prompt(user_input)).strip().lower()
        if intent in self.allowed_intents:
            return intent
        return keyword_intent

    def ask_analysis_question(self) -> str:
        """Prompt the user for a specific analysis question."""
        analysis_prompt = self.ui_config.get(
            "analysis_prompt", "Sure, I can help with that. What would you like to know?"
        )
        return input(f"\n[UI Agent]: {analysis_prompt}\n> ")

    def follow_up(self):
        """Conditional edge function for directing user follow-up questions."""
        follow_up_prompt = self.ui_config.get(
            "follow_up_prompt", "Is there anything else I can help you with?"
        )
        user_follow_up = input(f"\n[UI Agent]: {follow_up_prompt}\n> ")
        return user_follow_up

    def classify_followup(self, follow_up: str) -> str:
        """Classify the user's follow-up response. Used after the system asks: 'Is there anything else I can help you with?'"""
        keyword_intent = self._keyword_classification(follow_up)
        if keyword_intent in self.allowed_intents and keyword_intent != "unknown":
            return keyword_intent

        if self.test_mode:
            return keyword_intent

        followup_intent = self.llm.generate(
            self._build_intent_prompt(follow_up, include_followup=True)
        ).strip().lower()
        if followup_intent in self.allowed_intents:
            return followup_intent
        return keyword_intent

    def get_fallback_message(self) -> str:
        return self.ui_config.get(
            "fallback_message",
            "Sorry, I didn't understand that. Try another request.",
        )

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
