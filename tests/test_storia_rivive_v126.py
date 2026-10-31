"""V126: conservative five-shot review fallback with real V125 motion metadata.

Fixture timestamps and motion values are copied from the genuine source-film
Actions report 41159025397. No original movie, image or rights are embedded.
"""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from src.storia_rivive_v126_balanced_motion_review import choose_balanced_review,run

FILM_SHA="e3022cb130442f7695d411724ae619fc8c184696ddae30293958c1c75ec8ffd9"
# Eight verified pixel-motion photo windows from ORIGINAL 1920 film, not synthetic.
MOVING=[
    (21,210.16,61,.8092,7,23.112),
    (23,232.36,66,.8129,10,30.344),
    (27,277.96,78,.7889,3,19.492),
    (34,357.36,103,.8119,7,15.814),
    (40,425.00,119,.8012,10,15.921),
    (42,452.88,128,.8947,7,18.197),
    (47,498.36,141,.7674,9,43.889),
    (48,509.88,144,.8660,10,39.955),
]


def fixture():
    provenance=[]
    ranked=[]
    audit=[]
    for n,time,segment,quality,changed,spatial in MOVING:
        filename=f"frame_{n:02d}.png"
        sha=hashlib.sha256(filename.encode()).hexdigest()
        freeze_pts=round(time*1000)
        window={"start_pts":freeze_pts-1350,"freeze_pts":freeze_pts,"time_base":"1/1000"}
        provenance.append({"filename":filename,"source_pts":freeze_pts,
            "source_pts_time_s":time,"source_time_base":"1/1000",
            "shot_candidate_segment_index":segment,"sha256":sha})
        ranked.append({"filename":filename,"source_native_detail_sufficient":True,
            "source_picture_content_eligible":True,"pre_freeze_window_viable":True,
            "source_visual_quality_score":quality,"pre_freeze_window_pts":window})
        audit.append({"filename":filename,"status":"MOTION_EVIDENCE_PASS",
            "motion_verified":True,"source_pts":freeze_pts,
            "source_time_s":time,"candidate_segment_index":segment,
            "changed_pairs":changed,"sample_count":11,
            "max_spatial_pixel_delta":spatial,**window})
    scout={"original_sha256":FILM_SHA,"frame_provenance_source_sha256":FILM_SHA,
        "duration_s":524.96,"frame_provenance":provenance}
    rank={"adaptive_frame_source_sha256":FILM_SHA,
        "adaptive_review_only_not_camera_approval":True,
        "all_candidates":ranked}
    motion={"version":"V125_REAL_BW_DECODED_SPATIAL_MOTION_UNAPPROVED",
        "status":"V125_MOTION_SOURCE_SELECTION_BLOCKED",
        "source_video_sha256":FILM_SHA,"source_duration_s":524.96,
        "motion_audit":audit}
    return motion,rank,scout


class TestV126Balanced(unittest.TestCase):
    def test_eight_true_moving_metadata_yield_five_review_candidates(self):
        data=fixture()
        result=choose_balanced_review(*data)
        self.assertEqual(result["status"],"V126_FIVE_DIFFERENT_MOVING_SOURCE_CANDIDATES_REVIEW_ONLY")
        self.assertEqual(result["moving_photo_candidates"],8)
        self.assertEqual(len(result["five_review_candidates"]),5)
        self.assertEqual([x["filename"] for x in result["five_review_candidates"]],
                         ["frame_21.png","frame_23.png","frame_34.png",
                          "frame_42.png","frame_48.png"])
        self.assertEqual(result["selected_timeline_regions"],[2,3,4])
        self.assertEqual(len({x["candidate_segment_index"]
                              for x in result["five_review_candidates"]}),5)
        self.assertFalse(result["five_real_camera_shots_verified"])
        self.assertFalse(result["human_artistic_approved"])
        self.assertFalse(result["italian_rights_verified"])
        self.assertEqual(result["paid_api_calls"],0)
        self.assertFalse(result["published"])

    def test_one_or_two_time_regions_not_enough(self):
        motion,rank,scout=fixture()
        # Preserve real PTS but make the simulated film much longer, putting
        # all eight distinct moving samples in its first timeline region.
        motion["source_duration_s"]=3000.0
        scout["duration_s"]=3000.0
        result=choose_balanced_review(motion,rank,scout)
        self.assertEqual(result["status"],"V126_INSUFFICIENT_MOTION_SCENE_VARIETY")
        self.assertEqual(result["five_review_candidates"],[])

    def test_one_nearby_duplicate_camera_segment_not_automatically_selected(self):
        motion,rank,scout=fixture()
        scout["frame_provenance"][1]["shot_candidate_segment_index"]=61
        motion["motion_audit"][1]["candidate_segment_index"]=61
        result=choose_balanced_review(motion,rank,scout)
        self.assertEqual(len(result["five_review_candidates"]),5)
        self.assertEqual(len({x["candidate_segment_index"] for x in result["five_review_candidates"]}),5)

    def test_original_sha_mismatch_blocks(self):
        motion,rank,scout=fixture()
        scout["original_sha256"]="f"*64
        with self.assertRaisesRegex(ValueError,"SOURCE_REPORT_SHA_OR_STATE_MISMATCH"):
            choose_balanced_review(motion,rank,scout)

    def test_forged_motion_pts_blocks(self):
        motion,rank,scout=fixture()
        motion["motion_audit"][4]["source_pts"]=2
        with self.assertRaisesRegex(ValueError,"MOTION_PTS_OR_SEGMENT_MISMATCH"):
            choose_balanced_review(motion,rank,scout)

    def test_forged_original_clock_fails_even_if_motion_report_is_consistent(self):
        motion,rank,scout=fixture()
        scout["frame_provenance"][1]["source_pts_time_s"]+=0.1
        motion["motion_audit"][1]["source_time_s"]+=0.1
        with self.assertRaisesRegex(ValueError,"FRAME_NATIVE_PTS_CLOCK_MISMATCH"):
            choose_balanced_review(motion,rank,scout)

    def test_fake_motion_pass_below_decoding_threshold_is_not_accepted(self):
        motion,rank,scout=fixture()
        for row in motion["motion_audit"]:
            row["changed_pairs"]=1
        result=choose_balanced_review(motion,rank,scout)
        self.assertEqual(result["five_review_candidates"],[])
        self.assertEqual(result["moving_photo_candidates"],0)

    def test_report_written_even_when_blocked(self):
        motion,rank,scout=fixture()
        with tempfile.TemporaryDirectory() as root:
            base=Path(root)
            paths=[base/f for f in ("motion.json","rank.json","scout.json")]
            for file,data in zip(paths,(motion,rank,scout)):
                file.write_text(json.dumps(data),encoding="utf-8")
            out=base/"summary.json"
            result=run(*paths,out)
            self.assertEqual(json.loads(out.read_text())["status"],result["status"])
            rank["adaptive_frame_source_sha256"]="f"*64
            paths[1].write_text(json.dumps(rank),encoding="utf-8")
            blocked=run(*paths,out)
            self.assertEqual(blocked["status"],"V126_INSUFFICIENT_MOTION_SCENE_VARIETY")
            self.assertEqual(blocked["five_review_candidates"],[])


if __name__=="__main__":
    unittest.main()
