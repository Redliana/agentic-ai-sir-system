import csv
import os
import sys
import tempfile
import unittest


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from domains.critical_materials.model.scenario_runner import run_scenario


class TestCriticalMaterialsRunner(unittest.TestCase):
    def test_runner_writes_monthly_supply_chain_output(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "critical_materials_runs.csv")
            result = run_scenario(
                {
                    "seed": 7,
                    "time_horizon_months": 6,
                    "demand_growth_rate": 0.05,
                    "processing_disruption_pct": 0.20,
                    "substitution_factor": 0.10,
                    "material": "lithium",
                    "output_path": output_path,
                }
            )

            self.assertEqual(result["status"], "ok")
            self.assertTrue(os.path.exists(output_path))
            self.assertEqual(result["rows_written"], 18)

            with open(output_path, "r", newline="") as file:
                rows = list(csv.DictReader(file))

            self.assertEqual(len(rows), 18)
            self.assertEqual(rows[0]["material"], "lithium")
            self.assertIn("market_share", rows[0])
            self.assertIn("processing_capacity", rows[0])
            self.assertTrue(any(int(row["disruption_applied"]) == 1 for row in rows))


if __name__ == "__main__":
    unittest.main()
