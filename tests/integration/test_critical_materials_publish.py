import json
import os
import sys
import tempfile
import unittest


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from domains.critical_materials.ingestion.publish import publish_ingestion_outputs


class TestCriticalMaterialsPublish(unittest.TestCase):
    def test_publish_writes_backend_ready_artifacts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = os.path.join(tmpdir, "ingestion_manifest.json")
            publish_dir = os.path.join(tmpdir, "publish")

            manifest = {
                "kg": {
                    "facts": [
                        {
                            "subject_type": "Material",
                            "subject_id": "lithium",
                            "predicate": "INVOLVES_COUNTRY",
                            "object_type": "Country",
                            "object_id": "Chile",
                            "properties": {"stage": "supply"},
                        },
                        {
                            "subject_type": "Material",
                            "subject_id": "nickel",
                            "predicate": "INVOLVES_COUNTRY",
                            "object_type": "Country",
                            "object_id": "Indonesia",
                            "properties": {"stage": "processing"},
                        },
                    ],
                    "fact_count": 2,
                },
                "vector": {
                    "records": [
                        {
                            "id": "doc-1",
                            "text_content": "Lithium supply chain note.",
                            "metadata": {"source_path": "/tmp/a.txt", "material": "lithium"},
                        }
                    ],
                    "record_count": 1,
                },
            }
            with open(manifest_path, "w") as file:
                json.dump(manifest, file)

            result = publish_ingestion_outputs(
                manifest_path=manifest_path,
                output_dir=publish_dir,
                publish_config={"neo4j": {"enabled": False}, "milvus": {"enabled": False}},
            )

            self.assertEqual(result["status"], "ok")
            self.assertEqual(result["summary"]["kg_fact_count"], 2)
            self.assertEqual(result["summary"]["vector_record_count"], 1)
            self.assertFalse(result["summary"]["published_neo4j"])
            self.assertFalse(result["summary"]["published_milvus"])

            artifacts = result["artifacts"]
            for key in [
                "kg_facts_jsonl",
                "vector_records_jsonl",
                "neo4j_materials_csv",
                "neo4j_countries_csv",
                "neo4j_relations_csv",
                "publish_report",
            ]:
                self.assertTrue(os.path.exists(artifacts[key]), key)

            with open(artifacts["neo4j_relations_csv"], "r") as file:
                csv_text = file.read()
            self.assertIn("INVOLVES_COUNTRY", csv_text)
            self.assertIn("supply", csv_text)
            self.assertIn("processing", csv_text)


if __name__ == "__main__":
    unittest.main()
