"""V76 Bosch-only fourth pilot regression: previous masters, no fifth, no extra owner."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from artvision_pilot_guard_v58 import enforce_pilot_project
from artvision_next_render_v55 import choose

VARIANTS=("critico_standard","critico_museum","cinema_standard","cinema_museum")
S="rendered_needs_review"
B="The Garden of Earthly Delights"
G="bosch_garden_earthly_delights_prado_p002823"

class BoschScopedFourthTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory()
        self.root=Path(self.t.name)
        for p in ("config","queue"):(self.root/p).mkdir()
        lock={"schema":"artvision-pilot-lock-v58","active":True,
            "allowed_group_id":"socrates","allowed_title":"The Death of Socrates",
            "automatic_new_artwork_selection":False,
            "variant_ids":list(VARIANTS),
            "authorized_second_pilot":{"enabled":True,"phase":"second_pilot_only_not_automatic_series",
                "allowed_group_id":"klimt","allowed_title":"The Kiss"},
            "authorized_third_pilot":{"enabled":True,"phase":"third_pilot_only_no_unbounded_series",
                "allowed_group_id":"hokusai","allowed_title":"The Great Wave"},
            "authorized_fourth_pilot":{"enabled":True,"phase":"fourth_pilot_bosch_only",
                "allowed_group_id":G,"allowed_title":B,"automatic_fifth_artwork_selection":False}}
        (self.root/"config/artvision_pilot_lock_v58.json").write_text(json.dumps(lock))
        groups=[]
        for gid,title,status in (("socrates","The Death of Socrates",S),
                                  ("klimt","The Kiss",S),("hokusai","The Great Wave",S),
                                  (G,B,"planned")):
            groups.append({"group_id":gid,"artwork":title,
                           "variants":{v:{"status":status} for v in VARIANTS}})
        (self.root/"queue/artvision_four_variants_s01_20261028.json").write_text(json.dumps({"groups":groups}))
        (self.root/"queue/production_v15.json").write_text(json.dumps({"items":[]}))
    def tearDown(self):self.t.cleanup()
    def test_exact_four_variants_bosch_allowed(self):
        for v in VARIANTS:
            enforce_pilot_project({"serial_mode":"artvision_4x1","topic":B,
                "artvision_4x1_variant":v},self.root)
    def test_other_artworks_still_blocked(self):
        for title in ("The Goldfinch","A Fifth Painting","The Garden of Earthly Delights II"):
            with self.assertRaisesRegex(ValueError,"PILOT LOCK"):
                enforce_pilot_project({"serial_mode":"artvision_4x1","topic":title,
                    "artvision_4x1_variant":"cinema_standard"},self.root)
    def test_bad_fourth_phase_fails_closed(self):
        p=self.root/"config/artvision_pilot_lock_v58.json"; j=json.loads(p.read_text())
        j["authorized_fourth_pilot"]["phase"]="unbounded_series";p.write_text(json.dumps(j))
        with self.assertRaisesRegex(ValueError,"PILOT LOCK"):
            enforce_pilot_project({"serial_mode":"artvision_4x1","topic":B,
                "artvision_4x1_variant":"cinema_standard"},self.root)
    def test_choose_bosch_only_after_three_pilots_four_each(self):
        result=choose(self.root)
        self.assertEqual(result["status"],"fourth_pilot_in_progress")
        self.assertEqual(result["work"],G)
        self.assertEqual(result["rendered_count"],0)
        self.assertFalse(result["new_fifth_artwork_allowed"])
    def test_existing_job_blocks_render_selection(self):
        p=self.root/"queue/production_v15.json"
        p.write_text(json.dumps({"items":[{"id":"other_owner_active"}]}))
        self.assertEqual(choose(self.root)["status"],"existing_jobs_take_priority")
    def test_fourth_not_enabled_reverts_third_review(self):
        p=self.root/"config/artvision_pilot_lock_v58.json"; j=json.loads(p.read_text())
        j["authorized_fourth_pilot"]["enabled"]=False;p.write_text(json.dumps(j))
        self.assertEqual(choose(self.root)["status"],"third_pilot_four_rendered_review_pending")
    def test_non_artvision_formats_untouched(self):
        enforce_pilot_project({"serial_mode":"storia_rivive","topic":"Test"},self.root)

if __name__=="__main__":unittest.main()
