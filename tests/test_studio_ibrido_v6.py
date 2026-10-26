"""Test V6: nessuna API, nessuna dipendenza esterna."""
import json
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from studio_ibrido_v6 import build_plan, scene_method, source_report, storyboard_html
from prompt_asset_v6 import build_prompts


REGISTRY = {
    "tools": [
        {"id": "ffmpeg", "enabled": True},
        {"id": "gemini-tts", "enabled": True},
        {"id": "qwen3-tts", "enabled": False},
    ]
}


class StudioIbridoV6Tests(unittest.TestCase):
    def make_episode(self, root, descriptions=None):
        ep = root / "test_ep"
        ep.mkdir()
        descs = descriptions or ["Il fiume e la montagna", "Ritratto della protagonista"]
        cues = [{"start_sentence": idx * 2, "asset": idx + 1, "description": value}
                for idx, value in enumerate(descs)]
        (ep / "scene_cues.json").write_text(json.dumps(cues), encoding="utf-8")
        (ep / "metadata.json").write_text(json.dumps({"title": "Episodio Test"}), encoding="utf-8")
        return ep

    def test_zero_mode_keeps_existing_engine(self):
        with tempfile.TemporaryDirectory() as d:
            ep = self.make_episode(Path(d))
            report = build_plan(ep, "libri", "zero", REGISTRY)
            self.assertEqual(report["consumo_crediti_api"], 0)
            self.assertEqual(report["eseguiti_modelli_esterni"], [])
            self.assertEqual(report["render_attuale"], "ffmpeg")
            self.assertEqual(report["voce_attuale"], "gemini-tts")
            self.assertFalse(report["pubblicazione_automatica"])
            self.assertEqual(report["conteggi"]["inquadrature"], 2)
            self.assertEqual(report["scenes"][0]["alternative_da_testare_non_attive"], [])
            self.assertEqual(report["scenes"][0]["source_need_v34"], "fictional_action")
            self.assertIn("ai_horde_manual_three_scene_trial", report["scenes"][0]["priority_sources_v34"])
            self.assertFalse(report["scenes"][0]["media_v34_verified"])
            self.assertIn("Episodio Test", storyboard_html(report))

    def test_cronaca_without_sources_is_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            ep = self.make_episode(Path(d))
            report = build_plan(ep, "cronaca", "zero", REGISTRY)
            self.assertFalse(report["puo_passare_a_revisione_editoriale"])
            self.assertEqual(report["stato_fonti"]["status"], "FONTI_DA_AGGIUNGERE")
            self.assertEqual(report["scenes"][0]["regia_gratuita"], "archivio_verificato_o_grafica_neutra")
            self.assertEqual(report["scenes"][0]["source_need_v34"], "documentary_evidence")
            self.assertIn("STOP_and_label_reconstruction_if_no_evidence",
                          report["scenes"][0]["priority_sources_v34"])

    def test_two_domains_still_need_human_verification(self):
        with tempfile.TemporaryDirectory() as d:
            ep = self.make_episode(Path(d))
            (ep / "fonti.json").write_text(json.dumps([
                {"url": "https://example.org/a", "titolo": "Fonte A"},
                {"url": "https://example.com/b", "titolo": "Fonte B"}
            ]), encoding="utf-8")
            result = source_report(ep, "cronaca")
            self.assertEqual(result["status"], "DA_VERIFICARE_A_MANO")
            self.assertEqual(result["independent_domains"], 2)

    def test_no_duplicate_sentence_cue(self):
        with tempfile.TemporaryDirectory() as d:
            ep = self.make_episode(Path(d))
            (ep / "scene_cues.json").write_text(json.dumps([
                {"start_sentence": 0, "asset": 1, "description": "A"},
                {"start_sentence": 0, "asset": 2, "description": "B"}
            ]), encoding="utf-8")
            with self.assertRaises(ValueError):
                build_plan(ep, "libri", "zero", REGISTRY)

    def test_html_escaping(self):
        with tempfile.TemporaryDirectory() as d:
            ep = self.make_episode(Path(d), ["<script>alert('x')</script>"])
            h = storyboard_html(build_plan(ep, "libri", "zero", REGISTRY))
            self.assertNotIn("<script>", h)
            self.assertIn("&lt;script&gt;", h)

    def test_candidates_are_never_executed(self):
        with tempfile.TemporaryDirectory() as d:
            ep = self.make_episode(Path(d))
            report = build_plan(ep, "libri", "basso", REGISTRY)
            self.assertIn("wan2.2", report["scenes"][0]["alternative_da_testare_non_attive"])
            self.assertEqual(report["eseguiti_modelli_esterni"], [])


    def test_prompt_pack_reuses_assets(self):
        with tempfile.TemporaryDirectory() as d:
            ep = self.make_episode(Path(d))
            (ep / "scene_cues.json").write_text(json.dumps([
                {"start_sentence": 0, "asset": 1, "description": "Anna sul fiume"},
                {"start_sentence": 4, "asset": 1, "description": "Anna davanti al fiume, ripresa diversa"}
            ]), encoding="utf-8")
            (ep / "personaggi.json").write_text(json.dumps([
                {"nome": "Anna", "caratteristiche": "capelli castani, sciarpa rossa"}
            ]), encoding="utf-8")
            prompts = build_prompts(build_plan(ep, "libri", "zero", REGISTRY), ep)
            self.assertEqual(len(prompts["asset"]), 1)
            self.assertIn("sciarpa rossa", prompts["asset"][0]["prompt"])
            self.assertEqual(prompts["immagini_da_generare"], 1)

    def test_cronaca_prompts_are_marked_reconstruction(self):
        with tempfile.TemporaryDirectory() as d:
            ep = self.make_episode(Path(d))
            result = build_prompts(build_plan(ep, "cronaca", "zero", REGISTRY), ep)
            self.assertIn("NON UN FILMATO AUTENTICO", result["asset"][0]["prompt"])


if __name__ == "__main__":
    unittest.main()
