"""V46 offline integration regressions. Never connects to Vidu or spends credits."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))
import vidu_scene_integration_v46 as v46


class RealViduMontageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.master = self.root/"original.mp4"
        self.clip = self.root/"clip.mp4"
        def run(args):
            subprocess.run(["ffmpeg", "-v", "error", "-y", *args],
                           check=True, capture_output=True, timeout=60)
        run(["-f", "lavfi", "-i", "color=c=red:s=192x320:r=24:d=6",
             "-f", "lavfi", "-i", "sine=frequency=440:duration=6:sample_rate=44100",
             "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p",
             "-c:a", "aac", str(self.master)])
        run(["-f", "lavfi", "-i", "color=c=blue:s=192x320:r=24:d=2",
             "-c:v", "libx264", "-pix_fmt", "yuv420p", str(self.clip)])
        self.plan = self.root/"I2V_PLAN.json"
        self.task = self.root/"VIDU_TASK.json"
        self.out = self.root/"CANDIDATO_DA_REVISIONARE.mp4"
        self.plan.write_text(json.dumps({
            "version": "v42", "provider": "vidu", "duration": 2,
            "fingerprint": "a"*64, "image_sha256": "b"*64
        }))
        self.task.write_text(json.dumps({
            "status": "success", "task_id": "mock-task-not-real",
            "fingerprint": "a"*64,
            "download_sha256": v46.digest(self.clip)
        }))

    def test_reject_local_warp_without_vidu_receipt(self):
        state=json.loads(self.task.read_text())
        state["status"]="none"
        self.task.write_text(json.dumps(state))
        with self.assertRaisesRegex(ValueError,"ricevuta Vidu"):
            v46.validate(self.master,self.clip,self.plan,self.task,2.0,2)

    def test_reject_changed_video_bytes(self):
        state=json.loads(self.task.read_text())
        state["download_sha256"]="c"*64
        self.task.write_text(json.dumps(state))
        with self.assertRaisesRegex(ValueError,"ricevuta Vidu"):
            v46.validate(self.master,self.clip,self.plan,self.task,2.0,2)

    def test_reject_bad_duration_or_scene(self):
        with self.assertRaises(ValueError):
            v46.validate(self.master,self.clip,self.plan,self.task,2.0,5)
        with self.assertRaises(ValueError):
            v46.validate(self.master,self.clip,self.plan,self.task,5.9,2)

    def test_true_montage_preserves_original_audio_and_never_self_approves(self):
        result=v46.integrate(self.master,self.clip,self.plan,self.task,
                             2.0,2,self.out)
        self.assertEqual(result["status"],"rendered_needs_review")
        self.assertTrue(result["no_new_vidu_generation"])
        self.assertTrue(self.out.exists())
        self.assertTrue(v46.probe(self.out)["audio"])
        self.assertLess(abs(v46.probe(self.out)["duration"]-6),.25)
        reviewed=json.loads(self.out.with_suffix(".REVISIONE_V44.json").read_text())
        self.assertEqual(reviewed["provenance"]["kind"],"provider_i2v")
        self.assertFalse(any(v["passed"] for v in reviewed["reviews"].values()))
        self.assertEqual(reviewed["scene"]["time_start_seconds"],2.0)
        with self.assertRaisesRegex(ValueError,"Non sovrascrivere"):
            v46.integrate(self.master,self.clip,self.plan,self.task,
                         2.0,2,self.out)


if __name__=="__main__":
    unittest.main()
