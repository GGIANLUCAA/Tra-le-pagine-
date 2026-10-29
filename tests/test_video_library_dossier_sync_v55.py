"""Offline safety tests for the ArtVision V55 private dossier bridge."""
import importlib.util
import pathlib
import unittest

SCRIPT=pathlib.Path(__file__).resolve().parents[1]/"src"/"video_library_dossier_sync_v55.py"
spec=importlib.util.spec_from_file_location("v55_dossier_bridge",SCRIPT)
v55=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v55)

def valid():
    h="a"*64
    return {"schema":v55.SCHEMA,"video_key":"Example.mp4","video_sha256":h,
            "video_bytes":123456,"review_state":"rendered_needs_review",
            "posts":{k:(k+" original art-history story ")*8 for k in v55.PLATFORMS},
            "rights_markdown":"Licensed painting, genuine photograph and individually licensed recording. "*4,
            "recipe":{"video":{"sha256":h},"review_state":"rendered_needs_review"}}

class SyncValidation(unittest.TestCase):
    def test_turner_real_artifact_staging_validates_offline(self):
        import json
        p=SCRIPT.parents[1]/"docs"/"productions"/"2026-10-28-turner-temeraire-v55-research-1915"/"ARCHIVE_STAGING_V55.json"
        data=json.loads(p.read_text(encoding="utf8"))
        key,size,docs=v55.prepare(data)
        self.assertEqual(key,"ARTVISION_TURNER_CINEMA_MUSEUM_V55_REVIEW.mp4")
        self.assertEqual(size,25776806)
        self.assertEqual(data["video_sha256"],"dcac4d5155598a42fd3fc29f06f455ccf38a5f63da4a0f06ef9286cbaccc4ea8")
        self.assertEqual(len([k for k in docs if k.startswith("POST_")]),4)
    def test_turner_museum_archives_exact_original_posts_with_license_footer(self):
        import hashlib
        import json
        root=SCRIPT.parents[1]
        staging=json.loads((root/"docs/productions/2026-10-28-turner-temeraire-v55-research-1915/ARCHIVE_STAGING_V55.json").read_text(encoding="utf8"))
        editorial=json.loads((root/"config/artvision_turner_cinema_museum_v55_editorial.json").read_text(encoding="utf8"))
        entry=editorial["entries"]["turner_fighting_temeraire_cinema_museum_v55"]
        _,_,docs=v55.prepare(staging)
        expected={
            "facebook":"280698ca28e34f5634156615d71dae9ff5cece03671912767f007a0e233f2fe1",
            "instagram":"9cecca456c0df92662d1afbe26bfee94fd4679bd0070d44f2224034ebbf5cc14",
            "tiktok":"1a10cb7b2ea06451c5aca996a9043f7f56f31375af5dc994a90f6e0934cd1789",
            "youtube":"4e4d78f41fccdaad2cb6d42cfaf31bd50727d5dbdf97c0655c955a42514ce167"
        }
        self.assertEqual(staging["source_post_sha256"],expected)
        for platform,original_sha in expected.items():
            payload=docs["POST_"+platform.upper()+".txt"]
            self.assertEqual(hashlib.sha256(payload).hexdigest(),original_sha)
            self.assertEqual(payload.decode("utf8"),entry["captions"][platform].strip()+"\\n\\n"+"\\n".join(entry["credit_lines"])+"\\n\\n"+" ".join(entry["hashtags"])+"\\n")
            self.assertIn("CC BY-SA 4.0",payload.decode("utf8"))
            self.assertIn("Kevin MacLeod",payload.decode("utf8"))

    def test_source_post_hash_mismatch_blocks_sync(self):
        data=valid()
        data["source_post_sha256"]={k:"0"*64 for k in v55.PLATFORMS}
        with self.assertRaisesRegex(ValueError,"Original POST SHA256 mismatch"):
            v55.prepare(data)

    def test_private_mp4_missing_stays_pending(self):
        self.assertEqual(v55.remote_video_state({"exists":False},123456),"archive_sync_pending")
        self.assertEqual(v55.remote_video_state({"exists":True,"deleted":True,"size":123456},123456),"archive_sync_pending")
    def test_private_mp4_size_conflict_is_not_silently_skipped(self):
        self.assertEqual(v55.remote_video_state({"exists":True,"size":123455},123456),"size_conflict")
    def test_private_mp4_size_match_does_not_prove_sha(self):
        self.assertEqual(v55.remote_video_state({"exists":True,"size":123456},123456),"present_size_matched_hash_unverified")
    def test_accepted(self):
        key,size,docs=v55.prepare(valid())
        self.assertEqual((key,size),("Example.mp4",123456))
        self.assertEqual(set(docs),set(v55.FILES))
        self.assertIn(b"not_granted",docs["DELIVERY_MANIFEST_V55.json"])
    def test_path_escape_rejected(self):
        data=valid();data["video_key"]="../Example.mp4"
        with self.assertRaises(ValueError):v55.prepare(data)
    def test_wrong_video_hash_rejected(self):
        data=valid();data["recipe"]["video"]["sha256"]="b"*64
        with self.assertRaises(ValueError):v55.prepare(data)
    def test_duplicate_post_rejected(self):
        data=valid();data["posts"]["youtube"]=data["posts"]["facebook"]
        with self.assertRaises(ValueError):v55.prepare(data)
    def test_nonapproved_state_rejected(self):
        data=valid();data["review_state"]="published"
        with self.assertRaises(ValueError):v55.prepare(data)
    def test_oversize_attachment_rejected(self):
        data=valid();data["posts"]["facebook"]="art "*75000
        with self.assertRaises(ValueError):v55.prepare(data)

if __name__=="__main__":
    unittest.main()
