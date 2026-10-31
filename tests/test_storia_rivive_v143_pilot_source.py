"""V143: user-approved research-only source check for rare 1915 LOC trench film.

This protects the 4+1 pipeline from unwanted publishing, Vidu charges,
false provenance and accidental swapping back to the rejected 1916 source.
"""
import json
import unittest
from pathlib import Path

from src.storia_rivive_autopilot_v101 import build_work_order

ROOT=Path(__file__).resolve().parents[1]
BANK=json.loads((ROOT/"queue/storia_rivive_candidates_v58.json").read_text(encoding="utf-8"))
PROFILE=json.loads((ROOT/"config/storia_rivive_autopilot_v101.json").read_text(encoding="utf-8"))
REJECTED=json.loads((ROOT/"config/storia_rivive_v133_rejected_films.json").read_text(encoding="utf-8"))
LOW=json.loads((ROOT/"config/storia_rivive_v140_low_raster_sources.json").read_text(encoding="utf-8"))
TEXT=(ROOT/".github/workflows/storia-v143-trenches-source-audit.yml").read_text(encoding="utf-8")
NAME="russian_trenches_1915"
PAGE="https://commons.wikimedia.org/wiki/File:Into_the_Catacombs_of_War_-_Albert_Dawson_Inspecting_Russian_Trenches_(August_1915).ogg"


class TestV143Pilots(unittest.TestCase):
    def test_loc_archival_candidate_exists_once_and_is_not_cleared_for_italy(self):
        matches=[x for x in BANK["candidates"] if x.get("id")==NAME]
        self.assertEqual(len(matches),1)
        src=matches[0]
        self.assertEqual(src["source_page"],PAGE)
        self.assertEqual(src["commons_original_raster_claim_px"],[1920,1080])
        self.assertLess(src["commons_original_file_size_mb_approx"],160)
        self.assertEqual(src["year"],1915)
        self.assertEqual(src["license"],"PUBLIC_DOMAIN")
        for k in ("rights_italy_verified","historical_attribution_verified",
                  "source_native_visual_review","original_film_sha256_verified"):
            self.assertFalse(src[k])
        self.assertTrue(any("Library of Congress" in r for r in src["risks"]))

    def test_sha_bound_prior_four_rejected_sources_never_reenter_rotation(self):
        selected=build_work_order(BANK,"2026-10-31T15:00:00Z",PROFILE,REJECTED,LOW)
        self.assertEqual(selected["episode_id"],NAME)
        self.assertEqual(len(selected["excluded_sha_bound_sources"]),4)
        self.assertEqual(len(selected["excluded_low_native_raster_sources"]),7)
        self.assertFalse(selected["skip_source_acquisition"])
        self.assertFalse(selected["paid_api_call_permitted"])
        self.assertFalse(selected["publish_permitted"])
        self.assertFalse(selected["video_completed"])
        self.assertEqual(selected["credits_spent"],0)
        self.assertIn("ITALY_AND_RESIDUAL_RIGHTS_NEED_REVIEW",selected["blocking_issues"])

    def test_workflow_uses_real_bounded_source_and_never_calls_paid_providers(self):
        s=TEXT
        self.assertIn("  pull_request:",s)
        self.assertIn("  workflow_dispatch:",s)
        self.assertNotIn("  schedule:",s)
        self.assertIn("contents: read",s)
        self.assertIn('if: github.run_attempt == 1',s)
        self.assertIn('c["id"]=="'+NAME+'"',s)
        self.assertIn(PAGE,s)
        self.assertNotIn("constantinople_messter_1916",s)
        self.assertNotIn("versailles_treaty_1919",s)
        self.assertNotIn("secrets.",s)
        self.assertNotIn("VIDU_API_KEY",s)
        self.assertIn('if order["paid_api_call_permitted"] or order["publish_permitted"]:',s)
        for program in ("storia_rivive_scout_v101.py",
                        "storia_rivive_v134_cache_readiness.py",
                        "storia_rivive_adaptive_sampling_v124.py",
                        "storia_rivive_v125_real_motion_audit.py",
                        "storia_rivive_v126_balanced_motion_review.py",
                        "storia_rivive_v128_balanced_frame_review.py",
                        "storia_rivive_v129_prefreeze_motion_strips.py"):
            self.assertIn(program,s)

    def test_report_preserves_rights_and_attribution_uncertainty(self):
        s=TEXT
        for required in ('"rights_italy_verified":False',
                         '"exact_commons_file_matches_LOC_original":False',
                         '"modern_derivative_reuse_cleared":False',
                         '"i2i_generated":0,"vidu_generated":0,"mp4_generated":False',
                         '"credits_spent":0,"publication_permitted":False'):
            self.assertIn(required,s)
        artifact=s.split("      - name: Save only source metadata",1)[-1]
        self.assertIn("REAL_SOURCE_AUDIT_V143.json",artifact)
        self.assertIn("PREFREEZE_MOTION_STRIPS_V129.jpg",artifact)
        self.assertNotIn("ORIGINAL_ARCHIVE.webm",artifact)
        self.assertNotIn("original_frames/",artifact)


if __name__=="__main__":
    unittest.main()
