import json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from artvision_pilot_guard_v58 import enforce_pilot_project
from artvision_next_render_v55 import choose
GROUPS=[
("david_death_of_socrates_met436105_1787","The Death of Socrates"),
("klimt_the_kiss_belvedere912_1908","The Kiss"),
("hokusai_great_wave_met45434_1830","The Great Wave"),
("bosch_garden_earthly_delights_prado_p002823","The Garden of Earthly Delights"),
("wright_air_pump_1768","An Experiment on a Bird in the Air Pump")]
V=("cinema_standard","cinema_museum","critico_standard","critico_museum")
class WrightFifthFourByOneV85(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory()
  self.root=Path(self.tmp.name)
  for folder in ("config","queue"):(self.root/folder).mkdir()
  lock={"schema":"artvision-pilot-lock-v58","active":True,
        "allowed_group_id":GROUPS[0][0],"allowed_title":GROUPS[0][1],
        "variant_ids":list(V),"automatic_new_artwork_selection":False,
        "authorized_second_pilot":{"enabled":True,"phase":"second_pilot_only_not_automatic_series",
          "allowed_group_id":GROUPS[1][0],"allowed_title":GROUPS[1][1]},
        "authorized_third_pilot":{"enabled":True,"phase":"third_pilot_only_no_unbounded_series",
          "allowed_group_id":GROUPS[2][0],"allowed_title":GROUPS[2][1]},
        "authorized_fourth_pilot":{"enabled":True,"phase":"fourth_pilot_bosch_only",
          "allowed_group_id":GROUPS[3][0],"allowed_title":GROUPS[3][1],
          "automatic_fifth_artwork_selection":False},
        "authorized_fifth_pilot":{"enabled":True,"phase":"fifth_pilot_wright_only",
          "allowed_group_id":GROUPS[4][0],"allowed_title":GROUPS[4][1],
          "automatic_sixth_artwork_selection":False}}
  (self.root/"config/artvision_pilot_lock_v58.json").write_text(json.dumps(lock))
  (self.root/"queue/production_v15.json").write_text(json.dumps({"items":[]}))
  self.groups=[{"group_id":gid,"artwork":art,
                "variants":{v:{"status":"rendered_needs_review"} for v in V}} for gid,art in GROUPS]
  self._save()
 def _save(self):
  (self.root/"queue/artvision_four_variants_s01_20261028.json").write_text(json.dumps({"groups":self.groups}))
 def tearDown(self):self.tmp.cleanup()
 def test_only_five_productions_allowed(self):
  for gid,title in GROUPS:
   for variant in V:
    enforce_pilot_project({"serial_mode":"artvision_4x1","topic":title,
                           "artvision_4x1_variant":variant},self.root)
  for title in ("The Night Watch","The Nightmare","Mona Lisa","The Fighting Temeraire"):
   with self.assertRaisesRegex(ValueError,"PILOT LOCK"):
    enforce_pilot_project({"serial_mode":"artvision_4x1","topic":title,
                           "artvision_4x1_variant":"cinema_standard"},self.root)
 def test_all_wright_rendered_means_no_sixth_work(self):
  state=choose(self.root)
  self.assertEqual(state["status"],"fifth_pilot_four_rendered_review_pending")
  self.assertEqual(state["work"],GROUPS[4][0])
  self.assertEqual(state["rendered_count"],4)
  self.assertEqual(state["approved_count"],0)
  self.assertFalse(state["rendering_allowed"])
  self.assertFalse(state["new_sixth_artwork_allowed"])
  self.assertFalse(state["new_artwork_required"])
 def test_missing_one_critico_returns_same_fifth_work_not_sixth(self):
  self.groups[-1]["variants"]["critico_museum"]["status"]="blocked"
  self._save()
  state=choose(self.root)
  self.assertEqual(state["status"],"fifth_pilot_in_progress")
  self.assertEqual(state["rendered_count"],3)
  self.assertFalse(state["new_sixth_artwork_allowed"])
 def test_other_render_job_takes_priority(self):
  (self.root/"queue/production_v15.json").write_text(json.dumps({"items":[{"id":"busy"}]}))
  self.assertEqual(choose(self.root)["status"],"existing_jobs_take_priority")
 def test_exact_wright_four_source_hashes_on_repo(self):
  data=json.loads((ROOT/"queue/artvision_four_variants_s01_20261028.json").read_text())
  g=next(x for x in data["groups"] if x["group_id"]==GROUPS[4][0])
  self.assertEqual(set(g["variants"]),set(V))
  sha=[g["variants"][k]["rendered_mp4_sha256"] for k in V]
  self.assertEqual(len(set(sha)),4)
  self.assertTrue(all(len(s)==64 for s in sha))
  self.assertTrue(all(g["variants"][v]["V25_approved"] is False for v in V))
  self.assertEqual(g["variants"]["critico_standard"]["shared_AAC_sha256"],
                   g["variants"]["critico_museum"]["shared_AAC_sha256"])
  self.assertEqual(g["variants"]["cinema_standard"]["rendered_mp4_sha256"],
                   "ec4525c155334a02696bfa05d745005bea3084f178043c9eaf1dca6d7bfe29e2")
  self.assertEqual(g["four_video_pilot"]["real_rendered_slots"],4)
 def test_no_Gold_from_four_existing_reviews(self):
  state=choose(self.root)
  self.assertNotEqual(state["status"],"approved_for_final_delivery")
  self.assertEqual(state["approved_count"],0)
if __name__=="__main__":unittest.main()
