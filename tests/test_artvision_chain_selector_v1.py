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
        self.assertEqual(select_next({"candidates":[item()]})["status"], "blocked")
    def test_active_render_blocks(self):
        self.assertEqual(select_next({"active_heavy_render":True,"candidates":[item()]})["status"],"blocked")
    def test_ready_candidate(self):
        self.assertEqual(select_next({"active_heavy_render":False,"candidates":[item()]})["id"],"new")
    def test_skip_duplicates(self):
        self.assertEqual(select_next({"active_heavy_render":False,"completed_ids":["old"],
          "candidates":[item("old"),item("new") ]})["id"],"new")
    def test_rights_gate(self):
        self.assertEqual(select_next({"active_heavy_render":False,"candidates":[item(rights_verified=False)]})["status"],"blocked")
    def test_running_gate(self):
        self.assertEqual(select_next({"active_heavy_render":False,"running_ids":["new"],"candidates":[item()]})["status"],"blocked")
    def test_invalid_workflow(self):
        self.assertEqual(select_next({"active_heavy_render":False,"candidates":[item(workflow_path="other.yml")]})["status"],"blocked")

if __name__ == "__main__":
    unittest.main()
