#!/usr/bin/env python3
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ai_director_bridge_v1 import from_v13, from_four_variants, bridge


class BridgeTests(unittest.TestCase):
    def test_v13_without_durations_refuses_to_invent_timing(self):
        p = {"schema": "video-project-v13", "format": "documentario", "topic": "Le città",
             "assets": [{"id": "asset1", "source": "https://example.org/photo",
                         "rights": "public-domain"}],
             "scenes": [{"asset_id": "asset1", "description": "A street"}]}
        out = from_v13(p)
        self.assertFalse(out["timecodes_available"])
        self.assertEqual(out["scenes"], [])
        self.assertFalse(out["human_artistic_approval"])

    def test_v13_timed_scenes(self):
        p = {"schema": "video-project-v13", "format": "documentario", "topic": "Le città",
             "assets": [{"id": "x"}], "scenes": [
                 {"asset_id": "x", "duration_seconds": 2.3},
                 {"asset_id": "x", "duration_seconds": 1.9}
             ]}
        out = from_v13(p)
        self.assertEqual(out["scenes"][1]["start_s"], 2.3)
        self.assertAlmostEqual(out["scenes"][1]["end_s"], 4.2)
        self.assertTrue(out["timecodes_available"])

    def test_four_variants_keep_all_names_and_shared_words(self):
        v = {}
        for name in ("critico_standard", "critico_museum", "cinema_standard", "cinema_museum"):
            v[name] = {"scenes": [
                {"duration_seconds": 2.4, "kind": "detail", "detail_id": "d1",
                 "spoken_line": "Qui vediamo il vero dettaglio" if name.startswith("critico") else ""}
            ]}
        p = {"schema": "artvision-4x1-v1", "topic": "The Night Watch",
             "artist": "Rembrandt", "variants": v}
        out = from_four_variants(p)
        self.assertEqual(set(out), set(v))
        self.assertEqual(out["critico_standard"]["narration"], out["critico_museum"]["narration"])
        self.assertFalse(out["cinema_standard"]["narration"])

    def test_bridge_writes_android_report_without_generation(self):
        p = {"schema": "video-project-v13", "format": "documentario", "topic": "Le città",
             "assets": [], "scenes": []}
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "project.json"
            src.write_text(json.dumps(p))
            dst = Path(tmp) / "report"
            result = bridge(src, dst)
            self.assertFalse(result["automatic_publish"])
            self.assertFalse(result["render_performed"])
            self.assertTrue((dst / "INDEX.html").is_file())
            self.assertTrue((dst / "project_v13/ANDROID_REPORT.html").is_file())

    def test_rejects_missing_fourth_variant(self):
        with self.assertRaises(ValueError):
            from_four_variants({"schema": "artvision-4x1-v1",
                                "topic": "Test", "variants": {"critico_standard": {}}})


if __name__ == "__main__":
    unittest.main()
