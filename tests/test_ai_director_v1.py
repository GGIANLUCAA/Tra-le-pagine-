"""Regression tests for isolated AI Director V1; all tests are offline."""
import contextlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from ai_director_v1 import (
    DirectorError, inspect_brief, live_candidates, read_json, render_dashboard,
    write_json, MODEL_PATTERN, SCHEMA
)


def sample(fmt="documentary"):
    return {
        "schema": SCHEMA, "format": fmt, "title": "A careful documentary study",
        "duration_s": 6, "narration": "",
        "scenes": [
            {"id": "shot_01", "start_s": 0, "end_s": 3,
             "asset_id": "archive_01", "visual": "Original documented archive image"},
            {"id": "shot_02", "start_s": 3, "end_s": 6,
             "asset_id": "archive_02", "visual": "Second source shown without visual effects"}
        ],
    }


class DirectorTests(unittest.TestCase):
    def test_innocent_dry_run_is_review_not_approval(self):
        r = inspect_brief(sample())
        self.assertEqual(r["status"], "needs_artistic_review")
        self.assertFalse(r["qa"]["mp4_seen"])
        self.assertFalse(r["qa"]["human_approved"])
        self.assertFalse(r["qa"]["published"])
        self.assertEqual(r["model_calls_attempted"], 0)

    def test_flash_frame_is_blocking(self):
        x = sample()
        x["scenes"][1]["start_s"] = 3
        x["scenes"][1]["end_s"] = 3.08
        x["duration_s"] = 3.08
        r = inspect_brief(x)
        self.assertEqual(r["status"], "needs_changes")
        self.assertIn("FLASH_FRAME", [y["code"] for y in r["issues"]])

    def test_overlapping_shots_blocked(self):
        x = sample()
        x["scenes"][1]["start_s"] = 2.4
        r = inspect_brief(x)
        self.assertIn("OVERLAP", [y["code"] for y in r["issues"]])

    def test_color_claim_requires_real_mp4_gate(self):
        x = sample("storia_rivive")
        x["duration_s"] = 15
        x["scenes"][1]["end_s"] = 15
        x["scenes"][0]["color_reveal_s"] = 0.9
        r = inspect_brief(x)
        self.assertIn("TRUE_COLOR_UNVERIFIED", [y["code"] for y in r["issues"]])

    def test_artvision_narration_mapping(self):
        x = sample("artvision_critico")
        x["narration"] = "La scena descrive un ponte antico e i suoi viaggiatori."
        x["scenes"][0]["spoken_excerpt"] = "Parole che non ci sono."
        x["scenes"][1]["spoken_excerpt"] = "ponte antico"
        r = inspect_brief(x)
        self.assertIn("VOICE_SCENE_MAP_MISMATCH", [y["code"] for y in r["issues"]])

    def test_gold_and_auto_publish_rejected(self):
        x = sample()
        x["auto_publish"] = True
        x["claims_gold"] = True
        self.assertIn("UNAUTHORIZED_APPROVAL",
                      [y["code"] for y in inspect_brief(x)["issues"]])

    def test_duplicate_scene_id_rejected(self):
        x = sample()
        x["scenes"][1]["id"] = x["scenes"][0]["id"]
        with self.assertRaises(DirectorError):
            inspect_brief(x)

    def test_only_fixed_free_model_identifiers(self):
        self.assertIsNotNone(MODEL_PATTERN.fullmatch("google/gemma-3-27b-it:free"))
        self.assertIsNone(MODEL_PATTERN.fullmatch("openrouter/free"))
        self.assertIsNone(MODEL_PATTERN.fullmatch("anthropic/claude-opus-4.6"))

    def test_live_disabled_by_default_even_with_keys(self):
        with patch.dict(os.environ, {"AI_DIRECTOR_LIVE": "0"}):
            with self.assertRaisesRegex(DirectorError, "disabled"):
                live_candidates(sample(), inspect_brief(sample()),
                                models=["google/gemma-3-27b-it:free",
                                        "meta-llama/llama-3.3-70b-instruct:free"],
                                policy={"routes": []}, key="test")

    def test_empty_policy_fails_closed_before_network(self):
        with patch.dict(os.environ, {"AI_DIRECTOR_LIVE": "1"}):
            with self.assertRaises(Exception):
                live_candidates(sample(), inspect_brief(sample()),
                                models=["google/gemma-3-27b-it:free",
                                        "meta-llama/llama-3.3-70b-instruct:free"],
                                policy={"schema": "free-llm-zero-cost-v1",
                                        "default_deny": True,
                                        "max_evidence_age_days": 7, "routes": []},
                                key="test",
                                transport=lambda *args, **kwargs: self.fail("Unexpected network"))

    def test_reports_are_safe_for_android(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "state.json"
            h = Path(tmp) / "state.html"
            r = inspect_brief(sample())
            write_json(p, r)
            render_dashboard(r, h)
            self.assertEqual(read_json(p)["qa"]["published"], False)
            self.assertIn("Report statico", h.read_text(encoding="utf-8"))
            self.assertNotIn("sk-or-", h.read_text(encoding="utf-8"))

    def test_existing_zero_cost_policy_still_default_deny(self):
        p = json.loads((ROOT / "config/free_llm_zero_cost_v1.json").read_text())
        self.assertTrue(p["default_deny"])
        self.assertEqual(p["routes"], [])


if __name__ == "__main__":
    unittest.main()
