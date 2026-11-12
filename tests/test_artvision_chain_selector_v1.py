import unittest
from src.artvision_chain_selector_v1 import select_next


def item(id="new", **overrides):
    value = dict(id=id, status="ready", source_verified=True, rights_verified=True,
                 storyboard_ready=True, qa_plan_ready=True,
                 workflow_path=".github/workflows/new.yml")
    value.update(overrides)
    return value


class SelectorTests(unittest.TestCase):
    def test_unknown_active_state_fails_closed(self):
        self.assertEqual(select_next({"candidates": [item()]})["status"], "preparing")

    def test_active_render_blocks(self):
        self.assertEqual(select_next({"active_heavy_render": True, "candidates": [item()]})["status"], "preparing")

    def test_ready_candidate(self):
        self.assertEqual(select_next({"active_heavy_render": False, "candidates": [item()]})["id"], "new")

    def test_skip_duplicates(self):
        self.assertEqual(select_next({"active_heavy_render": False, "completed_ids": ["old"],
                                       "candidates": [item("old"), item("new")]})["id"], "new")

    def test_rights_gate(self):
        self.assertEqual(select_next({"active_heavy_render": False, "candidates": [item(rights_verified=False)]})["status"], "preparing")

    def test_running_gate(self):
        self.assertEqual(select_next({"active_heavy_render": False, "running_ids": ["new"],
                                       "candidates": [item()]})["status"], "preparing")

    def test_busy_prepares_independent_work(self):
        result = select_next({"active_heavy_render": True, "running_ids": ["busy"],
                              "candidates": [item("busy"), item("next", source_verified=False)]})
        self.assertEqual(result["id"], "next")
        self.assertIn("source_verified", result["missing_gates"])

    def test_unsafe_workflow_path(self):
        result = select_next({"active_heavy_render": False,
                              "candidates": [item(workflow_path=".github/workflows/../escape.yml")]})
        self.assertEqual(result["status"], "preparing")

    def test_invalid_workflow(self):
        self.assertEqual(select_next({"active_heavy_render": False,
                                      "candidates": [item(workflow_path="other.yml")]})["status"], "preparing")

    def test_skip_quarantined_and_select_independent(self):
        result = select_next({"active_heavy_render": False, "quarantined_ids": ["bad"],
                              "candidates": [item("bad"), item("good")]})
        self.assertEqual(result["id"], "good")

    def test_skip_blocked_and_select_independent(self):
        result = select_next({"active_heavy_render": False,
                              "candidates": [item("404", status="blocked"), item("good")]})
        self.assertEqual(result["id"], "good")

    def test_blocked_does_not_displace_other_preparation(self):
        result = select_next({"active_heavy_render": True,
                              "candidates": [item("404", status="blocked", source_verified=False),
                                             item("prepare", storyboard_ready=False)]})
        self.assertEqual(result["id"], "prepare")
        self.assertIn("storyboard_ready", result["missing_gates"])

    def test_invalid_candidates_fail_closed(self):
        result = select_next({"active_heavy_render": False, "candidates": {"id": "x"}})
        self.assertEqual(result["reason"], "invalid queue snapshot")

    def test_invalid_deduplication_fails_closed(self):
        result = select_next({"active_heavy_render": False, "running_ids": None,
                              "candidates": [item()]})
        self.assertEqual(result["reason"], "invalid deduplication snapshot")

    def test_nested_workflow_is_not_eligible(self):
        result = select_next({"active_heavy_render": False,
                              "candidates": [item(workflow_path=".github/workflows/nested/test.yml")]})
        self.assertEqual(result["status"], "preparing")

    def test_malformed_item_does_not_stop_independent_candidate(self):
        result = select_next({"active_heavy_render": False,
                              "candidates": [None, item("good")]})
        self.assertEqual(result["id"], "good")

    def test_snapshot_false_must_be_boolean(self):
        result = select_next({"active_heavy_render": 0, "candidates": [item()]})
        self.assertEqual(result["status"], "preparing")


if __name__ == "__main__":
    unittest.main()
