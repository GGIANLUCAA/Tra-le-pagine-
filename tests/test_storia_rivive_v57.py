import importlib.util
import unittest
from pathlib import Path
import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("v57", ROOT/"src/storia_rivive_visual_gate_v57.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class ReferenceColorV57(unittest.TestCase):
    def test_sepia_is_not_a_rich_palette(self):
        frame = np.empty((160, 90, 3), dtype=np.uint8)
        frame[:] = (70, 115, 160)  # BGR: warm sepia uniform
        info = m.frame_metrics(frame)
        self.assertLess(info["hue_entropy_bits"], .2)

    def test_multicolor_measured_separately(self):
        frame = np.empty((160, 120, 3), dtype=np.uint8)
        colors = [(35, 35, 180), (90, 150, 60), (170, 95, 35), (20, 175, 180)]
        for i, bgr in enumerate(colors):
            frame[:,i*30:(i+1)*30,:] = bgr
        info = m.frame_metrics(frame)
        self.assertGreater(info["hue_entropy_bits"], 1.5)

    def test_reference_gate_rejects_tint(self):
        info={"width":720,"height":1280,"median_hue_entropy_bits":.11,"p75_hue_entropy_bits":.12}
        errors,_=m.gates(info,"sepia_tint","")
        self.assertTrue(any("seppia" in x.lower() for x in errors))

    def test_false_4k_claim_blocked(self):
        info={"width":1080,"height":1920,"median_hue_entropy_bits":2.8,"p75_hue_entropy_bits":3.0}
        errors,_=m.gates(info,"ddcolor_temporal","ddcolor-cmnet2",claim_4k=True)
        self.assertTrue(any("4K" in x for x in errors))

    def test_1080_multicolor_technical_only(self):
        info={"width":1080,"height":1920,"median_hue_entropy_bits":2.8,"p75_hue_entropy_bits":3.0}
        errors,warnings=m.gates(info,"ddcolor_temporal","ddcolor-cmnet2",claim_4k=False)
        self.assertEqual(errors,[])
        self.assertTrue(warnings)

if __name__ == "__main__":
    unittest.main()
