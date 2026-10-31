"""V124: free deterministic adaptive sampling tests with ACTUALLY ENCODED MP4.

Synthetic video verifies source PTS, frame SHA and no I2I/Vidu calls, not real
archive quality or Italian rights. Real historical audit runs separately.
"""
import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from src.storia_rivive_adaptive_sampling_v124 import (
    choose_targets, extract_target_frames, inspect, sha256_file
)

def candidates():
    return {"version": "V113_FFMPEG_SCENE_CANDIDATES",
            "status": "FIVE_SEGMENTS_POSSIBLE_REVIEW_REQUIRED",
            "cut_candidate_times_s": [3.0, 6.0, 9.0, 12.0, 15.0]}


class V124Sampling(unittest.TestCase):
    def test_balanced_distinct_segments_leave_bw_lead_in(self):
        picks = choose_targets(candidates(), 18.0, limit=5)
        self.assertEqual(len(picks), 5)
        self.assertEqual(len({x["candidate_segment_index"] for x in picks}), 5)
        for row in picks:
            self.assertGreaterEqual(row["target_time_s"]-row["proposed_segment_start_s"], 1.45)
            self.assertGreater(row["proposed_segment_end_s"]-row["target_time_s"], 0.19)

    def test_bad_cut_metadata_fails_closed(self):
        meta = candidates()
        meta["cut_candidate_times_s"] = [3.0, 6.0, 6.0, 12.0, 15.0]
        with self.assertRaisesRegex(ValueError, "CUT_TIMES_INVALID"):
            choose_targets(meta, 18)
        with self.assertRaisesRegex(ValueError, "TARGET_LIMIT_INVALID"):
            choose_targets(candidates(), 18, limit=50)
        with self.assertRaisesRegex(ValueError, "SHOT_ANALYSIS_UNAVAILABLE"):
            choose_targets({"status": "INSUFFICIENT_CUT_CANDIDATES"}, 18)

    def test_tiny_segments_fail_without_decoding(self):
        meta = candidates()
        meta["cut_candidate_times_s"] = [2.0, 4.0, 6.0, 8.0, 10.0]
        with self.assertRaisesRegex(ValueError, "NOT_ENOUGH_LONG_SOURCE_SEGMENTS"):
            choose_targets(meta, 11.1)

    def test_no_duplicate_candidates_when_limited(self):
        cuts = [3.0*(i+1) for i in range(90)]
        analysis = {**candidates(), "cut_candidate_times_s": cuts}
        samples = choose_targets(analysis, 273.0, limit=48)
        self.assertEqual(len(samples), 48)
        self.assertEqual(len({x["candidate_segment_index"] for x in samples}), 48)

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg required")
    def test_encoded_source_video_native_pts_and_sha_survive_research(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            film = root/"original.mp4"
            subprocess.run([
                "ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y",
                "-f","lavfi","-i","testsrc2=size=1280x720:rate=6:duration=18",
                "-c:v","mpeg4","-q:v","7",str(film)],
                check=True,timeout=40)
            digest = sha256_file(film)
            self.assertEqual(digest, hashlib.sha256(film.read_bytes()).hexdigest())
            original = {
                "status": "REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW",
                "original_sha256": digest,
                "duration_s": 18,
                "original_width_px":1280,"original_height_px":720,
                "shot_boundary_analysis":{**candidates(),"source_sha256":digest}
            }
            scout = root/"SCOUT_REPORT.json"
            scout.write_text(json.dumps(original),encoding="utf-8")
            out = root/"supplemental"
            result = inspect(film, scout, out, limit=5)
            self.assertEqual(result["status"], "V124_SOURCE_RESEARCH_COMPLETE_NOT_APPROVED")
            self.assertEqual(result["sampled"], 5)
            self.assertEqual(result["paid_calls"], 0)
            self.assertFalse(result["artistic_approved"])
            self.assertFalse(result["italy_rights_verified"])
            self.assertTrue((out/"ADAPTIVE_CONTACT_SHEET_V124.jpg").is_file())
            report=json.loads((out/"SCOUT_REPORT.json").read_text(encoding="utf-8"))
            self.assertEqual(report["frame_provenance_source_sha256"], digest)
            self.assertEqual(len(report["frame_provenance"]),5)
            self.assertEqual(len(list((out/"original_frames").glob("frame_*.png"))),5)
            for row in report["frame_provenance"]:
                self.assertTrue(row["source_pts_logged_from_decode"])
                self.assertFalse(row["historical_camera_shot_verified"])
                self.assertEqual(sha256_file(out/"original_frames"/row["filename"]),row["sha256"])
                self.assertGreaterEqual(row["source_pts_time_s"]+.0001,row["target_time_s"])
            selection=json.loads((out/"ADAPTIVE_RANK_V124.json").read_text(encoding="utf-8"))
            self.assertFalse(selection["approved_restored_photos"])
            self.assertTrue(selection["adaptive_review_only_not_camera_approval"])

            with self.assertRaisesRegex(ValueError,"SOURCE_BYTES_SHA_MISMATCH"):
                forged={**original,"original_sha256":"f"*64,
                        "shot_boundary_analysis":{**candidates(),"source_sha256":"f"*64}}
                scout.write_text(json.dumps(forged),encoding="utf-8")
                inspect(film,scout,root/"must_not_be_created",limit=5)
            self.assertFalse((root/"must_not_be_created").exists())


if __name__ == "__main__":
    unittest.main()
