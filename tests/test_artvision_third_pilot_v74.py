import json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from artvision_pilot_guard_v58 import enforce_pilot_project
from artvision_next_render_v55 import choose
S="david_death_of_socrates_met436105_1787"
K="klimt_the_kiss_belvedere912_1908"
H="hokusai_great_wave_met45434_1830"
V=("cinema_standard","cinema_museum","critico_standard","critico_museum")
class ThirdPilotV74(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  for folder in ("config","queue"):(self.root/folder).mkdir()
  lock={"schema":"artvision-pilot-lock-v58","active":True,
        "allowed_title":"The Death of Socrates","allowed_group_id":S,
        "automatic_new_artwork_selection":False,"variant_ids":list(V),
        "authorized_second_pilot":{"enabled":True,"phase":"second_pilot_only_not_automatic_series",
                "allowed_group_id":K,"allowed_title":"The Kiss"},
        "authorized_third_pilot":{"enabled":True,"phase":"third_pilot_only_no_unbounded_series",
                "allowed_group_id":H,"allowed_title":"The Great Wave"}}
  (self.root/"config/artvision_pilot_lock_v58.json").write_text(json.dumps(lock))
  (self.root/"queue/production_v15.json").write_text(json.dumps({"items":[]}))
  self.groups=[{"group_id":S,"artwork":"The Death of Socrates","variants":{v:{"status":"rendered_needs_review"} for v in V}},
   {"group_id":K,"artwork":"The Kiss","variants":{v:{"status":"rendered_needs_review"} for v in V}},
   {"group_id":H,"artwork":"The Great Wave","variants":{v:{"status":"rendered_needs_review" if v.startswith("cinema") else "blocked"} for v in V}}]
  self.save()
 def save(self):(self.root/"queue/artvision_four_variants_s01_20261028.json").write_text(json.dumps({"groups":self.groups}))
 def tearDown(self):self.tmp.cleanup()
 def test_only_three_explicit_works_allowed(self):
  for t in ("The Death of Socrates","The Kiss","The Great Wave"):
   for v in V:enforce_pilot_project({"serial_mode":"artvision_4x1","topic":t,"artvision_4x1_variant":v},self.root)
  for t in ("The Garden of Earthly Delights","Mona Lisa","The Goldfinch"):
   with self.assertRaisesRegex(ValueError,"PILOT LOCK"):
    enforce_pilot_project({"serial_mode":"artvision_4x1","topic":t,"artvision_4x1_variant":"critico_museum"},self.root)
 def test_scheduler_has_two_existing_cinema_and_two_missing_critico(self):
  a=choose(self.root)
  self.assertEqual(a["status"],"third_pilot_in_progress")
  self.assertEqual(a["rendered_count"],2)
  self.assertEqual(a["work"],H)
  self.assertFalse(a["new_fourth_artwork_allowed"])
 def test_exact_four_reviewed_blocks_more_work(self):
  for v in V:self.groups[2]["variants"][v]["status"]="rendered_needs_review"
  self.save();a=choose(self.root)
  self.assertEqual(a["status"],"third_pilot_four_rendered_review_pending")
  self.assertEqual(a["rendered_count"],4)
  self.assertFalse(a["new_fourth_artwork_allowed"])
 def test_concurrent_render_precedence(self):
  (self.root/"queue/production_v15.json").write_text(json.dumps({"items":[{"id":"busy"}]}))
  self.assertEqual(choose(self.root)["status"],"existing_jobs_take_priority")
 def test_socrates_and_klimt_immutable_queue(self):
  self.assertEqual(self.groups[0]["artwork"],"The Death of Socrates")
  self.assertEqual(self.groups[1]["artwork"],"The Kiss")
if __name__=="__main__":unittest.main()
