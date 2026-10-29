import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from artvision_museum_director_v69 import template,evaluate

class MuseumDirectorTests(unittest.TestCase):
    def valid(self):
        d=template()
        d["artwork"].update(title="The Death of Socrates",artist="Jacques-Louis David",source_url="https://www.metmuseum.org/art/collection/search/436105",image_sha256="a"*64,rights="verify museum reproduction rights",width_cm=196.2,height_cm=129.5,dimensions_source="Met collection record: verify dimensions against exact object")
        d["gallery"]["architecture_rationale"]="Contemporary gallery sized to documented canvas; not asserted to be actual gallery"
        d["camera"]["scale_reference"]="doorway and human eye level, no foreground visitor"
        return d
    def test_planning_only(self):
        r=evaluate(self.valid())
        self.assertEqual(r["status"],"planning_evidence_valid")
        self.assertFalse(r["render_authorized"])
    def test_missing_dimensions_block(self):
        d=self.valid();d["artwork"]["width_cm"]=None
        self.assertEqual(evaluate(d)["status"],"blocked")
    def test_fabricated_original_frame_block(self):
        d=self.valid();d["frame"]["status"]="original_documented"
        self.assertEqual(evaluate(d)["status"],"blocked")
    def test_fake_actual_gallery_block(self):
        d=self.valid();d["gallery"]["status"]="actual_documented"
        self.assertEqual(evaluate(d)["status"],"blocked")
    def test_frame_smaller_than_canvas_block(self):
        d=self.valid();d["frame"].update(outer_width_cm=100,outer_height_cm=100)
        self.assertEqual(evaluate(d)["status"],"blocked")
    def test_noncontinuous_camera_block(self):
        d=self.valid();d["camera"]["continuous_entry_exit"]=False
        self.assertEqual(evaluate(d)["status"],"blocked")

if __name__=="__main__":unittest.main()
