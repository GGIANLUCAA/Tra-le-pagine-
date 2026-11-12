"""Offline no-network tests for API adapters and their billing safeguards."""
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
import ai_director_europeana_bridge_v1 as bridge


class FakeHTTP:
    def __init__(self, json_body, status=200):
        self.payload = json.dumps(json_body).encode()
        self.headers = {"Content-Length": str(len(self.payload))}
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def read(self, length):
        return self.payload[:length]


def approved(service, model):
    return {"schema": "ai-director-external-api-policy-v1", "default_deny": True,
            "routes": [{
                "service": service, "model": model, "enabled": True,
                "no_charge_verified": True, "commercial_terms_checked": True,
                "commercial_use_permitted": True,
                "billing_disabled_verified": True, "no_paid_fallback_verified": True,
                "account_limit_checked": True, "input_usd_per_million": 0,
                "output_usd_per_million": 0, "cost_per_audio_hour_usd": 0,
                "official_evidence_url": "https://example.org/terms/model",
                "verified_on": dt.datetime.now(dt.timezone.utc).date().isoformat()
            }]}


class AdapterTests(unittest.TestCase):
    def test_default_policy_denies_live_provider_calls(self):
        policy = api.load_policy(ROOT / "config/ai_director_external_api_v1.json")
        self.assertTrue(policy["default_deny"])
        self.assertEqual(policy["routes"], [])
        with mock.patch.dict(os.environ, {"AI_DIRECTOR_EXTERNAL_LIVE": "1"}):
            with self.assertRaisesRegex(api.ExternalAPIError, "not explicitly approved"):
                api._admit_live("gemini_image", "gemini-2.5-flash", policy)

    def test_europeana_uses_header_not_query_key(self):
        captured = []
        def fake(req, timeout):
            captured.append(req)
            return FakeHTTP({"success": True, "items": [
                {"id": "/92005/BibliographicResource_300012", "title": ["Venezia 1896"],
                 "type": "IMAGE", "guid": "https://www.europeana.eu/en/item/xx",
                 "rights": ["http://creativecommons.org/publicdomain/mark/1.0/"]}]})
        r = api.europeana_search("Venezia 1896", key="fake-key-do-not-share",
                                 limit=3, transport=fake)
        self.assertEqual(len(captured), 1)
        req = captured[0]
        self.assertEqual(req.get_method(), "GET")
        self.assertIn("query=Venezia+1896", req.full_url)
        self.assertNotIn("fake-key", req.full_url)
        self.assertEqual(req.get_header("X-api-key"), "fake-key-do-not-share")
        self.assertEqual(r["api_requests"], 1)
        self.assertFalse(r["items"][0]["approved"])
        self.assertEqual(r["items"][0]["rights_review"], "pending")
        self.assertNotIn("fake-key", json.dumps(r))

    def test_europeana_drops_unsafe_links_and_tags(self):
        def fake(req, timeout):
            return FakeHTTP({"success": True, "items": [{
                "id": "1", "title": ["<b>Artwork</b>"],
                "guid": "http://unsafe.example/x",
                "rights": ["unknown"], "edmPreview": ["http://unsafe.example/y"]}]})
        result=api.europeana_search("artwork",key="dummy",transport=fake)
        item=result["items"][0]
        self.assertEqual(item["title"], "Artwork")
        self.assertTrue(item["source_url"].startswith("https://www.europeana.eu/"))
        self.assertEqual(item["preview_url_unverified"], "")
        self.assertFalse(item["media_downloaded"])

    def test_europeana_fails_on_invalid_query_before_request(self):
        with self.assertRaises(api.ExternalAPIError):
            api.europeana_search("a",key="safe",transport=lambda *args, **kwargs: self.fail("network"))
        with self.assertRaises(api.ExternalAPIError):
            api.europeana_search("Long name",key="",transport=lambda *args, **kwargs: self.fail("network"))
        with self.assertRaises(api.ExternalAPIError):
            api.europeana_search("Long name",key="x",limit=100,transport=lambda *args, **kwargs: self.fail("network"))

    def test_groq_whisper_cannot_be_called_unverified(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"speech.wav"
            f.write_bytes(b"RIFF"+b"\x00"*200)
            with mock.patch.dict(os.environ, {"AI_DIRECTOR_EXTERNAL_LIVE": "1"}):
                with self.assertRaises(api.ExternalAPIError):
                    api.groq_transcription(f,model="whisper-large-v3-turbo",key="dummy",
                        policy=api.load_policy(),transport=lambda *x, **kw: self.fail("network"))
            self.assertTrue(f.exists())

    def test_gemini_cannot_be_called_unverified(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"frame.jpg"
            f.write_bytes(b"\xff\xd8\xff"+b"\x01"*200)
            with mock.patch.dict(os.environ, {"AI_DIRECTOR_EXTERNAL_LIVE": "1"}):
                with self.assertRaises(api.ExternalAPIError):
                    api.gemini_frame_review(f,model="gemini-2.5-flash",key="dummy",
                        prompt="Review the visual rhythm with care.",
                        policy=api.load_policy(),transport=lambda *x, **kw: self.fail("network"))

    def test_manual_gemini_payload_single_frame(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"frame.png"
            f.write_bytes(b"\x89PNG\r\n\x1a\n"+b"\x01"*300)
            received=[]
            def fake(req, timeout):
                payload=json.loads(req.data)
                self.assertIn("generateContent", req.full_url)
                self.assertEqual(req.get_header("X-goog-api-key"),"dummy")
                parts=payload["contents"][0]["parts"]
                self.assertEqual(parts[1]["inline_data"]["mime_type"],"image/png")
                received.append(payload)
                return FakeHTTP({"candidates":[{"content":{"parts":[{"text":"Frame review only"}]}}]})
            with mock.patch.dict(os.environ, {"AI_DIRECTOR_EXTERNAL_LIVE": "1"}):
                result=api.gemini_frame_review(f,model="gemini-2.5-flash",key="dummy",
                    prompt="Assess the details visible in this frame.",
                    policy=approved("gemini_image","gemini-2.5-flash"),transport=fake)
            self.assertEqual(result["text"],"Frame review only")
            self.assertFalse(result["full_video_watched"])
            self.assertEqual(len(received),1)

    def test_manual_groq_payload_segment_timestamps(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"speech.wav"; f.write_bytes(b"RIFF"+b"\x00"*300)
            received=[]
            def fake(req, timeout):
                self.assertIn(b'verbose_json',req.data)
                self.assertIn(b'name="timestamp_granularities[]"',req.data)
                self.assertNotIn(b"dummy", req.data)
                received.append(req)
                return FakeHTTP({"text":"Ciao Venezia","segments":[{"start":0,"end":2.1,"text":"Ciao Venezia"}]})
            with mock.patch.dict(os.environ, {"AI_DIRECTOR_EXTERNAL_LIVE": "1"}):
                result=api.groq_transcription(f,model="whisper-large-v3-turbo",
                    key="dummy",policy=approved("groq_transcription","whisper-large-v3-turbo"),
                    transport=fake)
            self.assertEqual(len(received),1)
            self.assertEqual(result["segments"][0]["end_s"],2.1)
            self.assertFalse(result["visual_alignment_verified"])

    def test_europeana_candidates_flow_into_existing_ai_director(self):
        research = {
            "schema": "ai-director-europeana-research-v1",
            "provider": "europeana", "api_requests": 1,
            "items": [
                {"id": "europeana:1", "title": "Venezia nel 1896",
                 "date": "1896", "source_url": "https://www.europeana.eu/en/item/1",
                 "rights_claim": "CC0 candidate, not inspected", "approved": False}
            ]}
        result=bridge.prepare(research,"Venezia 1896")
        self.assertEqual(result["schema"], "ai-director-v1")
        self.assertFalse(result["publication_authorized"])
        self.assertTrue(result["research_candidates_only"])
        self.assertEqual(len(result["source_notes"]),1)
        self.assertIn("UNVERIFIED",result["source_notes"][0]["license"])
        import ai_director_v1 as director
        prompts = director.editorial_prompts(result)
        self.assertIn("Venezia nel 1896",prompts["director"])
        with tempfile.TemporaryDirectory() as d:
            inp=Path(d)/"europeana.json"
            dest=Path(d)/"brief.json"
            rep=Path(d)/"report"
            inp.write_text(json.dumps(research))
            self.assertEqual(bridge.main(["--input",str(inp),"--subject","Venezia 1896",
                                          "--output",str(dest),"--report-dir",str(rep)]),0)
            self.assertTrue((rep/"ANDROID_REPORT.html").exists())
            r=json.loads((rep/"REPORT.json").read_text())
            self.assertFalse(r["publication_authorized"])
            self.assertFalse(r["sources_verified"])
            self.assertEqual(r["europeana_candidate_count"],1)

    def test_europeana_cli_offline_never_calls_network(self):
        with tempfile.TemporaryDirectory() as d:
            output=Path(d)/"status.json"
            with mock.patch("sys.argv",["api","--mode","europeana","--output",str(output)]), \
                 mock.patch("ai_director_external_apis_v1.europeana_search",side_effect=AssertionError("Unexpected network")):
                self.assertEqual(api.main(),0)
            self.assertEqual(json.loads(output.read_text())["status"],"europeana_dry_run_no_request")

    def test_inventory_does_not_expose_credential(self):
        with tempfile.TemporaryDirectory() as d:
            output=Path(d)/"status.json"
            with mock.patch.dict(os.environ,{"EUROPEANA_API_KEY":"top-secret-not-for-output"}), \
                 mock.patch("sys.argv",["api","--mode","inventory","--output",str(output)]):
                self.assertEqual(api.main(),0)
            report=output.read_text()
            self.assertNotIn("top-secret",report)
            self.assertTrue(json.loads(report)["credentials_present"]["EUROPEANA_API_KEY"])


if __name__ == "__main__":
    unittest.main()
