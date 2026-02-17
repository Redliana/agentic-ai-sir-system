import os
import sys
import tempfile
import unittest

import pandas as pd


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from agents.analyzer_agent import AnalyzerAgent
from core.registry.domain_loader import load_domain
from domains.critical_materials.model.scenario_runner import run_scenario


class TestCriticalMaterialsWorkflow(unittest.TestCase):
    def test_scenario_runner_writes_expected_log(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "critical_materials_runs.csv")
            result = run_scenario(
                {
                    "seed": 7,
                    "time_horizon_months": 6,
                    "demand_growth_rate": 0.03,
                    "processing_disruption_pct": 0.18,
                    "substitution_factor": 0.08,
                    "output_path": output_path,
                }
            )

            self.assertEqual(result["status"], "completed")
            self.assertTrue(os.path.exists(output_path))
            self.assertGreater(result["rows"], 0)

            df = pd.read_csv(output_path)
            required_columns = {
                "run_id",
                "month",
                "material",
                "supplier",
                "country",
                "market_share",
                "imports",
                "consumption",
                "processing_capacity",
                "demand",
                "effective_supply",
                "supply_gap",
            }
            self.assertTrue(required_columns.issubset(df.columns))
            self.assertGreater(df["month"].max(), 0)

    def test_analyzer_agent_computes_critical_material_metrics(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "critical_materials_runs.csv")
            run_scenario(
                {
                    "seed": 11,
                    "time_horizon_months": 4,
                    "demand_growth_rate": 0.02,
                    "processing_disruption_pct": 0.12,
                    "substitution_factor": 0.05,
                    "output_path": output_path,
                }
            )

            domain_cfg = load_domain("critical_materials")["config"]
            analyzer = AnalyzerAgent(state_logs=output_path, domain_config=domain_cfg)
            result = analyzer.analyze(
                "Please analyze supply risk using hhi, dependency, and bottleneck metrics."
            )

            self.assertIn("supply_concentration_hhi", result)
            self.assertIn("import_dependency", result)
            self.assertIn("processing_bottleneck_score", result)


if __name__ == "__main__":
    unittest.main()

