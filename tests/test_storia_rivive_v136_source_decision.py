#!/usr/bin/env python3
"""V136/V137 status tests: all fixtures synthetic, no media or API expense."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from storia_rivive_v136_source_decision import source_state


def good_reports():
    film = "a" * 64
    rows = [
        {"filename": f"frame_{i:02d}.png",
         "source_frame_sha256": f"{i:064x}",
         "source_film_sha256": film}
        for i in range(5)
    ]
    return [
        {"ready": True},
        {"version": "V125_REAL_BW_DECODED_SPATIAL_MOTION_UNAPPROVED",
         "status": "V125_FIVE_MOVING_PHOTO_REGIONS_REVIEW_REQUIRED",
         "source_motion_candidates_pass": 6,
         "source_video_sha256": film},
        {"version": "V126_FIVE_DIVERSE_MOVING_SHOTS_NOT_APPROVED",
         "status": "V126_FIVE_DIFFERENT_MOVING_SOURCE_CANDIDATES_REVIEW_ONLY",
         "source_film_sha256": film, "five_review_candidates": rows},
        {"version": "V128_BALANCED_REAL_ORIGINAL_FRAME_REVIEW_ONLY",
         "status": "V128_FIVE_BALANCED_FRAMES_VISUAL_REVIEW_REQUIRED",
         "source_film_sha256": film,
         "five_review_frames": [
             {"filename": row["filename"], "frame_sha256": row["source_frame_sha256"],
              "source_film_sha256": film} for row in rows]},
        {"version": "V129_REAL_PREFREEZE_MOTION_STRIPS_UNAPPROVED",
         "status": "V129_FIVE_SOURCE_LOCKED_MOTION_STRIPS_REVIEW_ONLY",
         "original_film_sha256": film,
         "five_prefreeze_proxy_strips": [
             {"source_frame": row["filename"]} for row in rows]},
    ]


class V137SourceDecisionTests(unittest.TestCase):
    def state(self, reports):
        return source_state(*reports)

    def test_real_white_house_evidence_is_rejected_not_review_ready(self):
        reports = good_reports()
        reports[1]["status"] = "V125_MOTION_SOURCE_SELECTION_BLOCKED"
        reports[1]["source_motion_candidates_pass"] = 1
        reports[2]["status"] = "V126_INSUFFICIENT_MOTION_SCENE_VARIETY"
        reports[2]["five_review_candidates"] = []
        reports[3]["status"] = "V128_SOURCE_AUDIT_BLOCKED"
        reports[4]["status"] = "V129_SOURCE_MOTION_STRIPS_BLOCKED"
        self.assertEqual(self.state(reports),
                         "SOURCE_REJECTED_V136_INSUFFICIENT_MOTION_VARIETY")

    def test_missing_verified_bytes_fail_closed(self):
        reports = good_reports()
        reports[0]["ready"] = False
        self.assertEqual(self.state(reports), "SOURCE_REJECTED_OR_UNVERIFIED")

    def test_partial_audit_is_not_review_ready(self):
        reports = good_reports()
        reports[1] = {}
        self.assertEqual(self.state(reports), "SOURCE_AUDIT_INCOMPLETE")

    def test_five_candidates_without_visual_evidence_not_ready(self):
        reports = good_reports()
        reports[3] = {}
        self.assertEqual(self.state(reports), "SOURCE_AUDIT_INCOMPLETE")

    def test_complete_evidence_still_needs_rights_and_artistic_review(self):
        self.assertEqual(self.state(good_reports()), "SOURCE_RESEARCH_REVIEW_REQUIRED")

    def test_malformed_motion_counts_not_promoted(self):
        reports = good_reports()
        reports[1]["source_motion_candidates_pass"] = True
        self.assertEqual(self.state(reports), "SOURCE_AUDIT_INCOMPLETE")

    def test_arbitrary_status_strings_do_not_promote_five_dummy_scenes(self):
        for index in (1, 2, 3, 4):
            reports = good_reports()
            reports[index]["status"] = "ERROR_BUT_NOT_BLOCKED"
            self.assertEqual(self.state(reports), "SOURCE_AUDIT_INCOMPLETE")

    def test_explicit_block_with_five_items_cannot_be_promoted(self):
        reports = good_reports()
        reports[1]["status"] = "V125_MOTION_SOURCE_SELECTION_BLOCKED"
        self.assertEqual(self.state(reports),
                         "SOURCE_REJECTED_V136_INSUFFICIENT_MOTION_VARIETY")

    def test_duplicate_or_placeholder_candidates_are_not_evidence(self):
        reports = good_reports()
        reports[2]["five_review_candidates"][1] = copy.deepcopy(
            reports[2]["five_review_candidates"][0])
        self.assertEqual(self.state(reports), "SOURCE_AUDIT_INCOMPLETE")
        reports = good_reports()
        reports[2]["five_review_candidates"] = [{} for _ in range(5)]
        self.assertEqual(self.state(reports), "SOURCE_AUDIT_INCOMPLETE")

    def test_wrong_source_sha_blocks_review(self):
        for index, key in ((1, "source_video_sha256"), (2, "source_film_sha256"),
                           (3, "source_film_sha256"), (4, "original_film_sha256")):
            reports = good_reports()
            reports[index][key] = "b" * 64
            self.assertEqual(self.state(reports), "SOURCE_AUDIT_INCOMPLETE")

    def test_visual_frame_sha_or_strip_identity_mismatch_blocks(self):
        reports = good_reports()
        reports[3]["five_review_frames"][0]["frame_sha256"] = "c" * 64
        self.assertEqual(self.state(reports), "SOURCE_AUDIT_INCOMPLETE")
        reports = good_reports()
        reports[4]["five_prefreeze_proxy_strips"][0]["source_frame"] = "frame_99.png"
        self.assertEqual(self.state(reports), "SOURCE_AUDIT_INCOMPLETE")

    def test_missing_fifth_proxy_or_extra_candidate_blocks(self):
        reports = good_reports()
        reports[4]["five_prefreeze_proxy_strips"].pop()
        self.assertEqual(self.state(reports), "SOURCE_AUDIT_INCOMPLETE")
        reports = good_reports()
        reports[2]["five_review_candidates"].append(copy.deepcopy(
            reports[2]["five_review_candidates"][0]))
        self.assertEqual(self.state(reports), "SOURCE_AUDIT_INCOMPLETE")

    def test_wrong_report_version_blocks(self):
        for index in (1, 2, 3, 4):
            reports = good_reports()
            reports[index]["version"] = "LEGACY_UNCHECKED"
            self.assertEqual(self.state(reports), "SOURCE_AUDIT_INCOMPLETE")

    def test_malformed_report_is_not_promoted(self):
        reports = good_reports()
        reports[4] = None
        self.assertEqual(self.state(reports), "SOURCE_AUDIT_INCOMPLETE")


if __name__ == "__main__":
    unittest.main()
