"""Regression tests for WOW LAB mask audit. Run: python -m unittest discover -s wow_lab/tests -v"""
import sys
import unittest
from pathlib import Path
import cv2
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from mask_audit import audit

class MaskAuditRegression(unittest.TestCase):
    def setUp(self):
        self.source=np.full((400,400,3),240,np.uint8)
        self.mask=np.zeros((400,400),np.uint8)
        cv2.ellipse(self.mask,(200,200),(70,105),0,0,360,255,-1)
        self.source[self.mask>0]=(30,60,100)

    def test_clean_subject_passes_geometry_only(self):
        r=audit(self.source,self.mask)
        self.assertTrue(r["pass"],r)
        self.assertFalse(r["semantic_completeness_verified"])
        self.assertTrue(r["requires_visual_review"])

    def test_missing_mask_fails(self):
        self.assertFalse(audit(self.source,None)["pass"])

    def test_wrong_size_fails(self):
        self.assertIn("dimension_mismatch",audit(self.source,self.mask[:200])["reasons"])

    def test_background_leak_fails(self):
        mask=self.mask.copy()
        mask[:50,:]=255
        self.assertIn("mask_touches_image_border",audit(self.source,mask)["reasons"])

    def test_multiple_subjects_fail(self):
        mask=self.mask.copy()
        cv2.circle(mask,(55,55),24,255,-1)
        self.assertIn("multiple_or_missing_subject_components",audit(self.source,mask)["reasons"])

    def test_internal_holes_fail(self):
        mask=self.mask.copy()
        for x,y in [(175,170),(225,170),(200,220)]:
            cv2.circle(mask,(x,y),12,0,-1)
        self.assertIn("internal_holes_subject_missing_patches",audit(self.source,mask)["reasons"])

    def test_background_patch_with_no_edge_fails(self):
        source=np.full_like(self.source,200)
        self.assertIn("weak_boundary_contrast_background_leak_risk",audit(source,self.mask)["reasons"])

if __name__=="__main__":
    unittest.main()
