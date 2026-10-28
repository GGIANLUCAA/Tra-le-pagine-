import copy,importlib.util,unittest
from pathlib import Path

spec=importlib.util.spec_from_file_location("v64",Path(__file__).resolve().parents[1]/"src/storia_rivive_quality_policy_v64.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def approved():
 return {"format":"storia_rivive","release_preset":"reference_photo_freeze","auto_publish":False,
 "paid_credits_consumed":False,"rights":{"original_license":"CC0"},
 "shots":[{"native_crop_size_px":[1100,1700],"keyframe_provenance_verified":True,
 "moving_archive_scene":True,"frame_source_license_verified":True,
 "masks_preserve_original_people_objects":True,
 "faces":[{"source_short_edge_px":120,"same_person_shape_reviewed":True,"no_age_or_ethnicity_changed":True}],
 "restoration":{"method":"reference_constrained_img2img","visual_face_reconstruction":True,
 "source_guidance_strength_reviewed":True,"model_weights_license_checked":True,
 "native_4k_claim":False,"photo_historically_hypothetical_disclosed":True},
 "quality_review":{"original_v_restored_side_by_side":True,"natural_skin_colors":True,
 "lifelike_eyes_skin_hair":True,"same_people_count":True,"same_pose_clothes_background":True,
 "no_synthetic_face_or_hand_artifacts":True,"actual_100_percent_mobile_crop_approved":True,
 "art_director_approved":True}}]}

class TestV64(unittest.TestCase):
 def test_good_documented_review(self):
  self.assertTrue(m.validate(approved())["eligible_for_reference_grade"])
 def test_v63_style_ESRGAN_is_rejected_even_if_marked_1080p(self):
  p=approved();s=p["shots"][0];s["native_crop_size_px"]=[324,576]
  s["faces"][0]["source_short_edge_px"]=32
  s["restoration"]["method"]="ddcolor_plus_realesrgan_x4"
  z=m.validate(p)
  self.assertEqual(z["status"],"REJECT_PHOTO_FIDELITY")
  self.assertTrue(any("source crop" in i for i in z["failures"]))
  self.assertTrue(any("too small" in i for i in z["failures"]))
  self.assertTrue(any("DDColor" in i for i in z["failures"]))
 def test_pretty_hallucinated_faces_not_approved(self):
  p=approved();s=p["shots"][0]
  s["quality_review"]["same_people_count"]=False
  s["quality_review"]["same_pose_clothes_background"]=False
  z=m.validate(p)
  self.assertFalse(z["eligible_for_reference_grade"])
  self.assertTrue(any("invented" in i for i in z["failures"]))
 def test_no_human_approval_no_claim(self):
  p=approved();p["shots"][0]["quality_review"]["art_director_approved"]=False
  self.assertFalse(m.validate(p)["eligible_for_reference_grade"])
 def test_noncommercial_is_not_pd(self):
  p=approved();p["rights"]["original_license"]="CC BY-NC"
  self.assertFalse(m.validate(p)["eligible_for_reference_grade"])
 def test_fake_4k_and_paid_calls(self):
  p=approved();p["shots"][0]["restoration"]["native_4k_claim"]=True;p["paid_credits_consumed"]=True
  self.assertFalse(m.validate(p)["eligible_for_reference_grade"])

if __name__=="__main__":unittest.main()
