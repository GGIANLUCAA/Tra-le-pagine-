"""V134 offline cache-integrity regression (synthetic bytes, NOT archival QA)."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from src.storia_rivive_v134_cache_readiness import assess


SOURCE_PAGE = "https://commons.wikimedia.org/wiki/File:Historical_sample.webm"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def order_for(root):
    return {"contract": "LA_STORIA_RIVIVE_V101_SAFE_AUTOPILOT",
            "episode_id": root.name, "source_page": SOURCE_PAGE}


def fixture(root):
    film = b"synthetic-film-bytes-not-a-real-movie"
    (root / "ORIGINAL_ARCHIVE.webm").write_bytes(film)
    folder = root / "original_frames"
    folder.mkdir()
    rows = []
    for i in range(5):
        name = f"frame_{i:02d}.png"
        payload = f"synthetic-png-{i}".encode()
        (folder / name).write_bytes(payload)
        rows.append({"filename": name, "sha256": sha(payload),
                     "source_pts_logged_from_decode": True,
                     "source_pts": i * 1000, "source_pts_time_s": float(i)})
    report = {
        "status": "REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW",
        "source_page": SOURCE_PAGE,
        "original_sha256": sha(film),
        "frame_provenance_source_sha256": sha(film),
        "frame_provenance_version": "V112_SOURCE_PTS_FROM_FFMPEG_SHOWINFO",
        "source_frames_extracted": len(rows),
        "frame_provenance": rows,
        "shot_boundary_analysis": {"source_sha256": sha(film)},
    }
    (root / "SCOUT_REPORT.json").write_text(json.dumps(report), encoding="utf-8")
    return report


class CacheReadinessTests(unittest.TestCase):
    def test_exact_cached_bytes_allow_only_research(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            result = assess(root, order_for(root))
            self.assertTrue(result["ready"])
            self.assertEqual(result["verified_source_png_count"], 5)
            self.assertFalse(result["paid_api_call_permitted"])
            self.assertFalse(result["publish_permitted"])

    def test_stale_or_missing_original_film_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            (root / "ORIGINAL_ARCHIVE.webm").write_bytes(b"changed")
            self.assertEqual(assess(root, order_for(root))["reason"], "FILM_OR_PROVENANCE_SHA_MISMATCH")
            (root / "ORIGINAL_ARCHIVE.webm").unlink()
            self.assertEqual(assess(root, order_for(root))["reason"], "ORIGINAL_FILM_MISSING")

    def test_missing_or_modified_source_png_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            p = root / "original_frames/frame_02.png"
            p.write_bytes(b"tampered")
            self.assertEqual(assess(root, order_for(root))["reason"], "SOURCE_PNG_SHA_MISMATCH")
            p.unlink()
            self.assertEqual(assess(root, order_for(root))["reason"], "SOURCE_PNG_COUNT_MISMATCH")

    def test_rejected_scout_cannot_be_promoted_from_old_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = fixture(root)
            report["status"] = "SOURCE_NATIVE_DETAIL_INSUFFICIENT_SKIP_DOWNLOAD"
            (root / "SCOUT_REPORT.json").write_text(json.dumps(report))
            result = assess(root, order_for(root))
            self.assertFalse(result["ready"])
            self.assertEqual(result["reason"], "SCOUT_NOT_READY")

    def test_forged_counts_and_duplicate_rows_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = fixture(root)
            report["frame_provenance"][1] = dict(report["frame_provenance"][0])
            (root / "SCOUT_REPORT.json").write_text(json.dumps(report))
            self.assertEqual(assess(root, order_for(root))["reason"], "SOURCE_PNG_PROVENANCE_INVALID")
            report = fixture_after_duplicate(root)
            report["source_frames_extracted"] = 12
            (root / "SCOUT_REPORT.json").write_text(json.dumps(report))
            self.assertEqual(assess(root, order_for(root))["reason"], "FRAME_PROVENANCE_COUNT_INVALID")

    def test_stale_cache_from_other_archival_page_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = fixture(root)
            report["source_page"] = "https://commons.wikimedia.org/wiki/File:Other_film.webm"
            (root / "SCOUT_REPORT.json").write_text(json.dumps(report))
            result = assess(root, order_for(root))
            self.assertFalse(result["ready"])
            self.assertEqual(result["reason"], "CACHED_FILM_SOURCE_PAGE_MISMATCH")

    def test_changed_candidate_page_blocks_even_with_sha_valid_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            order = order_for(root)
            order["source_page"] = "https://commons.wikimedia.org/wiki/File:Replacement.webm"
            result = assess(root, order)
            self.assertFalse(result["ready"])
            self.assertEqual(result["reason"], "CACHED_FILM_SOURCE_PAGE_MISMATCH")

    def test_missing_or_mismatched_work_order_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            for broken in (
                None,
                {**order_for(root), "episode_id": "different_candidate"},
                {**order_for(root), "contract": "FAKE_APPROVAL"},
                {**order_for(root), "source_page": None},
            ):
                result = assess(root, broken)
                self.assertFalse(result["ready"])
                self.assertEqual(result["reason"], "CURRENT_WORK_ORDER_SOURCE_BINDING_INVALID")

    def test_corrupt_report_is_safe(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "SCOUT_REPORT.json").write_text("{invalid")
            self.assertFalse(assess(root, order_for(root))["ready"])


def fixture_after_duplicate(root):
    # Restore only the synthetic metadata, without touching existing files.
    film = (root / "ORIGINAL_ARCHIVE.webm").read_bytes()
    rows = []
    for i in range(5):
        name = f"frame_{i:02d}.png"
        rows.append({"filename": name,
                     "sha256": sha((root / "original_frames" / name).read_bytes()),
                     "source_pts_logged_from_decode": True,
                     "source_pts": i * 1000, "source_pts_time_s": float(i)})
    return {"status": "REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW",
            "source_page": SOURCE_PAGE,
            "original_sha256": sha(film),
            "frame_provenance_source_sha256": sha(film),
            "frame_provenance_version": "V112_SOURCE_PTS_FROM_FFMPEG_SHOWINFO",
            "source_frames_extracted": 5, "frame_provenance": rows,
            "shot_boundary_analysis": {"source_sha256": sha(film)}}


if __name__ == "__main__":
    unittest.main()
