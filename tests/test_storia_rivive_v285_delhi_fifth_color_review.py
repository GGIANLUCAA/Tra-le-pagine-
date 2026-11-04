import sys,unittest,json,tempfile
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import storia_rivive_v285_delhi_fifth_color_review as m

class V285(unittest.TestCase):
    def test_no_false_vidu_acceptance_and_original_frame_hash(self):
        self.assertEqual(m.FIFTH_FRAME_SHA,m.v281.FRAME_HASHES[4])
        self.assertEqual(m.FIFTH_CROP,750)
        self.assertGreater(m.FIFTH_TIME,200)
    def test_reject_unknown_fifth_photo_before_render(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t); frame=p/"frame_12.png";Image.new("RGB",(1920,1080),"gray").save(frame)
            photo=p/"test.jpg";Image.new("RGB",(720,1280),"gray").save(photo)
            report=p/"manifest.json"
            report.write_text(json.dumps({
              "original_source_frame_sha256":m.FIFTH_FRAME_SHA,
              "original_time_s":m.FIFTH_TIME,
              "original_crop_bbox_px":[750,0,1358,1080],
              "generated_photo_sha256":m.FIFTH_SHA,
              "scene5_photo_generated":True,
              "auto_preflight_passed":True,
              "five_second_vidu_clip_generated":False,
              "scene5_photo_artistically_approved":False,
              "italian_rights_approved":False,
              "publication_allowed":False,
              "generated_photo_filename":"test.jpg"}))
            with self.assertRaisesRegex(ValueError,"REAL_IMAGE_HASH_MISMATCH"):
                m.assert_fifth(p,report,frame)
    def test_no_fake_vidu_source_code(self):
        import inspect
        source=inspect.getsource(m.render)
        self.assertIn('real_vidu_required_to_finish":True',source)
        self.assertIn('"vidu_animated_clips":0',source)
        self.assertIn('"approved_finished_episodes":0',source)

if __name__=="__main__":unittest.main()
