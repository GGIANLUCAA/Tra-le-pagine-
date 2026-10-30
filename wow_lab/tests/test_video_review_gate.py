"""WOW LAB post-render regression tests; synthetic clips are QA fixtures only."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from review_video import review

@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"),
                     "ffmpeg and ffprobe required")
class VideoReviewGateTests(unittest.TestCase):
    def make_video(self,folder,source):
        video=folder/"WOW_LAB_PREVIEW.mp4"
        cmd=["ffmpeg","-nostdin","-y","-hide_banner","-loglevel","error",
             "-f","lavfi","-i",source,
             "-f","lavfi","-i","sine=frequency=330:sample_rate=24000",
             "-t","8.4","-c:v","libx264","-pix_fmt","yuv420p",
             "-c:a","aac","-shortest",str(video)]
        subprocess.run(cmd,check=True,timeout=75,capture_output=True)
        return video

    def test_moving_video_has_review_sheet_but_no_artistic_approval(self):
        (ROOT/"runs").mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT/"runs") as tmp:
            folder=Path(tmp)
            video=self.make_video(folder,"testsrc2=size=120x212:rate=12")
            result=review(video)
            self.assertTrue(result["technical_pass"],result)
            self.assertGreaterEqual(result["active_transitions"],3)
            self.assertFalse(result["artistic_approval"])
            self.assertFalse(result["publishable_master"])
            self.assertTrue((folder/"VIDEO_CONTACT_SHEET.jpg").exists())
            self.assertTrue((folder/"VIDEO_REVIEW.json").exists())

    def test_static_video_with_audio_is_rejected(self):
        (ROOT/"runs").mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT/"runs") as tmp:
            folder=Path(tmp)
            video=self.make_video(folder,"color=c=gray:size=120x212:rate=12")
            result=review(video)
            self.assertFalse(result["technical_pass"],result)
            self.assertLess(result["active_transitions"],3)

    def test_outside_runs_is_rejected_before_video_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"sample.mp4"
            path.write_bytes(b"fake")
            with self.assertRaisesRegex(ValueError,"video_must_be_inside_wow_lab_runs"):
                review(path)

    def test_engine_calls_review_before_packaging(self):
        code=(ROOT/"engine.py").read_text(encoding="utf-8")
        stage=code[code.index("def run(args):"):]
        self.assertLess(stage.index("video_review = review(tmpvideo)"),
                        stage.index("create_social(out,rec,mode)"))
        self.assertLess(stage.index("video_review = review(tmpvideo)"),
                        stage.index("zipfile.ZipFile(zipname"))

if __name__=="__main__":
    unittest.main()
