# Critical Materials Domain Overview

This domain package supports workflows for:
- Supply concentration and dependency analysis
- Processing bottleneck and disruption scenarios
- Policy and trade risk exploration

## Current Capabilities
- Scenario runner outputs monthly synthetic supply-chain snapshots to CSV.
- Analyzer metrics compute:
  - Supply concentration HHI
  - Import dependency ratio
  - Processing bottleneck score
- Ingestion helpers load heterogeneous data and build KG/vector payloads.

## Heterogeneous Ingestion Support
- Structured: `.csv`, `.json`, `.jsonl`, `.xlsx`
- Unstructured: `.txt`, `.md`, `.pdf`
- Routing and transformation:
  - structured rows -> normalized records
  - normalized records -> KG fact payloads
  - unstructured chunks -> vector indexing payloads

### Run Ingestion CLI
```bash
python -m domains.critical_materials.ingestion.run_ingestion --config path/to/ingestion.yaml --output tmp/ingestion_manifest.json
```
The command prints summary counts and optionally writes a detailed JSON manifest.

### Optional Dependencies
- `.xlsx` parsing requires `openpyxl`
- `.pdf` extraction requires `pypdf`

## Expected Structured Fields
For structured records, prefer fields like:
- `material`
- `country`
- `stage` (for example `extraction`, `processing`, `trade`)
- optional quantitative fields (`production`, `imports`, `consumption`)

## Notes
- This package is a baseline domain implementation for integration testing and workflow wiring.
- Replace synthetic runner logic with your production model as it becomes available.
