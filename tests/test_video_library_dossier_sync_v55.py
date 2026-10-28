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
