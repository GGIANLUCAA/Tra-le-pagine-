"""V8 regression tests — zero network, no production API calls."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from orchestratore_v8 import (EpisodePlugin, ManualPlugin, prepare, plan,
                              safe_user_path, similarity, scene_html)


class OrchestratoreV8Tests(unittest.TestCase):
    def fixture(self, root):
        from PIL import Image
        root=Path(root)
        ep=root/"episodes"/"prova"
        ep.mkdir(parents=True)
        (root/"config").mkdir()
        (root/"config"/"studio_ibrido_tools.json").write_text(json.dumps({
            "tools":[{"id":"ffmpeg","enabled":True},{"id":"gemini-tts","enabled":True}]
        }))
        (ep/"images").mkdir()
        (ep/"metadata.json").write_text(json.dumps({
            "episode":"01", "title":"Prova V8", "author":"Test"
        }), encoding="utf-8")
        (ep/"testo.txt").write_text(
            "Questo è un racconto di prova. "*85,encoding="utf-8")
        (ep/"DESCRIZIONE_SOCIAL.txt").write_text("Test di regia senza pubblicazione",encoding="utf-8")
        cues=[{"start_sentence":i,"asset":i%2+1,
               "description":"fiume verde a mezzogiorno" if i%2==0 else "ritratto sereno vicino al fiume"}
               for i in range(8)]
        (ep/"scene_cues.json").write_text(json.dumps(cues),encoding="utf-8")
        Image.effect_noise((1200,1500),80).convert("RGB").save(ep/"images"/"scena_01.jpg",quality=89)
        Image.effect_noise((1200,1500),100).convert("RGB").save(ep/"images"/"scena_02.jpg",quality=89)
        return ep

    def test_plan_is_read_only_and_uses_current_voice(self):
        with tempfile.TemporaryDirectory() as td:
            ep=self.fixture(td)
            initial=hashlib.sha256((ep/"testo.txt").read_bytes()).hexdigest()
            report=plan(td,"prova","libri")
            self.assertEqual(report["unique_assets"],2)
            self.assertEqual(report["existing_assets_reused"],8)
            self.assertTrue(report["complete"])
            self.assertTrue(report["uses_google_gemini"])
            self.assertFalse(report["publish_enabled"])
            self.assertEqual(initial,hashlib.sha256((ep/"testo.txt").read_bytes()).hexdigest())

    def test_gate1_is_mandatory(self):
        with tempfile.TemporaryDirectory() as td:
            self.fixture(td)
            with self.assertRaises(ValueError):
                prepare(td,plan(td,"prova","libri"),Path(td)/"out",False)
            self.assertFalse((Path(td)/"out"/"stage").exists())

    def test_prepare_stages_and_does_not_modify_originals(self):
        with tempfile.TemporaryDirectory() as td:
            ep=self.fixture(td)
            original_sha=hashlib.sha256((ep/"images"/"scena_01.jpg").read_bytes()).hexdigest()
            dest=prepare(td,plan(td,"prova","libri"),Path(td)/"out",True)
            self.assertTrue((dest/"images"/"scena_01.jpg").is_file())
            self.assertTrue((dest/"images"/"scena_02.jpg").is_file())
            self.assertEqual(original_sha,hashlib.sha256((ep/"images"/"scena_01.jpg").read_bytes()).hexdigest())
            manifest=json.loads((Path(td)/"out"/"RAPPORTO_PREPARAZIONE_V8.json").read_text())
            self.assertFalse(manifest["publish_enabled"])
            self.assertEqual(manifest["gate2"],"in_attesa")
            self.assertEqual(manifest["v5_preflight"],"PASS")

    def test_missing_material_never_uses_fake_placeholder(self):
        with tempfile.TemporaryDirectory() as td:
            ep=self.fixture(td)
            (ep/"images"/"scena_02.jpg").unlink()
            p=plan(td,"prova","libri")
            self.assertEqual(p["missing_assets"],[2])
            with self.assertRaises(ValueError):
                prepare(td,p,Path(td)/"out",True)

    def test_private_manual_material_requires_approval(self):
        with tempfile.TemporaryDirectory() as td:
            ep=self.fixture(td)
            (ep/"images"/"scena_02.jpg").unlink()
            (Path(td)/"media").mkdir()
            from PIL import Image
            Image.new("RGB",(500,600),(7,5,3)).save(Path(td)/"media"/"test.jpg")
            mf=Path(td)/"manual.json"
            mf.write_text(json.dumps({"2":{"path":"media/test.jpg",
                "source":"mio_materiale", "approved_for_private_project":False}}))
            self.assertFalse(plan(td,"prova","libri","manual.json")["complete"])
            mf.write_text(json.dumps({"2":{"path":"media/test.jpg",
                "source":"mio_materiale", "approved_for_private_project":True}}))
            self.assertTrue(plan(td,"prova","libri","manual.json")["complete"])

    def test_reject_external_paths_and_urls(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                safe_user_path("../../etc/passwd",td)
            with self.assertRaises(ValueError):
                safe_user_path("https://example.com/a.jpg",td)

    def test_episode_suggestions_are_nonbinding(self):
        with tempfile.TemporaryDirectory() as td:
            ep=self.fixture(td)
            (ep/"images"/"scena_02.jpg").unlink()
            copy=Path(td)/"episodes"/"altra"
            copy.mkdir()
            (copy/"images").mkdir()
            from PIL import Image
            Image.new("RGB",(500,600),(44,44,44)).save(copy/"images"/"scena_01.jpg")
            (copy/"scene_cues.json").write_text(json.dumps([
                {"start_sentence":0,"asset":1,"description":"ritratto sereno vicino al fiume"}
            ]))
            r=plan(td,"prova","libri")
            self.assertFalse(r["complete"])
            self.assertEqual(r["scenes"][1]["suggestions"][0]["episode"],"altra")
            self.assertIn("solo_suggerimento",r["scenes"][1]["suggestions"][0]["status"])

    def test_html_escapes_description(self):
        with tempfile.TemporaryDirectory() as td:
            ep=self.fixture(td)
            cues=json.loads((ep/"scene_cues.json").read_text())
            cues[0]["description"]="<script>evil</script>"
            (ep/"scene_cues.json").write_text(json.dumps(cues))
            doc=scene_html(plan(td,"prova","libri"))
            self.assertNotIn("<script>",doc)
            self.assertIn("&lt;script&gt;",doc)

    def test_similarity_token_based(self):
        self.assertEqual(similarity("river sunset","river sunset"),1.0)
        self.assertEqual(similarity("mountain","city"),0.0)


if __name__=="__main__":
    unittest.main()
