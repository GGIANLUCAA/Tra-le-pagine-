"""Offline checks for the Verne story, source captions and editorial identity."""
import json
import unittest
from pathlib import Path
from src.verne_assets_20261027 import captions_from

EP=Path("episodes/nautilus_20261027")

class VerneEpisodeTests(unittest.TestCase):
    def plan(self):
        return json.loads((EP/"scene_plan_verne.json").read_text(encoding="utf-8"))["scenes"]

    def test_story_beats_match_the_original_script(self):
        beats=self.plan()
        parts=[v.strip() for v in (EP/"testo.txt").read_text(encoding="utf-8").split("\n\n") if v.strip()]
        self.assertEqual([x["narration"] for x in beats],parts)
        self.assertTrue(230<=len(" ".join(parts).split())<=700)
        self.assertEqual(len({x["source_image_id"] for x in beats}),len(beats))

    def test_all_images_are_original_and_story_motivated(self):
        for x in self.plan():
            self.assertRegex(x["source_image_id"],r"^im\d{3}$")
            self.assertTrue(x["visual_intent"] and x["justification"])
            self.assertIn(x["camera_style"],("locked","slow_zoom_in","slow_zoom_out","slow_pan_left","slow_pan_right"))

    def test_gutenberg_caption_parser(self):
        page='<div><img alt="" src="images/im029.jpg"><p class="caption" id="a">Une fenêtre ouverte sur ces abîmes. (<a href="#s">Page 103</a>.)</p></div>'
        self.assertIn("fenêtre ouverte",captions_from(page)["im029"])

    def test_social_post_texts_are_distinct_and_no_process_jargon(self):
        posts=[(EP/f"POST_{p}.txt").read_text(encoding="utf-8") for p in ("FACEBOOK","INSTAGRAM","TIKTOK","YOUTUBE")]
        self.assertEqual(len(set(posts)),4)
        for text in posts:
            self.assertGreater(len(text.strip()),250)
            self.assertNotIn("montaggio",text.lower())
            self.assertNotIn("zoom",text.lower())
            self.assertIn("Verne",text)

    def test_scene_count_is_not_a_mandatory_quota(self):
        plan=json.loads((EP/"scene_plan_verne.json").read_text(encoding="utf-8"))
        self.assertNotIn("target_image_count",plan)
        self.assertNotIn("required_duration_seconds",plan)

if __name__=="__main__":
    unittest.main()
