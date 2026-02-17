import os
import sys
import tempfile
import unittest
from unittest import mock


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from agents.ui_agent import UIAgent


class TestUIParameterPrompting(unittest.TestCase):
    def test_prompt_for_parameters_uses_defaults_when_requested(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            agent = UIAgent(
                domain_config={},
                test_mode=True,
                params_file=os.path.join(tmpdir, "params.yaml"),
            )
            defaults = {
                "seed": 42,
                "time_horizon_months": 24,
                "demand_growth_rate": 0.08,
                "material": "graphite",
            }
            with mock.patch("builtins.input", side_effect=["default"]):
                chosen = agent.prompt_for_parameters(defaults)

            self.assertEqual(chosen, defaults)

    def test_prompt_for_parameters_accepts_domain_specific_custom_values(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            agent = UIAgent(
                domain_config={},
                test_mode=True,
                params_file=os.path.join(tmpdir, "params.yaml"),
            )
            defaults = {
                "time_horizon_months": 24,
                "demand_growth_rate": 0.08,
                "processing_disruption_pct": 0.15,
                "material": "graphite",
            }
            with mock.patch(
                "builtins.input",
                side_effect=["custom", "12", "0.25", "0.30", "lithium"],
            ):
                chosen = agent.prompt_for_parameters(defaults)

            self.assertEqual(chosen["time_horizon_months"], 12)
            self.assertAlmostEqual(chosen["demand_growth_rate"], 0.25)
            self.assertAlmostEqual(chosen["processing_disruption_pct"], 0.30)
            self.assertEqual(chosen["material"], "lithium")


if __name__ == "__main__":
    unittest.main()
