"""Vector indexing payload builder for critical materials corpora."""

from typing import Any, Dict, List


def load_to_vector(config: Dict[str, Any]) -> Dict[str, Any]:
    """Build embedding-ready vector payloads from document chunks."""
    config = config or {}
    documents: List[Dict[str, Any]] = config.get("documents", [])
    material = config.get("material", "unspecified")

    payload = []
    for document in documents:
        text = str(document.get("text_content", "")).strip()
        if not text:
            continue
        payload.append(
            {
                "id": document.get("doc_id"),
                "text_content": text,
                "metadata": {
                    "source_path": document.get("source_path"),
                    "material": material,
                },
            }
        )

    return {"status": "ok", "records": payload, "record_count": len(payload)}
