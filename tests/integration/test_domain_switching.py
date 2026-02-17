import os
import tempfile
import unittest

import yaml


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC_DIR = os.path.join(ROOT_DIR, "src")

import sys

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from agents.ui_agent import UIAgent
from core.registry.domain_loader import load_active_domain, load_domain


class TestDomainSwitching(unittest.TestCase):
    def test_default_active_domain_is_sir(self):
        domain = load_active_domain()
        self.assertEqual(domain["name"], "sir")
        self.assertIn("ui", domain["config"])
        self.assertIn("analysis", domain["config"])

    def test_load_critical_materials_domain_by_name(self):
        domain = load_domain("critical_materials")
        self.assertEqual(domain["name"], "critical_materials")
        schema_path = os.path.join(
            ROOT_DIR, "src", "domains", "critical_materials", "ontology", "schema.cypher"
        )
        with open(schema_path, "r") as file:
            self.assertIn("Material", file.read())

    def test_can_switch_active_domain_with_temp_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_config_path = os.path.join(tmpdir, "domains.yaml")
            data = {
                "active_domain": "critical_materials",
                "domains": {
                    "critical_materials": {
                        "config_path": os.path.join(
                            ROOT_DIR, "src", "domains", "critical_materials", "domain.yaml"
                        ),
                        "package": "domains.critical_materials",
                    },
                    "sir": {
                        "config_path": os.path.join(
                            ROOT_DIR, "src", "domains", "sir", "domain.yaml"
                        ),
                        "package": "domains.sir",
                    },
                },
            }
            with open(tmp_config_path, "w") as file:
                yaml.safe_dump(data, file)

            domain = load_active_domain(domains_config_path=tmp_config_path)
            self.assertEqual(domain["name"], "critical_materials")

    def test_ui_agent_keyword_intent_is_domain_driven(self):
        critical = load_domain("critical_materials")["config"]
        ui = UIAgent(domain_config=critical, test_mode=True)
        self.assertEqual(ui.classify_intent("Please run scenario with shock assumptions"), "run")
        self.assertEqual(ui.classify_intent("Can you analyze supply risk and hhi?"), "analyze")
        self.assertEqual(ui.classify_intent("Explain the methodology and assumptions"), "learn")
        self.assertEqual(ui.classify_intent("Quit"), "exit")


if __name__ == "__main__":
    unittest.main()
