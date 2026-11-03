"""V213 license claim checks never authorize use in Italy or Vidu."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from storia_rivive_v213_license_metadata_gate import inspect, STATUS_OK, STATUS_BLOCKED

SHA = "a" * 64
PAGE = "https://commons.wikimedia.org/wiki/File:Archival_movie.webm"


def fixture(claim="CC0_as_declared", actual="CC0 1.0"):
    order = {"contract": "LA_STORIA_RIVIVE_V101_SAFE_AUTOPILOT",
             "source_page": PAGE, "source_license_claim": claim,
             "paid_api_call_permitted": False, "publish_permitted": False}
    scout = {"source_page": PAGE, "original_sha256": SHA,
             "license_metadata": actual, "historical_rights_italy_approved": False,
             "social_publish_permitted": False}
    v196 = {"ready": True, "status": "REAL_BW_FILM_FRAMES_VERIFIED_FOR_RESEARCH_ONLY",
            "original_film_sha256": SHA}
    return order, scout, v196


class LicenseMetadataTests(unittest.TestCase):
    def test_cc0_claim_matches_but_never_approves_rights(self):
        report = inspect(*fixture())
        self.assertEqual(report["status"], STATUS_OK)
        self.assertTrue(report["research_ready"])
        for field in ("italian_rights_approved", "underlying_film_rights_verified",
                      "human_legal_review_completed", "provider_calls_permitted",
                      "publish_permitted"):
            self.assertFalse(report[field], field)

    def test_public_domain_claim_matches_but_never_approves_italy(self):
        report = inspect(*fixture("PUBLIC_DOMAIN", "Public domain"))
        self.assertEqual(report["status"], STATUS_OK)
        self.assertFalse(report["italian_rights_approved"])

    def test_mismatched_license_blocks(self):
        report = inspect(*fixture("CC0_as_declared", "CC BY-SA 4.0"))
        self.assertEqual(report["status"], STATUS_BLOCKED)
        self.assertEqual(report["reason"], "CANDIDATE_LICENSE_CLAIM_DIFFERS_FROM_COMMONS")
        self.assertFalse(report["research_ready"])

    def test_unrecognized_pd_label_blocks(self):
        report = inspect(*fixture("PUBLIC_DOMAIN", "PD-old-70"))
        self.assertEqual(report["status"], STATUS_BLOCKED)

    def test_missing_metadata_blocks(self):
        report = inspect(*fixture("CC0", ""))
        self.assertEqual(report["reason"], "MISSING_OR_INVALID_COMMONS_LICENSE_METADATA")

    def test_wrong_source_page_blocks(self):
        order, scout, gate = fixture()
        scout["source_page"] = "https://commons.wikimedia.org/wiki/File:Other.webm"
        self.assertEqual(inspect(order, scout, gate)["reason"], "SCOUT_SOURCE_PAGE_MISMATCH")

    def test_sha_mismatch_blocks(self):
        order, scout, gate = fixture()
        gate["original_film_sha256"] = "b" * 64
        self.assertEqual(inspect(order, scout, gate)["reason"], "SOURCE_FILM_SHA_BINDING_MISMATCH")

    def test_false_v196_gate_blocks(self):
        order, scout, gate = fixture()
        gate["ready"] = False
        self.assertEqual(inspect(order, scout, gate)["reason"], "V196_SOURCE_BYTES_NOT_VERIFIED")

    def test_untrusted_scout_rights_claim_blocks(self):
        order, scout, gate = fixture()
        scout["historical_rights_italy_approved"] = True
        self.assertEqual(inspect(order, scout, gate)["reason"],
                         "SCOUT_CLAIMS_UNSUPPORTED_RIGHTS_OR_PUBLICATION")

    def test_unsafe_work_order_blocks(self):
        order, scout, gate = fixture()
        order["paid_api_call_permitted"] = True
        self.assertEqual(inspect(order, scout, gate)["reason"], "INVALID_OR_UNSAFE_WORK_ORDER")

    def test_non_commons_source_not_silently_accepted(self):
        order, scout, gate = fixture()
        order["source_page"] = "https://www.loc.gov/item/123"
        scout["source_page"] = order["source_page"]
        self.assertEqual(inspect(order, scout, gate)["reason"], "SOURCE_NOT_COMMONS_FILE_PAGE")

    def test_unexpected_license_html_blocks_without_logging_html(self):
        report = inspect(*fixture("CC0", "<b>CC0</b>"))
        self.assertEqual(report["status"], STATUS_BLOCKED)
        self.assertNotIn("<b>", str(report))


if __name__ == "__main__":
    unittest.main()
