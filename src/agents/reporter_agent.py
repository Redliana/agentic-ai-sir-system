# agents.reporter_agent.py

from utils.llm_utils import OllamaLLM
import logging
import requests

class ReporterAgent:
    def __init__(self, api_url, model="mistral", ):
        self.llm = OllamaLLM(model)
        self.api_url = api_url
        logging.basicConfig(level=logging.DEBUG)

    def report(self, user_question: str, analysis_results: dict) -> str:
        """Use an LLM to summarize the analysis results in a human-readable format."""
        prompt = f"""
        You are a expert in infectious disease modeling and are being asked to generate a report, outlining the results of an SIR model.

        The user asked: "{user_question}"

        Here are the analysis results (in dictionary format):
        {analysis_results}

        Please explain the results clearly and concisely in plain language for a general audience.
        Avoid repeating the dictionary format. Focus on summarizing key insights.
        If any values are missing, simply note that you couldn't determine the results.
        """
        return self.llm.generate(prompt)
    
    def get_action_from_input(self, user_input: str):
        try:
            response = requests.post(self.api_url, json={"text": user_input})
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx/5xx)
            response_json = response.json()  # Parse the JSON response

            # Print the raw response to see what we're getting
            print(f"Response from FastAPI: {response_json}")

            return response_json.get('response', 'No valid response returned')

        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")
            return None
        except ValueError as e:
            logging.error(f"Error decoding JSON response: {e}")
            return None

    def handle_request(self, user_input: str):
        action = self.get_action_from_input(user_input)

        # Print the action to see what's being returned
        print(f"Action received: {action}")

        if action == "calculate_average_infection_rate":
            return self.calculate_average_infection_rate()
        elif action == "get_peak_infection_time":
            return self.get_peak_infection_time()
        else:
            return "Sorry, I didn't understand that request."

    def calculate_average_infection_rate(self):
        return "The average infection rate is 0.15."

    def get_peak_infection_time(self):
        return "The peak infection occurred at step 50."
