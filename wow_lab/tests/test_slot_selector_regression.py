"""Offline regression for the 2026-11-07 WOW LAB production crash."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import engine


class WowLabSlotSelectorRegression(unittest.TestCase):
    def test_utc_slot_selection_does_not_parse_the_t_separator_as_a_day(self):
        conf = {
            "allowed_artwork_ids": [436535],
            "allow_museum_api_search": True,
            "search_queries": ["portrait", "ship at sea", "black crow"],
        }
        record = {
            "objectID": 436535,
            "isPublicDomain": True,
            "objectName": "Painting",
            "primaryImage": "https://images.metmuseum.org/valid-public-domain-example.jpg",
            "title": "Verified title",
        }
        with patch.object(engine, "discovery_ids", return_value=[]), patch.object(
            engine, "get_json", return_value=record
        ):
            for stamp in ("20261107T08", "20261107T16", "20261109T08", "20261109T10", "20261111T00", "20261111T02", "20261231T22", "20270101T00"):
                with self.subTest(stamp=stamp):
                    selected = engine.select_artwork(conf, stamp, history=[])
                    self.assertEqual(selected["objectID"], 436535)


if __name__ == "__main__":
    unittest.main()
