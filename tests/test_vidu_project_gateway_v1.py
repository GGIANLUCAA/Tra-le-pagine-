"""Offline tests of the Vidu project gateway: NO provider requests and NO paid POST."""
import json
import pathlib
import tempfile
import unittest
from unittest import mock
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
import vidu_project_gateway_v1 as g


def payload():
    return {
        "schema": "vidu_project_gateway_v1",
        "request_id": "vidu-test-safe-20261030",
        "mode": "plan",
        "format": "storia_rivive",
        "source": {
            "release_tag": "mock-historical-source-1906",
            "asset_name": "verified_source.jpg",
            "sha256": "a" * 64,
            "subject_reviewed_by_user": True,
            "provenance_url": "https://www.loc.gov/item/00694408/"
        },
        "clip": {
            "model": "viduq2-pro-fast", "resolution": "720p", "seconds": 5,
            "prompt": "Real people move at human speed; architecture and their historical clothes stay fixed in appearance; the scene is one continuous documentary shot.",
            "off_peak": False, "audio": False, "color_reveal_first_second": True
        },
        "distribution": {"github_public_preview": False}
    }


class GatewayChecks(unittest.TestCase):
    def test_real_5_second_price(self):
        v = payload()
        g.validate_common(v)
        self.assertEqual(g.quote(v), 16)
        self.assertRegex(g.fingerprint(v), r"^[A-F0-9]{12}$")

    def test_video_8_second_price(self):
        v = payload()
        v["clip"]["seconds"] = 8
        self.assertEqual(g.quote(v), 22)

    def test_wrong_photo_rejected_pre_spend(self):
        v = payload()
        v["source"]["subject_reviewed_by_user"] = False
        with self.assertRaises(g.GateError):
            g.validate_common(v)

    def test_source_changed_changes_approval_code(self):
        v = payload()
        code = g.fingerprint(v)
        v["source"]["sha256"] = "b" * 64
        self.assertNotEqual(g.fingerprint(v), code)

    def test_prompt_changed_changes_approval_code(self):
        v = payload()
        code = g.fingerprint(v)
        v["clip"]["prompt"] += " No camera motion."
        self.assertNotEqual(g.fingerprint(v), code)

    def test_requires_per_scene_payment_approval_and_never_fetches_or_posts(self):
        v = payload()
        v["mode"] = "generate"
        v["spend"] = {
            "approved_max_credits": 16,
            "approved_plan_code": g.fingerprint(v),
            "authorization_phrase": "WRONG",
            "user_approved_this_exact_scene": True,
        }
        with mock.patch.object(g, "source_image", side_effect=AssertionError("MUST_NOT_FETCH")):
            with mock.patch.object(g, "provider", side_effect=AssertionError("MUST_NOT_POST")):
                with self.assertRaises(g.GateError):
                    g.generate(v, pathlib.Path("output/test-no-billing"))

    def test_request_file_binds_filename_to_request_id(self):
        with tempfile.TemporaryDirectory() as root:
            previous = pathlib.Path.cwd()
            try:
                import os
                os.chdir(root)
                p = pathlib.Path("requests/vidu/vidu-test-safe-20261030.json")
                p.parent.mkdir(parents=True)
                p.write_text(json.dumps(payload()))
                self.assertEqual(g.request_file(str(p))["request_id"], p.stem)
                v = payload()
                v["request_id"] = "vidu-other-id-20261030"
                p.write_text(json.dumps(v))
                with self.assertRaises(g.GateError):
                    g.request_file(str(p))
            finally:
                os.chdir(previous)

    def test_balance_needs_no_expensive_fields(self):
        v = {"schema": "vidu_project_gateway_v1",
             "request_id": "vidu-test-balance-20261030", "mode": "balance"}
        g.validate_common(v)
        self.assertEqual(v["mode"], "balance")

    def test_collection_requires_prior_request(self):
        v = {"schema": "vidu_project_gateway_v1",
             "request_id": "vidu-test-collect-20261030", "mode": "collect"}
        with self.assertRaises(g.GateError):
            g.validate_common(v)
        v["collect_request_id"] = "vidu-old-paid-20261029"
        g.validate_common(v)

    def test_no_shell_injection_from_release_file_name(self):
        v = payload()
        v["source"]["asset_name"] = "../../secrets.jpg"
        with self.assertRaises(g.GateError):
            g.validate_common(v)

    def test_no_generic_provider_post_route(self):
        with mock.patch.object(g, "urllib", wraps=g.urllib):
            with self.assertRaises(g.GateError):
                g.provider("/v1/unknown-command", method="POST")


if __name__ == "__main__":
    unittest.main()
