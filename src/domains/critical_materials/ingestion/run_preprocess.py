"""CLI entrypoint for corpus preprocessing before ingestion."""

import argparse
import json
import os
from typing import Any, Dict

import yaml

from .preprocess import run_preprocess_workflow


def _load_config(path: str) -> Dict[str, Any]:
    with open(path, "r") as file:
        if path.lower().endswith(".json"):
            return json.load(file) or {}
        return yaml.safe_load(file) or {}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Preprocess critical-materials corpus and emit ingestion-ready artifacts."
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to preprocess config (.yaml, .yml, or .json).",
    )
    parser.add_argument(
        "--output-dir",
        default="",
        help="Override output directory from config.",
    )
    args = parser.parse_args()

    config_path = os.path.abspath(args.config)
    config = _load_config(config_path)
    if args.output_dir:
        config["output_dir"] = os.path.abspath(args.output_dir)

    result = run_preprocess_workflow(config=config)
    print(json.dumps(result["summary"], indent=2))
    print(json.dumps(result["artifacts"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
