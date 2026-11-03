"""V215 bounded real-frame scouting contract. No network/provider calls in tests."""
from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "src" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


scout = load("storia_rivive_scout_v101")
v210 = load("storia_rivive_v210_shot_aware_selection")
v204 = load("storia_rivive_v204_film_frame_provenance")


def make_frames(folder):
    folder.mkdir(parents=True, exist_ok=True)
    for index in range(1, 13):
        image = Image.new("RGB", (1280, 720), (25 + index * 9, 24, 26))
        draw = ImageDraw.Draw(image)
        draw.rectangle((320 + index * 8, 80, 450 + index * 8, 520),
                       fill=(80 + index * 9, 120, 190))
        draw.ellipse((530, index * 18, 700, index * 18 + 170),
                     fill=(210, 30 + index * 7, 70))
        image.save(folder / f"frame_{index:02d}.png")


class V215BoundedScouting(unittest.TestCase):
    def test_long_source_scout_extracts_twelve_frames_within_first_420_seconds(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            fake_film = b"v215 fake bytes for isolated downloader test"
            def fake_run(command, **kwargs):
                if command[0] == "ffprobe":
                    return type("Completed", (), {"stdout": json.dumps({"format": {"duration": 900}})})()
                self.assertIn("fps=1/35.0", command)
                make_frames(folder / "original_frames")
                return type("Completed", (), {"stdout": ""})()
            meta = {"download_url": "https://upload.wikimedia.org/wikipedia/commons/a/test.webm",
                    "size_bytes": len(fake_film), "source_page": "https://commons.wikimedia.org/wiki/File:Test.webm"}
            with patch.object(scout, "metadata", return_value=meta), \
                 patch.object(scout, "urlopen", return_value=io.BytesIO(fake_film)), \
                 patch.object(scout.subprocess, "run", side_effect=fake_run):
                report = scout.inspect(meta["source_page"], folder)
            self.assertEqual(report["sampling_window_s"], 420)
            self.assertEqual(report["sampling_period_s"], 35)
            self.assertEqual(report["source_frames_extracted"], 12)
            self.assertTrue((folder / "ORIGINAL_FILM_CONTACT_SHEET.jpg").is_file())
            self.assertEqual(report["original_sha256"], hashlib.sha256(fake_film).hexdigest())

    def test_v210_uses_reported_period_and_stays_inside_cut_scan(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            make_frames(folder / "original_frames")
            film = folder / "ORIGINAL_ARCHIVE.webm"
            film.write_bytes(b"source test")
            scout_report = {"original_sha256": hashlib.sha256(film.read_bytes()).hexdigest(),
                            "duration_s": 900.0, "sampling_window_s": 420.0,
                            "sampling_period_s": 35.0, "source_frames_extracted": 12}
            ranking = {"status": v210.READY, "all_candidates": [
                {"filename": f"frame_{i:02d}.png", "raster_px": [1280, 720],
                 "native_portrait_crop_px": [405, 720],
                 "source_visual_quality_score": 0.8}
                for i in range(1, 13)]}
            called = []
            def cuts(film, seconds):
                called.append(seconds)
                return [20 + 35 * i for i in range(11)]
            result = v210.select(ranking, scout_report, folder, detector=cuts)
            self.assertEqual(called, [420.0])
            self.assertEqual(result["status"], v210.READY, result)
            self.assertEqual(result["unscanned_late_frames"], 0)
            self.assertTrue(all(t < 420 for t in result["candidate_segment_times_s"]))
            self.assertFalse(result["provider_calls_permitted"])

    def test_v204_regenerates_using_same_period_not_whole_reel_period(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            make_frames(folder / "original_frames")
            film = folder / "ORIGINAL_ARCHIVE.webm"
            film.write_bytes(b"source test")
            jobs = []
            for i in (2, 4, 6, 8, 10):
                path = folder / "original_frames" / f"frame_{i:02d}.png"
                jobs.append({"source_file": str(path),
                             "source_sha256": v204.sha_file(path),
                             "source_pixel_sha256": v204.sha_pixels(path)})
            film_sha = v204.sha_file(film)
            manifest = {"version": "V102_SOURCE_LOCKED_I2I_JOBS",
                        "source_video_sha256": film_sha, "original_frame_jobs": jobs}
            report = {"status": "REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW",
                      "original_sha256": film_sha, "duration_s": 900.0,
                      "sampling_period_s": 35.0, "source_frames_extracted": 12}
            original_run = v204.subprocess.run
            def fake_run(command, **kwargs):
                self.assertIn("fps=1/35.0", command)
                target = Path(command[-1]).parent
                make_frames(target)
                return type("Completed", (), {})()
            with patch.object(v204.subprocess, "run", side_effect=fake_run):
                result = v204.inspect(manifest, report, folder)
            self.assertEqual(result["status"], "FIVE_FRAMES_REEXTRACTED_FROM_FILM_REVIEW_PENDING", result)
            self.assertEqual(result["fps_filter"], "fps=1/35.0")

    def test_v216_real_source_rejected_after_actual_contact_sheet_review(self):
        auto = load("storia_rivive_autopilot_v101")
        history = json.loads((ROOT / "queue" / "storia_rivive_episode_history_v200.json").read_text())
        bank = json.loads((ROOT / "queue" / "storia_rivive_candidates_v58.json").read_text())
        candidate = next(x for x in bank["candidates"]
                         if x["id"] == "france_cotton_mill_1920")
        self.assertFalse(candidate["rights_italy_verified"])
        self.assertEqual(candidate["license"], "PUBLIC_DOMAIN")
        self.assertIn(candidate["id"], auto.history_exclusions(history))
        self.assertEqual(next(x["status"] for x in history["entries"]
                              if x["episode_id"] == candidate["id"]), "source_rejected")

    def test_invalid_sampling_period_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            make_frames(folder / "original_frames")
            film = folder / "ORIGINAL_ARCHIVE.webm"
            film.write_bytes(b"source test")
            report = {"original_sha256": hashlib.sha256(film.read_bytes()).hexdigest(),
                      "duration_s": 900.0, "sampling_period_s": 500.0,
                      "source_frames_extracted": 12}
            ranking = {"status": v210.READY, "all_candidates": []}
            result = v210.select(ranking, report, folder, detector=lambda *_: [])
            self.assertEqual(result["reason"], "INVALID_FRAME_COUNT")
            ranking["all_candidates"] = [{"filename": f"frame_{i:02d}.png"} for i in range(1, 13)]
            result = v210.select(ranking, report, folder, detector=lambda *_: [])
            self.assertEqual(result["reason"], "SCOUT_SAMPLING_PERIOD_OUT_OF_BOUNDS")


if __name__ == "__main__":
    unittest.main()
