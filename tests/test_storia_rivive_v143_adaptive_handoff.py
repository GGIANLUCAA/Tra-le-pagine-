"""V143: no false five-shot status when V124 cannot sample the real film."""
import json
import tempfile
import unittest
from pathlib import Path

from src.storia_rivive_v143_adaptive_handoff import decide, read_json

SHA = "a" * 64


def fixture():
    adaptive = {"status": "V124_SOURCE_RESEARCH_COMPLETE_NOT_APPROVED",
                "sampled": 5, "source_sha256": SHA}
    rank = {"adaptive_frame_source_sha256": SHA,
            "all_candidates": [{"filename": f"frame_{i:02d}.png"} for i in range(5)]}
    scout = {"original_sha256": SHA,
             "adaptive_research_version": "V124_UNAPPROVED_LONG_SEGMENT_TARGET_SAMPLING"}
    readiness = {"ready": True}
    return adaptive, rank, scout, readiness


class TestV143AdaptiveHandoff(unittest.TestCase):
    def test_valid_five_source_frames_reach_only_motion_review(self):
        result = decide(*fixture())
        self.assertTrue(result["ready"])
        self.assertEqual(result["status"], "V143_ADAPTIVE_REVIEW_EVIDENCE_READY")
        self.assertNotIn("APPROVED", result["status"])

    def test_real_v142_no_v113_shots_rejected_without_downstream_crash(self):
        a, r, s, ready = fixture()
        a = {"status": "V124_ADAPTIVE_SOURCE_RESEARCH_BLOCKED",
             "reason": "V124_SHOT_ANALYSIS_UNAVAILABLE", "paid_calls": 0}
        result = decide(a, {}, s, ready)
        self.assertFalse(result["ready"])
        self.assertEqual(result["status"], "SOURCE_REJECTED_V143_INSUFFICIENT_DETECTED_SHOTS")

    def test_fewer_than_five_long_segments_is_not_a_video(self):
        a, r, s, ready = fixture()
        a = {"status": "V124_ADAPTIVE_SOURCE_RESEARCH_BLOCKED",
             "reason": "V124_NOT_ENOUGH_LONG_SOURCE_SEGMENTS"}
        self.assertEqual(decide(a, {}, s, ready)["status"],
                         "SOURCE_REJECTED_V143_INSUFFICIENT_DETECTED_SHOTS")

    def test_decoder_or_network_failure_is_not_false_source_rejection(self):
        a, r, s, ready = fixture()
        a = {"status": "V124_ADAPTIVE_SOURCE_RESEARCH_BLOCKED",
             "reason": "V124_ORIGINAL_FRAME_DECODE_FAILED_OR_TIMEOUT"}
        result = decide(a, {}, s, ready)
        self.assertEqual(result["status"], "SOURCE_AUDIT_INCOMPLETE")
        self.assertFalse(result["ready"])

    def test_missing_rank_or_source_metadata_cannot_pass(self):
        a, r, s, ready = fixture()
        self.assertFalse(decide(a, {}, s, ready)["ready"])
        self.assertFalse(decide(a, r, {}, ready)["ready"])

    def test_wrong_film_sha_or_mismatched_frame_count_cannot_pass(self):
        a, r, s, ready = fixture()
        r["adaptive_frame_source_sha256"] = "b" * 64
        self.assertFalse(decide(a, r, s, ready)["ready"])
        a, r, s, ready = fixture()
        r["all_candidates"] = r["all_candidates"][:4]
        self.assertFalse(decide(a, r, s, ready)["ready"])

    def test_unverified_original_bytes_cannot_be_rejected_as_proven(self):
        a, r, s, ready = fixture()
        a = {"status": "V124_ADAPTIVE_SOURCE_RESEARCH_BLOCKED",
             "reason": "V124_SHOT_ANALYSIS_UNAVAILABLE"}
        result = decide(a, {}, s, {"ready": False})
        self.assertEqual(result["status"], "SOURCE_AUDIT_INCOMPLETE")

    def test_missing_or_invalid_json_is_incomplete(self):
        with tempfile.TemporaryDirectory() as root:
            p = Path(root) / "report.json"
            self.assertEqual(read_json(p), {})
            p.write_text("{bad json")
            self.assertEqual(read_json(p), {})
            p.write_text(json.dumps([1, 2, 3]))
            self.assertEqual(read_json(p), {})

    def test_workflow_guards_downstream_steps_and_records_block(self):
        workflow = (Path(__file__).resolve().parents[1] /
                    ".github/workflows/storia-v142-constantinople-source-audit.yml").read_text()
        self.assertIn("storia_rivive_v143_adaptive_handoff.py", workflow)
        self.assertIn("ADAPTIVE_GATE_V143.json", workflow)
        self.assertGreaterEqual(workflow.count("if: steps.adaptive.outputs.ready == 'true'"), 5)
        self.assertIn("SOURCE_REJECTED_V143_INSUFFICIENT_DETECTED_SHOTS", workflow)
        self.assertNotIn("  schedule:", workflow)
        self.assertNotIn("VIDU_API_KEY", workflow)


if __name__ == "__main__":
    unittest.main()
