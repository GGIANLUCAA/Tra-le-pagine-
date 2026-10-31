#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from storia_rivive_v136_source_decision import source_state


class V136SourceDecisionTests(unittest.TestCase):
    def test_real_white_house_evidence_is_rejected_not_review_ready(self):
        self.assertEqual(source_state(
            {"ready": True},
            {"status": "V125_MOTION_SOURCE_SELECTION_BLOCKED", "source_motion_candidates_pass": 1},
            {"status": "V126_INSUFFICIENT_MOTION_SCENE_VARIETY", "five_review_candidates": []},
            {"status": "V128_SOURCE_AUDIT_BLOCKED"},
            {"status": "V129_SOURCE_MOTION_STRIPS_BLOCKED"}),
            "SOURCE_REJECTED_V136_INSUFFICIENT_MOTION_VARIETY")

    def test_missing_verified_bytes_fail_closed(self):
        self.assertEqual(source_state({"ready": False}, {}, {}, {}, {}),
                         "SOURCE_REJECTED_OR_UNVERIFIED")

    def test_partial_audit_is_not_review_ready(self):
        self.assertEqual(source_state({"ready": True}, {}, {}, {}, {}),
                         "SOURCE_AUDIT_INCOMPLETE")

    def test_five_candidates_without_visual_evidence_not_ready(self):
        self.assertEqual(source_state(
            {"ready": True}, {"status": "V125_COMPLETE", "source_motion_candidates_pass": 5},
            {"status": "V126_REVIEW", "five_review_candidates": [{}] * 5},
            {}, {}), "SOURCE_AUDIT_INCOMPLETE")

    def test_complete_evidence_still_needs_rights_and_artistic_review(self):
        self.assertEqual(source_state(
            {"ready": True}, {"status": "V125_COMPLETE", "source_motion_candidates_pass": 6},
            {"status": "V126_REVIEW", "five_review_candidates": [{}] * 5},
            {"status": "V128_REVIEW"}, {"status": "V129_REVIEW"}),
            "SOURCE_RESEARCH_REVIEW_REQUIRED")

    def test_malformed_motion_counts_not_promoted(self):
        self.assertEqual(source_state(
            {"ready": True}, {"status": "V125_COMPLETE", "source_motion_candidates_pass": True},
            {"status": "V126_REVIEW", "five_review_candidates": [{}] * 5},
            {"status": "V128_REVIEW"}, {"status": "V129_REVIEW"}),
            "SOURCE_AUDIT_INCOMPLETE")


if __name__ == "__main__":
    unittest.main()
