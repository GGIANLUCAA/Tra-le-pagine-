"""Failure-safe selector tests; all synthetic input, never hits remote services."""
import copy
import importlib.util
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "scripts/artvision_owner_nonstop_preflight_v1.py"
spec = importlib.util.spec_from_file_location("preflight", P)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def fixture():
    q, r = [], []
    for i in range(1, 31):
        base = {"selection_order": i, "title_as_chosen": "Painting " + str(i),
                "artist_as_chosen": "Artist " + str(i)}
        q.append({**base, "provisional_production_priority": i,
                  "production_ready": False, "rights_and_source_gate": "pending_review",
                  "render_status": "not_started"})
        r.append({**base, **{gate: False for gate in mod.GATES}})
    return {"selected_works": q}, {"works": r}


def clear(q, r, idx):
    a, b = q["selected_works"][idx], r["works"][idx]
    a["production_ready"] = True
    a["rights_and_source_gate"] = "cleared"
    b.update({gate: True for gate in mod.GATES})
    b["source_sha256"] = "a" * 64


class OwnerNonstopPreflight(unittest.TestCase):
    def test_all_pending_does_not_invent_production(self):
        q, r = fixture()
        p = mod.plan(q, r, [])
        self.assertEqual(p["status"], "no_source_cleared_work")
        self.assertEqual(p["blocked_count"], 30)
        self.assertFalse(p["auto_render"])
        self.assertFalse(p["auto_publish"])

    def test_ready_candidate_only_after_complete_evidence(self):
        q, r = fixture()
        clear(q, r, 3)
        p = mod.plan(q, r, [])
        self.assertEqual(p["first_preflight_candidate"]["selection_order"], 4)
        self.assertEqual(p["status"], "candidate_preflight_only")
        self.assertFalse(p["auto_render"])

    def test_stale_queue_cannot_rerender_verified_checkpoint(self):
        q, r = fixture()
        clear(q, r, 15)
        w = q["selected_works"][15]
        cp = {"secondary_work": {"selection_order": w["selection_order"],
              "selected_title": w["title_as_chosen"], "artist": w["artist_as_chosen"],
              "variant": "cinema_standard"}, "mp4": {"sha256": "b" * 64},
              "github_workflow_run_id": 123}
        p = mod.plan(q, r, [cp])
        self.assertIsNone(p["first_preflight_candidate"])
        self.assertIn("existing_verified_mp4_cinema_standard",
                      p["checks"][15]["reasons"])

    def test_unmatched_register_fails_closed(self):
        q, r = fixture()
        r["works"][0]["artist_as_chosen"] = "Wrong"
        with self.assertRaises(ValueError):
            mod.plan(q, r, [])

    def test_source_hash_missing_is_blocker(self):
        q, r = fixture()
        clear(q, r, 0)
        del r["works"][0]["source_sha256"]
        p = mod.plan(q, r, [])
        self.assertIn("original_image_sha256_missing", p["checks"][0]["reasons"])


if __name__ == "__main__":
    unittest.main()
