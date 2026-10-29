import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from artvision_museum_frame_focus_v73 import frame_visibility_at, focus_storyboard
from artvision_recipe_v68 import load_preset
from artvision_museum_pipeline_v71 import build,load_json
D=ROOT/"docs/productions/2026-10-29-socrates-pilot-v68/MUSEUM_DIRECTOR_DOSSIER_V71.json"

class MuseumV73Tests(unittest.TestCase):
    def test_editorial_scope_and_audio_safety(self):
        p=load_preset()
        self.assertLess(p["defaults"]["critico_pair"]["target_words"],365)
        self.assertTrue(p["defaults"]["critico_pair"]["editorial_voice_v73"]["existing_socrates_audio_immutable"])
        self.assertTrue(p["invariants"]["shared_critico_script_and_exact_wav_sha256"])
    def test_frame_exits_during_detail_and_returns(self):
        p=build(load_json(D))
        for slot in ("critico_museum","cinema_museum"):
            marks=p["museum_camera"][slot]["frame_visibility_v73"]
            self.assertTrue(marks[0]["frame_border_visible"])
            self.assertTrue(any(not x["frame_border_visible"] for x in marks[1:-1]))
            self.assertTrue(marks[-1]["frame_border_visible"])
    def test_no_fake_erasure_or_source_change(self):
        p=build(load_json(D))
        for slot in ("critico_museum","cinema_museum"):
            for mark in p["museum_camera"][slot]["frame_visibility_v73"]:
                self.assertTrue(mark["source_artwork_immutable"])
                self.assertEqual(mark["render_action"],"camera_only_no_fake_frame_erasure")
    def test_other_variants_unmodified_and_no_render(self):
        p=build(load_json(D))
        self.assertFalse(p["controls"]["render_authorized"])
        self.assertFalse(p["four_slots"]["critico_standard"]["museum_plan"])
        self.assertFalse(p["four_slots"]["cinema_standard"]["museum_plan"])
    def test_invalid_frame_bounds_rejected(self):
        with self.assertRaises(ValueError):
            frame_visibility_at(0,30,[0,5,10],[(.5,.5,1),(.5,.5,2),(.5,.5,1)],frame_half_width=0)
if __name__=="__main__":
    unittest.main()
