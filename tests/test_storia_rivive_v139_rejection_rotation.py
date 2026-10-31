"""V139: permanent, SHA-bound exclusion of three audited unusable original films.

No API calls. The film is excluded from this three-hour *research rotation*
only; a new source scan with different bytes and independently verified rights
can be considered through a separately reviewed candidate.
"""
import copy
import datetime
import json
import unittest
from pathlib import Path

from src.storia_rivive_autopilot_v101 import build_work_order, rejected_source_ids

ROOT=Path(__file__).resolve().parents[1]
BANK=json.loads((ROOT/"queue/storia_rivive_candidates_v58.json").read_text(encoding="utf-8"))
REGISTRY=json.loads((ROOT/"config/storia_rivive_v133_rejected_films.json").read_text(encoding="utf-8"))
PROFILE=json.loads((ROOT/"config/storia_rivive_autopilot_v101.json").read_text(encoding="utf-8"))
EXCLUDED={"france_cotton_mill_1920","white_house_1917_1921","versailles_treaty_1919"}


class TestV139SourceRotation(unittest.TestCase):
    def test_all_three_rejections_are_bound_to_current_source(self):
        entries=BANK["candidates"]
        ids=rejected_source_ids(entries,REGISTRY)
        self.assertEqual(ids,EXCLUDED)
        for row in REGISTRY["rejected"]:
            self.assertEqual(len(row["film_sha256"]),64)
            self.assertIn(row["audit_status"],{
                "SOURCE_REJECTED_V132_INSUFFICIENT_DIVERSITY_AFTER_VETO",
                "SOURCE_REJECTED_V136_INSUFFICIENT_MOTION_VARIETY"})
            self.assertTrue(row["evidence_url"].startswith(
                "https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/"))
            self.assertGreater(len(row["reason"]),30)

    def test_no_three_hour_research_cycle_reselects_same_unusable_file(self):
        for i in range(24):
            instant=(datetime.datetime(2026,10,31,tzinfo=datetime.timezone.utc)
                     +datetime.timedelta(hours=3*i)).isoformat()
            order=build_work_order(BANK,instant,PROFILE,REGISTRY)
            with self.subTest(time=instant):
                self.assertNotIn(order["episode_id"],EXCLUDED)
                self.assertEqual(set(order["excluded_sha_bound_sources"]),EXCLUDED)
                self.assertFalse(order["paid_api_call_permitted"])
                self.assertFalse(order["publish_permitted"])
                self.assertFalse(order["human_approved"])
                self.assertFalse(order["video_completed"])
                self.assertEqual(order["credits_spent"],0)

    def test_changed_page_disables_stale_rejection_instead_of_guessing(self):
        bank=copy.deepcopy(BANK)
        target=next(x for x in bank["candidates"] if x["id"]=="versailles_treaty_1919")
        target["source_page"]="https://commons.wikimedia.org/wiki/File:Versailles_RESCANNED.webm"
        with self.assertRaisesRegex(ValueError,"V133_STALE_REJECTION_SOURCE_CHANGED"):
            build_work_order(bank,"2026-10-31T12:00:00Z",PROFILE,REGISTRY)

    def test_missing_film_sha_or_fake_status_does_not_skip(self):
        for override in ({"film_sha256":"NOT_VERIFIED"},
                         {"audit_status":"SOURCE_PUBLISHED_APPROVED"},
                         {"evidence_url":"https://example.com/untrusted"}):
            registry=copy.deepcopy(REGISTRY)
            registry["rejected"][2].update(override)
            with self.subTest(override=override):
                with self.assertRaisesRegex(ValueError,"V133_REJECTION_EVIDENCE_INVALID"):
                    rejected_source_ids(BANK["candidates"],registry)

    def test_no_sources_remaining_is_gracefully_skipped_not_rendered(self):
        entries=[x for x in BANK["candidates"] if x["id"] in EXCLUDED]
        order=build_work_order({"candidates":entries},
                               "2026-10-31T12:00:00Z",PROFILE,REGISTRY)
        self.assertEqual(order["status"],"SOURCE_REJECTED_ALL_KNOWN")
        self.assertEqual(order["episode_id"],"no_eligible_source")
        self.assertTrue(order["skip_source_acquisition"])
        self.assertFalse(order["paid_api_call_permitted"])
        self.assertFalse(order["publish_permitted"])

    def test_duplicate_rejected_source_entry_aborts_rotation(self):
        registry=copy.deepcopy(REGISTRY)
        registry["rejected"].append(copy.deepcopy(registry["rejected"][2]))
        with self.assertRaisesRegex(ValueError,"V133_REJECTION_UNKNOWN_OR_DUPLICATE_ID"):
            rejected_source_ids(BANK["candidates"],registry)


if __name__=="__main__":
    unittest.main()
