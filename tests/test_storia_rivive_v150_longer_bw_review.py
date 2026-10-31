"""V150: longer means MORE verified archival footage, never padded or slow motion."""
import copy
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.storia_rivive_v150_longer_bw_review import (
    EXTRA_MS, extended_window, changed_frames_in_added_window,
    render_longer, process_one, process_batch, combine, STATUS,
)
from src.storia_rivive_v149_authentic_bw_proxy import sha256_file

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"config/storia_rivive_v149_five_original_motion_preview.json"
DATA=json.loads(MANIFEST.read_text(encoding="utf-8"))


class V150MoreRealFootage(unittest.TestCase):
    def test_extended_5_windows_keep_original_freeze_exact(self):
        self.assertEqual(EXTRA_MS,1050)
        for shot in DATA["sources"]:
            start,end=extended_window(shot)
            self.assertEqual(start,shot["start_pts"]-1050)
            self.assertEqual(end,shot["freeze_pts"])
            self.assertIn(end-start,(2399,2400))
            self.assertGreaterEqual(start,0)

    def test_reject_negative_or_tampered_pts(self):
        shot=copy.deepcopy(DATA["sources"][0])
        shot["start_pts"]=200
        with self.assertRaisesRegex(ValueError,"V150_INVALID_EXTENDED"):
            extended_window(shot)
        shot=copy.deepcopy(DATA["sources"][0])
        shot["freeze_pts"]+=1
        with self.assertRaisesRegex(ValueError,"V150_INVALID_EXTENDED"):
            extended_window(shot)

    def test_changed_sha_blocks_before_video_or_paid_api(self):
        shot=DATA["sources"][0]
        with tempfile.TemporaryDirectory() as d:
            result=process_one(
                shot,Path(d),
                lookup=lambda _:{"source_page":shot["source_page"],
                                 "original_sha1":"f"*40},
                download=lambda *a:self.fail("must not download changed archive"))
        self.assertEqual(result["status"],"V150_BLOCKED")
        self.assertIn("SHA1",result["reason"])
        self.assertEqual(result["paid_api_calls"],0)
        self.assertFalse(result["artistic_approved"])

    def test_batch_is_not_final_and_paces_requests(self):
        seen=[];wait=[]
        def fake_worker(item, root):
            seen.append(item["scene"])
            return {"scene":item["scene"],"status":STATUS}
        with tempfile.TemporaryDirectory() as d:
            report=process_batch(MANIFEST,d,"a",worker=fake_worker,sleep=wait.append)
            self.assertEqual(seen,[1,2,3])
            self.assertEqual(wait,[12,12])
            self.assertEqual(report["status"],"V150_EXTENDED_BW_SOURCE_BATCH_READY")
            self.assertFalse(report["is_finished_video"])
            self.assertFalse(report["publish_permitted"])
            self.assertEqual(report["real_i2i_generated"],0)
            self.assertEqual(report["real_vidu_generated"],0)

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"),"Requires FFmpeg")
    def test_real_2400ms_video_has_extra_original_frames_not_hold(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            film=root/"source.mp4"
            subprocess.run(["ffmpeg","-nostdin","-y","-hide_banner","-loglevel","error",
                            "-f","lavfi","-i","testsrc2=size=640x360:rate=15:duration=5",
                            "-an","-c:v","mpeg4","-q:v","4",str(film)],
                           check=True,capture_output=True,timeout=60)
            shot=copy.deepcopy(DATA["sources"][0])
            shot["start_pts"]=2100
            shot["freeze_pts"]=3450
            start,end=extended_window(shot)
            variation=changed_frames_in_added_window(film,start)
            self.assertGreaterEqual(variation["sampled_frames"],5)
            self.assertGreaterEqual(
                sum(x>=1.5 for x in variation["luma_mean_abs_differences"]),2)
            dest=root/"V150.mp4"
            duration=render_longer(film,shot,dest)
            self.assertGreater(duration,2.28)
            self.assertLess(duration,2.53)
            self.assertGreater(dest.stat().st_size,5000)

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"),"Requires FFmpeg")
    def test_combine_refuses_tampered_clip_sha_and_keeps_no_approval(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            reports=[]
            for batch in ("a","b"):
                sub=root/batch
                sub.mkdir()
                rows=[]
                for shot in DATA["sources"]:
                    if shot["batch"]!=batch:continue
                    filename=f"scene_{shot['scene']:02d}_V150_BW_LONGER.mp4"
                    film=sub/filename
                    subprocess.run(["ffmpeg","-nostdin","-y","-hide_banner","-loglevel","error",
                                    "-f","lavfi","-i",f"testsrc2=size=720x1280:rate=30:duration=2.4",
                                    "-an","-c:v","libx264","-preset","ultrafast",
                                    "-pix_fmt","yuv420p",str(film)],check=True,
                                   capture_output=True,timeout=90)
                    rows.append({"scene":shot["scene"],"id":shot["id"],"status":STATUS,
                                 "original_sha256":shot["original_sha256"],
                                 "freeze_frame_sha256":shot["frame_sha256"],
                                 "start_pts":shot["start_pts"]-EXTRA_MS,
                                 "freeze_pts":shot["freeze_pts"],
                                 "clip_filename":filename,"clip_sha256":sha256_file(film),
                                 "artistic_approved":False})
                (sub/"V150_BATCH_REPORT.json").write_text(json.dumps({
                    "batch":batch,"status":"V150_EXTENDED_BW_SOURCE_BATCH_READY",
                    "paid_api_calls":0,"is_finished_video":False,
                    "publish_permitted":False,"sources":rows}))
            video=root/"out"/"preview.mp4"
            report=combine(MANIFEST,root,video)
            self.assertTrue(video.is_file())
            self.assertGreater(report["duration_s"],11.4)
            self.assertFalse(report["rights_italy_verified"])
            self.assertFalse(report["artistic_approved"])
            self.assertFalse(report["has_vidu"])
            self.assertFalse(report["has_restorations"])
            # Byte-level tampering MUST reject a subsequently modified asset.
            film=root/"a"/"scene_01_V150_BW_LONGER.mp4"
            film.write_bytes(film.read_bytes()+b"tampered")
            with self.assertRaisesRegex(ValueError,"V150_VIDEO_BYTES_SHA_MISMATCH"):
                combine(MANIFEST,root,root/"out"/"reject.mp4")


if __name__=="__main__":
    unittest.main()
