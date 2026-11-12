import hashlib
import tempfile
import unittest
from pathlib import Path
from src.storia_photo_quality_evidence_gate_v1 import evaluate

class GateTests(unittest.TestCase):
    def test_empty_blocks(self):
        with tempfile.TemporaryDirectory() as t:
            result=evaluate({"scenes":[]},Path(t))
            self.assertIn("NO_SCENES",result["errors"])
    def test_ddcolor_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            result=evaluate({"scenes":[{"reconstruction_method":"ddcolor"}]},Path(t))
            self.assertIn("SCENE_1_NOT_GENERATIVE_I2I",result["errors"])
    def test_valid_evidence_not_artistic_guarantee(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            (root/"source.png").write_bytes(b"a"*1200)
            (root/"generated.png").write_bytes(b"b"*1200)
            def digest(p): return hashlib.sha256((root/p).read_bytes()).hexdigest()
            scene={"reconstruction_method":"generative_image_to_image","provider":"test",
                   "model":"test-model","original_timecode_s":1.2,
                   "original_frame":"source.png","original_frame_sha256":digest("source.png"),
                   "generated_photo":"generated.png","generated_photo_sha256":digest("generated.png"),
                   "human_scene_fidelity_review":True,"human_benchmark_visual_review":True}
            result=evaluate({"scenes":[scene]},root)
            self.assertEqual(result["status"],"FINAL_APPROVAL_EVIDENCE_PASS")
            self.assertFalse(result["artistic_quality_guaranteed"])
            scene["human_benchmark_visual_review"]=False
            self.assertIn("SCENE_1_BENCHMARK_VISUAL_REVIEW_PENDING",evaluate({"scenes":[scene]},root)["errors"])
if __name__=="__main__": unittest.main()
