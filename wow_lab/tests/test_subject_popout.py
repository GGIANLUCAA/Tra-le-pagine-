"""Offline, deterministic WOW LAB pop-out integration checks."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from subject_popout import (PreflightRejected, preflight_source,
                           make_subject_panel, composite_popout)


def sample_image():
    image = np.full((400, 400, 3), 242, np.uint8)
    cv2.ellipse(image, (200, 210), (70, 105), 0, 0, 360, (40, 60, 90), -1)
    return Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))


class SubjectPopoutTests(unittest.TestCase):
    def test_mask_audit_precedes_render_and_has_review_flag(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            clean, original, mask = preflight_source(sample_image(), root)
            self.assertEqual(clean.size, original.size)
            self.assertEqual(mask.size, original.size)
            self.assertTrue((root / "MASK_BEFORE_RENDER.jpg").exists())
            self.assertTrue((root / "SUBJECT_MASK.png").exists())
            report = json.loads((root / "SUBJECT_PREFLIGHT.json").read_text())
            self.assertTrue(report["technical_pass"])
            self.assertFalse(report["artistic_approval"])
            self.assertFalse(report["semantic_completeness_verified"])
            self.assertTrue(report["inpainting_disclosed"])

    def test_blank_source_fails_closed_without_video(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with self.assertRaises(PreflightRejected):
                preflight_source(Image.new("RGB", (400, 400), "white"), root)
            self.assertTrue((root / "SUBJECT_PREFLIGHT.json").exists())
            self.assertFalse(list(root.glob("*.mp4")))

    def test_subject_moves_independently_from_panel(self):
        with tempfile.TemporaryDirectory() as folder:
            clean, original, mask = preflight_source(sample_image(), Path(folder))
            panel = make_subject_panel(original, mask, (310, 310, 4), (260, 260))
            # The original 400x400 synthetic ellipse is deliberately scaled
            # to 230x230 inside the 260x260 art area. Requiring >10,000 alpha
            # pixels is physically inconsistent with this scale. Instead,
            # verify the complete *rescaled* silhouette survives compositing.
            expected_mask = np.asarray(mask.resize((230, 230),
                                        Image.Resampling.NEAREST)) >= 128
            composed_mask = panel[22:252, 22:252, 3] >= 32
            expected_area = int(np.count_nonzero(expected_mask))
            actual_area = int(np.count_nonzero(composed_mask))
            self.assertGreater(expected_area, 5000)
            self.assertGreater(actual_area, expected_area * .90)
            self.assertLess(actual_area, expected_area * 1.15)
            self.assertGreater(
                np.count_nonzero(composed_mask & expected_mask),
                expected_area * .97)
            base = np.full((960, 540, 3), 75, np.uint8)
            quad = np.float32([[120, 130], [420, 130], [420, 440], [120, 440]])
            start = composite_popout(base, panel, quad, 0.0)
            end = composite_popout(base, panel, quad, 0.78)
            self.assertGreater(float(np.mean(cv2.absdiff(start, end))), 1.0)
            self.assertEqual(end.shape, base.shape)

if __name__ == "__main__":
    unittest.main()
