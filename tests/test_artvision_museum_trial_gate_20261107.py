"""Regression tests for Museum trial gating (no automatic approval)."""
import unittest
from src.artvision_queue_next_v190 import plan

WORK = {"id": "simberg_garden", "slots_delivered_this_selection": 2,
        "museum_approved": False}
QUEUE = {"works": [WORK]}
BASE = {"verified_slots": {"simberg_garden": ["critico_standard", "cinema_standard"]},
        "blocked": {}}

class MuseumTrialTests(unittest.TestCase):
    def test_without_evidence_stays_blocked(self):
        result = plan(QUEUE, BASE)
        self.assertEqual(result["render_candidates"], [])
        self.assertEqual(len(result["pending"]), 2)

    def test_verified_neutral_trial_not_gold(self):
        state = dict(BASE, museum_trial_evidence={"simberg_garden": {
            "source_url": "https://example.org/licensed-source",
            "source_sha256": "a" * 64, "source_license": "CC BY 4.0",
            "painting_dimensions_verified": True,
            "scene_kind": "neutral_scenography",
            "rights_reviewed": True, "asset_readback_verified": True}})
        result = plan(QUEUE, state)
        self.assertEqual(len(result["render_candidates"]), 2)
        self.assertTrue(all(x["kind"] == "museum_trial_render_candidate_needs_preflight"
                            and not x["gold"] and not x["publication_authorized"]
                            for x in result["render_candidates"]))
        self.assertEqual(result["new_mp4_verified_by_planner"], 0)

    def test_missing_license_stays_blocked(self):
        state = dict(BASE, museum_trial_evidence={"simberg_garden": {
            "source_url": "https://example.org/source",
            "source_sha256": "a" * 64,
            "painting_dimensions_verified": True,
            "scene_kind": "neutral_scenography",
            "rights_reviewed": True, "asset_readback_verified": True}})
        self.assertEqual(plan(QUEUE, state)["render_candidates"], [])

if __name__ == "__main__":
    unittest.main()
