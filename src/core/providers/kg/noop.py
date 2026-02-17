"""No-op KG provider used until a graph backend is configured."""

from typing import Any, Dict, List

from .base import KGProvider


class NoopKGProvider(KGProvider):
    def upsert(self, entities: List[Dict[str, Any]], relations: List[Dict[str, Any]]) -> None:
        return None

    def query(self, query: str) -> List[Dict[str, Any]]:
        return []

