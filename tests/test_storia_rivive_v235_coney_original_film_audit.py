"""No-cost V235 regression: never generate, publish or trust nominal 1080p."""
import sys,tempfile,unittest
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import storia_rivive_v235_coney_original_film_audit as m

class OriginalConey1903Audit(unittest.TestCase):
    def test_twenty_nonrepeated_real_film_timecodes(self):
        self.assertEqual(len(m.FRAME_TIMES),20)
        self.assertEqual(len(set(m.FRAME_TIMES)),20)
        self.assertTrue(all(1.2<=x<=500 for x in m.FRAME_TIMES))
        self.assertEqual(m.EXPECTED_SIZE,198831577)
        self.assertEqual(len(m.EXPECTED_SHA1),40)

    def test_wrong_source_size_never_proceeds(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/"film.webm"
            path.write_bytes(b"wrong source")
            with self.assertRaisesRegex(ValueError,"SOURCE_MISSING_OR_SIZE_CHANGED"):
                m.verify_film(path)

    def test_colorized_or_other_color_video_is_not_bw_source(self):
        with tempfile.TemporaryDirectory() as t:
            img=Path(t)/"sample.png"
            Image.new("RGB",(1920,1080),(120,120,120)).save(img)
            qa=m.assess_frame(img)
            self.assertLess(qa["mean_channel_spread"],1)
            self.assertIs(qa["face_fidelity_assessed"],False)
            self.assertIs(qa["optical_resolution_certified"],False)
            Image.new("RGB",(1920,1080),(250,20,20)).save(img)
            with self.assertRaisesRegex(ValueError,"NOT_MONOCHROME"):
                m.assess_frame(img)

if __name__ == "__main__":
    unittest.main()
