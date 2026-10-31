"""V132 offline metadata regression; fixture mirrors eight real V125 motion rows.

The fixture is not a substitute for reviewing the original movie pixels.
"""
import json
import tempfile
import unittest
from pathlib import Path

from test_storia_rivive_v126 import fixture, FILM_SHA
from src.storia_rivive_v132_veto_aware_alternatives import evaluate, run


def registry():
    return {"version": "V131_REVIEWED_SOURCE_VETOES", "source_vetoes": [
        {"film_sha256": FILM_SHA, "frame": "frame_34.png", "freeze_s": 357.36,
         "reason": "Original film machinery overexposed; source detail is unrecoverable."},
        {"film_sha256": FILM_SHA, "frame": "frame_48.png", "freeze_s": 509.88,
         "reason": "Original film people too small for faithful facial reconstruction."},
    ]}


class V132Tests(unittest.TestCase):
    def test_real_eight_motion_rows_reject_after_two_visual_vetoes(self):
        result = evaluate(*fixture(), registry())
        self.assertEqual(result["status"], "SOURCE_REJECTED_V132_INSUFFICIENT_DIVERSITY_AFTER_VETO")
        self.assertEqual(result["original_verified_motion_candidates"], 8)
        self.assertEqual(result["editorial_veto_frames"], ["frame_34.png", "frame_48.png"])
        self.assertEqual(result["verified_motion_candidates_after_veto"], 6)
        self.assertEqual(result["timeline_regions_after_veto"], [2, 4])
        self.assertEqual(result["alternative_five_frame_names"], [])
        for key in ("i2i_permitted", "vidu_permitted", "paid_api_call_permitted",
                    "publish_permitted", "human_artistic_approved", "video_finished"):
            self.assertFalse(result[key])

    def test_unrelated_veto_never_grants_approval(self):
        r = registry()
        for row in r["source_vetoes"]:
            row["film_sha256"] = "f" * 64
        result = evaluate(*fixture(), r)
        self.assertEqual(result["status"], "SOURCE_ALTERNATIVE_FRAMES_REVIEW_REQUIRED")
        self.assertEqual(len(result["alternative_five_frame_names"]), 5)
        self.assertFalse(result["paid_api_call_permitted"])

    def test_stale_veto_pts_is_not_silently_skipped(self):
        r = registry()
        r["source_vetoes"][0]["freeze_s"] += 1
        with self.assertRaisesRegex(ValueError, "STALE_OR_UNVERIFIED"):
            evaluate(*fixture(), r)

    def test_duplicate_and_unknown_veto_are_invalid(self):
        r = registry()
        r["source_vetoes"].append(dict(r["source_vetoes"][0]))
        with self.assertRaisesRegex(ValueError, "STALE_OR_UNVERIFIED"):
            evaluate(*fixture(), r)
        r = registry()
        r["source_vetoes"][0]["frame"] = "frame_99.png"
        with self.assertRaisesRegex(ValueError, "STALE_OR_UNVERIFIED"):
            evaluate(*fixture(), r)

    def test_nonfinite_and_bad_sha_rejected(self):
        r = registry()
        r["source_vetoes"][0]["freeze_s"] = float("nan")
        with self.assertRaisesRegex(ValueError, "STALE_OR_UNVERIFIED"):
            evaluate(*fixture(), r)
        r = registry()
        r["source_vetoes"][0]["film_sha256"] = "unverified"
        with self.assertRaisesRegex(ValueError, "VETO_SOURCE_SHA_INVALID"):
            evaluate(*fixture(), r)

    def test_tampered_motion_source_is_blocked(self):
        motion, rank, scout = fixture()
        motion["motion_audit"][0]["source_pts"] = 0
        with self.assertRaisesRegex(ValueError, "MOTION_PTS_OR_SEGMENT_MISMATCH"):
            evaluate(motion, rank, scout, registry())

    def test_missing_real_motion_candidates_stays_rejected(self):
        motion, rank, scout = fixture()
        for row in motion["motion_audit"]:
            if row["filename"] == "frame_40.png":
                row["motion_verified"] = False
                row["status"] = "BLOCKED"
        result = evaluate(motion, rank, scout, registry())
        self.assertEqual(result["status"], "SOURCE_REJECTED_V132_INSUFFICIENT_DIVERSITY_AFTER_VETO")
        self.assertEqual(result["verified_motion_candidates_after_veto"], 5)

    def test_invalid_input_replaces_old_report_with_safe_state(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            paths = [root / name for name in ("motion.json", "rank.json", "scout.json", "veto.json")]
            for path, data in zip(paths, (*fixture(), registry())):
                path.write_text(json.dumps(data), encoding="utf-8")
            output = root / "result.json"
            self.assertEqual(run(*paths, output)["status"],
                             "SOURCE_REJECTED_V132_INSUFFICIENT_DIVERSITY_AFTER_VETO")
            paths[1].write_text("{}", encoding="utf-8")
            self.assertEqual(run(*paths, output)["status"], "SOURCE_AUDIT_INVALID")
            self.assertFalse(json.loads(output.read_text())["paid_api_call_permitted"])


if __name__ == "__main__":
    unittest.main()
