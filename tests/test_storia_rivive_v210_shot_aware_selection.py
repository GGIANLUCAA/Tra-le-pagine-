"""V210 source-locked shot-aware preselection regressions; no external calls."""
import hashlib
import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import storia_rivive_v210_shot_aware_selection as v210


def fixture(folder):
    film = folder / "ORIGINAL_ARCHIVE.webm"
    film.write_bytes(b"synthetic fixture: only detector is stubbed, source bytes are SHA checked")
    scout = {"original_sha256": hashlib.sha256(film.read_bytes()).hexdigest(),
             "duration_s": 60.0, "source_frames_extracted": 12}
    frames = [{"filename": f"frame_{i:02d}.png",
               "raster_px": [1280, 720],
               "native_portrait_crop_px": [405, 720],
               "source_visual_quality_score": round(0.50 + (i % 3) * 0.1, 3)}
              for i in range(1, 13)]
    ranking = {"status": v210.READY, "all_candidates": frames}
    original = folder / "original_frames"
    original.mkdir()
    for i in range(1, 13):
        rng = random.Random(i)
        shades = [rng.randrange(40, 225) for _ in range(96 * 72)]
        pixels = [(shade, shade, shade) for shade in shades]
        image = Image.new("RGB", (96, 72))
        image.putdata(pixels)
        image.resize((1280, 720), Image.Resampling.NEAREST).save(original / f"frame_{i:02d}.png")
    return film, ranking, scout


class ShotAwareSelectionTests(unittest.TestCase):
    def test_v223_ffmpeg_fps_midpoint_matches_actual_source_pixels(self):
        # Reproduce the FFmpeg sampling bug with real decoded frames.
        # fps=1/3 samples input seconds 1,4,7,10, NOT 0,3,6,9.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            film = root / "synthetic.mp4"
            subprocess.run([
                "ffmpeg", "-nostdin", "-v", "error", "-y",
                "-f", "lavfi", "-i", "testsrc2=size=160x90:rate=1:duration=12",
                "-c:v", "libx264", "-preset", "ultrafast", str(film)],
                check=True, capture_output=True, timeout=30)
            subprocess.run([
                "ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(film),
                "-vf", "fps=1/3", "-frames:v", "4",
                str(root / "sample_%02d.png")],
                check=True, capture_output=True, timeout=30)
            subprocess.run([
                "ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(film),
                "-vsync", "0", str(root / "raw_%02d.png")],
                check=True, capture_output=True, timeout=30)
            for index, source_index in enumerate((2, 5, 8, 11), 1):
                with Image.open(root / ("sample_%02d.png" % index)) as sample:
                    with Image.open(root / ("raw_%02d.png" % source_index)) as source:
                        self.assertEqual(sample.convert("RGB").tobytes(),
                                         source.convert("RGB").tobytes())

    def test_uses_five_distinct_segments_instead_of_score_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            film, ranking, scout = fixture(root)
            result = v210.select(ranking, scout, root, detector=lambda *_: [8, 18, 28, 38, 48])
            self.assertEqual(result["status"], v210.READY, result)
            self.assertEqual(len(result["preselected"]), 5)
            self.assertEqual(len(set(result["candidate_segment_times_s"])), 5)
            # FFmpeg fps=1/5 chooses the midpoint t=2.5, 7.5, ...;
            # using t=0,5,... made preview endpoints different from PNGs.
            self.assertTrue(all((t - 2.5) % 5 == 0
                                for t in result["candidate_segment_times_s"]))
            self.assertEqual(result["source_frame_timestamp_model"],
                             "V223_FFMPEG_FPS_BIN_MIDPOINT_NOT_LEFT_EDGE")
            self.assertFalse(result["five_distinct_shots_approved"])
            self.assertFalse(result["provider_calls_permitted"])

    def test_v216_real_pilot_style_intertitles_do_not_count_as_five_shots(self):
        from PIL import ImageDraw
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, ranking, scout = fixture(root)
            for i in range(1, 13):
                if i in (6, 10):
                    continue  # only two usable photographic/diagram frames
                path = root / "original_frames" / f"frame_{i:02d}.png"
                image = Image.new("RGB", (1280, 720), (5, 5, 5))
                draw = ImageDraw.Draw(image)
                for j in range(4):
                    draw.rectangle((260, 110 + j * 120, 1020, 145 + j * 120),
                                   fill=(220, 220, 220))
                image.save(path)
            result = v210.select(ranking, scout, root,
                                 detector=lambda *_: [8, 18, 28, 38, 48])
            self.assertEqual(result["reason"], "FIVE_PHOTOGRAPHIC_CANDIDATE_SEGMENTS_UNAVAILABLE")
            self.assertGreaterEqual(result["likely_intertitle_count"], 8)
            self.assertEqual(result["preselected"], [])
            self.assertFalse(result["provider_calls_permitted"])

    def test_v219_faint_grey_intertitle_is_not_photographic_source(self):
        # Paramountown 1922 had dark cards with faint grey text; V216's
        # bright>=2% check missed them. No OCR or artificial title metadata.
        from PIL import ImageDraw
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "faint_card.png"
            card = Image.new("RGB", (1280, 720), (16, 16, 16))
            draw = ImageDraw.Draw(card)
            draw.rectangle((100, 80, 1180, 650), outline=(75, 75, 75), width=3)
            for y in (210, 260, 310, 360):
                draw.rectangle((350, y, 930, y + 8), fill=(75, 75, 75))
            card.save(path)
            self.assertTrue(v210.likely_intertitle(path))
            # Dark-looking but visibly photographic geometry must remain
            # eligible for later human review, not automatically certified.
            photo = Image.new("RGB", (1280, 720), (65, 65, 65))
            ImageDraw.Draw(photo).ellipse((280, 80, 1050, 680), fill=(125, 125, 125))
            photo.save(path)
            self.assertFalse(v210.likely_intertitle(path))

    def test_v219_dark_car_shape_not_rejected_as_intertitle(self):
        # The real Paramountown 175s frame is a car against a dark backdrop;
        # V216 rejected it because it has >2% bright pixels on black.
        from PIL import ImageDraw
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "car_like_photo.png"
            image = Image.new("RGB", (1280, 720), (18, 18, 18))
            draw = ImageDraw.Draw(image)
            draw.ellipse((160, 300, 940, 570), fill=(135, 135, 135))
            draw.ellipse((290, 490, 420, 640), fill=(170, 170, 170))
            draw.ellipse((730, 490, 860, 640), fill=(170, 170, 170))
            image.save(path)
            self.assertFalse(v210.likely_intertitle(path))

    def test_v219_faint_cards_cannot_fill_five_photographic_segments(self):
        from PIL import ImageDraw
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, ranking, scout = fixture(root)
            for i in range(2, 10):
                path = root / "original_frames" / f"frame_{i:02d}.png"
                card = Image.new("RGB", (1280, 720), (16, 16, 16))
                draw = ImageDraw.Draw(card)
                for y in (210, 260, 310, 360):
                    draw.rectangle((350, y, 930, y + 8), fill=(75, 75, 75))
                card.save(path)
            result = v210.select(ranking, scout, root,
                                 detector=lambda *_: [8, 18, 28, 38, 48])
            self.assertEqual(result["reason"], "FIVE_PHOTOGRAPHIC_CANDIDATE_SEGMENTS_UNAVAILABLE")
            self.assertGreaterEqual(result["likely_intertitle_count"], 8)
            self.assertEqual(result["preselected"], [])
            self.assertFalse(result["provider_calls_permitted"])

    def test_v221_sha_bound_human_rejected_uploader_end_card_is_never_selected(self):
        # Actual Fiesole 1912 V220 frame_12 at t=106.004s is a modern
        # YouTube promotional end slate, not a historical photographic shot.
        # Synthetic fixture tests the fail-closed exclusion mechanism.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, ranking, scout = fixture(root)
            review = {
                "version": "V221_SOURCE_LOCKED_EXCLUSIONS",
                "sources": [{
                    "original_sha256": scout["original_sha256"],
                    "excluded_frames": ["frame_12.png"],
                    "reason": "Uploader end card, not historical film footage",
                }],
            }
            result = v210.select(ranking, scout, root,
                                 detector=lambda *_: [8, 18, 28, 38, 48],
                                 exclusions=review)
            self.assertEqual(result["status"], v210.READY, result)
            self.assertEqual(result["source_review_excluded_frames"], ["frame_12.png"])
            self.assertNotIn("frame_12.png",
                             [x["filename"] for x in result["preselected"]])
            self.assertFalse(result["provider_calls_permitted"])

    def test_v221_review_for_different_source_sha_does_not_apply(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, ranking, scout = fixture(root)
            review = {"version": "V221_SOURCE_LOCKED_EXCLUSIONS",
                      "sources": [{"original_sha256": "a" * 64,
                                   "excluded_frames": ["frame_12.png"],
                                   "reason": "Different source; no exclusion here"}]}
            result = v210.select(ranking, scout, root,
                                 detector=lambda *_: [8, 18, 28, 38, 48],
                                 exclusions=review)
            self.assertEqual(result["status"], v210.READY, result)
            self.assertEqual(result["source_review_excluded_frames"], [])

    def test_v221_malformed_exclusion_blocks_selection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, ranking, scout = fixture(root)
            review = {"version": "V221_SOURCE_LOCKED_EXCLUSIONS",
                      "sources": [{"original_sha256": scout["original_sha256"],
                                   "excluded_frames": ["../frame_12.png"],
                                   "reason": "Unsafe source review frame path"}]}
            result = v210.select(ranking, scout, root,
                                 detector=lambda *_: [8, 18, 28, 38, 48],
                                 exclusions=review)
            self.assertEqual(result["reason"], "INVALID_SOURCE_REVIEW_EXCLUSIONS")
            self.assertFalse(result["provider_calls_permitted"])

    def test_single_shot_does_not_produce_fake_five(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, ranking, scout = fixture(root)
            result = v210.select(ranking, scout, root, detector=lambda *_: [])
            self.assertEqual(result["reason"], "FIVE_SHOT_SEGMENTS_WITH_VALID_LEADIN_UNAVAILABLE")
            self.assertEqual(result["preselected"], [])

    def test_cut_during_lead_in_does_not_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, ranking, scout = fixture(root)
            # Midpoint samples at 2.5,7.5,...; a cut 0.5s before each
            # sample makes the 1.2s motion lead-in cross into another shot.
            result = v210.select(ranking, scout, root,
                                 detector=lambda *_: [2, 7, 12, 17, 22, 27,
                                                      32, 37, 42, 47, 52, 57])
            self.assertEqual(result["reason"], "FIVE_SHOT_SEGMENTS_WITH_VALID_LEADIN_UNAVAILABLE")

    def test_modified_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            film, ranking, scout = fixture(root)
            film.write_bytes(b"changed")
            result = v210.select(ranking, scout, root, detector=lambda *_: [8, 18, 28, 38, 48])
            self.assertEqual(result["reason"], "SOURCE_HASH_CHANGED")

    def test_repeated_portrait_selects_lower_ranked_alternative(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, ranking, scout = fixture(root)
            original = root / "original_frames"
            # Two different cut segments repeat the exact same visible shot.
            (original / "frame_04.png").write_bytes((original / "frame_05.png").read_bytes())
            result = v210.select(ranking, scout, root,
                                 detector=lambda *_: [8, 18, 28, 38])
            self.assertEqual(result["status"], v210.READY, result)
            names = [row["filename"] for row in result["preselected"]]
            self.assertFalse("frame_04.png" in names and "frame_05.png" in names)
            self.assertEqual(len(names), 5)
            self.assertEqual(result["visible_portrait_novelty_preflight"],
                             "V205_THRESHOLDS_REUSED_ON_SOURCE_PNG")

    def test_all_portraits_identical_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, ranking, scout = fixture(root)
            original = root / "original_frames"
            repeated = (original / "frame_01.png").read_bytes()
            for i in range(2, 13):
                (original / f"frame_{i:02d}.png").write_bytes(repeated)
            result = v210.select(ranking, scout, root,
                                 detector=lambda *_: [8, 18, 28, 38, 48])
            self.assertEqual(result["reason"],
                             "FIVE_VISUALLY_DISTINCT_SHOT_CANDIDATES_UNAVAILABLE")
            self.assertEqual(result["preselected"], [])
            self.assertFalse(result["provider_calls_permitted"])

    def test_missing_source_png_blocks_before_i2i(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, ranking, scout = fixture(root)
            (root / "original_frames" / "frame_05.png").unlink()
            result = v210.select(ranking, scout, root,
                                 detector=lambda *_: [8, 18, 28, 38, 48])
            self.assertEqual(result["reason"], "SOURCE_FRAME_MISSING_OR_UNSAFE")
            self.assertEqual(result["preselected"], [])

    def test_v212_rejects_real_480p_before_cut_scan(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, ranking, scout = fixture(root)
            low = root / "original_frames" / "frame_05.png"
            with Image.open(low) as source:
                source.resize((720, 480)).save(low)
            ranking["all_candidates"][4]["raster_px"] = [720, 480]
            ranking["all_candidates"][4]["native_portrait_crop_px"] = [270, 480]
            calls = []
            def detector(*args):
                calls.append(args)
                return [8, 18, 28, 38, 48]
            result = v210.select(ranking, scout, root, detector=detector)
            self.assertEqual(result["reason"], "INSUFFICIENT_NATIVE_PORTRAIT_DETAIL")
            self.assertEqual(result["native_portrait_crop_px"], [270, 480])
            self.assertFalse(result["provider_calls_permitted"])
            self.assertEqual(calls, [])

    def test_v212_rejects_forged_ranking_geometry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, ranking, scout = fixture(root)
            ranking["all_candidates"][2]["native_portrait_crop_px"] = [900, 720]
            result = v210.select(ranking, scout, root, detector=lambda *_: [8, 18, 28, 38, 48])
            self.assertEqual(result["reason"], "RANKING_NATIVE_GEOMETRY_MISMATCH")
            self.assertEqual(result["preselected"], [])

    def test_v212_rejects_mixed_native_geometry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, ranking, scout = fixture(root)
            changed = root / "original_frames" / "frame_03.png"
            with Image.open(changed) as source:
                source.resize((1920, 1080)).save(changed)
            ranking["all_candidates"][2]["raster_px"] = [1920, 1080]
            ranking["all_candidates"][2]["native_portrait_crop_px"] = [608, 1080]
            result = v210.select(ranking, scout, root, detector=lambda *_: [8, 18, 28, 38, 48])
            self.assertEqual(result["reason"], "MIXED_NATIVE_SOURCE_GEOMETRY")
            self.assertEqual(result["preselected"], [])

    def test_v214_long_realistic_hd_reel_uses_only_first_bounded_window(self):
        # A known 1920x1080 archival reel lasts ~525s; previous V210
        # rejected it without examining even the first 420 seconds.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, ranking, scout = fixture(root)
            scout["duration_s"] = 524.96
            calls = []
            def detector(film, seconds):
                calls.append(seconds)
                return [25, 70, 115, 160, 205, 250, 295, 340, 385]
            result = v210.select(ranking, scout, root, detector=detector)
            self.assertEqual(calls, [v210.MAX_SECONDS])
            self.assertEqual(result["status"], v210.READY, result)
            self.assertTrue(result["cut_scan_is_partial"])
            self.assertEqual(result["cut_scan_seconds"], 420)
            self.assertGreaterEqual(result["unscanned_late_frames"], 1)
            self.assertEqual(len(result["preselected"]), 5)
            self.assertTrue(all(t < 420 for t in result["candidate_segment_times_s"]))
            self.assertFalse(result["provider_calls_permitted"])
            self.assertFalse(result["five_distinct_shots_approved"])

    def test_v214_late_only_cuts_cannot_fabricate_five_early_shots(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, ranking, scout = fixture(root)
            scout["duration_s"] = 524.96
            result = v210.select(ranking, scout, root,
                                 detector=lambda *_: [440, 455, 470, 490, 510])
            self.assertEqual(result["reason"], "FIVE_SHOT_SEGMENTS_WITH_VALID_LEADIN_UNAVAILABLE")
            self.assertEqual(result["detected_cut_count"], 0)
            self.assertEqual(result["preselected"], [])
            self.assertFalse(result["provider_calls_permitted"])

    def test_v214_source_too_short_in_first_window_still_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, ranking, scout = fixture(root)
            scout["duration_s"] = 524.96
            result = v210.select(ranking, scout, root, detector=lambda *_: [30, 75])
            self.assertEqual(result["reason"], "FIVE_SHOT_SEGMENTS_WITH_VALID_LEADIN_UNAVAILABLE")
            self.assertFalse(result["provider_calls_permitted"])


if __name__ == "__main__":
    unittest.main()
