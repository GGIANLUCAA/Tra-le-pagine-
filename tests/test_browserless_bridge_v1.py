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


    def test_http_error_is_classified_without_leaking_credentials(self):
        from urllib.error import HTTPError
        from io import BytesIO
        secret = "private_example_secret_value"
        body = ("SELECTOR_NOT_FOUND " + secret).encode()
        simulated = HTTPError("https://example.org/?token=" + secret, 400,
                              "Bad Request", {}, BytesIO(body))
        with patch("tools.browserless_bridge_v1.urllib.request.urlopen", side_effect=simulated):
            with self.assertRaises(RuntimeError) as raised:
                run_request(sample(), secret)
        self.assertIn("selector_not_found", str(raised.exception))
        self.assertNotIn(secret, str(raised.exception))


    def test_structured_interaction_error_is_fail_closed(self):
        class Response:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self, n):
                return json.dumps({"data": {"browser_error": "SELECTOR_NOT_FOUND",
                                            "untrusted_page": "never disclose"}}).encode()
        with patch("tools.browserless_bridge_v1.urllib.request.urlopen", return_value=Response()):
            with self.assertRaisesRegex(RuntimeError, "SELECTOR_NOT_FOUND") as outcome:
                run_request(sample(), "test_secret")
        self.assertNotIn("never disclose", str(outcome.exception))


    def test_inspect_public_links_is_one_public_action(self):
        req = sample()
        req["actions"] = [{"type": "inspect_public_links"}]
        self.assertIs(validate_request(req), req)
        req["actions"] = [{"type": "inspect_public_links", "selector": "a"}]
        with self.assertRaises(ValueError):
            validate_request(req)
        req["actions"] = [{"type": "inspect_public_links"}, {"type": "click", "selector": "a"}]
        with self.assertRaises(ValueError):
            validate_request(req)

    def test_public_links_results_do_not_expose_unapproved_hosts(self):
        class Response:
            def __init__(self, host):
                self.host = host
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self, n):
                return json.dumps({"data": {"title": "Documentation", "url": "https://docs.browserless.io/",
                  "links": [{"host": self.host, "path": "/rest-apis/intro", "text": "REST APIs"}]}}).encode()
        req = sample()
        req["url"] = "https://docs.browserless.io/"
        req["actions"] = [{"type": "inspect_public_links"}]
        with patch("tools.browserless_bridge_v1.urllib.request.urlopen", return_value=Response("docs.browserless.io")):
            response = run_request(req, "private_token")
            self.assertEqual(response["public_links"][0]["path"], "/rest-apis/intro")
            self.assertNotIn("private_token", json.dumps(response))
        with patch("tools.browserless_bridge_v1.urllib.request.urlopen", return_value=Response("untrusted.example")):
            with self.assertRaises(RuntimeError):
                run_request(req, "private_token")


if __name__ == "__main__":
    unittest.main()
