"""V131 synthetic metadata tests; no archival-film pixels tested here."""
import json
import tempfile
import unittest
from pathlib import Path
from src.storia_rivive_v131_editorial_hold import evaluate, run

FILM = "e3022cb130442f7695d411724ae619fc8c184696ddae30293958c1c75ec8ffd9"
TIMES = [210.16, 232.36, 357.36, 452.88, 509.88]
NAMES = ["frame_21.png", "frame_23.png", "frame_34.png", "frame_42.png", "frame_48.png"]

def case():
    visual = {"version": "V128_BALANCED_REAL_ORIGINAL_FRAME_REVIEW_ONLY",
              "status": "V128_FIVE_BALANCED_FRAMES_VISUAL_REVIEW_REQUIRED",
              "source_film_sha256": FILM, "original_pts_sha_motion_evidence_crosschecked": True,
              "genuine_camera_shots_verified": False, "italian_rights_verified": False,
              "human_artistic_approved": False, "video_finished": False,
              "five_review_frames": [
                  {"filename": n, "source_pts_time_s": t, "frame_sha256": f"{i+1:064x}",
                   "source_film_sha256": FILM} for i, (n, t) in enumerate(zip(NAMES, TIMES))]}
    motion = {"version": "V129_REAL_PREFREEZE_MOTION_STRIPS_UNAPPROVED",
              "status": "V129_FIVE_SOURCE_LOCKED_MOTION_STRIPS_REVIEW_ONLY",
              "original_film_sha256": FILM, "proxy_sampling_is_not_exact_freeze_pts": True,
              "five_genuine_camera_shots_verified": False, "italian_rights_verified": False,
              "human_artistic_approved": False, "video_finished": False,
              "five_prefreeze_proxy_strips": [
                  {"source_frame": n, "freeze_source_pts_time_s": t,
                   "pre_freeze_start_pts": round(t*100)-100,
                   "freeze_pts": round(t*100), "source_time_base": "1/100",
                   "proxy_decoded_frame_count": 5,
                   "proxy_rgb_sha256": f"{i+10:064x}"} for i, (n, t) in enumerate(zip(NAMES, TIMES))]}
    registry = {"version": "V131_REVIEWED_SOURCE_VETOES", "source_vetoes": [
        {"film_sha256": FILM, "frame": "frame_34.png", "freeze_s": 357.36,
         "reason": "Extensive blown highlights; authentic detail cannot be recovered reliably."},
        {"film_sha256": FILM, "frame": "frame_48.png", "freeze_s": 509.88,
         "reason": "People are too small for faithful modern facial reconstruction."}]}
    return visual, motion, registry

class V131Tests(unittest.TestCase):
    def test_cotton_source_is_held_without_permission(self):
        result = evaluate(*case())
        self.assertEqual(result["status"], "SOURCE_ARTISTIC_REVIEW_HOLD")
        self.assertEqual([r["frame"] for r in result["source_review_vetoes"]], ["frame_34.png", "frame_48.png"])
        for key in ("i2i_permitted", "vidu_permitted", "paid_api_call_permitted", "publish_permitted"):
            self.assertFalse(result[key])

    def test_unknown_film_needs_review_not_approval(self):
        visual, motion, registry = case()
        other = "b" * 64
        visual["source_film_sha256"] = other
        motion["original_film_sha256"] = other
        for row in visual["five_review_frames"]:
            row["source_film_sha256"] = other
        result = evaluate(visual, motion, registry)
        self.assertEqual(result["status"], "SOURCE_ARTISTIC_REVIEW_REQUIRED")
        self.assertFalse(result["i2i_permitted"])

    def test_wrong_film_or_proxy_sha_fails(self):
        visual, motion, registry = case()
        motion["original_film_sha256"] = "c" * 64
        with self.assertRaisesRegex(ValueError, "FILM_OR_REVIEW_STATUS_INVALID"):
            evaluate(visual, motion, registry)
        motion["original_film_sha256"] = FILM
        motion["five_prefreeze_proxy_strips"][1]["proxy_rgb_sha256"] = "not-sha"
        with self.assertRaisesRegex(ValueError, "SHA_PTS_MISMATCH"):
            evaluate(visual, motion, registry)

    def test_stale_veto_cannot_be_silently_ignored(self):
        visual, motion, registry = case()
        registry["source_vetoes"][0]["freeze_s"] = 357.7
        with self.assertRaisesRegex(ValueError, "STALE_OR_MALFORMED_VETO"):
            evaluate(visual, motion, registry)

    def test_forged_approval_and_missing_frame_fail(self):
        visual, motion, registry = case()
        visual["human_artistic_approved"] = True
        with self.assertRaisesRegex(ValueError, "NOT_SOURCE_LOCKED"):
            evaluate(visual, motion, registry)
        visual["human_artistic_approved"] = False
        motion["five_prefreeze_proxy_strips"].pop()
        with self.assertRaisesRegex(ValueError, "FIVE_SOURCE_WINDOWS_REQUIRED"):
            evaluate(visual, motion, registry)

    def test_native_freeze_pts_and_proxy_frame_count_must_match(self):
        visual, motion, registry = case()
        motion["five_prefreeze_proxy_strips"][0]["freeze_pts"] += 1
        with self.assertRaisesRegex(ValueError, "SHA_PTS_MISMATCH"):
            evaluate(visual, motion, registry)
        motion["five_prefreeze_proxy_strips"][0]["freeze_pts"] -= 1
        motion["five_prefreeze_proxy_strips"][0]["proxy_decoded_frame_count"] = 2
        with self.assertRaisesRegex(ValueError, "SHA_PTS_MISMATCH"):
            evaluate(visual, motion, registry)
        motion["five_prefreeze_proxy_strips"][0]["proxy_decoded_frame_count"] = 5
        motion["five_prefreeze_proxy_strips"][0]["pre_freeze_start_pts"] = 0
        with self.assertRaisesRegex(ValueError, "SHA_PTS_MISMATCH"):
            evaluate(visual, motion, registry)

    def test_nonfinite_timestamps_cannot_bypass_veto(self):
        visual, motion, registry = case()
        registry["source_vetoes"][0]["freeze_s"] = float("nan")
        with self.assertRaisesRegex(ValueError, "STALE_OR_MALFORMED_VETO"):
            evaluate(visual, motion, registry)
        registry["source_vetoes"][0]["freeze_s"] = 357.36
        visual["five_review_frames"][0]["source_pts_time_s"] = float("nan")
        motion["five_prefreeze_proxy_strips"][0]["freeze_source_pts_time_s"] = float("nan")
        with self.assertRaisesRegex(ValueError, "SHA_PTS_MISMATCH"):
            evaluate(visual, motion, registry)
        visual["five_review_frames"][0]["source_pts_time_s"] = 10**1000
        motion["five_prefreeze_proxy_strips"][0]["freeze_source_pts_time_s"] = 10**1000
        with self.assertRaisesRegex(ValueError, "SHA_PTS_MISMATCH"):
            evaluate(visual, motion, registry)

    def test_invalid_input_replaces_prior_report_with_blocked_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = [root / n for n in ("visual.json", "motion.json", "vetoes.json")]
            for path, data in zip(paths, case()):
                path.write_text(json.dumps(data), encoding="utf-8")
            output = root / "result.json"
            self.assertEqual(run(*paths, output)["status"], "SOURCE_ARTISTIC_REVIEW_HOLD")
            paths[1].write_text("{}", encoding="utf-8")
            self.assertEqual(run(*paths, output)["status"], "SOURCE_AUDIT_INVALID")
            self.assertFalse(json.loads(output.read_text())["paid_api_call_permitted"])

if __name__ == "__main__":
    unittest.main()
