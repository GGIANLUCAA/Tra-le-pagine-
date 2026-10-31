"""Offline V154 provenance and no-fake-master tests; all files are synthetic."""
import hashlib
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

from src.storia_rivive_v154_i2i_four_asset_gate import audit


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def striped(path, size, scene, tinted=False):
    image = Image.new("RGB", size)
    draw = ImageDraw.Draw(image)
    for y in range(0, size[1], 64):
        level = (45 if (y // 64) % 2 == 0 else 175) + scene
        fill = (level + 8, level + 20, level + 30) if tinted else (level,) * 3
        draw.rectangle((0, y, size[0] - 1, min(y + 63, size[1] - 1)), fill=fill)
    if tinted:
        # New local texture not present in the source; a global tint alone
        # must NOT pass the V156 detail-change rejection test.
        for y in range(0, size[1], 16):
            if (y // 16) % 2 == 0:
                level = (45 if (y // 64) % 2 == 0 else 175) + scene
                draw.rectangle((0, y, size[0] - 1, min(y + 7, size[1] - 1)),
                               fill=(level + 24, level + 35, level + 45))
    image.save(path)


def fixture(root):
    root = Path(root)
    rows, jobs = [], []
    for scene in range(1, 6):
        original = root / f"original_{scene}.png"
        crop = root / f"crop_{scene}.png"
        striped(original, (1280, 720), scene)
        striped(crop, (720, 1280), scene)
        rows.append({"scene": scene, "role": "I2I_PHOTO_CANDIDATE_NOT_GENERATED" if scene < 5 else "VIDU_ANCHOR_NOT_SUBMITTED",
                     "source_id": f"source_{scene}", "native_raster": [1280, 720],
                     "native_original_frame_file": original.name, "native_original_frame_sha256": sha(original),
                     "vertical_review_file": crop.name, "vertical_review_sha256": sha(crop),
                     "image_to_image_sent": False, "vidu_request_sent": False,
                     "source_subject_artistically_reviewed": False,
                     "face_and_object_fidelity_verified": False, "rights_italy_verified": False})
        if scene < 5:
            output = root / f"ai_{scene}.png"
            striped(output, (720, 1280), scene, tinted=True)
            jobs.append({"scene": scene, "source_id": f"source_{scene}",
                         "source_frame_sha256": sha(original), "source_crop_sha256": sha(crop),
                         "source_crop_file": crop.name, "restored_photo_file": output.name,
                         "restored_photo_sha256": sha(output), "method": "generative_image_to_image",
                         "model": "test-model", "provider_request_reference": f"fixture-{scene}",
                         "human_visual_review": "pending", "rights_italy_verified": False,
                         "artistically_approved": False})
    handoff = {"version": "V151", "real_source_frames_sha_verified": 5, "candidate_i2i_jobs": 4,
               "vidu_frame_anchors": 1, "real_restored_photos_generated": 0,
               "real_vidu_clips_generated": 0, "provider_requests_sent": 0, "paid_api_calls": 0,
               "rights_italy_verified": False, "artistic_approved": False, "publish_permitted": False,
               "editorial_preflight": {"version": "V152", "status": "V152_EDITORIAL_SOURCE_COHERENCE_BLOCKED",
                                       "provider_jobs_may_start": False, "rights_italy_verified": False},
               "freeze_frames": rows}
    candidates = {"version": "V154", "source_handoff_version": "V151",
                  "rights_italy_verified": False, "human_artistic_approval": False,
                  "publish_permitted": False, "jobs": jobs}
    registry = {"version": "V153_KNOWN_I2I_ARTISTIC_REJECTS_V1",
                "not_a_user_approval": True, "production_rights_italy_verified": False,
                "entries": []}
    return handoff, candidates, registry


class FourI2IByteGate(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.h, self.c, self.n = fixture(self.root)

    def check(self):
        return audit(self.h, self.c, self.root, self.n)

    def test_four_byte_verified_still_not_master_or_approved(self):
        report = self.check()
        self.assertEqual(report["real_i2i_photo_files_sha_verified"], 4)
        self.assertEqual(report["status"], "V154_SOURCE_EDITORIAL_BLOCKED")
        self.assertFalse(report["master_eligible"])
        self.assertFalse(report["model_invocation_independently_verified"])
        self.assertFalse(report["publish_permitted"])

    def test_missing_fourth_is_pending_not_fake_four(self):
        self.c["jobs"].pop()
        report = self.check()
        self.assertEqual(report["missing_i2i_scenes"], [4])
        self.assertEqual(report["real_i2i_photo_files_sha_verified"], 3)

    def test_source_frame_mismatch(self):
        self.c["jobs"][0]["source_frame_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "SOURCE_FRAME_MISMATCH"):
            self.check()

    def test_tampered_photo_bytes(self):
        Image.new("RGB", (720, 1280), (1, 2, 3)).save(self.root / "ai_1.png")
        with self.assertRaisesRegex(ValueError, "IMAGE_BYTES_SHA_MISMATCH"):
            self.check()

    def test_known_bad_sha_rejected_even_under_new_scene(self):
        self.n["entries"] = [{"ai_photo_sha256": self.c["jobs"][0]["restored_photo_sha256"],
                              "pilot_reuse_permitted": False, "serial_production_permitted": False,
                              "social_or_site_publication_permitted": False}]
        with self.assertRaisesRegex(ValueError, "KNOWN_ARTISTICALLY_REJECTED"):
            self.check()

    def test_ddcolor_only_cannot_be_declared_i2i(self):
        self.c["jobs"][0]["model"] = "DDColor"
        with self.assertRaisesRegex(ValueError, "METHOD_OR_REVIEW_PROVENANCE"):
            self.check()

    def test_duplicate_photo_rejected(self):
        self.c["jobs"][1]["restored_photo_file"] = self.c["jobs"][0]["restored_photo_file"]
        self.c["jobs"][1]["restored_photo_sha256"] = self.c["jobs"][0]["restored_photo_sha256"]
        with self.assertRaisesRegex(ValueError, "DUPLICATE_RESTORED"):
            self.check()

    def test_false_rights_or_approval_rejected(self):
        self.c["human_artistic_approval"] = True
        with self.assertRaisesRegex(ValueError, "CLAIMS_UNVERIFIED_APPROVAL"):
            self.check()

    def test_missing_real_output_rejected(self):
        (self.root / "ai_3.png").unlink()
        with self.assertRaisesRegex(ValueError, "MISSING_OR_UNSAFE"):
            self.check()

    def test_unchanged_source_rejected_even_with_new_file(self):
        crop = self.root / "crop_1.png"
        output = self.root / "ai_1.png"
        output.write_bytes(crop.read_bytes())
        self.c["jobs"][0]["restored_photo_sha256"] = sha(output)
        with self.assertRaisesRegex(ValueError, "UNCHANGED_SOURCE"):
            self.check()

    def test_no_editorial_preflight_no_pass(self):
        self.h["editorial_preflight"].pop("provider_jobs_may_start")
        with self.assertRaisesRegex(ValueError, "EDITORIAL_PREFLIGHT"):
            self.check()

    def test_uniform_color_fake_rejected_even_with_correct_sha(self):
        output = self.root / "ai_1.png"
        Image.new("RGB", (720, 1280), (80, 130, 180)).save(output)
        self.c["jobs"][0]["restored_photo_sha256"] = sha(output)
        with self.assertRaisesRegex(ValueError, "LOW_DETAIL_OR_FLAT_OUTPUT"):
            self.check()

    def test_unrelated_colored_image_rejected_even_with_correct_sha(self):
        output = self.root / "ai_1.png"
        with Image.open(output) as image:
            ImageOps.invert(image.convert("RGB")).save(output)
        self.c["jobs"][0]["restored_photo_sha256"] = sha(output)
        with self.assertRaisesRegex(ValueError, "SOURCE_STRUCTURE_MISMATCH"):
            self.check()

    def test_low_detail_source_cannot_claim_faithful_restoration(self):
        crop = self.root / "crop_1.png"
        Image.new("RGB", (720, 1280), (90, 90, 90)).save(crop)
        self.h["freeze_frames"][0]["vertical_review_sha256"] = sha(crop)
        self.c["jobs"][0]["source_crop_sha256"] = sha(crop)
        with self.assertRaisesRegex(ValueError, "LOW_DETAIL_SOURCE_NEEDS_REVIEW"):
            self.check()

    def test_v156_color_tint_only_rejected_with_valid_sha(self):
        crop = self.root / "crop_1.png"
        output = self.root / "ai_1.png"
        with Image.open(crop) as image:
            gray = image.convert("L")
            Image.merge("RGB", (gray.point(lambda x: x + 8),
                                gray.point(lambda x: x + 20),
                                gray.point(lambda x: x + 30))).save(output)
        self.c["jobs"][0]["restored_photo_sha256"] = sha(output)
        with self.assertRaisesRegex(ValueError, "V156_COLOR_TINT_OR_AFFINE_LUMA_ONLY"):
            self.check()

    def test_v156_global_contrast_change_is_not_i2i_detail(self):
        crop = self.root / "crop_1.png"
        output = self.root / "ai_1.png"
        with Image.open(crop) as image:
            gray = image.convert("L")
            Image.merge("RGB", (gray.point(lambda x: int(x * 1.1) + 3),
                                gray.point(lambda x: int(x * 1.1) + 12),
                                gray.point(lambda x: int(x * 1.1) + 20))).save(output)
        self.c["jobs"][0]["restored_photo_sha256"] = sha(output)
        with self.assertRaisesRegex(ValueError, "V156_COLOR_TINT_OR_AFFINE_LUMA_ONLY"):
            self.check()

    def test_v156_new_texture_measured_but_not_claimed_as_real_i2i(self):
        report = self.check()
        self.assertGreaterEqual(report["verified_byte_evidence"][0]["source_luminance_residual_rms"], 4.0)
        self.assertFalse(report["model_invocation_independently_verified"])
        self.assertFalse(report["master_eligible"])

    def test_v157_duplicate_native_frame_bytes_cannot_claim_five_sources(self):
        target = self.root / "original_2.png"
        target.write_bytes((self.root / "original_1.png").read_bytes())
        self.h["freeze_frames"][1]["native_original_frame_sha256"] = sha(target)
        with self.assertRaisesRegex(ValueError, "V157_DUPLICATE_FIVE_SCENE_SOURCE_NATIVE_ORIGINAL_FRAME_SHA256"):
            self.check()

    def test_v157_duplicate_vertical_crop_bytes_rejected(self):
        target = self.root / "crop_2.png"
        target.write_bytes((self.root / "crop_1.png").read_bytes())
        self.h["freeze_frames"][1]["vertical_review_sha256"] = sha(target)
        with self.assertRaisesRegex(ValueError, "V157_DUPLICATE_FIVE_SCENE_SOURCE_VERTICAL_REVIEW_SHA256"):
            self.check()

    def test_v157_duplicate_source_id_rejected(self):
        self.h["freeze_frames"][1]["source_id"] = self.h["freeze_frames"][0]["source_id"]
        with self.assertRaisesRegex(ValueError, "V157_DUPLICATE_FIVE_SCENE_SOURCE_SOURCE_ID"):
            self.check()

    def test_v157_transparent_png_cannot_be_passed_as_photo(self):
        output = self.root / "ai_1.png"
        with Image.open(output) as image:
            rgba = image.convert("RGBA")
            rgba.putalpha(0)
            rgba.save(output)
        self.c["jobs"][0]["restored_photo_sha256"] = sha(output)
        with self.assertRaisesRegex(ValueError, "V157_TRANSPARENT_RESTORATION_NOT_VISIBLE"):
            self.check()

    def test_v157_opaque_rgba_remains_valid_for_review_only(self):
        output = self.root / "ai_1.png"
        with Image.open(output) as image:
            image.convert("RGBA").save(output)
        self.c["jobs"][0]["restored_photo_sha256"] = sha(output)
        report = self.check()
        self.assertTrue(report["five_source_frame_byte_distinctness_verified"])
        self.assertFalse(report["five_shot_coherence_verified"])
        self.assertFalse(report["master_eligible"])

    def test_output_path_traversal_rejected(self):
        self.c["jobs"][0]["restored_photo_file"] = "../outside.png"
        with self.assertRaisesRegex(ValueError, "UNSAFE_ASSET_PATH"):
            self.check()


if __name__ == "__main__":
    unittest.main()
