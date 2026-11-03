"""Groq direct API safety tests: only stubs, no secrets or network calls."""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from groq_editorial_v1 import (  # noqa: E402
    GroqError, API_URL, generate_groq_draft,
)


MODEL = "openai/gpt-oss-120b"


class Response:
    def __init__(self, body):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def read(self, _size):
        return self.body


def good_response(content="A thoughtful caption about Rembrandt."):
    return Response(json.dumps({
        "model": MODEL,
        "choices": [{"message": {"content": content}}],
    }).encode("utf-8"))


def fake_opener(req, timeout):
    assert req.full_url == API_URL
    assert req.method == "POST"
    assert req.get_header("Authorization") == "Bearer fixture-only-key"
    assert timeout <= 30
    posted = json.loads(req.data)
    assert posted["model"] == MODEL
    assert posted["max_tokens"] <= 600
    return good_response()


class GroqAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.policy_path = str(Path(cls.directory.name) / "policy.json")
        cls.free_route = {
            "model": MODEL,
            "provider": "groq",
            "enabled": True,
            "free_plan_verified": True,
            "commercial_use_terms_checked": True,
            "commercial_use_permitted": True,
            "billing_disabled_verified": True,
            "free_only_fallback_verified": True,
            "no_promo_credit_dependency": True,
            "input_usd_per_million": 0,
            "output_usd_per_million": 0,
            "official_evidence_url": "https://console.groq.com/docs/rate-limits",
            "verified_on": dt.datetime.now(dt.timezone.utc).date().isoformat(),
        }
        cls.policy = {
            "schema": "free-llm-zero-cost-v1",
            "default_deny": True,
            "max_evidence_age_days": 7,
            "routes": [cls.free_route],
        }
        Path(cls.policy_path).write_text(json.dumps(cls.policy), encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def env(self):
        return {
            "GROQ_EDITORIAL_ENABLED": "1",
            "GROQ_API_KEY": "fixture-only-key",
            "GROQ_MODEL": MODEL,
            "GROQ_ZERO_COST_POLICY": self.policy_path,
        }

    def test_disabled_by_default_even_if_key_exists(self):
        env = self.env()
        env["GROQ_EDITORIAL_ENABLED"] = "0"
        with self.assertRaisesRegex(GroqError, "Disabled"):
            generate_groq_draft("social", "Test", environ=env, opener=fake_opener)

    def test_unverified_default_registry_cannot_call(self):
        env = self.env()
        del env["GROQ_ZERO_COST_POLICY"]
        with self.assertRaisesRegex(GroqError, "route denied"):
            generate_groq_draft("social", "Test", environ=env, opener=fake_opener)

    def test_missing_key_rejected(self):
        env = self.env()
        del env["GROQ_API_KEY"]
        with self.assertRaisesRegex(GroqError, "GROQ_API_KEY"):
            generate_groq_draft("social", "Test", environ=env, opener=fake_opener)

    def test_only_editorial_tasks(self):
        with self.assertRaisesRegex(GroqError, "Unsupported"):
            generate_groq_draft("render_video", "Test", environ=self.env(), opener=fake_opener)

    def test_valid_response_is_unapproved(self):
        for task in ("social", "narration", "storyboard", "source_notes", "qa_second_opinion"):
            with self.subTest(task=task):
                result = generate_groq_draft(task, "A supplied museum note", environ=self.env(), opener=fake_opener)
                self.assertEqual(result["status"], "draft_unreviewed")
                self.assertFalse(result["publication_authorized"])
                self.assertFalse(result["artistic_approval"])
                self.assertFalse(result["rights_verified"])
                self.assertFalse(result["cost_guaranteed"])
                self.assertEqual(result["model"], MODEL)

    def test_public_name_forbidden(self):
        def unsafe(req, timeout):
            return good_response("ArtVision presents an artwork")
        with self.assertRaisesRegex(GroqError, "V134"):
            generate_groq_draft("social", "A verified source note",
                                environ=self.env(), opener=unsafe)

    def test_mismatched_model_rejected(self):
        def wrong(req, timeout):
            return Response(b'{"model":"not-requested","choices":[{"message":{"content":"test"}}]}')
        with self.assertRaisesRegex(GroqError, "Unexpected model"):
            generate_groq_draft("social", "Test", environ=self.env(), opener=wrong)

    def test_dry_run_does_not_create_file(self):
        with tempfile.TemporaryDirectory() as directory:
            prompt = Path(directory) / "prompt.txt"
            output = Path(directory) / "output.json"
            prompt.write_text("Museum source note", encoding="utf-8")
            proc = subprocess.run([
                sys.executable, str(SRC / "groq_editorial_v1.py"),
                "--task", "social", "--prompt-file", str(prompt),
                "--output", str(output),
            ], check=True, capture_output=True, text=True, env={
                **os.environ, "GROQ_EDITORIAL_ENABLED": "0",
            })
            self.assertIn("DRY_RUN_ONLY", proc.stdout)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
