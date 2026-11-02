#!/usr/bin/env python3
"""V204 regression on a REAL FFmpeg-decoded synthetic film, no provider calls."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "v204", ROOT / "src" / "storia_rivive_v204_film_frame_provenance.py"
)
v204 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v204)


class FilmFrameProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_tmp = tempfile.TemporaryDirectory()
        cls.base = Path(cls.base_tmp.name)
        cls.film = cls.base / "ORIGINAL_ARCHIVE.webm"
        subprocess.run([
            "ffmpeg", "-nostdin", "-y", "-v", "error",
            "-f", "lavfi", "-i", "testsrc2=size=720x720:rate=1:duration=6",
            "-c:v", "libvpx", "-deadline", "realtime", "-cpu-used", "8",
            "-b:v", "1M", "-an", str(cls.film),
        ], check=True, timeout=90)
        frames = cls.base / "original_frames"
        frames.mkdir()
        subprocess.run([
            "ffmpeg", "-nostdin", "-y", "-v", "error", "-i", str(cls.film),
            "-vf", "fps=1/1", "-frames:v", "12", str(frames / "frame_%02d.png"),
        ], check=True, timeout=90)
        cls.count = len(list(frames.glob("frame_*.png")))
        if cls.count != 6:
            raise AssertionError("Expected six actual decoded video frames, got " + str(cls.count))
        probe = subprocess.run([
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "json", str(cls.film),
        ], capture_output=True, text=True, check=True, timeout=20)
        cls.duration = float(json.loads(probe.stdout)["format"]["duration"])

    @classmethod
    def tearDownClass(cls):
        cls.base_tmp.cleanup()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.cache = Path(self.tmp.name) / "cache"
        shutil.copytree(self.base, self.cache)
        film_sha = v204.sha_file(self.cache / "ORIGINAL_ARCHIVE.webm")
        self.report = {
            "status": "REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW",
            "original_sha256": film_sha,
            "duration_s": self.duration,
            "source_frames_extracted": self.count,
        }
        self.manifest = {
            "version": "V102_SOURCE_LOCKED_I2I_JOBS",
            "source_video_sha256": film_sha,
            "original_frame_jobs": [],
        }
        for n in range(1, 6):
            path = self.cache / "original_frames" / f"frame_{n:02d}.png"
            self.manifest["original_frame_jobs"].append({
                "source_file": str(path),
                "source_sha256": v204.sha_file(path),
                "source_pixel_sha256": v204.sha_pixels(path),
            })

    def check(self):
        return v204.inspect(self.manifest, self.report, self.cache)

    def test_exact_five_frames_from_real_film(self):
        result = self.check()
        self.assertEqual(result["status"], "FIVE_FRAMES_REEXTRACTED_FROM_FILM_REVIEW_PENDING")
        self.assertEqual(result["verified_film_extracted_frames"], 5)
        self.assertFalse(result["provider_calls_permitted"])
        self.assertFalse(result["publish_permitted"])
        self.assertFalse(result["five_distinct_shots_approved"])
        self.assertEqual(result["selected_frame_names"], [f"frame_{n:02d}.png" for n in range(1, 6)])
        self.assertEqual(result["selected_frame_pixel_sha256"],
                         [job["source_pixel_sha256"] for job in self.manifest["original_frame_jobs"]])

    def test_png_replacement_with_matching_manifest_hash_still_blocked(self):
        path = self.cache / "original_frames/frame_03.png"
        Image.new("RGB", (720, 720), (80, 100, 120)).save(path)
        self.manifest["original_frame_jobs"][2]["source_sha256"] = v204.sha_file(path)
        self.manifest["original_frame_jobs"][2]["source_pixel_sha256"] = v204.sha_pixels(path)
        self.assertEqual(self.check()["reason"], "FRAME_NOT_FROM_SHA_LOCKED_FILM")

    def test_swapped_source_png_with_updated_hash_still_blocked(self):
        a = self.cache / "original_frames/frame_02.png"
        b = self.cache / "original_frames/frame_04.png"
        a.write_bytes(b.read_bytes())
        job = self.manifest["original_frame_jobs"][1]
        job["source_sha256"] = v204.sha_file(a)
        job["source_pixel_sha256"] = v204.sha_pixels(a)
        self.assertEqual(self.check()["reason"], "FRAME_NOT_FROM_SHA_LOCKED_FILM")

    def test_missing_scout_duration_is_not_approved(self):
        del self.report["duration_s"]
        self.assertEqual(self.check()["reason"], "INVALID_SCOUT_DURATION")

    def test_corrupt_source_film_fails_before_reextracting(self):
        (self.cache / "ORIGINAL_ARCHIVE.webm").write_bytes(b"corrupt")
        self.assertEqual(self.check()["reason"], "FILM_BYTES_SHA_MISMATCH")

    def test_reused_source_frame_fails(self):
        self.manifest["original_frame_jobs"][1] = dict(self.manifest["original_frame_jobs"][0])
        self.assertEqual(self.check()["reason"], "REUSED_SOURCE_FRAME")

    def test_inconsistent_scout_frame_count_fails(self):
        self.report["source_frames_extracted"] = 5
        self.assertEqual(self.check()["reason"], "SCOUT_REEXTRACTION_FRAME_COUNT_MISMATCH")


if __name__ == "__main__":
    unittest.main()
