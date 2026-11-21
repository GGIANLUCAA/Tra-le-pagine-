"""No-network ArtVision Eleven v4 pilot tests, zero credits."""
import copy
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "eleven_pilot", ROOT / "src/artvision_eleven_v4_pilot_v1.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class ElevenPilotTests(unittest.TestCase):
    def test_recipe_source_script_and_budget_are_pinned(self):
        q, scenes, text = m.recipe_and_text()
        self.assertEqual(len(scenes), 4)
        self.assertEqual(len(text), 623)
        self.assertLess(len(text), m.MAX_PREVIEW_CREDITS_ESTIMATE)
        self.assertEqual(q["source_art_dimensions"], [3840, 2772])
        self.assertEqual(m.MODEL, "eleven_v4")

    def test_alignment_uses_actual_character_times(self):
        _, chapters, text = m.recipe_and_text()
        chars = list(text)
        alignment = {"characters": chars,
                     "character_start_times_seconds": [i * .06 for i in range(len(chars))],
                     "character_end_times_seconds": [(i + 1) * .06 for i in range(len(chars))]}
        rows = m.chapter_ranges(text, chapters, alignment, len(chars) * .06 + 1)
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[0]["voice_start"], 0.)
        self.assertGreater(rows[1]["voice_start"], rows[0]["voice_end"])
        self.assertGreater(rows[3]["voice_end"], rows[2]["voice_end"])
        self.assertEqual(rows[0]["video_start"], m.INTRO)

    def test_bad_alignment_is_rejected_not_faked(self):
        _, chapters, text = m.recipe_and_text()
        alignment = {"characters": list("not this script"),
                     "character_start_times_seconds": [.1] * 15,
                     "character_end_times_seconds": [.2] * 15}
        with self.assertRaises(ValueError):
            m.chapter_ranges(text, chapters, alignment, 20)

    def test_read_only_account_with_enough_budget(self):
        def fake_api(path, key):
            if "subscription" in path:
                return {"character_count": 3000, "character_limit": 40000, "tier": "starter"}
            if "models" in path:
                return [{"model_id": "eleven_v4", "can_do_text_to_speech": True}]
            return {"voice_id": "voice123456", "name": "Selected narrator", "category": "premade"}
        with patch.object(m, "api_get", side_effect=fake_api):
            info = m.account_read_only("key", "voice123456", 623)
        self.assertEqual(info["workspace_remaining_before"], 37000)
        self.assertFalse(info["credits_hard_cap_guaranteed"])

    def test_account_denies_no_budget_or_unknown_voice(self):
        def fake_api(path, key):
            if "subscription" in path:
                return {"character_count": 990, "character_limit": 1000}
            return {}
        with patch.object(m, "api_get", side_effect=fake_api):
            with self.assertRaises(RuntimeError):
                m.account_read_only("key", "voice123456", 623)

    def test_missing_credentials_cannot_generate(self):
        with patch.object(m, "api_get") as mock:
            with self.assertRaises(RuntimeError):
                m.account_read_only("", "", 623)
            mock.assert_not_called()

    def test_voice_id_is_validated(self):
        with self.assertRaises(ValueError):
            m.account_read_only("secret", "../../etc/passwd", 623)


if __name__ == "__main__":
    unittest.main()
