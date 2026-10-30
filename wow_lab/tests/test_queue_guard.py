"""Queue isolation regression tests; no GitHub API access required."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import engine

class QueueGuardTests(unittest.TestCase):
    def test_other_wow_render_blocks(self):
        runs=[
            {"id":111,"name":"WOW LAB · independent render","status":"in_progress"},
            {"id":222,"name":"ArtVision 4x1","status":"in_progress"},
        ]
        self.assertEqual([x["id"] for x in engine.active_wow_conflicts(runs,"333")],["111"])

    def test_own_run_and_completed_wow_ignored(self):
        runs=[
            {"id":111,"name":"WOW LAB V1","status":"in_progress"},
            {"id":112,"name":"WOW LAB V1","status":"completed"},
        ]
        self.assertEqual(engine.active_wow_conflicts(runs,"111"),[])

    def test_queued_branch_render_blocks(self):
        runs=[{"id":115,"name":"specialized render",
               "head_branch":"experiment/wow-lab-specialized",
               "status":"queued"}]
        self.assertEqual(len(engine.active_wow_conflicts(runs,"116")),1)

    def test_public_queue_check_fails_closed_if_listing_truncated(self):
        with patch.dict(engine.os.environ,
                        {"GITHUB_REPOSITORY":"GGIANLUCAA/Tra-le-pagine-",
                         "GITHUB_RUN_ID":"222"}):
            with patch.object(engine,"get_json",
                              return_value={"total_count":101,"workflow_runs":[]}):
                with self.assertRaisesRegex(RuntimeError,"WOW_LAB_QUEUE_UNVERIFIED"):
                    engine.ensure_no_parallel_wow_render()

    def test_public_queue_check_blocks_other_run(self):
        payload={"total_count":1,"workflow_runs":[
            {"id":111,"name":"WOW LAB V4","status":"in_progress"}]}
        with patch.dict(engine.os.environ,
                        {"GITHUB_REPOSITORY":"GGIANLUCAA/Tra-le-pagine-",
                         "GITHUB_RUN_ID":"222"}):
            with patch.object(engine,"get_json",return_value=payload):
                with self.assertRaisesRegex(RuntimeError,"WOW_LAB_PARALLEL_RENDER"):
                    engine.ensure_no_parallel_wow_render()

    def test_offline_test_does_not_use_network(self):
        with patch.dict(engine.os.environ,{"GITHUB_REPOSITORY":""}):
            with patch.object(engine,"get_json",
                              side_effect=AssertionError("unexpected network")):
                engine.ensure_no_parallel_wow_render()

if __name__=="__main__":
    unittest.main()
