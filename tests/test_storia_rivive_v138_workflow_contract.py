#!/usr/bin/env python3
"""V138 contract tests: no paid API calls, only source research for Versailles 1919."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/storia-v138-versailles-source-audit.yml"
BANK = ROOT / "queue/storia_rivive_candidates_v58.json"
ID = "versailles_treaty_1919"


class VersaillesWorkflowSafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = WORKFLOW.read_text(encoding="utf-8")
        cls.candidates = json.loads(BANK.read_text(encoding="utf-8"))["candidates"]

    def test_exact_catalogued_candidate_and_public_source_page(self):
        found = [x for x in self.candidates if x.get("id") == ID]
        self.assertEqual(len(found), 1)
        source = found[0]
        self.assertEqual(source["license"], "PUBLIC_DOMAIN")
        self.assertTrue(source["source_page"].startswith("https://commons.wikimedia.org/wiki/File:"))
        self.assertIn(source["source_page"], self.text)
        self.assertIn('c["id"]=="'+ID+'"', self.text)
        self.assertNotIn("white_house_1917_1921", self.text)

    def test_workflow_no_schedule_or_paid_publishing_service(self):
        workflow = self.text
        self.assertIn("  workflow_call:", workflow)
        self.assertIn("  workflow_dispatch:", workflow)
        self.assertNotIn("  pull_request:", workflow)
        self.assertNotIn("  schedule:", workflow)
        self.assertIn("  contents: read", workflow)
        self.assertNotIn("contents: write", workflow)
        self.assertNotIn("secrets.", workflow)
        self.assertNotIn("VIDU_API_KEY", workflow)
        self.assertNotIn("gh release create", workflow)
        self.assertIn('if order["paid_api_call_permitted"] or order["publish_permitted"]:', workflow)

    def test_full_source_pipeline_uses_one_candidate_and_real_byte_guards(self):
        workflow = self.text
        for script in ("storia_rivive_scout_v101.py",
                       "storia_rivive_v134_cache_readiness.py",
                       "storia_rivive_adaptive_sampling_v124.py",
                       "storia_rivive_v125_real_motion_audit.py",
                       "storia_rivive_v126_balanced_motion_review.py",
                       "storia_rivive_v126_frame_diversity.py",
                       "storia_rivive_v128_balanced_frame_review.py",
                       "storia_rivive_v129_prefreeze_motion_strips.py",
                       "storia_rivive_v136_source_decision"):
            self.assertIn(script, workflow)
        self.assertIn('steps.source.outputs.ready == \'true\'', workflow)
        self.assertIn('"status":source_state(readiness,motion,balanced,visual,strips)', workflow)

    def test_artifact_does_not_upload_original_media_or_sensitive_balance(self):
        content = self.text
        self.assertIn("actions/upload-artifact@v4", content)
        self.assertIn("if: always()", content)
        self.assertIn("PREFREEZE_MOTION_STRIPS_V129.jpg", content)
        self.assertIn("REAL_SOURCE_AUDIT_V138.json", content)
        files = content.split("      - name: Save only source metadata", 1)[-1]
        self.assertNotIn("ORIGINAL_ARCHIVE.webm", files)
        self.assertNotIn("original_frames/", files)
        self.assertNotIn("PRIVATE_CREDIT_REPORT", files)
        self.assertIn('"rights_italy_verified":False', content)
        self.assertIn('"publication_permitted":False', content)

    def test_workflow_paths_all_use_own_isolated_work_directory(self):
        text = self.text
        self.assertIn("output/storia_v138_versailles", text)
        self.assertNotIn("output/storia_v136_white_house", text)
        self.assertNotIn("output/storia_v121_real/", text)
        self.assertNotIn("requests/vidu/", text)


if __name__ == "__main__":
    unittest.main()
