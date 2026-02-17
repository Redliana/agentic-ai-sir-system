import json
import os
import sys
import tempfile
import unittest


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from domains.critical_materials.ingestion.pipeline import (
    ingest_heterogeneous_sources,
    run_ingestion_workflow,
)


class TestCriticalMaterialsIngestion(unittest.TestCase):
    def test_mixed_source_ingestion_builds_kg_and_vector_payloads(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "supply.csv")
            json_path = os.path.join(tmpdir, "profiles.json")
            jsonl_path = os.path.join(tmpdir, "trade.jsonl")
            txt_path = os.path.join(tmpdir, "brief.txt")
            md_path = os.path.join(tmpdir, "notes.md")
            xlsx_path = os.path.join(tmpdir, "table.xlsx")
            pdf_path = os.path.join(tmpdir, "report.pdf")

            with open(csv_path, "w") as file:
                file.write("material,country,stage\n")
                file.write("graphite,USA,processing\n")

            with open(json_path, "w") as file:
                json.dump([{"mineral": "nickel", "nation": "Canada"}], file)

            with open(jsonl_path, "w") as file:
                file.write(json.dumps({"commodity": "lithium", "jurisdiction": "Chile"}) + "\n")

            with open(txt_path, "w") as file:
                file.write("Critical minerals supply chains face disruption and concentration risk.")

            with open(md_path, "w") as file:
                file.write("# Policy note\nDiversification of processing can reduce bottlenecks.")

            # Intentional malformed files to verify graceful handling paths.
            with open(xlsx_path, "w") as file:
                file.write("not a real workbook")
            with open(pdf_path, "wb") as file:
                file.write(b"not a real pdf")

            config = {
                "source_paths": [
                    csv_path,
                    json_path,
                    jsonl_path,
                    txt_path,
                    md_path,
                    xlsx_path,
                    pdf_path,
                ],
                "material": "graphite",
                "structured": {
                    "required_fields": ["material", "country"],
                    "field_aliases": {
                        "mineral": "material",
                        "commodity": "material",
                        "nation": "country",
                        "jurisdiction": "country",
                    },
                    "default_values": {"stage": "supply"},
                },
                "unstructured": {"chunk_size": 8, "chunk_overlap": 2},
            }

            result = ingest_heterogeneous_sources(config)

            self.assertEqual(result["structured"]["record_count"], 3)
            self.assertGreater(result["unstructured"]["document_count"], 0)
            self.assertEqual(result["kg"]["fact_count"], 3)
            self.assertEqual(
                result["vector"]["record_count"],
                result["unstructured"]["document_count"],
            )
            self.assertEqual(result["summary"]["unknown_paths"], [])

            failed_structured_paths = {item["path"] for item in result["structured"]["failed_paths"]}
            failed_unstructured_paths = {item["path"] for item in result["unstructured"]["failed_paths"]}
            self.assertIn(xlsx_path, failed_structured_paths)
            self.assertIn(pdf_path, failed_unstructured_paths)

            manifest_path = os.path.join(tmpdir, "ingestion_manifest.json")
            persisted = run_ingestion_workflow(config, output_path=manifest_path)
            self.assertTrue(os.path.exists(manifest_path))
            self.assertEqual(
                persisted["summary"]["structured_record_count"],
                result["summary"]["structured_record_count"],
            )


if __name__ == "__main__":
    unittest.main()
