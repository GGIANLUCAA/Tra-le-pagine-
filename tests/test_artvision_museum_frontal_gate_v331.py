"""V331 frontal framing hard gate: strict positives and negative regressions."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from artvision_museum_frontal_gate_v331 import assess, evaluate_quad


class GeometryV331(unittest.TestCase):
    def test_frontal_perfect(self):
        pts=[[160,400],[560,400],[560,700],[160,700]]
        v=evaluate_quad(pts,720,1280,160/120)
        self.assertTrue(v["passed"],v)
        self.assertEqual(v["problems"],[])

    def test_unacceptable_skewed_wall(self):
        # Perspective: top is 20% shorter and right is much taller.
        pts=[[183,360],[548,386],[565,738],[150,699]]
        v=evaluate_quad(pts,720,1280,160/120)
        self.assertFalse(v["passed"])
        self.assertIn("trapezoid_or_oblique_perspective",v["problems"])

    def test_rolled_canvas(self):
        v=evaluate_quad([[145,380],[540,409],[520,710],[125,681]],720,1280)
        self.assertFalse(v["passed"])
        self.assertIn("picture_is_rolled_relative_to_wall",v["problems"])

    def test_not_centered(self):
        v=evaluate_quad([[270,400],[670,400],[670,700],[270,700]],720,1280,160/120)
        self.assertFalse(v["passed"])
        self.assertIn("painting_off_horizontal_center",v["problems"])

    def test_artwork_ratio_stretched(self):
        v=evaluate_quad([[160,400],[560,400],[560,650],[160,650]],720,1280,160/120)
        self.assertFalse(v["passed"])
        self.assertIn("painting_stretched_or_proportions_incorrect",v["problems"])

    def test_invalid_corners_not_a_pass(self):
        with self.assertRaises(ValueError):
            evaluate_quad([[1,2],[4,2],[1,7]],720,1280)

    def create_dossier(self, dirpath, corners=None):
        if corners is None: corners=[[160,400],[560,400],[560,700],[160,700]]
        sha={}
        for role in ("entry_frontal","exit_frontal"):
            file=dirpath/(role+".png")
            Image.new("RGB",(720,1280),(12,18,23)).save(file)
            sha[role]=hashlib.sha256(file.read_bytes()).hexdigest()
        return {
           "schema":"artvision-museum-frontal-v331",
           "variant":"cinema_museum",
           "artwork":{"width_cm":160,"height_cm":120},
           "video":{"sha256":"a"*64,"sha256_attested_by_independent_readback":True},
           "samples":[{"role":role,"png":role+".png","png_sha256":sha[role],
                       "painting_inner_corners_px":corners,"timestamp_s":t}
               for role,t in (("entry_frontal",1.0),("exit_frontal",46.0))]
        }

    def test_real_png_hash_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)
            dossier=self.create_dossier(base)
            self.assertTrue(assess(dossier,base)["passed_geometry_gate"])
            dossier["samples"][0]["png_sha256"]="0"*64
            out=assess(dossier,base)
            self.assertFalse(out["passed_geometry_gate"])
            self.assertIn("entry_frontal_frame_sha_mismatch",out["errors"])

    def test_real_video_hash_when_file_supplied(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)
            dossier=self.create_dossier(base)
            (base/"film.mp4").write_bytes(b"test")
            dossier["video"]={"file":"film.mp4","sha256":"b"*64}
            self.assertIn("video_file_hash_mismatch",assess(dossier,base)["errors"])

    def test_missing_exit_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)
            dossier=self.create_dossier(base)
            dossier["samples"].pop()
            self.assertIn("both_entry_and_exit_frontal_samples_required",
                          assess(dossier,base)["errors"])

    def test_angle_exception_never_auto_approved(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)
            dossier=self.create_dossier(base,[[183,360],[548,386],[565,738],[150,699]])
            dossier["angled_exception"]={"requested":True,
                "artwork_specific_rationale":"A deliberate rare shot of this work requires seeing its thickness and adjacent room.",
                "explicit_owner_artistic_approval":False,
                "preview_viewed_at_full_speed":True}
            result=assess(dossier,base)
            self.assertFalse(result["passed_geometry_gate"])
            self.assertIn("angle_exception_not_approved_by_owner",result["errors"])
            dossier["angled_exception"]["explicit_owner_artistic_approval"]=True
            result=assess(dossier,base)
            self.assertTrue(result["passed_geometry_gate"])
            self.assertFalse(result["artistic_approval"])
            self.assertFalse(result["Gold_V25"])


if __name__=="__main__":unittest.main()
