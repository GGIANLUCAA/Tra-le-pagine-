import unittest
from src.artvision_chain_live_preview_v1 import preview
from src.artvision_chain_live_snapshot_v1 import ACTIVE_STATUSES, REPO


def snapshot(**overrides):
    value = dict(repo=REPO, inventory_status="complete_read_only_non_atomic",
                 active_run_statuses_checked=list(ACTIVE_STATUSES),
                 active_heavy_render=False, dispatch_authorized=False)
    value.update(overrides)
    return value


def candidate(id="next", **overrides):
    value = dict(id=id, status="ready",
                 source_verified=True, rights_verified=True,
                 storyboard_ready=True, qa_plan_ready=True,
                 workflow_path=".github/workflows/approved.yml")
    value.update(overrides)
    return value


def queue(**overrides):
    value = dict(schema="artvision-chain-candidates-v1",
                 reviewed_workflow_paths=[".github/workflows/approved.yml"],
                 completed_ids=[], running_ids=[], quarantined_ids=[],
                 candidates=[candidate()])
    value.update(overrides)
    return value


class PreviewTests(unittest.TestCase):
    def test_complete_snapshot_still_not_authorize_dispatch(self):
        result = preview(snapshot(), queue())
        self.assertEqual(result["status"], "candidate_manual_review_only")
        self.assertFalse(result["dispatch_authorized"])
        self.assertFalse(result["render_started"])

    def test_busy_live_state_overrides_queue_false(self):
        result = preview(snapshot(active_heavy_render=True),
                         queue(active_heavy_render=False))
        self.assertEqual(result["status"], "preparing")
        self.assertFalse(result["render_started"])

    def test_wrong_repo_blocks(self):
        self.assertEqual(preview(snapshot(repo="attacker/other"), queue())["status"], "blocked")

    def test_incomplete_scan_blocks(self):
        result = preview(snapshot(inventory_status="unknown_fail_closed"), queue())
        self.assertEqual(result["status"], "blocked")

    def test_missing_states_blocks(self):
        self.assertEqual(preview(snapshot(active_run_statuses_checked=[]), queue())["status"], "blocked")

    def test_nonboolean_busy_blocks(self):
        self.assertEqual(preview(snapshot(active_heavy_render=0), queue())["status"], "blocked")

    def test_claimed_dispatch_authorized_blocks(self):
        self.assertEqual(preview(snapshot(dispatch_authorized=True), queue())["status"], "blocked")

    def test_no_workflow_allowlist_blocks(self):
        self.assertEqual(preview(snapshot(), queue(reviewed_workflow_paths=[]))["status"], "blocked")

    def test_unreviewed_workflow_blocks(self):
        result = preview(snapshot(), queue(reviewed_workflow_paths=[".github/workflows/other.yml"]))
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["reason"], "candidate workflow not independently allowlisted")

    def test_path_traversal_allowlist_blocks(self):
        self.assertEqual(preview(snapshot(),
                                 queue(reviewed_workflow_paths=[".github/workflows/../escape.yml"]))["status"], "blocked")

    def test_unverified_rights_prepares(self):
        result = preview(snapshot(), queue(candidates=[candidate(rights_verified=False)]))
        self.assertEqual(result["status"], "preparing")
        self.assertIn("rights_verified", result["selector"]["missing_gates"])

    def test_completed_or_quarantined_candidates_do_not_repeat(self):
        for name in ("completed_ids", "quarantined_ids"):
            with self.subTest(name=name):
                result = preview(snapshot(), queue(**{name: ["next"]}))
                self.assertEqual(result["status"], "preparing")

    def test_invalid_queue_schema_blocks(self):
        self.assertEqual(preview(snapshot(), queue(schema="unknown"))["status"], "blocked")

    def test_unknown_run_status_fails_closed_prior_to_preview(self):
        self.assertEqual(preview(snapshot(active_heavy_render=None), queue())["status"], "blocked")


if __name__ == "__main__":
    unittest.main()
