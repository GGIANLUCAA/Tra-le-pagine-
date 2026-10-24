import unittest
from src.artvision_no_ghosting_gate_v1 import check_recipe,check_source

class NoGhostingTests(unittest.TestCase):
    def good(self):
        return {"visual_transition_policy":{"image_opacity":1.0,"max_simultaneous_source_images":1,"frames_with_two_visuals":0},
                "crossfade_seconds":0,"overlap_frames":0,"transition_style":"hard_cut_only",
                "transitions":[{"at":6.0,"type":"geometric_match_cut_no_overlap","overlap_frames":0}]}
    def test_clean_edit(self):self.assertEqual([],check_recipe(self.good()))
    def test_positive_overlay_is_blocked(self):
        x=self.good();x["overlap_frames"]=1;self.assertTrue(check_recipe(x))
    def test_crossfade_is_blocked(self):
        x=self.good();x["crossfade_seconds"]=0.25;self.assertTrue(check_recipe(x))
    def test_alpha_is_blocked(self):
        x=self.good();x["visual_transition_policy"]["image_opacity"]=0.65;self.assertTrue(check_recipe(x))
    def test_frame_with_two_images_is_blocked(self):
        x=self.good();x["visual_transition_policy"]["frames_with_two_visuals"]=1;self.assertTrue(check_recipe(x))
    def test_museum_pov_is_allowed(self):
        x=self.good();x["visual_transition_policy"]["gallery_pov_optional"]=True;self.assertEqual([],check_recipe(x))
    def test_image_blend_source_is_blocked(self):self.assertTrue(check_source("Image.blend(scene1, scene2, 0.5)"))
    def test_opencv_overlay_source_is_blocked(self):self.assertTrue(check_source("cv2.addWeighted(a,1-b,b,b,0)"))
    def test_normal_editor_is_allowed(self):self.assertEqual([],check_source("frame=cv2.warpAffine(room,m,(1080,1920))"))
if __name__=="__main__":unittest.main()
