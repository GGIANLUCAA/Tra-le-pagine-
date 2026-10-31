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

    def test_failed_mask_or_video_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for name in REQUIRED:
                (root/name).write_bytes(b"placeholder")
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
