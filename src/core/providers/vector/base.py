"""Abstract retrieval provider used by RAG workflows."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class VectorProvider(ABC):
    @abstractmethod
    def embed(self, model: str, prompts: List[str]) -> Any:
        raise NotImplementedError

    @abstractmethod
    def search(
        self,
        collection: str,
        vector: List[float],
        output_fields: List[str],
        limit: int,
    ) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def chat(
        self,
        instructions: str,
        model: str,
        prompt: str,
    ) -> str:
        raise NotImplementedError

