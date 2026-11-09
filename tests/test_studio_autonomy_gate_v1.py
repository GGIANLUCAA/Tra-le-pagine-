import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from studio_autonomy_gate_v1 import evaluate, diagnostic


SHA_A = "a" * 64
SHA_B = "b" * 64


def checkpoint(**updates):
    base = {
        "schema": "studio-autonomy-checkpoint-v1",
        "job_id": "artvision.test:1",
        "format": "artvision_4x1",
        "variant": "critico_museum",
        "stage": "rendered",
        "source_rights_verified": True,
        "source_hash_verified": True,
        "music_rights_verified": True,
        "narration_verified": True,
        "delivery": {
            "mp4_sha256": SHA_A,
            "mp4_bytes": 999000,
            "zip_sha256": SHA_B,
            "zip_bytes": 1000020,
            "cover_verified": True,
            "social_drafts_verified": True,
        },
        "technical_qa": {
            "schema": "quality-director-v17",
            "status": "needs_artistic_review",
            "blocking": [],
        },
        "owner_review": None,
    }
    base.update(updates)
    return base


class AutonomyGateTests(unittest.TestCase):
    def test_technical_success_does_not_grant_artistic_approval(self):
        x = evaluate(checkpoint())
        self.assertEqual(x["status"], "owner_review_required")
        self.assertFalse(x["can_publish"])

    def test_owner_review_bound_to_exact_mp4_but_not_publication(self):
        j = checkpoint(owner_review={"decision": "approved",
                                     "reviewer": "owner",
                                     "mp4_sha256": SHA_A})
        x = evaluate(j)
        self.assertEqual(x["status"], "approved_record_needs_release_check")
        self.assertFalse(x["can_publish"])

    def test_fake_or_stale_approval_rejected(self):
        j = checkpoint(owner_review={"decision": "approved",
                                     "reviewer": "owner",
                                     "mp4_sha256": SHA_B})
        self.assertEqual(evaluate(j)["status"], "owner_review_required")

    def test_missing_narration_blocks_critico_and_books(self):
        for kind in ("libri_narrati", "artvision_4x1"):
            j = checkpoint(format=kind, narration_verified=False)
            self.assertEqual(evaluate(j)["suggested_action"], "repair_narration")

    def test_cinema_without_voice_does_not_invent_audio(self):
        j = checkpoint(variant="cinema_museum", narration_verified=False)
        self.assertEqual(evaluate(j)["status"], "owner_review_required")

    def test_missing_rights_or_hash_blocks(self):
        for key in ("source_rights_verified", "source_hash_verified"):
            j = checkpoint(**{key: False})
            self.assertEqual(evaluate(j)["status"], "blocked")

    def test_partial_package_and_qa_fail(self):
        j = checkpoint(delivery={})
        self.assertEqual(evaluate(j)["suggested_action"], "verify_real_mp4_and_zip")
        j = checkpoint(technical_qa={"schema": "quality-director-v17",
                                     "status": "technical_blocked",
                                     "blocking": [{"code": "SILENT"}]})
        self.assertEqual(evaluate(j)["suggested_action"], "repair_technical_qa")

    def test_no_implicit_spending_or_publication(self):
        self.assertEqual(
            evaluate(checkpoint(paid_request_pending=True))["status"],
            "owner_action_required")
        self.assertEqual(
            evaluate(checkpoint(publish_requested=True))["status"],
            "owner_action_required")

    def test_safe_retry_only_readonly_without_charge_uncertainty(self):
        j = checkpoint(stage="failed", error={"code": "github_503"},
                       attempts=1, charge_uncertain=False,
                       failure_is_readonly=True)
        self.assertEqual(evaluate(j)["status"], "safe_retry_candidate")
        self.assertTrue(evaluate(j)["can_auto_continue"])
        j["charge_uncertain"] = True
        self.assertEqual(evaluate(j)["status"], "repair_review_required")
        j["charge_uncertain"] = False
        j["attempts"] = 2
        self.assertEqual(evaluate(j)["status"], "repair_review_required")
        j["attempts"] = 1
        j["error"]["code"] = "render_failed"
        self.assertEqual(evaluate(j)["status"], "repair_review_required")

    def test_duplicate_suppresses_next_production(self):
        x = evaluate(checkpoint(completed_same_input=True))
        self.assertEqual(x["suggested_action"], "skip_same_input")
        self.assertFalse(x["can_publish"])

    def test_preflight_is_not_render(self):
        x = evaluate(checkpoint(stage="preflight"))
        self.assertEqual(x["status"], "prepared_for_owner_pipeline")
        self.assertFalse(x["video_created_by_gate"])

    def test_diagnostic_only_verified_run_url_no_raw_logs(self):
        j = checkpoint(stage="failed", error={"code": "render_failed",
                                              "secret_log": "sk-example-never-share"},
                       run_url="https://evil.example/steal")
        x = evaluate(j)
        t = diagnostic(x, j)
        self.assertNotIn("sk-example-never-share", t)
        self.assertNotIn("evil.example", t)
        j["run_url"] = "https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/123"
        self.assertIn("/actions/runs/123", diagnostic(evaluate(j), j))

    def test_unknown_schema_and_invalid_retries_rejected(self):
        with self.assertRaises(ValueError):
            evaluate(checkpoint(schema="unknown"))
        with self.assertRaises(ValueError):
            evaluate(checkpoint(stage="failed", attempts=True))


if __name__ == "__main__":
    unittest.main()
