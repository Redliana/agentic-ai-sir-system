"""CLI entrypoint for critical-materials heterogeneous data ingestion."""

import argparse
import json
import os
from typing import Any, Dict

import yaml

from .pipeline import run_ingestion_workflow


def _load_config(path: str) -> Dict[str, Any]:
    with open(path, "r") as file:
        if path.lower().endswith(".json"):
            return json.load(file) or {}
        return yaml.safe_load(file) or {}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run critical-materials ingestion workflow.")
    parser.add_argument(
        "--config",
        required=True,
        help="Path to ingestion config file (.yaml, .yml, or .json)",
    )
    parser.add_argument(
        "--output",
        default="",
        help="Optional JSON path to write workflow output manifest.",
    )
    args = parser.parse_args()

    config_path = os.path.abspath(args.config)
    config = _load_config(config_path)
    result = run_ingestion_workflow(config=config, output_path=args.output)
    print(json.dumps(result.get("summary", {}), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
