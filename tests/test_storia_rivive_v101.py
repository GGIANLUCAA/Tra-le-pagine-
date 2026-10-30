#!/usr/bin/env python3
"""Offline V101 tests; no remote network or secrets."""
import importlib.util
import json
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
    def test_source_rights_not_self_approved(self):
        a=auto.build_work_order(BANK,"2026-10-30T15:00:00Z",PROFILE)
        self.assertIn("ITALY_AND_RESIDUAL_RIGHTS_NEED_REVIEW",a["blocking_issues"])

if __name__=="__main__":unittest.main()
