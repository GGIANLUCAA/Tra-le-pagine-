"""V96 regressions: force all previously repeated defects to fail before a final MP4 is delivered.
Tests never call Vidu, don't synthesize image, and don't falsely assert actual human approval.
"""
import copy,pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"src"))
from storia_rivive_v96_guard import inspect


def valid_manifest():
    scenes=[]
    pos=0.0
    for n in range(4):
        d=3.75
        scenes.append({
            "kind":"classic_photo","start_s":pos,"duration_s":d,
            "source":{"film_sha256":format(50+n,"064x"),
                "exact_frame_sha256":format(60+n,"064x"),
                "source_timecode_s":10.0+n*35,"shot_real_film_moving":True},
            "original_people_objects_checked":True,
            "photo":{"color_photo_sha256":format(70+n,"064x"),
                "method":"real_image_to_image_photographic_restoration",
                "same_real_source_frame_and_geometry":True,
                "human_photographic_quality_approved":True,
                "all_faces_objects_identity_verified":True,
                "eyes_skin_hair_and_expression_checked":True,
                "adjacent_archival_frames_identity_checked":True,
                "useful_native_face_width_px":86},
            "bw_motion_s":1.3,"reveal_s":.35,"color_photo_hold_s":2.10,
            "faces_visible":n==0
        })
        pos+=d
    scenes.append({
        "kind":"vidu_motion","start_s":15.0,"duration_s":6.0,
        "source":{"film_sha256":"a"*64,"exact_frame_sha256":"b"*64,
                  "source_timecode_s":225,"shot_real_film_moving":True},
        "original_people_objects_checked":True,
        "vidu":{"actual_videofile_sha256":"c"*64,"task_id":"1013629164059643904",
              "provider_state":"success","paid_post_count":1,"credits_spent":16,
              "start_real_original_bw_motion_present":True,"original_bw_motion_s":1.0,
              "generated_live_video_s":5.0,"color_reveal_by_s":1.0,
              "real_motion_in_color_after_reveal":True,
              "first_vidu_frame_matches_same_real_source_shot":True,
              "no_people_or_object_morphs_reviewed":True,
              "photo_and_vidu_palette_visually_matched":True,
              "full_five_second_video_reviewed":True}
    })
    return {"format":"storia_rivive","quality_policy_version":"V96",
            "project_format":"4classic_1vidu","episode_id":"test-not-a-real-video",
            "copyright_italy_checked":True,
            "source_visual_reference_compared":True,
            "full_video_watched_with_audio":True,"artistic_final_approved":True,
            "four_posts_cover_and_zip_verified":True,"music_continuous_no_interruptions":True,
            "titles":{"faces_hands_main_objects_unobscured":True,
                      "opaque_background_frame_fraction":.04,"appears_s":.2},
            "scenes":scenes}


class GateTests(unittest.TestCase):
    def test_good_structural_example_not_actual_video(self):
        errs,_=inspect(valid_manifest(),actual_duration=21.0)
        self.assertEqual(errs,[])

    def test_photo_with_ddcolor_only_rejected(self):
        d=valid_manifest()
        d["scenes"][1]["photo"]["method"]="DDColor_only"
        self.assertIn("SCENE_2_DDCOLOR_ONLY_IS_NOT_PHOTOGRAPHIC_RESTORATION",
                      inspect(d)[0])

    def test_no_one_can_call_computer_qa_human_approval(self):
        d=valid_manifest()
        d["full_video_watched_with_audio"]=False
        d["artistic_final_approved"]=False
        failures,_=inspect(d)
        self.assertIn("FINAL_FILM_NOT_WATCHED_WITH_AUDIO",failures)
        self.assertIn("HUMAN_ARTISTIC_FINAL_APPROVAL_NOT_PRESENT",failures)

    def test_overlong_freeze_rejected(self):
        d=valid_manifest()
        d["scenes"][1]["color_photo_hold_s"]=3.5
        d["scenes"][1]["duration_s"]=5.15
        self.assertIn("SCENE_2_PHOTO_HOLD_TOO_LONG_OR_TOO_SHORT",inspect(d)[0])

    def test_missing_original_bw_before_vidu_rejected(self):
        d=valid_manifest()
        d["scenes"][4]["vidu"]["start_real_original_bw_motion_present"]=False
        d["scenes"][4]["vidu"]["original_bw_motion_s"]=0
        self.assertIn("SCENE_5_VIDU_MUST_BEGIN_WITH_REAL_ORIGINAL_BW_FILM",inspect(d)[0])
        self.assertIn("SCENE_5_VIDU_MISSING_SAME_SHOT_ARCHIVAL_BW_MOTION",inspect(d)[0])

    def test_wrong_cut_scene_no_source_match(self):
        d=valid_manifest()
        d["scenes"][4]["vidu"]["first_vidu_frame_matches_same_real_source_shot"]=False
        self.assertIn("SCENE_5_VIDU_ABRUPTLY_JUMPS_TO_A_DIFFERENT_SCENE",inspect(d)[0])

    def test_mismatched_color_grade(self):
        d=valid_manifest()
        d["scenes"][4]["vidu"]["photo_and_vidu_palette_visually_matched"]=False
        self.assertIn("SCENE_5_ORANGE_PALETTE_OR_LIGHTING_MISMATCH_WITH_PHOTOS",inspect(d)[0])

    def test_large_black_title_covers_people(self):
        d=valid_manifest()
        d["titles"]["opaque_background_frame_fraction"]=.13
        d["titles"]["faces_hands_main_objects_unobscured"]=False
        errs,_=inspect(d)
        self.assertIn("TITLE_OPAQUE_BAND_EXCEEDS_8_PERCENT",errs)
        self.assertIn("TITLE_OBSCURES_PEOPLE_OR_OBJECTS",errs)

    def test_only_four_real_restorations_and_one_vidu(self):
        d=valid_manifest()
        d["scenes"][2]["kind"]="vidu_motion"
        errs,_=inspect(d)
        self.assertIn("FOUR_REAL_SOURCE_TO_PHOTO_CYCLES_REQUIRED",errs)
        self.assertIn("EXACTLY_ONE_REAL_VIDU_MOVING_SCENE_REQUIRED",errs)

    def test_repeated_source_shot_not_counted_twice(self):
        d=valid_manifest()
        d["scenes"][1]["source"]["source_timecode_s"]=d["scenes"][0]["source"]["source_timecode_s"]
        d["scenes"][1]["source"]["film_sha256"]=d["scenes"][0]["source"]["film_sha256"]
        self.assertIn("SCENE_2_REPEATS_PREVIOUS_SOURCE_SHOT",inspect(d)[0])

    def test_missing_timeline_cannot_claim_success(self):
        d=valid_manifest()
        d.pop("scenes")
        self.assertIn("SCENE_BY_SCENE_TIMELINE_MISSING",inspect(d)[0])

    def test_actual_v91_final_gate_invokes_v96_and_rejects_ddcolor(self):
        import importlib.util
        gate_path=pathlib.Path(__file__).resolve().parents[1]/"src"/"storia_rivive_final_gate_v91.py"
        spec=importlib.util.spec_from_file_location("combined_final_gate_v91",gate_path)
        mod=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        d=valid_manifest()
        d["quality_policy_version"]="V94"
        d["production_date"]="2026-10-30"
        d["scenes"][0]["photo"]["method"]="DDColor_only"
        failures=mod.validate(d,{"duration_s":21.0,"valid_h264_aac":True})
        self.assertTrue(any("V96: SCENE_1_DDCOLOR_ONLY_IS_NOT_PHOTOGRAPHIC_RESTORATION" in e for e in failures),failures)
        self.assertTrue(any("V94" in e for e in failures),failures)

    def test_real_old_v95_review_data_does_not_pass(self):
        d={"production":"New York 1911 V95","format":"storia_rivive",
           "status":"TECHNICAL_RENDER_VISUAL_REVIEW_PENDING",
           "duration_s":29.067,"photo_reconstruction_level":"DDColor neural color original 4 historical shots, does NOT qualify as full photoreal face restoration",
           "rights_italy":"PENDING_REVIEW","full_V94_artistically_approved":False}
        err,_=inspect(d)
        self.assertIn("V96_QUALITY_POLICY_NOT_ENFORCED",err)
        self.assertIn("SCENE_BY_SCENE_TIMELINE_MISSING",err)
        self.assertIn("HUMAN_ARTISTIC_FINAL_APPROVAL_NOT_PRESENT",err)


if __name__=="__main__": unittest.main()
