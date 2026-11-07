"""Regression tests for Museum trial gating (no automatic approval)."""
import unittest
import json
from pathlib import Path
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
            "scenography_disclosure": "Fictional neutral gallery scene; not an actual installation.",
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


    def test_licensed_magic_circle_is_a_trial_candidate_not_approved_delivery(self):
        manifest = json.loads(Path("config/artvision_museum_trial_sources_v208.json").read_text(encoding="utf8"))
        self.assertEqual(manifest["schema"], "artvision-museum-trial-source-v208")
        wid = "waterhouse_magic_circle_1886_tate_n01572"
        q = {"works": [{"id": wid, "slots_delivered_this_selection": 2,
                         "museum_approved": False}]}
        s = {"verified_slots": {wid: ["critico_standard", "cinema_standard"]}, "blocked": {}}
        result = plan(q, s, manifest["museum_trial_evidence"])
        self.assertEqual(len(result["render_candidates"]), 2)
        self.assertTrue(all(x["source_manifest_is_not_render_approval"]
                            and x["artistic_review"] == "PENDING"
                            and x["gold"] is False
                            and x["publication_authorized"] is False
                            for x in result["render_candidates"]))
        self.assertEqual(result["new_mp4_verified_by_planner"], 0)

    def test_trial_source_manifest_cannot_sneak_bad_hash_or_unlicensed_room(self):
        valid = json.loads(Path("config/artvision_museum_trial_sources_v208.json").read_text(encoding="utf8"))["museum_trial_evidence"]
        wid = next(iter(valid))
        q = {"works": [{"id": wid, "slots_delivered_this_selection": 2, "museum_approved": False}]}
        s = {"verified_slots": {wid: ["critico_standard", "cinema_standard"]}, "blocked": {}}
        for override in ({"source_sha256": "z" * 64}, {"scenography_disclosure": ""},
                         {"rights_reviewed": False}, {"gold": True},
                         {"publication_authorized": True}, {"source_url": "http://example.com/room.jpg"}):
            changed = dict(valid[wid], **override)
            self.assertEqual(plan(q, s, {wid: changed})["render_candidates"], [],
                             msg=str(override))

if __name__ == "__main__":
    unittest.main()
