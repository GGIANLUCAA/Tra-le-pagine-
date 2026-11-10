"""Fail-closed offline regression tests for the ArtVision owner selector."""
import importlib.util
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "scripts/artvision_owner_nonstop_preflight_v1.py"
spec = importlib.util.spec_from_file_location("owner_preflight", P)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def fixture():
    fast, registry = [], []
    for i in range(1, 31):
        ident = {"selection_order": i, "title_as_chosen": f"Painting {i}",
                 "artist_as_chosen": f"Artist {i}"}
        fast.append({**ident, "provisional_production_priority": i,
                     "production_ready": False,
                     "rights_and_source_gate": "pending_review",
                     "render_status": "not_started"})
        registry.append({**ident, **{gate: False for gate in mod.GATES}})
    return {"selected_works": fast}, {"works": registry}


def clear(q, s, index):
    q["selected_works"][index].update(
        production_ready=True, rights_and_source_gate="cleared")
    s["works"][index].update({gate: True for gate in mod.GATES})
    s["works"][index]["source_sha256"] = "a" * 64


def identity(q, index):
    w = q["selected_works"][index]
    return {"selection_order": w["selection_order"],
            "title": w["title_as_chosen"],
            "artist": w["artist_as_chosen"],
            "variant": "cinema_standard"}


class OwnerNonstopPreflight(unittest.TestCase):
    def test_all_pending_does_not_invent_production(self):
        q, s = fixture()
        p = mod.plan(q, s, [])
        self.assertEqual(p["status"], "no_source_cleared_work")
        self.assertEqual(p["blocked_count"], 30)
        self.assertFalse(p["auto_render"])
        self.assertFalse(p["auto_publish"])

    def test_ready_candidate_only_after_complete_evidence(self):
        q, s = fixture()
        clear(q, s, 3)
        p = mod.plan(q, s, [])
        self.assertEqual(p["first_preflight_candidate"]["selection_order"], 4)
        self.assertFalse(p["auto_render"])

    def test_historical_checkpoint_deduplicates(self):
        q, s = fixture()
        clear(q, s, 15)
        w = identity(q, 15)
        cp = {"secondary_work": {"selection_order": w["selection_order"],
              "selected_title": w["title"], "artist": w["artist"],
              "variant": w["variant"]},
              "mp4": {"sha256": "b" * 64}, "github_workflow_run_id": 123}
        p = mod.plan(q, s, [cp])
        self.assertIsNone(p["first_preflight_candidate"])
        row = next(r for r in p["checks"] if r["selection_order"] == 16)
        self.assertIn("existing_cinema_standard_verified_mp4_checkpoint",
                      row["reasons"])
        self.assertEqual(p["sha_documented_checkpoints"], 1)

    def test_new_verified_nested_checkpoint_deduplicates(self):
        q, s = fixture()
        clear(q, s, 11)
        cp = {"work": identity(q, 11),
              "github": {"run_id": 123},
              "qa": {"mp4_sha256": "b" * 64}}
        p = mod.plan(q, s, [cp])
        self.assertIsNone(p["first_preflight_candidate"])
        self.assertEqual(p["sha_documented_checkpoints"], 1)

    def test_two_in_progress_schema_variants_block_without_fake_pass(self):
        q, s = fixture()
        clear(q, s, 8)
        clear(q, s, 12)
        cole = {"secondary_work": identity(q, 8),
                "github_run_id": 42737588988,
                "qa": {"new_mp4_verified": False, "sha256_mp4": None}}
        duel = {"work": identity(q, 12), "run_id": 42782307048,
                "qa": {"new_verified_mp4": 0}}
        p = mod.plan(q, s, [cole, duel])
        self.assertEqual(p["runs_needing_checkpoint_reconciliation"], 2)
        self.assertEqual(p["sha_documented_checkpoints"], 0)
        self.assertIsNone(p["first_preflight_candidate"])
        self.assertEqual(p["existing_cinema_standard_checkpoints"], 2)

    def test_five_independent_checkpoint_slots(self):
        q, s = fixture()
        indices = (8, 11, 12, 15, 25)
        for i in indices:
            clear(q, s, i)
        cps = [{"work": identity(q, i), "run_id": 100 + i,
                "qa": {"mp4_sha256": "b" * 64}} for i in indices]
        p = mod.plan(q, s, cps)
        self.assertEqual(p["existing_cinema_standard_checkpoints"], 5)
        self.assertEqual(p["sha_documented_checkpoints"], 5)
        self.assertIsNone(p["first_preflight_candidate"])

    def test_unmatched_register_fails_closed(self):
        q, s = fixture()
        s["works"][0]["artist_as_chosen"] = "Wrong"
        with self.assertRaises(ValueError):
            mod.plan(q, s, [])

    def test_unmatched_checkpoint_fails_closed(self):
        q, s = fixture()
        cp = {"work": {**identity(q, 0), "artist": "Wrong"}, "run_id": 22}
        with self.assertRaises(ValueError):
            mod.plan(q, s, [cp])

    def test_no_source_hash_is_blocker(self):
        q, s = fixture()
        clear(q, s, 0)
        del s["works"][0]["source_sha256"]
        p = mod.plan(q, s, [])
        self.assertIn("original_image_sha256_missing", p["checks"][0]["reasons"])

    def test_duplicate_checkpoint_is_blocking_not_double_counted(self):
        q, s = fixture()
        cp = {"work": identity(q, 0), "run_id": 123}
        with self.assertRaises(ValueError):
            mod.plan(q, s, [cp, cp])


if __name__ == "__main__":
    unittest.main()
