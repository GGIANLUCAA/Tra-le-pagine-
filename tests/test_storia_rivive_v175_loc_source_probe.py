import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

FILE = Path(__file__).resolve().parents[1]/"src"/"storia_rivive_v175_loc_source_probe.py"
spec=importlib.util.spec_from_file_location("loc175",FILE)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


class V175LocTests(unittest.TestCase):
    def test_id_allowlist_safety(self):
        self.assertEqual(m.safe_item_id("2012600307"),"2012600307")
        for v in ("../2012600307","2012600307?other=1","https://loc.gov/item/123","abcd","1234",None):
            with self.subTest(v=v),self.assertRaises(ValueError):m.safe_item_id(v)

    def test_reject_non_loc_or_scheme(self):
        for v in ("https://evil.loc.gov/x.mp4","https://loc.gov.evil.com/x.mov",
                  "http://tile.loc.gov/a.mp4","https://tile.loc.gov@evil.com/a.mp4",
                  "https://example.com/a.mp4","file:///tmp/a.mov"):
            with self.subTest(v=v): self.assertFalse(m.is_media_url(v))
        self.assertTrue(m.is_media_url("https://tile.loc.gov/storage/video/film.mov"))
        self.assertFalse(m.is_media_url("https://www.loc.gov/item/2012600307/?fo=json"))

    def test_find_nested_downloads_without_false_native_claims(self):
        doc={"resources":[{"files":[{"url":"https://tile.loc.gov/storage/a.mov"},
                                      {"url":"https://cdn.loc.gov/files/b.mp4"},
                                      {"url":"https://evil.com/fake.mp4"}]}],
             "random":{"links":["https://tile.loc.gov/storage/a.mov",
                                "https://tile.loc.gov/storage/not-video.mp3"]}}
        items=m.collect_media_urls(doc)
        self.assertEqual(len(items),2)
        self.assertFalse(any(x["native_raster_verified"] for x in items))
        self.assertFalse(any(x["actual_source_quality_approved"] for x in items))

    def test_metadata_missing_not_imply_final_approval(self):
        with patch.object(m,"get_json",return_value={"item":{"title":"A corner in wheat","date":"1909"},
                                                      "resources":[],"media":[] }):
            r=m.inspect_one("2012600307",m.ITEMS["2012600307"])
        self.assertEqual(r["status"],"LOC_ITEM_HAS_NO_DOWNLOADABLE_MEDIA_LINK_IN_JSON")
        self.assertFalse(r["source_eligible_for_final"])
        self.assertFalse(r["italian_rights_verified"])
        self.assertEqual(r["real_vidu_count"],0)

    def test_record_has_correct_candidate_role_and_no_v98_reuse(self):
        with patch.object(m,"get_json",return_value={"item":{"title":"San Francisco Market Street","date":"1906"}}):
            r=m.inspect_one("00694408",m.ITEMS["00694408"])
        self.assertEqual(r["role"],"existing_V98_do_not_reproduce")
        self.assertFalse(r["source_eligible_for_final"])

    def test_fail_closed_when_remote_metadata_errors(self):
        with patch.object(m,"get_json",side_effect=RuntimeError("network")):
            r=m.inspect_one("2012600307",m.ITEMS["2012600307"])
        self.assertEqual(r["status"],"LOC_API_ACCESS_OR_METADATA_BLOCKED")
        self.assertFalse(r["film_original_or_high_res_verified"])
        self.assertEqual(r["error_type"],"RuntimeError")


if __name__=="__main__":
    unittest.main()
