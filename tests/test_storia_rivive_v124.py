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
    choose_targets, extract_target_frames, inspect, sha256_file, spread_review_shortlist, exact_pts_time_from_showinfo
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
        meta["cut_candidate_times_s"] = [1.0, 2.0, 3.0, 4.0, 5.0]
        with self.assertRaisesRegex(ValueError, "NOT_ENOUGH_LONG_SOURCE_SEGMENTS"):
            choose_targets(meta, 6.1)

    def test_real_1916_ogg_showinfo_rounded_pts_are_not_forgery(self):
        # Actual unmodified Commons Theora source has timebase 100/2997.
        # Observed frame_12: pts=4367, showinfo pts_time=145.712
        # although the exact timestamp is 145.7123790457...
        from fractions import Fraction
        exact = float(Fraction(4367*100,2997))
        self.assertAlmostEqual(exact_pts_time_from_showinfo(
            4367,"100/2997","145.712"),exact,places=9)
        self.assertAlmostEqual(exact_pts_time_from_showinfo(
            3970,"100/2997","132.466"),
            float(Fraction(3970*100,2997)),places=9)
        # A forged rounded time beyond the printed 0.001 precision is rejected.
        for bad in ("145.713","145.710","146.712","not-a-time"):
            with self.subTest(bad=bad):
                with self.assertRaisesRegex(ValueError,"V124_SOURCE_PTS_NOT_GENUINE"):
                    exact_pts_time_from_showinfo(4367,"100/2997",bad)

    def test_ogg_source_pts_time_base_cannot_be_forged(self):
        for bad_base in ("100/0","0/2997","100/xx","-2/2997"):
            with self.subTest(base=bad_base):
                with self.assertRaisesRegex(ValueError,"V124_SOURCE_PTS_NOT_GENUINE"):
                    exact_pts_time_from_showinfo(4367,bad_base,"145.712")
        with self.assertRaisesRegex(ValueError,"V124_SOURCE_PTS_NOT_GENUINE"):
            exact_pts_time_from_showinfo(-1,"100/2997","-0.03337")

    def test_no_duplicate_candidates_when_limited(self):
        cuts = [3.0*(i+1) for i in range(90)]
        analysis = {**candidates(), "cut_candidate_times_s": cuts}
        samples = choose_targets(analysis, 273.0, limit=48)
        self.assertEqual(len(samples), 48)
        self.assertEqual(len({x["candidate_segment_index"] for x in samples}), 48)

    def test_real_1920_verified_photo_metrics_yield_wide_spread_instead_of_late_repeats(self):
        # Filename, actual original source PTS seconds, V113 segment, V123 score,
        # from GitHub Actions authentic archived report 41157549529.
        # Metadata only: real film frames are NOT embedded in this test.
        observed = [
            (3,22.16,5,.4685),(4,30.68,8,.6968),
            (9,85.16,25,.7861),(10,98.16,28,.7883),
            (11,105.0,30,.6715),(14,143.16,39,.6378),
            (16,161.16,46,.7187),(20,199.68,58,.7573),
            (21,210.16,61,.8092),(23,232.36,66,.8129),
            (25,260.68,73,.8536),(26,269.68,76,.7736),
            (27,277.96,78,.7889),(34,357.36,103,.8119),
            (37,390.52,111,.8569),(40,425.0,119,.8012),
            (42,452.88,128,.8947),(43,461.68,130,.8588),
            (46,492.52,139,.8246),(47,498.36,141,.7674),
            (48,509.88,144,.8660)]
        scored=[{"filename":f"frame_{n:02d}.png",
                 "source_visual_quality_score":score,
                 "source_picture_content_eligible":True,
                 "source_native_detail_sufficient":True,
                 "pre_freeze_window_viable":True}
                for n, seconds, seg, score in observed]
        provenance=[{"filename":f"frame_{n:02d}.png",
                     "source_pts_time_s":seconds,
                     "shot_candidate_segment_index":seg}
                    for n, seconds, seg, score in observed]
        result=spread_review_shortlist({"all_candidates":scored},provenance,524.96)
        self.assertEqual(result["status"],"V124_FIVE_TIME_SPREAD_SOURCE_CANDIDATES_REVIEW_ONLY")
        self.assertEqual([x["filename"] for x in result["preselected"]],
                         ["frame_10.png","frame_20.png","frame_25.png","frame_37.png","frame_42.png"])
        self.assertEqual({x["review_time_bucket"] for x in result["preselected"]},set(range(5)))
        self.assertFalse(result["artistic_approved"])
        self.assertFalse(result["historical_camera_shots_verified"])

    def test_temporal_shortlist_rejects_one_region_empty(self):
        result=spread_review_shortlist(
            {"all_candidates":[{"filename":f"frame_{i:02d}.png",
                 "source_visual_quality_score":.9,
                 "source_picture_content_eligible":True,
                 "source_native_detail_sufficient":True,
                 "pre_freeze_window_viable":True} for i in range(1,6)]},
            [{"filename":f"frame_{i:02d}.png","source_pts_time_s":100+i,
              "shot_candidate_segment_index":i} for i in range(1,6)],525)
        self.assertEqual(result["status"],"V124_NOT_FIVE_SPREAD_REGIONS")
        self.assertEqual(result["preselected"],[])

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
