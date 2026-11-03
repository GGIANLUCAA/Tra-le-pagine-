import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import storia_rivive_v247_motion_intertitle_qa as mod

@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"),"ffmpeg needed")
class RealMotionIntertitleTests(unittest.TestCase):
    def test_five_real_decoded_segments_and_title_intrusion(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            video=root/"source.mp4"
            # 575 real encoded frames; 1st segment black (must be flagged),
            # remaining segments textured/bright photographic surrogates.
            vf=("color=c=black:s=720x1280:r=24:d=4.791667 [a];"
                "testsrc2=s=720x1280:r=24:d=19.166667 [b];"
                "[a][b]concat=n=2:v=1:a=0,format=yuv420p[v]")
            subprocess.run(["ffmpeg","-nostdin","-v","error","-y",
                "-filter_complex",vf,"-map","[v]","-frames:v","575",
                "-c:v","libx264","-preset","ultrafast","-crf","30",str(video)],
                check=True,timeout=120)
            manifest=root/"manifest.json"
            manifest.write_text(json.dumps({"version":"V243_ARCHIVAL_FREEZE_ENDPOINT_REVIEW",
                "shots":[{"source_frame":f"frame_{i:02}.png","sha256":"0"*64}
                         for i in range(1,6)]}))
            report=mod.check(video,manifest,root/"report.json")
            self.assertEqual(report["sampled_decoded_frames"],15)
            self.assertIn(1,report["flagged_shots"])
            self.assertEqual(report["status"],"REJECT_MOTION_WINDOW_FOR_EDITORIAL_REVIEW")
            self.assertFalse(report["final_video"])
            self.assertEqual(len(report["shots"]),5)
            self.assertTrue((root/"report.json").is_file())

    def test_invalid_manifest_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            video=root/"fake.mp4"
            video.write_bytes(b"not a real video")
            manifest=root/"manifest.json"
            manifest.write_text(json.dumps({"version":"V243_ARCHIVAL_FREEZE_ENDPOINT_REVIEW","shots":[]}))
            with self.assertRaisesRegex(ValueError,"INVALID_SOURCE_REVIEW_MANIFEST"):
                mod.check(video,manifest,root/"out.json")

if __name__=="__main__":
    unittest.main()
