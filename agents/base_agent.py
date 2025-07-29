# agents/base_agent.py

import requests

class OllamaLLM:
    def __init__(self, model="mistral", base_url="http://localhost:11434/api/generate"):
        self.model = model
        self.base_url = base_url

    def generate(self, prompt: str, system: str = "") -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        if system:
            payload["system"] = system

        response = requests.post(self.base_url, json=payload)
        return response.json()["response"].strip()
