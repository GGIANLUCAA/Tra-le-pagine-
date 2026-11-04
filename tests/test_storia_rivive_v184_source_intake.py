"""Offline V184 source intake tests: no network, paid APIs or media downloads."""
import importlib.util
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

MODULE_PATH = Path(__file__).resolve().parents[1] / "src" / "storia_rivive_v184_source_intake.py"
spec = importlib.util.spec_from_file_location("v184", MODULE_PATH)
v184 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v184)


class V184SourceIntakeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.file = Path(self.temp.name) / "archive.webm"
        self.file.write_bytes(b"synthetic-media-test-not-a-real-film")
        self.sha = hashlib.sha256(self.file.read_bytes()).hexdigest()

    def fake_probe(self, width=1436, height=1080, duration=820.7):
        return {"width": width, "height": height,
                "duration_seconds": duration, "codec": "vp9"}

    def test_good_metadata_still_blocks_providers_and_rights(self):
        with patch.object(v184, "probe_video", return_value=self.fake_probe()):
            r = v184.inspect_local(self.file, self.sha)
        self.assertEqual(r["status"], "ASSETS_PENDING")
        self.assertEqual(r["source_sha256"], self.sha)
        self.assertFalse(r["provider_jobs_may_start"])
        self.assertFalse(r["publish_permitted"])
        self.assertIn("ITALIAN_TERRITORIAL_RIGHTS_REVIEW_PENDING", r["blocking_issues"])

    def test_480p_is_rejected(self):
        with patch.object(v184, "probe_video", return_value=self.fake_probe(480, 360)):
            r = v184.inspect_local(self.file, self.sha)
        self.assertEqual(r["status"], "SOURCE_REJECTED")
        self.assertIn("INSUFFICIENT_VIDEO_RESOLUTION", r["blocking_issues"])

    def test_sha_mismatch_is_rejected(self):
        with patch.object(v184, "probe_video", return_value=self.fake_probe()):
            r = v184.inspect_local(self.file, "0" * 64)
        self.assertEqual(r["status"], "SOURCE_REJECTED")
        self.assertIn("SOURCE_SHA256_MISMATCH", r["blocking_issues"])

    def test_missing_sha_never_unlocks(self):
        with patch.object(v184, "probe_video", return_value=self.fake_probe()):
            r = v184.inspect_local(self.file)
        self.assertIn("SHA_LOCK_NOT_PROVIDED", r["blocking_issues"])
        self.assertFalse(r["provider_jobs_may_start"])

    def test_corrupt_video_is_rejected(self):
        with patch.object(v184, "probe_video", side_effect=ValueError("bad media")):
            r = v184.inspect_local(self.file, self.sha)
        self.assertEqual(r["status"], "SOURCE_REJECTED")
        self.assertIn("FFPROBE_FAILED", r["blocking_issues"])

    def test_symlink_is_rejected(self):
        link = Path(self.temp.name) / "link.webm"
        link.symlink_to(self.file)
        r = v184.inspect_local(link, self.sha)
        self.assertIn("LOCAL_SOURCE_MISSING_OR_SYMLINK", r["blocking_issues"])


if __name__ == "__main__":
    unittest.main()
