"""V326 regression: editorial suggestions, explicit timing, real MP4 black tail."""
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from src.director_reference_v326 import analyze_scenes, inspect_black_tail


class DirectorReferenceV326Tests(unittest.TestCase):
    def test_optional_timings_preserve_old_projects(self):
        blockers, warnings, data = analyze_scenes([
            {"artwork": "Painting", "framing": "detail", "move": "static"},
            {"artwork": "Painting", "framing": "full_artwork", "move": "pull_out"}])
        self.assertEqual(blockers, [])
        self.assertEqual(warnings, [])
        self.assertEqual(data["timed_shots"], 0)
        self.assertFalse(data["artistically_approved"])

    def test_flash_complex_details_endcard_and_monotony(self):
        shots = [
            {"artwork": "A", "framing": "detail", "move": "push_in",
             "duration": 1, "complex_detail": True},
            {"artwork": "B", "framing": "detail", "move": "static", "duration": 1},
            {"artwork": "C", "framing": "detail", "move": "static", "duration": 1},
            {"artwork": "D", "framing": "medium", "move": "static", "duration": 1},
            {"artwork": "E", "framing": "full_artwork", "move": "static",
             "duration": 1, "kind": "end_card"}]
        blocking, warnings, data = analyze_scenes(shots, short=True)
        codes = {w["code"] for w in warnings}
        self.assertEqual(blocking, [])
        self.assertTrue({"FLASH_SHOT", "COMPLEX_DETAIL_TOO_FAST",
                         "TOO_MANY_FLASHES", "MECHANICAL_CADENCE"}.issubset(codes))
        self.assertEqual(data["timed_shots"], 5)

    def test_intentional_holds_and_variation_do_not_fail(self):
        shots = [
            {"artwork": "A", "framing": "detail", "move": "static",
             "duration": .9, "rhythm_justification": "Strong single frame"},
            {"artwork": "A", "framing": "medium", "move": "pan_left", "duration": 3},
            {"artwork": "A", "framing": "detail", "move": "push_in", "duration": 4},
            {"artwork": "A", "framing": "full_artwork", "move": "static", "duration": 7,
             "rhythm_justification": "Painting reveals complete story"},
            {"artwork": "A", "framing": "portrait", "move": "pull_out", "duration": 2.7}]
        blocking, warnings, _ = analyze_scenes(shots, short=True)
        self.assertEqual(blocking, [])
        self.assertNotIn("MECHANICAL_CADENCE", {x["code"] for x in warnings})
        self.assertNotIn("LONG_STATIC_SHORT", {x["code"] for x in warnings})
        self.assertNotIn("FLASH_SHOT", {x["code"] for x in warnings})

    def test_invalid_timing_is_blocked_and_overlap_is_review_only(self):
        blocking, warnings, _ = analyze_scenes([
            {"start": 0, "end": 2},
            {"start": 1.8, "end": 4},
            {"duration": -1},
        ])
        self.assertIn("INVALID_TIMING", {x["code"] for x in blocking})
        self.assertIn("TIMELINE_OVERLAP", {x["code"] for x in warnings})

    def test_anchors_and_three_identical_shots(self):
        shots = [{"artwork": "A", "framing": "detail", "move": "push_in",
                  "spoken_anchor": "hand", "camera_reason": "auto_zoom"} for _ in range(3)]
        _, warnings, facts = analyze_scenes(shots)
        codes = {w["code"] for w in warnings}
        self.assertIn("SAME_SHOT_PATTERN", codes)
        self.assertIn("VISUAL_ANCHOR_MISSING", codes)
        self.assertIn("UNMOTIVATED_CAMERA", codes)
        self.assertFalse(facts["narration_alignment_verified"])

    @unittest.skipUnless(shutil.which("ffmpeg"), "ffmpeg missing")
    def test_detects_genuine_black_tail_not_bright_tail(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tail.mp4"
            cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                   "-f", "lavfi", "-i", "color=c=white:s=160x288:r=10:d=2",
                   "-f", "lavfi", "-i", "color=c=black:s=160x288:r=10:d=1.5",
                   "-filter_complex", "[0:v][1:v]concat=n=2:v=1:a=0[v]",
                   "-map", "[v]", "-c:v", "mpeg4", str(path)]
            subprocess.run(cmd, check=True, timeout=35)
            warnings, facts = inspect_black_tail(path, 3.5)
            self.assertIn("BLACK_TAIL", {w["code"] for w in warnings},
                          msg=str(facts))
            self.assertTrue(facts["black_end_warning"])

    def test_unavailable_video_is_not_pretended_reviewed(self):
        warnings, facts = inspect_black_tail("/missing.mp4", 4)
        self.assertIn("BLACK_TAIL_SCAN_UNAVAILABLE", {x["code"] for x in warnings})
        self.assertEqual(facts["black_tail_scan"], "unavailable")


if __name__ == "__main__":
    unittest.main()
