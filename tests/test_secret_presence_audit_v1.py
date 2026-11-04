"""Offline tests for secret-presence-only reporting."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from secret_presence_audit_v1 import SECRETS, make_report


class SecretAuditTests(unittest.TestCase):
    def test_no_values_appear_in_json(self):
        env = {f"AUDIT_{name}": f"highly-sensitive-test-secret-{name}-xyz"
               for name in SECRETS}
        report = make_report(env)
        payload = json.dumps(report)
        self.assertTrue(all(p["secret_present"] for p in report["providers"]))
        self.assertNotIn("highly-sensitive-test-secret", payload)
        self.assertEqual(report["provider_calls"], 0)
        self.assertEqual(report["calls_to_paid_services"], 0)
        self.assertTrue(all(p["api_validated"] is False for p in report["providers"]))
        self.assertTrue(all(p["billing_verified"] is False for p in report["providers"]))

    def test_legacy_secret_aliases_work(self):
        report = make_report({
            "AUDIT_GROQ": "existing-groq-token",
            "AUDIT_OPENROUTER2": "existing-router-token",
            "AUDIT_PIXABAY": "existing-pixabay-token",
            "AUDIT_VIDUOK": "existing-vidu-token",
        })
        by_name = {x["service"]: x for x in report["providers"]}
        for name in ("Groq", "OpenRouter", "Pixabay primary", "Vidu API primary"):
            self.assertTrue(by_name[name]["secret_present"])
        self.assertEqual(by_name["Groq"]["matching_secret_names"], ["GROQ"])
        self.assertFalse(by_name["AI Horde primary"]["secret_present"])

    def test_secondary_keys_do_not_become_active(self):
        report = make_report({
            "AUDIT_AIHORDE_API_KEY_2": "second",
            "AUDIT_PRIXIBAY2": "second",
            "AUDIT_VIDU2": "second",
        })
        states = {x["service"]: x for x in report["providers"]}
        self.assertFalse(states["AI Horde primary"]["secret_present"])
        self.assertTrue(states["AI Horde reserve"]["secret_present"])
        self.assertFalse(states["Pixabay primary"]["secret_present"])
        self.assertEqual(states["Pixabay secondary"]["integration_stage"],
                         "reserved_unverified_not_used")
        self.assertFalse(states["Vidu API primary"]["secret_present"])
        self.assertEqual(states["Vidu other"]["integration_stage"],
                         "not_auto_selected_for_api")

    def test_empty_blank_not_a_valid_secret(self):
        report = make_report({"AUDIT_GROQ": " ", "AUDIT_GEMINI_API_KEY": ""})
        by_name = {x["service"]: x for x in report["providers"]}
        self.assertFalse(by_name["Groq"]["secret_present"])
        self.assertFalse(by_name["Gemini TTS primary"]["secret_present"])


if __name__ == "__main__":
    unittest.main()
