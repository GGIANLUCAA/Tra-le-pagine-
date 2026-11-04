"""No-network NVIDIA Cosmos3 video test adapter regression suite."""
import base64
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SRC=Path(__file__).resolve().parents[1]/"src"
sys.path.insert(0,str(SRC))
from nvidia_cosmos3_video_dev_v1 import URL, CosmosDevError, preview_clip

def dev_env():
    return {"NVIDIA_COSMOS_DEV_ENABLED":"1",
            "NVIDIA_NIM_NONCOMMERCIAL_ACK":"1",
            "NVIDIA_NIM_ZERO_SPEND_CONFIRMED":"1",
            "NVIDIA_API_KEY":"fixture-only-key"}

def fake_mp4():
    return b"\x00\x00\x00\x18ftypisom" + b"\x00"*512

class Reply:
    def __init__(self, body):
        self.body=json.dumps(body).encode()
    def __enter__(self):return self
    def __exit__(self,*a):return None
    def read(self,n):return self.body

def transport(req,timeout):
    assert req.full_url==URL
    assert req.get_header("Authorization")=="Bearer fixture-only-key"
    assert req.method=="POST"
    body=json.loads(req.data)
    assert body["model_mode"]=="text2video"
    assert body["resolution"]=="480_9_16"
    assert body["num_frames"]==25
    assert body["fps"]==24
    assert timeout<=120
    return Reply({"b64_video":base64.b64encode(fake_mp4()).decode()})

class CosmosDevTests(unittest.TestCase):
    def test_disabled_by_default_even_with_key(self):
        e=dev_env();e.pop("NVIDIA_COSMOS_DEV_ENABLED")
        with self.assertRaisesRegex(CosmosDevError,"Disabled"):
            preview_clip("An archival inspired street",environ=e,
                         opener=lambda *_:self.fail("should not connect"))

    def test_terms_zero_spend_and_key_required(self):
        for field in ("NVIDIA_NIM_NONCOMMERCIAL_ACK","NVIDIA_NIM_ZERO_SPEND_CONFIRMED","NVIDIA_API_KEY"):
            e=dev_env();e.pop(field)
            with self.subTest(field=field),self.assertRaises(CosmosDevError):
                preview_clip("Old tram in Paris",environ=e,
                             opener=lambda *_:self.fail("should not connect"))

    def test_text_to_video_unapproved_short_preview(self):
        x=preview_clip("An imaginary streetcar in the early 1900s.",environ=dev_env(),opener=transport)
        self.assertEqual(x["video_bytes"],fake_mp4())
        self.assertFalse(x["metadata"]["source_is_historical_footage"])
        self.assertFalse(x["metadata"]["publication_authorized"])
        self.assertFalse(x["metadata"]["commercial_use_authorized"])
        self.assertTrue(x["metadata"]["watermark_preserved"])
        self.assertLess(x["metadata"]["video_duration_estimate_seconds"],2)

    def test_source_image_mode_only_accepted_types(self):
        with tempfile.TemporaryDirectory() as d:
            file=Path(d)/"reference.png"
            file.write_bytes(b"\x89PNG\r\n\x1a\n"+b"0"*150)
            def image_transport(req,timeout):
                data=json.loads(req.data)
                self.assertEqual(data["model_mode"],"image2video")
                self.assertTrue(data["input_reference"].startswith("data:image/png;base64,"))
                return Reply({"b64_video":base64.b64encode(fake_mp4()).decode()})
            x=preview_clip("A gentle dolly motion",source_image=file,
                           environ=dev_env(),opener=image_transport)
            self.assertEqual(x["metadata"]["mode"],"image2video")
            file.write_text("not an image")
            with self.assertRaises(CosmosDevError):
                preview_clip("A gentle dolly motion",source_image=file,
                             environ=dev_env(),opener=image_transport)

    def test_invalid_base64_is_not_saved(self):
        with self.assertRaisesRegex(CosmosDevError,"base64"):
            preview_clip("Old world scene",environ=dev_env(),
                         opener=lambda req,timeout:Reply({"b64_video":"??notvideo!!"}))

    def test_invalid_payload_is_not_accepted_as_mp4(self):
        with self.assertRaisesRegex(CosmosDevError,"MP4"):
            preview_clip("Old world scene",environ=dev_env(),
                         opener=lambda req,timeout:Reply({"b64_video":base64.b64encode(b"no video"*100).decode()}))

    def test_dry_run_has_no_network_or_file(self):
        with tempfile.TemporaryDirectory() as d:
            prompt=Path(d)/"prompt.txt";prompt.write_text("An old moving street")
            output=Path(d)/"test.mp4"
            p=subprocess.run([sys.executable,str(SRC/"nvidia_cosmos3_video_dev_v1.py"),
                "--prompt-file",str(prompt),"--output",str(output)],
                capture_output=True,text=True,check=True,env=os.environ.copy())
            self.assertIn("DRY_RUN_ONLY",p.stdout)
            self.assertFalse(output.exists())

if __name__=="__main__":
    unittest.main()
