"""Factory helpers for resolving provider implementations from config."""

from typing import Any, Dict

from .kg.base import KGProvider
from .kg.noop import NoopKGProvider
from .llm.base import LLMProvider
from .llm.ollama import OllamaProvider
from .vector.argo_milvus import ArgoMilvusProvider
from .vector.base import VectorProvider


def create_llm_provider(config: Dict[str, Any]) -> LLMProvider:
    provider_type = (config or {}).get("type", "ollama")
    if provider_type == "ollama":
        return OllamaProvider(
            model=config.get("model", "mistral"),
            base_url=config.get("base_url", "http://localhost:11434/api/generate"),
            timeout=config.get("timeout", 120),
        )
    raise ValueError(f"Unsupported LLM provider type: {provider_type}")


def create_vector_provider(config: Dict[str, Any]) -> VectorProvider:
    provider_type = (config or {}).get("type", "argo_milvus")
    if provider_type == "argo_milvus":
        return ArgoMilvusProvider(
            embed_url=config.get(
                "embed_url", "https://apps.inside.anl.gov/argoapi/api/v1/resource/embed/"
            ),
            chat_url=config.get(
                "chat_url", "https://apps-dev.inside.anl.gov/argoapi/api/v1/resource/chat/"
            ),
            search_url=config.get("search_url", "http://titanv.gss.anl.gov:19530/v1/vector/search"),
            timeout=config.get("timeout", 120),
        )
    raise ValueError(f"Unsupported vector provider type: {provider_type}")


def create_kg_provider(config: Dict[str, Any]) -> KGProvider:
    provider_type = (config or {}).get("type", "noop")
    if provider_type == "noop":
        return NoopKGProvider()
    raise ValueError(f"Unsupported KG provider type: {provider_type}")

