"""V126 frame-diversity offline regression; fixtures are artificial, NOT archive proof."""
import hashlib
import json
import random
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from src.storia_rivive_v126_frame_diversity import audit
from src.storia_rivive_frame_rank_v101 import pre_freeze_window_evidence


def make_case(root, *, duplicate=False, flat=False):
    root = Path(root)
    frames = root / "original_frames"
    frames.mkdir()
    rng = random.Random(4261)
    rows = []
    source = None
    for i in range(5):
        if flat and i == 3:
            pixels = [128] * (128*96)
        elif duplicate and i == 4:
            pixels = [min(255, v+9) for v in source]
        else:
            pixels = [rng.randrange(10, 245) for _ in range(128*96)]
            if i == 0:
                source = pixels
        name = f"frame_{i:02d}.png"
        path = frames/name
        im = Image.new("L", (128,96))
        im.putdata(pixels)
        im.save(path)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append({"filename":name,"frame_sha256":digest,
                     "source_film_sha256":"a"*64,"timeline_region":i,
                     "human_camera_shot_approval":False})
    times=[1.65,5.,9.,13.,17.]
    cuts=[3.,7.,11.,15.]
    provenance=[]
    for i, row in enumerate(rows):
        time_s=times[i]
        source={"filename":row["filename"],"sha256":row["frame_sha256"],
                "source_pts":round(time_s*1000),"source_pts_time_s":time_s,
                "source_time_base":"1/1000","source_pts_logged_from_decode":True,
                "shot_candidate_segment_index":i}
        provenance.append(source)
        window=pre_freeze_window_evidence(source,cuts)
        assert window["eligible"],window
        row.update({"source_pts":source["source_pts"],"source_time_s":time_s,
                    "time_base":"1/1000","candidate_segment_index":i,
                    "pre_freeze_window_pts":{k:window[k] for k in
                                             ("start_pts","freeze_pts","time_base")}})
    scout_data={
        "status":"REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW",
        "adaptive_research_version":"V124_UNAPPROVED_LONG_SEGMENT_TARGET_SAMPLING",
        "original_sha256":"a"*64,"frame_provenance_source_sha256":"a"*64,
        "duration_s":20.,"historical_camera_shots_verified":False,
        "frame_provenance":provenance,
        "shot_boundary_analysis":{
            "version":"V113_FFMPEG_SCENE_CANDIDATES",
            "source_sha256":"a"*64,
            "status":"FIVE_SEGMENTS_POSSIBLE_REVIEW_REQUIRED",
            "cut_candidate_times_s":cuts}}
    scout_file=root/"SCOUT_REPORT.json"
    scout_file.write_text(json.dumps(scout_data),encoding="utf-8")
    data={"version":"V125_REAL_BW_DECODED_SPATIAL_MOTION_UNAPPROVED",
          "status":"V125_FIVE_MOVING_PHOTO_REGIONS_REVIEW_REQUIRED",
          "five_genuine_camera_shots_approved":False,
          "italian_rights_verified":False,"source_video_sha256":"a"*64,
          "five_review_shots":rows}
    report=root/"V125.json"
    report.write_text(json.dumps(data),encoding="utf-8")
    return report,frames,root/"V126.json",scout_file


class V126FrameDiversityTests(unittest.TestCase):
    def test_five_different_photographs_still_need_human_review(self):
        with tempfile.TemporaryDirectory() as root:
            result=audit(*make_case(root))
            self.assertEqual(result["status"],"V126_VISUALLY_DIVERSE_FRAMES_REVIEW_REQUIRED")
            self.assertFalse(result["five_genuine_camera_shots_approved"])
            self.assertFalse(result["italian_rights_verified"])
            self.assertEqual(result["vidu_calls"],0)
            self.assertTrue(result["original_pts_provenance_crosschecked"])

    def test_brightness_shifted_duplicate_blocked(self):
        with tempfile.TemporaryDirectory() as root:
            result=audit(*make_case(root,duplicate=True))
            self.assertEqual(result["status"],"V126_NEAR_DUPLICATE_FRAMES_BLOCKED_FOR_REVIEW")
            self.assertEqual([(p["first"],p["second"]) for p in result["near_duplicate_pairs"]],
                             [("frame_00.png","frame_04.png")])

    def test_low_detail_frame_blocked(self):
        with tempfile.TemporaryDirectory() as root:
            result=audit(*make_case(root,flat=True))
            self.assertEqual(result["status"],"V126_LOW_DETAIL_SOURCE_FRAMES_BLOCKED")
            self.assertEqual(result["low_contrast_frames"][0]["filename"],"frame_03.png")

    def test_tampered_png_is_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            report,frames,out,scout=make_case(root)
            (frames/"frame_02.png").write_bytes(b"fake")
            with self.assertRaisesRegex(ValueError,"BYTES_MISSING_OR_TAMPERED"):
                audit(report,frames,out,scout)

    def test_forged_review_or_duplicate_region_is_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            report,frames,out,scout=make_case(root)
            data=json.loads(report.read_text())
            data["five_genuine_camera_shots_approved"]=True
            report.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,"NOT_IN_REVIEW_STATE"):
                audit(report,frames,out,scout)
            data["five_genuine_camera_shots_approved"]=False
            data["five_review_shots"][4]["timeline_region"]=0
            report.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,"TIME_REGION"):
                audit(report,frames,out,scout)


    def test_v125_timecode_forgery_rejected_against_original_ledger(self):
        with tempfile.TemporaryDirectory() as root:
            report,frames,out,scout=make_case(root)
            rows=json.loads(report.read_text())
            rows["five_review_shots"][2]["source_pts"]+=10
            report.write_text(json.dumps(rows))
            with self.assertRaisesRegex(ValueError,"SOURCE_PTS_OR_FRAME_SHA_MISMATCH"):
                audit(report,frames,out,scout)

    def test_fake_time_region_rejected_before_photo_comparison(self):
        with tempfile.TemporaryDirectory() as root:
            report,frames,out,scout=make_case(root)
            rows=json.loads(report.read_text())
            rows["five_review_shots"][3]["timeline_region"]=4
            report.write_text(json.dumps(rows))
            with self.assertRaisesRegex(ValueError,"FAKE_TIMELINE_REGION_OR_SEGMENT"):
                audit(report,frames,out,scout)

    def test_cross_film_scout_ledger_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            report,frames,out,scout=make_case(root)
            data=json.loads(scout.read_text())
            data["frame_provenance_source_sha256"]="b"*64
            scout.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,"SCOUT_SOURCE_SHA_OR_REVIEW_STATE_INVALID"):
                audit(report,frames,out,scout)

    def test_forged_freeze_window_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            report,frames,out,scout=make_case(root)
            data=json.loads(report.read_text())
            data["five_review_shots"][0]["pre_freeze_window_pts"]["start_pts"]+=50
            report.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,"SOURCE_FREEZE_PTS_WINDOW_MISMATCH"):
                audit(report,frames,out,scout)


if __name__=="__main__":
    unittest.main()
