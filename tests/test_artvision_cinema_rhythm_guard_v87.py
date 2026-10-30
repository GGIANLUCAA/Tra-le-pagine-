"""Synthetic controls for read-only ArtVision Cinema cadence review."""
import tempfile
import unittest
from pathlib import Path
import cv2
import numpy as np
from src.artvision_cinema_rhythm_guard_v87 import inspect


class RhythmGuardTests(unittest.TestCase):
    def make_clip(self, path, segments, fps=10):
        writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (135, 240))
        self.assertTrue(writer.isOpened())
        for seconds, intensity in segments:
            frame = np.full((240, 135, 3), intensity, dtype=np.uint8)
            for _ in range(int(seconds * fps)):
                writer.write(frame)
        writer.release()

    def test_periodic_and_long_black_outro_flagged(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "synthetic.mp4"
            self.make_clip(path, [(1, 30 if i % 2 else 235) for i in range(9)] + [(6, 0)])
            report = inspect(str(path))
            self.assertGreaterEqual(len(report["hard_cut_candidates_seconds"]), 8)
            self.assertEqual(len(report["advisories"]), 2)
            self.assertGreaterEqual(report["trailing_majority_black_seconds"], 5.0)
            self.assertFalse(report["v25_approved"])

    def test_stable_nonblack_has_no_advisories(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "stable.mp4"
            self.make_clip(path, [(3, 140)])
            self.assertEqual(inspect(str(path))["advisories"], [])

    def test_nonexistent_path_fails(self):
        with self.assertRaises(ValueError):
            inspect("/does/not/exist.mp4")


if __name__ == "__main__":
    unittest.main()
