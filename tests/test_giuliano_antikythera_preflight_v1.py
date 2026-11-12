#!/usr/bin/env python3
"""Offline safety/editorial tests for Giuliano Antikythera preproduction."""
import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
import giuliano_antikythera_preflight_v1 as p

class AntikytheraDirectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.brief=json.loads((ROOT/"research/giuliano_antikythera_v1/BRIEF_AI_DIRECTOR.json").read_text(encoding="utf8"))
    def test_exact_25_scenes_and_short_target(self):
        b=self.brief
        self.assertEqual(len(b["scenes"]),25)
        self.assertEqual(b["target_duration_seconds"],154)
        self.assertFalse(b["human_artistic_approval"])
        self.assertFalse(b["publication_authorized"])
    def test_original_speech_must_match_visual_semantics(self):
        b=copy.deepcopy(self.brief)
        b["scenes"][7]["visual_detail_id"]="altra_scena"
        codes=[x["code"] for x in p.inspect(b)["issues"]]
        self.assertIn("SEMANTIC_MISMATCH",codes)
    def test_no_microflash_allowed(self):
        b=copy.deepcopy(self.brief)
        b["scenes"][0]["end_s"]=.1
        self.assertIn("MICRO_HOLD",[x["code"] for x in p.inspect(b)["issues"]])
    def test_credits_and_provenance_before_render(self):
        b=copy.deepcopy(self.brief)
        r=p.inspect(b,phase="render")
        self.assertFalse(r["ready_for_voice_or_render"])
        self.assertIn("NOT_READY_FOR_RENDER",[x["code"] for x in r["issues"]])
    def test_no_payments_no_fabricated_approval(self):
        r=p.inspect(copy.deepcopy(self.brief))
        self.assertEqual(r["live_multi_model_calls"],0)
        self.assertEqual(r["openrouter_cost_eur"],0)
        self.assertFalse(r["human_approval"])
        self.assertFalse(r["published"])
    def test_main_timings_after_corrections(self):
        r=p.inspect(copy.deepcopy(self.brief))
        self.assertFalse(any(x["code"] in ("TIMELINE_GAP_OR_OVERLAP","DURATION_MISMATCH") for x in r["issues"]))
    def test_fake_publish_permission_is_blocked(self):
        b=copy.deepcopy(self.brief)
        b["publication_authorized"]=True
        self.assertIn("FABRICATED_APPROVAL",[x["code"] for x in p.inspect(b)["issues"]])
if __name__=="__main__":unittest.main()
