"""Regression tests of the no-key/secret bridge. All tests run without network."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.parse

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("free_sources_bridge_v1", ROOT/"src/free_sources_bridge_v1.py")
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)


class SourceBridgeTests(unittest.TestCase):
    def test_01_secret_presence_does_not_expose_values(self):
        env = {"PIXABAY": "my-sensitive-value", "OPENROUTER2": "secret-router", "PRIXIBAY2": "second"}
        result = bridge.produce("status", "", "image", 3, env)
        s = str(result)
        self.assertTrue(result["configuration"]["pixabay_ready"])
        self.assertTrue(result["configuration"]["secrets_presence_only"]["OPENROUTER2"])
        for secret in env.values():
            self.assertNotIn(secret, s)

    def test_02_dry_run_makes_no_external_request(self):
        with patch.object(bridge, "fetch_json", side_effect=AssertionError("Unexpected web call")):
            result = bridge.produce("plan", "", "image", 3)
        self.assertFalse(result["automatic_download"])
        self.assertFalse(result["automatic_publish"])

    def test_03_pixabay_is_single_candidate_search(self):
        fixture = {"hits":[
            {"id":1234, "pageURL":"https://pixabay.com/photos/trees-1234/",
             "imageWidth":1200,"imageHeight":1800,"tags":"garden", "user":"Artist",
             "webformatURL":"https://cdn.pixabay.com/photo/example_640.jpg"},
            {"id":2345, "pageURL":"https://pixabay.com/photos/very-small-2345/",
             "imageWidth":120,"imageHeight":120}
        ]}
        def fake(url):
            p=urllib.parse.urlsplit(url)
            params=urllib.parse.parse_qs(p.query)
            self.assertEqual(params["key"], ["key-value-not-logged"])
            self.assertEqual(params["q"], ["victorian garden"])
            self.assertEqual(params["orientation"], ["vertical"])
            return fixture
        with patch.object(bridge, "fetch_json", side_effect=fake):
            result=bridge.produce("pixabay", "victorian garden", "image", 3,
                                  {"PIXABAY":"key-value-not-logged"})
        self.assertEqual(len(result["items"]),1)
        self.assertTrue(result["items"][0]["review_required"])
        self.assertNotIn("key-value-not-logged", str(result))

    def test_04_video_candidates_only(self):
        data={"hits":[{"id":35,"pageURL":"https://pixabay.com/videos/forest-35/",
                       "tags":"forest","videos":{"medium":{"url":"https://cdn.pixabay.com/video.mp4",
                                                              "width":720,"height":1280}}}]}
        with patch.object(bridge,"fetch_json", return_value=data):
            result=bridge.produce("pixabay","forest sunset","video",1,{"PIXABAY":"abc"})
        self.assertEqual(result["items"][0]["dimensions"],[720,1280])
        self.assertFalse(result["automatic_download"])

    def test_05_pixabay_alias(self):
        with patch.object(bridge,"fetch_json",return_value={"hits":[]}):
            x=bridge.produce("pixabay","green tree","image",2,{"PIXABAY_API_KEY":"alias"})
        self.assertEqual(x["items"],[])

    def test_06_invalid_queries_fail_before_network(self):
        for q in ["x","a"*101,"http://localhost/a",""]:
            with self.assertRaises(bridge.SourceError):
                bridge.pixabay_search(q,"image",3,"abc")

    def test_07_no_mass_batch(self):
        with self.assertRaises(bridge.SourceError):
            bridge.pixabay_search("red roses","image",100,"abc")

    def test_08_missing_secret_fails(self):
        with self.assertRaises(bridge.SourceError):
            bridge.produce("pixabay","red roses","image",2,{})

    def test_09_openverse_reuses_v7(self):
        with patch.object(bridge,"openverse_search",return_value=[{"id":"abc"}]) as p:
            x=bridge.produce("openverse","Victorian painting","image",2,{})
        self.assertEqual(len(x["items"]),1)
        p.assert_called_once()

    def test_10_unexpected_host_rejected(self):
        with self.assertRaises(bridge.SourceError):
            bridge.fetch_json("https://example.com/api?key=SECRET")

if __name__ == "__main__":
    unittest.main()
