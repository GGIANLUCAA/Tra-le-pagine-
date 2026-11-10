"""V321: compare real five ArtVision narratives without rerendering or spending."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
import editorial_series_naturalness_v321 as audit

RECIPES=[
 "bruegel_rebel_angels_v144.json",
 "simberg_garden_v146.json",
 "bruegel_triumph_v151.json",
 "waterhouse_magic_circle_v159.json",
 "blake_ghost_flea_v159.json",
]
RENDERERS=[
 "artvision_rebel_critico_standard_v144.py",
 "artvision_simberg_garden_critico_v146.py",
 "artvision_bruegel_triumph_critico_v151.py",
 "artvision_waterhouse_magic_circle_critico_v159.py",
 "artvision_blake_ghost_flea_critico_v159.py",
]


class CrossEpisodeAuditTests(unittest.TestCase):
    def test_real_five_recipes_report_prior_style_without_overwriting(self):
        paths=[ROOT/"modules"/"artvision_critico"/"production_series"/x for x in RECIPES]
        renderers=[ROOT/"src"/x for x in RENDERERS]
        before=[p.read_bytes() for p in paths]
        report=audit.inspect_paths(paths,renderers)
        self.assertEqual(report["episode_count"],5)
        self.assertTrue(all(p.read_bytes()==content for p,content in zip(paths,before)))
        self.assertEqual(len(report["pairwise_literal_similarity"]),10)
        code=[x["code"] for x in report["observations"]]
        self.assertIn("UNIFORM_CHAPTER_COUNT",code)
        self.assertIn("UNIFORM_RENDERER_PACING",code)
        self.assertIn("LEGACY_STOCK_ENDING",code)
        self.assertFalse(report["human_approved"])
        self.assertFalse(report["changed_master"])
        self.assertEqual(report["paid_calls"],0)
        self.assertTrue(all(ep["requires_artistic_relisten"] for ep in report["episodes"]))

    def _recipe(self,path,title,opening,ending,chapters=2):
        data={"public_title":title,"work_id":title.lower(),"variant":"critico_standard",
              "chapters":[{"text":opening}]+
                         [{"text":f"Un'osservazione verificata sulle immagini {i}."}
                          for i in range(chapters-2)]+[{"text":ending}]}
        path.write_text(json.dumps(data,ensure_ascii=False))
        return path

    def test_repeat_opening_is_reviewer_warning_not_ai_detection(self):
        with tempfile.TemporaryDirectory() as d:
            a=self._recipe(Path(d)/"a.json","Work A","La porta si apre davanti alla figura.","A terra c'è una spada.")
            b=self._recipe(Path(d)/"b.json","Work B","La porta si apre davanti alla figura.","Qui vediamo la strada.")
            r=audit.inspect_paths([a,b])
        codes=[x["code"] for x in r["observations"]]
        self.assertIn("SIMILAR_OPENING",codes)
        self.assertNotIn("SIMILAR_CLOSING",codes)
        self.assertFalse(r["human_approved"])

    def test_different_openings_and_specific_endings_have_no_repeated_phrase_warning(self):
        with tempfile.TemporaryDirectory() as d:
            a=self._recipe(Path(d)/"a.json","Work A","Una barca tocca l'argine.","Il pescatore torna a terra.")
            b=self._recipe(Path(d)/"b.json","Work B","La luce illumina la finestra.","Il tavolo resta vuoto.")
            r=audit.inspect_paths([a,b])
        codes=[x["code"] for x in r["observations"]]
        self.assertNotIn("SIMILAR_OPENING",codes)
        self.assertNotIn("SIMILAR_CLOSING",codes)

    def test_malformed_recipe_and_duplicate_paths_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            a=Path(d)/"a.json"
            a.write_text('{"chapters":[{"title":"No text"}]}')
            with self.assertRaises(ValueError):audit.inspect_paths([a,a])
            b=Path(d)/"b.json";b.write_text('{"chapters":[{"text":"ok"}]}')
            with self.assertRaises(ValueError):audit.inspect_paths([a,b])

    def test_scripts_and_renderers_must_correspond(self):
        with tempfile.TemporaryDirectory() as d:
            a=self._recipe(Path(d)/"a.json","Work A","Segno.","Dettaglio.")
            b=self._recipe(Path(d)/"b.json","Work B","Altro segno.","Altra cosa.")
            with self.assertRaises(ValueError):audit.inspect_paths([a,b],[Path(d)/"renderer.py"])
            with self.assertRaises(ValueError):audit.inspect_paths([a])

    def test_no_fake_measured_mp4_from_python_literals(self):
        with tempfile.TemporaryDirectory() as d:
            a=self._recipe(Path(d)/"a.json","Work A","La porta.","Il fuoco.")
            b=self._recipe(Path(d)/"b.json","Work B","Il cielo.","La terra.")
            p=Path(d)/"one.py";p.write_text("DELAY,TAIL=3.5,6.0\n")
            q=Path(d)/"two.py";q.write_text("DELAY,TAIL=3.5,6.0\n")
            r=audit.inspect_paths([a,b],[p,q])
        self.assertEqual(r["episodes"][0]["renderer"]["outro_tail_s"],6.0)
        self.assertIn("not measured",r["episodes"][0]["renderer"]["note"])


if __name__=="__main__":unittest.main()
