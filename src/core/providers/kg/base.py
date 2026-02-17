"""Abstract interface for knowledge graph providers."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class KGProvider(ABC):
    @abstractmethod
    def upsert(self, entities: List[Dict[str, Any]], relations: List[Dict[str, Any]]) -> None:
        raise NotImplementedError

    @abstractmethod
    def query(self, query: str) -> List[Dict[str, Any]]:
        raise NotImplementedError

