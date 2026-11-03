import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from storia_rivive_v243_freeze_endpoint_roughcut import build

@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg required")
class V245RealDecodedFiveShotRegression(unittest.TestCase):
    def test_real_24fps_five_shot_cut_has_575_decoded_frames(self):
        """Regression for Delhi: 4.8s*24fps can encode 116, not always 115."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            film = root / "original.mp4"
            subprocess.run([
                "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
                "-f", "lavfi", "-i", "testsrc2=size=640x360:rate=24:duration=53",
                "-an", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "34",
                str(film)
            ], check=True, timeout=90)
            plan = [
                {"source_frame": f"frame_{i+1:02d}.png",
                 "sha256": "0" * 64,
                 "start_s": float(5 + i * 10),
                 "freeze_timecode_s": float(9.8 + i * 10)}
                for i in range(5)
            ]
            output = root / "V245_REVIEW_NOT_FINAL.mp4"
            report = build(film, plan, output)
            result = subprocess.run([
                "ffprobe", "-v", "error", "-select_streams", "v:0",
                "-count_frames", "-show_entries", "stream=nb_read_frames",
                "-of", "json", str(output)
            ], capture_output=True, text=True, check=True, timeout=30)
            count = int(json.loads(result.stdout)["streams"][0]["nb_read_frames"])
            self.assertEqual(count, 575)
            self.assertEqual(report["status"], "NOT_FINAL")
            self.assertFalse(report["final_mp4"])
            self.assertFalse(report["vidu_generated"])
            self.assertEqual(report["new_final_episodes_delivered"], 0)
            self.assertTrue(output.stat().st_size > 5000)

if __name__ == "__main__":
    unittest.main()
