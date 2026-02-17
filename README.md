# Agentic AI Domain Platform

This repository provides a multi-agent workflow platform with pluggable domain packages.
It supports:
- model execution
- result analysis
- RAG-based question answering
- configurable UI/intent routing

The same orchestration stack can run multiple use-cases by switching the active domain.

## Current Domains
- `sir`: stochastic infectious disease simulation
- `critical_materials`: critical minerals and materials supply-chain workflow

## Project Structure
- `configs/platform.yaml`: graph routing and orchestration profile
- `configs/domains.yaml`: active domain + domain registry
- `src/agents`: agent implementations (UI, model, analyzer, reporter, RAG)
- `src/core`: provider factory, contracts, orchestration, and registry
- `src/domains/<domain_name>`: domain packs (config, model, analysis, knowledge, ingestion)

## Quickstart
1. Install dependencies:
```bash
python -m pip install -r requirements.txt
```
2. Set active domain in `configs/domains.yaml`:
```yaml
active_domain: critical_materials
```
3. Run the workflow:
```bash
python src/main_graph.py
```

## Critical Materials Workflow
The `critical_materials` domain includes:
- scenario runner writing monthly outputs to `src/logs/critical_materials_runs.csv`
- metrics for supply concentration (HHI), import dependency, and bottleneck risk
- ingestion helpers for heterogeneous source loading (`.csv`, `.json`, `.jsonl`, `.xlsx`, `.txt`, `.md`, `.pdf`)
- mapping helpers for KG and vector payloads

Start by setting `active_domain: critical_materials`, then request:
- run scenario
- analyze supply risk / HHI / bottleneck
- learn assumptions and methods

Run heterogeneous ingestion with:
```bash
PYTHONPATH=src python -m domains.critical_materials.ingestion.run_ingestion --config configs/critical_materials_ingestion.example.yaml --output tmp/ingestion_manifest.json
```
`.xlsx` ingestion uses `openpyxl` and `.pdf` ingestion uses `pypdf`.

For large raw corpora, run preprocessing first:
```bash
PYTHONPATH=src python -m domains.critical_materials.ingestion.run_preprocess --config configs/critical_materials_preprocess.example.yaml
```
This generates:
- `ingestion_ready.yaml` (ingestion config with deduplicated source paths)
- `staged/normalized_structured.jsonl` (normalized structured records)
- `ocr_queue.txt` (PDFs requiring OCR)
- `duplicates.json` (duplicate selection decisions)
- `preprocess_report.json` (includes `quality_filtered_record_count` and filter reason counts)

Quality filtering can be configured under `normalization` in `configs/critical_materials_preprocess.example.yaml`:
- `country_drop_equals`
- `country_drop_contains`
- `material_drop_equals`
- `material_drop_contains`

Material naming normalization can also be configured under `normalization`:
- `material_casefold` (for case-insensitive material normalization)
- `material_map` (for explicit alias-to-canonical mappings, for example `gold -> gold, mine`)

Publish ingestion outputs to backend-ready load packages:
```bash
PYTHONPATH=src python -m domains.critical_materials.ingestion.run_publish \
  --manifest /tmp/cmm_preprocess_run_20260217/ingestion_manifest.json \
  --output-dir /tmp/cmm_preprocess_run_20260217/publish
```
Optional live backend publish settings can be passed via `--publish-config configs/critical_materials_publish.example.yaml`.

## Containerized Workflow (Neo4j + Pipeline)
This repo includes a contained Docker stack for the full workflow:
- `neo4j` container (local graph database)
- `workflow` container (preprocess, ingest, publish tooling)

1. Create env file:
```bash
cp .env.workflow.example .env.workflow
```
2. Start containers:
```bash
docker compose --env-file .env.workflow -f docker-compose.workflow.yml up -d --build
```
3. Run full workflow in container:
```bash
docker compose --env-file .env.workflow -f docker-compose.workflow.yml exec workflow \
  bash -lc "scripts/docker/run_full_workflow.sh"
```
By default the runner executes in memory-safe KG mode (`ENABLE_UNSTRUCTURED=false`) and keeps only
`material,country,stage` structured fields during ingestion. You can override at runtime:
```bash
docker compose --env-file .env.workflow -f docker-compose.workflow.yml exec workflow \
  bash -lc "ENABLE_UNSTRUCTURED=true STRUCTURED_KEEP_FIELDS=material,country,stage scripts/docker/run_full_workflow.sh"
```
Optional knobs:
- `ENABLE_UNSTRUCTURED`: set `true` to include unstructured chunk ingestion/vector payloads.
- `PREPROCESS_REQUIRED_FIELDS`: comma-separated structured required fields (default `material,country`).
- `STRUCTURED_KEEP_FIELDS`: comma-separated structured fields retained post-filter (default `material,country,stage`).
4. Open Neo4j Browser:
- URL: `http://localhost:7474`
- User: `neo4j`
- Password: value from `.env.workflow` (`NEO4J_PASSWORD`)

Run output artifacts are written under the mounted workspace path (`CMM_WORKSPACE_PATH` in `.env.workflow`).

## Tests
Run integration tests with:
```bash
python -m unittest discover -s tests/integration -p "test_*.py"
```
