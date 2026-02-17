"""CLI entrypoint for publishing ingestion outputs to load packages/backends."""

import argparse
import json
import os
from typing import Any, Dict

import yaml

from .publish import publish_ingestion_outputs


def _load_config(path: str) -> Dict[str, Any]:
    with open(path, "r") as file:
        if path.lower().endswith(".json"):
            return json.load(file) or {}
        return yaml.safe_load(file) or {}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Publish ingestion outputs to backend-ready artifacts and optional live sinks."
    )
    parser.add_argument("--manifest", required=True, help="Path to ingestion manifest JSON.")
    parser.add_argument("--output-dir", required=True, help="Directory to write publish artifacts.")
    parser.add_argument(
        "--publish-config",
        default="",
        help="Optional YAML/JSON file for live backend publish settings (neo4j/milvus).",
    )
    args = parser.parse_args()

    publish_config: Dict[str, Any] = {}
    if args.publish_config:
        publish_config = _load_config(os.path.abspath(args.publish_config))

    result = publish_ingestion_outputs(
        manifest_path=os.path.abspath(args.manifest),
        output_dir=os.path.abspath(args.output_dir),
        publish_config=publish_config,
    )
    print(json.dumps(result["summary"], indent=2))
    print(json.dumps(result["artifacts"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
