"""All tests offline; no provider keys, purchases, inference, or live network."""
import datetime as dt
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ai_free_catalog_audit_v2 import (  # noqa: E402
    CatalogError, TARGETS, MAX_BYTES, fetch_catalog, review_snapshot,
)


DAY = dt.date(2026, 11, 4)


def provider(slug="groq", **changes):
    result = {
        "slug": slug,
        "verified": True,
        "last_verified": "2026-11-03",
        "category": "ongoing",
        "free_type": "renewing-quota",
        "card_required": False,
        "phone_required": True,
        "commercial_ok": True,
        "is_text_llm": True,
        "docs_url": "https://console.groq.com/docs/rate-limits",
        "modalities": ["text", "audio"],
        "models_free": ["openai/gpt-oss-120b"],
        "notes": "Review usage limits before enabling.",
    }
    result.update(changes)
    return result


def snapshot(providers=None, generated="2026-11-04"):
    return {
        "version": "9.0.0",
        "generated": generated,
        "providers": [provider()] if providers is None else providers,
    }


class CatalogTests(unittest.TestCase):
    def test_verified_provider_only_candidate_not_enabled(self):
        result = review_snapshot(snapshot(), today=DAY)
        self.assertEqual(result["status"], "read_only_no_providers_enabled")
        self.assertEqual(result["provider_calls_performed"], 0)
        self.assertFalse(result["automatic_provider_activation"])
        self.assertFalse(result["billing_state_verified"])
        groq = next(x for x in result["candidates"] if x["provider"] == "groq")
        self.assertEqual(groq["status"], "candidate_manual_review")
        self.assertFalse(groq["may_call_api"])
        self.assertEqual(len(result["candidates"]), len(TARGETS))

    def test_trials_credits_unknown_cards_and_commercial_block(self):
        variants = [
            {"category": "trial"},
            {"free_type": "trial-credit"},
            {"free_type": "recurring-credit"},
            {"card_required": True},
            {"card_required": None},
            {"commercial_ok": False},
            {"commercial_ok": None},
            {"verified": False},
            {"last_verified": "2024-01-01"},
            {"docs_url": "http://insecure.example/pricing"},
            {"is_text_llm": False},
        ]
        for variant in variants:
            with self.subTest(variant=variant):
                result = review_snapshot(snapshot([provider(**variant)]), today=DAY)
                candidate = next(x for x in result["candidates"] if x["provider"] == "groq")
                self.assertEqual(candidate["status"], "hold_reverification_needed")
                self.assertFalse(candidate["may_call_api"])

    def test_missing_provider_is_reported_without_guessing(self):
        data = review_snapshot(snapshot([]), today=DAY)
        self.assertEqual(len(data["candidates"]), len(TARGETS))
        self.assertTrue(all(x["status"] == "unavailable_in_catalog" for x in data["candidates"]))

    def test_stale_dataset_or_duplicate_provider_rejected(self):
        with self.assertRaises(CatalogError):
            review_snapshot(snapshot(generated="2024-01-01"), today=DAY)
        with self.assertRaises(CatalogError):
            review_snapshot(snapshot([provider(), provider()]), today=DAY)

    def test_future_dated_proof_rejected(self):
        result = review_snapshot(snapshot([provider(last_verified="2027-01-01")]), today=DAY)
        groq = next(x for x in result["candidates"] if x["provider"] == "groq")
        self.assertEqual(groq["status"], "hold_reverification_needed")

    def test_local_compute_not_claimed_zero_cost_total(self):
        r = review_snapshot(snapshot(), today=DAY)
        self.assertEqual({p["engine"] for p in r["local_options"]},
                         {"Ollama", "llama.cpp", "LocalAI"})
        self.assertTrue(all("Hardware" in p["note"] for p in r["local_options"]))

    def test_refresh_fetch_uses_only_public_github_json_and_size_limit(self):
        class Response:
            def __init__(self, raw):
                self.raw = raw
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return None
            def read(self, n):
                return self.raw[:n]
        seen = {}
        def fake(req, timeout):
            seen["url"] = req.full_url
            seen["timeout"] = timeout
            return Response(json.dumps(snapshot()).encode("utf-8"))
        data = fetch_catalog(opener=fake)
        self.assertEqual(data["version"], "9.0.0")
        self.assertEqual(seen["url"],
                         "https://raw.githubusercontent.com/pacocartones/free-llm-api-hub/main/data/providers.json")
        self.assertLessEqual(seen["timeout"], 20)
        with self.assertRaises(CatalogError):
            fetch_catalog(opener=lambda req, timeout: Response(b"x" * (MAX_BYTES + 1)))

    def test_snapshot_written_without_tokens_or_provider_calls(self):
        from ai_free_catalog_audit_v2 import main
        with tempfile.TemporaryDirectory() as root:
            p = Path(root) / "hub.json"
            q = Path(root) / "report.json"
            p.write_text(json.dumps(snapshot()), encoding="utf-8")
            old = sys.argv
            try:
                sys.argv = ["catalog", "--snapshot", str(p), "--report", str(q)]
                self.assertEqual(main(), 0)
            finally:
                sys.argv = old
            report = json.loads(q.read_text(encoding="utf-8"))
            self.assertFalse(report["automatic_provider_activation"])
            self.assertEqual(report["provider_calls_performed"], 0)


if __name__ == "__main__":
    unittest.main()
