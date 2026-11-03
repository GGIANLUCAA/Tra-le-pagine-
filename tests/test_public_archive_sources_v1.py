"""Offline API adapter and V34 integration regression tests. Zero network."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlsplit,parse_qs

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import public_archive_sources_v1 as api
import source_selector_v34 as sel

def brief(fmt,need):
    return {"title":"Primary-source research","format":fmt,"scenes":[
        {"id":"research","need":need,"description":"Original historically authentic archival scene",
         "narration_anchor":"Documented narration"}]}

class ApiAdapterTests(unittest.TestCase):
    def test_reject_before_http(self):
        for provider,q,limit in [("foo","hello",2),("met","hi",2),
                                 ("met","hello\nbad",2),("met","hello",6)]:
            with self.assertRaises(api.ResearchError):
                api.search(provider,q,limit,lambda u:self.fail("network"))
    def test_met_uses_2026_endpoint_public_domain_filter(self):
        urls=[]
        def fake(u):
            urls.append(u)
            if "/v1.1/search" in u:return {"objectIDs":[1,2]}
            if u.endswith("/1"):return {"isPublicDomain":True,"title":"Art",
                                         "primaryImageSmall":"https://images.metmuseum.org/a.jpg"}
            return {"isPublicDomain":False,"primaryImageSmall":"https://images.metmuseum.org/b.jpg"}
        x=api.search("met","night watch",2,fake)
        self.assertEqual(x["api_requests"],3)
        self.assertIn("/v1.1/search",urls[0])
        self.assertEqual(len(x["items"]),1)
        self.assertEqual(x["items"][0]["rights_review"],"pending")
    def test_artic_restricts_pd_image(self):
        def fake(u):
            self.assertIn("query%5Bterm%5D%5Bis_public_domain%5D=true",u)
            return {"data":[{"id":5,"title":"Art","image_id":"abc123",
                              "is_public_domain":True},
                            {"id":6,"image_id":"abc123","is_public_domain":False}]}
        x=api.search("artic","a painting",2,fake)
        self.assertEqual(len(x["items"]),1)
        self.assertIn("iiif",x["items"][0]["preview"])
    def test_cleveland_search_cc0(self):
        def fake(u):
            self.assertIn("cc0=",u)
            return {"data":[{"id":14,"title":"Art","share_license_status":"CC0",
                              "url":"https://www.clevelandart.org/art/1900.1"}]}
        x=api.search("cleveland","river scenery",1,fake)
        self.assertEqual(x["items"][0]["license_claim"],"CC0")
        self.assertEqual(x["items"][0]["authenticity_review"],"pending")
    def test_loc_archive_and_commons_are_candidates_not_rights_clearance(self):
        loc=api.search("loc","Market Street 1906",1,lambda u:{"results":[{
            "id":"https://www.loc.gov/item/123","title":"Street Scene",
            "original_format":["Motion picture"],"date":"1906"}]})
        self.assertEqual(loc["items"][0]["media_kind"],"video")
        def archive_fake(u):
            self.assertIn("mediatype:(movies)",parse_qs(urlsplit(u).query)["q"][0])
            return {"response":{"docs":[{"identifier":"market_1906","title":"Old film"}]}}
        archive=api.search("archive","Market Street",1,archive_fake)
        self.assertEqual(archive["items"][0]["license_claim"],"UNKNOWN")
        commons=api.search("commons","Venice 1896",1,lambda u:{"query":{"pages":[{
            "pageid":42,"title":"File:Venice.webm",
            "imageinfo":[{"mime":"video/webm",
            "url":"https://upload.wikimedia.org/video.webm",
            "extmetadata":{"LicenseShortName":{"value":"CC0"}}}]}]}})
        self.assertEqual(commons["items"][0]["media_kind"],"video")
        for result in (loc,archive,commons):
            self.assertEqual(result["items"][0]["rights_review"],"pending")
            self.assertFalse(result["automatic_download"])
            self.assertFalse(result["automatic_publish"])
    def test_source_selector_routes_but_does_not_autoapprove(self):
        row={"id":"artic:5","provider":"artic",
             "source_url":"https://www.artic.edu/artworks/5",
             "source_reference":"https://www.artic.edu/artworks/5","media_kind":"image"}
        with patch.object(api,"search",return_value={"items":[row],"api_requests":1}) as called:
            report,detail=sel.discover_single(brief("artvision_critico","authentic_artwork"),
                                              [],"research","artic","Seurat",2)
        called.assert_called_once()
        self.assertEqual(detail["results"][0]["source_kind"],"authentic_artwork")
        self.assertEqual(detail["results"][0]["rights_review"],"pending")
        self.assertEqual(report["counts"]["need_sources"],1)
        self.assertFalse(detail["automatic_selection"])
    def test_source_selector_rejects_wrong_format_without_api(self):
        with patch.object(api,"search",side_effect=AssertionError("unexpected HTTP")):
            with self.assertRaises(sel.SelectionError):
                sel.discover_single(brief("artvision_critico","authentic_artwork"),
                                    [],"research","archive","painting",2)
    def test_security_untrusted_source_url(self):
        self.assertEqual(api.trusted("https://evil.example/pic",{"www.loc.gov"}),"")
        self.assertEqual(api.trusted("http://www.loc.gov/item/1",{"www.loc.gov"}),"")

if __name__=="__main__":
    unittest.main()
