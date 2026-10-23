"""ArtVision cinematic library V23 — offline and deterministic unit checks."""
import json
import tempfile
import unittest
from pathlib import Path

from src.cinematic_director_v23 import load_catalog, plan, motion_check, export_plan

class CinematicDirectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog=load_catalog()

    def test_over_hundred_distinct_practical_techniques(self):
        ts=self.catalog["techniques"]
        self.assertGreaterEqual(len(ts),100)
        self.assertEqual(len(ts),len({x["id"] for x in ts}))
        for x in ts:
            self.assertTrue(x["intention"] and x["application"] and x["avoid"])
            self.assertFalse(x["automatic_effect"])

    def test_fuseli_critico_keeps_static_camera_and_sensible_end(self):
        b={"format":"artvision_critico","artwork":"L'incubo",
           "cinematic_tags":["portrait","dramatic"],
           "beats":[{"speech":"Questa donna sogna. Il demone occupa il petto."}]}
        result=plan(b,self.catalog)
        choices={x["id"] for x in result["selected"]}
        self.assertTrue({"locked_hold","nonforced_ending","camera_seasick_gate","narration_anchor"}<=choices)
        self.assertLessEqual(len(choices),8)
        self.assertTrue(result["requires_real_preview_and_audio_listening"])
        self.assertFalse(result["autopublish"])

    def test_different_formats_have_different_presets(self):
        crit={x["id"] for x in plan({"format":"artvision_critico","artwork":"L'incubo"},self.catalog)["selected"]}
        music={x["id"] for x in plan({"format":"visual_music","artwork":"Notturno"},self.catalog)["selected"]}
        cinema={x["id"] for x in plan({"format":"artvision_cinema","artwork":"La notte"},self.catalog)["selected"]}
        self.assertNotEqual(crit,music)
        self.assertIn("true_onset_sync",music)
        self.assertIn("static_tableau",cinema)
        self.assertNotIn("true_onset_sync",crit)

    def test_oscillation_is_blocked_even_when_low_amplitude(self):
        b={"shots":[{"camera":{"move":"sine","scale_delta_fraction":0.001}}]}
        report=motion_check(b,"artvision_critico",self.catalog["safety"])
        self.assertTrue(any(x["severity"]=="block" for x in report["issues"]))

    def test_critico_overmovement_requires_editorial_review(self):
        b={"shots":[{"camera":{"move":"slow_push","scale_delta_fraction":0.08}},
                    {"camera":{"move":"slow_pan_x","travel_fraction":0.2}},
                    {"camera":{"move":"slow_pull","scale_delta_fraction":.0005}},
                    {"camera":{"move":"locked"}}]}
        result=motion_check(b,"artvision_critico",self.catalog["safety"])
        self.assertTrue(any("Troppi piani mobili" in i["problem"] for i in result["issues"]))
        self.assertTrue(any("Scala" in i["problem"] for i in result["issues"]))
        self.assertTrue(any("Pan" in i["problem"] for i in result["issues"]))

    def test_stable_cam_ok(self):
        b={"beats":[{"camera":{"move":"locked"}},
                    {"camera":{"move":"slow_push","scale_delta_fraction":.004}},
                    {"camera":{"move":"locked"}},
                    {"camera":{"move":"locked"}}]}
        r=motion_check(b,"artvision_critico",self.catalog["safety"])
        self.assertEqual(r["issues"],[])
        self.assertEqual(r["locked"],3)

    def test_eye_trace_large_jump_advises_reset_not_false_certification(self):
        b={"shots":[{"focus_xy":[.1,.2],"framing":"detail"},
                    {"focus_xy":[.88,.82],"framing":"detail"}]}
        r=motion_check(b,"artvision_critico",self.catalog["safety"])
        self.assertEqual(r["eye_trace_points_checked"],2)
        self.assertTrue(any("eye-trace" in x["problem"] for x in r["issues"]))
        self.assertTrue(all(x["severity"]!="block" for x in r["issues"]))
        b["shots"][1]["framing"]="full"
        q=motion_check(b,"artvision_critico",self.catalog["safety"])
        self.assertFalse(any("eye-trace" in x["problem"] for x in q["issues"]))

    def test_unplanned_camera_never_claims_validated(self):
        r=plan({"format":"libri","scenes":[{"narration_anchor":"Quel giorno","description":"La porta si apre"}]},self.catalog)
        self.assertEqual(r["camera_preflight"]["plans_with_camera"],0)
        self.assertFalse(r["camera_preflight"]["real_video_inspected"])
        self.assertTrue(any("Mancano coordinate" in w for w in r["warnings"]))

    def test_no_word_timestamp_inference_from_script(self):
        r=plan({"format":"artvision_critico","beats":[{"speech":"La fragola cade nel fiume"}]},self.catalog)
        self.assertIn("Mancano coordinate", " ".join(r["warnings"]))
        self.assertNotIn("sync_certified",r)

    def test_export_is_additive_and_no_video_generated(self):
        p=plan({"format":"artvision_cinema","artwork":"Guernica"},self.catalog)
        with tempfile.TemporaryDirectory() as root:
            export_plan(p,root)
            path=Path(root)
            self.assertTrue((path/"CINEMATOGRAPHY_PLAN_V23.json").exists())
            self.assertTrue((path/"CINEMATOGRAPHY_NOTE_V23.md").exists())
            self.assertFalse(any(x.suffix==".mp4" for x in path.iterdir()))
            self.assertEqual(json.loads((path/"CINEMATOGRAPHY_PLAN_V23.json").read_text())["number_selected"],len(p["selected"]))

    def test_automatically_included_in_creative_director_v21(self):
        from src.creative_director_v21 import write_package
        brief={"format":"artvision_critico","artwork":"L'incubo",
          "artist":"Johann Heinrich Füssli",
          "beats":[{"speech":"La donna è immobile. L'incubo compare."}],
          "music":{"origin":"external_licensed","title":"Licensed score",
                   "artist":"Composer","source_url":"https://example.com/score",
                   "license_url":"https://creativecommons.org/licenses/by/4.0/",
                   "commercial_allowed":True}}
        with tempfile.TemporaryDirectory() as td:
            r=write_package(brief,Path(td))
            c=Path(td)/"CINEMATOGRAPHY_PLAN_V23.json"
            self.assertTrue(c.is_file())
            self.assertTrue((Path(td)/"CINEMATOGRAPHY_NOTE_V23.md").is_file())
            self.assertEqual(r["cinematography_v23"]["plan_file"],c.name)
            self.assertFalse(r["cinematography_v23"]["automatically_applied"])
            self.assertFalse(r["ready_to_publish"])

    def test_catalog_missing_metadata_rejected(self):
        bad=dict(self.catalog)
        bad["techniques"]=[dict(x) for x in self.catalog["techniques"]]
        bad["techniques"][0]["application"]=""
        with tempfile.TemporaryDirectory() as td:
            file=Path(td)/"bad.json"
            file.write_text(json.dumps(bad),encoding="utf-8")
            with self.assertRaises(ValueError):
                load_catalog(file)

if __name__=="__main__":
    unittest.main()
