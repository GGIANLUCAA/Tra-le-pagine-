"""V146: six real-reel editorial contract, no-cost source/motion source-lock QA."""
import copy
import hashlib
import io
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from PIL import Image,ImageDraw

from src.storia_rivive_v146_multi_reel_audit import (
    validate_manifest,download_source,select_five_film_sources,
    extract_source_freezes,check_candidate,probe_real_video
)

ROOT=Path(__file__).resolve().parents[1]
M=json.loads((ROOT/"config/storia_rivive_v146_five_lumiere_reels.json").read_text(encoding="utf-8"))


def good_reel(i):
    sha=hashlib.sha256(f"original-film-{i}".encode()).hexdigest()
    return {"reel_id":f"film_{i}","source_page":f"https://commons.wikimedia.org/wiki/File:Film_{i}.webm",
            "year":1895+i,"place_label":f"YEAR {1895+i}",
            "original_sha256":sha,"original_sha1":hashlib.sha1(sha.encode()).hexdigest(),
            "status":"V146_ONE_MOVING_ORIGINAL_SOURCE_REVIEW_ONLY",
            "best_moving_freeze":{"filename":f"freeze_0{i}.png","motion_verified":True,
                "original_picture_content":True,"original_native_detail":True,
                "frame_sha256":hashlib.sha256(sha.encode()).hexdigest(),
                "source_pts":2200,"source_time_base":"1/1000","source_pts_time_s":2.2}}


class FakeStream(io.BytesIO):
    def geturl(self):
        return "https://upload.wikimedia.org/wikipedia/commons/a/ab/film.webm"
    def __enter__(self):
        return self
    def __exit__(self,*args):
        self.close()


class V146MultiReelTests(unittest.TestCase):
    def test_six_distinct_wikimedia_reels_user_gates_locked(self):
        sources=validate_manifest(M)
        self.assertEqual(len(sources),6)
        self.assertEqual(len({x["page"] for x in sources}),6)
        self.assertEqual([x["ordinal"] for x in sources],list(range(1,7)))
        self.assertTrue(all(x["year"] in (1896,1898,1899,1900) for x in sources))
        self.assertFalse(M["vidu_post_permitted"])
        self.assertFalse(M["i2i_permitted"])
        self.assertFalse(M["publish_permitted"])
        self.assertFalse(M["rights_italy_verified"])

    def test_untrusted_url_or_duplicate_source_blocks_before_network(self):
        for modification in [
            lambda m:m["sources"][5].update(page=m["sources"][0]["page"]),
            lambda m:m["sources"][5].update(page="http://not-wikimedia.example/File:Fake.webm"),
            lambda m:m["sources"][1].update(id=m["sources"][0]["id"]),
            lambda m:m["sources"][2].update(year=2026),
            lambda m:m.update(vidu_post_permitted=True),
            lambda m:m.update(rights_italy_verified=True),
        ]:
            with self.subTest(modification=str(modification)):
                wrong=copy.deepcopy(M);modification(wrong)
                with self.assertRaisesRegex(ValueError,"V146_"):
                    validate_manifest(wrong)

    def test_all_five_must_be_distinct_original_film_bytes_and_pages(self):
        reels=[good_reel(i) for i in range(6)]
        result=select_five_film_sources(reels)
        self.assertEqual(len(result),5)
        self.assertEqual(len({x["source_sha256"] for x in result}),5)
        self.assertFalse(any(x["true_physical_camera_shot_approved"] for x in result))
        self.assertFalse(any(x["vidu_clip_approved"] for x in result))
        reels[1]["original_sha256"]=reels[0]["original_sha256"]
        reels[5]["original_sha256"]=reels[3]["original_sha256"]
        self.assertEqual(select_five_film_sources(reels),[])

    def test_block_one_moving_scene_choose_alternate_sixth_reel(self):
        reels=[good_reel(i) for i in range(6)]
        reels[1]["best_moving_freeze"]["motion_verified"]=False
        picks=select_five_film_sources(reels)
        self.assertEqual(len(picks),5)
        self.assertEqual([x["reel_id"] for x in picks],
                         ["film_0","film_2","film_3","film_4","film_5"])

    def test_no_fake_motion_or_photo_promoted(self):
        reels=[good_reel(i) for i in range(6)]
        reels[0]["best_moving_freeze"]["original_picture_content"]=False
        reels[1]["best_moving_freeze"]["original_native_detail"]=False
        reels[2]["status"]="SOURCE_RESEARCH_BLOCKED"
        self.assertEqual(select_five_film_sources(reels),[])

    def test_download_original_stream_uses_commons_sha1_and_sha256(self):
        film=b"genuine source media byte fixture, not a real historical film"
        info={"download_url":"https://upload.wikimedia.org/wikipedia/commons/a/ab/film.webm",
              "size_bytes":len(film),"original_sha1":hashlib.sha1(film).hexdigest()}
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)/"source.webm"
            digest=download_source(info,dest,1000,open_url=lambda *args,**kw:FakeStream(film))
            self.assertEqual(digest,hashlib.sha256(film).hexdigest())
            self.assertEqual(dest.read_bytes(),film)
            wrong={**info,"original_sha1":"0"*40}
            with self.assertRaisesRegex(ValueError,"SHA1_MISMATCH"):
                download_source(wrong,Path(tmp)/"tampered.webm",1000,
                                open_url=lambda *args,**kw:FakeStream(film))
            self.assertFalse((Path(tmp)/"tampered.webm").exists())
            with self.assertRaisesRegex(ValueError,"SIZE_SHA1_OR_HOST_INVALID"):
                download_source({**info,"download_url":"https://evil.org/x.webm"},
                                Path(tmp)/"bad.webm",1000)

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"),"FFmpeg needed")
    def test_actual_encoded_video_native_pts_and_movie_motion_on_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            film=folder/"ORIGINAL_ARCHIVE.webm"
            # Synthetic genuine motion (scroll) is merely a regression fixture.
            subprocess.run(["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y",
                            "-f","lavfi","-i","testsrc2=size=1280x720:rate=12:duration=35,scroll=h=0.1",
                            "-c:v","mpeg4","-q:v","6",str(film)],
                           capture_output=True,check=True,timeout=55)
            duration,probe=probe_real_video(film,{
                "original_width_px":1280,"original_height_px":720})
            self.assertGreater(duration,34)
            self.assertEqual(probe["width"],1280)
            self.assertEqual(probe["height"],720)
            pngs=extract_source_freezes(film,folder/"frames",duration)
            self.assertEqual(len(pngs),3)
            self.assertTrue(all(p["source_pts_logged_from_decode"] for p in pngs))
            self.assertEqual(len({p["frame_sha256"] for p in pngs}),3)
            digest=hashlib.sha256(film.read_bytes()).hexdigest()
            row=check_candidate(film,digest,folder/"frames",pngs[1])
            self.assertTrue(row["original_picture_content"])
            self.assertTrue(row["original_native_detail"])
            self.assertTrue(row["motion_verified"],row)
            self.assertEqual(row["status"],"MOTION_EVIDENCE_PASS_REVIEW_REQUIRED")
            self.assertFalse(row["artistically_approved"])
            self.assertFalse(row["rights_italy_verified"])


if __name__=="__main__":
    unittest.main()
