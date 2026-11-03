"""Offline contract tests for five additional no-key search sources."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlsplit,parse_qs

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import public_archive_sources_v2 as api
import source_selector_v34 as sel

def brief(fmt,need):
    return {"title":"Historical archive search","format":fmt,"scenes":[{
        "id":"research","need":need,
        "description":"Genuine archival source of the historical subject",
        "narration_anchor":"Documented source"}]}

class PublicArchiveV2Tests(unittest.TestCase):
    def test_validation_before_network(self):
        for provider,query,limit in [("not-real","art painting",1),("vam","x",2),
                                     ("smk","painting\nsecret",1),("nasa","space",6)]:
            with self.assertRaises(api.old.ResearchError):
                api.search(provider,query,limit,lambda url:self.fail("network call"))
    def test_vam_metadata_and_thumbnail(self):
        def fake(url):
            p=parse_qs(urlsplit(url).query)
            self.assertEqual(p["images_exist"],["1"])
            self.assertEqual(p["page_size"],["2"])
            return {"records":[
                {"systemNumber":"O12345","_primaryTitle":"Portrait",
                 "_primaryMaker":{"name":"Artist"},"_primaryDate":"1840",
                 "_images":{"_primary_thumbnail":"https://framemark.vam.ac.uk/x.jpg"}},
                {"systemNumber":"unsafe/file","_primaryTitle":"Not valid"}
            ]}
        x=api.search("vam","Victorian portrait",2,fake)
        self.assertEqual(len(x["items"]),1)
        self.assertEqual(x["items"][0]["author"],"Artist")
        self.assertTrue(x["items"][0]["source_url"].endswith("/O12345/"))
        self.assertEqual(x["items"][0]["rights_review"],"pending")
    def test_smk_filtered_public_domain(self):
        def fake(url):
            params=parse_qs(urlsplit(url).query)
            self.assertIn("public_domain:true",params["filters"][0])
            return {"items":[{"object_number":"KMS1","title":"Nature",
                              "image_thumbnail":"https://iip-thumb.smk.dk/x.jpg"}]}
        x=api.search("smk","Eckersberg painter",1,fake)
        self.assertEqual(x["items"][0]["provider"],"smk")
        self.assertEqual(x["items"][0]["authenticity_review"],"pending")
    def test_wellcome_work_records(self):
        def fake(url):
            self.assertIn("include=images%2Ccontributors%2Cproduction",url)
            return {"results":[{"id":"ab12345","title":"Historical science",
                                "contributors":[{"agent":{"label":"Researcher"}}]}]}
        x=api.search("wellcome","historical science",1,fake)
        self.assertEqual(len(x["items"]),1)
        self.assertIn("wellcomecollection.org/works/ab12345",x["items"][0]["source_url"])
        self.assertEqual(x["items"][0]["license_claim"],"Work metadata; image license varies by item")
    def test_nasa_video_and_image_metadata(self):
        x=api.search("nasa","Apollo 11",2,lambda url:{"collection":{"items":[
            {"data":[{"nasa_id":"as11_1","media_type":"video","title":"Moon",
                      "date_created":"1969-07-20"}],
             "links":[{"href":"https://images-assets.nasa.gov/thumbnail.jpg"}]},
            {"data":[{"nasa_id":"as11_2","media_type":"audio","title":"Not visual"}]}
        ]}})
        self.assertEqual(len(x["items"]),1)
        self.assertEqual(x["items"][0]["media_kind"],"video")
        self.assertEqual(x["items"][0]["visual_review"],"pending")
    def test_gallica_xml_and_unsafe_identifier(self):
        xml="""<?xml version="1.0"?>
        <srw:searchRetrieveResponse xmlns:srw="http://www.loc.gov/zing/srw/"
          xmlns:dc="http://purl.org/dc/elements/1.1/">
          <srw:records><srw:record><srw:recordData>
            <dc:identifier>https://gallica.bnf.fr/ark:/12148/bpt6k12345</dc:identifier>
            <dc:title>Paris 1900</dc:title><dc:date>1900</dc:date>
          </srw:recordData></srw:record></srw:records></srw:searchRetrieveResponse>"""
        x=api.search("gallica","Paris 1900",2,lambda url:xml.encode())
        self.assertEqual(len(x["items"]),1)
        self.assertEqual(x["items"][0]["title"],"Paris 1900")
        self.assertEqual(x["items"][0]["rights_review"],"pending")
    def test_selector_artwork_and_archive_paths(self):
        for provider,fmt,need in [
            ("vam","artvision_critico","authentic_artwork"),
            ("smk","artvision_cinema","authentic_artwork"),
            ("wellcome","artvision_critico","authentic_artwork"),
            ("nasa","controluce","documentary_evidence"),
            ("gallica","controluce","documentary_evidence")
        ]:
            item={"id":provider+":1","provider":provider,
                  "source_reference":"https://example.test/not-downloaded",
                  "source_url":"https://example.test/not-downloaded"}
            with self.subTest(provider=provider),patch.object(api,"search",
                 return_value={"items":[item],"api_requests":1}) as call:
                report,detail=sel.discover_single(brief(fmt,need),[],"research",
                                                  provider,"historical landscape",1)
                call.assert_called_once()
                self.assertEqual(report["counts"]["need_sources"],1)
                self.assertEqual(detail["results"][0]["rights_review"],"pending")
                self.assertFalse(detail["automatic_selection"])
                self.assertEqual(detail["downloaded_files"],0)
    def test_reject_wrong_source_before_call(self):
        with patch.object(api,"search",side_effect=AssertionError("Network")):
            with self.assertRaises(sel.SelectionError):
                sel.discover_single(brief("artvision_critico","authentic_artwork"),
                                    [],"research","nasa","space images",1)
    def test_old_providers_delegated(self):
        with patch.object(api.old,"search",return_value={"items":[],"api_requests":1}) as call:
            x=api.search("artic","seurat",1)
            self.assertEqual(x["api_requests"],1)
            call.assert_called_once()

if __name__=="__main__":
    unittest.main()
