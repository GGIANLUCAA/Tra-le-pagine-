"""V123: conservative no-OCR photographic-content selection checks.

Synthetic images test pixel-structure heuristics only. Real cinema scenes still
require human inspection of the contact sheet and original moving film.
"""
import tempfile
import unittest
from pathlib import Path
from PIL import Image,ImageDraw
from src.storia_rivive_frame_rank_v101 import measure, rank, source_picture_content_guard


class TestV123NoIntertitleI2I(unittest.TestCase):
    def test_dark_intertitle_like_bright_strokes_is_rejected(self):
        img=Image.new("L",(256,256),12)
        d=ImageDraw.Draw(img)
        for i in range(10):
            d.rectangle((40,32+i*19,215,38+i*19),fill=235)
        result=source_picture_content_guard(img)
        self.assertFalse(result["source_picture_content_eligible"])
        self.assertEqual(result["source_picture_content_rejection"],
                         "LIKELY_INTERTITLE_LOGO_OR_BLACK_CARD")

    def test_bright_diagram_like_card_is_rejected(self):
        img=Image.new("L",(256,256),222)
        d=ImageDraw.Draw(img)
        for i in range(5):
            d.line((22,15+i*32,239,45+i*32),fill=10,width=3)
        result=source_picture_content_guard(img)
        self.assertFalse(result["source_picture_content_eligible"])
        self.assertEqual(result["source_picture_content_rejection"],
                         "LIKELY_DIAGRAM_OR_LIGHT_CARD")

    def test_medium_tone_machinery_like_scene_remains_candidate_only(self):
        img=Image.new("L",(256,256),90)
        d=ImageDraw.Draw(img)
        for x in range(20,230,22):
            d.rectangle((x,35,x+8,205),fill=175)
        result=source_picture_content_guard(img)
        self.assertTrue(result["source_picture_content_eligible"])

    def test_ranking_blocks_pure_intertitle_bundle_even_when_high_resolution(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp)
            for k in range(12):
                img=Image.new("RGB",(1280,720),(12,12,12))
                d=ImageDraw.Draw(img)
                for i in range(9):
                    d.rectangle((160,75+i*63,1080,95+i*63),fill=(225,225,225))
                img.save(directory/f"frame_{k:02d}.png")
            result=rank(directory)
            self.assertEqual(result["status"],"INSUFFICIENT_PHOTOGRAPHIC_SCENE_CANDIDATES")
            self.assertEqual(result["preselected"],[])
            self.assertFalse(any(x["source_picture_content_eligible"] for x in result["all_candidates"]))

    def test_selected_images_are_still_marked_unapproved(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp)
            for k in range(12):
                img=Image.new("RGB",(1280,720),(90,92,94))
                d=ImageDraw.Draw(img)
                d.rectangle((100+k*20,80,350+k*20,650),fill=(180,175,170))
                img.save(directory/f"frame_{k:02d}.png")
            result=rank(directory)
            self.assertEqual(len(result["preselected"]),5)
            self.assertTrue(all(not r["approved_for_i2i"] for r in result["preselected"]))
            self.assertTrue(all(not r["historical_shot_distinctness_verified"] for r in result["preselected"]))


if __name__=="__main__":
    unittest.main()
