"""Gemini still-image and Groq ASR connectors: offline tests; no API keys charged."""
import datetime as dt
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import ai_director_external_apis_v1 as api


class FakeHTTP:
    def __init__(self, body):
        self.payload = json.dumps(body).encode()
        self.headers = {"Content-Length": str(len(self.payload))}
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def read(self, max_bytes):
        return self.payload[:max_bytes]


def approved(service, model, price=0):
    return {
        "schema": "ai-director-external-api-policy-v1", "default_deny": True,
        "routes": [{
            "service": service, "model": model, "enabled": True,
            "no_charge_verified": True, "commercial_terms_checked": True,
            "commercial_use_permitted": True,
            "billing_disabled_verified": True, "no_paid_fallback_verified": True,
            "account_limit_checked": True,
            "input_usd_per_million": price, "output_usd_per_million": price,
            "cost_per_audio_hour_usd": price,
            "official_evidence_url": "https://example.org/model-terms",
            "verified_on": dt.datetime.now(dt.timezone.utc).date().isoformat()
        }]}


class ExternalClientTests(unittest.TestCase):
    def test_default_policy_blocks_all_live_inference(self):
        p = api.load_policy()
        self.assertTrue(p["default_deny"])
        self.assertEqual(p["routes"], [])
        with mock.patch.dict(os.environ, {"AI_DIRECTOR_EXTERNAL_LIVE": "1"}):
            for service, model in [("gemini_image","gemini-2.5-flash"),
                                   ("groq_transcription","whisper-large-v3-turbo")]:
                with self.assertRaises(api.ExternalAPIError):
                    api._admit_live(service, model, p)

    def test_only_account_verified_zero_price_route_admitted(self):
        with mock.patch.dict(os.environ, {"AI_DIRECTOR_EXTERNAL_LIVE": "1"}):
            with self.assertRaisesRegex(api.ExternalAPIError, "exactly zero"):
                api._admit_live("groq_transcription", "whisper-large-v3-turbo",
                                approved("groq_transcription","whisper-large-v3-turbo",price=0.1))

    def test_live_flag_is_required_even_for_mocked_approved_route(self):
        with mock.patch.dict(os.environ, {"AI_DIRECTOR_EXTERNAL_LIVE": "0"}):
            with self.assertRaisesRegex(api.ExternalAPIError, "disabled"):
                api._admit_live("gemini_image","gemini-2.5-flash",
                                approved("gemini_image","gemini-2.5-flash"))

    def test_no_gemini_network_without_plan_verification(self):
        with tempfile.TemporaryDirectory() as d:
            image=Path(d)/"frame.png"
            image.write_bytes(b"\x89PNG\r\n\x1a\n"+b"\x00"*128)
            with mock.patch.dict(os.environ, {"AI_DIRECTOR_EXTERNAL_LIVE": "1"}):
                with self.assertRaises(api.ExternalAPIError):
                    api.gemini_frame_review(image, model="gemini-2.5-flash",
                        prompt="Describe scene details without claiming a full video review",
                        key="test-only",
                        policy=api.load_policy(),
                        transport=lambda *args,**kw: self.fail("network request not permitted"))

    def test_no_groq_network_without_plan_verification(self):
        with tempfile.TemporaryDirectory() as d:
            audio=Path(d)/"voice.wav";audio.write_bytes(b"RIFF"+b"\x00"*300)
            with mock.patch.dict(os.environ, {"AI_DIRECTOR_EXTERNAL_LIVE": "1"}):
                with self.assertRaises(api.ExternalAPIError):
                    api.groq_transcription(audio, model="whisper-large-v3-turbo",
                        key="test-only",policy=api.load_policy(),
                        transport=lambda *args,**kw:self.fail("network not permitted"))

    def test_mock_gemini_single_frame_only(self):
        with tempfile.TemporaryDirectory() as d:
            image=Path(d)/"frame.png";image.write_bytes(b"\x89PNG\r\n\x1a\n"+b"\x01"*300)
            calls=[]
            def fake(req, timeout):
                calls.append(req)
                data=json.loads(req.data)
                self.assertEqual(data["contents"][0]["parts"][1]["inline_data"]["mime_type"],"image/png")
                return FakeHTTP({"candidates":[{"content":{"parts":[{"text":"Single frame only"}]}}]})
            with mock.patch.dict(os.environ, {"AI_DIRECTOR_EXTERNAL_LIVE": "1"}):
                result=api.gemini_frame_review(image,model="gemini-2.5-flash",
                    key="fixture",prompt="Review the one image and be precise",
                    policy=approved("gemini_image","gemini-2.5-flash"),transport=fake)
            self.assertEqual(result["text"], "Single frame only")
            self.assertFalse(result["full_video_watched"])
            self.assertFalse(result["auto_publish"])
            self.assertEqual(len(calls),1)

    def test_mock_groq_segment_stamps_only(self):
        with tempfile.TemporaryDirectory() as d:
            audio=Path(d)/"voice.wav";audio.write_bytes(b"RIFF"+b"\x00"*300)
            calls=[]
            def fake(req, timeout):
                calls.append(req)
                self.assertIn(b'name="timestamp_granularities[]"',req.data)
                self.assertNotIn(b"fixture",req.data)
                return FakeHTTP({"text":"Buongiorno","segments":[{"start":0,"end":1.7,"text":"Buongiorno"}]})
            with mock.patch.dict(os.environ, {"AI_DIRECTOR_EXTERNAL_LIVE": "1"}):
                result=api.groq_transcription(audio,model="whisper-large-v3-turbo",
                    key="fixture",policy=approved("groq_transcription","whisper-large-v3-turbo"),
                    transport=fake)
            self.assertEqual(result["segments"][0]["end_s"],1.7)
            self.assertFalse(result["visual_alignment_verified"])
            self.assertEqual(len(calls),1)

    def test_inventory_neither_exposes_key_nor_mentions_europeana(self):
        with tempfile.TemporaryDirectory() as d:
            output=Path(d)/"report.json"
            with mock.patch.dict(os.environ, {"GEMINI_API_KEY":"opaque-example-not-real"}), \
                 mock.patch("sys.argv", ["adapter","--mode","inventory","--output",str(output)]):
                self.assertEqual(api.main(),0)
            report=output.read_text()
            self.assertNotIn("opaque-example-not-real",report)
            self.assertNotIn("EUROPEANA",report)
            self.assertTrue(json.loads(report)["credentials_present"]["GEMINI_API_KEY"])


if __name__ == "__main__":
    unittest.main()
