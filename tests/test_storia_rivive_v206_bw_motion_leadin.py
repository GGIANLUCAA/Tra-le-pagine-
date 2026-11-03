#!/usr/bin/env python3
"""V206/V207 tests: real motion, portrait-only motion, static cuts, flicker."""
import hashlib
import importlib.util
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageEnhance, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "v206", ROOT / "src/storia_rivive_v206_bw_motion_leadin.py")
v206 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v206)


@unittest.skipUnless(shutil.which("ffmpeg"), "FFmpeg required for real media tests")
class MotionLeadInTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.cache = Path(self.tmp.name)
        self.film = self.cache / "ORIGINAL_ARCHIVE.webm"
        self.frames = self.cache / "original_frames"
        self.frames.mkdir()
        self.duration = 16.0

    def build(self, moving=True):
        source = ("testsrc2=size=320x180:rate=12:duration=16" if moving else
                  "color=c=gray:size=320x180:rate=12:duration=16")
        subprocess.run(["ffmpeg", "-nostdin", "-y", "-v", "error", "-f", "lavfi",
                        "-i", source, "-c:v", "libvpx-vp9", "-b:v", "400k",
                        str(self.film)], check=True, timeout=50)
        period = self.duration / 12
        subprocess.run(["ffmpeg", "-nostdin", "-y", "-v", "error", "-i",
                        str(self.film), "-vf", "fps=1/" + str(round(period, 4)),
                        "-frames:v", "12", str(self.frames / "frame_%02d.png")],
                       check=True, timeout=40)
        sha = v206.sha256(self.film)
        names = [f"frame_{i:02d}.png" for i in range(2, 7)]
        manifest = {"source_video_sha256": sha,
                    "original_frame_jobs": [{"source_file": str(self.frames / name)}
                                            for name in names]}
        provenance = {"status": v206.READY_V204, "source_film_sha256": sha,
                      "fps_filter": "fps=1/" + str(round(period, 4)),
                      "selected_frame_names": names}
        novelty = {"status": v206.READY_V205}
        scout = {"original_sha256": sha, "duration_s": self.duration}
        return manifest, provenance, novelty, scout

    def test_real_moving_video_passes_only_as_research(self):
        result = v206.inspect(*self.build(moving=True), self.cache)
        self.assertEqual(result["status"], v206.READY_V206, result)
        self.assertEqual(len(result["motion_evidence"]), 5)
        self.assertTrue(all(x["moving"] for x in result["motion_evidence"]))
        self.assertFalse(result["five_distinct_shots_approved"])
        self.assertFalse(result["provider_calls_permitted"])
        self.assertFalse(result["publish_permitted"])

    def test_static_film_cannot_masquerade_as_moving_bw(self):
        result = v206.inspect(*self.build(moving=False), self.cache)
        self.assertEqual(result["reason"], "STATIC_OR_FLICKER_ONLY_BW_LEADIN")

    def test_first_archival_frame_has_no_preceding_film(self):
        manifest, provenance, novelty, scout = self.build()
        manifest["original_frame_jobs"][0]["source_file"] = str(self.frames / "frame_01.png")
        provenance["selected_frame_names"][0] = "frame_01.png"
        result = v206.inspect(manifest, provenance, novelty, scout, self.cache)
        self.assertEqual(result["reason"], "NO_PRECEDING_BW_MOTION_WINDOW")

    def test_tampered_film_blocks_before_motion_sampling(self):
        manifest, provenance, novelty, scout = self.build()
        with self.film.open("ab") as f:
            f.write(b"tampered")
        result = v206.inspect(manifest, provenance, novelty, scout, self.cache)
        self.assertEqual(result["reason"], "FILM_BYTES_CHANGED_AFTER_V204")

    def test_false_prior_gate_cannot_pass(self):
        manifest, provenance, novelty, scout = self.build()
        novelty["status"] = "VISUAL_NOVELTY_BLOCKED"
        result = v206.inspect(manifest, provenance, novelty, scout, self.cache)
        self.assertEqual(result["reason"], "PREVIOUS_SOURCE_GATES_NOT_VERIFIED")


class ExposureOnlyTests(unittest.TestCase):
    def test_global_brightness_is_not_movement(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp) / "a.png", Path(tmp) / "b.png"
            im = Image.new("L", (96, 96))
            im.putdata([(x * 2 + y) % 220 + 10 for y in range(96) for x in range(96)])
            im.save(a)
            ImageEnhance.Brightness(im).enhance(1.05).save(b)
            self.assertFalse(v206.metric(a, b)["moving"])

    def test_static_identical_frames_are_not_movement(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.png"
            Image.new("RGB", (96, 96), (120, 120, 120)).save(a)
            self.assertFalse(v206.metric(a, a)["moving"])

    def test_motion_only_in_landscape_edges_is_not_reel_motion(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp) / "a.png", Path(tmp) / "b.png"
            original = Image.new("RGB", (320, 180), (120, 120, 120))
            changed = original.copy()
            draw = ImageDraw.Draw(changed)
            # Only x<90 and x>230 change; the 9:16 center crop is x=109..210.
            for x in range(0, 90, 8):
                draw.rectangle((x, 0, x + 3, 179), fill=(20, 220, 20))
            for x in range(231, 320, 8):
                draw.rectangle((x, 0, x + 3, 179), fill=(230, 20, 20))
            original.save(a)
            changed.save(b)
            self.assertFalse(v206.metric(a, b)["moving"])

    def test_one_hard_cut_between_two_static_shots_is_not_sustained_motion(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = [Path(tmp) / f"frame_{i}.png" for i in range(4)]
            a = Image.new("RGB", (320, 180), (60, 60, 60))
            b = Image.new("RGB", (320, 180), (60, 60, 60))
            ImageDraw.Draw(a).rectangle((115, 10, 195, 150), fill=(230, 230, 230))
            ImageDraw.Draw(b).ellipse((115, 10, 195, 150), fill=(230, 230, 230))
            for p, im in zip(paths, [a, a, b, b]):
                im.save(p)
            result = v206.sequence_metric(paths)
            self.assertEqual(result["moving_intervals"], 1, result)
            self.assertFalse(result["moving"], result)
            self.assertTrue(result["visible_portrait_only"])

    def test_short_sample_cannot_fake_sustained_motion(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = [Path(tmp) / f"frame_{i}.png" for i in range(3)]
            for p in paths:
                Image.new("RGB", (320, 180), (120, 120, 120)).save(p)
            with self.assertRaises(ValueError):
                v206.sequence_metric(paths)


if __name__ == "__main__":
    unittest.main()
