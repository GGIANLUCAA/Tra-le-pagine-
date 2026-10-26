"""Offline checks for the first Oz episode, no APIs, no generation credits."""
import json,re,unittest
from pathlib import Path
from src.oz_assets_20261026 import key,Images
EP=Path("episodes/oz_dorothy_20261026")
class OzTests(unittest.TestCase):
 def test_script_and_plan_are_exactly_aligned(self):
  plan=json.loads((EP/"scene_plan_oz.json").read_text())["scenes"]
  pars=[p.strip() for p in (EP/"testo.txt").read_text().split("\n\n") if p.strip()]
  self.assertEqual(len(plan),len(pars))
  self.assertEqual([row["narration"] for row in plan],pars)
  words=sum(len(x.split()) for x in pars)
  self.assertTrue(230<=words<=700,words)
  self.assertTrue(18<=len(plan)<=32)
  self.assertEqual(len({key(x["source_alt"]) for x in plan}),len(plan))
 def test_asset_identification_uses_exact_label(self):
  parser=Images()
  parser.feed('<img src="images/test.jpg" alt="The Emerald City.">')
  self.assertIn(key("The Emerald City."),parser.items)
  self.assertNotIn(key("The Emerald-City Alternative"),parser.items)
 def test_visuals_are_story_driven_not_count_target(self):
  plan=json.loads((EP/"scene_plan_oz.json").read_text())["scenes"]
  for item in plan:
   self.assertTrue(item["intent"].strip())
   self.assertTrue(item["source_alt"].strip())
   self.assertIn(item["camera_style"],{"locked","slow_scale_up","slow_scale_down","micro_pan"})
 def test_original_social_captions_differ_without_process_notes(self):
  docs=[]
  for platform in ("FACEBOOK","INSTAGRAM","TIKTOK","YOUTUBE"):
   s=(EP/f"POST_{platform}.txt").read_text().strip()
   self.assertGreater(len(s),150)
   self.assertNotIn("zoom",s.lower())
   self.assertNotIn("montaggio",s.lower())
   docs.append(s)
  self.assertEqual(len(set(docs)),4)
if __name__=="__main__":unittest.main()
