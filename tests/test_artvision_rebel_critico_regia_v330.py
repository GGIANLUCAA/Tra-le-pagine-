"""Offline checks for a safe V330 direction remaster, not artistic certification."""
import hashlib
import importlib
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
import artvision_rebel_critico_regia_v330 as m


class BruegelV330DirectionTests(unittest.TestCase):
    def test_same_original_script_and_verifiable_identity(self):
        q,script=m.load()
        self.assertEqual(q["accession"],"584")
        self.assertEqual(len(q["chapters"]),9)
        self.assertEqual(m.ART_SHA,"09f675e7861da808ede4bc1f85573e97884fdbcc6c1d6cb482e3e449d58aace5")
        self.assertIn("Michele",script)
        self.assertEqual(m.FPS,20)

    def test_narrative_crop_real_source_bounds(self):
        art=np.zeros((2772,3840,3),dtype=np.uint8)
        for ix in range(2,8):
            for u in (0.,.2,.5,.8,1.):
                with self.subTest(chapter=ix,u=u):
                    audit={}
                    im=m.shot(art,None,u,audit,chapter_index=ix)
                    self.assertEqual(im.shape,(m.H,m.W,3))
                    b=audit["camera_crop_xyxy"]
                    self.assertTrue(0<=b[0]<b[2]<=1 and 0<=b[1]<b[3]<=1)

    def test_sky_and_fall_are_distinct_camera_targets(self):
        art=np.zeros((2772,3840,3),dtype=np.uint8)
        a,b={},{}
        m.shot(art,None,.5,a,chapter_index=3,part=0)
        m.shot(art,None,.5,b,chapter_index=3,part=1)
        self.assertLess(a["camera_crop_xyxy"][1],b["camera_crop_xyxy"][1])
        self.assertEqual(a["director_reason"],"sky_then_fall")

    def test_no_new_voice_allowed_in_remaster(self):
        with self.assertRaisesRegex(RuntimeError,"never synthesizes"):
            m.voice()

    def test_intro_uses_real_painting_pixels(self):
        rng=np.random.default_rng(22)
        img=rng.integers(5,220,size=(2772,3840,3),dtype=np.uint8)
        frame=m.opening_frame(img,.8)
        self.assertEqual(frame.shape,(m.H,m.W,3))
        self.assertGreater(frame.std(),15)


if __name__=="__main__":
    unittest.main()
