"""Unstructured ingestion helpers for reports and policy documents."""

import os
from typing import Any, Dict, List


def _split_text(text: str, chunk_size: int) -> List[str]:
    words = text.split()
    if not words:
        return []
    chunks = []
    for idx in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[idx : idx + chunk_size]))
    return chunks


def ingest_unstructured_sources(config: Dict[str, Any]) -> Dict[str, Any]:
    """Load plain-text sources and return chunked documents."""
    config = config or {}
    source_paths = config.get("source_paths", [])
    chunk_size = int(config.get("chunk_size", 180))

    documents = []
    missing_paths = []

    for path in source_paths:
        if not os.path.exists(path):
            missing_paths.append(path)
            continue
        with open(path, "r") as file:
            text = file.read().strip()
        for idx, chunk in enumerate(_split_text(text, chunk_size)):
            documents.append(
                {
                    "doc_id": f"{os.path.basename(path)}:{idx}",
                    "source_path": path,
                    "text_content": chunk,
                }
            )

    return {
        "status": "ok",
        "documents": documents,
        "document_count": len(documents),
        "missing_paths": missing_paths,
    }
