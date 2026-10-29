import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from artvision_next_render_v55 import choose

class PilotQueueTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        (self.root/"config").mkdir()
        (self.root/"queue").mkdir()
        (self.root/"config/artvision_pilot_lock_v58.json").write_text(json.dumps({
            "schema":"artvision-pilot-lock-v58","active":True,
            "allowed_title":"The Death of Socrates",
            "allowed_group_id":"socrates",
            "variant_ids":["critico_standard","critico_museum","cinema_standard","cinema_museum"],
            "automatic_new_artwork_selection":False}))
        (self.root/"queue/production_v15.json").write_text(json.dumps({"items":[]}))
        (self.root/"queue/artvision_four_variants_s01_20261028.json").write_text(json.dumps({
            "groups":[{"group_id":"socrates","artwork":"The Death of Socrates",
                      "variants":{v:{"status":"blocked"} for v in
                        ("critico_standard","critico_museum","cinema_standard","cinema_museum")}},
                      {"group_id":"other","artwork":"Another Painting","variants":{}}]}))
    def tearDown(self):self.temp.cleanup()
    def test_pilot_overrides_old_new_artwork_recommendation(self):
        out=choose(self.root)
        self.assertEqual(out["status"],"pilot_in_progress")
        self.assertEqual(out["work"],"socrates")
        self.assertFalse(out["new_artwork_required"])
        self.assertEqual(len(out["variants"]),4)

if __name__=="__main__":unittest.main()
