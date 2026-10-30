"""V118: zero-credit tests of V102 -> decoded-motion preflight."""
import json
import tempfile
import unittest
from pathlib import Path

from src.storia_rivive_motion_preflight_v118 import plan_windows, run

SHA = "b" * 64


def fixture():
    cuts = [5.0, 10.0, 15.0, 20.0]
    times = [3.0, 8.0, 13.0, 18.0, 23.0]
    manifest = {"status": "I2I_INPUTS_PREPARED_NO_AI_GENERATION",
                "source_video_sha256": SHA,
                "photos_requested": 5,
                "original_frame_jobs": [
                    {"source_film_sha256": SHA, "source_pts": int(t * 1000),
                     "source_pts_time_s": t, "source_time_base": "1/1000",
                     "shot_candidate_segment_index": i}
                    for i, t in enumerate(times)]}
    scout = {"original_sha256": SHA, "shot_boundary_analysis": {
        "version": "V113_FFMPEG_SCENE_CANDIDATES",
        "source_sha256": SHA, "cut_candidate_times_s": cuts}}
    return manifest, scout


class TestWindows(unittest.TestCase):
    def test_five_windows_from_five_distinct_shots(self):
        manifest, scout = fixture()
        windows = plan_windows(manifest, scout)
        self.assertEqual(len(windows), 5)
        self.assertEqual(windows[0]["freeze_pts"], 3000)
        self.assertGreaterEqual(windows[1]["start_pts"], 5000)
        self.assertAlmostEqual((windows[1]["freeze_pts"] - windows[1]["start_pts"]) / 1000, 1.35, places=2)

    def test_legacy_manifest_without_native_pts_rejected(self):
        manifest, scout = fixture()
        del manifest["original_frame_jobs"][0]["source_pts"]
        with self.assertRaisesRegex(ValueError, "INVALID_OR_MISSING_NATIVE_PTS"):
            plan_windows(manifest, scout)

    def test_wrong_segment_rejected(self):
        manifest, scout = fixture()
        manifest["original_frame_jobs"][0]["shot_candidate_segment_index"] = 2
        with self.assertRaisesRegex(ValueError, "SELECTED_SHOT_SEGMENT_MISMATCH"):
            plan_windows(manifest, scout)

    def test_clock_falsification_rejected(self):
        manifest, scout = fixture()
        manifest["original_frame_jobs"][2]["source_pts_time_s"] = 12.0
        with self.assertRaisesRegex(ValueError, "PTS_CLOCK_MISMATCH"):
            plan_windows(manifest, scout)

    def test_sha_falsification_rejected(self):
        manifest, scout = fixture()
        scout["original_sha256"] = "a"*64
        with self.assertRaisesRegex(ValueError, "SCOUT_FILM_SHA_MISMATCH"):
            plan_windows(manifest, scout)

    def test_cut_too_close_means_short_window_not_approved(self):
        manifest, scout = fixture()
        manifest["original_frame_jobs"][1].update(source_pts=5100, source_pts_time_s=5.1)
        with self.assertRaisesRegex(ValueError, "PRE_FREEZE_WINDOW_TOO_SHORT"):
            plan_windows(manifest, scout)


class TestPersistence(unittest.TestCase):
    def invoke(self, inspector):
        manifest, scout = fixture()
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            a, b, c = d/"manifest.json", d/"scout.json", d/"motion.json"
            a.write_text(json.dumps(manifest), encoding="utf-8")
            b.write_text(json.dumps(scout), encoding="utf-8")
            result = run(a, b, d/"film.webm", c, inspector=inspector)
            self.assertTrue(c.is_file())
            return result, json.loads(a.read_text(encoding="utf-8"))

    def test_missing_scout_blocks_requests(self):
        manifest, _ = fixture()
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            a, c = d/"manifest.json", d/"motion.json"
            a.write_text(json.dumps(manifest), encoding="utf-8")
            result = run(a, d/"missing_scout.json", d/"film.webm", c)
            self.assertEqual(result["status"], "BLOCKED")
            self.assertEqual(json.loads(a.read_text())["original_frame_jobs"], [])

    def test_rejection_disables_source_requests(self):
        result, updated = self.invoke(lambda *args: {"status": "BLOCKED", "reason": "STATIC"})
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(updated["original_frame_jobs"], [])
        self.assertEqual(updated["photos_requested"], 0)
        self.assertEqual(updated["status"], "I2I_INPUTS_BLOCKED")

    def test_pass_keeps_five_jobs_but_not_artistic_approval(self):
        result, updated = self.invoke(lambda *args: {
            "status": "FIVE_MOTION_WINDOWS_EVIDENCED_REVIEW_REQUIRED"})
        self.assertEqual(result["status"], "MOTION_EVIDENCE_PASS_REVIEW_PENDING")
        self.assertEqual(len(updated["original_frame_jobs"]), 5)
        self.assertEqual(updated["source_bw_motion_gate"], "V118_FIVE_DECODED_WINDOWS_PASS_REVIEW_REQUIRED")
        self.assertNotIn("final_approved", updated)


if __name__ == "__main__":
    unittest.main()
