import json,sys,tempfile,unittest
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from storia_rivive_v244_real_endpoint_pixel_qa import endpoint_error,inspect

class V244Tests(unittest.TestCase):
    def test_identical_frame_zero_error(self):
        with tempfile.TemporaryDirectory() as d:
            a=Path(d)/"a.png";b=Path(d)/"b.png"
            Image.new("RGB",(640,360),(60,70,80)).save(a)
            Image.new("RGB",(640,360),(60,70,80)).save(b)
            self.assertEqual(endpoint_error(a,b),0)
    def test_large_difference_detected(self):
        with tempfile.TemporaryDirectory() as d:
            a=Path(d)/"a.png";b=Path(d)/"b.png"
            Image.new("RGB",(640,360),"black").save(a)
            Image.new("RGB",(640,360),"white").save(b)
            self.assertGreater(endpoint_error(a,b),200)
    def test_missing_video_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            with self.assertRaisesRegex(ValueError,"VIDEO_MISSING"):
                inspect(root/"none.mp4",root/"none.json",root,root/"out.json")
    def test_reject_bad_threshold(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            with self.assertRaisesRegex(ValueError,"UNSAFE_THRESHOLD"):
                inspect(root/"none.mp4",root/"none.json",root,root/"out.json",threshold=100)
if __name__=="__main__":unittest.main()
