#!/usr/bin/env python3
"""No-network regression tests for AI Director V1."""
import datetime as dt
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import ai_director_v1 as d


def route(model):
    return {
        "model": model, "enabled": True, "provider": "openrouter",
        "free_plan_verified": True, "commercial_use_terms_checked": True,
        "commercial_use_permitted": True, "billing_disabled_verified": True,
        "free_only_fallback_verified": True, "no_promo_credit_dependency": True,
        "input_usd_per_million": 0, "output_usd_per_million": 0,
        "official_evidence_url": "https://openrouter.ai/models",
        "verified_on": dt.datetime.now(dt.timezone.utc).date().isoformat(),
    }


def policy(models):
    return {"schema": "free-llm-zero-cost-v1", "default_deny": True,
            "max_evidence_age_days": 7, "routes": [route(m) for m in models]}


class DirectorTests(unittest.TestCase):
    def setUp(self):
        self.brief = d.make_brief("documentario", "Roma nel 1900")
        self.models = ["provider/model-one:free", "provider/model-two:free"]

    def test_brief_unapproved(self):
        self.assertFalse(self.brief["human_artistic_approval"])
        self.assertFalse(self.brief["publication_authorized"])

    def test_no_scenes_never_passes_artistic_qa(self):
        issues = d.audit_scenes(self.brief)
        self.assertEqual(issues[0]["code"], "NO_STORYBOARD")
        r = d.base_report(self.brief, issues, {"status": "not_checked"})
        self.assertEqual(r["status"], "needs_artistic_review")
        self.assertFalse(r["video_seen_by_ai"])

    def test_reject_faked_human_approval(self):
        self.brief["human_artistic_approval"] = True
        with self.assertRaises(ValueError):
            d.audit_scenes(self.brief)

    def test_flags_micro_flash_and_scene_gaps(self):
        self.brief["scenes"] = [
            {"start_s": 0, "end_s": 0.2, "asset_id": "a", "rights_status": "verified"},
            {"start_s": 2, "end_s": 4, "asset_id": "b", "rights_status": "verified"},
        ]
        codes = [x["code"] for x in d.audit_scenes(self.brief)]
        self.assertIn("MICRO_FLASH", codes)
        self.assertIn("UNEXPLAINED_GAP", codes)

    def test_narration_visual_mismatch(self):
        self.brief["narration"] = "Qui si vede un carro"
        self.brief["scenes"] = [
            {"start_s": 0, "end_s": 3, "asset_id": "frame1",
             "spoken_detail_id": "carro", "visual_detail_id": "finestra",
             "rights_status": "verified"}
        ]
        self.assertIn("VOICE_VISUAL_MISMATCH", [x["code"] for x in d.audit_scenes(self.brief)])

    def test_museum_provenance_blocks(self):
        b = d.make_brief("artvision_4x1", "The Night Watch")
        b["scenes"] = [{"start_s": 0, "end_s": 4, "asset_id": "gallery",
                        "kind": "gallery_entry", "rights_status": "licensed"}]
        self.assertIn("MUSEUM_SCALE_UNVERIFIED", [x["code"] for x in d.audit_scenes(b)])

    def test_unsafe_model_rejected_before_call(self):
        self.assertRaises(ValueError, d._approved_models,
                          ["anthropic/claude-opus-4.6", self.models[1]], policy(self.models))
        self.assertRaises(ValueError, d._approved_models,
                          ["openrouter/free", self.models[1]], policy(self.models))

    def test_empty_default_policy_prevents_any_calls(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "policy.json"
            p.write_text(json.dumps(policy([])))
            called = []
            with self.assertRaises(Exception):
                d.compare(self.brief, self.models, p, execute=True,
                          environ={"AI_DIRECTOR_ALLOW_FREE_CALLS": "1", "OPENROUTER_API_KEY": "secret"},
                          transport=lambda *x: called.append(x))
            self.assertEqual(called, [])

    def test_opt_in_required_even_when_models_approved(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "policy.json"
            p.write_text(json.dumps(policy(self.models)))
            with self.assertRaisesRegex(RuntimeError, "Explicit opt-in"):
                d.compare(self.brief, self.models, p, execute=True,
                          environ={"OPENROUTER_API_KEY": "secret"})
            self.assertEqual(d.compare(self.brief, self.models, p)["model_calls"], 0)

    def test_exactly_two_calls_no_retry(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "policy.json"
            p.write_text(json.dumps(policy(self.models)))
            requests = []
            def fake(model, prompt, key):
                requests.append((model, prompt, key))
                return "specific unapproved draft"
            r = d.compare(self.brief, self.models, p, execute=True,
                          environ={"OPENROUTER_API_KEY": "mock", "AI_DIRECTOR_ALLOW_FREE_CALLS": "1"},
                          transport=fake)
            self.assertEqual(r["model_calls"], 2)
            self.assertEqual(len(requests), 2)
            self.assertEqual(r["status"], "draft_unreviewed")
            self.assertFalse(r["publication_authorized"])

    def test_openrouter_request_hard_zero_price_and_no_fallback(self):
        import urllib.request
        sent = []
        model = "provider/model-one:free"
        class Response:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self, limit):
                return json.dumps({
                    "model": model,
                    "choices": [{"message": {"content": "Proposta non approvata"}}],
                }).encode()
        def fake_urlopen(req, timeout):
            body = json.loads(req.data.decode("utf-8"))
            sent.append(body)
            self.assertEqual(body["model"], model)
            self.assertEqual(body["provider"]["max_price"],
                             {"prompt": 0, "completion": 0})
            self.assertIs(body["provider"]["allow_fallbacks"], False)
            self.assertEqual(timeout, 35)
            return Response()
        with mock.patch.object(urllib.request, "urlopen", side_effect=fake_urlopen):
            result = d._ask_openrouter(model, "Cerca coerenza narrativa.", "placeholder")
        self.assertEqual(result, "Proposta non approvata")
        self.assertEqual(len(sent), 1)

    def test_failure_never_retries(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "policy.json"
            p.write_text(json.dumps(policy(self.models)))
            calls = []
            def fake(model, prompt, key):
                calls.append(model)
                raise RuntimeError("mock provider refused")
            r = d.compare(self.brief, self.models, p, execute=True,
                          environ={"OPENROUTER_API_KEY": "mock", "AI_DIRECTOR_ALLOW_FREE_CALLS": "1"},
                          transport=fake)
            self.assertEqual(calls, [self.models[0]])
            self.assertEqual(r["model_calls"], 1)
            self.assertEqual(r["status"], "partial_failed_no_retry")

    def test_html_escapes_untrusted_text(self):
        report = d.base_report(self.brief, [d.issue("<script>", "warning", "<b>x</b>")],
                               {"status": "not_checked"})
        s = d.dashboard(report)
        self.assertNotIn("<script>", s)
        self.assertNotIn("<b>x</b>", s)
        self.assertIn("&lt;script&gt;", s)

    def test_report_serializable_without_api(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(d.main(["--format", "giuliano", "--subject", "Gli scavi di Pompei",
                                     "--mode", "plan", "--out-dir", tmp]), 0)
            report = json.loads((Path(tmp) / "REPORT.json").read_text())
            self.assertEqual(report["model_calls"], 0)
            self.assertEqual(report["billing_actions"], 0)
            self.assertFalse(report["human_artistic_approval"])
            self.assertTrue((Path(tmp) / "ANDROID_REPORT.html").exists())

    def test_validates_bad_timecode(self):
        self.brief["scenes"] = [{"start_s": "bad", "end_s": 2}]
        self.assertIn("BAD_TIMECODE", [x["code"] for x in d.audit_scenes(self.brief)])

    def test_prompts_no_fake_citations(self):
        p = d.editorial_prompts(self.brief)
        self.assertIn("do not invent", p["director"].lower())
        self.assertIn("unapproved", p["critic"].lower())


if __name__ == "__main__":
    unittest.main()
