import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from artvision_pilot_guard_v58 import enforce_pilot_project
from artvision_next_render_v55 import choose

KLIMT="klimt_the_kiss_belvedere912_1908"
SOCRATES="david_death_of_socrates_met436105_1787"
VARIANTS=("cinema_standard","cinema_museum","critico_standard","critico_museum")

class KlimtSecondPilotV69Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        for p in ("config","queue"): (self.root/p).mkdir()
        lock={"schema":"artvision-pilot-lock-v58","active":True,
              "allowed_title":"The Death of Socrates","allowed_group_id":SOCRATES,
              "automatic_new_artwork_selection":False,"variant_ids":list(VARIANTS),
              "authorized_second_pilot":{"enabled":True,"phase":"second_pilot_only_not_automatic_series",
                  "allowed_group_id":KLIMT,"allowed_title":"The Kiss","allowed_artist":"Gustav Klimt"}}
        (self.root/"config/artvision_pilot_lock_v58.json").write_text(json.dumps(lock))
        (self.root/"queue/production_v15.json").write_text(json.dumps({"items":[]}))
        (self.root/"queue/artvision_four_variants_s01_20261028.json").write_text(json.dumps({
          "groups":[{"group_id":SOCRATES,"artwork":"The Death of Socrates",
                     "variants":{k:{"status":"rendered_needs_review"} for k in VARIANTS}},
                    {"group_id":KLIMT,"artwork":"The Kiss",
                     "variants":{k:{"status":"planned" if k=="cinema_standard" else "blocked"} for k in VARIANTS}}]}))
    def tearDown(self):self.tmp.cleanup()
    def test_second_pilot_only_authorized(self):
        for title in ("The Death of Socrates","The Kiss"):
            for v in VARIANTS:
                enforce_pilot_project({"serial_mode":"artvision_4x1","topic":title,
                                       "artvision_4x1_variant":v},self.root)
        for title in ("The Great Wave","The Goldfinch","Mona Lisa"):
            with self.assertRaisesRegex(ValueError,"PILOT LOCK"):
                enforce_pilot_project({"serial_mode":"artvision_4x1","topic":title,
                                       "artvision_4x1_variant":"cinema_standard"},self.root)
    def test_scheduler_moves_only_to_klimt(self):
        s=choose(self.root)
        self.assertEqual(s["status"],"second_pilot_preproduction")
        self.assertEqual(s["work"],KLIMT)
        self.assertFalse(s["new_third_artwork_allowed"])
        self.assertEqual(s["rendered_count"],0)
    def test_other_historic_jobs_are_not_converted_to_new_pilot(self):
        s=choose(self.root)
        self.assertEqual(set(s["variants"]),set(VARIANTS))
        self.assertNotEqual(s["work"],SOCRATES)
    def test_existing_job_blocks_concurrent_klimt_render(self):
        (self.root/"queue/production_v15.json").write_text(json.dumps(
            {"items":[{"id":"existing-generic-render"}]}))
        s=choose(self.root)
        self.assertEqual(s["status"],"existing_jobs_take_priority")
    def test_four_klimt_movies_remain_review_only(self):
        qpath=self.root/"queue/artvision_four_variants_s01_20261028.json"
        q=json.loads(qpath.read_text())
        for v in q["groups"][1]["variants"].values():v["status"]="rendered_needs_review"
        qpath.write_text(json.dumps(q))
        s=choose(self.root)
        self.assertEqual(s["status"],"second_pilot_four_rendered_review_pending")
        self.assertEqual(s["approved_count"],0)
        self.assertFalse(s["new_third_artwork_allowed"])

if __name__=="__main__":unittest.main()
