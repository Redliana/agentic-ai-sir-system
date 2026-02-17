"""Abstract interface for chat/completion-style language model providers."""

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, system: str = "") -> str:
        raise NotImplementedError

