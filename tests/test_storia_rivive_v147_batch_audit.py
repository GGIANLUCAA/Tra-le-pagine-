"""V147 zero-credit 3+2 archival rate-limit recovery, validate 5 SHA sources."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from src.storia_rivive_v147_archival_rate_limit_batches import validate_config
from src.storia_rivive_v147_aggregate_batches import aggregate

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"config/storia_rivive_v147_remaining_five_reels.json"
BASE=ROOT/"docs/evidence/STORIA_V146_FIRST_3_REAL_FILMS_41221612482.json"


def reel(item,pass_flag=True):
    n=item["id"]
    digest=hashlib.sha256(n.encode()).hexdigest()
    return {
        "reel_id":n,"source_page":item["page"],"year":item["year"],
        "place_label":item["place_label"],"status":(
            "V146_ONE_MOVING_ORIGINAL_SOURCE_REVIEW_ONLY" if pass_flag else "V147_NO_SAFE_MOVEMENT"),
        "original_sha256":digest,"rights_italy_verified":False,
        "artistically_approved":False,
        "best_moving_freeze":({
            "filename":"freeze_01.png","frame_sha256":hashlib.sha256(digest.encode()).hexdigest(),
            "motion_verified":True,"original_picture_content":True,
            "original_native_detail":True} if pass_flag else None)}


def create_batch_files(root,manifest,*,all_pass=True):
    paths={}
    for item in manifest["source_batches"]:
        batch=item["id"]
        folder=Path(root)/f"STORIA_V147_BATCH_{batch.upper()}_FIXTURE"
        folder.mkdir(parents=True,exist_ok=True)
        entries=[reel(x,all_pass) for x in item["reels"]]
        content={"version":"V147_TWO_BATCH_NO_REDOWNLOAD_ARCHIVAL_RESEARCH",
                 "status":"V147_SOURCE_REVIEW_ONLY","batch":batch,"source_reels":entries,
                 "api_paid_calls":0,"publish_permitted":False,"video_completed":False,
                 "rights_italy_verified":False,
                 "previous_v146_originals_reused_not_redownloaded":3}
        path=folder/"V147_BATCH_REPORT.json"
        path.write_text(json.dumps(content),encoding="utf-8")
        paths[batch]=path
    return paths


class V147BatchedTests(unittest.TestCase):
    def test_two_exact_unique_throttle_safe_batches_and_real_baseline(self):
        manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
        groups=validate_config(manifest)
        self.assertEqual({x:len(g) for x,g in groups.items()},{"a":3,"b":2})
        b=json.loads(BASE.read_text(encoding="utf-8"))
        self.assertEqual(b["verified_original_sha_count"],3)
        self.assertEqual(sum(r["best_moving_freeze"] is not None for r in b["first_three_originals"]),1)
        self.assertEqual(b["source_artifact"],13050560931)
        self.assertEqual(b["paid_api_calls"],0)

    def test_combined_eight_originals_five_moving_film_sources_not_video(self):
        manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as d:
            create_batch_files(d,manifest)
            r=aggregate(MANIFEST,BASE,d,Path(d)/"RESULT.json")
            self.assertEqual(r["status"],
                "V147_FIVE_DIFFERENT_ORIGINAL_FILMS_HAVE_MOVEMENT_REVIEW_REQUIRED")
            self.assertEqual(r["original_reels_examined"],8)
            self.assertEqual(len(r["five_review_reels"]),5)
            self.assertEqual(len({x["source_sha256"] for x in r["five_review_reels"]}),5)
            self.assertFalse(r["five_real_camera_shots_artistic_review"])
            self.assertFalse(r["rights_italy_verified"])
            self.assertFalse(r["video_finished"])
            self.assertEqual(r["paid_calls"],0)

    def test_one_missing_motion_film_blocks_five_without_fake_approval(self):
        manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as d:
            paths=create_batch_files(d,manifest,all_pass=False)
            a=json.loads(paths["a"].read_text())
            a["source_reels"][0]=reel(manifest["source_batches"][0]["reels"][0],True)
            paths["a"].write_text(json.dumps(a))
            result=aggregate(MANIFEST,BASE,d,Path(d)/"NO_REVIEW.json")
            self.assertEqual(result["status"],"V147_INSUFFICIENT_DIFFERENT_MOVING_ORIGINAL_FILMS")
            self.assertEqual(len(result["five_review_reels"]),0)

    def test_duplicate_sha_film_cannot_fake_fifth_reel(self):
        manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as d:
            paths=create_batch_files(d,manifest)
            a=json.loads(paths["a"].read_text())
            b=json.loads(paths["b"].read_text())
            for row in b["source_reels"]:
                row["original_sha256"]=a["source_reels"][0]["original_sha256"]
            paths["b"].write_text(json.dumps(b))
            result=aggregate(MANIFEST,BASE,d,Path(d)/"NO_DUPLICATE.json")
            self.assertEqual(result["status"],"V147_INSUFFICIENT_DIFFERENT_MOVING_ORIGINAL_FILMS")
            self.assertEqual(result["five_review_reels"],[])

    def test_missing_batch_or_forged_rights_fail_closed(self):
        manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as d:
            paths=create_batch_files(d,manifest)
            paths["a"].unlink()
            with self.assertRaisesRegex(ValueError,"TWO_INDEPENDENT"):
                aggregate(MANIFEST,BASE,d,Path(d)/"BLOCKED.json")
            paths=create_batch_files(d,manifest)
            b=json.loads(paths["b"].read_text())
            b["source_reels"][0]["rights_italy_verified"]=True
            paths["b"].write_text(json.dumps(b))
            with self.assertRaisesRegex(ValueError,"FORGED_APPROVAL"):
                aggregate(MANIFEST,BASE,d,Path(d)/"BLOCKED2.json")

    def test_baseline_forged_sha_document_blocks(self):
        manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as d:
            create_batch_files(d,manifest)
            prior=json.loads(BASE.read_text())
            prior["paid_api_calls"]=1
            file=Path(d)/"forged.json"
            file.write_text(json.dumps(prior))
            with self.assertRaisesRegex(ValueError,"PREVIOUS_SHA_BOUND"):
                aggregate(MANIFEST,file,d,Path(d)/"BLOCKED.json")


if __name__=="__main__":
    unittest.main()
