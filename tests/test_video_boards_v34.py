"""Visual Boards V34: offline and batch tests. No external API, TTS or publication."""
import json
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from src.video_boards_v34 import generate, prepare


class BoardTests(unittest.TestCase):
    def sample(self, folder, index=1, incomplete=True):
        folder.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (720, 1280), (23, 65, 77)).save(folder/"scena_01.jpg")
        Image.new("RGB", (720, 1280), (183, 132, 84)).save(folder/"scena_02.jpg")
        project = {
          "schema": "video-project-v13", "format": "libri",
          "topic": "Fiaba di prova " + str(index), "preset": "narrative-v12-harmonic-v5", "status": "planned",
          "editorial_plan": {
             "opening_promise": "Una promessa verificabile e motivata",
             "subject_insight": "Una storia raccontata da illustrazioni originali",
             "duration_seconds": 178, "duration_reason": "Sulla durata del racconto",
             "mix_reason": "Movimenti discreti guidati dalle parole",
             "payoff": "Conclusione completa del racconto",
             "media_sourcing": {"decisions": [
                {"asset_id": "V1", "source_reference": "Illustrazione originale 1",
                 "rights_review": "reviewed", "scene_relevance": "reviewed",
                 "visual_review": "passed"},
                {"asset_id": "V2", "source_reference": "Da controllare",
                 "rights_review": "pending", "scene_relevance": "pending",
                 "visual_review": "pending"}] }},
          "assets": [
             {"id": "V1", "role": "visual", "file": "scena_01.jpg",
              "source": "Produzione originale", "rights": "Da controllare per uso commerciale"},
             {"id": "V2", "role": "visual", "file": "scena_02.jpg",
              "source": "Produzione originale", "rights": "Non verificati"}],
          "scenes": [
             {"asset_id": "V1", "description": "Prima scena del racconto", "reason": "Apertura"},
             {"asset_id": "V2", "description": "Seconda scena del racconto", "reason": "Sviluppo"}],
        }
        path=folder/"PROJECT_V13.json"
        path.write_text(json.dumps(project,ensure_ascii=False), encoding="utf-8")
        return path

    def test_produce_three_readable_boards_without_verifying_rights(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)
            p=self.sample(base/"episode")
            out=base/"out"
            result=generate(p,out)
            self.assertFalse(result["calls_paid_models"])
            self.assertEqual(result["scene_count"],2)
            self.assertIn("MASTER_BOARD.png",result["files"])
            self.assertEqual(len(result["files"]),4)
            self.assertEqual(result["unreviewed_visual_assets"],["V2"])
            self.assertEqual(result["status"],"informational_not_approved")
            for name in result["files"]:
                file=out/name
                self.assertGreater(file.stat().st_size,1000)
                with Image.open(file) as im:
                    self.assertGreaterEqual(im.width,1600)
                    im.verify()

    def test_batch_20_distinct_projects(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)
            for i in range(20):
                project=self.sample(base/("ep_%02d"%i),i)
                out=base/"boards"/("ep_%02d"%i)
                result=generate(project,out)
                self.assertEqual(result["visual_asset_count"],2)
                self.assertTrue((out/"BOARD_MANIFEST.json").exists())
                self.assertGreater((out/"MASTER_BOARD.png").stat().st_size,1000)
            self.assertEqual(len(list((base/"boards").glob("*/CONCEPT_BOARD.png"))),20)

    def test_reject_non_v13_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"PROJECT_V13.json"
            path.write_text('{"schema":"not-v13"}',encoding="utf-8")
            with self.assertRaises(ValueError):
                prepare(path)


if __name__ == "__main__":
    unittest.main()
