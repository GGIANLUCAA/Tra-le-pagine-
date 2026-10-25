"""Test senza rete, API key e GPU. Si eseguono anche sui runner GitHub CPU."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SRC = Path(__file__).resolve().parents[1] / "src" / "image_pipeline_v1.py"
spec = importlib.util.spec_from_file_location("image_pipeline_v1", SRC)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class ImagesV1Test(unittest.TestCase):
    def setUp(self):
        self.demo = Path(__file__).resolve().parents[1] / "config" / "image_pipeline_v1_demo.json"

    def test_01_plan_no_network(self):
        with tempfile.TemporaryDirectory() as td:
            brief = mod.load_brief(self.demo, mod.MAX_IMAGES)
            with patch.object(mod, "request_json", side_effect=AssertionError("Network in plan!")):
                output = mod.execute(brief, Path(td), mode="plan")
            self.assertEqual(len(output["images"]), 3)
            self.assertTrue(output["completed"])
            self.assertFalse(output["publication"])
            self.assertTrue(Path(td, "MANIFEST_IMAGES_V1.json").is_file())

    def test_02_prompt_has_single_scene_and_bible(self):
        brief = mod.load_brief(self.demo, mod.MAX_IMAGES)
        s = mod.prompt_for(brief, brief["scenes"][1])
        self.assertIn("The scientist", s)
        self.assertIn("same", s.lower())
        self.assertIn("no collage", s.lower())

    def test_03_duplicate_ids_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            obj = json.loads(self.demo.read_text())
            obj["scenes"][1]["id"] = obj["scenes"][0]["id"]
            p = Path(td, "bad.json")
            p.write_text(json.dumps(obj))
            with self.assertRaises(mod.PipelineError):
                mod.load_brief(p, mod.MAX_IMAGES)

    def test_04_batch_is_bounded(self):
        with tempfile.TemporaryDirectory() as td:
            obj = json.loads(self.demo.read_text())
            obj["scenes"].append(dict(obj["scenes"][0], id="04_troppo"))
            p = Path(td, "too-many.json")
            p.write_text(json.dumps(obj))
            with self.assertRaises(mod.PipelineError):
                mod.load_brief(p, mod.MAX_IMAGES)

    def test_05_untrusted_download_domains_blocked(self):
        for link in ["http://r2.dev/test.png", "https://localhost/a.png",
                     "https://evil-r2.dev/image.jpg", "https://127.0.0.1/a",
                     "https://r2.dev.evil.com/a", "file:///etc/passwd"]:
            self.assertFalse(mod.validated_cdn(link), link)
        self.assertTrue(mod.validated_cdn("https://subdomain.r2.dev/result.webp"))

    def test_06_generate_requires_api_key_and_model(self):
        with tempfile.TemporaryDirectory() as td:
            brief = mod.load_brief(self.demo, mod.MAX_IMAGES)
            with self.assertRaises(mod.PipelineError):
                mod.execute(brief, Path(td), mode="generate", model="", key="")

    def test_07_request_not_shared_and_only_one_image(self):
        brief = mod.load_brief(self.demo, mod.MAX_IMAGES)
        payload = mod.make_request(brief, brief["scenes"][0], "example-model")
        self.assertFalse(payload["shared"])
        self.assertFalse(payload["nsfw"])
        self.assertEqual(payload["params"]["n"], 1)
        self.assertEqual(payload["models"], ["example-model"])

    def test_08_no_automatic_retry_when_rate_limited(self):
        class Response:
            status = 429
        from urllib.error import HTTPError
        with patch.object(mod.urllib.request, "urlopen", side_effect=HTTPError(
                "https://aihorde.net/api/v2/generate/async", 429, "rate limit", {}, None)) as mocked:
            with self.assertRaisesRegex(mod.PipelineError, "429"):
                mod.request_json("POST", mod.API + "/generate/async", payload={})
            self.assertEqual(mocked.call_count, 1)


if __name__ == "__main__":
    unittest.main()
