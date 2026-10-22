import copy
import json
import unittest
from pathlib import Path
from src.artvision_editor_v19 import check, outputs

EXAMPLE=json.loads(Path("templates/ARTVISION_JOHN_MARTIN_V19.json").read_text(encoding="utf-8"))

class TestArtvisionV19(unittest.TestCase):
    def test_john_martin_editorial(self):
        report,plan,caption,rights=outputs(EXAMPLE)
        self.assertEqual(report["status"],"editorial_review_required")
        self.assertFalse(report["video_modified"])
        self.assertIn("Licenza:",caption)
        self.assertIn("The Last Judgement",rights)
        self.assertIn("Piano di regia",plan)

    def test_repeated_movement_is_warning(self):
        case=copy.deepcopy(EXAMPLE)
        for shot in case["scenes"][:3]:shot["move"]="push_in"
        self.assertTrue(any("tre movimenti" in x for x in check(case)[1]))

    def test_missing_music_license_is_blocker(self):
        case=copy.deepcopy(EXAMPLE)
        case["music"]["license_url"]=""
        self.assertTrue(check(case)[0])

    def test_text_after_intro_not_allowed_cinema(self):
        case=copy.deepcopy(EXAMPLE)
        case["scenes"][1]["on_screen_text"]="Segui la pagina"
        self.assertTrue(any("Cinema V6" in x for x in check(case)[0]))

if __name__=="__main__":unittest.main()
