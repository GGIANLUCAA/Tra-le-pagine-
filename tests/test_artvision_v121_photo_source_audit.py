"""V121 tests: genuine bytes + provenance, zero bogus Museum approvals."""
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "v121_audit", ROOT / "src" / "artvision_v121_photo_source_audit.py")
audit_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit_module)


class TestV121(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.archive = Path(self.temp.name) / "five.zip"
        self.entries = []
        self.sources = []
        self.photo_bytes = {}
        for n in range(1, 6):
            ident = f"GAL{n:02}"
            raw = b"photo-test-byte-sequence-" + ident.encode()
            sha = hashlib.sha256(raw).hexdigest()
            name = ident + "_PHOTOGRAPH.jpg"
            self.photo_bytes[name] = raw
            self.entries.append({
                "id": ident, "photo_jpg_sha256": sha, "dimensions_px": [1200, 900],
                "source_page": "https://commons.wikimedia.org/wiki/File:" + ident,
                "license_declared_by_source_manifest": "CC0 1.0",
                "photographer": "Photographer",
                "assistant_visual_triage": "reference_only",
                "metric_room_reconstruction_exists": False,
                "tracked_camera_mp4_exists": False,
                "artwork_specific_frame_verified": False,
                "artistic_approval": False, "owner_approval": False,
                "eligible_for_museum_final": False,
            })
            self.sources.append({
                "id": ident, "local_basename": name, "sha256": sha,
                "dimensions": [1200, 900],
                "source_page": self.entries[-1]["source_page"],
                "license": "CC0 1.0", "author": "Photographer",
                "status": "photo_downloaded_unreviewed",
            })
        self.review = {
            "schema": audit_module.SCHEMA, "entries": self.entries,
            "accepted_room_preset_count": 0, "approved_museum_video_count": 0,
        }
        self.write_archive()

    def write_archive(self):
        with zipfile.ZipFile(self.archive, "w") as z:
            for name, raw in self.photo_bytes.items():
                z.writestr(name, raw)
            z.writestr("PROVENANCE_AND_RIGHTS.json", json.dumps({
                "asset_count": 5, "items": self.sources,
            }))

    def test_integrity_pass_does_not_certify_museum(self):
        self.assertEqual(audit_module.audit(self.archive, self.review), [])

    def test_modified_photo_is_rejected(self):
        self.photo_bytes["GAL02_PHOTOGRAPH.jpg"] += b"tampered"
        self.write_archive()
        self.assertIn("GAL02_byte_sha_mismatch",
                      audit_module.audit(self.archive, self.review))

    def test_fake_approval_is_rejected(self):
        self.review["entries"][1]["eligible_for_museum_final"] = True
        self.assertIn("GAL02_eligible_for_museum_final_false_claim",
                      audit_module.audit(self.archive, self.review))

    def test_false_claim_approved_room_is_rejected(self):
        self.review["accepted_room_preset_count"] = 1
        self.assertIn("accepted_room_preset_count_must_stay_zero_in_candidate_study",
                      audit_module.audit(self.archive, self.review))

    def test_wrong_provenance_is_rejected(self):
        self.review["entries"][0]["photographer"] = "Not Real"
        self.assertIn("GAL01_provenance_review_mismatch",
                      audit_module.audit(self.archive, self.review))

    def test_missing_photo_is_rejected(self):
        del self.photo_bytes["GAL03_PHOTOGRAPH.jpg"]
        self.write_archive()
        self.assertIn("GAL03_file_missing_or_renamed",
                      audit_module.audit(self.archive, self.review))

    def test_duplicate_identity_is_rejected(self):
        self.review["entries"][4]["id"] = "GAL01"
        self.assertIn("photo_review_ids_invalid",
                      audit_module.audit(self.archive, self.review))

    def test_zero_artifact_still_fails(self):
        self.archive.unlink()
        self.assertIn("real_photo_archive_missing",
                      audit_module.audit(self.archive, self.review))


if __name__ == "__main__":
    unittest.main()
