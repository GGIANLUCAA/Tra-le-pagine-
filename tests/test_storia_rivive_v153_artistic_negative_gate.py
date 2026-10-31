"""Known-bad I2I QA must override numerical technical PASS on actual files."""
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from src.storia_rivive_v149_authentic_bw_proxy import sha256_file
from src.storia_rivive_v153_artistic_negative_gate import audit,REJECT,REVIEW


def fake_bytes(root):
    root=Path(root)
    photo=root/"SCENE02_FREE_I2I_CANDIDATE.png"
    Image.new("RGB",(720,1280),(29,76,116)).save(photo)
    movie=root/"SCENE02_BW_FREEZE_REAL_I2I_REVIEW_ONLY.mp4"
    subprocess.run([
        "ffmpeg","-nostdin","-y","-hide_banner","-loglevel","error",
        "-f","lavfi","-i","testsrc2=size=720x1280:rate=30:duration=4.567",
        "-an","-c:v","libx264","-preset","ultrafast","-pix_fmt","yuv420p",
        str(movie)],check=True,capture_output=True,timeout=60)
    psha=sha256_file(photo)
    msha=sha256_file(movie)
    data={
        "version":"V153","scene":2,"source_id":"girl_cat_1900",
        "source_frame_sha256":"37da59961c75fddea7609ab2d29302f0171dd2c45f9e823ebc8059b7ab810534",
        "source_crop_sha256":"209320b0bcf9b734e28f5160542c6d99a4043dedf09d0ed36e84833d4a367b25",
        "real_i2i_generated":True,"technical_candidate_pass":True,
        "free_provider_requests_sent":1,
        "paid_calls":0,"vidu_calls":0,"finished_video":False,
        "rights_italy_verified":False,"artistically_approved":False,
        "i2i_candidate_sha256":psha,"technical_video_preview_sha256":msha
    }
    (root/"V153_EXPERIMENT_REPORT.json").write_text(json.dumps(data))
    registry=root/"rejects.json"
    registry.write_text(json.dumps({
        "version":"V153_KNOWN_I2I_ARTISTIC_REJECTS_V1",
        "not_a_user_approval":True,"production_rights_italy_verified":False,
        "entries":[{"scene":2,"source_id":"girl_cat_1900",
                    "source_frame_sha256":data["source_frame_sha256"],
                    "source_crop_sha256":data["source_crop_sha256"],
                    "ai_photo_sha256":psha,
                    "inspection":"ASSISTANT_VISUAL_REVIEW_REJECT_NOT_HUMAN_APPROVAL",
                    "pilot_reuse_permitted":False,"serial_production_permitted":False,
                    "social_or_site_publication_permitted":False,
                    "reasons":["unsupported human face"]}]
    }))
    return registry,photo,movie


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"),"FFmpeg required")
class KnownBadHumanAnimalVisualQA(unittest.TestCase):
    def test_known_rejected_sha_overrides_numeric_qa(self):
        with tempfile.TemporaryDirectory() as d:
            registry,photo,movie=fake_bytes(d)
            report=audit(d,registry)
            self.assertEqual(report["status"],REJECT)
            self.assertFalse(report["master_eligible"])
            self.assertFalse(report["candidate_allowed_as_reused_i2i"])
            self.assertFalse(report["human_artistic_approval"])
            self.assertFalse(report["rights_italy_verified"])
            self.assertEqual(report["credits_spent_during_this_QA"],0)
            self.assertEqual(report["visual_inspection_reasons"],["unsupported human face"])

    def test_different_new_sha_is_not_implicitly_approved(self):
        with tempfile.TemporaryDirectory() as d:
            registry,_,_=fake_bytes(d)
            r=json.loads(registry.read_text())
            r["entries"][0]["ai_photo_sha256"]="0"*64
            registry.write_text(json.dumps(r))
            result=audit(d,registry)
            self.assertEqual(result["status"],REVIEW)
            self.assertFalse(result["master_eligible"])

    def test_tampered_image_pixels_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            registry,photo,_=fake_bytes(d)
            Image.new("RGB",(720,1280),(55,88,92)).save(photo)
            with self.assertRaisesRegex(ValueError,"V153_REAL_PHOTO_OR_MP4_BYTES_SHA"):
                audit(d,registry)

    def test_tampered_mp4_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            registry,_,movie=fake_bytes(d)
            movie.write_bytes(movie.read_bytes()+b"change")
            with self.assertRaisesRegex(ValueError,"V153_REAL_PHOTO_OR_MP4_BYTES_SHA"):
                audit(d,registry)

    def test_fake_human_approval_never_passes(self):
        with tempfile.TemporaryDirectory() as d:
            registry,_,_=fake_bytes(d)
            report=Path(d)/"V153_EXPERIMENT_REPORT.json"
            r=json.loads(report.read_text());r["artistically_approved"]=True
            report.write_text(json.dumps(r))
            with self.assertRaisesRegex(ValueError,"V153_PREVIOUS_TECHNICAL_ARTIFACT_INVALID"):
                audit(d,registry)

    def test_registry_wrong_claim_prevents_QA(self):
        with tempfile.TemporaryDirectory() as d:
            registry,_,_=fake_bytes(d)
            r=json.loads(registry.read_text())
            r["production_rights_italy_verified"]=True
            registry.write_text(json.dumps(r))
            with self.assertRaisesRegex(ValueError,"V153_KNOWN_BAD_REGISTRY_NOT_AUTHENTIC"):
                audit(d,registry)


if __name__=="__main__":
    unittest.main()
