"""Regression guard: the render runner must inspect the entire ready backlog.

The daily planning CLI still limits its displayed ready batch; only the runner
opts into scanning all ready candidates so a locally blocked candidate cannot
hide the next viable job.
"""
import ast
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class SkipBlockedBacklogTest(unittest.TestCase):
    def test_batch_plan_supports_explicit_backlog(self):
        tree = ast.parse((ROOT / "src/production_batch_v15.py").read_text())
        plan = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "plan")
        self.assertIn("include_backlog", [arg.arg for arg in plan.args.args])
        self.assertTrue(any(isinstance(node, ast.IfExp) and
                            isinstance(node.test, ast.Name) and node.test.id == "include_backlog"
                            for node in ast.walk(plan)))

    def test_runner_requests_backlog(self):
        tree = ast.parse((ROOT / "src/production_runner_v16.py").read_text())
        run = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "run_locked")
        calls = [node for node in ast.walk(run) if isinstance(node, ast.Call)
                 and isinstance(node.func, ast.Attribute) and node.func.attr == "plan"]
        self.assertEqual(len(calls), 1)
        self.assertTrue(any(kw.arg == "include_backlog" and isinstance(kw.value, ast.Constant)
                            and kw.value.value is True for kw in calls[0].keywords))


if __name__ == "__main__":
    unittest.main()
