import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from artvision_museum_director_v69 import template
from artvision_museum_stage_v70 import plan_stage

def dossier(width,height):
    d=template()
    d["artwork"].update(title="Test painting",artist="Test artist",
       source_url="https://example.org/art",image_sha256="a"*64,
       rights="Test only",width_cm=width,height_cm=height,
       dimensions_source="Fixture only")
    d["gallery"]["architecture_rationale"]="Plausible gallery, not original room"
    d["camera"]["scale_reference"]="door and floor"
    return d

class MuseumStageTests(unittest.TestCase):
    def test_small_artwork_remains_small(self):
        result=plan_stage(dossier(22.8,33.5))
        self.assertEqual(result["status"],"stage_plan_ready")
        self.assertEqual(result["artwork"]["height_cm"],33.5)
        self.assertFalse(result["render_authorized"])
    def test_monumental_artwork_expands_room(self):
        result=plan_stage(dossier(400,250))
        self.assertGreaterEqual(result["gallery"]["minimum_suggested_width_cm"],500)
    def test_frame_estimates_disclosed(self):
        result=plan_stage(dossier(196.2,129.5))
        self.assertEqual(result["frame"]["dimensions_kind"],"estimated_scenography")
    def test_invalid_dossier_blocked(self):
        d=dossier(100,100)
        d["artwork"]["dimensions_source"]=""
        self.assertEqual(plan_stage(d)["status"],"blocked")
    def test_no_change_to_four_slot_plan(self):
        result=plan_stage(dossier(100,100))
        self.assertEqual(result["variants"],["critico_museum","cinema_museum"])

    def test_tiny_print_not_false_monumental(self):
        little=plan_stage(dossier(22.8,33.5))
        canvas=plan_stage(dossier(196.2,129.5))
        self.assertLess(little["storyboard_9_16"]["frame_width_px"],180)
        self.assertGreater(canvas["storyboard_9_16"]["frame_width_px"],500)
        self.assertGreater(little["gallery"]["camera_start_distance_cm"],349)
        self.assertLess(little["frame"]["height_vs_170cm_person_ratio"],.5)
    def test_off_center_frame_not_clipped_in_opening(self):
        d=dossier(196.2,129.5)
        d["camera"]["painting_center_x"]=.8
        d["camera"]["painting_center_y"]=.8
        plan=plan_stage(d)
        left,top,right,bottom=plan["storyboard_9_16"]["opening_frame_bounds_px"]
        self.assertGreaterEqual(left,108)
        self.assertGreaterEqual(top,192)
        self.assertLessEqual(right,972)
        self.assertLessEqual(bottom,1728)
    def test_large_canvas_backing_distance_and_room_depth(self):
        huge=plan_stage(dossier(550,350))
        self.assertGreater(huge["gallery"]["camera_start_distance_cm"],600)
        self.assertGreater(huge["gallery"]["minimum_suggested_depth_cm"],huge["gallery"]["camera_start_distance_cm"])
    def test_render_stays_blocked_after_scale_fix(self):
        self.assertFalse(plan_stage(dossier(22.8,33.5))["render_authorized"])

if __name__=="__main__":
    unittest.main()
