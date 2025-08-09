
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)

from agents.reporter_agent import ReporterAgent

# Initialize the reporter agent with the FastAPI URL
agent = ReporterAgent(api_url="http://localhost:8000/predict")

# Test with different user inputs
print(agent.handle_request("What is the average infection rate?"))
print(agent.handle_request("When did the peak infection occur?"))
print(agent.handle_request("How many agents are infected?"))
