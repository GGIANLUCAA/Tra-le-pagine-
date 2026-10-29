import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from artvision_museum_camera_v64 import camera_at

POSES=[(2525,1510,1.0),(2600,1450,1.8),(2780,1330,4.7),
       (2770,1310,6.0),(2500,1500,6.1),(3060,1430,6.6),
       (2310,1490,6.4),(2600,1690,6.3),(2730,1300,5.4),
       (2525,1510,1.0)]
STARTS=[i*2.2 for i in range(10)]
DURATION=22.0

class ArtVisionMuseumReturnV64(unittest.TestCase):
    def test_starts_and_ends_in_exact_same_room(self):
        self.assertEqual(camera_at(0,DURATION,STARTS,POSES),POSES[0])
        self.assertEqual(camera_at(DURATION,DURATION,STARTS,POSES),POSES[-1])
    def test_no_reset_at_19_point_8_seconds(self):
        left=camera_at(19.8-.001,DURATION,STARTS,POSES)
        right=camera_at(19.8+.001,DURATION,STARTS,POSES)
        self.assertLess(abs(left[0]-right[0]),2)
        self.assertLess(abs(left[1]-right[1]),2)
        self.assertLess(abs(left[2]-right[2]),0.03)
    def test_strictly_retreats_during_final_two_beats(self):
        times=[17.6+i*.05 for i in range(89)]
        zoom=[camera_at(t,DURATION,STARTS,POSES)[2] for t in times]
        self.assertTrue(all(z0>=z1 for z0,z1 in zip(zoom,zoom[1:])))
    def test_each_interior_joint_is_continuous(self):
        for at in STARTS[1:-1]:
            l=camera_at(at-.001,DURATION,STARTS,POSES)
            r=camera_at(at+.001,DURATION,STARTS,POSES)
            self.assertLess(abs(l[2]-r[2]),.04)
    def test_malformed_camera_fails(self):
        with self.assertRaises(ValueError):camera_at(1,DURATION,STARTS[:-1],POSES)
        with self.assertRaises(ValueError):camera_at(1,DURATION,STARTS,[(0,0,1)]*9+[(0,0,0)])
if __name__=='__main__':unittest.main()
