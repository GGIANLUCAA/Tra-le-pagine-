"""Offline regression tests: no source downloads, paid services or core imports."""
import sys
import unittest
from pathlib import Path
import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from subject_extractor import propose_mask


class SubjectExtractorTests(unittest.TestCase):
    def test_single_dark_silhouette(self):
        image = np.full((400, 400, 3), 245, np.uint8)
        cv2.ellipse(image, (200, 200), (70, 100), 0, 0, 360, (30, 55, 70), -1)
        mask, report = propose_mask(image)
        self.assertTrue(report["pass"], report)
        self.assertIsNotNone(mask)
        self.assertGreater(np.count_nonzero(mask), 17000)
        self.assertFalse(report["semantic_completeness_verified"])

    def test_blank_background_rejected(self):
        image = np.full((400, 400, 3), 245, np.uint8)
        mask, report = propose_mask(image)
        self.assertIsNone(mask)
        self.assertIn("no_confident_subject", report["reasons"])

    def test_two_separate_figures_rejected(self):
        image = np.full((400, 400, 3), 245, np.uint8)
        cv2.circle(image, (120, 190), 58, (20, 20, 20), -1)
        cv2.circle(image, (280, 190), 58, (20, 20, 20), -1)
        mask, report = propose_mask(image)
        self.assertIsNone(mask)
        self.assertIn("multiple_ambiguous_components", report["reasons"])

    def test_busy_background_rejected(self):
        image = np.random.default_rng(23).integers(0, 256, (400, 400, 3), dtype=np.uint8)
        mask, report = propose_mask(image)
        self.assertIsNone(mask)
        self.assertIn("nonuniform_background", report["reasons"])

    def test_edge_touching_subject_rejected(self):
        image = np.full((400, 400, 3), 245, np.uint8)
        cv2.rectangle(image, (0, 110), (220, 290), (10, 10, 10), -1)
        mask, report = propose_mask(image)
        self.assertIsNone(mask)


if __name__ == "__main__":
    unittest.main()
