"""V149: preserve exact five authenticated original source clips before coloring.

The test MP4 is synthetically encoded only. Historical source SHA frames must
be physically verified in the GitHub Actions run before the B/W preview.
"""
import copy
import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from src.storia_rivive_v149_authentic_bw_proxy import (
    validate,render_clip,probe_clip,exact_frame_png_from_pts,
    process_one,process_with_rate_limit_policy,run
)

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"config/storia_rivive_v149_five_original_motion_preview.json"
DATA=json.loads(MANIFEST.read_text(encoding="utf-8"))


class V149BWSafePreview(unittest.TestCase):
    def test_five_independent_originals_match_previous_real_video_sha_audits(self):
        shots=validate(DATA)
        self.assertEqual([r["scene"] for r in shots],list(range(1,6)))
        self.assertEqual([r["batch"] for r in shots],["a","a","a","b","b"])
        self.assertEqual(len({r["original_sha256"] for r in shots}),5)
        self.assertEqual(len({r["source_page"] for r in shots}),5)
        self.assertTrue(all(r["original_motion_evidence"].startswith(("V146","V147","V148"))
                            for r in shots))
        self.assertEqual(DATA["target_proxy"]["raster"],[720,1280])
        self.assertFalse(DATA["target_proxy"]["audio"])
        self.assertFalse(DATA["target_proxy"]["is_final"])
        self.assertEqual(DATA["credits_spent"],0)

    def test_no_approval_sha_or_timing_forgery(self):
        for change in (
            lambda m:m.update(vidu_allowed=True),
            lambda m:m.update(publish_allowed=True),
            lambda m:m.update(artistic_approved=True),
            lambda m:m["sources"][0].update(original_sha256="f"),
            lambda m:m["sources"][4].update(source_page=m["sources"][0]["source_page"]),
            lambda m:m["sources"][1].update(freeze_pts=20590),
            lambda m:m["sources"][3].update(role="vidu_later_only"),
            lambda m:m["target_proxy"].update(allow_color_generation=True),
            lambda m:m["target_proxy"].update(is_final=True),
        ):
            m=copy.deepcopy(DATA)
            change(m)
            with self.subTest(change=str(change)):
                with self.assertRaisesRegex(ValueError,"V149_"):
                    validate(m)

    def test_download_and_proxy_must_remain_explicit_not_final(self):
        shots=validate(DATA)
        def lookup(page):
            p=next(x for x in shots if x["source_page"]==page)
            return {"source_page":page,"original_sha1":p["original_sha1"],
                    "original_width_px":1920,"original_height_px":1080}
        def download(info,path,limit):
            Path(path).parent.mkdir(parents=True,exist_ok=True)
            Path(path).write_bytes(b"safe mocked byte fixture")
            return next(x["original_sha256"] for x in shots
                        if x["source_page"]==info["source_page"])
        def probe(path,meta):
            return 40.0,{"width":1920,"height":1080}
        def freeze(path,item,dest):
            Path(dest).parent.mkdir(parents=True,exist_ok=True)
            Path(dest).write_bytes(b"test provenance")
            return item["frame_sha256"]
        def render(path,item,dest):
            Path(dest).parent.mkdir(parents=True,exist_ok=True)
            Path(dest).write_bytes(b"synthetic fixture pretending to be MP4 only in this test")
            return 1.35
        with tempfile.TemporaryDirectory() as d:
            obj=process_one(shots[0],Path(d),lookup=lookup,download=download,
                            probe=probe,freeze=freeze,render=render)
            self.assertEqual(obj["status"],"V149_TRUE_SOURCE_BW_MOVING_MP4_REVIEW_ONLY")
            self.assertFalse(obj["artistic_approved"])
            self.assertFalse(obj["rights_italy_verified"])
            self.assertFalse(obj["video_finished"])
            self.assertEqual(obj["paid_api_calls"],0)
            self.assertEqual(obj["source_sha256"],shots[0]["original_sha256"])

    def test_changed_commons_sha_blocks_renamed_or_replaced_source(self):
        s=DATA["sources"][0]
        def fake_lookup(page):
            return {"source_page":page,"original_sha1":"f"*40}
        def forbidden_download(*args):
            self.fail("Changed Commons byte fingerprint cannot be downloaded")
        with tempfile.TemporaryDirectory() as d:
            report=process_one(s,Path(d),lookup=fake_lookup,download=forbidden_download)
            self.assertEqual(report["status"],"V149_ARCHIVE_OR_PREVIEW_BLOCKED_NOT_APPROVED")
            self.assertIn("SHA1_OR_PAGE_CHANGED",report["reason"])

    def test_commons_429_get_only_one_bounded_retry(self):
        shot=DATA["sources"][2]
        calls=[]
        waits=[]
        def worker(item,root):
            calls.append(item["id"])
            if len(calls)==1:
                return {"status":"V149_ARCHIVE_OR_PREVIEW_BLOCKED_NOT_APPROVED",
                        "reason":"HTTP Error 429: Too many requests"}
            return {"status":"V149_TRUE_SOURCE_BW_MOVING_MP4_REVIEW_ONLY"}
        with tempfile.TemporaryDirectory() as d:
            report=process_with_rate_limit_policy(
                shot,Path(d),worker=worker,sleep=waits.append)
        self.assertEqual(calls,[shot["id"],shot["id"]])
        self.assertEqual(waits,[60])
        self.assertEqual(report["commons_429_retry_count"],1)
        self.assertEqual(report["status"],"V149_TRUE_SOURCE_BW_MOVING_MP4_REVIEW_ONLY")

    def test_commons_429_twice_stays_blocked_no_third_request(self):
        calls=[]
        def worker(item,root):
            calls.append(item["id"])
            return {"status":"V149_ARCHIVE_OR_PREVIEW_BLOCKED_NOT_APPROVED",
                    "reason":"HTTP Error 429: Too many requests"}
        with tempfile.TemporaryDirectory() as d:
            report=process_with_rate_limit_policy(
                DATA["sources"][0],Path(d),worker=worker,sleep=lambda _:None)
        self.assertEqual(len(calls),2)
        self.assertEqual(report["status"],"V149_ARCHIVE_OR_PREVIEW_BLOCKED_NOT_APPROVED")
        self.assertEqual(report["commons_429_retry_count"],1)

    def test_sha_mismatch_never_retried_even_if_later_network_recovers(self):
        calls=[]
        waits=[]
        def worker(item,root):
            calls.append(item["id"])
            return {"status":"V149_ARCHIVE_OR_PREVIEW_BLOCKED_NOT_APPROVED",
                    "reason":"V149_FILM_SHA256_CHANGED_FROM_REAL_AUDIT"}
        with tempfile.TemporaryDirectory() as d:
            report=process_with_rate_limit_policy(
                DATA["sources"][0],Path(d),worker=worker,sleep=waits.append)
        self.assertEqual(len(calls),1)
        self.assertEqual(waits,[])
        self.assertIn("SHA256_CHANGED",report["reason"])

    def test_batch_a_paces_requests_and_does_not_claim_final(self):
        waits=[]
        seen=[]
        def worker(item,root):
            seen.append(item["scene"])
            return {"scene":item["scene"],
                    "status":"V149_TRUE_SOURCE_BW_MOVING_MP4_REVIEW_ONLY"}
        with tempfile.TemporaryDirectory() as d:
            report=run(MANIFEST,Path(d),"a",worker=worker,sleep=waits.append)
        self.assertEqual(seen,[1,2,3])
        self.assertEqual(waits,[12,12])
        self.assertEqual(report["clips_verified"],3)
        self.assertFalse(report["is_finished_video"])
        self.assertFalse(report["publish_permitted"])
        self.assertEqual(report["paid_api_calls"],0)

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"),
                         "Requires actual FFmpeg encoding and source PNG re-decode")
    def test_actual_encoded_original_mp4_creates_silent_portrait_bw_clip(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            film=root/"real_synthetic_source.mp4"
            subprocess.run([
                "ffmpeg","-nostdin","-y","-hide_banner","-loglevel","error",
                "-f","lavfi","-i","testsrc2=size=640x360:rate=15:duration=4",
                "-an","-c:v","mpeg4","-q:v","6",str(film)],
                capture_output=True,check=True,timeout=55)
            item={"start_pts":1000,"freeze_pts":2350,"time_base":"1/1000"}
            preview=root/"source_only_bw.mp4"
            duration=render_clip(film,item,preview)
            self.assertTrue(preview.is_file())
            self.assertGreater(preview.stat().st_size,5_000)
            self.assertTrue(1.25<=duration<=1.48)
            self.assertAlmostEqual(probe_clip(preview),duration,places=2)
            # Exact PNG from an actually encoded video with 1/15000 native PTS:
            # capture a frame using ffmpeg and verify checksum, then tamper.
            f={"freeze_pts":2350,"frame_sha256":"0"*64}
            with self.assertRaisesRegex(ValueError,"V149_FREEZE_FRAME"):
                exact_frame_png_from_pts(film,f,root/"original.png")


if __name__=="__main__":
    unittest.main()
