"""Regression for the exact 2026-10-30 GitHub Actions failure.

Main's historical engine used int(stamp[-4:-2]) on YYYYMMDDTHH, which
sliced '0T' and crashed before downloading a CC0 source.
This test targets the isolated WOW LAB branch only.
"""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import engine


class MainWorkflowFailureRegression(unittest.TestCase):
    def test_all_even_utc_slots_rotate_search_without_invalid_literal(self):
        record = {
            "objectID": 400112,
            "isPublicDomain": True,
            "primaryImage": "https://images.metmuseum.org/example.jpg",
            "objectName": "Drawing",
            "medium": "watercolor",
            "title": "A Moth",
        }
        conf = {
            "allowed_artwork_ids": [400112],
            "allow_museum_api_search": True,
            "search_queries": ["moth", "butterfly", "bird"],
        }
        with (patch.object(engine, "discovery_ids", return_value=[]),
              patch.object(engine, "get_json", return_value=record)):
            for day in ("20261030", "20261031", "20261101"):
                for hour in range(0, 24, 2):
                    with self.subTest(day=day, hour=hour):
                        chosen = engine.select_artwork(
                            conf, f"{day}T{hour:02d}", history=[])
                        self.assertEqual(chosen["objectID"], 400112)

    def test_legacy_two_releases_same_slot_reserve_once(self):
        releases = [
            {"tag_name": "wow-lab-sharaku-kabuki-hand-v4-20261030",
             "body": "11.5s, authentic CC0 Met 37358.",
             "published_at": "2026-10-30T12:50:17Z"},
            {"tag_name": "wow-lab-zhu-ling-ink-cat-v4-20261030",
             "body": "Separate Met CC0 art V4 (object ID 36075).",
             "published_at": "2026-10-30T13:05:06Z"},
        ]
        history = engine.parse_wow_release_history(releases)
        self.assertEqual(len(history), 2)
        with self.assertRaisesRegex(RuntimeError, "WOW_LAB_SLOT_ALREADY_RELEASED"):
            engine.ensure_slot_available("20261030T12", history)


if __name__ == "__main__":
    unittest.main()
