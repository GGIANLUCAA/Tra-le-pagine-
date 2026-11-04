"""Offline safety tests: NVIDIA NIM developer-only text connector."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SRC=Path(__file__).resolve().parents[1]/"src"
sys.path.insert(0,str(SRC))
from nvidia_nim_dev_v1 import API_URL, NvidiaNimError, generate_dev_draft

MODEL="nvidia/llama-3.3-nemotron-super-49b-v1.5"

def env():
    return {"NVIDIA_API_KEY":"fixture-only-key",
            "NVIDIA_NIM_DEV_ENABLED":"1",
            "NVIDIA_NIM_NONCOMMERCIAL_ACK":"1",
            "NVIDIA_NIM_ZERO_SPEND_CONFIRMED":"1",
            "NVIDIA_NIM_MODEL":MODEL}

class Reply:
    def __init__(self, content="Useful museum narration draft.", model=MODEL):
        self.raw=json.dumps({"model":model,
            "choices":[{"message":{"content":content}}]}).encode()
    def __enter__(self):return self
    def __exit__(self,*unused):return None
    def read(self,n):return self.raw

def fake_transport(req,timeout):
    assert req.full_url==API_URL
    assert req.method=="POST"
    assert req.get_header("Authorization")=="Bearer fixture-only-key"
    assert timeout<=30
    payload=json.loads(req.data)
    assert payload["model"]==MODEL
    assert payload["max_tokens"]<=512
    assert payload["stream"] is False
    return Reply()

class NvidiaNimDevTests(unittest.TestCase):
    def test_enabled_flag_required(self):
        e=env();e["NVIDIA_NIM_DEV_ENABLED"]="0"
        with self.assertRaisesRegex(NvidiaNimError,"Disabled"):
            generate_dev_draft("social","Source note",environ=e,
                               opener=lambda *_:self.fail("HTTP unexpected"))

    def test_terms_and_cost_attestations_required(self):
        for flag in ("NVIDIA_NIM_NONCOMMERCIAL_ACK","NVIDIA_NIM_ZERO_SPEND_CONFIRMED"):
            e=env();e.pop(flag)
            with self.subTest(flag=flag),self.assertRaises(NvidiaNimError):
                generate_dev_draft("social","Source note",environ=e,
                                   opener=lambda *_:self.fail("HTTP unexpected"))

    def test_missing_key_and_bad_model_rejected_without_network(self):
        e=env();e.pop("NVIDIA_API_KEY")
        with self.assertRaisesRegex(NvidiaNimError,"NVIDIA_API_KEY"):
            generate_dev_draft("storyboard","Source note",environ=e,
                               opener=lambda *_:self.fail("HTTP unexpected"))
        for model in ("auto","","nvidia/","http://evil.test/api","nvidia/x\nunsafe"):
            e=env();e["NVIDIA_NIM_MODEL"]=model
            with self.subTest(model=model),self.assertRaisesRegex(NvidiaNimError,"model"):
                generate_dev_draft("storyboard","Source note",environ=e,
                                   opener=lambda *_:self.fail("HTTP unexpected"))

    def test_no_video_render_task(self):
        with self.assertRaisesRegex(NvidiaNimError,"task"):
            generate_dev_draft("render_mp4","Source note",environ=env(),
                               opener=lambda *_:self.fail("HTTP unexpected"))

    def test_drafts_are_not_certified_or_published(self):
        for task in ("social","storyboard","narration","source_notes","qa_second_opinion"):
            with self.subTest(task=task):
                result=generate_dev_draft(task,"Museum source",environ=env(),
                                          opener=fake_transport)
                self.assertEqual(result["status"],"draft_unreviewed")
                for key in ("publication_authorized","commercial_use_authorized",
                            "rights_verified","artistic_approval","video_generated",
                            "cost_guaranteed"):
                    self.assertFalse(result[key])
                self.assertNotIn("fixture-only-key",repr(result))

    def test_public_branding_guard(self):
        with self.assertRaisesRegex(NvidiaNimError,"V134"):
            generate_dev_draft("social","Museum source",environ=env(),
                               opener=lambda *args, **kwargs:Reply(content="ArtVision presents the film"))

    def test_provider_mismatch_rejected(self):
        with self.assertRaisesRegex(NvidiaNimError,"Unexpected returned model"):
            generate_dev_draft("social","Museum note",environ=env(),
                               opener=lambda *args, **kwargs:Reply(model="other/model"))

    def test_dry_run_no_api_key_and_no_file_created(self):
        with tempfile.TemporaryDirectory() as d:
            input_path=Path(d)/"prompt.txt"
            output_path=Path(d)/"result.json"
            input_path.write_text("Historical footage")
            res=subprocess.run([sys.executable,str(SRC/"nvidia_nim_dev_v1.py"),
                "--task","social","--prompt-file",str(input_path),
                "--output",str(output_path)],capture_output=True,text=True,
                env={**os.environ,"NVIDIA_NIM_DEV_ENABLED":"0"},check=True)
            self.assertIn("DRY_RUN_ONLY",res.stdout)
            self.assertFalse(output_path.exists())

if __name__=="__main__":
    unittest.main()
