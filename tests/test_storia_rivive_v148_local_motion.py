"""V148: genuine small-subject motion vs uniform/patchwise historic flicker.

These tests are synthetic. Only real archival FFmpeg decode is evidence
of a corresponding historical source's movement; artist review still required.
"""
import hashlib
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from PIL import Image,ImageDraw

from src.storia_rivive_v148_local_motion import (
    local_motion_in_gray_frames,inspect_local_original_window)


def local_square_motion():
    sequence=[]
    for index in range(12):
        im=Image.new("L",(128,128),102)
        d=ImageDraw.Draw(im)
        x=8+index*6
        # A small original subject moves over 1.35 s, while most background
        # is unchanged. Whole-image 64x64 average dilutes these differences.
        d.rectangle((x,40,x+32,75),fill=220)
        sequence.append(im.tobytes())
    return sequence


class V148LocalMotionQA(unittest.TestCase):
    def test_small_subject_moving_across_two_adjacent_tiles_is_detected(self):
        report=local_motion_in_gray_frames(local_square_motion())
        self.assertEqual(report["status"],"V148_LOCAL_MOTION_PASS_REVIEW_ONLY",report)
        self.assertGreaterEqual(report["qualifying_pairs"],3)
        self.assertGreaterEqual(report["changed_tile_regions"],3)

    def test_uniform_global_flicker_is_not_original_subject_motion(self):
        frames=[Image.new("L",(128,128),100+18*(i%2)).tobytes()
                for i in range(12)]
        result=local_motion_in_gray_frames(frames)
        self.assertFalse(result["motion_verified"])
        self.assertEqual(result["qualifying_pairs"],0)

    def test_stationary_grain_pattern_is_rejected(self):
        im=Image.new("L",(128,128),100)
        d=ImageDraw.Draw(im)
        for i in range(160):
            x=(i*17)%128;y=(i*31)%128
            d.rectangle((x,y,x+1,y+1),fill=170)
        frames=[im.tobytes() for _ in range(12)]
        result=local_motion_in_gray_frames(frames)
        self.assertFalse(result["motion_verified"])

    def test_local_uniform_exposure_patch_is_rejected(self):
        # A patch becomes brighter but has no internal spatial displacement.
        frames=[]
        for i in range(12):
            im=Image.new("L",(128,128),95)
            ImageDraw.Draw(im).rectangle((20,30,79,79),fill=110+15*(i%2))
            frames.append(im.tobytes())
        r=local_motion_in_gray_frames(frames)
        self.assertFalse(r["motion_verified"],r)

    def test_invalid_frames_and_short_windows_fail(self):
        for frames in ([b"noise"],[b"x"*16384]*4,[b"x"*150]*12):
            self.assertFalse(local_motion_in_gray_frames(list(frames))["motion_verified"])

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"),
                         "FFmpeg necessary for physically encoded video")
    def test_encoded_source_video_local_motion_and_sha_tamper(self):
        with tempfile.TemporaryDirectory() as d:
            film=Path(d)/"film.mp4"
            subprocess.run([
                "ffmpeg","-nostdin","-y","-hide_banner","-loglevel","error",
                "-f","lavfi","-i",
                "testsrc2=size=512x512:rate=12:duration=4,scroll=h=0.2",
                "-c:v","mpeg4","-q:v","8",str(film)],
                capture_output=True,check=True,timeout=45)
            sha=hashlib.sha256(film.read_bytes()).hexdigest()
            r=inspect_local_original_window(film,sha,1000,2350,"1/1000")
            self.assertTrue(r["motion_verified"],r)
            fail=inspect_local_original_window(film,"f"*64,1000,2350,"1/1000")
            self.assertFalse(fail["motion_verified"])
            self.assertIn("SHA_MISMATCH",fail["reason"])
            too_short=inspect_local_original_window(film,sha,1000,1500,"1/1000")
            self.assertFalse(too_short["motion_verified"])


if __name__=="__main__":
    unittest.main()
