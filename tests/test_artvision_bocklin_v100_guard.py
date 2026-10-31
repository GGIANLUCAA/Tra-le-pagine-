"""Regression tests for exact Böcklin sixth pilot; never release seventh."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from artvision_pilot_guard_v58 import enforce_pilot_project
from artvision_next_render_v55 import choose

SIXTH="bocklin_isle_of_dead_1883_berlin_ng2_80"
FIVE=("wright_air_pump_1768","david_death_of_socrates_met436105_1787",
      "klimt_the_kiss_belvedere912_1908","hokusai_great_wave_met45434_1830",
      "bosch_garden_earthly_delights_prado_p002823")
VARIANTS=("critico_standard","critico_museum","cinema_standard","cinema_museum")

class SixthPilotTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        (self.root/"config").mkdir()
        (self.root/"queue").mkdir()
        lock=json.loads((ROOT/"config/artvision_pilot_lock_v58.json").read_text())
        queue=json.loads((ROOT/"queue/artvision_four_variants_s01_20261028.json").read_text())
        for group in queue["groups"]:
            if group["group_id"] in FIVE:
                for v in VARIANTS:
                    group["variants"][v]["status"]="rendered_needs_review"
        (self.root/"config/artvision_pilot_lock_v58.json").write_text(json.dumps(lock))
        (self.root/"queue/artvision_four_variants_s01_20261028.json").write_text(json.dumps(queue))
        (self.root/"queue/production_v15.json").write_text('{"items":[]}')
    def tearDown(self):
        self.tmp.cleanup()
    def test_only_exact_sixth_work_is_authorized(self):
        for v in VARIANTS:
            enforce_pilot_project({"serial_mode":"artvision_4x1","topic":"Isle of the Dead",
                                   "artvision_4x1_variant":v},self.root)
        with self.assertRaises(ValueError):
            enforce_pilot_project({"serial_mode":"artvision_4x1","topic":"Seventh Painting",
                                   "artvision_4x1_variant":"cinema_standard"},self.root)
    def test_scheduler_honest_preflight(self):
        r=choose(self.root)
        self.assertEqual(r["status"],"sixth_pilot_preflight_pending")
        self.assertEqual(r["work"],SIXTH)
        self.assertEqual(r["rendered_count"],0)
        self.assertFalse(r["rendering_allowed"])
        self.assertFalse(r["new_seventh_artwork_allowed"])
    def test_scheduler_requires_sha_and_unblocked_variant(self):
        qpath=self.root/"queue/artvision_four_variants_s01_20261028.json"
        q=json.loads(qpath.read_text())
        g=next(x for x in q["groups"] if x["group_id"]==SIXTH)
        g["source_sha256_verified"]=True
        qpath.write_text(json.dumps(q))
        self.assertFalse(choose(self.root)["rendering_allowed"])
        g["variants"]["cinema_standard"]["preflight_blockers"]=[]
        g["variants"]["cinema_standard"]["status"]="ready_for_render"
        qpath.write_text(json.dumps(q))
        self.assertTrue(choose(self.root)["rendering_allowed"])
        self.assertEqual(choose(self.root)["status"],"sixth_pilot_in_progress")

if __name__=="__main__":
    unittest.main()
