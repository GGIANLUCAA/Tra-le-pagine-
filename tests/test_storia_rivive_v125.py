"""V125: zero-credit source-motion audit regression (SHA, true PTS, 5 regions).

Tests are synthetic fixtures; only the separate GitHub archival audit decodes
the actual 1920 cotton documentary. Never claim rights or video approval.
"""
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from PIL import Image
from src.storia_rivive_adaptive_sampling_v124 import sha256_file
from src.storia_rivive_frame_rank_v101 import pre_freeze_window_evidence
from src.storia_rivive_v125_real_motion_audit import audit

TIMES=[1.65,5.0,9.0,13.0,17.0]
CUTS=[3.0,7.0,11.0,15.0]


def fixture(path):
    path=Path(path)
    film=path/"film.mp4"
    # Bytes contain a synthetic moving archive analog; no historic footage.
    if shutil.which("ffmpeg"):
        subprocess.run(["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y",
                        "-f","lavfi","-i","testsrc2=size=640x360:rate=12:duration=20",
                        "-c:v","mpeg4","-q:v","8",str(film)],check=True,timeout=60)
    else:
        film.write_bytes(b"offline film fixture, not a real movie")
    digest=sha256_file(film)
    folder=path/"adaptive"
    frames=folder/"original_frames"
    frames.mkdir(parents=True)
    provenance=[]
    candidates=[]
    for i,time_s in enumerate(TIMES):
        name=f"frame_{i:02d}.png"
        Image.new("RGB",(720,1280),(100+i*4,96,92)).save(frames/name)
        src={"filename":name,"sha256":sha256_file(frames/name),
             "source_pts":round(time_s*1000),"source_pts_time_s":time_s,
             "source_time_base":"1/1000","source_pts_logged_from_decode":True,
             "shot_candidate_segment_index":i}
        provenance.append(src)
        window=pre_freeze_window_evidence(src,CUTS)
        assert window["eligible"],window
        candidates.append({
            "filename":name,"source_visual_quality_score":.81+i*.02,
            "source_native_detail_sufficient":True,
            "source_picture_content_eligible":True,
            "pre_freeze_window_viable":True,
            "pre_freeze_window_pts":{k:window[k] for k in ("start_pts","freeze_pts","time_base")},
            "shot_candidate_segment_index":i
        })
    report={"status":"REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW",
            "adaptive_research_version":"V124_UNAPPROVED_LONG_SEGMENT_TARGET_SAMPLING",
            "original_sha256":digest,"duration_s":20.,
            "frame_provenance_source_sha256":digest,
            "frame_provenance":provenance,
            "shot_boundary_analysis":{"version":"V113_FFMPEG_SCENE_CANDIDATES",
                "status":"FIVE_SEGMENTS_POSSIBLE_REVIEW_REQUIRED",
                "source_sha256":digest,"cut_candidate_times_s":CUTS}}
    rank={"status":"FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW",
          "adaptive_frame_source_sha256":digest,
          "adaptive_review_only_not_camera_approval":True,
          "all_candidates":candidates}
    scout=folder/"SCOUT_REPORT.json";rank_file=folder/"ADAPTIVE_RANK_V124.json"
    scout.write_text(json.dumps(report),encoding="utf-8")
    rank_file.write_text(json.dumps(rank),encoding="utf-8")
    return film, scout, rank_file, folder/"MOTION_AUDIT_V125.json"


def mocked_motion(film, digest, start, freeze, base):
    return {"status":"MOTION_EVIDENCE_PASS","reason":"SYNTHETIC_FIXTURE",
            "motion_verified":True,"sample_count":11,
            "changed_pairs":5,"max_spatial_pixel_delta":14.0}


class V125Tests(unittest.TestCase):
    def test_valid_five_regions_still_not_an_approval(self):
        with tempfile.TemporaryDirectory() as root:
            args=fixture(root)
            result=audit(*args,inspector=mocked_motion)
            self.assertEqual(result["status"],"V125_FIVE_MOVING_PHOTO_REGIONS_REVIEW_REQUIRED")
            self.assertEqual(result["source_motion_candidates_pass"],5)
            self.assertEqual(len(result["five_review_shots"]),5)
            self.assertEqual({x["timeline_region"] for x in result["five_review_shots"]},
                             set(range(5)))
            self.assertTrue(all(not x["human_camera_shot_approval"]
                                for x in result["five_review_shots"]))
            self.assertFalse(result["italian_rights_verified"])
            self.assertEqual(result["paid_api_calls"],0)
            self.assertFalse(result["published"])
            self.assertTrue(args[-1].is_file())

    def test_failed_motion_in_one_region_blocks_all_five(self):
        with tempfile.TemporaryDirectory() as root:
            args=fixture(root)
            def reject_one(film,digest,start,freeze,base):
                if freeze==9000:
                    return {"status":"BLOCKED","reason":"SOURCE_WINDOW_STATIC_OR_TOO_LITTLE_MOTION",
                            "motion_verified":False,"sample_count":11}
                return mocked_motion(film,digest,start,freeze,base)
            result=audit(*args,inspector=reject_one)
            self.assertEqual(result["status"],"V125_MOTION_SOURCE_SELECTION_BLOCKED")
            self.assertEqual(len(result["five_review_shots"]),0)
            self.assertEqual(result["source_motion_candidates_pass"],4)
            self.assertIn("SOURCE_WINDOW_STATIC", [x["reason"] for x in result["motion_audit"]])

    def test_altered_original_frame_blocks_before_any_motion(self):
        with tempfile.TemporaryDirectory() as root:
            args=fixture(root)
            frame=args[1].parent/"original_frames"/"frame_02.png"
            frame.write_bytes(b"tampered source frame")
            def do_not_call(*args):
                self.fail("source motion should not decode with altered PNG")
            with self.assertRaisesRegex(ValueError,"ORIGINAL_FRAME_BYTES_CHANGED"):
                audit(*args,inspector=do_not_call)

    def test_altered_film_blocks_before_any_motion(self):
        with tempfile.TemporaryDirectory() as root:
            args=fixture(root)
            with args[0].open("ab") as f:
                f.write(b"appended bytes")
            def do_not_call(*args):
                self.fail("film mismatch cannot reach motion")
            with self.assertRaisesRegex(ValueError,"ORIGINAL_SOURCE_SHA256_MISMATCH"):
                audit(*args,inspector=do_not_call)

    def test_forged_pts_window_blocks_before_any_motion(self):
        with tempfile.TemporaryDirectory() as root:
            film,scout,rank_file,out=fixture(root)
            data=json.loads(rank_file.read_text(encoding="utf-8"))
            data["all_candidates"][1]["pre_freeze_window_pts"]["freeze_pts"]+=100
            rank_file.write_text(json.dumps(data),encoding="utf-8")
            def do_not_call(*args):
                self.fail("forged PTS must block before any FFmpeg")
            with self.assertRaisesRegex(ValueError,"RANKED_SOURCE_PTS_WINDOW_TAMPERED"):
                audit(film,scout,rank_file,out,inspector=do_not_call)

    @unittest.skipUnless(shutil.which("ffmpeg"),"FFmpeg required")
    def test_five_real_decoded_windows_in_synthetic_motion_mp4(self):
        with tempfile.TemporaryDirectory() as root:
            args=fixture(root)
            result=audit(*args) # actual FFmpeg spatial pixel residuals on synthetic testsrc2
            self.assertEqual(result["source_photo_candidates_tested"],5)
            self.assertEqual(result["status"],"V125_FIVE_MOVING_PHOTO_REGIONS_REVIEW_REQUIRED",result)
            self.assertEqual(result["source_motion_candidates_pass"],5)


if __name__=="__main__":
    unittest.main()
