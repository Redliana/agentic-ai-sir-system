"""Structured ingestion utilities for critical materials datasets."""

import csv
import json
import os
from typing import Any, Dict, List


def _load_csv(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", newline="") as file:
        return list(csv.DictReader(file))


def _load_json(path: str) -> List[Dict[str, Any]]:
    with open(path, "r") as file:
        payload = json.load(file)
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        return [payload]
    return []


def _load_jsonl(path: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with open(path, "r") as file:
        for line in file:
            text = line.strip()
            if not text:
                continue
            item = json.loads(text)
            if isinstance(item, dict):
                rows.append(item)
    return rows


def ingest_structured_sources(config: Dict[str, Any]) -> Dict[str, Any]:
    """Load tabular structured inputs from CSV/JSON files."""
    config = config or {}
    source_paths = config.get("source_paths", [])
    required_fields = set(config.get("required_fields", []))

    ingested: List[Dict[str, Any]] = []
    missing_paths: List[str] = []
    unsupported_paths: List[str] = []

    for path in source_paths:
        if not os.path.exists(path):
            missing_paths.append(path)
            continue

        ext = os.path.splitext(path)[1].lower()
        if ext == ".csv":
            records = _load_csv(path)
        elif ext == ".json":
            records = _load_json(path)
        elif ext == ".jsonl":
            records = _load_jsonl(path)
        else:
            unsupported_paths.append(path)
            continue

        for record in records:
            if required_fields and not required_fields.issubset(record.keys()):
                continue
            ingested.append(record)

    return {
        "status": "ok",
        "records": ingested,
        "record_count": len(ingested),
        "missing_paths": missing_paths,
        "unsupported_paths": unsupported_paths,
    }
