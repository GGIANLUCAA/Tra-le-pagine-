import importlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from studio_autopilot_v11 import validate_story, crop_to_poster, split_phrases, content_prompt

def good_story():
    sentences=[
        "Il giovane protagonista attraversa un bosco dove i rami nascondono il cielo."
        for _ in range(27)
    ]
    # >230 words for complete story; each sentence starts uppercase.
    script=" ".join(sentences)
    scenes=[{"start_sentence":i*3,"description":"Bosco e luce del mattino",
             "search":"forest sunlight trees"} for i in range(9)]
    return {"narration":script,"scenes":scenes}


class AutopilotV11Tests(unittest.TestCase):
    def test_robust_scene_contract(self):
        story=good_story()
        meta=validate_story(story)
        self.assertEqual(meta["scenes"],9)
        self.assertEqual(meta["sentences"],27)
        self.assertTrue(230<=meta["words"]<=700)

    def test_no_short_or_fake_story(self):
        story=good_story()
        story["narration"]="Una frase soltanto."
        with self.assertRaises(ValueError):validate_story(story)

    def test_scene_order_and_image_criteria(self):
        story=good_story()
        story["scenes"][1]["start_sentence"]=0
        with self.assertRaises(ValueError):validate_story(story)
        story=good_story()
        story["scenes"][2]["search"]=""
        with self.assertRaises(ValueError):validate_story(story)

    def test_italian_prompt_and_no_false_footage(self):
        p=content_prompt("Ricerca","Storia di crescita","fiabe",3)
        self.assertIn("narrativa",p.lower())
        self.assertIn("non dichiarare immagini storiche",p.lower())

    def test_real_jpg_poster_sizes(self):
        image=Image.effect_noise((1100,900),60).convert("RGB")
        poster=crop_to_poster(image)
        self.assertEqual(poster.size,(1080,1920))
        with tempfile.TemporaryDirectory() as td:
            target=Path(td)/"scene.jpg";poster.save(target,quality=94)
            self.assertGreater(target.stat().st_size,35000)

    def test_reject_tiny_images_instead_of_using_placeholder(self):
        im=Image.new("RGB",(40,40),"blue")
        with self.assertRaises(ValueError):crop_to_poster(im)


if __name__=="__main__":
    unittest.main()
