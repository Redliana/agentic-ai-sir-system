"""Structured ingestion utilities for critical materials datasets."""

import csv
import json
import os
from typing import Any, Dict, List


SUPPORTED_STRUCTURED_EXTENSIONS = {".csv", ".json", ".jsonl", ".xlsx"}


class MissingDependencyError(RuntimeError):
    """Raised when an optional parser dependency is not installed."""


def _safe_column_name(value: Any, idx: int) -> str:
    text = str(value).strip() if value is not None else ""
    return text if text else f"column_{idx}"


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


def _load_xlsx(path: str, sheet_name: str = None) -> List[Dict[str, Any]]:
    try:
        from openpyxl import load_workbook
    except ImportError as exc:
        raise MissingDependencyError(
            "openpyxl is required for .xlsx ingestion. Install with: python3 -m pip install openpyxl"
        ) from exc

    workbook = load_workbook(path, read_only=True, data_only=True)
    sheet_names = [sheet_name] if sheet_name else list(workbook.sheetnames)
    rows: List[Dict[str, Any]] = []

    for sheet in sheet_names:
        worksheet = workbook[sheet]
        iter_rows = worksheet.iter_rows(values_only=True)
        headers_row = next(iter_rows, None)
        if headers_row is None:
            continue
        headers = [_safe_column_name(value, idx) for idx, value in enumerate(headers_row, start=1)]
        for row in iter_rows:
            if row is None or not any(cell is not None and str(cell).strip() for cell in row):
                continue
            record = {headers[idx]: row[idx] if idx < len(row) else None for idx in range(len(headers))}
            record["__sheet_name"] = sheet
            rows.append(record)

    return rows


def _has_required_fields(record: Dict[str, Any], required_fields: set) -> bool:
    if not required_fields:
        return True
    for field in required_fields:
        value = record.get(field)
        if value is None:
            return False
        if isinstance(value, str) and not value.strip():
            return False
    return True


def _normalize_record(
    record: Dict[str, Any],
    field_aliases: Dict[str, str],
    default_values: Dict[str, Any],
) -> Dict[str, Any]:
    normalized = dict(record)
    for alias, canonical in field_aliases.items():
        if alias in normalized and canonical not in normalized:
            normalized[canonical] = normalized[alias]
    for key, value in default_values.items():
        if key not in normalized or normalized[key] in ("", None):
            normalized[key] = value
    return normalized


def ingest_structured_sources(config: Dict[str, Any]) -> Dict[str, Any]:
    """Load tabular structured inputs from CSV, JSON, JSONL, and XLSX files."""
    config = config or {}
    source_paths = config.get("source_paths", [])
    required_fields = set(config.get("required_fields", []))
    field_aliases = dict(config.get("field_aliases", {}))
    default_values = dict(config.get("default_values", {}))
    include_source_metadata = bool(config.get("include_source_metadata", True))
    xlsx_sheet_name = config.get("xlsx_sheet_name")

    ingested: List[Dict[str, Any]] = []
    missing_paths: List[str] = []
    unsupported_paths: List[str] = []
    failed_paths: List[Dict[str, str]] = []
    missing_dependencies: List[str] = []
    skipped_required_count = 0

    for path in source_paths:
        if not os.path.exists(path):
            missing_paths.append(path)
            continue

        ext = os.path.splitext(path)[1].lower()
        if ext not in SUPPORTED_STRUCTURED_EXTENSIONS:
            unsupported_paths.append(path)
            continue

        try:
            if ext == ".csv":
                records = _load_csv(path)
            elif ext == ".json":
                records = _load_json(path)
            elif ext == ".jsonl":
                records = _load_jsonl(path)
            else:
                records = _load_xlsx(path, sheet_name=xlsx_sheet_name)
        except MissingDependencyError as exc:
            message = str(exc)
            if message not in missing_dependencies:
                missing_dependencies.append(message)
            failed_paths.append({"path": path, "error": message})
            continue
        except Exception as exc:  # pragma: no cover - protection for malformed files
            failed_paths.append({"path": path, "error": str(exc)})
            continue

        for record in records:
            normalized = _normalize_record(record, field_aliases, default_values)
            if include_source_metadata:
                normalized["__source_path"] = path
                normalized["__source_type"] = ext
            if not _has_required_fields(normalized, required_fields):
                skipped_required_count += 1
                continue
            ingested.append(normalized)

    status = "ok" if not missing_paths and not unsupported_paths and not failed_paths else "partial"
    return {
        "status": status,
        "records": ingested,
        "record_count": len(ingested),
        "missing_paths": missing_paths,
        "unsupported_paths": unsupported_paths,
        "failed_paths": failed_paths,
        "missing_dependencies": missing_dependencies,
        "skipped_required_count": skipped_required_count,
    }
