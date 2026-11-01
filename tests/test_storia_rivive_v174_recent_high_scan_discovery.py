import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

FILE=Path(__file__).resolve().parents[1]/"src"/"storia_rivive_v174_recent_high_scan_discovery.py"
spec=importlib.util.spec_from_file_location("v174",FILE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class V174RecentScanTests(unittest.TestCase):
    def test_parse_actual_filming_year_not_upload_date(self):
        self.assertEqual(m.parse_historical_year({"year":"1917","publicdate":"2026-10-02"}),1917)
        self.assertEqual(m.parse_historical_year({"date":"1926-05-07","publicdate":"2026-10-02"}),1926)
        self.assertIsNone(m.parse_historical_year({"publicdate":"2025-11-01"}))
        self.assertIsNone(m.parse_historical_year({"year":"1945","publicdate":"2025-11-01"}))

    def test_exact_licensed_item_not_collection(self):
        self.assertTrue(m.public_domain_exact({"licenseurl":"http://creativecommons.org/licenses/publicdomain/"}))
        self.assertFalse(m.public_domain_exact({"licenseurl":"http://creativecommons.org/licenses/by/4.0/"}))
        self.assertFalse(m.public_domain_exact({}))

    def test_reject_unsafe_identifiers(self):
        for item in ("../film","film/a","film?b","",None,"film with spaces"):
            with self.subTest(item=item),self.assertRaises(ValueError):
                m.safe_id(item)
        self.assertEqual(m.safe_id("film_1917-4k"),"film_1917-4k")

    def test_filter_video_media_no_traversal(self):
        records=[
            {"name":"original_scan.mov","size":"130000000","source":"original","format":"ProRes"},
            {"name":"../../../payload.mp4","size":"130000000"},
            {"name":"x.jpg","size":"100000000"},
            {"name":"source.mp4","size":"100"},
        ]
        items=m.video_files(records)
        self.assertEqual(len(items),1)
        self.assertEqual(items[0]["filename"],"original_scan.mov")

    def test_search_dedupe(self):
        def fake(url):
            return {"response":{"docs":[{"identifier":"one"},{"identifier":"two"}]}} if "year%3A" in url else {"response":{"docs":[{"identifier":"one"}]}}
        with patch.object(m,"metadata_get",side_effect=fake):
            self.assertEqual(len(m.search_ids()),2)

    def test_discovery_flags_unverified_hd(self):
        def metadata_get(url):
            if "advancedsearch.php" in url:
                return {"response":{"docs":[{"identifier":"good","publicdate":"2025-04-04"},{"identifier":"bad"}]}}
            if url.endswith("good"):
                return {"metadata":{"identifier":"good","title":"Good film","year":"1922","licenseurl":"http://creativecommons.org/licenses/publicdomain/"},
                        "files":[{"name":"good_scan.mp4","size":"190000000","source":"original","format":"MPEG4"}]}
            return {"metadata":{"identifier":"bad","year":"1922","licenseurl":"https://creativecommons.org/licenses/by/4.0/"}, "files":[]}
        with patch.object(m,"metadata_get",side_effect=metadata_get):
            r=m.discover()
        self.assertEqual(r["status"],"CANDIDATES_REQUIRE_NATIVE_VIDEO_FFPROBE_AND_ARTISTIC_REVIEW")
        self.assertEqual([x["identifier"] for x in r["candidates"]],["good"])
        self.assertFalse(r["candidates"][0]["native_high_res_confirmed"])
        self.assertFalse(r["native_resolution_verified_by_ffprobe"])
        self.assertTrue(r["requires_independent_italian_rights_review"])
        self.assertEqual(r["videos_downloaded"],0)
        self.assertEqual(r["vidu_requests"],0)


if __name__=="__main__":
    unittest.main()
