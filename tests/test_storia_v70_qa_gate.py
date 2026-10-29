import importlib.util, json, tempfile, unittest
from pathlib import Path
import numpy as np,cv2
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location("gate",ROOT/"src/storia_v70_qa_gate.py")
g=importlib.util.module_from_spec(s);s.loader.exec_module(g)
GOOD={"rights_cleared_for_intended_countries":True,"unaltered_historical_source_verified":True,
"watermark_free":True,"true_source_scan_verified":True,"editorial_visual_reviewed":True,
"human_reconstruction_feasibility_approved":True,
"scene_candidates":[{"time_s":10,"distinct_shot_id":"harbor"},{"time_s":45,"distinct_shot_id":"market"},{"time_s":90,"distinct_shot_id":"street"}]}

class TestV70HistoricalImageGates(unittest.TestCase):
 def test_failing_real_source_is_blocked_before_ai(self):
  report=ROOT/"config/storia_v70_nyc_failed_source.json"
  with self.assertRaisesRegex(RuntimeError,"SOURCE_REJECTED_BEFORE_AI"):g.review_source(report)
 def test_duplicate_shot_ids_fail(self):
  r={**GOOD,"scene_candidates":[{"time_s":10,"distinct_shot_id":"same"},{"time_s":45,"distinct_shot_id":"same"},{"time_s":90,"distinct_shot_id":"same"}]}
  with self.assertRaisesRegex(RuntimeError,"distinct_shots"):g.review_source(r)
 def test_clean_three_independent_shots_can_pass(self):
  self.assertEqual(len(g.review_source(GOOD)),3)
 def test_monochrome_output_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/"bw.png";Image.fromarray(np.repeat(np.linspace(0,255,1024,dtype=np.uint8)[None,:,None],1920,axis=0).repeat(3,axis=2)).save(p)
   with self.assertRaisesRegex(ValueError,"BLACK_AND_WHITE"):g.test_color_photo(p)
 def test_truly_colored_image_can_pass(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/"color.png";a=np.zeros((1920,1080,3),dtype=np.uint8);a[:]=[194,141,95]
   Image.fromarray(a).save(p)
   self.assertGreater(g.test_color_photo(p)["mean_rgb_range"],9)
 def test_no_fake_different_scenes(self):
  with tempfile.TemporaryDirectory() as tmp:
   paths=[]
   rng=np.random.default_rng(12)
   im=rng.integers(0,255,(576,324,3),dtype=np.uint8)
   for i in range(3):
    path=Path(tmp)/(str(i)+".png");cv2.imwrite(str(path),im);paths.append(str(path))
   with self.assertRaisesRegex(RuntimeError,"REPEATED_SIMILAR_SCENE"):g.check_distinct_source_frames(paths)
 def test_real_different_scenes_can_pass(self):
  with tempfile.TemporaryDirectory() as tmp:
   paths=[]
   rng=np.random.default_rng(12)
   for i in range(3):
    path=Path(tmp)/(str(i)+".png")
    im=rng.integers(0,255,(576,324,3),dtype=np.uint8)
    cv2.rectangle(im,(30+i*55,30+i*50),(150+i*30,210+i*65),(220,220,220),thickness=-1)
    cv2.imwrite(str(path),im);paths.append(str(path))
   corr=g.check_distinct_source_frames(paths)
   self.assertEqual(len(corr),3)
if __name__=="__main__":unittest.main()
