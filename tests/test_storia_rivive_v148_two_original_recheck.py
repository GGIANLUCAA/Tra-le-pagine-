"""V148: only exact historically verified film SHA, PTS, local motion.

No approval, rights, paid API or fake new finished video.
"""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from src.storia_rivive_v148_recheck_two_originals import audit,validate

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"config/storia_rivive_v148_two_source_local_motion_recheck.json"
DATA=json.loads(SOURCE.read_text(encoding="utf-8"))


class V148RealSourceIdentity(unittest.TestCase):
    def test_two_specific_prior_sha_verified_reels(self):
        rows=validate(DATA)
        self.assertEqual(len(rows),2)
        self.assertEqual({r["id"] for r in rows},{
            "perrache_train_arrival_1896","workers_sidewalk_1898"})
        self.assertTrue(all(len(r["verified_windows"])==3 for r in rows))
        self.assertFalse(DATA["vidu_permitted"])
        self.assertFalse(DATA["rights_italy_verified"])

    def test_source_page_sha_and_prior_pts_forgery_fail_before_network(self):
        bads=[
            lambda p:p["sources"][0].update(original_sha256="f"),
            lambda p:p["sources"][0].update(page="https://bad.example.org/file.webm"),
            lambda p:p["sources"][1]["verified_windows"][0].update(freeze_pts=20),
            lambda p:p["sources"][1]["verified_windows"][0].update(original_frame_sha256="0"),
            lambda p:p.update(artistically_approved=True),
            lambda p:p.update(publish_permitted=True)
        ]
        for fn in bads:
            config=copy.deepcopy(DATA);fn(config)
            with self.subTest(which=str(fn)):
                with self.assertRaisesRegex(ValueError,"V148_"):
                    validate(config)

    def test_one_or_two_originals_stay_review_only(self):
        expected={r["page"]:r for r in DATA["sources"]}
        def lookup(page):
            src=expected[page]
            return {"source_page":page,"original_sha1":src["original_sha1"],
                    "original_width_px":1920,"original_height_px":1080,
                    "download_url":"https://upload.wikimedia.org/wikipedia/commons/file.webm",
                    "size_bytes":1024}
        def download(meta,path,limit):
            Path(path).parent.mkdir(parents=True,exist_ok=True)
            Path(path).write_bytes(b"demo, not a real film")
            return expected[meta["source_page"]]["original_sha256"]
        def probe(path,meta):
            return 40.0,{"width":1920,"height":1080}
        def motion(*args):
            return {"status":"V148_LOCAL_MOTION_PASS_REVIEW_ONLY",
                    "motion_verified":True,"qualifying_pairs":6}
        with tempfile.TemporaryDirectory() as tmp:
            r=audit(SOURCE,tmp,lookup=lookup,download=download,probe=probe,check=motion)
            self.assertEqual(r["status"],"V148_TWO_ADDITIONAL_MOVING_REELS_NEED_ARTISTIC_REVIEW")
            self.assertEqual(r["additional_local_moving_reels"],2)
            self.assertEqual(r["possible_total_distinct_moving_original_reels"],5)
            self.assertFalse(r["video_finished"])
            self.assertFalse(r["five_genuine_camera_shots_artistic_review"])
            self.assertEqual(r["paid_calls"],0)
            self.assertTrue((Path(tmp)/"V148_TWO_ORIGINALS_RECHECK.json").is_file())

    def test_suspected_movement_not_autopromoted_when_metadata_changed(self):
        expected={r["page"]:r for r in DATA["sources"]}
        def lookup(page):
            src=expected[page]
            return {"source_page":page,"original_sha1":"f"*40,
                    "original_width_px":1920,"original_height_px":1080}
        def forbid_download(*args):
            self.fail("fingerprint mismatch must stop before downloading")
        with tempfile.TemporaryDirectory() as tmp:
            r=audit(SOURCE,tmp,lookup=lookup,download=forbid_download)
            self.assertEqual(r["additional_local_moving_reels"],0)
            self.assertEqual(r["status"],"V148_NOT_ENOUGH_LOCAL_MOTION_NEW_FILMS")
            self.assertTrue(all(x["status"]=="V148_SOURCE_RECHECK_BLOCKED_NOT_APPROVED"
                                for x in r["sources"]))


if __name__=="__main__":
    unittest.main()
