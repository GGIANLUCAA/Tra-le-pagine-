import importlib.util, json, tempfile, unittest
from pathlib import Path
import cv2
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("selector",ROOT/"src/storia_rivive_source_selector_v69.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class SourceSelectorV69(unittest.TestCase):
    def make(self,where):
        p=Path(where);rng=np.random.default_rng(12)
        sharp=rng.integers(0,256,size=(576,720,3),dtype=np.uint8)
        blur=cv2.GaussianBlur(sharp,(35,35),10)
        a=p/"sharp.png";b=p/"blur.png";cv2.imwrite(str(a),sharp);cv2.imwrite(str(b),blur)
        return a,b
    def shot(self,path,**kwargs):
        return {"id":"historical-scene","rights_territories_checked":True,
            "license":"CC0","true_scan_vs_upscale_checked":True,
            "actuality_not_staged":True,"source_frame_path":str(path),
            "subject_box":[.25,.2,.3,.65],"editorial_wow_0_5":4,**kwargs}
    def test_original_detail_beats_blurry_same_resolution(self):
        with tempfile.TemporaryDirectory() as tmp:
            sharp,blur=self.make(tmp)
            a=m.source_metrics(m.image(sharp))
            b=m.source_metrics(m.image(blur))
            self.assertEqual(a["original_raster_px"],b["original_raster_px"])
            self.assertGreater(a["normalized_detail"],b["normalized_detail"]+.2)
    def test_real_vertical_crop_not_full_horizontal_export(self):
        a=m.source_metrics(np.zeros((576,720,3),np.uint8))
        self.assertEqual(a["usable_vertical_crop_px"],[324,576])
        self.assertEqual(a["crop_source_pixels"],324*576)
    def test_rights_and_original_provenance_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path,_=self.make(tmp)
            v=self.shot(path)
            for changes in ({"rights_territories_checked":False},
                            {"license":"CC BY-NC"},
                            {"true_scan_vs_upscale_checked":False},
                            {"actuality_not_staged":False}):
                candidate={**v,**changes}
                out=m.evaluate({"candidates":[candidate]})
                self.assertFalse(out["results"][0]["eligible"])
    def test_no_restorer_no_final_rank(self):
        with tempfile.TemporaryDirectory() as tmp:
            path,_=self.make(tmp)
            out=m.evaluate({"candidates":[self.shot(path)]})["results"][0]
            self.assertEqual(out["stage"],"SCOUT_ONLY_UNAPPROVED")
            self.assertIsNone(out["after_real_ai_and_human_review_100"])
    def test_cannot_fake_visual_review(self):
        with self.assertRaises(ValueError):
            m.review_score({"faces":5})
    def test_real_ai_candidate_requires_actual_photo_and_correctness(self):
        with tempfile.TemporaryDirectory() as tmp:
            path,_=self.make(tmp)
            review={"actually_compared_by_reviewer":True,"no_new_people":True,
                "faces":4.5,"skin_hair_clothes":4.3,"objects_architecture":4,
                "natural_photograph":4,"same_people_geometry":5,"wow_emotion":4.5}
            result=m.evaluate({"candidates":[self.shot(path,restored_image_path=str(path),
                                                        actual_restoration_review=review)]})["results"][0]
            self.assertEqual(result["stage"],"REVIEWED_AI_CANDIDATE")
            self.assertGreater(result["after_real_ai_and_human_review_100"],0)
            self.assertGreaterEqual(result["structural_similarity"],.99)
            review["same_people_geometry"]=1
            with self.assertRaises(ValueError):
                m.evaluate({"candidates":[self.shot(path,restored_image_path=str(path),
                                                        actual_restoration_review=review)]})
    def test_generator_hallucinated_different_scene_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            sharp,_=self.make(tmp)
            other=Path(tmp)/"other.png"
            cv2.imwrite(str(other),np.zeros((576,720,3),np.uint8)+100)
            review={"actually_compared_by_reviewer":True,"no_new_people":True,
                    "faces":5,"skin_hair_clothes":5,"objects_architecture":5,
                    "natural_photograph":5,"same_people_geometry":5,"wow_emotion":5}
            output=m.evaluate({"candidates":[self.shot(sharp,restored_image_path=str(other),
                actual_restoration_review=review)]})["results"][0]
            self.assertFalse(output["eligible"])
            self.assertIn("geometry",output["why"])
if __name__=="__main__":unittest.main()
