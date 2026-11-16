import unittest
from scripts.artvision_preflight_duplicate_v1 import preflight

WORK={"id":"artwork-1","artist":"Example Painter","title":"The River",
      "excluded":False,"site_candidates":["maybe-one.mp4"],
      "variants":{"cinema_standard":{"state":"render_documentato",
        "evidence":[{"status_claim":"rendered","sha256":"1"*64}]},
        "critico_standard":{"state":"bloccato","evidence":[]}}}
class PreflightDuplicateTests(unittest.TestCase):
    def test_documented_render_never_silently_repeated(self):
        d=preflight({"works":[WORK]},"Example Painter","The River","cinema_standard")
        self.assertEqual(d["verdict"],"RENDER_EXISTS_VERIFY_REUSE_OR_REVISION")
        self.assertFalse(d["auto_skip_render"])
        self.assertEqual(d["site_candidate_count"],1)
    def test_actual_sha_claim_matched(self):
        d=preflight({"works":[WORK]},"Example Painter","The River","cinema_standard","1"*64)
        self.assertEqual(d["verdict"],"SHA_ALREADY_RECORDED")
        self.assertTrue(d["same_sha_claim"])
    def test_unknown_and_blocked(self):
        self.assertEqual(preflight({"works":[WORK]},"Other","Other","cinema_standard")["verdict"],
                         "UNKNOWN_NEEDS_RESEARCH")
        self.assertEqual(preflight({"works":[WORK]},"Example Painter","The River","critico_standard")["verdict"],
                         "BLOCKED_REPAIR_INDEPENDENTLY")
    def test_owner_exclusion_never_undone(self):
        x={**WORK,"excluded":True}
        d=preflight({"works":[x]},"Example Painter","The River","cinema_standard")
        self.assertEqual(d["verdict"],"EXCLUDED_BY_OWNER")
if __name__=="__main__":unittest.main()
