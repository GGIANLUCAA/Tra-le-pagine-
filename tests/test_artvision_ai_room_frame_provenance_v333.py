"""Regressions for V332 frame authenticity and paired Museum asset reuse."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from artvision_ai_room_integrator_v332 import assemble,select_gallery


class TestFrameProvenance(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.base=Path(self.tmp.name)
        self.assets=self.base/"assets";self.assets.mkdir()
        self.paint=self.base/"painting.png"
        self.frame=self.base/"documented_frame.png"
        Image.new("RGB",(400,300),(130,70,30)).save(self.paint)
        Image.new("RGB",(460,360),(120,75,40)).save(self.frame)
        room=self.assets/"room.png"
        Image.new("RGB",(941,1672),(30,40,50)).save(room)
        self.catalog=self.base/"catalog.json"
        self.data={"schema":"artvision-reusable-ai-room-library-v332",
                   "scenes":[{
                       "room_id":"G_TEST","title":"Test",
                       "status":"candidate_ready_for_compositing_review",
                       "frame_in_background":False,
                       "original_generated_filename":"room.png","file_name":"room.png",
                       "sha256":hashlib.sha256(room.read_bytes()).hexdigest(),
                       "safe_wall_box_norm":[.1,.25,.9,.7],
                       "design_camera_distance_cm":600,
                       "projection_horizontal_fov_degrees":38,
                       "mood_tags":["historic"],"library_path":"test"
                   }]*10}
        # Catalog needs 10 scenes; the selector can use a single unique id.
        self.catalog.write_text(json.dumps(self.data))

    def tearDown(self):self.tmp.cleanup()

    def assemble(self,variant,**kwargs):
        return assemble(self.catalog,self.assets,self.paint,self.base/variant,120,90,
                        ["historic"],variant,authentic_frame_photo=self.frame,
                        frame_source_url="https://example.org/photographed-frame",
                        frame_license="CC BY 4.0",**kwargs)

    def test_current_frame_not_mislabelled_original(self):
        img,qa=self.assemble("cinema_museum")
        self.assertEqual(qa["frame_status"],"current_documented")
        self.assertIsNone(qa["original_frame_historical_evidence_url"])
        self.assertFalse(qa["museum_approved"])
        self.assertTrue(img.is_file())

    def test_original_requires_separate_evidence(self):
        with self.assertRaisesRegex(ValueError,"separate verifiable historical provenance"):
            self.assemble("critico_museum",verified_frame_type="original_documented")

    def test_original_with_explicit_evidence_is_still_review(self):
        img,qa=self.assemble("critico_museum",
            verified_frame_type="original_documented",
            original_frame_evidence_url="https://museum.example.org/frame-provenance")
        self.assertEqual(qa["frame_status"],"original_documented")
        self.assertFalse(qa["Gold_V25"])
        self.assertEqual(qa["full_speed_video_qa"],"NOT_PERFORMED")

    def test_editorial_requires_optin(self):
        with self.assertRaisesRegex(ValueError,"editorial fallback approval"):
            assemble(self.catalog,self.assets,self.paint,self.base/"other",120,90,
                     ["historic"],"cinema_museum")

    def test_two_museum_variants_lock_same_room_and_frame(self):
        _,a=self.assemble("cinema_museum")
        _,b=self.assemble("critico_museum")
        self.assertEqual(a["source_gallery"],b["source_gallery"])
        self.assertEqual(a["frame_source_sha256"],b["frame_source_sha256"])
        self.assertEqual(a["source_artwork_sha256"],b["source_artwork_sha256"])
        self.assertEqual(a["geometry"]["frame_pixel_box"],b["geometry"]["frame_pixel_box"])


if __name__=="__main__":unittest.main()
