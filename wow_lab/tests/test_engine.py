"""WOW LAB isolation and technical behavior tests; no internet or GPU required."""
import json
import sys
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MODULE))
import engine


class WowLabContractTests(unittest.TestCase):
    def test_config_strict_isolation(self):
        cfg = engine.read_config(MODULE / "config.json")
        self.assertTrue(cfg["enabled"])
        self.assertTrue(cfg["no_vidu"])
        self.assertTrue(cfg["no_paid_services"])
        self.assertTrue(cfg["no_core_automation_edits"])
        self.assertEqual(cfg["requested_cadence_hours"], 2)
        self.assertTrue(cfg["no_social_publish"])

    def test_slot_rounding(self):
        self.assertEqual(engine.slot_id("2026-10-29T19"), "20261029T18")
        self.assertEqual(engine.slot_id("2026-10-29T20"), "20261029T20")
        with self.assertRaises(ValueError):
            engine.slot_id("not-a-time")

    def test_autonomous_selection_parses_utc_slot_without_crashing(self):
        from unittest.mock import patch
        cfg = engine.read_config(MODULE / "config.json")
        sample = {"objectID": 400112, "isPublicDomain": True, "objectName": "Drawing",
                  "primaryImage": "https://images.metmuseum.org/test.jpg",
                  "title": "A Moth"}
        with patch.object(engine, "discovery_ids", return_value=[]), patch.object(engine, "get_json", return_value=sample):
            chosen = engine.select_artwork(cfg, "20261030T06", [])
        self.assertEqual(chosen["objectID"], 400112)

    def test_wrong_met_object_id_never_passes_candidate_selection(self):
        from unittest.mock import patch
        cfg = engine.read_config(MODULE / "config.json")
        wrong = {"objectID": 436535, "isPublicDomain": True, "objectName": "Painting",
                 "primaryImage": "https://images.metmuseum.org/test.jpg",
                 "title": "Other work"}
        with patch.object(engine, "get_json", return_value=wrong):
            with self.assertRaisesRegex(RuntimeError, "museum_object_id_mismatch"):
                engine.select_artwork(cfg, "20261031T04", [])

    def test_single_subject_mask_first_selection_configuration(self):
        cfg = engine.read_config(MODULE / "config.json")
        self.assertEqual(cfg["allowed_artwork_ids"], [400112])
        self.assertFalse(cfg["allow_museum_api_search"])
        self.assertFalse(cfg["production_ready"])

    def test_legacy_wow_releases_count_distinct_subjects(self):
        releases = [
            {"tag_name": "wow-lab-madame-x-silhouette-v2-20261030",
             "body": "Metropolitan Museum of Art CC0, object 12127."},
            {"tag_name": "wow-lab-madame-x-silhouette-v1-20261030",
             "body": "Metropolitan Museum of Art CC0, object 12127."},
            {"tag_name": "wow-lab-hokusai-45434-android-20261029",
             "body": "Met CC0 Hokusai print 45434."},
        ]
        history = engine.parse_wow_release_history(releases)
        self.assertEqual([x["object_id"] for x in history], [12127, 45434])

    def test_unverified_wow_release_history_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError, "WOW_LAB_HISTORY_UNVERIFIED"):
            engine.parse_wow_release_history([
                {"tag_name": "wow-lab-unknown-subject", "body": "No museum object ID"}
            ])

    def test_recent_six_subjects_are_never_reused(self):
        from unittest.mock import patch
        cfg = engine.read_config(MODULE / "config.json")
        cfg["allow_museum_api_search"] = False
        history = [{"object_id": value} for value in cfg["allowed_artwork_ids"]]
        with patch.object(engine, "get_json", side_effect=AssertionError("Recent object must not be fetched")):
            with self.assertRaisesRegex(RuntimeError, "No suitable verified CC0 artwork"):
                engine.select_artwork(cfg, "20261030T08", history)

    def test_artwork_rights_fail_closed(self):
        rec = {"objectID": 436535,"isPublicDomain": True,"objectName":"Painting",
               "primaryImage":"https://images.metmuseum.org/photo.jpg"}
        self.assertTrue(engine.valid_object(rec))
        rec["isPublicDomain"] = False
        self.assertFalse(engine.valid_object(rec))
        rec["isPublicDomain"] = True
        rec["primaryImage"] = "http://untrusted/image.jpg"
        self.assertFalse(engine.valid_object(rec))

    def test_visual_techniques_vary_camera(self):
        w,h=540,960
        modes = []
        for mode in engine.SAFE_MODES:
            a=engine.shot_params(mode,.15,w,h,(420,450))
            b=engine.shot_params(mode,.85,w,h,(420,450))
            self.assertGreater(float(abs(a-b).sum()), 35.0)
            modes.append(tuple(round(float(x),2) for x in b.flatten()))
        self.assertEqual(len(set(modes)),len(engine.SAFE_MODES))


    def test_every_camera_trajectory_remains_convex_and_in_safe_frame(self):
        import cv2
        import numpy as np
        W,H=540,960
        for mode in engine.SAFE_MODES:
            for dims in ((420,450),(380,532),(470,300)):
                for step in range(41):
                    p=step/40
                    quad=engine.shot_params(mode,p,W,H,dims)
                    self.assertTrue(cv2.isContourConvex(quad.astype(np.int32)),(mode,dims,p))
                    self.assertGreater(cv2.contourArea(quad),25000)
                    self.assertGreater(float(quad[:,1].min()),0)
                    self.assertLess(float(quad[:,1].max()),H*.84)

    def test_no_imports_from_parent_core(self):
        src=(MODULE/"engine.py").read_text(encoding="utf-8")
        prohibited = ["import src.", "from src", "import config.",
                      "from worker", "import site."]
        self.assertTrue(all(bad not in src for bad in prohibited))
        self.assertIn("wow_lab/runs/<unique-slot>",src)

    def test_module_has_no_owner_or_original_master_side_effects(self):
        cfg=json.loads((MODULE/"config.json").read_text())
        self.assertFalse(cfg["production_ready"])
        self.assertTrue(cfg["preview_releases_enabled"])
        self.assertTrue(cfg["no_original_master_overwrite"])
        self.assertEqual(cfg["output_scope"],"wow-lab-* releases and artifacts only")
        self.assertEqual(cfg["history_scope"],"wow-lab-v1-* GitHub releases only")


if __name__ == "__main__":
    unittest.main()
