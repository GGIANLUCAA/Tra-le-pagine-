"""Additional WOW LAB regressions: the renderer must not be mistaken for a publishable master."""
import sys
import unittest
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import mask_audit
from subject_popout import audit_popout_projection

class PublicationSafetyTests(unittest.TestCase):
    def test_mask_gate_rejects_uniform_paper_patch(self):
        image=np.full((400,400,3),210,dtype=np.uint8)
        mask=np.zeros((400,400),dtype=np.uint8)
        mask[120:280,140:260]=255
        report=mask_audit.audit(image,mask)
        self.assertFalse(report["pass"])
        self.assertIn("weak_boundary_contrast_background_leak_risk",report["reasons"])

    def test_mask_geometry_does_not_grant_artistic_approval(self):
        image=np.full((400,400,3),245,dtype=np.uint8)
        mask=np.zeros((400,400),dtype=np.uint8)
        import cv2
        cv2.circle(mask,(200,200),70,255,-1)
        image[mask>0]=(40,60,100)
        report=mask_audit.audit(image,mask)
        self.assertFalse(report["semantic_completeness_verified"])
        self.assertTrue(report["requires_visual_review"])

    def test_crossing_gate_does_not_grant_artistic_approval(self):
        layer=np.zeros((200,200,4),dtype=np.uint8)
        layer[85:121,70:130,3]=255
        quad=np.float32([[170,240],[370,240],[370,440],[170,440]])
        report=audit_popout_projection(layer,quad,width=540,height=960)
        self.assertFalse(report["artistic_approval"])

if __name__=="__main__":
    unittest.main()
