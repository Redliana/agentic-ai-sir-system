"""Publish ingestion outputs to backend-ready artifacts and optional live sinks."""

from __future__ import annotations

import csv
import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


@dataclass(frozen=True)
class PublishSummary:
    kg_fact_count: int
    vector_record_count: int
    material_node_count: int
    country_node_count: int
    published_neo4j: bool
    published_milvus: bool


def _load_manifest(manifest_path: str) -> Dict[str, Any]:
    with open(manifest_path, "r") as file:
        return json.load(file) or {}


def _iter_kg_facts(manifest: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    for fact in manifest.get("kg", {}).get("facts", []) or []:
        if isinstance(fact, dict):
            yield fact


def _iter_vector_records(manifest: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    for record in manifest.get("vector", {}).get("records", []) or []:
        if isinstance(record, dict):
            yield record


def _sanitize_rel_type(value: str) -> str:
    text = (value or "RELATED_TO").strip().upper().replace("-", "_").replace(" ", "_")
    return "".join(ch for ch in text if ch.isalnum() or ch == "_") or "RELATED_TO"


def _write_jsonl(path: str, rows: Sequence[Dict[str, Any]]) -> None:
    with open(path, "w") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=True) + "\n")


def _build_neo4j_tables(
    facts: Sequence[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    materials = {}
    countries = {}
    relations = []

    for fact in facts:
        subject_type = str(fact.get("subject_type", "")).strip().lower()
        object_type = str(fact.get("object_type", "")).strip().lower()
        subject_id = str(fact.get("subject_id", "")).strip()
        object_id = str(fact.get("object_id", "")).strip()
        if not subject_id or not object_id:
            continue

        if subject_type == "material":
            materials.setdefault(subject_id, {"material_id:ID(Material)": subject_id, "name": subject_id})
        if object_type == "country":
            countries.setdefault(object_id, {"country_id:ID(Country)": object_id, "name": object_id})

        props = dict(fact.get("properties", {}))
        rel_type = _sanitize_rel_type(str(fact.get("predicate", "RELATED_TO")))
        relations.append(
            {
                ":START_ID(Material)": subject_id,
                ":END_ID(Country)": object_id,
                ":TYPE": rel_type,
                "stage": str(props.get("stage", "")),
            }
        )

    return list(materials.values()), list(countries.values()), relations


def _write_csv(path: str, rows: Sequence[Dict[str, Any]], fieldnames: Sequence[str]) -> None:
    with open(path, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(fieldnames))
        writer.writeheader()
        writer.writerows(rows)


def _publish_neo4j(facts: Sequence[Dict[str, Any]], config: Dict[str, Any]) -> bool:
    uri = config.get("uri") or os.getenv("NEO4J_URI")
    user = config.get("user") or os.getenv("NEO4J_USER")
    password = config.get("password") or os.getenv("NEO4J_PASSWORD")
    database = config.get("database") or os.getenv("NEO4J_DATABASE", "neo4j")
    if not uri or not user or not password:
        return False

    try:
        from neo4j import GraphDatabase
    except ImportError:
        raise RuntimeError(
            "neo4j driver is required for live KG publish. Install with: python3 -m pip install neo4j"
        )

    batch_size = int(config.get("batch_size", 5000))
    driver = GraphDatabase.driver(uri, auth=(user, password))
    query = """
    UNWIND $rows AS row
    MERGE (m:Material {name: row.subject_id})
    MERGE (c:Country {name: row.object_id})
    MERGE (m)-[r:INVOLVES_COUNTRY]->(c)
    SET r.stage = row.stage
    """

    rows = []
    with driver.session(database=database) as session:
        for fact in facts:
            rows.append(
                {
                    "subject_id": str(fact.get("subject_id", "")),
                    "object_id": str(fact.get("object_id", "")),
                    "stage": str(dict(fact.get("properties", {})).get("stage", "")),
                }
            )
            if len(rows) >= batch_size:
                session.run(query, rows=rows)
                rows = []
        if rows:
            session.run(query, rows=rows)
    driver.close()
    return True


def _publish_milvus(records: Sequence[Dict[str, Any]], config: Dict[str, Any]) -> bool:
    if not records:
        return False

    uri = config.get("uri") or os.getenv("MILVUS_URI")
    token = config.get("token") or os.getenv("MILVUS_AUTH_TOKEN")
    collection = config.get("collection", "critical_materials_docs")
    embed_url = config.get("embed_url") or os.getenv("ARGO_EMBED_URL")
    embedding_model = config.get("embedding_model", "v3large")
    if not uri or not token or not embed_url:
        return False

    try:
        import requests
        from pymilvus import MilvusClient
    except ImportError:
        raise RuntimeError(
            "pymilvus and requests are required for live Milvus publish. Install with: python3 -m pip install pymilvus requests"
        )

    batch_size = int(config.get("batch_size", 128))

    client = MilvusClient(uri=uri, token=token)
    if not client.has_collection(collection_name=collection):
        client.create_collection(
            collection_name=collection,
            dimension=3072,
            metric_type="COSINE",
            consistency_level="Strong",
        )

    def embed_texts(texts: List[str]) -> List[List[float]]:
        payload = json.dumps({"user": os.getenv("USER", "unknown"), "model": embedding_model, "prompt": texts})
        response = requests.post(
            embed_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            timeout=int(config.get("timeout", 120)),
        )
        response.raise_for_status()
        data = response.json()
        vectors = data.get("embedding")
        if not vectors:
            raise RuntimeError("Embedding endpoint returned no vectors.")
        return vectors

    batch: List[Dict[str, Any]] = []
    next_id = 1
    for record in records:
        text = str(record.get("text_content", "")).strip()
        if not text:
            continue
        batch.append(record)
        if len(batch) >= batch_size:
            texts = [str(item.get("text_content", "")) for item in batch]
            vectors = embed_texts(texts)
            payload = []
            for item, vector in zip(batch, vectors):
                payload.append(
                    {
                        "id": next_id,
                        "text_content": str(item.get("text_content", "")),
                        "text_vector": vector,
                        "source_path": str(dict(item.get("metadata", {})).get("source_path", "")),
                        "material": str(dict(item.get("metadata", {})).get("material", "")),
                    }
                )
                next_id += 1
            client.insert(collection_name=collection, data=payload)
            batch = []
    if batch:
        texts = [str(item.get("text_content", "")) for item in batch]
        vectors = embed_texts(texts)
        payload = []
        for item, vector in zip(batch, vectors):
            payload.append(
                {
                    "id": next_id,
                    "text_content": str(item.get("text_content", "")),
                    "text_vector": vector,
                    "source_path": str(dict(item.get("metadata", {})).get("source_path", "")),
                    "material": str(dict(item.get("metadata", {})).get("material", "")),
                }
            )
            next_id += 1
        client.insert(collection_name=collection, data=payload)

    return True


def publish_ingestion_outputs(
    *,
    manifest_path: str,
    output_dir: str,
    publish_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Export ingestion payloads and optionally publish to live backends.

    Always writes:
    - `kg_facts.jsonl`
    - `vector_records.jsonl`
    - `neo4j/materials.csv`
    - `neo4j/countries.csv`
    - `neo4j/relations.csv`
    """
    publish_config = publish_config or {}
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "neo4j"), exist_ok=True)

    manifest = _load_manifest(manifest_path)
    facts = list(_iter_kg_facts(manifest))
    records = list(_iter_vector_records(manifest))

    kg_jsonl_path = os.path.join(output_dir, "kg_facts.jsonl")
    vector_jsonl_path = os.path.join(output_dir, "vector_records.jsonl")
    _write_jsonl(kg_jsonl_path, facts)
    _write_jsonl(vector_jsonl_path, records)

    materials, countries, relations = _build_neo4j_tables(facts)
    materials_csv = os.path.join(output_dir, "neo4j", "materials.csv")
    countries_csv = os.path.join(output_dir, "neo4j", "countries.csv")
    relations_csv = os.path.join(output_dir, "neo4j", "relations.csv")

    _write_csv(materials_csv, materials, fieldnames=["material_id:ID(Material)", "name"])
    _write_csv(countries_csv, countries, fieldnames=["country_id:ID(Country)", "name"])
    _write_csv(relations_csv, relations, fieldnames=[":START_ID(Material)", ":END_ID(Country)", ":TYPE", "stage"])

    published_neo4j = False
    published_milvus = False
    if publish_config.get("neo4j", {}).get("enabled", False):
        published_neo4j = _publish_neo4j(facts, publish_config.get("neo4j", {}))
    if publish_config.get("milvus", {}).get("enabled", False):
        published_milvus = _publish_milvus(records, publish_config.get("milvus", {}))

    summary = PublishSummary(
        kg_fact_count=len(facts),
        vector_record_count=len(records),
        material_node_count=len(materials),
        country_node_count=len(countries),
        published_neo4j=published_neo4j,
        published_milvus=published_milvus,
    )

    report = {
        "status": "ok",
        "summary": {
            "kg_fact_count": summary.kg_fact_count,
            "vector_record_count": summary.vector_record_count,
            "material_node_count": summary.material_node_count,
            "country_node_count": summary.country_node_count,
            "published_neo4j": summary.published_neo4j,
            "published_milvus": summary.published_milvus,
        },
        "artifacts": {
            "kg_facts_jsonl": kg_jsonl_path,
            "vector_records_jsonl": vector_jsonl_path,
            "neo4j_materials_csv": materials_csv,
            "neo4j_countries_csv": countries_csv,
            "neo4j_relations_csv": relations_csv,
        },
    }
    report_path = os.path.join(output_dir, "publish_report.json")
    with open(report_path, "w") as file:
        json.dump(report, file, indent=2)
    report["artifacts"]["publish_report"] = report_path
    return report
