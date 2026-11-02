#!/usr/bin/env python3
"""V205 regression: real PNG bytes, no provider calls and no fake shot approval."""
import hashlib
import importlib.util
import random
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageEnhance

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("v205", ROOT / "src/storia_rivive_v205_visual_novelty.py")
v205 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v205)


def pixel_sha(path):
    with Image.open(path) as image:
        return hashlib.sha256(image.convert("RGB").tobytes()).hexdigest()


class VisualNoveltyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.cache = Path(self.temp.name)
        folder = self.cache / "original_frames"
        folder.mkdir()
        jobs = []
        for n in range(1, 6):
            rng = random.Random(1200 + n)
            path = folder / f"frame_{n:02d}.png"
            Image.frombytes("RGB", (256, 144), rng.randbytes(256 * 144 * 3)).save(path)
            jobs.append({"source_file": str(path), "source_sha256": v205.digest(path),
                         "source_pixel_sha256": pixel_sha(path)})
        self.manifest = {"source_video_sha256": "a" * 64, "original_frame_jobs": jobs}
        self.provenance = {
            "status": v205.READY_V204, "source_film_sha256": "a" * 64,
            "selected_frame_names": [Path(j["source_file"]).name for j in jobs],
            "selected_frame_pixel_sha256": [j["source_pixel_sha256"] for j in jobs],
        }

    def check(self):
        return v205.inspect(self.manifest, self.provenance, self.cache)

    def refresh(self, n, refresh_v204=True):
        job = self.manifest["original_frame_jobs"][n]
        path = Path(job["source_file"])
        job["source_sha256"] = v205.digest(path)
        job["source_pixel_sha256"] = pixel_sha(path)
        if refresh_v204:
            self.provenance["selected_frame_pixel_sha256"][n] = job["source_pixel_sha256"]

    def test_five_visually_different_frames_are_still_not_approved_shots(self):
        result = self.check()
        self.assertEqual(result["status"], v205.READY_V205)
        self.assertEqual(result["checked_pairs"], 10)
        self.assertFalse(result["five_distinct_shots_approved"])
        self.assertFalse(result["provider_calls_permitted"])
        self.assertFalse(result["publish_permitted"])

    def test_duplicate_visible_frame_is_blocked_even_with_matching_hashes(self):
        a, b = [Path(j["source_file"]) for j in self.manifest["original_frame_jobs"][:2]]
        b.write_bytes(a.read_bytes())
        self.refresh(1)
        self.assertEqual(self.check()["reason"], "NEAR_DUPLICATE_VISIBLE_PORTRAIT_FRAMES")

    def test_only_outside_portrait_crop_changes_are_not_new_shots(self):
        a, b = [Path(j["source_file"]) for j in self.manifest["original_frame_jobs"][:2]]
        with Image.open(a) as src, Image.open(b) as dst:
            x = (src.width - src.height * 9 // 16) // 2
            w = src.height * 9 // 16
            dst = dst.copy()
            dst.paste(src.crop((x, 0, x + w, src.height)), (x, 0))
            dst.save(b)
        self.refresh(1)
        self.assertEqual(self.check()["reason"], "NEAR_DUPLICATE_VISIBLE_PORTRAIT_FRAMES")

    def test_brightness_only_change_is_not_new_camera_shot(self):
        a, b = [Path(j["source_file"]) for j in self.manifest["original_frame_jobs"][:2]]
        with Image.open(a) as image:
            ImageEnhance.Brightness(image).enhance(1.08).save(b)
        self.refresh(1)
        self.assertEqual(self.check()["reason"], "NEAR_DUPLICATE_VISIBLE_PORTRAIT_FRAMES")

    def test_modified_after_v204_is_blocked(self):
        path = Path(self.manifest["original_frame_jobs"][0]["source_file"])
        Image.new("RGB", (256, 144), "black").save(path)
        self.assertEqual(self.check()["reason"], "SOURCE_BYTES_CHANGED_AFTER_V204")

    def test_updated_manifest_without_v204_frame_binding_is_blocked(self):
        path = Path(self.manifest["original_frame_jobs"][0]["source_file"])
        Image.new("RGB", (256, 144), "black").save(path)
        self.refresh(0, refresh_v204=False)
        self.assertEqual(self.check()["reason"], "V204_FRAME_BINDING_MISMATCH")

    def test_missing_v204_binding_is_blocked(self):
        del self.provenance["selected_frame_names"]
        self.assertEqual(self.check()["reason"], "V204_FRAME_BINDING_MISSING")

    def test_fake_v204_success_is_blocked(self):
        self.provenance["status"] = "FILM_FRAME_PROVENANCE_BLOCKED"
        self.assertEqual(self.check()["reason"], "V204_PROVENANCE_NOT_VERIFIED")

    def test_symlink_source_is_blocked(self):
        path = Path(self.manifest["original_frame_jobs"][0]["source_file"])
        path.unlink()
        path.symlink_to(Path(self.manifest["original_frame_jobs"][1]["source_file"]))
        self.assertEqual(self.check()["reason"], "SOURCE_OUTSIDE_VERIFIED_CACHE")


if __name__ == "__main__":
    unittest.main()
