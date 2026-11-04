"""V185 offline regression on real synthetic MP4 bytes, not historical film."""
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SRC = Path(__file__).resolve().parents[1] / "src" / "storia_rivive_v185_storyboard_scout.py"
sys.path.insert(0, str(SRC.parent))
spec = importlib.util.spec_from_file_location("v185", SRC)
v185 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v185)


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args],
                   check=True, timeout=120)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class V185StoryboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)
        clips = []
        for i, color in enumerate(["red", "blue", "yellow", "green", "magenta", "cyan"]):
            dest = cls.root / f"scene_{i}.mp4"
            ffmpeg("-f", "lavfi", "-i", f"color=c={color}:s=1280x720:r=2",
                   "-t", "6", "-c:v", "libx264", "-preset", "ultrafast",
                   "-pix_fmt", "yuv420p", str(dest))
            clips.append(dest)
        concat = cls.root / "list.txt"
        concat.write_text("".join(f"file '{c}'\n" for c in clips))
        cls.film = cls.root / "six_synthetic_scenes.mp4"
        ffmpeg("-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", str(cls.film))
        cls.hash = sha(cls.film)
        cls.one_shot = cls.root / "one_shot.mp4"
        ffmpeg("-f", "lavfi", "-i", "color=c=blue:s=1280x720:r=1",
               "-t", "31", "-c:v", "libx264", "-preset", "ultrafast", str(cls.one_shot))
        cls.sd = cls.root / "sd.mp4"
        ffmpeg("-f", "lavfi", "-i", "color=c=red:s=480x360:r=1",
               "-t", "31", "-c:v", "libx264", "-preset", "ultrafast", str(cls.sd))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name) / "storyboard"

    def test_real_six_scene_mp4_produces_five_native_pngs_not_approval(self):
        r = v185.scout_local(self.film, self.hash, self.output)
        self.assertEqual(r["status"], "FIVE_CANDIDATES_NEED_VISUAL_REVIEW")
        self.assertEqual(len(r["candidates"]), 5)
        self.assertEqual(len({x["png_sha256"] for x in r["candidates"]}), 5)
        self.assertEqual(r["source_sha256"], self.hash)
        self.assertFalse(r["five_distinct_shots_verified"])
        self.assertFalse(r["freeze_pts_verified"])
        self.assertFalse(r["rights_italy_verified"])
        self.assertFalse(r["provider_jobs_may_start"])
        self.assertFalse(r["publish_permitted"])
        for c in r["candidates"]:
            path = self.output / c["png_filename"]
            self.assertEqual(sha(path), c["png_sha256"])
        self.assertTrue((self.output / "V185_STORYBOARD.json").exists())

    def test_single_shot_never_fabricates_five_scenes(self):
        r = v185.scout_local(self.one_shot, sha(self.one_shot), self.output)
        self.assertEqual(r["status"], "SCOUT_BLOCKED")
        self.assertIn("FEWER_THAN_FIVE_SCENE_CANDIDATES", r["blocking_issues"])
        self.assertFalse(self.output.exists())

    def test_sd_rejected_before_scene_detection(self):
        with patch.object(v185, "detect_scene_cuts") as detect:
            r = v185.scout_local(self.sd, sha(self.sd), self.output)
        self.assertEqual(r["status"], "SCOUT_BLOCKED")
        self.assertIn("V184_SOURCE_INTAKE_NOT_READY", r["blocking_issues"])
        detect.assert_not_called()

    def test_sha_mismatch_rejected_before_scene_detection(self):
        with patch.object(v185, "detect_scene_cuts") as detect:
            r = v185.scout_local(self.film, "0" * 64, self.output)
        self.assertEqual(r["status"], "SCOUT_BLOCKED")
        detect.assert_not_called()

    def test_missing_sha_rejected(self):
        r = v185.scout_local(self.film, None, self.output)
        self.assertIn("VALID_SOURCE_SHA256_REQUIRED", r["blocking_issues"])

    def test_existing_output_dir_not_overwritten(self):
        self.output.mkdir()
        sentinel = self.output / "sentinel.txt"
        sentinel.write_text("KEEP")
        with patch.object(v185, "detect_scene_cuts", return_value=[3, 7, 11, 15, 20]):
            r = v185.scout_local(self.film, self.hash, self.output)
        self.assertIn("OUTPUT_DIR_ALREADY_EXISTS", r["blocking_issues"])
        self.assertEqual(sentinel.read_text(), "KEEP")

    def test_ancestor_symlink_rejected(self):
        parent = Path(self.temp.name) / "link"
        parent.symlink_to(self.root, target_is_directory=True)
        r = v185.scout_local(parent / self.film.name, self.hash, self.output)
        self.assertIn("SYMLINK_SOURCE_REJECTED", r["blocking_issues"])

    def test_detector_error_fail_closed(self):
        with patch.object(v185, "detect_scene_cuts",
                          side_effect=subprocess.TimeoutExpired("ffmpeg", 1)):
            r = v185.scout_local(self.film, self.hash, self.output)
        self.assertIn("SCENE_DETECTION_FAILED", r["blocking_issues"])
        self.assertFalse(r["provider_jobs_may_start"])


if __name__ == "__main__":
    unittest.main()
