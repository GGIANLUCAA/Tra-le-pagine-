"""V126 frame-diversity offline regression; fixtures are artificial, NOT archive proof."""
import hashlib
import json
import random
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from src.storia_rivive_v126_frame_diversity import audit


def make_case(root, *, duplicate=False, flat=False):
    root = Path(root)
    frames = root / "original_frames"
    frames.mkdir()
    rng = random.Random(4261)
    rows = []
    source = None
    for i in range(5):
        if flat and i == 3:
            pixels = [128] * (128*96)
        elif duplicate and i == 4:
            pixels = [min(255, v+9) for v in source]
        else:
            pixels = [rng.randrange(10, 245) for _ in range(128*96)]
            if i == 0:
                source = pixels
        name = f"frame_{i:02d}.png"
        path = frames/name
        im = Image.new("L", (128,96))
        im.putdata(pixels)
        im.save(path)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append({"filename":name,"frame_sha256":digest,
                     "source_film_sha256":"a"*64,"timeline_region":i,
                     "human_camera_shot_approval":False})
    data={"version":"V125_REAL_BW_DECODED_SPATIAL_MOTION_UNAPPROVED",
          "status":"V125_FIVE_MOVING_PHOTO_REGIONS_REVIEW_REQUIRED",
          "five_genuine_camera_shots_approved":False,
          "italian_rights_verified":False,"source_video_sha256":"a"*64,
          "five_review_shots":rows}
    report=root/"V125.json"
    report.write_text(json.dumps(data),encoding="utf-8")
    return report,frames,root/"V126.json"


class V126FrameDiversityTests(unittest.TestCase):
    def test_five_different_photographs_still_need_human_review(self):
        with tempfile.TemporaryDirectory() as root:
            result=audit(*make_case(root))
            self.assertEqual(result["status"],"V126_VISUALLY_DIVERSE_FRAMES_REVIEW_REQUIRED")
            self.assertFalse(result["five_genuine_camera_shots_approved"])
            self.assertFalse(result["italian_rights_verified"])
            self.assertEqual(result["vidu_calls"],0)

    def test_brightness_shifted_duplicate_blocked(self):
        with tempfile.TemporaryDirectory() as root:
            result=audit(*make_case(root,duplicate=True))
            self.assertEqual(result["status"],"V126_NEAR_DUPLICATE_FRAMES_BLOCKED_FOR_REVIEW")
            self.assertEqual([(p["first"],p["second"]) for p in result["near_duplicate_pairs"]],
                             [("frame_00.png","frame_04.png")])

    def test_low_detail_frame_blocked(self):
        with tempfile.TemporaryDirectory() as root:
            result=audit(*make_case(root,flat=True))
            self.assertEqual(result["status"],"V126_LOW_DETAIL_SOURCE_FRAMES_BLOCKED")
            self.assertEqual(result["low_contrast_frames"][0]["filename"],"frame_03.png")

    def test_tampered_png_is_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            report,frames,out=make_case(root)
            (frames/"frame_02.png").write_bytes(b"fake")
            with self.assertRaisesRegex(ValueError,"BYTES_MISSING_OR_TAMPERED"):
                audit(report,frames,out)

    def test_forged_review_or_duplicate_region_is_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            report,frames,out=make_case(root)
            data=json.loads(report.read_text())
            data["five_genuine_camera_shots_approved"]=True
            report.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,"NOT_IN_REVIEW_STATE"):
                audit(report,frames,out)
            data["five_genuine_camera_shots_approved"]=False
            data["five_review_shots"][4]["timeline_region"]=0
            report.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,"TIME_REGION"):
                audit(report,frames,out)


if __name__=="__main__":
    unittest.main()
