"""V210 source-locked shot-aware preselection regressions; no external calls."""
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import storia_rivive_v210_shot_aware_selection as v210


def fixture(folder):
    film = folder / "ORIGINAL_ARCHIVE.webm"
    film.write_bytes(b"synthetic fixture: only detector is stubbed, source bytes are SHA checked")
    scout = {"original_sha256": hashlib.sha256(film.read_bytes()).hexdigest(),
             "duration_s": 60.0, "source_frames_extracted": 12}
    frames = [{"filename": f"frame_{i:02d}.png",
               "source_visual_quality_score": round(0.50 + (i % 3) * 0.1, 3)}
              for i in range(1, 13)]
    ranking = {"status": v210.READY, "all_candidates": frames}
    return film, ranking, scout


class ShotAwareSelectionTests(unittest.TestCase):
    def test_uses_five_distinct_segments_instead_of_score_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            film, ranking, scout = fixture(root)
            result = v210.select(ranking, scout, root, detector=lambda *_: [8, 18, 28, 38, 48])
            self.assertEqual(result["status"], v210.READY, result)
            self.assertEqual(len(result["preselected"]), 5)
            self.assertEqual(len(set(result["candidate_segment_times_s"])), 5)
            self.assertFalse(result["five_distinct_shots_approved"])
            self.assertFalse(result["provider_calls_permitted"])

    def test_single_shot_does_not_produce_fake_five(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, ranking, scout = fixture(root)
            result = v210.select(ranking, scout, root, detector=lambda *_: [])
            self.assertEqual(result["reason"], "FIVE_SHOT_SEGMENTS_WITH_VALID_LEADIN_UNAVAILABLE")
            self.assertEqual(result["preselected"], [])

    def test_cut_during_lead_in_does_not_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, ranking, scout = fixture(root)
            # Samples at 5-second intervals; cut just before sample makes it unsafe.
            result = v210.select(ranking, scout, root,
                                 detector=lambda *_: [4.5, 9.5, 14.5, 19.5, 24.5,
                                                      29.5, 34.5, 39.5, 44.5, 49.5])
            self.assertEqual(result["reason"], "FIVE_SHOT_SEGMENTS_WITH_VALID_LEADIN_UNAVAILABLE")

    def test_modified_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            film, ranking, scout = fixture(root)
            film.write_bytes(b"changed")
            result = v210.select(ranking, scout, root, detector=lambda *_: [8, 18, 28, 38, 48])
            self.assertEqual(result["reason"], "SOURCE_HASH_CHANGED")

    def test_overlong_source_is_bounded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, ranking, scout = fixture(root)
            scout["duration_s"] = 489.0
            result = v210.select(ranking, scout, root, detector=lambda *_: [])
            self.assertEqual(result["reason"], "SOURCE_TOO_LONG_FOR_BOUNDED_SCENE_SCAN")


if __name__ == "__main__":
    unittest.main()
