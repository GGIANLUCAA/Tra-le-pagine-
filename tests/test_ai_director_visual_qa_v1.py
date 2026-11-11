#!/usr/bin/env python3
"""No-network real-MP4 QA tests: parsing and safely unavailable media."""
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import ai_director_visual_qa_v1 as qa


class RealVideoTests(unittest.TestCase):
    @mock.patch.object(qa, "_run_ffmpeg")
    @mock.patch.object(qa, "probe")
    def test_detects_probable_flash_and_black_intervals(self, fake_probe, fake_filter):
        fake_probe.return_value = (
            Path("/tmp/sample.mp4"), 5.0,
            [{"codec_type": "video", "codec_name": "h264"},
             {"codec_type": "audio", "codec_name": "aac"}]
        )
        fake_filter.side_effect = [
            "[Parsed_showinfo_3] pts_time:1.100\n"
            "[Parsed_showinfo_3] pts_time:1.350\n"
            "[Parsed_showinfo_3] pts_time:3.200\n",
            "[blackdetect @abc] black_start:2.1 black_end:2.3 black_duration:0.2\n",
        ]
        report = qa.inspect("/tmp/sample.mp4")
        self.assertEqual(report["status"], "technical_review_only")
        self.assertFalse(report["human_artistic_approval"])
        codes = [i["code"] for i in report["issues"]]
        self.assertIn("POSSIBLE_BLINK_FRAME", codes)
        self.assertIn("BLACK_FRAME_REVIEW", codes)
        self.assertEqual(report["black_intervals"][0]["duration_s"], 0.2)
        self.assertEqual(len(fake_filter.call_args_list), 2)

    @mock.patch.object(qa, "_run_ffmpeg")
    @mock.patch.object(qa, "probe")
    def test_unavailable_scan_does_not_fabricate_success(self, fake_probe, fake_filter):
        fake_probe.return_value = (
            Path("/tmp/sample.mp4"), 5.0,
            [{"codec_type": "video", "codec_name": "h264"}]
        )
        fake_filter.side_effect = RuntimeError("diagnostic failed")
        r = qa.inspect("/tmp/sample.mp4")
        codes = [x["code"] for x in r["issues"]]
        self.assertIn("CUT_SCAN_UNAVAILABLE", codes)
        self.assertIn("BLACK_SCAN_UNAVAILABLE", codes)
        self.assertFalse(r["narration_alignment_verified"])

    @mock.patch.object(qa, "_run_ffmpeg")
    @mock.patch.object(qa, "probe")
    def test_long_video_reports_partial_scan(self, fake_probe, fake_filter):
        fake_probe.return_value = (
            Path("/tmp/sample.mp4"), 500.0,
            [{"codec_type": "video", "codec_name": "hevc"},
             {"codec_type": "audio", "codec_name": "aac"}]
        )
        fake_filter.return_value = ""
        r = qa.inspect("/tmp/sample.mp4")
        self.assertEqual(r["analyzed_seconds"], 240)
        self.assertTrue(r["partial_scan"])
        self.assertIn("PARTIAL_SCAN", [x["code"] for x in r["issues"]])
        self.assertIn("VIDEO_CODEC_REVIEW", [x["code"] for x in r["issues"]])

    def test_missing_file_is_rejected(self):
        with self.assertRaises((ValueError, RuntimeError)):
            qa.probe("/mnt/data/this-file-should-not-exist.mp4")


if __name__ == "__main__":
    unittest.main()
