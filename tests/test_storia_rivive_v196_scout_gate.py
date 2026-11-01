"""Offline regression: V101 must not treat broken cache as ready or spend credits."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("v196", ROOT / "src" / "storia_rivive_v196_scout_gate.py")
v196 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v196)

ORDER = {
    "contract": "LA_STORIA_RIVIVE_V101_SAFE_AUTOPILOT",
    "source_page": "https://commons.wikimedia.org/wiki/File:Example.webm",
    "paid_api_call_permitted": False,
    "publish_permitted": False,
}


class V196ScoutGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.film = self.root / "ORIGINAL_ARCHIVE.webm"
        self.film.write_bytes(b"synthetic archival bytes for offline unit test")
        self.frames = self.root / "original_frames"
        self.frames.mkdir()
        for index in range(5):
            Image.new("RGB", (128, 128), (index * 30, 80, 90)).save(self.frames / f"frame_{index:02}.png")
        self.report = {
            "status": v196.READY_STATUS,
            "source_page": ORDER["source_page"],
            "original_sha256": hashlib.sha256(self.film.read_bytes()).hexdigest(),
            "source_frames_extracted": 5,
        }
        self.save_report()

    def save_report(self):
        (self.root / "SCOUT_REPORT.json").write_text(json.dumps(self.report), encoding="utf-8")

    def check_blocked(self, reason):
        result = v196.inspect_cache(ORDER, self.root)
        self.assertFalse(result["ready"])
        self.assertEqual(result["reason"], reason)
        self.assertEqual(result["paid_calls"], 0)
        self.assertFalse(result["publish_permitted"])

    def test_genuine_cache_is_research_only(self):
        result = v196.inspect_cache(ORDER, self.root)
        self.assertTrue(result["ready"])
        self.assertEqual(result["verified_original_frames"], 5)
        self.assertEqual(result["restored_photos"], 0)
        self.assertEqual(result["vidu_clips"], 0)
        self.assertNotIn("FINAL", result["status"])

    def test_missing_report(self):
        (self.root / "SCOUT_REPORT.json").unlink()
        self.check_blocked("MISSING_OR_INVALID_SCOUT_REPORT")

    def test_false_ready_string_does_not_suffice(self):
        self.film.write_bytes(b"tampered film")
        self.check_blocked("ORIGINAL_FILM_SHA256_MISMATCH")

    def test_cached_different_source(self):
        self.report["source_page"] = "https://commons.wikimedia.org/wiki/File:Other.webm"
        self.save_report()
        self.check_blocked("CACHE_SOURCE_MISMATCH")

    def test_fewer_than_five_frames(self):
        (self.frames / "frame_04.png").unlink()
        self.check_blocked("INSUFFICIENT_OR_INCONSISTENT_FRAMES")

    def test_corrupt_png(self):
        (self.frames / "frame_04.png").write_bytes(b"not png")
        self.check_blocked("FRAME_PNG_DECODE_FAILED")

    def test_unsafe_permissions(self):
        result = v196.inspect_cache({**ORDER, "paid_api_call_permitted": True}, self.root)
        self.assertEqual(result["reason"], "UNSAFE_WORK_ORDER_PERMISSIONS")

    def test_source_scout_failed(self):
        self.report["status"] = "SOURCE_SCOUT_BLOCKED_NO_PRODUCTION"
        self.save_report()
        self.check_blocked("SCOUT_NOT_READY")


if __name__ == "__main__":
    unittest.main()
