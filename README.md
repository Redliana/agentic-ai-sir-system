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
python -m domains.critical_materials.ingestion.run_ingestion --config configs/critical_materials_ingestion.example.yaml --output tmp/ingestion_manifest.json
```
`.xlsx` ingestion uses `openpyxl` and `.pdf` ingestion uses `pypdf`.

## Tests
Run integration tests with:
```bash
python -m unittest discover -s tests/integration -p "test_*.py"
```
