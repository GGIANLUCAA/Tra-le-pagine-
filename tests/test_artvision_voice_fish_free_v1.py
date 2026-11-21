import importlib.util
import json
import os
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.request import Request

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("fish", ROOT / "src/artvision_voice_fish_free_v1.py")
fish = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fish)


class FishVoiceUnitTests(unittest.TestCase):
    def job(self, **overrides):
        x = {"work_id": "painting_001", "provider": "fish_audio_free",
             "format": "critico_standard", "allow_paid_api": False,
             "auto_publish": False, "review_only": True}
        x.update(overrides)
        return x

    def test_explicit_free_model_immutable(self):
        self.assertEqual(fish.MODEL, "s2.1-pro-free")
        self.assertEqual(fish.URL, "https://api.fish.audio/v1/tts")

    def test_review_is_allowed_before_voice_approval(self):
        plan = fish.validate_request(self.job(), "abcd1234567890", False)
        self.assertEqual(plan["state"], "READY_REVIEW")
        self.assertEqual(plan["paid_calls"], 0)
        self.assertEqual(len(plan["shared_variants"]), 2)

    def test_longer_production_requires_owner_approval(self):
        with self.assertRaises(RuntimeError):
            fish.validate_request(self.job(review_only=False), "abcd1234567890", False)
        plan = fish.validate_request(self.job(review_only=False), "abcd1234567890", True)
        self.assertEqual(plan["state"], "READY_APPROVED_VOICE")

    def test_rejects_paid_calls_and_autopublish(self):
        for field in ("allow_paid_api", "auto_publish"):
            with self.assertRaises(ValueError):
                fish.validate_request(self.job(**{field: True}), "abcd1234567890", True)

    def test_rejects_other_providers(self):
        with self.assertRaises(ValueError):
            fish.validate_request(self.job(provider="paid_fish"), "abcd1234567890", True)

    def test_missing_key_causes_zero_network_requests(self):
        with patch("urllib.request.urlopen") as mocked:
            with self.assertRaises(RuntimeError):
                fish.request_audio("Una voce naturale.", "abcd1234567890", "")
            mocked.assert_not_called()

    def test_no_unsafe_file_path(self):
        with self.assertRaises(ValueError):
            fish.read_script("../../../../etc/passwd")

    def test_request_uses_free_header_and_private_reference(self):
        class FakeResponse:
            status = 200
            headers = {"Content-Type": "audio/mpeg"}
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def read(self, n):
                return b"ID3" + b"x" * 2048

        def fake_open(req, timeout):
            self.assertIsInstance(req, Request)
            self.assertEqual(req.get_header("Model"), "s2.1-pro-free")
            self.assertIn("Bearer test-key", req.get_header("Authorization"))
            body = json.loads(req.data.decode("utf-8"))
            self.assertEqual(body["reference_id"], "voice12345678")
            self.assertEqual(body["language"], "it")
            return FakeResponse()

        with patch("urllib.request.urlopen", side_effect=fake_open):
            data = fish.request_audio("Una luce attraversa il quadro.", "voice12345678", "test-key")
            self.assertTrue(data.startswith(b"ID3"))


if __name__ == "__main__":
    unittest.main()
