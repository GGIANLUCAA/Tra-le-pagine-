"""V151 tests: five real PNG bytes, provenance, no fake approval or API spending."""
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from src.storia_rivive_v149_authentic_bw_proxy import sha256_file
from src.storia_rivive_v151_source_locked_handoff import (
    OUTPUT_STATUS, prepare, read_verified_inputs,
)

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = json.loads(
    (ROOT / "config/storia_rivive_v149_five_original_motion_preview.json").read_text(encoding="utf-8")
)


def fixture(root):
    """All pixels are artificial ONLY for tests. The real workflow supplies native archive PNGs."""
    root = Path(root)
    data = copy.deepcopy(ORIGINAL)
    artifacts = root / "batches"
    artifacts.mkdir()
    rows_by_batch = {"a": [], "b": []}
    for shot in data["sources"]:
        batch = artifacts / shot["batch"]
        native = batch / "originals" / shot["id"] / "EXACT_FREEZE.png"
        native.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (1920, 1080), (25 * shot["scene"], 30, 60)).save(native)
        source_hash = sha256_file(native)
        shot["frame_sha256"] = source_hash
        preview = batch / "preview" / f"scene_{shot['scene']:02d}_V150_BW_LONGER.mp4"
        preview.parent.mkdir(parents=True, exist_ok=True)
        preview.write_bytes(b"SYNTHETIC_TEST_CLIP_ONLY_" + str(shot["scene"]).encode())
        rows_by_batch[shot["batch"]].append({
            "scene": shot["scene"], "status": "V150_LONGER_AUTHENTIC_BW_REVIEW_ONLY",
            "id": shot["id"], "source_page": shot["source_page"],
            "original_sha256": shot["original_sha256"],
            "freeze_frame_sha256": source_hash,
            "start_pts": shot["start_pts"] - 1050,
            "freeze_pts": shot["freeze_pts"], "time_base": "1/1000",
            "clip_filename": preview.name, "clip_sha256": sha256_file(preview),
            "seconds": 2.4, "artistic_approved": False,
            "rights_italy_verified": False, "paid_api_calls": 0
        })
    for batch, rows in rows_by_batch.items():
        (artifacts / batch / "V150_BATCH_REPORT.json").write_text(json.dumps({
            "batch": batch, "status": "V150_EXTENDED_BW_SOURCE_BATCH_READY",
            "paid_api_calls": 0, "is_finished_video": False,
            "publish_permitted": False, "artistic_approved": False,
            "rights_italy_verified": False, "real_i2i_generated": 0,
            "real_vidu_generated": 0, "sources": rows
        }))
    manifest = root / "manifest.json"
    manifest.write_text(json.dumps(data))
    return manifest, artifacts


class V151NativeFrameHandoff(unittest.TestCase):
    def test_five_native_pngs_packaged_with_sha_and_no_ai_claims(self):
        with tempfile.TemporaryDirectory() as d:
            manifest, artifacts = fixture(d)
            out = Path(d) / "prepared"
            report = prepare(manifest, artifacts, out)
            self.assertEqual(report["status"], OUTPUT_STATUS)
            self.assertEqual(report["real_source_frames_sha_verified"], 5)
            self.assertEqual([x["role"] for x in report["freeze_frames"]],
                ["I2I_PHOTO_CANDIDATE_NOT_GENERATED"]*4 + ["VIDU_ANCHOR_NOT_SUBMITTED"])
            self.assertEqual(len(list((out/"native_frames").glob("*.png"))),5)
            self.assertEqual(len(list((out/"review_crops").glob("*.png"))),5)
            self.assertTrue((out/"V151_FIVE_ORIGINAL_FRAMES_VISUAL_REVIEW.jpg").is_file())
            self.assertEqual(report["real_restored_photos_generated"], 0)
            self.assertEqual(report["real_vidu_clips_generated"], 0)
            self.assertEqual(report["provider_requests_sent"], 0)
            self.assertEqual(report["paid_api_calls"], 0)
            self.assertFalse(report["artistic_approved"])
            self.assertFalse(report["rights_italy_verified"])
            self.assertFalse(report["publish_permitted"])
            self.assertFalse(report["source_subjects_are_a_coherent_single_episode_verified"])
            for row in report["freeze_frames"]:
                self.assertEqual(row["native_original_frame_sha256"],
                                 sha256_file(out/row["native_original_frame_file"]))
                self.assertEqual(row["vertical_review_sha256"],
                                 sha256_file(out/row["vertical_review_file"]))
                self.assertEqual(row["vertical_review_raster"],[720,1280])
                self.assertFalse(row["provider_credit_budget_approved"])

    def test_one_pixel_changed_blocks_native_sha(self):
        with tempfile.TemporaryDirectory() as d:
            manifest, artifacts = fixture(d)
            shot = json.loads(manifest.read_text())["sources"][0]
            native = artifacts/"a"/"originals"/shot["id"]/"EXACT_FREEZE.png"
            with Image.open(native) as image:
                img = image.copy()
            img.putpixel((10,10),(99,99,99))
            img.save(native)
            with self.assertRaisesRegex(ValueError,"V151_EXACT_NATIVE_PNG_BYTES_SHA_MISMATCH"):
                read_verified_inputs(manifest, artifacts)

    def test_wrong_clip_bytes_blocks_even_if_report_claims_ready(self):
        with tempfile.TemporaryDirectory() as d:
            manifest, artifacts = fixture(d)
            clip = artifacts/"b"/"preview"/"scene_05_V150_BW_LONGER.mp4"
            clip.write_bytes(clip.read_bytes()+b"tampered")
            with self.assertRaisesRegex(ValueError,"V151_REAL_MP4_BYTES_SHA_MISMATCH"):
                read_verified_inputs(manifest,artifacts)

    def test_missing_frame_png_blocks_not_fake_restoration(self):
        with tempfile.TemporaryDirectory() as d:
            manifest, artifacts = fixture(d)
            shot=json.loads(manifest.read_text())["sources"][3]
            (artifacts/"b"/"originals"/shot["id"]/"EXACT_FREEZE.png").unlink()
            with self.assertRaisesRegex(ValueError,"V151_MISSING_REAL_CLIP_OR_EXACT_NATIVE_PNG"):
                read_verified_inputs(manifest,artifacts)

    def test_fake_rights_or_spending_report_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            manifest, artifacts=fixture(d)
            path=artifacts/"a"/"V150_BATCH_REPORT.json"
            data=json.loads(path.read_text())
            data["rights_italy_verified"]=True
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,"V151_UNVERIFIED_OR_DUPLICATE_SOURCE_BATCH"):
                read_verified_inputs(manifest,artifacts)

    def test_changed_pts_and_frame_role_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            manifest, artifacts=fixture(d)
            path=artifacts/"a"/"V150_BATCH_REPORT.json"
            data=json.loads(path.read_text())
            data["sources"][0]["freeze_pts"]+=100
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,"V151_FRAME_MOVIE_SOURCE_PTS_ROLE_MISMATCH"):
                read_verified_inputs(manifest,artifacts)

    def test_all_five_film_sources_must_remain_unique(self):
        with tempfile.TemporaryDirectory() as d:
            manifest, artifacts=fixture(d)
            data=json.loads(manifest.read_text())
            data["sources"][1]["original_sha256"]=data["sources"][0]["original_sha256"]
            manifest.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,"V149_"):
                read_verified_inputs(manifest,artifacts)


if __name__=="__main__":
    unittest.main()
