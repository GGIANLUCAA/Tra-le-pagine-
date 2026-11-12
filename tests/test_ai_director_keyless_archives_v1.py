"""Regression suite: only already-installed keyless museum/archive sources.

All tests are offline; no key, media download, cost or publication.
"""
from pathlib import Path
import json
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import ai_director_keyless_archives_v1 as r


def catalogue(provider, *ids, calls=1):
    return {"provider": provider, "api_requests": calls,
            "items": [{"id": provider + ":" + str(i), "title": "Archive object " + str(i),
                       "date": "1896", "author": "Museum", "media_kind": "image",
                       "source_url": "https://www.loc.gov/item/" + str(i) + "/",
                       "license_claim": "Check individual license"} for i in ids]}


class KeylessTests(unittest.TestCase):
    def test_default_categories_stay_keyless(self):
        self.assertEqual(r.select_providers("art"), ("artic", "met", "cleveland"))
        self.assertEqual(r.select_providers("historical_video"), ("loc", "archive", "commons"))
        self.assertNotIn("europeana", r.ALLOWED)
        self.assertEqual(len(r.select_providers("general")), 3)
        with self.assertRaises(r.KeylessResearchError):
            r.select_providers("art", "europeana")

    def test_result_not_cleared_for_publication(self):
        calls = []
        def fake(provider, query, limit, fetcher=None):
            calls.append(provider)
            data = catalogue(provider, len(calls))
            data["items"][0]["media_kind"] = "video"
            return data
        with mock.patch.object(r, "search_public", side_effect=fake):
            found = r.research("Venice 1896", category="historical_video", per_provider=2)
        self.assertEqual(calls, ["loc", "archive", "commons"])
        self.assertEqual(found["candidate_count"], 3)
        self.assertFalse(found["key_required"])
        self.assertFalse(found["europeana_used"])
        self.assertFalse(found["paid_calls"])
        self.assertFalse(found["publication_authorized"])
        self.assertFalse(found["items"][0]["approved"])
        self.assertEqual(found["items"][0]["rights_review"], "pending")

    def test_invalid_query_stops_before_network(self):
        with mock.patch.object(r, "search_public", side_effect=AssertionError("network")):
            for bad in ("a", "x" * 101, "a\nb", 456):
                with self.assertRaises(r.KeylessResearchError):
                    r.research(bad)
            with self.assertRaises(r.KeylessResearchError):
                r.research("Proper query", category="invalid")

    def test_single_provider_manual(self):
        call = []
        def fake(provider, query, limit, fetcher=None):
            call.append((provider, limit))
            return catalogue(provider, 1)
        with mock.patch.object(r, "search_public", side_effect=fake):
            result = r.research("A historical city", selected="loc", per_provider=3)
        self.assertEqual(call, [("loc", 3)])
        self.assertEqual(result["api_requests_upper_bound"], 1)

    def test_provider_failure_does_not_block_other_sources(self):
        order = []
        def fake(provider, query, limit, fetcher=None):
            order.append(provider)
            if provider == "loc":
                raise ValueError("upstream error")
            data = catalogue(provider, len(order))
            data["items"][0]["media_kind"] = "video"
            return data
        with mock.patch.object(r, "search_public", side_effect=fake):
            data = r.research("Venice 1896", category="historical_video")
        self.assertEqual(order, ["loc", "archive", "commons"])
        self.assertEqual(data["providers"][0]["status"], "provider_unavailable_or_invalid")
        self.assertEqual(data["candidate_count"], 2)
        self.assertLessEqual(data["api_requests_upper_bound"], r.MAX_REQUESTS)

    def test_historical_video_does_not_admit_unrelated_museum_photos(self):
        def fake(provider, query, limit, fetcher=None):
            if provider == "commons":
                return {"provider": provider, "api_requests": 1, "items": [
                    {"id": "commons:painting", "title": "A Venetian Museum Artwork",
                     "source_url": "https://commons.wikimedia.org/wiki/File:Painting.jpg",
                     "media_kind": "image", "license_claim": "unverified"},
                    {"id": "commons:film", "title": "Panorama du Grand Canal 1896",
                     "source_url": "https://commons.wikimedia.org/wiki/File:Venise_1896.webm",
                     "media_kind": "video", "license_claim": "unverified"}]}
            return {"provider": provider, "api_requests": 1, "items": []}
        with mock.patch.object(r, "search_public", side_effect=fake):
            data = r.research("Venice 1896", category="historical_video", per_provider=2)
        self.assertEqual(data["candidate_count"], 1)
        self.assertEqual(data["items"][0]["media_kind"], "video")
        self.assertEqual(data["providers"][2]["excluded_by_media_kind"], 1)
        self.assertFalse(data["items"][0]["approved"])

    def test_historical_photo_does_not_admit_video(self):
        def fake(provider, query, limit, fetcher=None):
            return {"provider": provider, "api_requests": 1, "items": [
                {"id": "archive:film", "title": "Moving footage",
                 "source_url": "https://example.org/movie", "media_kind": "video"}]}
        with mock.patch.object(r, "search_public", side_effect=fake):
            data = r.research("Historic Paris 1900", category="historical_photo")
        self.assertEqual(data["candidate_count"], 0)
        self.assertEqual(sum(p.get("excluded_by_media_kind", 0) for p in data["providers"]), 3)

    def test_all_upstream_failures_do_not_fake_results(self):
        with mock.patch.object(r, "search_public", side_effect=OSError("down")):
            data = r.research("The city at night", category="art")
        self.assertEqual(data["candidate_count"], 0)
        self.assertEqual(data["status"], "no_candidates_or_sources_unavailable")
        self.assertFalse(data["rights_verified"])

    def test_duplicate_landing_pages_deduplicated(self):
        def fake(provider, query, limit, fetcher=None):
            return catalogue(provider, 1)
        with mock.patch.object(r, "search_public", side_effect=fake):
            data = r.research("A landscape painting", category="art")
        self.assertEqual(len(data["items"]), 1)

    def test_bridge_generates_report_without_video_or_ai(self):
        fake_result = {"schema": "ai-director-keyless-archives-v1", "key_required": False,
                       "europeana_used": False, "providers": [{"provider":"loc","status":"response_received"}],
                       "api_requests_upper_bound": 1, "candidate_count": 1,
                       "items": [{"provider": "loc", "title": "Historic footage",
                                 "date": "1903", "source_url": "https://www.loc.gov/item/1/",
                                 "license_claim": "unknown", "approved": False}]}
        brief = r.director_from_candidates(fake_result, "Paris 1903", "storia_rivive")
        self.assertEqual(brief["schema"], "ai-director-v1")
        self.assertFalse(brief["publication_authorized"])
        self.assertIn("NOT VERIFIED", brief["source_notes"][0]["license"])
        self.assertEqual(brief["scenes"], [])
        with tempfile.TemporaryDirectory() as d:
            report = r.export_result(fake_result, "Paris 1903", "storia_rivive", d)
            self.assertTrue((Path(d) / "director" / "ANDROID_REPORT.html").is_file())
            self.assertTrue((Path(d) / "DIRECTOR_BRIEF.json").is_file())
            self.assertFalse(report["sources_verified"])
            self.assertFalse(report["rights_verified"])

    def test_excludes_preapproved_candidates_from_other_input(self):
        example={"schema": "ai-director-keyless-archives-v1", "key_required":False,
                 "europeana_used":False, "items":[
                     {"approved":True,"source_url":"https://example.org/a"},
                     {"approved":False,"source_url":"https://example.org/b"}]}
        brief=r.director_from_candidates(example,"A new documentary")
        self.assertEqual(len(brief["source_notes"]),1)

    def test_dry_run_cli_never_uses_provider(self):
        with tempfile.TemporaryDirectory() as d:
            with mock.patch.object(r, "research", side_effect=AssertionError("Unexpected internet call")):
                self.assertEqual(r.main(["--query", "Venice 1896", "--output", d]), 0)
            data=json.loads((Path(d)/"CANDIDATES.json").read_text())
            self.assertEqual(data["api_requests_upper_bound"],0)
            self.assertFalse(data["europeana_used"])

    def test_loc_public_adapter_parsing_under_fake_fetcher(self):
        def http_result(url):
            self.assertTrue(url.startswith("https://www.loc.gov/search/"))
            return {"results": [{"id":"https://www.loc.gov/item/123/",
                                 "title":"1906 San Francisco street",
                                 "original_format":["Motion Pictures"],
                                 "contributor":["Library of Congress"],"date":"1906"}]}
        out = r.research("San Francisco 1906", category="historical_video",
                         selected="loc", fetcher=http_result)
        self.assertEqual(out["items"][0]["provider"], "loc")
        self.assertEqual(out["items"][0]["media_kind"], "video")
        self.assertEqual(out["api_requests_upper_bound"], 1)

    def test_artic_public_adapter_parsing_under_fake_fetcher(self):
        def http_result(url):
            self.assertIn("api.artic.edu/api/v1/artworks/search", url)
            return {"data": [{"id":12345,"title":"An Old Painting",
                              "artist_display":"Artist","date_display":"1800",
                              "is_public_domain":True,
                              "image_id":"abcde1234"}]}
        out = r.research("Old painting", category="art", selected="artic", fetcher=http_result)
        self.assertEqual(out["items"][0]["provider"], "artic")
        self.assertEqual(out["items"][0]["rights_review"], "pending")
        self.assertFalse(out["items"][0]["downloaded"])


if __name__ == "__main__":
    unittest.main()
