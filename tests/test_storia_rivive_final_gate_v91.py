import importlib.util
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("v91",ROOT/"src/storia_rivive_final_gate_v91.py")
gate=importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

def good():
    scenes=[]
    for i in range(7):
        scenes.append({"event_id":f"distinct-historic-shot-{i}",
            "source_frame_checked":True,
            "historical_scene_fidelity_approved":True,
            "photo_looks_naturally_restored":True,
            "visual_distinction":f"Scene {i}: a different event with recognizable real people"})
    return {"historic_source_rights_verified":True,
        "actual_frame_to_photo_geometry_verified":True,
        "scenes":scenes,
        "opening_hook_approved":True,
        "strong_ending_approved":True,
        "full_reel_watched_with_audio":True,
        "rhythm_nonrepetitive_approved":True,
        "full_video_human_artistic_approval":True,
        "four_social_posts_present":True,"cover_present":True,"zip_verified":True}

class TestGateV91(unittest.TestCase):
    def test_good_25s_independent_reel(self):
        self.assertEqual(gate.validate(good(),{"duration_s":25,"valid_h264_aac":True}),[])
    def test_bad_short_delivery_after_vidu_rejection(self):
        q=good()
        q["scenes"]=q["scenes"][:4]
        q.update(paid_ai_generation_used=True,paid_ai_scene_rejected=True,
                 paid_ai_scene_removed_from_final=True,
                 material_scene_removed_after_plan=True)
        errs=gate.validate(q,{"duration_s":14.333,"valid_h264_aac":True})
        self.assertTrue(any("short" in x.lower() for x in errs))
        self.assertTrue(any("re-planning" in x or "redesign" in x for x in errs))
        self.assertTrue(any("identity" in x for x in errs))
    def test_short_exception_is_possible_when_well_justified(self):
        q=good()
        q.update(short_form_exception_approved=True,
                short_form_justification="A genuine emotionally complete micro-story with a powerful last revealing frame, no padding.",
                 )
        self.assertEqual(gate.validate(q,{"duration_s":17.8,"valid_h264_aac":True}),[])
    def test_technical_pass_alone_is_not_artistic_approval(self):
        q=good()
        q["full_video_human_artistic_approval"]=False
        q["strong_ending_approved"]=False
        errs=gate.validate(q,{"duration_s":25,"valid_h264_aac":True})
        self.assertTrue(any("artistic" in x for x in errs))
        self.assertTrue(any("ending" in x for x in errs))
    def test_material_scene_removed_requires_replan(self):
        q=good()
        q["material_scene_removed_after_plan"]=True
        errs=gate.validate(q,{"duration_s":24.6,"valid_h264_aac":True})
        self.assertTrue(any("redesign" in x for x in errs))
if __name__=="__main__":
    unittest.main()
