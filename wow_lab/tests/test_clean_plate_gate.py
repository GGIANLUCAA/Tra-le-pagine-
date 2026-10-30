"""Fail-closed synthetic background tests: no misleading inpainted scenery."""
import sys
import unittest
from pathlib import Path
import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from subject_popout import audit_clean_plate

class CleanPlateGate(unittest.TestCase):
    def fixtures(self):
        src=np.full((400,400,3),240,np.uint8)
        mask=np.zeros((400,400),np.uint8)
        cv2.ellipse(mask,(200,200),(65,90),0,0,360,255,-1)
        src[mask>0]=(40,70,100)
        return src,mask

    def test_uniform_background_and_matching_inpaint_pass_technical_only(self):
        src,mask=self.fixtures()
        clean=cv2.inpaint(src,mask,5,cv2.INPAINT_TELEA)
        report=audit_clean_plate(src,mask,clean)
        self.assertTrue(report["pass"],report)
        self.assertFalse(report["artistic_approval"])
        self.assertTrue(report["requires_visual_review"])

    def test_patterned_background_is_rejected(self):
        src,mask=self.fixtures()
        y,x=np.indices(mask.shape)
        pattern=((x//7+y//7)%2)==0
        src[(mask==0)&pattern]=(20,20,20)
        clean=cv2.inpaint(src,mask,5,cv2.INPAINT_TELEA)
        report=audit_clean_plate(src,mask,clean)
        self.assertFalse(report["pass"],report)
        self.assertIn("complex_background_near_subject",report["reasons"])

    def test_wrong_inpaint_color_is_rejected(self):
        src,mask=self.fixtures()
        fake=np.full_like(src,(0,0,220))
        report=audit_clean_plate(src,mask,fake)
        self.assertFalse(report["pass"],report)
        self.assertIn("inpaint_inconsistent_with_background",report["reasons"])

    def test_dimension_mismatch_is_rejected(self):
        src,mask=self.fixtures()
        report=audit_clean_plate(src,mask,src[:300])
        self.assertFalse(report["pass"])
        self.assertIn("invalid_clean_plate_inputs",report["reasons"])

if __name__=="__main__":
    unittest.main()
