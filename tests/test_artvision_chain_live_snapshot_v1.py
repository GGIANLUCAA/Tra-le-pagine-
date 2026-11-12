import unittest

from src.artvision_chain_live_snapshot_v1 import (
    ACTIVE_STATUSES, SnapshotError, build_snapshot, collect_active_runs,
    _is_possible_heavy,
)


def run(id=10, status="in_progress", path=".github/workflows/artvision-owner-sadko-cinema-v1.yml",
        name="ArtVision OWNER | Sadko | New Cinema private review", **extra):
    return dict(id=id, status=status, path=path, name=name,
                html_url="https://github.com/example/actions/runs/" + str(id),
                head_branch="main", **extra)


def fetcher(status_to_runs):
    def fetch(status, page):
        rows = status_to_runs.get(status, [])
        start = (page - 1) * 100
        return {"total_count": len(rows), "workflow_runs": rows[start:start + 100]}
    return fetch


class LiveSnapshotTests(unittest.TestCase):
    def test_idle_only_after_complete_authenticated_inventory(self):
        report = build_snapshot(fetcher({}))
        self.assertEqual(report["inventory_status"], "complete_read_only_non_atomic")
        self.assertFalse(report["active_heavy_render"])
        self.assertFalse(report["dispatch_authorized"])

    def test_owner_heavy_job_is_busy(self):
        report = build_snapshot(fetcher({"in_progress": [run()]}))
        self.assertTrue(report["active_heavy_render"])
        self.assertEqual(report["possible_heavy_runs"][0]["id"], 10)

    def test_owner_queued_job_is_busy(self):
        report = build_snapshot(fetcher({"queued": [run(status="queued")]}))
        self.assertTrue(report["active_heavy_render"])

    def test_all_owner_active_states_are_checked(self):
        for status in ACTIVE_STATUSES:
            with self.subTest(status=status):
                self.assertTrue(build_snapshot(fetcher({status: [run(status=status)]}))["active_heavy_render"])

    def test_research_workflow_is_excluded_from_heavy(self):
        r = run(path=".github/workflows/artvision-owner-source-research-v4.yml",
                name="ArtVision V4 - Ricerca fonti automatica per le dieci opere")
        self.assertFalse(_is_possible_heavy(r))
        self.assertFalse(build_snapshot(fetcher({"in_progress": [r]}))["active_heavy_render"])

    def test_nonowner_artvision_render_is_conservatively_busy(self):
        r = run(path=".github/workflows/artvision-wright-v85.yml", name="ArtVision Cinema render")
        self.assertTrue(_is_possible_heavy(r))

    def test_unrelated_site_job_not_heavy(self):
        r = run(path=".github/workflows/site-test.yml", name="Video Library Studio checks")
        self.assertFalse(_is_possible_heavy(r))

    def test_full_page_pagination_and_deduplication(self):
        rows = [run(id=i + 1) for i in range(101)]
        report = build_snapshot(fetcher({"in_progress": rows}))
        self.assertEqual(report["active_runs_observed"], 101)
        self.assertEqual(len(report["possible_heavy_runs"]), 101)

    def test_partial_inventory_fails_closed(self):
        def incomplete(status, page):
            if status == "queued":
                return {"total_count": 2, "workflow_runs": [run(status="queued")]} if page == 1 else {
                    "total_count": 2, "workflow_runs": []}
            return {"total_count": 0, "workflow_runs": []}
        with self.assertRaises(SnapshotError):
            build_snapshot(incomplete)

    def test_changed_page_count_fails_closed(self):
        def unstable(status, page):
            if status == "queued":
                return {"total_count": 2 if page == 1 else 3,
                        "workflow_runs": [run(id=page, status="queued")]}
            return {"total_count": 0, "workflow_runs": []}
        with self.assertRaises(SnapshotError):
            build_snapshot(unstable)

    def test_malformed_payload_fails_closed(self):
        def malformed(status, page):
            if status == "queued":
                return {"total_count": None, "workflow_runs": []}
            return {"total_count": 0, "workflow_runs": []}
        with self.assertRaises(SnapshotError):
            build_snapshot(malformed)

    def test_malformed_run_id_fails_closed(self):
        r = run(id="bad")
        with self.assertRaises(SnapshotError):
            build_snapshot(fetcher({"in_progress": [r]}))

    def test_unknown_run_status_fails_closed(self):
        with self.assertRaises(SnapshotError):
            build_snapshot(fetcher({"in_progress": [run(status="surprise")]}))

    def test_completed_transition_does_not_claim_active(self):
        # Non-atomic transitions are documented; a completed run isn't active.
        report = build_snapshot(fetcher({"queued": [run(status="completed")]}))
        self.assertFalse(report["active_heavy_render"])
        self.assertFalse(report["dispatch_authorized"])

    def test_untrusted_path_fails_closed(self):
        with self.assertRaises(SnapshotError):
            build_snapshot(fetcher({"in_progress": [run(path=None)]}))

    def test_repo_scoped_read_only_report(self):
        report = build_snapshot(fetcher({}))
        self.assertEqual(report["repo"], "GGIANLUCAA/Tra-le-pagine-")
        self.assertEqual(report["paid_api_calls"], 0)
        self.assertFalse(report["publication_authorized"])


if __name__ == "__main__":
    unittest.main()
