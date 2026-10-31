"""Fail-closed tests for the real WOW LAB rendering entrypoint.

Offline tests may use pure helper functions, but cannot render or publish while
release history and the Actions queue are unverifiable.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import engine


class LivePreflightSafety(unittest.TestCase):
    def test_missing_github_context_rejected(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "WOW_LAB_LIVE_PREFLIGHT_REQUIRED"):
                engine.require_live_preflight_context()

    def test_other_repository_rejected(self):
        env = {"GITHUB_REPOSITORY": "another/repository",
               "GITHUB_RUN_ID": "12345", "GITHUB_TOKEN": "dummy"}
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaisesRegex(RuntimeError, "repository context missing"):
                engine.require_live_preflight_context()

    def test_missing_or_malformed_run_id_rejected(self):
        for run_id in ("", "not-a-run", "123T", "1/2"):
            env = {"GITHUB_REPOSITORY": "GGIANLUCAA/Tra-le-pagine-",
                   "GITHUB_RUN_ID": run_id, "GITHUB_TOKEN": "dummy"}
            with self.subTest(run_id=run_id), patch.dict(os.environ, env, clear=True):
                with self.assertRaisesRegex(RuntimeError, "GitHub run ID missing"):
                    engine.require_live_preflight_context()

    def test_missing_token_rejected(self):
        env = {"GITHUB_REPOSITORY": "GGIANLUCAA/Tra-le-pagine-",
               "GITHUB_RUN_ID": "12345"}
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaisesRegex(RuntimeError, "GitHub token missing"):
                engine.require_live_preflight_context()

    def test_complete_github_context_accepted(self):
        env = {"GITHUB_REPOSITORY": "GGIANLUCAA/Tra-le-pagine-",
               "GITHUB_RUN_ID": "12345", "GITHUB_TOKEN": "dummy"}
        with patch.dict(os.environ, env, clear=True):
            engine.require_live_preflight_context()

    def test_existing_run_artifact_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder)
            (out / "SUBJECT_PREFLIGHT.json").write_text('{"technical_pass":false}')
            with self.assertRaisesRegex(RuntimeError, "WOW_LAB_RUN_DIRECTORY_ALREADY_EXISTS"):
                engine.require_fresh_run_directory(out)

    def test_existing_empty_directory_rejected_but_missing_directory_accepted(self):
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder)
            with self.assertRaisesRegex(RuntimeError, "WOW_LAB_RUN_DIRECTORY_ALREADY_EXISTS"):
                engine.require_fresh_run_directory(out)
            engine.require_fresh_run_directory(out / "fresh")

    def test_render_gate_runs_before_network_and_output_writes(self):
        code = (ROOT / "engine.py").read_text(encoding="utf-8")
        run = code[code.index("def run(args):"):]
        self.assertLess(run.index("require_live_preflight_context()"),
                        run.index("ensure_no_parallel_wow_render()"))
        self.assertLess(run.index("require_fresh_run_directory(out)"),
                        run.index("out.mkdir(parents=True,exist_ok=False)"))
        self.assertLess(run.index("ensure_slot_available(stamp, past)"),
                        run.index("out.mkdir(parents=True,exist_ok=False)"))


if __name__ == "__main__":
    unittest.main()
