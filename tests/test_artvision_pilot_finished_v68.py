import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from artvision_next_render_v55 import choose

SLOTS=("cinema_standard","cinema_museum","critico_standard","critico_museum")
WORK="david_death_of_socrates_met436105_1787"

class FourRenderedPilotV68Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        (self.root/"queue").mkdir()
        (self.root/"config").mkdir()
        lock={"schema":"artvision-pilot-lock-v58","active":True,
              "allowed_group_id":WORK,"allowed_title":"The Death of Socrates",
              "variant_ids":list(SLOTS),"automatic_new_artwork_selection":False}
        (self.root/"config/artvision_pilot_lock_v58.json").write_text(json.dumps(lock))
        (self.root/"queue/production_v15.json").write_text(json.dumps({"items":[]}))
        self.variants={k:{"status":"rendered_needs_review"} for k in SLOTS}
        self.write_queue()

    def write_queue(self):
        (self.root/"queue/artvision_four_variants_s01_20261028.json").write_text(
            json.dumps({"groups":[{"group_id":WORK,"artwork":"The Death of Socrates",
                                  "variants":self.variants}]}))

    def tearDown(self):self.tmp.cleanup()

    def test_four_mp4s_are_not_approval_and_scheduler_stops(self):
        out=choose(self.root)
        self.assertEqual(out["status"],"pilot_four_rendered_review_pending")
        self.assertEqual(out["rendered_count"],4)
        self.assertEqual(out["approved_count"],0)
        self.assertFalse(out["new_artwork_required"])
        self.assertFalse(out["rendering_allowed"])

    def test_even_four_approvals_do_not_auto_unlock_new_works(self):
        for v in self.variants.values():v["status"]="approved_for_final_delivery"
        self.write_queue()
        out=choose(self.root)
        self.assertEqual(out["status"],"pilot_awaiting_explicit_second_pilot")
        self.assertEqual(out["approved_count"],4)
        self.assertFalse(out["new_artwork_required"])

    def test_existing_partial_pilot_remains_in_progress(self):
        self.variants["critico_museum"]["status"]="blocked_voice_unavailable"
        self.write_queue()
        out=choose(self.root)
        self.assertEqual(out["status"],"pilot_in_progress")
        self.assertFalse(out["new_artwork_required"])

    def test_existing_render_job_takes_precedence(self):
        (self.root/"queue/production_v15.json").write_text(json.dumps({"items":[{"id":"running"}]}))
        out=choose(self.root)
        self.assertEqual(out["status"],"existing_jobs_take_priority")
        self.assertFalse(out["new_artwork_required"])

if __name__=="__main__":
    unittest.main()
