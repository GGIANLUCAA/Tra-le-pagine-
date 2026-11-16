"""Offline guards for the private automatic importer (no API calls)."""
import hashlib
import io
import json
import unittest
from unittest.mock import patch
import zipfile

from src.video_library_private_auto_reconcile import (
    Bridge, candidate_artifact, candidate_video,
)


class CandidateTests(unittest.TestCase):
    def test_real_owner_review_is_private_archive_candidate(self):
        self.assertTrue(candidate_video(
            "THE_LAST_OF_THE_BUFFALO_CINEMA_ANDROID_REVIEW.mp4",
            "ARTVISION_BIERSTADT_LAST_BUFFALO_CINEMA_20261115_REVIEW"))
        self.assertTrue(candidate_video(
            "GIULIANO_ANTICITERA_CINEMA_HD.mp4", "GIULIANO_ANTIKYTHERA_DONE"))

    def test_reject_source_unapproved_master_and_intermediate(self):
        for name, artifact in [
            ("SOURCE_SHOT_01.mp4", "ARTVISION_SOURCE_SCOUT"),
            ("AUDIO_POLISHED_REVIEW.mp4", "ARTVISION_REVIEW"),
            ("THE_DRYAD_CRITICO_STANDARD_GOOGLE_MUSIC20.mp4", "ARTVISION_DRYAD"),
            ("ROUGH_NOT_FINAL.mp4", "ARTVISION_READY"),
            ("TRUE_BW_MOTION_9S.mp4", "STORIA_DONE"),
            ("short.mp4", "ARTVISION_QA_ONLY_PROBE"),
            ("VIDEO.png", "ARTVISION_DONE"),
        ]:
            with self.subTest(name=name):
                self.assertFalse(candidate_video(name, artifact))

    def test_artifact_requires_video_family_and_time(self):
        recent = {"name": "ARTVISION_REAL_VIDEO_REVIEW",
                  "created_at": "2026-11-16T04:00:00Z",
                  "expired": False}
        self.assertTrue(candidate_artifact(recent, "2026-11-12T00:00:00Z"))
        self.assertFalse(candidate_artifact(recent, "2026-11-17T00:00:00Z"))
        self.assertFalse(candidate_artifact(dict(recent, expired=True),
                                            "2026-11-12T00:00:00Z"))
        self.assertFalse(candidate_artifact(dict(recent, name="SOURCE_SCOUT_TEST"),
                                            "2026-11-12T00:00:00Z"))

    def test_stage_known_exact_hash_to_private_only(self):
        raw = b"synthetic-test-bytes-" * 80
        sha = hashlib.sha256(raw).hexdigest()
        archive = io.BytesIO()
        with zipfile.ZipFile(archive, "w") as z:
            z.writestr("VIDEO_OWNER_REVIEW.mp4", raw)
        archive.seek(0)

        class FakeBridge(Bridge):
            def __init__(self):
                self.calls = []
                self.saved = False

            def private(self, method, path, *, params=None, **kwargs):
                self.calls.append((method, path, params, kwargs))
                if path == "/private-status":
                    return {"private": True, "exists": self.saved}
                if path in ("/private-single", "/private-stream"):
                    self.saved = True
                    assert params["sha256"] == sha
                    assert kwargs["data"] == raw
                    return {"private": True, "stored": True,
                            "size": len(raw), "sha256": sha}
                raise AssertionError("Unexpected route " + path)

        bridge = FakeBridge()
        with zipfile.ZipFile(archive) as z:
            with patch("src.video_library_private_auto_reconcile.audit_complete_mp4"):
                result = bridge.stage_video(14156323297,
                                            "VIDEO_OWNER_REVIEW.mp4", z)
        self.assertEqual(result, {"name": "VIDEO_OWNER_REVIEW.mp4",
                                  "sha256": sha, "bytes": len(raw)})
        self.assertNotIn("/single", [x[1] for x in bridge.calls])
        self.assertTrue(all(x[1].startswith("/private-") for x in bridge.calls))


if __name__ == "__main__":
    unittest.main()
