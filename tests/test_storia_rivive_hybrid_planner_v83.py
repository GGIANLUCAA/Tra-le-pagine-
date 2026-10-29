"""V83 selector regression tests: no provider calls and no false editorial approvals."""
import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from storia_rivive_hybrid_planner_v83 import build_plan,PlanningError
def scene(i,year="1918",vidu=False,photo=True):
 return {"id":f"historic_{i}","place":"PARIS","period":year,
  "source_page":"https://example.org/fictional-training-source/"+str(i),
  "source_footage_id":"fictional-film-asset",
  "source_timecode":i*10,
  "source_frame_hash":format(i+1,"064x"),
  "description":f"fictional scene {i} testing only",
  "rights":{"license":"CC0","jurisdiction_reviewed":False},
  "editorial":{"hook":4.0 if vidu else 3.2,"movement":4.3 if vidu else 3.0,"source_quality":4,
    "photo_fidelity":4,"identity_risk":1,"story_value":4,"continuity":4.2},
  "restored_photo_available":photo,"restored_photo_path":f"fake_scene_{i}.jpg" if photo else None,
  "vidu_possible":vidu,"vidu_clip_path":None,"narrative_roles":{"opening":5,"middle":4,"ending":2},
  "story_order":i}
class HybridPlannerTests(unittest.TestCase):
 def setUp(self):
  self.data={"scenes":[scene(0,"1900",True,False),*[scene(i) for i in range(1,6)]]}
 def test_five_genuine_shots_and_one_vidu(self):
  p=build_plan(self.data)
  self.assertEqual(len(p["chapters"]),5)
  self.assertEqual(sum(x["type"]=="VIDU_MOVING_COLOR_5S" for x in p["chapters"]),1)
  self.assertEqual(sum(x["type"]=="CLASSICAL_REAL_FILM_TO_AI_PHOTO" for x in p["chapters"]),4)
  self.assertEqual(len(set(x["id"] for x in p["chapters"])),5)
  self.assertTrue(p["warn_mixed_eras"])
  self.assertTrue(p["user_approval_required_before_single_Vidu_POST"])
  self.assertEqual(p["new_credits_spent"],0)
  self.assertFalse(p["social_publish_authorized"])
  self.assertEqual(p["recommended_vidu_position"],1)
 def test_no_duplicate_source_shot(self):
  d={"scenes":[dict(x) for x in self.data["scenes"]]}
  d["scenes"][1]["source_timecode"]=d["scenes"][0]["source_timecode"]
  with self.assertRaises(PlanningError):build_plan(d)
 def test_no_vidu_candidate(self):
  d={"scenes":[dict(x) for x in self.data["scenes"]]}
  for x in d["scenes"]:x["vidu_possible"]=False
  with self.assertRaises(PlanningError):build_plan(d)
 def test_only_two_classical_photos_rejected(self):
  d={"scenes":[dict(x) for x in self.data["scenes"]]}
  for x in d["scenes"][3:]:x["restored_photo_available"]=False
  with self.assertRaises(PlanningError):build_plan(d)
 def test_same_era_tag(self):
  d={"scenes":[dict(x) for x in self.data["scenes"]]}
  d["scenes"][0]["period"]="1918"
  p=build_plan(d)
  self.assertTrue(p["same_historical_period"])
  self.assertTrue(p["production_may_proceed_without_period_label"])
 def test_invented_rating_not_accepted(self):
  d={"scenes":[dict(x) for x in self.data["scenes"]]}
  d["scenes"][0]["editorial"]=dict(d["scenes"][0]["editorial"])
  del d["scenes"][0]["editorial"]["source_quality"]
  with self.assertRaises(PlanningError):build_plan(d)
if __name__=="__main__":unittest.main()
