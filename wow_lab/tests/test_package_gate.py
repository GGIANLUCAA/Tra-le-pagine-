import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from package_gate import REQUIRED, validate_preview_package

class PreviewPackageGateTests(unittest.TestCase):
    def test_empty_package_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            report=validate_preview_package(Path(temp))
            self.assertFalse(report["technical_preview_package_pass"])
            self.assertFalse(report["release_as_success_allowed"])

    def test_complete_technical_preview_does_not_approve_art(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for name in REQUIRED:
                (root/name).write_bytes(b"placeholder")
            for name in ("MASK_BEFORE_RENDER.jpg","VIDEO_CONTACT_SHEET.jpg","COVER.jpg"):
                (root/name).write_bytes(b"\xff\xd8\xff" + b"sample")
            (root/"SUBJECT_MASK.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"sample")
            (root/"WOW_LAB_PREVIEW.mp4").write_bytes(b"\x00\x00\x00\x18ftypisom" + b"sample")
            data={
                "SUBJECT_PREFLIGHT.json":{"technical_pass":True,"artistic_approval":False},
                "CLEAN_PLATE_AUDIT.json":{"pass":True,"artistic_approval":False},
                "POPOUT_GEOMETRY_PREFLIGHT.json":{"pass":True,"artistic_approval":False},
                "VIDEO_REVIEW.json":{"technical_pass":True,"full_decode_pass":True,
                                     "artistic_approval":False},
            }
            for name, value in data.items():
                (root/name).write_text(json.dumps(value))
            result=validate_preview_package(root)
            self.assertTrue(result["technical_preview_package_pass"],result)
            self.assertFalse(result["approved_master"])
            self.assertFalse(result["release_as_success_allowed"])

    def test_invalid_media_placeholders_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for name in REQUIRED:
                (root/name).write_bytes(b"placeholder")
            for name, key in (("SUBJECT_PREFLIGHT.json","technical_pass"),
                              ("CLEAN_PLATE_AUDIT.json","pass"),
                              ("POPOUT_GEOMETRY_PREFLIGHT.json","pass"),
                              ("VIDEO_REVIEW.json","technical_pass")):
                report={key:True}
                if name=="VIDEO_REVIEW.json":
                    report["full_decode_pass"]=True
                (root/name).write_text(json.dumps(report))
            result=validate_preview_package(root)
            self.assertFalse(result["technical_preview_package_pass"])
            self.assertTrue(any("invalid_media_signature" in x for x in result["reasons"]))

    def test_failed_mask_or_video_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for name in REQUIRED:
                (root/name).write_bytes(b"placeholder")
            for name in ("MASK_BEFORE_RENDER.jpg","VIDEO_CONTACT_SHEET.jpg","COVER.jpg"):
                (root/name).write_bytes(b"\xff\xd8\xff" + b"sample")
            (root/"SUBJECT_MASK.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"sample")
            (root/"WOW_LAB_PREVIEW.mp4").write_bytes(b"\x00\x00\x00\x18ftypisom" + b"sample")
            data={
                "SUBJECT_PREFLIGHT.json":{"technical_pass":False},
                "CLEAN_PLATE_AUDIT.json":{"pass":True},
                "POPOUT_GEOMETRY_PREFLIGHT.json":{"pass":True},
                "VIDEO_REVIEW.json":{"technical_pass":False,"full_decode_pass":False},
            }
            for name,value in data.items():
                (root/name).write_text(json.dumps(value))
            result=validate_preview_package(root)
            self.assertFalse(result["technical_preview_package_pass"])
            self.assertTrue(any("failed_gate" in r for r in result["reasons"]))

if __name__=="__main__":
    unittest.main()
