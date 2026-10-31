"""V140: skip already verified 480p/576p *published originals* before download.

These are editorial/research exclusions for a dated Commons snapshot, not
proof about museum negatives or rights. No I2I, Vidu, purchases or publishing.
"""
import copy
import datetime as dt
import json
import unittest
from pathlib import Path

from src.storia_rivive_autopilot_v101 import build_work_order, known_low_raster_ids

ROOT=Path(__file__).resolve().parents[1]
BANK=json.loads((ROOT/"queue/storia_rivive_candidates_v58.json").read_text(encoding="utf-8"))
PROFILE=json.loads((ROOT/"config/storia_rivive_autopilot_v101.json").read_text(encoding="utf-8"))
REJECTED=json.loads((ROOT/"config/storia_rivive_v133_rejected_films.json").read_text(encoding="utf-8"))
LOW_RASTER=json.loads((ROOT/"config/storia_rivive_v140_low_raster_sources.json").read_text(encoding="utf-8"))
SEVEN={"paris_swim_1918","paris_train_1918","beirut_1919_street",
       "paris_cafe_strike_1919","paris_champs_1918","market_rural_1920",
       "china_daily_life_1928"}
THREE={"france_cotton_mill_1920","white_house_1917_1921","versailles_treaty_1919"}
# Keep the V140 snapshot stable when the producer adds the next *new* candidate.
KNOWN_V140_BANK={"candidates":[c for c in BANK["candidates"] if c["id"] in (SEVEN|THREE)]}
REJECTED_V140_ONLY={"version":REJECTED["version"],"rejected":[r for r in REJECTED["rejected"] if r["candidate_id"] in THREE]}




class TestV140ResearchQueue(unittest.TestCase):
    def test_all_seven_old_original_rasters_are_below_crop_minimum(self):
        self.assertEqual(known_low_raster_ids(BANK["candidates"],LOW_RASTER),SEVEN)
        rows=LOW_RASTER["excluded"]
        self.assertEqual(len(rows),7)
        for row in rows:
            width,height=row["commons_original_raster_px"]
            self.assertTrue(height<720 or min(width,round(height*9/16))<400)
            self.assertEqual(row["verified_snapshot_utc"],"2026-10-31")
        self.assertEqual(
            next(r for r in rows if r["candidate_id"]=="china_daily_life_1928")["commons_original_raster_px"],
            [720,480])
        self.assertEqual(
            sum(r["commons_original_raster_px"]==[768,576] for r in rows),6)

    def test_full_current_queue_skips_gracefully_until_new_hd_source_added(self):
        order=build_work_order(KNOWN_V140_BANK,"2026-10-31T12:00:00Z",PROFILE,REJECTED_V140_ONLY,LOW_RASTER)
        self.assertEqual(order["episode_id"],"no_eligible_source")
        self.assertEqual(order["status"],"SOURCE_RESEARCH_SKIPPED_NO_NATIVE_HD_CANDIDATES")
        self.assertIn("NO_NATIVE_HD_CANDIDATE_IN_CURRENT_RESEARCH_QUEUE",order["blocking_issues"])
        self.assertEqual(set(order["excluded_sha_bound_sources"]),THREE)
        self.assertEqual(set(order["excluded_low_native_raster_sources"]),SEVEN)
        self.assertTrue(order["skip_source_acquisition"])
        self.assertFalse(order["paid_api_call_permitted"])
        self.assertFalse(order["publish_permitted"])
        self.assertFalse(order["video_completed"])

    def test_every_three_hour_cycle_skips_with_zero_credits(self):
        start=dt.datetime(2026,10,31,tzinfo=dt.timezone.utc)
        for i in range(24):
            now=(start+dt.timedelta(hours=i*3)).isoformat()
            order=build_work_order(KNOWN_V140_BANK,now,PROFILE,REJECTED_V140_ONLY,LOW_RASTER)
            with self.subTest(now=now):
                self.assertTrue(order["skip_source_acquisition"])
                self.assertEqual(order["status"],"SOURCE_RESEARCH_SKIPPED_NO_NATIVE_HD_CANDIDATES")
                self.assertEqual(order["credits_spent"],0)
                self.assertFalse(order["human_approved"])

    def test_new_hd_film_can_enter_queue_without_fabricating_approval(self):
        bank=copy.deepcopy(KNOWN_V140_BANK)
        bank["candidates"].append({
            "id":"new_verified_source_scan_1924",
            "source_page":"https://commons.wikimedia.org/wiki/File:New_original_scan_1924.webm",
            "year":1924,"license":"PDM"})
        order=build_work_order(bank,"2026-10-31T12:00:00Z",PROFILE,REJECTED_V140_ONLY,LOW_RASTER)
        self.assertEqual(order["episode_id"],"new_verified_source_scan_1924")
        self.assertFalse(order["skip_source_acquisition"])
        self.assertFalse(order["paid_api_call_permitted"])
        self.assertFalse(order["publish_permitted"])
        self.assertIn("ITALY_AND_RESIDUAL_RIGHTS_NEED_REVIEW",order["blocking_issues"])

    def test_next_real_trench_film_enters_research_queue_but_not_production(self):
        order=build_work_order(BANK,"2026-10-31T14:00:00Z",PROFILE,REJECTED,LOW_RASTER)
        self.assertEqual(order["episode_id"],"russian_trenches_1915")
        self.assertEqual(len(order["excluded_sha_bound_sources"]),4)
        self.assertEqual(len(order["excluded_low_native_raster_sources"]),7)
        self.assertFalse(order["skip_source_acquisition"])
        self.assertEqual(order["status"],"SOURCE_PREFLIGHT_REVIEW_REQUIRED")
        self.assertFalse(order["paid_api_call_permitted"])
        self.assertFalse(order["publish_permitted"])
        self.assertFalse(order["video_completed"])
        self.assertIn("ITALY_AND_RESIDUAL_RIGHTS_NEED_REVIEW",order["blocking_issues"])

    def test_stale_page_is_not_silently_excluded(self):
        bank=copy.deepcopy(BANK)
        selected=next(c for c in bank["candidates"] if c["id"]=="paris_swim_1918")
        selected["source_page"]="https://commons.wikimedia.org/wiki/File:New_HD_version.webm"
        with self.assertRaisesRegex(ValueError,"V140_LOW_RASTER_SOURCE_PAGE_CHANGED"):
            known_low_raster_ids(bank["candidates"],LOW_RASTER)

    def test_malformed_dimensions_or_incomplete_evidence_fail_closed(self):
        overrides=(
            {"commons_original_raster_px":[1920,1080]},
            {"commons_original_raster_px":[768,True]},
            {"commons_original_raster_px":[768,-1]},
            {"commons_original_raster_px":"768x576"},
            {"evidence_url":"https://example.com/not-official"},
        )
        for change in overrides:
            with self.subTest(change=change):
                registry=copy.deepcopy(LOW_RASTER)
                registry["excluded"][0].update(change)
                with self.assertRaisesRegex(ValueError,"V140_"):
                    known_low_raster_ids(BANK["candidates"],registry)

    def test_duplicate_and_unrecognized_exclusions_abort(self):
        registry=copy.deepcopy(LOW_RASTER)
        registry["excluded"].append(copy.deepcopy(registry["excluded"][0]))
        with self.assertRaisesRegex(ValueError,"V140_LOW_RASTER_ID_UNKNOWN_OR_DUPLICATE"):
            known_low_raster_ids(BANK["candidates"],registry)
        registry=copy.deepcopy(LOW_RASTER)
        registry["excluded"][0]["candidate_id"]="made_up_low_raster_source"
        with self.assertRaisesRegex(ValueError,"V140_LOW_RASTER_ID_UNKNOWN_OR_DUPLICATE"):
            known_low_raster_ids(BANK["candidates"],registry)

    def test_legacy_work_orders_unchanged_when_no_low_raster_registry_given(self):
        order=build_work_order(BANK,"2026-10-31T12:00:00Z",PROFILE,REJECTED)
        self.assertNotEqual(order["episode_id"],"no_eligible_source")
        self.assertEqual(order["excluded_low_native_raster_sources"],[])
        self.assertFalse(order["paid_api_call_permitted"])


if __name__=="__main__":
    unittest.main()
