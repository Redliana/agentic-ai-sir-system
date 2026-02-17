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
- Ingestion helpers load structured/unstructured data and build KG/vector payloads.

## Expected Structured Fields
For structured records, prefer fields like:
- `material`
- `country`
- `stage` (for example `extraction`, `processing`, `trade`)
- optional quantitative fields (`production`, `imports`, `consumption`)

## Notes
- This package is a baseline domain implementation for integration testing and workflow wiring.
- Replace synthetic runner logic with your production model as it becomes available.
