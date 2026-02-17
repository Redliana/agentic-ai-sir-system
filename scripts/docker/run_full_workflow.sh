#!/usr/bin/env bash
set -euo pipefail

CORPUS_ROOT="${CORPUS_ROOT:-/corpus}"
RUN_NAME="${RUN_NAME:-cmm_run_$(date +%Y%m%d_%H%M%S)}"
RUN_ROOT="${RUN_ROOT:-/workspace/${RUN_NAME}}"
ENABLE_UNSTRUCTURED="${ENABLE_UNSTRUCTURED:-false}"
PREPROCESS_REQUIRED_FIELDS="${PREPROCESS_REQUIRED_FIELDS:-material,country}"
STRUCTURED_KEEP_FIELDS="${STRUCTURED_KEEP_FIELDS:-material,country,stage}"

mkdir -p "${RUN_ROOT}"

echo "[workflow] waiting for neo4j:7687..."
python - <<'PY'
import socket
import time

deadline = time.time() + 120
while time.time() < deadline:
    try:
        with socket.create_connection(("neo4j", 7687), timeout=2):
            print("[workflow] neo4j reachable")
            raise SystemExit(0)
    except OSError:
        time.sleep(2)
print("[workflow] neo4j not reachable after timeout")
raise SystemExit(1)
PY

PREPROCESS_CFG="${RUN_ROOT}/preprocess_config.yaml"
python - <<PY
import os
import yaml


def _csv_fields(value: str):
    return [field.strip() for field in value.split(",") if field.strip()]


def _to_bool(value: str, default: bool = False) -> bool:
    text = str(value).strip().lower()
    if not text:
        return default
    return text in {"1", "true", "yes", "on"}


template_path = "configs/critical_materials_preprocess.example.yaml"
with open(template_path, "r") as f:
    cfg = yaml.safe_load(f) or {}
cfg["corpus_root"] = "${CORPUS_ROOT}"
cfg["output_dir"] = "${RUN_ROOT}/preprocess"

preprocess_cfg = dict(cfg.get("preprocess", {}))
required_fields = _csv_fields(os.getenv("PREPROCESS_REQUIRED_FIELDS", ""))
if required_fields:
    preprocess_cfg["required_fields"] = required_fields
cfg["preprocess"] = preprocess_cfg

ingestion_cfg = dict(cfg.get("ingestion", {}))
ingestion_cfg["include_unstructured"] = _to_bool(os.getenv("ENABLE_UNSTRUCTURED", "false"), default=False)
structured_ingestion_cfg = dict(ingestion_cfg.get("structured", {}))
keep_fields = _csv_fields(os.getenv("STRUCTURED_KEEP_FIELDS", ""))
if keep_fields:
    structured_ingestion_cfg["keep_fields"] = keep_fields
ingestion_cfg["structured"] = structured_ingestion_cfg
cfg["ingestion"] = ingestion_cfg

with open("${PREPROCESS_CFG}", "w") as f:
    yaml.safe_dump(cfg, f, sort_keys=False)
print("${PREPROCESS_CFG}")
PY

echo "[workflow] include_unstructured=${ENABLE_UNSTRUCTURED}"
echo "[workflow] preprocess_required_fields=${PREPROCESS_REQUIRED_FIELDS}"
echo "[workflow] structured_keep_fields=${STRUCTURED_KEEP_FIELDS}"

echo "[workflow] running preprocess..."
PYTHONPATH=src python -m domains.critical_materials.ingestion.run_preprocess --config "${PREPROCESS_CFG}"

INGESTION_CFG="${RUN_ROOT}/preprocess/ingestion_ready.yaml"
INGESTION_MANIFEST="${RUN_ROOT}/preprocess/ingestion_manifest.json"

echo "[workflow] running ingestion..."
PYTHONPATH=src python -m domains.critical_materials.ingestion.run_ingestion \
  --config "${INGESTION_CFG}" \
  --output "${INGESTION_MANIFEST}"

PUBLISH_CFG="${RUN_ROOT}/publish_config.yaml"
PUBLISH_CFG_PATH="${PUBLISH_CFG}" python - <<'PY'
import os
import yaml

cfg = {
    "neo4j": {
        "enabled": True,
        "uri": os.getenv("NEO4J_URI", "bolt://neo4j:7687"),
        "user": os.getenv("NEO4J_USER", "neo4j"),
        "password": os.getenv("NEO4J_PASSWORD", ""),
        "database": os.getenv("NEO4J_DATABASE", "neo4j"),
        "batch_size": 5000,
    },
    "milvus": {
        "enabled": False,
        "uri": os.getenv("MILVUS_URI", ""),
        "token": os.getenv("MILVUS_AUTH_TOKEN", ""),
        "collection": "critical_materials_docs",
        "embedding_model": "v3large",
        "embed_url": os.getenv("ARGO_EMBED_URL", ""),
        "batch_size": 128,
        "timeout": 120,
    },
}
out = os.environ["PUBLISH_CFG_PATH"]
with open(out, "w") as f:
    yaml.safe_dump(cfg, f, sort_keys=False)
print(out)
PY

echo "[workflow] running publish..."
PYTHONPATH=src python -m domains.critical_materials.ingestion.run_publish \
  --manifest "${INGESTION_MANIFEST}" \
  --output-dir "${RUN_ROOT}/publish" \
  --publish-config "${PUBLISH_CFG}"

echo "[workflow] complete"
echo "[workflow] run_root=${RUN_ROOT}"
echo "[workflow] preprocess_report=${RUN_ROOT}/preprocess/preprocess_report.json"
echo "[workflow] ingestion_manifest=${INGESTION_MANIFEST}"
echo "[workflow] publish_report=${RUN_ROOT}/publish/publish_report.json"
