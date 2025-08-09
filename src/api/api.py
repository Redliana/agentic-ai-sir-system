# src/api/api.py

"""
Utility file for LoRA model API.
"""

from fastapi import FastAPI
from transformers import GPTJForCausalLM, AutoTokenizer

import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)

from utils.llm_utils import OllamaLLM

app = FastAPI()

# Load the fine-tuned model
model = OllamaLLM(model="./models/fine_tuned_lora_model")

def predict(request: dict):
    user_input = request['text']
    try:
        # Update the URL to the correct endpoint
        ollama_url = "http://localhost:11434/api/generate"  # Adjust the endpoint as needed
        response = requests.post(ollama_url, json={"text": user_input})
        response.raise_for_status()

        # Check if the response contains 'response'
        if 'response' in response.json():
            return {"response": response.json()['response']}
        else:
            return {"error": "Response key not found in model output."}
        
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {e}"}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}