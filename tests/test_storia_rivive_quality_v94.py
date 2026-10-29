import copy,importlib.util,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sp=importlib.util.spec_from_file_location("v94",ROOT/"src/storia_rivive_quality_gate_v94.py")
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
D="a"*64
B="b"*64
C="c"*64
def sample():
 scenes=[]
 for i in range(5):
  scenes.append({"event_id":f"real_source_event_{i+1}","original_source_frame_checked":True,
    "original_frame_sha256":D,
    "objects_and_people_preserved":True,"faces_visible":i<2,
    "source_face_native_width_px":95,
    "actual_photo_image2image_generated":True,
    "face_against_adjacent_original_frames_reviewed":True,
    "eyes_skin_hair_expression_reviewed":True,
    "no_face_swap_or_person_object_hallucinations":True,
    "restored_face_still_sha256":B})
 return {"format":"storia_rivive","quality_policy_version":"V94","production_date":"2026-10-30",
   "episode_id":"test_v94_001","editorial_subject_type":"people_focused",
   "authentic_source_reviewed":True,"copyright_and_territories_checked":True,
   "visual_reference_reviewed":True,"scenes":scenes,
   "full_video_watched_with_audio":True,"full_video_artistically_approved":True,
   "vidu":{"source_crop_complete_subject_checked":True,
      "start_photo_source_fidelity_checked":True,"original_frame_sha256":D,"color_anchor_sha256":B,
      "model":"viduq2-pro-fast","resolution":"720p","duration_s":5,"prompt_sha256":C,
      "prepaid_credits_only":True,"no_purchase_or_recharge":True,"immutable_ledger_reserved_before_POST":True,
      "fresh_live_provider_balance_checked":True,"fresh_live_cost_quote_checked":True,
      "quoted_credits":16,"current_balance_credits":20,"attempts_previously_submitted":0,
      "single_post_no_retry_enforced":True,
      "provider_state":"success","provider_task_id":"1013489806023331840",
      "actual_vidu_mp4_sha256":C,"provider_clip_in_final_master":True,
      "real_clip_duration_s":5.0,"actual_motion_after_color_verified":True,
      "same_faces_people_objects_and_camera_approved":True,
      "no_morphs_or_extra_limbs_approved":True,"full_scene_reviewed_in_motion":True,
      "actual_spent_credits":16,"paid_submission_count":1}}

class TestStoriaV94(unittest.TestCase):
 def test_preflight_approved_bounded_16(self):
  self.assertEqual(m.inspect(sample(),"pre_spend"),[])
 def test_complete_verified_video(self):
  self.assertEqual(m.inspect(sample(),"delivery"),[])
 def test_missing_vidu_block(self):
  a=sample();a.pop("vidu")
  self.assertIn("MANDATORY_VIDU_SCENE_MISSING",m.inspect(a))
 def test_color_only_must_not_pass_modern_face(self):
  a=sample();a["scenes"][0]["actual_photo_image2image_generated"]=False
  self.assertTrue(any("DDCOLOR_ONLY" in x for x in m.inspect(a)))
 def test_source_face_swaps_not_approved(self):
  a=sample();a["scenes"][1]["no_face_swap_or_person_object_hallucinations"]=False
  self.assertTrue(any("FACE_OR_OBJECT_CHANGED" in x for x in m.inspect(a)))
 def test_provider_clip_missing_reject(self):
  a=sample();a["vidu"]["provider_clip_in_final_master"]=False
  self.assertIn("VIDU_GENERATION_NOT_IN_FINAL_VIDEO",m.inspect(a))
 def test_dancer_anchor_cropped_reject_prebill(self):
  a=sample();a["vidu"]["source_crop_complete_subject_checked"]=False
  self.assertIn("VIDU_ANCHOR_CROPS_SUBJECT",m.inspect(a,"pre_spend"))
 def test_bill_cap_prevents_more_than_16(self):
  a=sample();a["vidu"]["quoted_credits"]=25
  self.assertIn("VIDU_CREDITS_OVER_16_CAP_OR_UNQUOTED",m.inspect(a,"pre_spend"))
 def test_no_second_billable_submission(self):
  a=sample();a["vidu"]["attempts_previously_submitted"]=1
  self.assertIn("DUPLICATE_PAID_TASK_NOT_ALLOWED",m.inspect(a,"pre_spend"))
 def test_balance_insufficient(self):
  a=sample();a["vidu"]["current_balance_credits"]=4
  self.assertIn("VIDU_INSUFFICIENT_AVAILABLE_CREDITS",m.inspect(a,"pre_spend"))
 def test_artvision_never_affected(self):
  a=sample();a["format"]="artvision_cinema";a.pop("vidu")
  self.assertEqual(m.inspect(a),[])
 def test_fake_legacy_flag_cannot_bypass(self):
  a=sample();a["legacy_historical_master_readonly"]=True;a.pop("vidu")
  self.assertIn("MANDATORY_VIDU_SCENE_MISSING",m.inspect(a))
 def test_old_legacy_not_modified(self):
  a=sample();a["legacy_historical_master_readonly"]=True;a["quality_policy_version"]="V92";a["production_date"]="2026-10-29";a.pop("vidu")
  self.assertEqual(m.inspect(a),[])

if __name__=="__main__":
 unittest.main()
