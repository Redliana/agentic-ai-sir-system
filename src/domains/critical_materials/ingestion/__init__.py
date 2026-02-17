"""Ingestion utilities for critical materials domain sources."""

from .pipeline import ingest_heterogeneous_sources, run_ingestion_workflow
from .preprocess import deduplicate_paths, run_preprocess_workflow
from .publish import publish_ingestion_outputs
from .structured_ingest import ingest_structured_sources
from .to_kg import load_to_kg
from .to_vector import load_to_vector
from .unstructured_ingest import ingest_unstructured_sources

__all__ = [
    "deduplicate_paths",
    "ingest_heterogeneous_sources",
    "ingest_structured_sources",
    "ingest_unstructured_sources",
    "load_to_kg",
    "load_to_vector",
    "publish_ingestion_outputs",
    "run_ingestion_workflow",
    "run_preprocess_workflow",
]
