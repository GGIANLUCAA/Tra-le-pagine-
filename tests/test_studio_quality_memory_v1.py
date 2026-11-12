"""Offline regression tests: global learning requires evidence and deliberate PR."""
from __future__ import annotations
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from studio_quality_memory_v1 import (load, applicable, project_summary, record_feedback,
                                       promote_feedback, DEFAULT_PATH)
from video_director_v13 import brief
from studio_cycle_handoff_v1 import handoff


class StudioMemoryTests(unittest.TestCase):
    def test_current_approved_rules_load_but_are_not_claimed_verified(self):
        doc = load(DEFAULT_PATH)
        self.assertIsNotNone(doc)
        self.assertGreaterEqual(len(doc["lessons"]), 6)
        self.assertFalse(doc["history"])
        rows = applicable(doc, "storia_rivive")
        ids = {r["id"] for r in rows}
        self.assertIn("L001_no_ai_stamp_endings", ids)
        self.assertIn("L005_storia_vidu_source_lock", ids)
        self.assertNotIn("L003_museum_authentic_scale", ids)
        self.assertTrue(all(r["status"] == "owner_approved" for r in rows))
        self.assertTrue(all(not r["effectiveness_proven_by_new_video"] for r in rows))

    def test_corrupt_or_missing_memory_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            missing = Path(temp) / "missing.json"
            self.assertIsNone(load(missing))
            self.assertEqual(project_summary(None, "artvision")["state"], "MISSING_OR_INVALID")
            missing.write_text('{"schema":"studio-video-lessons-v1","lessons":[{}],"history":[]}')
            self.assertIsNone(load(missing))

    def test_new_feedback_is_reported_and_cannot_generalize_by_itself(self):
        doc = load()
        self.assertIsNotNone(doc)
        note = {"id": "feedback_20261110_001", "work_id": "simberg_garden",
                "slot_id": "critico_museum", "note": "Inquadratura museo troppo rapida",
                "category": "direction", "status": "verified_effective",
                "owner_requested_generalization": True, "created_at": "2026-11-10T18:00:00Z"}
        revised = record_feedback(doc, note)
        self.assertEqual(revised["history"][-1]["status"], "reported")
        self.assertEqual(len(revised["lessons"]), len(doc["lessons"]))
        self.assertEqual(len(doc["history"]), 0, "Never mutate original source in place")
        with self.assertRaises(ValueError):
            record_feedback(revised, note)

    def test_promotion_fails_without_human_and_real_media_evidence(self):
        doc = load()
        note = {"id": "feedback_20261110_002", "work_id": "the_tower_of_babel",
                "slot_id": "cinema_museum", "note": "L'avvio del museo e troppo veloce",
                "category": "pacing", "status": "reported"}
        reported = record_feedback(doc, note)
        lesson = {"id": "L099_museum_entry", "title": "Ingresso museo",
                  "status": "verified_effective",
                  "applies_to": ["artvision_cinema"],
                  "source": "docs/qa/comparison.md", "rule": "Ritmo corretto",
                  "check": "Rivedi il MP4", "effectiveness_proven_by_new_video": True}
        with self.assertRaises(ValueError):
            promote_feedback(reported, note["id"], lesson)
        lesson.update(owner_confirmed=True, evidence_sha256="a" * 64,
                      comparison_report="docs/qa/comparison.md")
        reported["history"][-1].update(status="verified_effective", owner_confirmed=True,
                                      before_after_comparison=True,
                                      video_sha256="b" * 64,
                                      qa_reference="docs/qa/comparison.md")
        promoted = promote_feedback(reported, note["id"], lesson)
        self.assertIn("L099_museum_entry",
                      [r["id"] for r in applicable(promoted, "artvision_cinema")])
        self.assertNotIn("L099_museum_entry",
                         [r["id"] for r in applicable(promoted, "storia_rivive")])

    def test_new_project_receives_snapshot_not_automatic_gold(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "new"
            project = brief("storia_rivive", "Venezia 1896", out)
            saved = json.loads((out / "STUDIO_QUALITY_CHECKLIST_V1.json").read_text())
            self.assertEqual(saved["format"], "storia_rivive")
            self.assertFalse(saved["video_quality_verified"])
            self.assertIn("L005_storia_vidu_source_lock",
                          project["studio_quality_memory"]["active_lesson_ids"])
            self.assertIn("Memoria regia condivisa", (out / "BRIEF_GPT.md").read_text())
            self.assertFalse(project["studio_quality_memory"]["improvement_verified"])

    def test_existing_research_handoff_inherits_only_instructions(self):
        row = handoff("artvision", None)
        self.assertEqual(row["quality_memory"]["state"], "AVAILABLE")
        self.assertIn("L003_museum_authentic_scale", row["quality_memory"]["lesson_ids"])
        self.assertEqual(row["new_finished_mp4"], 0)
        self.assertFalse(row["quality_memory"]["proof_of_improvement_in_new_mp4"])
        self.assertFalse(row["auto_render_started"])


if __name__ == "__main__":
    unittest.main()
