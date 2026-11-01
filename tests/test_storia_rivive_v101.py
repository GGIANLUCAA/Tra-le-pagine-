#!/usr/bin/env python3
"""Offline V101 tests; no remote network or secrets."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
def load(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/"src"/(name+".py"))
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

auto=load("storia_rivive_autopilot_v101")
flag=load("storia_rivive_flag_title_v101")
scout=load("storia_rivive_scout_v101")
frame_rank=load("storia_rivive_frame_rank_v101")
i2i=load("storia_rivive_i2i_prepare_v102")
PROFILE={"format":"storia_rivive","schedule_hours":3,"paid_calls_allowed":False,"social_autopublish":False}
BANK={"candidates":[
    {"id":"paris_swim_1918","source_page":"https://commons.wikimedia.org/wiki/File:Example.webm","license":"CC0_as_declared","year":1918},
    {"id":"paris_train_1918","source_page":"https://commons.wikimedia.org/wiki/File:Example2.webm","license":"CC0_as_declared","year":1918}
]}

class V101Tests(unittest.TestCase):
    def test_cycle_is_stable(self):
        a=auto.build_work_order(BANK,"2026-10-30T15:01:00Z",PROFILE)
        b=auto.build_work_order(BANK,"2026-10-30T17:59:59Z",PROFILE)
        self.assertEqual(a["cycle_id"],b["cycle_id"])
        self.assertEqual(a["episode_id"],b["episode_id"])
    def test_no_fictional_approval(self):
        a=auto.build_work_order(BANK,"2026-10-30T15:00:00Z",PROFILE)
        self.assertFalse(a["human_approved"])
        self.assertFalse(a["publish_permitted"])
        self.assertEqual(a["credits_spent"],0)
        self.assertTrue(a["blocking_issues"])
    def test_paid_enabled_is_rejected(self):
        with self.assertRaises(ValueError):
            auto.build_work_order(BANK,"2026-10-30T15:00:00Z",{**PROFILE,"paid_calls_allowed":True})
    def test_source_host_allowlist(self):
        x=auto.candidate_issues({"source_page":"https://untrusted.invalid/film.webm"})
        self.assertIn("SOURCE_PAGE_NOT_ALLOWLISTED",x)
        with self.assertRaises(ValueError):scout.metadata("https://untrusted.invalid/file.webm")
    def test_unknown_historical_flag_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                flag.produce({"flag":"US","place":"NEW YORK","year":1906},str(Path(temp)/"bad.png"))
    def test_french_tricolor_render(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"title.png"
            flag.produce({"flag":"FR","place":"PARIS","year":1918},str(p))
            image=Image.open(p)
            self.assertEqual(image.size,(720,1280))
            self.assertEqual(image.getpixel((52,65))[:3],(0,35,149))
            self.assertEqual(image.getpixel((10,10))[3],0)
    def test_quality_rank_does_not_forge_approved_photos(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as temp:
            for i in range(12):
                im=Image.new("RGB",(180,320),(40+i*5,75+i*3,125))
                im.save(Path(temp)/("frame_%02d.png"%i))
            result=frame_rank.rank(temp)
            self.assertEqual(len(result["preselected"]),5)
            self.assertEqual(result["approved_restored_photos"],0)
            self.assertTrue(all(x["approved_for_i2i"] is False for x in result["preselected"]))
    def test_i2i_manifest_locks_five_real_source_frames(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as temp:
            d=Path(temp);(d/"original_frames").mkdir()
            (d/"ORIGINAL_ARCHIVE.webm").write_bytes(b"synthetic test only")
            for i in range(1,6):
                Image.new("RGB",(640,480),(20*i,40,70)).save(d/"original_frames"/("frame_%02d.png"%i))
            order={"contract":"LA_STORIA_RIVIVE_V101_SAFE_AUTOPILOT",
                   "cycle_id":"storia-20261030-1200","episode_id":"beirut_1919_street",
                   "paid_api_call_permitted":False,"publish_permitted":False}
            selection={"status":"FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW",
                       "preselected":[{"filename":"frame_%02d.png"%i} for i in range(1,6)]}
            result=i2i.build(order,selection,d)
            self.assertEqual(len(result["original_frame_jobs"]),5)
            self.assertEqual(result["photos_generated"],0)
            self.assertEqual(result["provider_requests_sent"],0)
            self.assertTrue(all(x["source_sha256"] and x["request_sent"] is False for x in result["original_frame_jobs"]))
    def test_i2i_manifest_blocks_missing_source_frame(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                i2i.build({"contract":"LA_STORIA_RIVIVE_V101_SAFE_AUTOPILOT",
                    "paid_api_call_permitted":False,"publish_permitted":False},
                    {"status":"FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW",
                     "preselected":[{"filename":"frame_%02d.png"%i} for i in range(1,6)]},Path(temp))
    def test_used_candidate_is_not_reselected(self):
        a=auto.build_work_order(BANK,"2026-10-30T15:00:00Z",{**PROFILE,"used_episode_ids":["paris_swim_1918"]})
        self.assertEqual(a["episode_id"],"paris_train_1918")
    def test_exhausted_queue_skips_without_spend(self):
        a=auto.build_work_order(BANK,"2026-10-30T15:00:00Z",{**PROFILE,"used_episode_ids":["paris_swim_1918","paris_train_1918"]})
        self.assertEqual(a["status"],"SOURCE_REJECTED_QUEUE_EXHAUSTED")
        self.assertFalse(a["paid_api_call_permitted"])
        self.assertFalse(a["video_completed"])
    def test_malformed_used_ledger_rejected(self):
        with self.assertRaises(ValueError):
            auto.build_work_order(BANK,"2026-10-30T15:00:00Z",{**PROFILE,"used_episode_ids":"paris_swim_1918"})
    def test_v200_history_holds_incomplete_existing_episode(self):
        bank={"candidates":[*BANK["candidates"],{
            "id":"china_daily_life_1928",
            "source_page":"https://commons.wikimedia.org/wiki/File:China.webm",
            "license":"PUBLIC_DOMAIN","year":1928}]}
        history={"entries":[{"episode_id":"china_daily_life_1928",
                            "status":"rendered_needs_review",
                            "evidence":"docs/LA_STORIA_RIVIVE_CHINA_1928_V107_ESITO_E_GUARDRAIL.md"}]}
        for hour in range(0,24,3):
            result=auto.build_work_order(bank,f"2026-10-30T{hour:02d}:00:00Z",PROFILE,history)
            self.assertNotEqual(result["episode_id"],"china_daily_life_1928")
            self.assertFalse(result["paid_api_call_permitted"])
    def test_v200_history_exhausted_is_safe_for_workflow(self):
        history={"entries":[{"episode_id":x["id"],"status":"assets_pending",
                             "evidence":"docs/LA_STORIA_RIVIVE_V108_MANDATO_AUTOMAZIONE_CREDITI_20261030.md"}
                            for x in BANK["candidates"]]}
        result=auto.build_work_order(BANK,"2026-10-30T15:00:00Z",PROFILE,history)
        self.assertIsNone(result["episode_id"])
        self.assertIsNone(result["title"])
        self.assertEqual(result["status"],"SOURCE_REJECTED_QUEUE_EXHAUSTED")
        self.assertFalse(result["publish_permitted"])
        self.assertFalse(result["paid_api_call_permitted"])
    def test_v200_history_rejects_missing_evidence_and_duplicate(self):
        valid={"episode_id":"paris_swim_1918","status":"rendered_needs_review",
               "evidence":"docs/LA_STORIA_RIVIVE_CHINA_1928_V107_ESITO_E_GUARDRAIL.md"}
        for bad in ({"entries":[{**valid,"evidence":"https://example.invalid/false"}]},
                    {"entries":[valid,valid]},
                    {"entries":[{**valid,"status":"approved_without_review"}]},
                    {"entries":"not_a_list"}):
            with self.subTest(bad=bad),self.assertRaises(ValueError):
                auto.build_work_order(BANK,"2026-10-30T15:00:00Z",PROFILE,bad)
    def test_v200_repository_history_file_is_valid(self):
        history=json.loads((ROOT/"queue"/"storia_rivive_episode_history_v200.json").read_text(encoding="utf-8"))
        self.assertIn("china_daily_life_1928",auto.history_exclusions(history))
        self.assertFalse(any(x.get("status")=="final_approved" for x in history["entries"]))
    def test_v200_cli_exhausted_history_writes_skip_without_media(self):
        with tempfile.TemporaryDirectory() as temp:
            d=Path(temp)
            bank=d/"bank.json";profile=d/"profile.json";history=d/"history.json";out=d/"order.json"
            bank.write_text(json.dumps(BANK),encoding="utf-8")
            profile.write_text(json.dumps(PROFILE),encoding="utf-8")
            history.write_text(json.dumps({"entries":[
                {"episode_id":x["id"],"status":"assets_pending",
                 "evidence":"docs/LA_STORIA_RIVIVE_V108_MANDATO_AUTOMAZIONE_CREDITI_20261030.md"}
                for x in BANK["candidates"]]}),encoding="utf-8")
            p=subprocess.run([sys.executable,str(ROOT/"src"/"storia_rivive_autopilot_v101.py"),
                              "--bank",str(bank),"--profile",str(profile),"--history",str(history),
                              "--now","2026-10-30T15:00:00Z","--out",str(out)],
                             capture_output=True,text=True,check=True)
            data=json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(data["status"],"SOURCE_REJECTED_QUEUE_EXHAUSTED")
            self.assertIsNone(data["episode_id"])
            self.assertEqual(json.loads(p.stdout)["paid_calls"],0)
    def test_v200_cli_missing_history_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            d=Path(temp)
            bank=d/"bank.json";profile=d/"profile.json";out=d/"order.json"
            bank.write_text(json.dumps(BANK),encoding="utf-8")
            profile.write_text(json.dumps(PROFILE),encoding="utf-8")
            p=subprocess.run([sys.executable,str(ROOT/"src"/"storia_rivive_autopilot_v101.py"),
                              "--bank",str(bank),"--profile",str(profile),
                              "--history",str(d/"missing.json"),
                              "--now","2026-10-30T15:00:00Z","--out",str(out)],
                             capture_output=True,text=True)
            self.assertNotEqual(p.returncode,0)
            self.assertFalse(out.exists())
    def test_source_rights_not_self_approved(self):
        a=auto.build_work_order(BANK,"2026-10-30T15:00:00Z",PROFILE)
        self.assertIn("ITALY_AND_RESIDUAL_RIGHTS_NEED_REVIEW",a["blocking_issues"])

if __name__=="__main__":unittest.main()
