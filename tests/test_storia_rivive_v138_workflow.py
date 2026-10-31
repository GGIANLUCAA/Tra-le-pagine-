"""V138: safe, source-exact third archival pilot contract — no paid providers.

This test validates workflow wiring and real candidate metadata without
pretending that a synthetic test proves the five-shot historic film quality.
"""
import json
import re
import unittest
from pathlib import Path

from src.storia_rivive_autopilot_v101 import build_work_order

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT/".github/workflows/storia-v138-versailles-source-audit.yml"
BANK = ROOT/"queue/storia_rivive_candidates_v58.json"
PROFILE = ROOT/"config/storia_rivive_autopilot_v101.json"
ID = "versailles_treaty_1919"
PAGE = "https://commons.wikimedia.org/wiki/File:The_signing_of_the_peace_treaty_of_Versailles_(16_fps).webm"


class TestV138VersaillesAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.yaml = WORKFLOW.read_text(encoding="utf-8")
        cls.bank = json.loads(BANK.read_text(encoding="utf-8"))
        cls.profile = json.loads(PROFILE.read_text(encoding="utf-8"))

    def test_one_exact_archival_page_with_no_italian_rights_claim(self):
        found = [c for c in self.bank["candidates"] if c.get("id") == ID]
        self.assertEqual(len(found), 1)
        item = found[0]
        self.assertEqual(item["source_page"], PAGE)
        self.assertEqual(item["year"], 1919)
        self.assertFalse(item.get("rights_italy_verified"))
        self.assertFalse(item.get("source_native_visual_review"))
        self.assertFalse(item.get("historical_attribution_verified"))
        self.assertEqual(item["commons_original_raster_claim_px"], [1920, 1080])
        self.assertLess(item["commons_original_file_size_mb_approx"], 160)

    def test_workorder_remains_research_only(self):
        item = next(c for c in self.bank["candidates"] if c["id"] == ID)
        order = build_work_order({"candidates":[item]}, "2026-10-31T12:00:00Z",self.profile)
        self.assertEqual(order["episode_id"],ID)
        self.assertEqual(order["source_page"],PAGE)
        self.assertFalse(order["paid_api_call_permitted"])
        self.assertFalse(order["publish_permitted"])
        self.assertFalse(order["human_approved"])
        self.assertEqual(order["credits_spent"],0)
        self.assertIn("ITALY_AND_RESIDUAL_RIGHTS_NEED_REVIEW",order["blocking_issues"])
        self.assertIn("HISTORICAL_PLACE_DATE_NEED_REVIEW",order["blocking_issues"])

    def test_workflow_uses_exact_source_and_never_auto_publishes(self):
        s=self.yaml
        self.assertIn("pull_request:",s)
        self.assertIn("workflow_dispatch:",s)
        self.assertIn('contents: read',s)
        self.assertIn('if: github.run_attempt == 1',s)
        self.assertIn(f'c["id"]=="{ID}"',s)
        self.assertIn(PAGE,s)
        self.assertNotIn("white_house_1917_1921",s)
        self.assertNotIn("france_cotton_mill_1920",s)
        self.assertNotIn("write-all",s)
        self.assertNotIn("secrets.",s)
        self.assertNotIn("VIDU_API",s)
        self.assertNotIn("purchase",s.lower())
        self.assertIn("Unexpected paid or publication permission",s)
        self.assertIn('"credits_spent":0,"publication_permitted":False',s)

    def test_live_bytes_pts_and_five_motion_gate_are_all_linked(self):
        s=self.yaml
        for program in (
            "storia_rivive_scout_v101.py",
            "storia_rivive_v134_cache_readiness.py",
            "storia_rivive_adaptive_sampling_v124.py",
            "storia_rivive_v125_real_motion_audit.py",
            "storia_rivive_v126_balanced_motion_review.py",
            "storia_rivive_v126_frame_diversity.py",
            "storia_rivive_v128_balanced_frame_review.py",
            "storia_rivive_v129_prefreeze_motion_strips.py",
            "storia_rivive_v136_source_decision",
        ):
            self.assertIn(program,s)
        self.assertIn("SOURCE_READINESS_V134.json",s)
        self.assertIn("REAL_BW_MOTION_V125.json",s)
        self.assertIn("FIVE_MOVING_REVIEW_V126.json",s)
        self.assertIn("BALANCED_VISUAL_REVIEW_V128.json",s)
        self.assertIn("PREFREEZE_MOTION_STRIPS_V129.json",s)
        self.assertIn("REAL_SOURCE_AUDIT_V138.json",s)
        self.assertIn('if: always()',s)
        self.assertIn('source_state(readiness,motion,balanced,visual,strips)',s)

    def test_artifact_has_review_reports_not_original_media(self):
        s=self.yaml
        artifact = s.split("      - name: Save only source metadata")[1]
        self.assertIn("STORIA_V138_VERSAILLES_SOURCE_AUDIT_",artifact)
        self.assertIn("ORIGINAL_FILM_CONTACT_SHEET.jpg",artifact)
        self.assertIn("PREFREEZE_MOTION_STRIPS_V129.jpg",artifact)
        self.assertNotIn("ORIGINAL_ARCHIVE.webm",artifact)
        self.assertNotIn("original_frames/*.png",artifact)
        self.assertNotIn("*.mp4",artifact)


if __name__=="__main__":
    unittest.main()
