"""Corpus preprocessing for large heterogeneous critical-materials datasets."""

import hashlib
import json
import os
from typing import Any, Dict, List, Optional, Tuple

import yaml

from .structured_ingest import ingest_structured_sources


STRUCTURED_EXTENSIONS = {".csv", ".json", ".jsonl", ".xlsx"}
UNSTRUCTURED_EXTENSIONS = {".txt", ".md", ".pdf"}
TARGET_EXTENSIONS = STRUCTURED_EXTENSIONS | UNSTRUCTURED_EXTENSIONS

DEFAULT_COUNTRY_MAP = {
    "u.s.": "United States",
    "u.s.a.": "United States",
    "usa": "United States",
    "us": "United States",
    "uk": "United Kingdom",
    "uae": "United Arab Emirates",
    "drc": "Democratic Republic of the Congo",
    "congo, democratic republic of the": "Democratic Republic of the Congo",
    "russia": "Russian Federation",
}
DEFAULT_MATERIAL_MAP = {
    "rare earth elements": "REE",
    "rare earth element": "REE",
    "ree": "REE",
    "lithium carbonate": "lithium",
    "nickel matte": "nickel",
    "copper concentrate": "copper",
}
DEFAULT_UNIT_MAP = {
    "t": "tonnes",
    "ton": "tonnes",
    "tons": "tonnes",
    "tonnes": "tonnes",
    "metric ton": "tonnes",
    "metric tons": "tonnes",
    "mt": "tonnes",
    "kt": "kilotonnes",
    "kg": "kilograms",
    "lb": "pounds",
    "lbs": "pounds",
}
DEFAULT_UNIT_TO_TONNES = {
    "tonnes": 1.0,
    "kilotonnes": 1000.0,
    "kilograms": 0.001,
    "pounds": 0.00045359237,
}


def _safe_relpath(path: str, root: str) -> str:
    try:
        return os.path.relpath(path, root)
    except Exception:
        return path


def _iter_target_paths(corpus_root: str, config: Dict[str, Any]) -> List[str]:
    include_extensions = {
        ext.lower() if ext.startswith(".") else f".{ext.lower()}"
        for ext in config.get("extensions", sorted(TARGET_EXTENSIONS))
    }
    skip_dir_names = set(
        config.get(
            "skip_dir_names",
            [
                "__pycache__",
                ".git",
                ".venv",
                "venv",
                ".claude",
                ".playwright-mcp",
                ".ipynb_checkpoints",
            ],
        )
    )
    paths: List[str] = []

    for dirpath, dirnames, filenames in os.walk(corpus_root):
        dirnames[:] = [d for d in dirnames if d not in skip_dir_names and not d.startswith(".")]
        for name in filenames:
            ext = os.path.splitext(name)[1].lower()
            if ext in include_extensions:
                paths.append(os.path.join(dirpath, name))
    return sorted(paths)


def _hash_file(path: str, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _dedupe_key(path: str, method: str) -> Tuple[Any, ...]:
    stat = os.stat(path)
    size = stat.st_size
    if method == "sha256_size":
        return (_hash_file(path), size)
    return (os.path.basename(path).lower(), size)


def _path_score(path: str, prefer_tokens: List[str], avoid_tokens: List[str]) -> Tuple[int, int]:
    path_lower = path.lower()
    score = 0
    for token in prefer_tokens:
        if token.lower() in path_lower:
            score += 2
    for token in avoid_tokens:
        if token.lower() in path_lower:
            score -= 2
    # Tie-breaker: shorter paths usually cleaner/canonical.
    return score, -len(path)


def deduplicate_paths(paths: List[str], config: Dict[str, Any]) -> Dict[str, Any]:
    dedup_cfg = dict(config.get("deduplication", {}))
    if not dedup_cfg.get("enabled", True):
        return {"selected_paths": list(paths), "groups": []}

    method = dedup_cfg.get("method", "name_size")
    prefer_tokens = list(dedup_cfg.get("prefer_path_contains", []))
    avoid_tokens = list(dedup_cfg.get("avoid_path_contains", []))

    groups: Dict[Tuple[Any, ...], List[str]] = {}
    for path in paths:
        key = _dedupe_key(path, method=method)
        groups.setdefault(key, []).append(path)

    selected_paths: List[str] = []
    duplicate_groups: List[Dict[str, Any]] = []
    for grouped_paths in groups.values():
        if len(grouped_paths) == 1:
            selected_paths.append(grouped_paths[0])
            continue

        ranked = sorted(
            grouped_paths,
            key=lambda path: _path_score(path, prefer_tokens=prefer_tokens, avoid_tokens=avoid_tokens),
            reverse=True,
        )
        selected = ranked[0]
        selected_paths.append(selected)
        duplicate_groups.append(
            {
                "selected": selected,
                "dropped": ranked[1:],
                "count": len(ranked),
            }
        )

    return {"selected_paths": sorted(selected_paths), "groups": duplicate_groups}


def _parse_number(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        return None
    text = text.replace(",", "")
    try:
        return float(text)
    except ValueError:
        return None


def _normalize_text_value(value: Any, mapping: Dict[str, str]) -> Any:
    if value is None:
        return value
    text = str(value).strip()
    if not text:
        return value
    return mapping.get(text.lower(), value)


def _match_source_rule(path: str, source_rules: List[Dict[str, Any]]) -> Dict[str, Any]:
    path_lower = path.lower()
    for rule in source_rules:
        tokens = [str(token).lower() for token in rule.get("path_contains", [])]
        if tokens and all(token in path_lower for token in tokens):
            return rule
    return {}


def _normalize_structured_record(record: Dict[str, Any], normalize_cfg: Dict[str, Any]) -> Dict[str, Any]:
    country_map = dict(DEFAULT_COUNTRY_MAP)
    country_map.update({k.lower(): v for k, v in dict(normalize_cfg.get("country_map", {})).items()})
    material_map = dict(DEFAULT_MATERIAL_MAP)
    material_map.update({k.lower(): v for k, v in dict(normalize_cfg.get("material_map", {})).items()})
    unit_map = dict(DEFAULT_UNIT_MAP)
    unit_map.update({k.lower(): v for k, v in dict(normalize_cfg.get("unit_map", {})).items()})

    unit_to_tonnes = dict(DEFAULT_UNIT_TO_TONNES)
    unit_to_tonnes.update(
        {
            str(key).lower(): float(value)
            for key, value in dict(normalize_cfg.get("unit_to_tonnes", {})).items()
        }
    )

    record["country"] = _normalize_text_value(record.get("country"), country_map)
    record["material"] = _normalize_text_value(record.get("material"), material_map)
    record["unit"] = _normalize_text_value(record.get("unit"), unit_map)

    quantity_fields = list(
        normalize_cfg.get(
            "quantity_fields",
            ["quantity", "value", "production", "imports", "consumption", "demand"],
        )
    )
    unit_field = str(normalize_cfg.get("unit_field", "unit"))
    unit_value = str(record.get(unit_field, "")).strip().lower()
    factor = unit_to_tonnes.get(unit_value)

    for field in quantity_fields:
        if field not in record:
            continue
        numeric = _parse_number(record.get(field))
        if numeric is None:
            continue
        record[field] = numeric
        if factor is not None:
            record[f"{field}_tonnes"] = numeric * factor

    return record


def _pdf_first_page_text_len(path: str) -> int:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError(
            "pypdf is required for PDF preprocessing. Install with: python3 -m pip install pypdf"
        ) from exc

    reader = PdfReader(path)
    if not reader.pages:
        return 0
    text = (reader.pages[0].extract_text() or "").strip()
    return len(text)


def _build_ingestion_ready_config(
    *,
    normalized_structured_path: str,
    unstructured_paths: List[str],
    config: Dict[str, Any],
) -> Dict[str, Any]:
    ingestion_cfg = dict(config.get("ingestion", {}))
    include_unstructured = bool(ingestion_cfg.get("include_unstructured", True))
    structured_overrides = dict(ingestion_cfg.get("structured", {}))

    required_fields = list(structured_overrides.pop("required_fields", ["material", "country"]))
    include_source_metadata = bool(structured_overrides.pop("include_source_metadata", True))
    keep_fields = structured_overrides.pop("keep_fields", ["material", "country", "stage"])
    source_paths = [normalized_structured_path]
    if include_unstructured:
        source_paths.extend(sorted(unstructured_paths))

    structured_cfg = {
        "required_fields": required_fields,
        "include_source_metadata": include_source_metadata,
    }
    if keep_fields is not None:
        structured_cfg["keep_fields"] = list(keep_fields)
    structured_cfg.update(structured_overrides)

    ingestion_cfg = {
        "source_paths": source_paths,
        "structured_paths": [normalized_structured_path],
        "unstructured_paths": sorted(unstructured_paths) if include_unstructured else [],
        "include_unstructured": include_unstructured,
        "material": config.get("material", "unspecified"),
        "structured": structured_cfg,
        "unstructured": dict(config.get("unstructured", {"chunk_size": 180, "chunk_overlap": 30})),
        "kg": dict(config.get("kg", {})),
        "vector": dict(config.get("vector", {})),
    }
    if "material" not in ingestion_cfg["vector"]:
        ingestion_cfg["vector"]["material"] = ingestion_cfg["material"]
    return ingestion_cfg


def run_preprocess_workflow(config: Dict[str, Any]) -> Dict[str, Any]:
    """Preprocess corpus files and emit ingestion-ready artifacts."""
    config = config or {}
    corpus_root = os.path.abspath(config["corpus_root"])
    output_dir = os.path.abspath(config.get("output_dir", "tmp/corpus_preprocess"))
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "staged"), exist_ok=True)

    discovered_paths = _iter_target_paths(corpus_root=corpus_root, config=config)
    dedupe_result = deduplicate_paths(discovered_paths, config=config)
    selected_paths = dedupe_result["selected_paths"]

    structured_paths = [path for path in selected_paths if os.path.splitext(path)[1].lower() in STRUCTURED_EXTENSIONS]
    unstructured_paths = [
        path for path in selected_paths if os.path.splitext(path)[1].lower() in UNSTRUCTURED_EXTENSIONS
    ]

    preprocess_cfg = dict(config.get("preprocess", {}))
    source_rules = list(preprocess_cfg.get("source_rules", []))
    global_aliases = dict(preprocess_cfg.get("global_field_aliases", {}))
    global_defaults = dict(preprocess_cfg.get("global_default_values", {}))
    normalize_cfg = dict(config.get("normalization", {}))

    grouped_structured_paths: Dict[str, Dict[str, Any]] = {}
    for path in structured_paths:
        rule = _match_source_rule(path, source_rules)
        rule_name = str(rule.get("name", "__default__"))
        grouped_structured_paths.setdefault(rule_name, {"rule": rule, "paths": []})
        grouped_structured_paths[rule_name]["paths"].append(path)

    normalized_structured_records: List[Dict[str, Any]] = []
    structured_failures: List[Dict[str, str]] = []
    for group in grouped_structured_paths.values():
        rule = group["rule"]
        rule_aliases = dict(rule.get("field_aliases", {}))
        rule_defaults = dict(rule.get("default_values", {}))

        group_cfg = {
            "source_paths": group["paths"],
            "required_fields": list(preprocess_cfg.get("required_fields", [])),
            "field_aliases": {**global_aliases, **rule_aliases},
            "default_values": {**global_defaults, **rule_defaults},
            "include_source_metadata": True,
            "xlsx_sheet_name": preprocess_cfg.get("xlsx_sheet_name"),
        }
        ingested = ingest_structured_sources(group_cfg)
        for failure in ingested.get("failed_paths", []):
            structured_failures.append(failure)
        for record in ingested.get("records", []):
            normalized_structured_records.append(_normalize_structured_record(record, normalize_cfg))

    ocr_cfg = dict(config.get("ocr", {}))
    scanned_threshold = int(ocr_cfg.get("scanned_text_threshold", 80))

    ocr_queue: List[Dict[str, Any]] = []
    text_ready_unstructured_paths: List[str] = []
    unstructured_failures: List[Dict[str, str]] = []

    for path in unstructured_paths:
        ext = os.path.splitext(path)[1].lower()
        if ext != ".pdf":
            text_ready_unstructured_paths.append(path)
            continue

        try:
            chars = _pdf_first_page_text_len(path)
            if chars < scanned_threshold:
                ocr_queue.append({"path": path, "first_page_text_chars": chars, "reason": "low_extractable_text"})
            else:
                text_ready_unstructured_paths.append(path)
        except Exception as exc:  # pragma: no cover - defensive parse guard for broken PDFs
            ocr_queue.append({"path": path, "first_page_text_chars": 0, "reason": str(exc)})
            unstructured_failures.append({"path": path, "error": str(exc)})

    outputs_cfg = dict(config.get("outputs", {}))
    normalized_structured_rel = outputs_cfg.get(
        "normalized_structured_path",
        "staged/normalized_structured.jsonl",
    )
    normalized_structured_path = os.path.join(output_dir, normalized_structured_rel)
    os.makedirs(os.path.dirname(normalized_structured_path), exist_ok=True)
    with open(normalized_structured_path, "w") as file:
        for record in normalized_structured_records:
            file.write(json.dumps(record, ensure_ascii=True) + "\n")

    ingestion_ready_cfg = _build_ingestion_ready_config(
        normalized_structured_path=normalized_structured_path,
        unstructured_paths=text_ready_unstructured_paths,
        config=config,
    )

    ingestion_config_rel = outputs_cfg.get("ingestion_config_path", "ingestion_ready.yaml")
    ingestion_config_path = os.path.join(output_dir, ingestion_config_rel)
    os.makedirs(os.path.dirname(ingestion_config_path), exist_ok=True)
    with open(ingestion_config_path, "w") as file:
        yaml.safe_dump(ingestion_ready_cfg, file, sort_keys=False)

    ocr_queue_rel = outputs_cfg.get("ocr_queue_path", "ocr_queue.txt")
    ocr_queue_path = os.path.join(output_dir, ocr_queue_rel)
    os.makedirs(os.path.dirname(ocr_queue_path), exist_ok=True)
    with open(ocr_queue_path, "w") as file:
        for item in ocr_queue:
            file.write(f"{item['path']}\n")

    duplicate_manifest_rel = outputs_cfg.get("duplicate_manifest_path", "duplicates.json")
    duplicate_manifest_path = os.path.join(output_dir, duplicate_manifest_rel)
    os.makedirs(os.path.dirname(duplicate_manifest_path), exist_ok=True)
    with open(duplicate_manifest_path, "w") as file:
        json.dump(dedupe_result["groups"], file, indent=2)

    report = {
        "status": "ok",
        "corpus_root": corpus_root,
        "summary": {
            "discovered_path_count": len(discovered_paths),
            "selected_path_count": len(selected_paths),
            "structured_path_count": len(structured_paths),
            "unstructured_path_count": len(unstructured_paths),
            "duplicate_group_count": len(dedupe_result["groups"]),
            "normalized_record_count": len(normalized_structured_records),
            "text_ready_unstructured_count": len(text_ready_unstructured_paths),
            "ocr_queue_count": len(ocr_queue),
        },
        "artifacts": {
            "normalized_structured_path": normalized_structured_path,
            "ingestion_config_path": ingestion_config_path,
            "ocr_queue_path": ocr_queue_path,
            "duplicate_manifest_path": duplicate_manifest_path,
        },
        "preprocess": {
            "ocr_queue": ocr_queue,
            "structured_failures": structured_failures,
            "unstructured_failures": unstructured_failures,
        },
    }

    report_rel = outputs_cfg.get("preprocess_report_path", "preprocess_report.json")
    report_path = os.path.join(output_dir, report_rel)
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w") as file:
        json.dump(report, file, indent=2)
    report["artifacts"]["preprocess_report_path"] = report_path

    # Include a concise preview of drop decisions for quick review.
    report["preprocess"]["duplicate_groups_preview"] = [
        {
            "selected": _safe_relpath(group["selected"], corpus_root),
            "dropped_count": len(group["dropped"]),
        }
        for group in dedupe_result["groups"][:25]
    ]

    return report
