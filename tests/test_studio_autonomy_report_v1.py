import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from studio_autonomy_report_v1 import summarize, diagnosis


def qa(**updates):
    report = {
        "schema": "quality-director-v17",
        "status": "needs_artistic_review",
        "video": None,
        "blocking": [],
        "warnings": [],
        "format": "libri",
        "paid_calls": 0,
        "published": False,
    }
    report.update(updates)
    return report


class QualityBridgeTests(unittest.TestCase):
    def test_report_without_mp4_is_not_claimed_as_video(self):
        x = summarize(qa())
        self.assertEqual(x["state"], "needs_real_mp4_evidence")
        self.assertFalse(x["owner_approved"])
        self.assertFalse(x["mp4_bytes_verified_by_bridge"])

    def test_report_with_video_reference_still_needs_real_review(self):
        x = summarize(qa(video="output/example.mp4"))
        self.assertEqual(x["state"], "qa_report_for_video_needs_verification")
        self.assertFalse(x["video_sha256_verified_by_bridge"])
        self.assertFalse(x["publish_authorized"])

    def test_blocked_qa_wins_over_video(self):
        x = summarize(qa(video="video.mp4",status="technical_blocked",
                         blocking=[{"code": "INVALID_MP4", "message": "untrusted"}]))
        self.assertEqual(x["state"], "technical_blocked")
        self.assertEqual(x["blocker_codes"], ["INVALID_MP4"])

    def test_codes_are_deduplicated_and_raw_errors_are_not_exposed(self):
        x = summarize(qa(warnings=[{"code": "DARK_SAMPLES",
                                    "message": "PRIVATE TOKEN should not escape"},
                                   {"code": "DARK_SAMPLES", "message": "ignored"},
                                   {"code": "ALERT<script>", "message": "malicious"}]))
        self.assertEqual(x["warning_codes"], ["DARK_SAMPLES"])
        self.assertNotIn("PRIVATE TOKEN", json.dumps(x))
        self.assertNotIn("<script>", json.dumps(x))

    def test_run_link_same_repo_only(self):
        valid = "https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/123456"
        self.assertEqual(summarize(qa(), valid)["run_url"], valid)
        self.assertIsNone(summarize(qa(), "https://otherdomain.example/run")["run_url"])
        self.assertIn("Esecuzione GitHub", diagnosis(summarize(qa(), valid)))

    def test_invalid_report_blocks(self):
        with self.assertRaises(ValueError):
            summarize(qa(schema="unknown"))
        with self.assertRaises(ValueError):
            summarize(qa(status="complete"))
        with self.assertRaises(ValueError):
            summarize(qa(warnings="not-an-array"))


if __name__ == "__main__":
    unittest.main()
