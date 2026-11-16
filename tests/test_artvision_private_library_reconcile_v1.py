import json
import tempfile
import unittest
from pathlib import Path
from scripts.artvision_private_library_reconcile_v1 import reconcile, secure_destination, family_hint

class PrivateLibraryReconcileTests(unittest.TestCase):
    def test_exact_name_and_size_is_only_metadata(self):
        manifest={"entries":[
            {"path":"/Private/Winter/VIDEO_MOBILE.mp4","name":"VIDEO_MOBILE.mp4","size_bytes":100},
            {"path":"/Private/Winter/VIDEO_MOBILE.zip","name":"VIDEO_MOBILE.zip","size_bytes":120},
            {"path":"/Private/Other/VIDEO_MOBILE.mp4","name":"VIDEO_MOBILE.mp4","size_bytes":200},
            {"path":"/Private/Other/other.mp4","name":"other.mp4","size_bytes":50}]}
        site={"items":[{"name":"VIDEO_MOBILE.mp4","size":100},{"name":"other.mp4","size":40}]}
        report=reconcile(manifest,site)
        self.assertEqual(report["summary"]["library_mp4"],3)
        self.assertEqual(report["summary"]["same_name_same_size"],1)
        self.assertEqual(report["summary"]["same_name_size_unconfirmed_or_different"],2)
        self.assertEqual(report["summary"]["byte_hashes_independently_verified"],0)
        self.assertFalse(report["entries"][0]["file_sha256_verified"])
    def test_generic_filenames_need_folder_context(self):
        self.assertNotEqual(family_hint("CINEMA_STANDARD.mp4","/ArtVision/Stuck/CINEMA_STANDARD.mp4"),
                            family_hint("CINEMA_STANDARD.mp4","/ArtVision/Rembrandt/CINEMA_STANDARD.mp4"))
    def test_output_inside_public_repo_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/"public";root.mkdir()
            manifest=Path(tmp)/"private.json";manifest.write_text("{}")
            with self.assertRaises(ValueError):
                secure_destination(root/"data/private.json",root,manifest)
            self.assertEqual(secure_destination(Path(tmp)/"private-output.json",root,manifest),
                             (Path(tmp)/"private-output.json").resolve())
    def test_invalid_manifest_rejected(self):
        with self.assertRaises(ValueError):
            reconcile({},{"items":[]})

if __name__=="__main__":
    unittest.main()
