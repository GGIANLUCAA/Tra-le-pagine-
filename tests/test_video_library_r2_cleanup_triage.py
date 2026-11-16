import copy
import json
from pathlib import Path
import unittest

from tools.video_library_r2_cleanup_triage import triage

AUDIT = Path(__file__).resolve().parents[1] / "reports/video_library_r2_storage_audit_20261116.json"


class R2StorageSafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = json.loads(AUDIT.read_text(encoding="utf-8"))

    def test_full_inventory_and_not_zeroed(self):
        self.assertEqual(self.audit["objects"]["count"], 6244)
        self.assertEqual(self.audit["mp4"]["count"], 729)
        self.assertEqual(len(self.audit["numbered_variant_rows"]), 279)
        self.assertEqual(self.audit["totals"]["numbered_bytes"], 3515282007)

    def test_duplicate_group_sha_is_distinct_from_etag(self):
        result = triage(self.audit)
        self.assertEqual(len(result["fingerprint_groups"]), 12)
        self.assertEqual(result["possible_fingerprint_bytes"], 312090019)
        confirmed = [x for x in result["fingerprint_groups"] if x.get("sha256")]
        self.assertEqual(len(confirmed), 1)
        self.assertEqual(confirmed[0]["possible_bytes"], 41361075)
        self.assertIn("ArtVision_WOW7_Piranesi_Le_Prigioni_Impossibili.mp4",
                      confirmed[0]["ready_keys"])
        self.assertEqual(len(result["eligible_to_delete_now"]), 0)

    def test_other_numbered_versions_not_promoted_to_duplicates(self):
        variants = self.audit["numbered_variant_rows"]
        self.assertEqual(sum(int(x[3]) for x in variants), 1)
        self.assertGreater(sum(x[1] for x in variants), 3_000_000_000)
        self.assertTrue(all(len(x) == 4 for x in variants))

    def test_fail_closed_when_report_claims_prior_deletion(self):
        fake = copy.deepcopy(self.audit)
        fake["totals"]["deleted_bytes"] = 12
        with self.assertRaises(AssertionError):
            triage(fake)

    def test_no_delete_codepath(self):
        tool = (AUDIT.parents[1] / "tools/video_library_r2_cleanup_triage.py").read_text()
        self.assertNotIn("cloudflare.request", tool)
        self.assertNotIn(".delete(", tool)
        self.assertIn('"DO_NOT_DELETE"', tool)


if __name__ == "__main__":
    unittest.main()
