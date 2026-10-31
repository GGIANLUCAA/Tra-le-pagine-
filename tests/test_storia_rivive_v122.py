"""V122: source film PTS evidence from actual 1920 cotton documentary GitHub run.

The timings/cuts below are from SCOUT_REPORT.json in GitHub Actions run
41154281234, original film SHA e3022cb130442f7695d411724ae619fc8c184696ddae30293958c1c75ec8ffd9.
Only the lightweight test PNGs are synthetic. This does NOT certify the camera shots.
"""
import bisect
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw
from src.storia_rivive_frame_rank_v101 import pre_freeze_window_evidence, rank

REAL_FILM_SHA = "e3022cb130442f7695d411724ae619fc8c184696ddae30293958c1c75ec8ffd9"
REAL_CUTS = [
    2.5,6.0,12.5,17.5,20.5,23.5,26.0,29.0,32.0,36.5,39.0,42.0,
    47.5,49.0,54.0,55.5,58.5,61.0,65.0,67.0,71.0,72.0,76.5,79.5,
    83.5,86.5,90.0,96.5,99.5,103.5,106.0,109.0,112.0,116.0,122.5,
    127.5,133.5,138.5,141.5,144.5,147.5,151.5,152.0,155.0,156.5,
    159.5,162.5,165.5,167.0,170.0,177.5,180.5,184.5,187.5,189.5,
    192.5,195.0,198.0,201.0,204.0,208.5,211.5,217.0,220.0,225.0,
    230.0,241.0,244.0,248.0,249.0,252.0,255.0,259.0,262.0,265.0,
    268.0,271.0,276.0,279.5,283.5,285.0,289.0,290.0,291.0,297.0,
    302.5,305.0,310.5,313.5,315.5,318.5,320.5,325.0,332.0,334.0,
    338.0,338.5,340.0,343.0,346.0,349.0,352.0,355.0,362.0,364.0,
    369.0,374.0,376.5,381.0,384.5,389.0,391.5,402.5,404.5,411.5,
    415.0,418.0,420.5,423.5,426.0,430.0,435.0,439.0,439.5,444.0,
    444.5,450.0,450.5,455.5,460.0,463.0,467.5,470.5,473.5,477.5,
    480.5,484.0,487.0,491.0,493.0,496.0,501.5,504.0,507.5
]
REAL_PTS = [0,43760,87520,131280,175040,218800,262560,306320,350080,
            393840,437600,481360]


def provenance():
    return [{"filename": f"frame_{i+1:02d}.png",
             "source_pts":pts,"source_pts_time_s":pts/1000.0,
             "source_time_base":"1/1000",
             "shot_candidate_segment_index":bisect.bisect_right(REAL_CUTS,pts/1000.0)}
            for i,pts in enumerate(REAL_PTS)]


class TestRealFilmTemporalWindow(unittest.TestCase):
    def test_exact_archival_report_cut_count(self):
        self.assertEqual(len(REAL_CUTS), 144)
        self.assertEqual(len(REAL_PTS), 12)

    def test_three_original_freezes_are_too_close_to_previous_cut(self):
        findings=[pre_freeze_window_evidence(entry,REAL_CUTS) for entry in provenance()]
        invalid=[i+1 for i,f in enumerate(findings) if not f["eligible"]]
        self.assertEqual(invalid,[1,7,12])
        self.assertEqual(sum(f["eligible"] for f in findings),9)
        self.assertEqual(findings[0]["reason"],"NO_PRE_FREEZE_SOURCE_WINDOW")
        self.assertEqual(findings[6]["reason"],"PRE_FREEZE_WINDOW_TOO_SHORT")
        self.assertEqual(findings[11]["reason"],"PRE_FREEZE_WINDOW_TOO_SHORT")

    def test_rank_will_not_select_invalid_real_pts_even_if_picture_scores_high(self):
        with tempfile.TemporaryDirectory() as root:
            base=Path(root); folder=base/"original_frames";folder.mkdir()
            for i in range(12):
                # Artificial pixels only; real 1920 film is NOT bundled or reused.
                pic=Image.new("RGB",(1280,720),(80+i*6,85,90))
                ImageDraw.Draw(pic).rectangle((100+i*12,120,380+i*12,630),
                                               fill=(160,175,190))
                pic.save(folder/f"frame_{i+1:02d}.png")
            report={"shot_boundary_analysis":{"version":"V113_FFMPEG_SCENE_CANDIDATES",
                    "status":"FIVE_SEGMENTS_POSSIBLE_REVIEW_REQUIRED",
                    "cut_candidate_times_s":REAL_CUTS},
                    "frame_provenance":provenance()}
            (base/"SCOUT_REPORT.json").write_text(json.dumps(report),encoding="utf-8")
            result=rank(folder)
            self.assertEqual(result["status"],
                             "FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW",result)
            self.assertEqual(len(result["preselected"]),5)
            self.assertNotIn("frame_01.png",[r["filename"] for r in result["preselected"]])
            self.assertNotIn("frame_07.png",[r["filename"] for r in result["preselected"]])
            self.assertNotIn("frame_12.png",[r["filename"] for r in result["preselected"]])
            self.assertTrue(all(r["pre_freeze_window_viable"] for r in result["preselected"]))
            self.assertFalse(any(r["approved_for_i2i"] for r in result["preselected"]))

    def test_forged_pts_and_shot_segment_fail_without_decoding(self):
        original=provenance()[3]
        self.assertTrue(pre_freeze_window_evidence(original,REAL_CUTS)["eligible"])
        altered={**original,"source_pts_time_s":original["source_pts_time_s"]+0.5}
        self.assertEqual(pre_freeze_window_evidence(altered,REAL_CUTS)["reason"],
                         "SOURCE_PTS_CLOCK_MISMATCH")
        altered={**original,"shot_candidate_segment_index":0}
        self.assertEqual(pre_freeze_window_evidence(altered,REAL_CUTS)["reason"],
                         "SOURCE_PTS_SEGMENT_MISMATCH")


if __name__=="__main__":
    unittest.main()
