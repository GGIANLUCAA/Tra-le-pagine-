"""V153 safety & actual-byte tests; all tests use synthetic images, no provider."""
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import cv2
import numpy as np
from PIL import Image

from src.storia_rivive_v149_authentic_bw_proxy import sha256_file
from src import storia_rivive_v153_one_free_i2i_cat as v153


def fixture(root, *, with_video=False):
    root=Path(root);root.mkdir(parents=True,exist_ok=True)
    data=np.zeros((1280,720),dtype=np.uint8)
    data[:]=np.linspace(42,230,720,dtype=np.uint8)[None,:]
    cv2.circle(data,(360,640),270,60,-1)
    cv2.rectangle(data,(75,250),(245,525),195,-1)
    bw=Image.fromarray(data,"L").convert("RGB")
    native=root/"native_frames"/"scene_02_NATIVE_FREEZE.png"
    crop=root/"review_crops"/"scene_02_SOURCE_CROP_720x1280.png"
    native.parent.mkdir(parents=True);crop.parent.mkdir(parents=True)
    bw.save(crop)
    bw.resize((1920,1080)).save(native)
    native_sha=sha256_file(native); crop_sha=sha256_file(crop)
    report={
        "version":"V151","real_source_frames_sha_verified":5,
        "candidate_i2i_jobs":4,"real_restored_photos_generated":0,
        "real_vidu_clips_generated":0,"provider_requests_sent":0,"paid_api_calls":0,
        "publish_permitted":False,"rights_italy_verified":False,
        "artistic_approved":False,
        "freeze_frames":[{"scene":k,"source_id":"other",
                          "role":"I2I_PHOTO_CANDIDATE_NOT_GENERATED"}
                          for k in range(1,6)]
    }
    film_sha="d"*64
    row={
        "scene":2,"source_id":v153.SOURCE_ID,
        "role":"I2I_PHOTO_CANDIDATE_NOT_GENERATED",
        "native_original_frame_sha256":native_sha,
        "vertical_review_sha256":crop_sha,"source_film_sha256":film_sha,
        "native_original_frame_pts":21800,"native_time_base":"1/1000",
        "vertical_review_raster":[720,1280],
        "image_to_image_sent":False,"vidu_request_sent":False,
        "source_subject_artistically_reviewed":False,"face_and_object_fidelity_verified":False,
        "rights_italy_verified":False,"provider_credit_budget_approved":False,
        "source_bw_video_sha256":"f"*64
    }
    report["freeze_frames"][1]=row
    (root/"V151_SOURCE_LOCKED_HANDOFF.json").write_text(json.dumps(report))
    (root/"V152_EDITORIAL_PREFLIGHT.json").write_text(json.dumps({
        "status":"V152_EDITORIAL_SOURCE_COHERENCE_BLOCKED",
        "provider_jobs_may_start":False,"rights_italy_verified":False
    }))
    if with_video:
        video=root/"scene_02_V150_BW_LONGER.mp4"
        subprocess.run(["ffmpeg","-nostdin","-y","-hide_banner","-loglevel","error",
                        "-f","lavfi","-i","testsrc2=size=720x1280:rate=30:duration=2.4",
                        "-c:v","libx264","-preset","ultrafast","-pix_fmt","yuv420p",
                        str(video)],check=True,capture_output=True,timeout=75)
        row["source_bw_video_sha256"]=sha256_file(video)
        (root/"V151_SOURCE_LOCKED_HANDOFF.json").write_text(json.dumps(report))
    return native_sha, crop_sha, film_sha


def colorizer(source, base):
    img=cv2.imread(str(source))
    img[:,:,0]=np.clip(img[:,:,0]*.62,0,255)
    img[:,:,1]=np.clip(img[:,:,1]*.78,0,255)
    cv2.imwrite(str(base),img)
    return {"model_sha256":"e"*64}


class V153NoCostSingleRealI2I(unittest.TestCase):
    def test_sha_locked_authentic_frame_and_v152_block_retained(self):
        with tempfile.TemporaryDirectory() as folder:
            shas=fixture(folder)
            with patch.object(v153,"SOURCE_SHA",shas[0]),patch.object(v153,"CROP_SHA",shas[1]),patch.object(v153,"FILM_SHA",shas[2]):
                crop, row=v153.verify_source(Path(folder))
                self.assertEqual(row["scene"],2)
                self.assertTrue(crop.is_file())

    def test_tampered_photo_never_sent_to_model(self):
        with tempfile.TemporaryDirectory() as folder:
            shas=fixture(folder)
            with patch.object(v153,"SOURCE_SHA",shas[0]),patch.object(v153,"CROP_SHA",shas[1]),patch.object(v153,"FILM_SHA",shas[2]):
                crop=Path(folder)/"review_crops/scene_02_SOURCE_CROP_720x1280.png"
                with Image.open(crop) as im: photo=im.copy()
                photo.putpixel((12,12),(12,9,4))
                photo.save(crop)
                with self.assertRaisesRegex(ValueError,"V153_PHOTO_BYTES_NOT_AUTHENTIC"):
                    v153.run(folder,Path(folder)/"out",base_colorizer=colorizer,
                        generator=lambda p:self.fail("Must not send"))

    def test_fake_rights_or_preapproved_production_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            shas=fixture(folder)
            editorial=Path(folder)/"V152_EDITORIAL_PREFLIGHT.json"
            obj=json.loads(editorial.read_text())
            obj["provider_jobs_may_start"]=True
            editorial.write_text(json.dumps(obj))
            with patch.object(v153,"SOURCE_SHA",shas[0]),patch.object(v153,"CROP_SHA",shas[1]),patch.object(v153,"FILM_SHA",shas[2]):
                with self.assertRaisesRegex(ValueError,"V153_V152_EDITORIAL_STATUS_MODIFIED"):
                    v153.verify_source(Path(folder))

    def test_dry_run_never_calls_free_provider(self):
        with tempfile.TemporaryDirectory() as folder:
            shas=fixture(folder)
            with patch.object(v153,"SOURCE_SHA",shas[0]),patch.object(v153,"CROP_SHA",shas[1]),patch.object(v153,"FILM_SHA",shas[2]):
                result=v153.run(folder,Path(folder)/"out",base_colorizer=colorizer,
                    generator=lambda p:self.fail("Provider must remain unused"),
                    allow_one_free_public_request=False)
            self.assertEqual(result["free_provider_requests_sent"],0)
            self.assertFalse(result["real_i2i_generated"])
            self.assertFalse(result["finished_video"])

    def test_provider_failure_is_one_call_no_faked_photo_and_zero_spend(self):
        with tempfile.TemporaryDirectory() as folder:
            shas=fixture(folder)
            calls=[]
            def once(base):
                calls.append(str(base))
                raise RuntimeError("ZeroGPU runs limit")
            with patch.object(v153,"SOURCE_SHA",shas[0]),patch.object(v153,"CROP_SHA",shas[1]),patch.object(v153,"FILM_SHA",shas[2]):
                result=v153.run(folder,Path(folder)/"out",base_colorizer=colorizer,generator=once)
            self.assertEqual(len(calls),1)
            self.assertEqual(result["free_provider_requests_sent"],1)
            self.assertFalse(result["real_i2i_generated"])
            self.assertEqual(result["paid_calls"],0)
            self.assertEqual(result["status"],"V153_ONE_FREE_I2I_CALL_FAILED_OR_QUOTA_REACHED")

    def test_real_color_image_can_be_technical_candidate_without_claiming_human_approval(self):
        with tempfile.TemporaryDirectory() as folder:
            shas=fixture(folder,with_video=True)
            def generator(base):
                return base
            with patch.object(v153,"SOURCE_SHA",shas[0]),patch.object(v153,"CROP_SHA",shas[1]),patch.object(v153,"FILM_SHA",shas[2]):
                result=v153.run(folder,Path(folder)/"out",base_colorizer=colorizer,generator=generator)
            self.assertTrue(result["real_i2i_generated"])  # synthetic mock of a model output only in this test
            self.assertTrue(result["technical_candidate_pass"])
            self.assertFalse(result["artistically_approved"])
            self.assertFalse(result["finished_video"])
            self.assertEqual(result["free_provider_requests_sent"],1)
            self.assertEqual(result["paid_calls"],0)
            self.assertIn("technical_video_preview_sha256",result)
            self.assertGreater((Path(folder)/"out"/"SCENE02_BW_FREEZE_REAL_I2I_REVIEW_ONLY.mp4").stat().st_size,8000)

    def test_grayscale_output_rejected_and_not_called_real_restoration(self):
        with tempfile.TemporaryDirectory() as folder:
            shas=fixture(folder)
            src=Path(folder)/"review_crops/scene_02_SOURCE_CROP_720x1280.png"
            with patch.object(v153,"SOURCE_SHA",shas[0]),patch.object(v153,"CROP_SHA",shas[1]),patch.object(v153,"FILM_SHA",shas[2]):
                result=v153.run(folder,Path(folder)/"out",base_colorizer=colorizer,generator=lambda _:src)
            self.assertTrue(result["real_i2i_generated"])  # mock returned image, but color gate must REJECT
            self.assertFalse(result["technical_candidate_pass"])
            self.assertEqual(result["status"],"V153_REAL_I2I_GENERATED_BUT_TECHNICAL_REJECT")
            self.assertNotIn("technical_video_preview_sha256",result)

    def test_missing_ddcolor_base_blocks_without_any_provider_call(self):
        with tempfile.TemporaryDirectory() as folder:
            shas=fixture(folder)
            with patch.object(v153,"SOURCE_SHA",shas[0]),patch.object(v153,"CROP_SHA",shas[1]),patch.object(v153,"FILM_SHA",shas[2]):
                result=v153.run(folder,Path(folder)/"out",base_colorizer=lambda *_:1,
                    generator=lambda _:self.fail("No base, no request"))
            self.assertEqual(result["status"],"V153_FREE_BASE_MODEL_OR_COLOR_PREP_UNAVAILABLE")
            self.assertEqual(result["free_provider_requests_sent"],0)


if __name__ == "__main__":
    unittest.main()
