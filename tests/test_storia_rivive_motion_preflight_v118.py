"""V118: zero-credit tests of V102 -> decoded-motion preflight."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from PIL import Image

from src.storia_rivive_motion_preflight_v118 import plan_windows, run, verify_five_source_pngs

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
    def invoke(self, inspector, mutate=None):
        manifest, scout = fixture()
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            a, b, c = d/"manifest.json", d/"scout.json", d/"motion.json"
            # V119: real PNG bytes and their independently recorded scout hashes.
            frames = d/"original_frames"
            frames.mkdir()
            scout["frame_provenance_version"] = "V112_SOURCE_PTS_FROM_FFMPEG_SHOWINFO"
            scout["frame_provenance_source_sha256"] = SHA
            scout["frame_provenance"] = []
            for i, job in enumerate(manifest["original_frame_jobs"]):
                path = frames / f"frame_{i:02d}.png"
                Image.new("RGB", (64, 64), (20*i, 40+i, 90)).save(path)
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                job.update(source_file=str(path), source_sha256=digest,
                           source_raster_px=[64, 64], extraction_index=i,
                           source_pts_logged_from_decode=True)
                scout["frame_provenance"].append({
                    "filename": path.name, "sha256": digest,
                    "source_pts": job["source_pts"],
                    "source_pts_time_s": job["source_pts_time_s"],
                    "source_time_base": job["source_time_base"],
                    "shot_candidate_segment_index": job["shot_candidate_segment_index"],
                    "extraction_index": i, "source_pts_logged_from_decode": True})
            if mutate is not None:
                mutate(d, manifest, scout)
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
        self.assertEqual(updated["source_png_integrity_gate"], "V119_FIVE_SOURCE_PNG_BYTES_VERIFIED")
        self.assertNotIn("final_approved", updated)


    def test_cached_png_modified_after_v102_is_rejected(self):
        def corrupt(d, manifest, scout):
            (d/"original_frames"/"frame_00.png").write_bytes(b"tampered")
        result, updated = self.invoke(lambda *args: self.fail("motion must not run"), mutate=corrupt)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("SOURCE_PNG_SHA_MISMATCH", result["reason"])
        self.assertEqual(updated["original_frame_jobs"], [])

    def test_scout_png_digest_forged_is_rejected(self):
        def corrupt(d, manifest, scout):
            scout["frame_provenance"][1]["sha256"] = "0"*64
        result, updated = self.invoke(lambda *args: self.fail("motion must not run"), mutate=corrupt)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("SOURCE_PNG_SHA_MISMATCH", result["reason"])
        self.assertEqual(updated["photos_requested"], 0)

    def test_source_png_path_escape_is_rejected(self):
        def corrupt(d, manifest, scout):
            manifest["original_frame_jobs"][2]["source_file"] = str(d/"outside.png")
        result, updated = self.invoke(lambda *args: self.fail("motion must not run"), mutate=corrupt)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("SOURCE_PNG_PATH_INVALID_OR_MISSING", result["reason"])
        self.assertEqual(updated["original_frame_jobs"], [])

    def test_png_pts_mismatch_with_scout_is_rejected(self):
        def corrupt(d, manifest, scout):
            scout["frame_provenance"][0]["source_pts"] += 1
        result, updated = self.invoke(lambda *args: self.fail("motion must not run"), mutate=corrupt)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("SOURCE_PNG_SCOUT_METADATA_MISMATCH", result["reason"])
        self.assertEqual(updated["original_frame_jobs"], [])

    def test_missing_png_provenance_is_rejected(self):
        def corrupt(d, manifest, scout):
            scout.pop("frame_provenance")
        result, updated = self.invoke(lambda *args: self.fail("motion must not run"), mutate=corrupt)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("SOURCE_PNG_PROVENANCE_MISSING", result["reason"])
        self.assertEqual(updated["original_frame_jobs"], [])



if __name__ == "__main__":
    unittest.main()
