"""V150: no duplicated media downloads, reuse exact archival artifact provenance."""
import json
import tempfile
import unittest
from pathlib import Path

from src.storia_rivive_v150_single_429_recovery import recover
from src.storia_rivive_v149_authentic_bw_proxy import validate

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"config/storia_rivive_v149_five_original_motion_preview.json"


class V150RecoverWorker(unittest.TestCase):
    def test_only_third_source_from_five_is_retried_once(self):
        s=validate(json.loads(MANIFEST.read_text()))
        calls=[]
        def processor(item,out):
            calls.append(item["scene"])
            return {"status":"V149_TRUE_SOURCE_BW_MOVING_MP4_REVIEW_ONLY",
                    "scene":item["scene"],"id":item["id"]}
        with tempfile.TemporaryDirectory() as tmp:
            record=recover(MANIFEST,tmp,processor=processor,delay=lambda _:self.fail("delay if no 429"))
            self.assertEqual(calls,[3])
            self.assertEqual(record["status"],"V150_WORKERS_REAL_BW_SOURCE_MP4_RECOVERED")
            self.assertEqual(record["original_source_reused_not_redownloaded_count"],4)
            self.assertEqual(record["prior_original_artifacts"],[13050324762,13050802833])
            self.assertEqual(record["paid_calls"],0)
            self.assertFalse(record["video_finished"])
            self.assertFalse(record["publish_permitted"])

    def test_explicit_429_only_one_cooldown_retry(self):
        calls=[];sleep=[]
        def processor(item,folder):
            calls.append(item["id"])
            return ({"status":"V149_ARCHIVE_OR_PREVIEW_BLOCKED_NOT_APPROVED",
                     "reason":"HTTP Error 429: too many requests"} if len(calls)==1 else
                    {"status":"V149_TRUE_SOURCE_BW_MOVING_MP4_REVIEW_ONLY"})
        with tempfile.TemporaryDirectory() as root:
            r=recover(MANIFEST,root,processor=processor,delay=lambda n:sleep.append(n))
            self.assertEqual(len(calls),2)
            self.assertEqual(sleep,[12])
            self.assertEqual(r["paid_calls"],0)

    def test_never_retries_fake_sha_or_other_failures(self):
        calls=[]
        def processor(item,folder):
            calls.append(item["id"])
            return {"status":"V149_ARCHIVE_OR_PREVIEW_BLOCKED_NOT_APPROVED",
                    "reason":"V149_SOURCE_SHA_CHANGED"}
        with tempfile.TemporaryDirectory() as root:
            r=recover(MANIFEST,root,processor=processor,
                      delay=lambda _:self.fail("Must not retry SHA failure"))
            self.assertEqual(len(calls),1)
            self.assertEqual(r["status"],"V150_COMMONS_SOURCE_STILL_BLOCKED_NO_RESTORATION")
            self.assertEqual(r["i2i_generated"],0)
            self.assertEqual(r["vidu_generated"],0)


if __name__=="__main__":
    unittest.main()
