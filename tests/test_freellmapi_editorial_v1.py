"""Offline tests: never contact a real LLM provider or consume credits."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from freellmapi_editorial_v1 import (  # noqa: E402
    FreeLLMAPIError, generate_draft, validate_local_url,
)


class StubResponse:
    headers = {"X-Routed-Via": "mock/free-test-model"}

    def __init__(self, data):
        self.data = data

    def read(self, _size):
        return self.data

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None


def mock_opener(req, timeout):
    assert timeout <= 35
    assert req.full_url == "http://127.0.0.1:3001/v1/chat/completions"
    assert req.get_header("Authorization") == "Bearer mock-unified-key"
    payload = json.loads(req.data)
    assert payload["model"] == "auto"
    assert "unapproved" in payload["messages"][0]["content"]
    return StubResponse(
        json.dumps({
            "model": "mock-free-test-model",
            "choices": [{"message": {"content": "Draft text, human review pending."}}],
        }).encode("utf-8")
    )


ENV = {
    "FREELLMAPI_ENABLED": "1",
    "FREELLMAPI_API_KEY": "mock-unified-key",
    "FREELLMAPI_BASE_URL": "http://127.0.0.1:3001/v1",
}


class FreeLLMAPIEditorialTests(unittest.TestCase):
    def test_disabled_by_default(self):
        with self.assertRaisesRegex(FreeLLMAPIError, "Disabled"):
            generate_draft("social", "Artwork", environ={}, opener=mock_opener)

    def test_missing_key_is_rejected(self):
        env = {k: v for k, v in ENV.items() if k != "FREELLMAPI_API_KEY"}
        with self.assertRaisesRegex(FreeLLMAPIError, "key"):
            generate_draft("social", "Artwork", environ=env, opener=mock_opener)

    def test_only_loopback_allowed(self):
        self.assertEqual(
            validate_local_url("http://localhost:3001/v1"),
            "http://localhost:3001/v1",
        )
        for url in (
            "https://free.example/v1",
            "http://192.168.1.9:3001/v1",
            "http://127.0.0.1:3001/admin",
            "http://user:pass@localhost:3001/v1",
            "http://localhost/v1",
            "http://localhost:3001/v1?token=x",
        ):
            with self.subTest(url=url), self.assertRaises(FreeLLMAPIError):
                validate_local_url(url)

    def test_supported_tasks_generate_only_drafts(self):
        for task in ("storyboard", "narration", "social", "source_notes", "qa_second_opinion"):
            with self.subTest(task=task):
                data = generate_draft(task, "Public artwork title and verified notes", environ=ENV,
                                      opener=mock_opener)
                self.assertEqual(data["status"], "draft_unreviewed")
                self.assertFalse(data["artistic_approval"])
                self.assertFalse(data["publication_authorized"])
                self.assertFalse(data["rights_verified"])
                self.assertEqual(data["routed_via"], "mock/free-test-model")

    def test_no_unapproved_tasks(self):
        with self.assertRaisesRegex(FreeLLMAPIError, "Unsupported"):
            generate_draft("publish_video", "Publish now", environ=ENV, opener=mock_opener)

    def test_response_without_text_rejected(self):
        def blank(_req, timeout):
            return StubResponse(b'{"choices": [{"message": {"content": ""}}]}')
        with self.assertRaisesRegex(FreeLLMAPIError, "no usable text"):
            generate_draft("social", "Artwork", environ=ENV, opener=blank)

    def test_large_response_rejected(self):
        def huge(_req, timeout):
            return StubResponse(b"X" * (524288 + 1))
        with self.assertRaisesRegex(FreeLLMAPIError, "size limit"):
            generate_draft("social", "Artwork", environ=ENV, opener=huge)

    def test_dry_run_never_calls_network_or_writes_file(self):
        with tempfile.TemporaryDirectory() as tempdir:
            prompt = Path(tempdir) / "prompt.txt"
            output = Path(tempdir) / "draft.json"
            prompt.write_text("A verified public-domain painting", encoding="utf-8")
            env = dict(os.environ)
            env.pop("FREELLMAPI_ENABLED", None)
            env.pop("FREELLMAPI_API_KEY", None)
            proc = subprocess.run([
                sys.executable, str(ROOT / "src" / "freellmapi_editorial_v1.py"),
                "--task", "social",
                "--prompt-file", str(prompt),
                "--output", str(output),
            ], capture_output=True, text=True, env=env, check=True)
            self.assertIn("DRY_RUN_ONLY", proc.stdout)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
