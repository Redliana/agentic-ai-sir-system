"""Heterogeneous ingestion workflow for critical materials datasets."""

import json
import os
from typing import Any, Dict, List, Tuple

from .structured_ingest import SUPPORTED_STRUCTURED_EXTENSIONS, ingest_structured_sources
from .to_kg import load_to_kg
from .to_vector import load_to_vector
from .unstructured_ingest import SUPPORTED_UNSTRUCTURED_EXTENSIONS, ingest_unstructured_sources


def _partition_paths(
    paths: List[str],
    structured_paths_override: List[str],
    unstructured_paths_override: List[str],
) -> Tuple[List[str], List[str], List[str]]:
    if structured_paths_override or unstructured_paths_override:
        structured_paths = list(structured_paths_override or [])
        unstructured_paths = list(unstructured_paths_override or [])
        used = set(structured_paths) | set(unstructured_paths)
        unknown = [path for path in paths if path not in used]
        return structured_paths, unstructured_paths, unknown

    structured_paths = []
    unstructured_paths = []
    unknown = []

    for path in paths:
        ext = os.path.splitext(path)[1].lower()
        if ext in SUPPORTED_STRUCTURED_EXTENSIONS:
            structured_paths.append(path)
        elif ext in SUPPORTED_UNSTRUCTURED_EXTENSIONS:
            unstructured_paths.append(path)
        else:
            unknown.append(path)

    return structured_paths, unstructured_paths, unknown


def ingest_heterogeneous_sources(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ingest mixed source files and build downstream KG/vector payloads.

    Expected config keys:
    - source_paths: list[str]
    - structured_paths: optional explicit structured files
    - unstructured_paths: optional explicit unstructured files
    - structured: config passed to ingest_structured_sources
    - unstructured: config passed to ingest_unstructured_sources
    - kg: config passed to load_to_kg
    - vector: config passed to load_to_vector
    - material: material label for vector metadata fallback
    """
    config = config or {}
    source_paths = list(config.get("source_paths", []))
    structured_paths_override = list(config.get("structured_paths", []))
    unstructured_paths_override = list(config.get("unstructured_paths", []))

    structured_paths, unstructured_paths, unknown_paths = _partition_paths(
        source_paths,
        structured_paths_override,
        unstructured_paths_override,
    )

    structured_cfg = dict(config.get("structured", {}))
    structured_cfg["source_paths"] = structured_paths
    structured_result = ingest_structured_sources(structured_cfg)

    unstructured_cfg = dict(config.get("unstructured", {}))
    unstructured_cfg["source_paths"] = unstructured_paths
    unstructured_result = ingest_unstructured_sources(unstructured_cfg)

    kg_cfg = dict(config.get("kg", {}))
    kg_cfg["records"] = structured_result.get("records", [])
    kg_result = load_to_kg(kg_cfg)

    vector_cfg = dict(config.get("vector", {}))
    vector_cfg["documents"] = unstructured_result.get("documents", [])
    if "material" not in vector_cfg:
        vector_cfg["material"] = config.get("material", "unspecified")
    vector_result = load_to_vector(vector_cfg)

    status = "ok"
    for result in (structured_result, unstructured_result):
        if result.get("status") != "ok":
            status = "partial"
            break
    if unknown_paths:
        status = "partial"

    return {
        "status": status,
        "summary": {
            "source_count": len(source_paths),
            "structured_paths": structured_paths,
            "unstructured_paths": unstructured_paths,
            "unknown_paths": unknown_paths,
            "structured_record_count": structured_result.get("record_count", 0),
            "document_count": unstructured_result.get("document_count", 0),
            "kg_fact_count": kg_result.get("fact_count", 0),
            "vector_record_count": vector_result.get("record_count", 0),
        },
        "structured": structured_result,
        "unstructured": unstructured_result,
        "kg": kg_result,
        "vector": vector_result,
    }


def run_ingestion_workflow(config: Dict[str, Any], output_path: str = "") -> Dict[str, Any]:
    """Run ingestion and optionally write the result manifest to JSON."""
    result = ingest_heterogeneous_sources(config)
    if output_path:
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        with open(output_path, "w") as file:
            json.dump(result, file, indent=2)
    return result
