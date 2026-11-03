"""Offline tests: never contact a real LLM provider or consume credits."""
import json
import datetime as dt
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from free_llm_zero_cost_v1 import ZeroCostPolicyError, admit, route_matches_actual  # noqa: E402
from freellmapi_editorial_v1 import (  # noqa: E402
    FreeLLMAPIError, generate_draft, validate_local_url,
)


class StubResponse:
    headers = {"X-Routed-Via": "mock/mock-free-test-model", "X-Fallback-Attempts": "0"}

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
    assert payload["model"] == "mock-free-test-model"
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
    @classmethod
    def setUpClass(cls):
        cls.tempdir = tempfile.TemporaryDirectory()
        cls.policy = str(Path(cls.tempdir.name) / "free_policy.json")
        cls.valid_policy = {
            "schema": "free-llm-zero-cost-v1",
            "default_deny": True,
            "max_evidence_age_days": 7,
            "routes": [{
                "model": "mock-free-test-model",
                "provider": "mock",
                "enabled": True,
                "free_plan_verified": True,
                "commercial_use_terms_checked": True,
                "commercial_use_permitted": True,
                "billing_disabled_verified": True,
                "free_only_fallback_verified": True,
                "no_promo_credit_dependency": True,
                "input_usd_per_million": 0,
                "output_usd_per_million": 0,
                "official_evidence_url": "https://example.com/official-pricing",
                "verified_on": dt.datetime.now(dt.timezone.utc).date().isoformat()
            }],
        }
        Path(cls.policy).write_text(json.dumps(cls.valid_policy))

    @classmethod
    def tearDownClass(cls):
        cls.tempdir.cleanup()

    def active_env(self):
        return {**ENV, "FREELLMAPI_MODEL": "mock-free-test-model",
                "FREELLMAPI_ZERO_COST_POLICY": self.policy}

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
                data = generate_draft(task, "Public artwork title and verified notes", environ=self.active_env(),
                                      opener=mock_opener)
                self.assertEqual(data["status"], "draft_unreviewed")
                self.assertFalse(data["artistic_approval"])
                self.assertFalse(data["publication_authorized"])
                self.assertFalse(data["rights_verified"])
                self.assertEqual(data["routed_via"], "mock/mock-free-test-model")

    def test_no_unapproved_tasks(self):
        with self.assertRaisesRegex(FreeLLMAPIError, "Unsupported"):
            generate_draft("publish_video", "Publish now", environ=ENV, opener=mock_opener)

    def test_response_without_text_rejected(self):
        def blank(_req, timeout):
            return StubResponse(b'{"choices": [{"message": {"content": ""}}]}')
        with self.assertRaisesRegex(FreeLLMAPIError, "no usable text"):
            generate_draft("social", "Artwork", environ=self.active_env(), opener=blank)

    def test_large_response_rejected(self):
        def huge(_req, timeout):
            return StubResponse(b"X" * (524288 + 1))
        with self.assertRaisesRegex(FreeLLMAPIError, "size limit"):
            generate_draft("social", "Artwork", environ=self.active_env(), opener=huge)

    def test_zero_cost_rejects_auto_or_fusion(self):
        for alias in ("auto", "auto:smart", "fusion"):
            with self.subTest(alias=alias), self.assertRaises(ZeroCostPolicyError):
                admit(alias, self.valid_policy)

    def test_zero_cost_rejects_paid_or_unverified(self):
        def altered(**changes):
            policy = json.loads(json.dumps(self.valid_policy))
            policy["routes"][0].update(changes)
            return policy
        cases = [
            {"input_usd_per_million": 0.001},
            {"output_usd_per_million": 0.001},
            {"billing_disabled_verified": False},
            {"free_only_fallback_verified": False},
            {"commercial_use_permitted": False},
            {"free_plan_verified": False},
            {"no_promo_credit_dependency": False},
            {"official_evidence_url": ""},
            {"verified_on": "2020-01-01"},
        ]
        for case in cases:
            with self.subTest(case=case), self.assertRaises(ZeroCostPolicyError):
                admit("mock-free-test-model", altered(**case))

    def test_zero_cost_rejects_unlisted_model(self):
        with self.assertRaises(ZeroCostPolicyError):
            admit("unknown-free", self.valid_policy)

    def test_zero_cost_postcall_detects_fallback_or_mismatch(self):
        r = self.valid_policy["routes"][0]
        self.assertTrue(route_matches_actual(r, "mock/mock-free-test-model", "0"))
        self.assertFalse(route_matches_actual(r, "paid/other-model", "0"))
        self.assertFalse(route_matches_actual(r, "mock/mock-free-test-model", "1"))

    def test_client_rejects_auto_even_when_enabled(self):
        with self.assertRaisesRegex(FreeLLMAPIError, "admission denied"):
            generate_draft("social", "Artwork", environ={
                **ENV, "FREELLMAPI_ZERO_COST_POLICY": self.policy,
                "FREELLMAPI_MODEL": "auto",
            }, opener=mock_opener)

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
