"""Argo embeddings/chat + Milvus search provider adapter."""

import json
import os
from typing import Any, Dict, List

import requests

from .base import VectorProvider


class ArgoMilvusProvider(VectorProvider):
    def __init__(
        self,
        embed_url: str,
        chat_url: str,
        search_url: str,
        timeout: int = 120,
        auth_token: str | None = None,
    ):
        self.embed_url = embed_url
        self.chat_url = chat_url
        self.search_url = search_url
        self.timeout = timeout
        self.auth_token = auth_token or os.getenv("MILVUS_AUTH_TOKEN")

    def _default_user(self) -> str:
        return (os.getenv("USERNAME") or os.getenv("USER") or "unknown").strip()

    def embed(self, model: str, prompts: List[str]) -> Any:
        payload = json.dumps({"user": self._default_user(), "model": model, "prompt": prompts})
        headers = {"Content-Type": "application/json"}
        response = requests.post(self.embed_url, data=payload, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def search(
        self,
        collection: str,
        vector: List[float],
        output_fields: List[str],
        limit: int,
    ) -> Dict[str, Any]:
        if not self.auth_token:
            raise ValueError(
                "Milvus auth token is not configured. Set MILVUS_AUTH_TOKEN environment variable."
            )

        auth_token = (
            self.auth_token
            if self.auth_token.lower().startswith("bearer ")
            else f"Bearer {self.auth_token}"
        )

        payload = json.dumps(
            {
                "collectionName": collection,
                "vector": vector,
                "annsField": "text_vector",
                "outputFields": output_fields,
                "limit": limit,
            }
        )
        headers = {
            "Authorization-Token": auth_token,
            "Content-Type": "application/json",
        }
        response = requests.post(self.search_url, data=payload, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def chat(self, instructions: str, model: str, prompt: str) -> str:
        payload = json.dumps(
            {
                "user": self._default_user(),
                "model": model,
                "system": instructions,
                "prompt": [prompt],
                "stop": [],
                "temperature": 0.1,
                "top_p": 0.9,
            }
        )
        headers = {"Content-Type": "application/json"}
        response = requests.post(self.chat_url, data=payload, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json().get("response", "")
