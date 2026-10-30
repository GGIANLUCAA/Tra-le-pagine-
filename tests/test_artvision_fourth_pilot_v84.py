import json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from artvision_pilot_guard_v58 import enforce_pilot_project
from artvision_next_render_v55 import choose
S="david_death_of_socrates_met436105_1787"
K="klimt_the_kiss_belvedere912_1908"
H="hokusai_great_wave_met45434_1830"
B="bosch_garden_earthly_delights_prado_p002823"
V=("cinema_standard","cinema_museum","critico_standard","critico_museum")
class BoschFourthPilotV84(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  for name in ("config","queue"):(self.root/name).mkdir()
  lock={"schema":"artvision-pilot-lock-v58","active":True,"automatic_new_artwork_selection":False,"allowed_group_id":S,"allowed_title":"The Death of Socrates","variant_ids":list(V),
        "authorized_second_pilot":{"enabled":True,"phase":"second_pilot_only_not_automatic_series","allowed_group_id":K,"allowed_title":"The Kiss"},
        "authorized_third_pilot":{"enabled":True,"phase":"third_pilot_only_no_unbounded_series","allowed_group_id":H,"allowed_title":"The Great Wave"},
        "authorized_fourth_pilot":{"enabled":True,"phase":"fourth_pilot_bosch_only","allowed_group_id":B,"allowed_title":"The Garden of Earthly Delights","automatic_fifth_artwork_selection":False}}
  (self.root/"config/artvision_pilot_lock_v58.json").write_text(json.dumps(lock))
  (self.root/"queue/production_v15.json").write_text(json.dumps({"items":[]}))
  self.groups=[{"group_id":id,"artwork":title,"variants":{v:{"status":"rendered_needs_review"} for v in V}} for id,title in [(S,"The Death of Socrates"),(K,"The Kiss"),(H,"The Great Wave"),(B,"The Garden of Earthly Delights")]]
  self.save()
 def save(self):
  (self.root/"queue/artvision_four_variants_s01_20261028.json").write_text(json.dumps({"groups":self.groups}))
 def tearDown(self):self.tmp.cleanup()
 def test_exact_four_user_authorized_only(self):
  for name in ("The Death of Socrates","The Kiss","The Great Wave","The Garden of Earthly Delights"):
   for variant in V:enforce_pilot_project({"serial_mode":"artvision_4x1","topic":name,"artvision_4x1_variant":variant},self.root)
  for name in ("Mona Lisa","The Scream","The Goldfinch","The Fighting Temeraire"):
   with self.assertRaisesRegex(ValueError,"PILOT LOCK"):
    enforce_pilot_project({"serial_mode":"artvision_4x1","topic":name,"artvision_4x1_variant":"critico_standard"},self.root)
 def test_fourth_rendered_does_not_unlock_fifth(self):
  a=choose(self.root)
  self.assertEqual(a["status"],"fourth_pilot_four_rendered_review_pending")
  self.assertEqual(a["work"],B)
  self.assertEqual(a["rendered_count"],4)
  self.assertFalse(a["rendering_allowed"])
  self.assertFalse(a["new_artwork_required"])
  self.assertFalse(a["new_fifth_artwork_allowed"])
 def test_partial_fourth_pilot_stays_same_work(self):
  self.groups[-1]["variants"]["critico_museum"]["status"]="blocked"
  self.save();a=choose(self.root)
  self.assertEqual(a["status"],"fourth_pilot_in_progress")
  self.assertEqual(a["rendered_count"],3)
 def test_one_renderer_at_a_time(self):
  (self.root/"queue/production_v15.json").write_text(json.dumps({"items":[{"id":"busy"}]}))
  self.assertEqual(choose(self.root)["status"],"existing_jobs_take_priority")
 def test_approvals_are_not_invented(self):
  result=choose(self.root)
  self.assertEqual(len(result["variants"]),4)
 def test_exact_queue_master_four_distinct_and_alternate_same_slot(self):
  q=json.loads((ROOT/"queue/artvision_four_variants_s01_20261028.json").read_text())
  b=next(g for g in q["groups"] if g.get("group_id")==B)
  self.assertEqual(set(b["variants"]),set(V))
  sha=[v["rendered_mp4_sha256"] for v in b["variants"].values()]
  self.assertEqual(len(set(sha)),4)
  self.assertTrue(all(isinstance(x,str) and len(x)==64 for x in sha))
  self.assertTrue(all(v["V25_approved"] is False for v in b["variants"].values()))
  self.assertEqual(b["variants"]["critico_standard"]["shared_critico_AAC_sha256"],
                   b["variants"]["critico_museum"]["shared_critico_AAC_sha256"])
  self.assertTrue(b["variants"]["critico_standard"]["reused_historical_reference"])
  self.assertEqual(len(b["variants"]["cinema_standard"]["alternative_rendered_review_mp4s"]),1)
  self.assertEqual(b["actual_rendered_count"],4)
if __name__=="__main__":unittest.main()
