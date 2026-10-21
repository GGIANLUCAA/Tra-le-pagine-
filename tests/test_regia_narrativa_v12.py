"""V12 scene-by-scene editorial mapping tests. No external services."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from regia_narrativa_v12 import scene_review,write_review

class NarrativeReviewV12(unittest.TestCase):
    def make_episode(self,root):
        ep=Path(root)/"episode"
        ep.mkdir()
        phrases=[f"Il protagonista entra nella stanza numero {i} e incontra una persona misteriosa."
                 for i in range(16)]
        (ep/"testo.txt").write_text(" ".join(phrases),encoding="utf-8")
        cues=[{"asset":i+1,"start_sentence":i*2,
               "narration_anchor":phrases[i*2],
               "description":f"La persona nella stanza {i*2}"}
              for i in range(8)]
        (ep/"scene_cues.json").write_text(json.dumps(cues),encoding="utf-8")
        return ep

    def test_one_scene_maps_to_exact_voice_span(self):
        with tempfile.TemporaryDirectory() as d:
            ep=self.make_episode(d)
            data=write_review(ep)
            self.assertEqual(data["scene_count"],8)
            self.assertEqual(data["scenes"][0]["sentence_start"],0)
            self.assertIn("stanza numero 1",data["scenes"][0]["exact_voice_segment"])
            self.assertNotIn("stanza numero 2",data["scenes"][0]["exact_voice_segment"])
            self.assertFalse(data["visuals_certified"])
            self.assertEqual(data["subtitle_policy"],"DISABLED")
            self.assertTrue((ep/"REGIA_NARRATIVA_V12.txt").is_file())
            self.assertIn("VERIFICA ARTISTICA",(ep/"REGIA_NARRATIVA_V12.txt").read_text())

    def test_does_not_certify_visual_accuracy_without_actual_review(self):
        with tempfile.TemporaryDirectory() as d:
            ep=self.make_episode(d)
            report=scene_review(ep)
            self.assertTrue(all(x["semantic_alignment"]=="NEEDS_VISUAL_REVIEW" for x in report["scenes"]))

    def test_refuses_wrong_voice_anchor(self):
        with tempfile.TemporaryDirectory() as d:
            ep=self.make_episode(d)
            p=ep/"scene_cues.json"
            cues=json.loads(p.read_text());cues[3]["narration_anchor"]="Una frase che non appare nel copione."
            p.write_text(json.dumps(cues))
            with self.assertRaises(ValueError):scene_review(ep)

    def test_refuses_invalid_scene_order(self):
        with tempfile.TemporaryDirectory() as d:
            ep=self.make_episode(d)
            p=ep/"scene_cues.json"
            cues=json.loads(p.read_text());cues[3]["start_sentence"]=0
            p.write_text(json.dumps(cues))
            with self.assertRaises(ValueError):scene_review(ep)

    def test_autopilot_provenance_and_original_schema_both_preserve_sources(self):
        with tempfile.TemporaryDirectory() as d:
            ep=self.make_episode(d)
            (ep/"PROVENIENZA_FOTO.json").write_text(json.dumps([
                {"image":"scena_01.jpg","source":"https://museum.example/one"},
                {"asset":2,"source_url":"https://museum.example/two"},
                {"asset":"invalid","source":"ignored"},
            ]))
            report=scene_review(ep)
            self.assertEqual(report["scenes"][0]["original_source"],"https://museum.example/one")
            self.assertEqual(report["scenes"][1]["original_source"],"https://museum.example/two")

if __name__=="__main__":
    unittest.main()
