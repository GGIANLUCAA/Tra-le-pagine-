"""Regression tests for real-video, real-voice ArtVision Critico review capture."""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from artvision_critico_review_capture_v1 import capture, digest

ROOT = Path(__file__).resolve().parents[1]


def fixture(tmp):
    tmp = Path(tmp)
    wav = tmp / "VOCE.wav"
    with wave.open(str(wav), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(8000)
        f.writeframes(b"\x00\x00" * (8000 * 4))
    cache = tmp / "VOICE_CACHE_V13.json"
    cache.write_text(json.dumps({
        "wav_sha256": digest(wav),
        "alignment": {"method": "asr_with_interpolation", "matched_fraction": .97},
        "timed": [["La figura indica il cielo.", 0, 1.4],
                  ["La mano alzata risalta.", 1.4, 3.7]],
    }), encoding="utf8")
    return wav, cache


@unittest.skipUnless(shutil.which("ffmpeg"), "Requires FFmpeg for real MP4 frames")
class FocusCaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.wav, self.cache = fixture(self.root)
        self.mp4 = self.root / "ACTUAL_REVIEW.mp4"
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-f", "lavfi", "-i", "color=c=blue:s=96x128:r=5:d=5",
            "-an", "-c:v", "mpeg4", "-q:v", "5", str(self.mp4),
        ], check=True, timeout=30)
        self.trace = [
            {"time_s": .5, "chapter_index": 0, "kind": "detail",
             "camera_crop_xyxy": [.1, .1, .4, .4]},
            {"time_s": 1., "chapter_index": 0, "kind": "detail",
             "camera_crop_xyxy": [.2, .1, .5, .4]},
            {"time_s": 1.5, "chapter_index": 0, "kind": "detail",
             "camera_crop_xyxy": [.2, .1, .5, .4]},
            {"time_s": 2., "chapter_index": 1, "kind": "whole_plate",
             "camera_crop_xyxy": None},
            {"time_s": 2.5, "chapter_index": 1, "kind": "whole_plate",
             "camera_crop_xyxy": None},
            {"time_s": 3., "chapter_index": 1, "kind": "whole_plate",
             "camera_crop_xyxy": None},
            {"time_s": 3.5, "chapter_index": 1, "kind": "whole_plate",
             "camera_crop_xyxy": None},
            {"time_s": 4., "chapter_index": 1, "kind": "whole_plate",
             "camera_crop_xyxy": None},
        ]

    def params(self):
        return dict(video=self.mp4, wav=self.wav, voice_cache=self.cache,
                    output_dir=self.root / "QA", variant="critico_standard",
                    voice_offset_s=.5, video_duration_s=5.,
                    camera_trace=self.trace,
                    expected_video_sha256=digest(self.mp4))

    def test_real_mp4_three_samples_per_sentence_pending_not_gold(self):
        report = capture(**self.params())
        self.assertEqual(report["sentence_count"], 2)
        self.assertEqual(report["real_frames_extracted"], 6)
        self.assertEqual(report["status"], "needs_visual_and_semantic_review")
        self.assertFalse(report["v25_gold"])
        self.assertTrue(report["camera_measurements_from_renderer"])
        self.assertEqual(report["media_sha256"], digest(self.mp4))
        paths = [self.root/"QA"/sample["actual_mp4_frame"]
                 for sentence in report["sentences"]
                 for sample in sentence["samples"]]
        self.assertEqual(len(paths), 6)
        self.assertTrue(all(path.is_file() and path.stat().st_size > 0 for path in paths))
        self.assertTrue(any(s["camera_measurement"] is not None
                            for sentence in report["sentences"]
                            for s in sentence["samples"]))
        for sentence in report["sentences"]:
            for sample in sentence["samples"]:
                self.assertEqual(sample["visual_review"], "PENDING")
        self.assertTrue((self.root/"QA"/"ARTVISION_CRITICO_REAL_MP4_FOCUS_QA.json").is_file())

    def test_wrong_video_sha_fails_closed(self):
        args = self.params()
        args["expected_video_sha256"] = "a" * 64
        with self.assertRaisesRegex(ValueError, "MP4 SHA mismatch"):
            capture(**args)

    def test_wrong_wav_fails_closed(self):
        bad = json.loads(self.cache.read_text())
        bad["wav_sha256"] = "a" * 64
        self.cache.write_text(json.dumps(bad))
        with self.assertRaisesRegex(ValueError, "WAV not identical"):
            capture(**self.params())

    def test_unsorted_actual_camera_track_fails(self):
        args = self.params()
        args["camera_trace"] = list(reversed(self.trace))
        with self.assertRaisesRegex(ValueError, "ordered frame times"):
            capture(**args)


class ExistingRendererHookTests(unittest.TestCase):
    def test_all_five_reuse_shared_capture_and_preserve_original_media(self):
        srcs = [
            "artvision_rebel_critico_standard_v144.py",
            "artvision_simberg_garden_critico_v146.py",
            "artvision_bruegel_triumph_critico_v151.py",
            "artvision_waterhouse_magic_circle_critico_v159.py",
            "artvision_blake_ghost_flea_critico_v159.py",
        ]
        for name in srcs:
            with self.subTest(name=name):
                content = (ROOT / "src" / name).read_text(encoding="utf-8")
                self.assertIn("capture_artvision_focus(", content)
                self.assertIn("camera_trace.append(", content)
                self.assertIn('focus["real_frames_extracted"]', content)
                self.assertIn('if f.is_file():z.write(f,arcname=str(f.relative_to(OUT)))', content)
                self.assertIn('"Gold_V25":False', content)


if __name__ == "__main__":
    unittest.main()
