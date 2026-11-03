#!/usr/bin/env python3
"""V202 offline tests: no provider, network, spending or release."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("handoff", ROOT / "src" / "storia_rivive_v202_source_handoff.py")
handoff = importlib.util.module_from_spec(spec)
spec.loader.exec_module(handoff)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixture(root):
    cache = root / "cache"
    frames = cache / "original_frames"
    frames.mkdir(parents=True)
    film = cache / "ORIGINAL_ARCHIVE.webm"
    film.write_bytes(b"synthetic fixture, never a historical source")
    order = {
        "contract": "LA_STORIA_RIVIVE_V101_SAFE_AUTOPILOT",
        "cycle_id": "storia-20261102-0000", "episode_id": "synthetic_v202",
        "source_page": "https://commons.wikimedia.org/wiki/File:Example.webm",
        "paid_api_call_permitted": False, "publish_permitted": False,
    }
    report = {
        "status": handoff.READY, "source_page": order["source_page"],
        "original_sha256": sha(film), "source_frames_extracted": 5,
    }
    jobs = []
    for n in range(5):
        path = frames / ("frame_%02d.png" % (n + 1))
        Image.new("RGB", (1280, 720), (20 + n * 25, 30 + n, 80)).save(path)
        with Image.open(path) as image:
            pixels = hashlib.sha256(image.convert("RGB").tobytes()).hexdigest()
        photo = n < 4
        jobs.append({
            "source_file": str(path), "source_sha256": sha(path),
            "source_pixel_sha256": pixels, "source_raster_px": [1280, 720],
            "target_kind": "REAL_SOURCE_LOCKED_I2I_PHOTOGRAPH" if photo else "VIDU_SOURCE_ANCHOR_NO_I2I",
            "role": "STATIC_COLOR_REVEAL" if photo else "VIDU_SOURCE_ANCHOR_NOT_RENDERED",
            "prompt": "Restore exact frame faithfully" if photo else None,
            "provider": "NOT_SELECTED_NO_CALL" if photo else "NOT_APPLICABLE_NO_I2I",
            "request_sent": False, "result_file": None, "restored_photo_approved": False,
            "allow_source_reframing": False, "allow_invented_people": False,
        })
    fifth = jobs[4]
    manifest = {
        "version": "V102_SOURCE_LOCKED_I2I_JOBS",
        "cycle_id": order["cycle_id"], "episode_id": order["episode_id"],
        "source_video_sha256": sha(film), "source_frames_prepared": 5,
        "photos_requested": 4, "photo_jobs_prepared": 4,
        "photos_generated": 0, "photos_approved": 0, "provider_requests_sent": 0,
        "paid_api_calls": 0, "vidu_calls": 0, "publication_permitted": False,
        "original_frame_jobs": jobs,
        "vidu_source_anchor": {
            "source_file": fifth["source_file"], "source_sha256": fifth["source_sha256"],
            "source_pixel_sha256": fifth["source_pixel_sha256"],
            "approved": False, "vidu_request_sent": False,
        },
    }
    return manifest, order, report, cache


class SourceHandoffTests(unittest.TestCase):
    def run_case(self, mutate=None):
        with tempfile.TemporaryDirectory() as temp:
            m, o, r, cache = fixture(Path(temp))
            if mutate:
                mutate(m, o, r, cache)
            return handoff.inspect(m, o, r, cache)

    def test_valid_five_native_files_four_photo_one_vidu_only(self):
        result = self.run_case()
        self.assertEqual(result["status"], "SOURCE_HANDOFF_BYTES_VERIFIED_REVIEW_PENDING")
        self.assertEqual(result["verified_photo_source_frames"], 4)
        self.assertEqual(result["verified_vidu_source_anchors"], 1)
        self.assertFalse(result["provider_calls_permitted"])
        self.assertFalse(result["publish_permitted"])
        self.assertEqual(result["native_portrait_crop_px"], [405, 720])

    def test_reject_film_swapped_after_scout(self):
        self.assertEqual(self.run_case(lambda m, o, r, c:
            (c / "ORIGINAL_ARCHIVE.webm").write_bytes(b"tampered"))["reason"], "FILM_BYTES_SHA_MISMATCH")

    def test_reject_manifest_film_sha_swapped(self):
        self.assertEqual(self.run_case(lambda m, o, r, c:
            m.update(source_video_sha256="0" * 64))["reason"], "FILM_BYTES_SHA_MISMATCH")

    def test_reject_wrong_source_page(self):
        self.assertEqual(self.run_case(lambda m, o, r, c:
            r.update(source_page="https://commons.wikimedia.org/wiki/File:Wrong.webm"))["reason"],
            "SCOUT_REPORT_NOT_BOUND_TO_ORDER")

    def test_reject_sd_480p_even_with_updated_sha_and_metadata(self):
        def mutate(m, o, r, c):
            path = c / "original_frames/frame_01.png"
            Image.new("RGB", (854, 480), (20, 30, 80)).save(path)
            with Image.open(path) as image:
                pixel_sha = hashlib.sha256(image.convert("RGB").tobytes()).hexdigest()
            m["original_frame_jobs"][0].update(
                source_sha256=sha(path), source_pixel_sha256=pixel_sha,
                source_raster_px=[854, 480],
            )
        self.assertEqual(self.run_case(mutate)["reason"],
                         "SOURCE_NATIVE_PORTRAIT_CROP_TOO_SMALL")

    def test_reject_narrow_portrait_crop_despite_tall_source(self):
        def mutate(m, o, r, c):
            path = c / "original_frames/frame_01.png"
            Image.new("RGB", (360, 1080), (20, 30, 80)).save(path)
            with Image.open(path) as image:
                pixel_sha = hashlib.sha256(image.convert("RGB").tobytes()).hexdigest()
            m["original_frame_jobs"][0].update(
                source_sha256=sha(path), source_pixel_sha256=pixel_sha,
                source_raster_px=[360, 1080],
            )
        self.assertEqual(self.run_case(mutate)["reason"],
                         "SOURCE_NATIVE_PORTRAIT_CROP_TOO_SMALL")

    def test_reject_native_png_tampered(self):
        def mutate(m, o, r, c):
            Image.new("RGB", (1280, 720), (0, 0, 0)).save(c / "original_frames/frame_03.png")
        self.assertEqual(self.run_case(mutate)["reason"], "SOURCE_FRAME_BYTES_SHA_MISMATCH")

    def test_reject_external_png_even_with_matching_hash(self):
        def mutate(m, o, r, c):
            external = c.parent / "injected" / "frame_01.png"
            external.parent.mkdir()
            external.write_bytes((c / "original_frames/frame_01.png").read_bytes())
            m["original_frame_jobs"][0]["source_file"] = str(external)
        self.assertEqual(self.run_case(mutate)["reason"], "SOURCE_FRAME_OUTSIDE_VERIFIED_CACHE")

    def test_reject_fifth_scene_relabelled_as_photo(self):
        self.assertEqual(self.run_case(lambda m, o, r, c:
            m["original_frame_jobs"][4].update(target_kind="REAL_SOURCE_LOCKED_I2I_PHOTOGRAPH"))["reason"],
            "VIDU_ANCHOR_ROLE_INVALID")

    def test_reject_anchor_not_matching_fifth_frame(self):
        self.assertEqual(self.run_case(lambda m, o, r, c:
            m["vidu_source_anchor"].update(source_sha256="f" * 64))["reason"],
            "VIDU_ANCHOR_NOT_BOUND_TO_FIFTH_FRAME")

    def test_reject_forged_photo_approval(self):
        self.assertEqual(self.run_case(lambda m, o, r, c:
            m["original_frame_jobs"][1].update(restored_photo_approved=True))["reason"],
            "FORGED_PHOTO_APPROVAL")

    def test_reject_fake_generated_photos(self):
        self.assertEqual(self.run_case(lambda m, o, r, c:
            m.update(photos_generated=4))["reason"], "UNVERIFIED_GENERATION_OR_PERMISSION_CLAIM")

    def test_reject_unsafe_spend_permissions(self):
        self.assertEqual(self.run_case(lambda m, o, r, c:
            o.update(paid_api_call_permitted=True))["reason"], "UNSAFE_WORK_ORDER")

    def test_reject_symlink_source(self):
        def mutate(m, o, r, c):
            path = c / "original_frames/frame_02.png"
            path.unlink()
            path.symlink_to(c / "original_frames/frame_01.png")
        self.assertEqual(self.run_case(mutate)["reason"], "SOURCE_FRAME_OUTSIDE_VERIFIED_CACHE")


    def test_real_v102_builder_output_round_trip(self):
        """Exercise the actual V102 handoff, not only a hand-crafted manifest."""
        v102_spec = importlib.util.spec_from_file_location(
            "v102", ROOT / "src" / "storia_rivive_i2i_prepare_v102.py")
        v102 = importlib.util.module_from_spec(v102_spec)
        v102_spec.loader.exec_module(v102)
        with tempfile.TemporaryDirectory() as temp:
            m, order, report, cache = fixture(Path(temp))
            selection = {
                "status": "FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW",
                "preselected": [{"filename": "frame_%02d.png" % n} for n in range(1, 6)],
            }
            actual = v102.build(order, selection, cache)
            self.assertEqual(actual["photos_requested"], 4)
            self.assertEqual(actual["vidu_source_anchor"]["source_sha256"],
                             actual["original_frame_jobs"][4]["source_sha256"])
            checked = handoff.inspect(actual, order, report, cache)
            self.assertEqual(checked["status"], "SOURCE_HANDOFF_BYTES_VERIFIED_REVIEW_PENDING")
            self.assertEqual(checked["verified_photo_source_frames"], 4)

if __name__ == "__main__":
    unittest.main()
