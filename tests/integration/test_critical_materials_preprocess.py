import json
import os
import sys
import tempfile
import unittest
from unittest import mock

import yaml


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from domains.critical_materials.ingestion.preprocess import run_preprocess_workflow


class TestCriticalMaterialsPreprocess(unittest.TestCase):
    def test_preprocess_generates_ingestion_ready_outputs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            corpus_root = os.path.join(tmpdir, "corpus")
            os.makedirs(corpus_root, exist_ok=True)
            os.makedirs(os.path.join(corpus_root, "preferred"), exist_ok=True)
            os.makedirs(os.path.join(corpus_root, "backup_copy"), exist_ok=True)
            os.makedirs(os.path.join(corpus_root, "UNComtrade"), exist_ok=True)
            os.makedirs(os.path.join(corpus_root, "docs"), exist_ok=True)

            preferred_csv = os.path.join(corpus_root, "preferred", "supply.csv")
            backup_csv = os.path.join(corpus_root, "backup_copy", "supply.csv")
            csv_content = "material,country,unit,quantity\nGraphite,USA,t,1200\n"
            with open(preferred_csv, "w") as file:
                file.write(csv_content)
            with open(backup_csv, "w") as file:
                file.write(csv_content)

            trade_json = os.path.join(corpus_root, "UNComtrade", "trade.json")
            with open(trade_json, "w") as file:
                json.dump(
                    [{"reporter": "US", "commodity": "Rare Earth Elements", "qty": "2,500", "unit": "kg"}],
                    file,
                )

            pdf_scanned = os.path.join(corpus_root, "docs", "low_text.pdf")
            pdf_text = os.path.join(corpus_root, "docs", "textful.pdf")
            for path in (pdf_scanned, pdf_text):
                with open(path, "wb") as file:
                    file.write(b"%PDF-1.4")

            output_dir = os.path.join(tmpdir, "out")
            config = {
                "corpus_root": corpus_root,
                "output_dir": output_dir,
                "extensions": [".csv", ".json", ".pdf"],
                "deduplication": {
                    "enabled": True,
                    "method": "name_size",
                    "prefer_path_contains": ["preferred"],
                    "avoid_path_contains": ["backup"],
                },
                "preprocess": {
                    "global_field_aliases": {"reporter": "country", "commodity": "material", "qty": "quantity"},
                    "source_rules": [
                        {
                            "name": "trade",
                            "path_contains": ["UNComtrade"],
                            "default_values": {"stage": "trade"},
                        }
                    ],
                },
                "normalization": {
                    "country_map": {"us": "United States", "usa": "United States"},
                    "material_map": {"rare earth elements": "REE"},
                    "unit_map": {"kg": "kilograms", "t": "tonnes"},
                    "unit_to_tonnes": {"kilograms": 0.001, "tonnes": 1.0},
                    "quantity_fields": ["quantity"],
                },
                "outputs": {
                    "normalized_structured_path": "staged/normalized_structured.jsonl",
                    "ingestion_config_path": "ingestion_ready.yaml",
                    "preprocess_report_path": "preprocess_report.json",
                    "duplicate_manifest_path": "duplicates.json",
                    "ocr_queue_path": "ocr_queue.txt",
                },
            }

            with mock.patch(
                "domains.critical_materials.ingestion.preprocess._pdf_first_page_text_len",
                side_effect=lambda path: 10 if path.endswith("low_text.pdf") else 300,
            ):
                result = run_preprocess_workflow(config)

            self.assertEqual(result["status"], "ok")
            self.assertEqual(result["summary"]["duplicate_group_count"], 1)
            self.assertEqual(result["summary"]["ocr_queue_count"], 1)

            normalized_path = result["artifacts"]["normalized_structured_path"]
            ingestion_cfg_path = result["artifacts"]["ingestion_config_path"]
            ocr_queue_path = result["artifacts"]["ocr_queue_path"]
            self.assertTrue(os.path.exists(normalized_path))
            self.assertTrue(os.path.exists(ingestion_cfg_path))
            self.assertTrue(os.path.exists(ocr_queue_path))

            with open(normalized_path, "r") as file:
                records = [json.loads(line) for line in file if line.strip()]
            self.assertEqual(len(records), 2)
            self.assertIn("United States", {record.get("country") for record in records})
            self.assertIn("REE", {record.get("material") for record in records})
            ree_record = next(record for record in records if record.get("material") == "REE")
            self.assertAlmostEqual(float(ree_record["quantity"]), 2500.0)
            self.assertAlmostEqual(float(ree_record["quantity_tonnes"]), 2.5)

            with open(ingestion_cfg_path, "r") as file:
                ingestion_cfg = yaml.safe_load(file) or {}
            self.assertEqual(len(ingestion_cfg.get("structured_paths", [])), 1)
            self.assertIn(normalized_path, ingestion_cfg.get("structured_paths", []))
            self.assertIn(pdf_text, ingestion_cfg.get("unstructured_paths", []))
            self.assertNotIn(pdf_scanned, ingestion_cfg.get("unstructured_paths", []))
            self.assertTrue(ingestion_cfg.get("include_unstructured"))
            self.assertEqual(
                ingestion_cfg.get("structured", {}).get("keep_fields"),
                ["material", "country", "stage"],
            )

            with open(ocr_queue_path, "r") as file:
                ocr_lines = [line.strip() for line in file if line.strip()]
            self.assertIn(pdf_scanned, ocr_lines)


if __name__ == "__main__":
    unittest.main()
