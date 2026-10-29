"""Blake V77 frame regression: no fake gilt frame on a paper watercolor.
Run with python -m unittest discover -s tests -p test_artvision_blake_frame_v77.py
Synthetic pixels only; NOT artistic approval.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from PIL import Image
import numpy as np
import artvision_blake_visual_v74 as v


class BlakeFrameV77Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.art = Image.new("RGB", (1586, 2000), (70, 100, 132))
        cls.room = Image.new("RGB", (v.W, v.H), (95, 94, 91))

    def test_matting_replaces_old_fake_gold_on_wide_shot(self):
        shot = v.museum(self.art, self.room, 1.0, (.5, .5))
        pixels = np.asarray(shot)
        self.assertEqual(tuple(pixels[550, 312]), (207, 200, 185))
        self.assertFalse(np.all(pixels == np.array([196, 157, 91]), axis=2).any())
        self.assertFalse(np.all(pixels == np.array([112, 83, 46]), axis=2).any())

    def test_source_pixels_fill_detail_view_without_frame_overlay(self):
        shot = v.museum(self.art, self.room, 18.0, (.5, .5))
        self.assertEqual(shot.getpixel((v.W // 2, v.H // 2)), (70, 100, 132))
        self.assertEqual(shot.getpixel((1, v.H // 2)), (70, 100, 132))

    def test_same_room_and_mount_return_in_last_shot(self):
        first = v.museum_frame(self.art, self.room, 0, 51)
        last = v.museum_frame(self.art, self.room, 51, 51)
        self.assertTrue(np.array_equal(np.asarray(first), np.asarray(last)))


if __name__ == "__main__":
    unittest.main()
