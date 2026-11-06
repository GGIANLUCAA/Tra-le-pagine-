"""The one-off sculpture format must not weaken CC0 or media checks."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import engine


class EgyptianCatArtworkTests(unittest.TestCase):
    def setUp(self):
        self.cat = {
            "objectID": 544118,
            "title": "Cat Statuette intended to contain a mummified cat",
            "objectName": "Statuette",
            "medium": "Leaded bronze",
            "classification": "Metalwork",
            "isPublicDomain": True,
            "primaryImage": "https://images.metmuseum.org/CRDImages/eg/original/cat.jpg",
        }

    def test_only_actual_verified_cat_passes(self):
        self.assertTrue(engine.valid_object(self.cat))
        for alteration in (
            {"isPublicDomain": False},
            {"primaryImage": "http://example.com/cat.jpg"},
            {"title": "Bronze bowl"},
            {"medium": "Ceramic"},
            {"objectID": 544119},
        ):
            candidate = {**self.cat, **alteration}
            self.assertFalse(engine.valid_object(candidate), alteration)

    def test_generic_sculpture_stays_rejected(self):
        bronze = {**self.cat, "objectID": 551122, "title": "Other bronze statuette"}
        self.assertFalse(engine.valid_object(bronze))


if __name__ == "__main__":
    unittest.main()
