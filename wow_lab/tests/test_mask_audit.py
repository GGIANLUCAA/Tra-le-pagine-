"""WOW LAB mask gate regression tests; no internet or paid services."""
import sys
import unittest
from pathlib import Path
import cv2
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mask_audit import audit

class MaskGateTests(unittest.TestCase):
    def setUp(self):
        self.image = np.full((320, 320, 3), (210, 225, 235), np.uint8)
        self.mask = np.zeros((320, 320), np.uint8)
        cv2.ellipse(self.image, (160, 160), (65, 90), 0, 0, 360, (35, 40, 55), -1)
        cv2.ellipse(self.mask, (160, 160), (65, 90), 0, 0, 360, 255, -1)

    def test_single_contrasting_subject_passes_geometric_gate(self):
        result = audit(self.image, self.mask)
        self.assertTrue(result["pass"], result)
        self.assertFalse(result["semantic_completeness_verified"])
        self.assertTrue(result["requires_visual_review"])

    def test_background_patch_is_rejected(self):
        mask = np.zeros_like(self.mask)
        cv2.rectangle(mask, (15, 15), (85, 85), 255, -1)
        self.assertIn("weak_boundary_contrast_background_leak_risk",
                      audit(self.image, mask)["reasons"])

    def test_two_disconnected_subjects_are_rejected(self):
        image, mask = self.image.copy(), self.mask.copy()
        cv2.circle(image, (280, 280), 25, (20, 20, 20), -1)
        cv2.circle(mask, (280, 280), 25, 255, -1)
        self.assertIn("multiple_or_missing_subject_components", audit(image, mask)["reasons"])

    def test_missing_patches_inside_subject_are_rejected(self):
        mask = self.mask.copy()
        for x, y in [(145, 135), (165, 155), (170, 180), (145, 195)]:
            cv2.circle(mask, (x, y), 5, 0, -1)
        self.assertIn("internal_holes_subject_missing_patches", audit(self.image, mask)["reasons"])

    def test_border_is_rejected(self):
        mask = self.mask.copy()
        cv2.rectangle(mask, (0, 130), (45, 170), 255, -1)
        self.assertIn("mask_touches_image_border", audit(self.image, mask)["reasons"])

    def test_incompatible_dimensions_fail_closed(self):
        self.assertEqual(audit(self.image, self.mask[:100])["reasons"], ["dimension_mismatch"])

    def test_missing_mask_fails_closed(self):
        self.assertEqual(audit(self.image, None)["reasons"], ["missing_source_or_mask"])

if __name__ == "__main__":
    unittest.main()
