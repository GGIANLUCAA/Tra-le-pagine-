"""Offline preflight for the Delacroix V169 critic recipe. No rendering or API calls."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECIPE = ROOT / "modules/artvision_critico/production_series/delacroix_sardanapalus_critico_v169.json"
QUEUE = ROOT / "queue/artvision_owner_selected_ten_20261102.json"
REQUEST = ROOT / "requests/artvision/delacroix-sardanapalus-cinema-v168.json"


class TestDelacroixCriticoRecipe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.recipe = json.loads(RECIPE.read_text(encoding="utf-8"))
        cls.queue = json.loads(QUEUE.read_text(encoding="utf-8"))
        cls.cinema = json.loads(REQUEST.read_text(encoding="utf-8"))

    def test_exact_work_and_public_title(self):
        r = self.recipe
        self.assertEqual(r["work_id"], self.cinema["work_id"])
        self.assertEqual(r["public_title"], "The Death of Sardanapalus")
        self.assertEqual(r["accession"], "RF 2346")
        self.assertEqual(r["variant"], "critico_standard")
        self.assertNotIn("Standard", r["public_title"])
        self.assertNotIn("ArtVision", r["public_title"])

    def test_chapters_and_safe_crops(self):
        chapters = self.recipe["chapters"]
        self.assertEqual([c["beat"] for c in chapters], list(range(1, 10)))
        width, height = self.recipe["source_image_expected_pixels"]
        for c in chapters:
            self.assertTrue(c["text"].strip())
            self.assertTrue(c["focus"].strip())
            self.assertTrue(0 <= c["cx"] <= 1 and 0 <= c["cy"] <= 1)
            self.assertTrue(0 < c["crop_height_px"] <= height)
            crop_width = c["crop_height_px"] * 720 / 1280
            self.assertLessEqual(crop_width, width)
        self.assertGreaterEqual(len(" ".join(c["text"] for c in chapters).split()), 150)

    def test_voice_cost_and_museum_gates(self):
        r = self.recipe
        self.assertTrue(r["voice"]["one_call_only"])
        self.assertTrue(r["voice"]["no_paid_api"])
        self.assertTrue(r["voice"]["require_verified_free_tier_before_call"])
        self.assertTrue(r["voice"]["reuse_exact_WAV_for_future_critico_museum"])
        self.assertTrue(r["museum_variant_blocked_without_verified_frame"])
        self.assertTrue(r["existing_cinema_v168_must_not_be_rerendered"])
        self.assertFalse(r["publication_authorized"])

    def test_queue_membership_and_no_dali(self):
        works = [w for w in self.queue["works"] if w["id"] == self.recipe["work_id"]]
        self.assertEqual(len(works), 1)
        self.assertEqual(works[0]["accession"], "RF 2346")
        self.assertNotIn("dali", self.recipe["work_id"].lower())


if __name__ == "__main__":
    unittest.main()
