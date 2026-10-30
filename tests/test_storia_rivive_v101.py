#!/usr/bin/env python3
"""Offline V101 tests; no remote network or secrets."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
def load(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/"src"/(name+".py"))
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

auto=load("storia_rivive_autopilot_v101")
flag=load("storia_rivive_flag_title_v101")
scout=load("storia_rivive_scout_v101")
frame_rank=load("storia_rivive_frame_rank_v101")
i2i=load("storia_rivive_i2i_prepare_v102")
PROFILE={"format":"storia_rivive","schedule_hours":3,"paid_calls_allowed":False,"social_autopublish":False}
BANK={"candidates":[
    {"id":"paris_swim_1918","source_page":"https://commons.wikimedia.org/wiki/File:Example.webm","license":"CC0_as_declared","year":1918},
    {"id":"paris_train_1918","source_page":"https://commons.wikimedia.org/wiki/File:Example2.webm","license":"CC0_as_declared","year":1918}
]}

class V101Tests(unittest.TestCase):
    def test_cycle_is_stable(self):
        a=auto.build_work_order(BANK,"2026-10-30T15:01:00Z",PROFILE)
        b=auto.build_work_order(BANK,"2026-10-30T17:59:59Z",PROFILE)
        self.assertEqual(a["cycle_id"],b["cycle_id"])
        self.assertEqual(a["episode_id"],b["episode_id"])
    def test_no_fictional_approval(self):
        a=auto.build_work_order(BANK,"2026-10-30T15:00:00Z",PROFILE)
        self.assertFalse(a["human_approved"])
        self.assertFalse(a["publish_permitted"])
        self.assertEqual(a["credits_spent"],0)
        self.assertTrue(a["blocking_issues"])
    def test_paid_enabled_is_rejected(self):
        with self.assertRaises(ValueError):
            auto.build_work_order(BANK,"2026-10-30T15:00:00Z",{**PROFILE,"paid_calls_allowed":True})
    def test_source_host_allowlist(self):
        x=auto.candidate_issues({"source_page":"https://untrusted.invalid/film.webm"})
        self.assertIn("SOURCE_PAGE_NOT_ALLOWLISTED",x)
        with self.assertRaises(ValueError):scout.metadata("https://untrusted.invalid/file.webm")
    def test_unknown_historical_flag_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                flag.produce({"flag":"US","place":"NEW YORK","year":1906},str(Path(temp)/"bad.png"))
    def test_french_tricolor_render(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"title.png"
            flag.produce({"flag":"FR","place":"PARIS","year":1918},str(p))
            image=Image.open(p)
            self.assertEqual(image.size,(720,1280))
            self.assertEqual(image.getpixel((52,65))[:3],(0,35,149))
            self.assertEqual(image.getpixel((10,10))[3],0)
    def test_quality_rank_does_not_forge_approved_photos(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as temp:
            for i in range(12):
                im=Image.new("RGB",(1280,720),(40+i*5,75+i*3,125))
                im.save(Path(temp)/("frame_%02d.png"%i))
            result=frame_rank.rank(temp)
            self.assertEqual(len(result["preselected"]),5)
            self.assertEqual(result["approved_restored_photos"],0)
            self.assertTrue(all(x["approved_for_i2i"] is False for x in result["preselected"]))
            self.assertTrue(all(x["source_native_detail_sufficient"] for x in result["preselected"]))
    def test_rank_rejects_low_detail_480p_before_i2i(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as temp:
            for i in range(12):
                Image.new("RGB",(720,480),(40+i*5,70,100)).save(
                    Path(temp)/("frame_%02d.png"%i))
            result=frame_rank.rank(temp)
            self.assertEqual(result["status"],"SOURCE_NATIVE_DETAIL_INSUFFICIENT_FOR_FIVE_SHOTS")
            self.assertEqual(result["preselected"],[])
            self.assertEqual(result["eligible_native_detail_frames"],0)

    def test_i2i_manifest_locks_five_real_source_frames(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as temp:
            d=Path(temp);(d/"original_frames").mkdir()
            (d/"ORIGINAL_ARCHIVE.webm").write_bytes(b"synthetic test only")
            (d/"SCOUT_REPORT.json").write_text(json.dumps({
                "status":"REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW",
                "original_sha256":i2i.sha(d/"ORIGINAL_ARCHIVE.webm")}))
            for i in range(1,6):
                Image.new("RGB",(1280,720),(20*i,40,70)).save(d/"original_frames"/("frame_%02d.png"%i))
            order={"contract":"LA_STORIA_RIVIVE_V101_SAFE_AUTOPILOT",
                   "cycle_id":"storia-20261030-1200","episode_id":"beirut_1919_street",
                   "paid_api_call_permitted":False,"publish_permitted":False,
                   "blocking_issues":[]}
            selection={"status":"FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW",
                       "preselected":[{"filename":"frame_%02d.png"%i} for i in range(1,6)]}
            result=i2i.build(order,selection,d)
            self.assertEqual(len(result["original_frame_jobs"]),5)
            self.assertEqual(result["photos_generated"],0)
            self.assertEqual(result["provider_requests_sent"],0)
            self.assertTrue(all(x["source_sha256"] and x["request_sent"] is False for x in result["original_frame_jobs"]))
            self.assertEqual(result["source_video_sha256"],i2i.sha(d/"ORIGINAL_ARCHIVE.webm"))
    def test_i2i_preflight_blocks_unverified_italian_rights(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError,"V101_SOURCE_PREFLIGHT_BLOCKED"):
                i2i.build({"contract":"LA_STORIA_RIVIVE_V101_SAFE_AUTOPILOT",
                    "paid_api_call_permitted":False,"publish_permitted":False,
                    "blocking_issues":["ITALY_AND_RESIDUAL_RIGHTS_NEED_REVIEW"]},
                    {"status":"FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW",
                     "preselected":[{"filename":"frame_%02d.png"%i} for i in range(1,6)]},
                    Path(temp))

    def test_i2i_preflight_blocks_480p_and_duplicate_bytes(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as temp:
            d=Path(temp);(d/"original_frames").mkdir()
            (d/"ORIGINAL_ARCHIVE.webm").write_bytes(b"synthetic test only")
            (d/"SCOUT_REPORT.json").write_text(json.dumps({
                "status":"REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW",
                "original_sha256":i2i.sha(d/"ORIGINAL_ARCHIVE.webm")}))
            order={"contract":"LA_STORIA_RIVIVE_V101_SAFE_AUTOPILOT",
                   "cycle_id":"storia-20261030-1200","episode_id":"beirut_1919_street",
                   "paid_api_call_permitted":False,"publish_permitted":False,
                   "blocking_issues":[]}
            selection={"status":"FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW",
                       "preselected":[{"filename":"frame_%02d.png"%i} for i in range(1,6)]}
            for i in range(1,6):
                Image.new("RGB",(720,480),(20*i,40,70)).save(d/"original_frames"/("frame_%02d.png"%i))
            with self.assertRaisesRegex(ValueError,"SOURCE_NATIVE_DETAIL_INSUFFICIENT"):
                i2i.build(order,selection,d)
            for i in range(1,6):
                Image.new("RGB",(1280,720),(20,40,70)).save(d/"original_frames"/("frame_%02d.png"%i))
            with self.assertRaisesRegex(ValueError,"DUPLICATE_SOURCE_FRAME_BYTES"):
                i2i.build(order,selection,d)
            (d/"SCOUT_REPORT.json").write_text(json.dumps({
                "status":"REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW",
                "original_sha256":"0"*64}))
            with self.assertRaisesRegex(ValueError,"SCOUT_FILM_SHA_MISMATCH"):
                i2i.build(order,selection,d)

    def test_i2i_manifest_blocks_missing_source_frame(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                i2i.build({"contract":"LA_STORIA_RIVIVE_V101_SAFE_AUTOPILOT",
                    "paid_api_call_permitted":False,"publish_permitted":False},
                    {"status":"FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW",
                     "preselected":[{"filename":"frame_%02d.png"%i} for i in range(1,6)]},Path(temp))
    def test_source_rights_not_self_approved(self):
        a=auto.build_work_order(BANK,"2026-10-30T15:00:00Z",PROFILE)
        self.assertIn("ITALY_AND_RESIDUAL_RIGHTS_NEED_REVIEW",a["blocking_issues"])

if __name__=="__main__":unittest.main()
