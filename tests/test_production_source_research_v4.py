"""V4 companion tests: use real editorial queue and synthetic safe provider results."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
import production_source_research_v4 as v4
from storia_rivive_autopilot_v101 import build_work_order

CONFIG=json.loads((ROOT/"config/source_cycle_companion_v4.json").read_text())
ART=json.loads((ROOT/"queue/artvision_owner_selected_ten_20261102.json").read_text())
STORY_BANK=json.loads((ROOT/"queue/storia_rivive_candidates_v58.json").read_text())
STORY_PROFILE=json.loads((ROOT/"config/storia_rivive_autopilot_v101.json").read_text())
NOW="2026-11-04T01:05:00Z"

def order(now=NOW):
    return build_work_order(STORY_BANK,now,STORY_PROFILE)

class AutoResearchTests(unittest.TestCase):
    def test_owner_and_story_are_deterministic_in_same_slot(self):
        a=v4.plan("artvision",NOW,CONFIG,queue=ART)
        b=v4.plan("artvision","2026-11-04T01:59:59Z",CONFIG,queue=ART)
        self.assertEqual(a["request_sha256"],b["request_sha256"])
        self.assertEqual(a["owner"],"ARTVISION_OWNER_SELECTED_TEN_V128")
        self.assertNotIn("dali_temptation",a["item_id"])
        self.assertFalse(a["auto_download"])
        self.assertFalse(a["auto_render"])
        self.assertFalse(a["auto_publish"])
        p=v4.plan("storia",NOW,CONFIG,order=order())
        self.assertEqual(p["owner"],"STORIA_RIVIVE_V101_SOURCE_ORDER")
        self.assertEqual(p["official_source_page"],order()["source_page"])
        self.assertEqual(p["request_budget"]["max_results"],1)
        self.assertEqual(p["request_budget"]["max_provider_requests"],2)

    def test_rotate_all_eligible_without_dali_and_no_duplicates(self):
        ids=[]
        for i in range(9):
            when=f"2026-11-{4+(i//8):02}T{(i%8)*3:02}:19:00Z"
            ids.append(v4.plan("artvision",when,CONFIG,queue=ART)["item_id"])
        self.assertEqual(len(set(ids)),9)
        self.assertTrue(all("dali_temptation" not in item for item in ids))

    def test_single_query_yields_pending_not_selected(self):
        p=v4.plan("artvision",NOW,CONFIG,queue=ART)
        row={"provider":p["provider"],"source_reference":"https://commons.wikimedia.org/wiki/File:source",
             "title":"Some source","rights_review":"reviewed",
             "visual_review":"passed","authenticity_review":"reviewed"}
        fake={"items":[row],"api_requests":1}
        adapter=v4.rare if p["provider"] in v4.rare.PROVIDERS else v4.archive
        with patch.object(adapter,"search",return_value=fake) as called:
            result=v4.execute(p)
        called.assert_called_once()
        self.assertEqual(result["status"],"RESEARCH_CANDIDATES_PENDING_REVIEW")
        self.assertEqual(result["approved_assets"],0)
        self.assertEqual(result["paid_api_calls"],0)
        for field in v4.STATUS_PENDING:
            self.assertEqual(result["candidates"][0][field],"pending")
        self.assertIs(result["candidates"][0]["selected"],False)
        self.assertIs(result["candidates"][0]["approved"],False)

    def test_zero_match_and_api_failure_are_honest(self):
        p=v4.plan("storia",NOW,CONFIG,order=order())
        adapter=v4.rare if p["provider"] in v4.rare.PROVIDERS else v4.archive
        with patch.object(adapter,"search",return_value={"items":[],"api_requests":1}):
            report=v4.execute(p)
            self.assertEqual(report["status"],"NO_MATCH")
        with patch.object(adapter,"search",side_effect=v4.archive.old.ResearchError("HTTP 429")):
            report=v4.execute(p)
            self.assertEqual(report["status"],"API_FAILED_NO_RETRY")
            self.assertIn("429",report["error_note"])
            self.assertEqual(report["candidates"],[])

    def test_rejects_expensive_config_and_wrong_owner(self):
        for patch_cfg in ({"paid_calls_allowed":True},
                          {"auto_publish":True},
                          {"max_results_per_cycle":3},
                          {"max_api_calls_per_cycle":10}):
            d=copy.deepcopy(CONFIG);d.update(patch_cfg)
            with self.assertRaises(v4.CycleResearchError):
                v4.plan("artvision",NOW,d,queue=ART)
        bad=copy.deepcopy(ART);bad["owner_automation_id"]="unknown"
        with self.assertRaises(v4.CycleResearchError):
            v4.plan("artvision",NOW,CONFIG,queue=bad)

    def test_storia_mismatch_never_switches_candidate(self):
        wrong=order()
        wrong["cycle_id"]="storia-20261105-0000"
        with self.assertRaisesRegex(v4.CycleResearchError,"cycle"):
            v4.plan("storia",NOW,CONFIG,order=wrong)

    def test_reports_can_be_saved_with_no_media_or_secrets(self):
        p=v4.plan("artvision",NOW,CONFIG,queue=ART)
        with tempfile.TemporaryDirectory() as d:
            dest=Path(d)/"source"/"report.json"
            v4.save_report(dest,p)
            x=json.loads(dest.read_text())
            self.assertEqual(x["status"],"PLANNED_NOT_QUERIED")
            self.assertTrue(x["source_unchanged"])
            self.assertFalse(x["auto_publish"])

    def test_timezones_and_short_input_are_strict(self):
        with self.assertRaises(v4.CycleResearchError):
            v4.utc_slot("2026-11-04T01:00:00")
        with self.assertRaises(v4.CycleResearchError):
            v4.utc_slot("bad")
        d=copy.deepcopy(CONFIG);d["artvision"][next(iter(d["artvision"]))]["provider"]="shotstack"
        with self.assertRaises(v4.CycleResearchError):
            v4.config_checked(d)

if __name__=="__main__":
    unittest.main()
