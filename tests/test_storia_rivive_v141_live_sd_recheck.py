"""V141 Commons SD recheck: offline, injected metadata; no paid calls."""
import json
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from storia_rivive_v141_live_sd_recheck import recheck_low_raster_snapshots

REGISTRY = json.loads((ROOT / "config/storia_rivive_v140_low_raster_sources.json").read_text(encoding="utf-8"))


class TestV141LiveSDRecheck(unittest.TestCase):
    def test_all_seven_same_raster_remain_research_only(self):
        dimensions = {r["source_page"]: r["commons_original_raster_px"] for r in REGISTRY["excluded"]}
        result = recheck_low_raster_snapshots(REGISTRY, lambda p: {
            "original_width_px": dimensions[p][0], "original_height_px": dimensions[p][1]})
        self.assertEqual(result["status"], "ALL_LOW_RASTER_SNAPSHOTS_CURRENT")
        self.assertEqual(result["checked_count"], 7)
        self.assertFalse(result["source_acquisition_permitted"])
        self.assertFalse(result["vidu_post_permitted"])
        self.assertFalse(result["publication_permitted"])

    def test_same_page_upgraded_to_hd_requires_review_not_automatic_approval(self):
        dimensions = {r["source_page"]: r["commons_original_raster_px"] for r in REGISTRY["excluded"]}
        changed = REGISTRY["excluded"][0]["source_page"]
        def lookup(page):
            w, h = ([1920, 1080] if page == changed else dimensions[page])
            return {"original_width_px": w, "original_height_px": h}
        result = recheck_low_raster_snapshots(REGISTRY, lookup)
        self.assertEqual(result["status"], "SOURCE_SNAPSHOT_REVIEW_REQUIRED")
        self.assertEqual(result["sources"][0]["status"], "RASTER_CHANGED_REQUIRES_NEW_SOURCE_REVIEW")
        self.assertFalse(result["source_acquisition_permitted"])
        self.assertFalse(result["i2i_permitted"])

    def test_network_failure_fails_closed_without_leaking_exception(self):
        def unavailable(page):
            raise RuntimeError("secret token should not appear in output")
        result = recheck_low_raster_snapshots(REGISTRY, unavailable)
        self.assertEqual(result["status"], "SOURCE_SNAPSHOT_CHECK_UNAVAILABLE")
        self.assertNotIn("secret token", json.dumps(result))
        self.assertTrue(all(r["status"] == "RECHECK_PENDING_NETWORK_ERROR" for r in result["sources"]))
        self.assertFalse(result["vidu_post_permitted"])

    def test_missing_metadata_fails_closed(self):
        result = recheck_low_raster_snapshots(REGISTRY, lambda _: {"original_width_px": "1920"})
        self.assertEqual(result["status"], "SOURCE_SNAPSHOT_CHECK_UNAVAILABLE")
        self.assertEqual(result["sources"][0]["status"], "LIVE_RASTER_METADATA_UNAVAILABLE")

    def test_reject_duplicate_ids_and_untrusted_pages_before_network(self):
        for field, value in [("candidate_id", REGISTRY["excluded"][1]["candidate_id"]),
                             ("source_page", "http://untrusted.invalid/video")]:
            altered = json.loads(json.dumps(REGISTRY))
            altered["excluded"][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                recheck_low_raster_snapshots(altered, lambda _: self.fail("network must not be used"))

    def test_invalid_registry_rejected(self):
        with self.assertRaises(ValueError):
            recheck_low_raster_snapshots({"version": "unknown", "excluded": []})


if __name__ == "__main__":
    unittest.main()
