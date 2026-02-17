"""Ollama provider adapter."""

import requests

from .base import LLMProvider


class OllamaProvider(LLMProvider):
    def __init__(self, model: str, base_url: str, timeout: int = 120):
        self.model = model
        self.base_url = base_url
        self.timeout = timeout

    def generate(self, prompt: str, system: str = "") -> str:
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        if system:
            payload["system"] = system

        response = requests.post(self.base_url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        return response.json().get("response", "").strip()

