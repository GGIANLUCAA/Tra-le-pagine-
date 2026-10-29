import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from artvision_pilot_guard_v58 import enforce_pilot_project

class PilotLockTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        (self.root/"config").mkdir()
        (self.root/"config/artvision_pilot_lock_v58.json").write_text(json.dumps({
            "schema":"artvision-pilot-lock-v58","active":True,
            "automatic_new_artwork_selection":False,"allowed_title":"The Death of Socrates",
            "variant_ids":["critico_standard","critico_museum","cinema_standard","cinema_museum"]}))
    def tearDown(self):self.tmp.cleanup()
    def test_all_four_socrates_allowed(self):
        for v in ["critico_standard","critico_museum","cinema_standard","cinema_museum"]:
            enforce_pilot_project({"serial_mode":"artvision_4x1","topic":"The Death of Socrates","artvision_4x1_variant":v},self.root)
    def test_any_new_painting_rejected(self):
        with self.assertRaisesRegex(ValueError,"PILOT LOCK"):
            enforce_pilot_project({"serial_mode":"artvision_4x1","topic":"The Goldfinch","artvision_4x1_variant":"cinema_standard"},self.root)
    def test_invalid_variant_rejected(self):
        with self.assertRaisesRegex(ValueError,"PILOT LOCK"):
            enforce_pilot_project({"serial_mode":"artvision_4x1","topic":"The Death of Socrates","artvision_4x1_variant":"fifth_variant"},self.root)
    def test_other_formats_untouched(self):
        enforce_pilot_project({"format":"libri","topic":"Another Book"},self.root)

if __name__=="__main__":unittest.main()
