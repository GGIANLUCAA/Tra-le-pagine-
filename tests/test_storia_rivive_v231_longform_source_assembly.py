"""V231: enforce >25 seconds with deliberate outro; never promise a complete 4+1."""
import math,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import storia_rivive_v231_longform_source_assembly as v231

class LongformSourceOnly(unittest.TestCase):
    def test_28_point_5_total_and_nonzero_ending(self):
        self.assertAlmostEqual(v231.DURATION,28.5)
        self.assertGreaterEqual(v231.DURATION,25)
        self.assertLessEqual(v231.DURATION,35)
        self.assertEqual(v231.OUTRO,2.5)
        self.assertEqual(v231.SHOT,5.2)

    def test_real_5_point_2_second_camera_segment(self):
        t=18.0
        start=v231.safe_start(t,[10.0,25.0,40.0],50.0)
        self.assertGreater(start,10.3)
        self.assertLess(start+v231.SHOT,24.7)
        self.assertTrue(start<=t<=start+v231.SHOT)

    def test_short_scene_fails_instead_of_repeating_filler(self):
        with self.assertRaisesRegex(ValueError,"TOO_SHORT"):
            v231.safe_start(13.2,[12.5,16.5],45)

    def test_bad_timestamps_fail(self):
        with self.assertRaisesRegex(ValueError,"INVALID"):
            v231.safe_start(float('nan'),[],35)
        with self.assertRaisesRegex(ValueError,"INVALID"):
            v231.safe_start(-4,[],35)

if __name__=="__main__":
    unittest.main()
