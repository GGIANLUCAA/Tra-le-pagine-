"""Offline tests: never call Browserless and never require its API token."""
import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.browserless_bridge_v1 import validate_request, run_request, main


def sample():
    return {"version": 1, "request_id": "artvision-demo-001",
            "url": "https://example.com/", "actions": []}


class TestPublicBrowserBridge(unittest.TestCase):
    def test_public_request_is_valid(self):
        self.assertEqual(validate_request(sample())["request_id"], "artvision-demo-001")

    def test_url_must_be_approved_and_have_no_credentials(self):
        for bad in ("http://example.com", "https://evil.example.com",
                    "https://example.com/?token=secret", "https://alice:password@example.com/",
                    "https://accounts.google.com/", "https://work.trae.ai/",
                    "https://example.com:8080/"):
            with self.subTest(bad=bad):
                v = sample()
                v["url"] = bad
                with self.assertRaises(ValueError):
                    validate_request(v)

    def test_no_unbounded_actions_or_private_typing(self):
        v = sample()
        v["actions"] = [{"type": "click", "selector": "a"}] * 5
        with self.assertRaises(ValueError):
            validate_request(v)
        for txt in ("person@example.com", "my Password", "API_KEY_ABC", "codice 111111"):
            with self.subTest(text=txt):
                v = sample()
                v["actions"] = [{"type": "type_public", "selector": "input", "text": txt}]
                with self.assertRaises(ValueError):
                    validate_request(v)

    def test_public_click_and_nonprivate_typing(self):
        v = sample()
        v["actions"] = [{"type": "click", "selector": "a[href]"},
                        {"type": "type_public", "selector": "input.search", "text": "museum"}]
        self.assertIs(validate_request(v), v)

    def test_response_validation_and_no_secret_in_result(self):
        class Response:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self, n):
                return json.dumps({"data": {"title": "Example Domain", "heading": "Example Domain",
                                            "url": "https://example.com/", "action_count": 0}}).encode()

        with patch("tools.browserless_bridge_v1.urllib.request.urlopen", return_value=Response()) as urlopen:
            result = run_request(sample(), "private_test_token")
            self.assertEqual(result["title"], "Example Domain")
            self.assertNotIn("private_test_token", json.dumps(result))
            req = urlopen.call_args.args[0]
            payload = json.loads(req.data.decode())
            self.assertEqual(payload["context"]["url"], "https://example.com/")
            self.assertNotIn("private_test_token", json.dumps(payload))

    def test_refuse_wrong_redirect(self):
        class Response:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self, n):
                return json.dumps({"data": {"title": "Login", "url": "https://accounts.google.com/"}}).encode()

        with patch("tools.browserless_bridge_v1.urllib.request.urlopen", return_value=Response()):
            with self.assertRaisesRegex(RuntimeError, "outside allowlist"):
                run_request(sample(), "private_test_token")


if __name__ == "__main__":
    unittest.main()
