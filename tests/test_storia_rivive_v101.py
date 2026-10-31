#!/usr/bin/env python3
"""Offline V101 tests; no remote network or secrets."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]
def load(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/"src"/(name+".py"))
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

auto=load("storia_rivive_autopilot_v101")
flag=load("storia_rivive_flag_title_v101")
scout=load("storia_rivive_scout_v101")
frame_rank=load("storia_rivive_frame_rank_v101")
i2i=load("storia_rivive_i2i_prepare_v102")
shot=load("storia_rivive_shot_boundaries_v113")
def bind_scout_frame_hashes(folder):
    """Synthetic V112 provenance fixture; never a claim of real film decoding."""
    report_path=folder/"SCOUT_REPORT.json"
    report=json.loads(report_path.read_text())
    report["frame_provenance_source_sha256"]=i2i.sha(folder/"ORIGINAL_ARCHIVE.webm")
    report["frame_provenance_version"]="V112_SOURCE_PTS_FROM_FFMPEG_SHOWINFO"
    report["frame_provenance"]=[
        {"filename":p.name,"sha256":i2i.sha(p),"extraction_index":idx,
         "source_pts":idx*1000,"source_pts_time_s":float(idx),
         "source_time_base":"1/1000","source_pts_logged_from_decode":True,
         "exact_source_timecode_verified":False,"historical_camera_shot_verified":False}
        for idx,p in enumerate(sorted((folder/"original_frames").glob("frame_*.png")))
    ]
    # Synthetic boundary fixtures test the guard, NOT authentic camera-shot detection.
    cuts=[0.5,1.5,2.5,3.5]
    report["shot_boundary_analysis"]={
        "version":"V113_FFMPEG_SCENE_CANDIDATES",
        "source_sha256":report["frame_provenance_source_sha256"],
        "status":"FIVE_SEGMENTS_POSSIBLE_REVIEW_REQUIRED",
        "cut_candidate_times_s":cuts,
        "historical_camera_shots_verified":False}
    for entry in report["frame_provenance"]:
        entry["shot_candidate_segment_index"]=shot.segment_for_time(entry["source_pts_time_s"],cuts)
    report_path.write_text(json.dumps(report))

PROFILE={"format":"storia_rivive","schedule_hours":3,"paid_calls_allowed":False,"social_autopublish":False}
BANK={"candidates":[
    {"id":"paris_swim_1918","source_page":"https://commons.wikimedia.org/wiki/File:Example.webm","license":"CC0_as_declared","year":1918},
    {"id":"paris_train_1918","source_page":"https://commons.wikimedia.org/wiki/File:Example2.webm","license":"CC0_as_declared","year":1918}
]}

class V101Tests(unittest.TestCase):
    def test_v133_skips_rejected_source_without_repeating_research(self):
        bank={"candidates":[*BANK["candidates"], {
            "id":"france_cotton_mill_1920",
            "source_page":"https://commons.wikimedia.org/wiki/File:Filature_et_Tissage_du_coton_(1920).webm",
            "license":"PDM"}]}
        registry=json.loads((ROOT/"config"/"storia_rivive_v133_rejected_films.json").read_text())
        # This V133 fixture deliberately tests only the original cotton source.
        registry["rejected"]=[x for x in registry["rejected"] if x["candidate_id"]=="france_cotton_mill_1920"]
        for hour in (0,3,6,9,12,15,18,21):
            order=auto.build_work_order(bank,f"2026-10-31T{hour:02d}:00:00Z",PROFILE,registry)
            self.assertNotEqual(order["episode_id"],"france_cotton_mill_1920")
            self.assertEqual(order["excluded_sha_bound_sources"],["france_cotton_mill_1920"])
            self.assertFalse(order["skip_source_acquisition"])
            self.assertFalse(order["paid_api_call_permitted"])

    def test_v133_all_rejected_skips_cleanly_and_never_approves(self):
        candidate={"id":"france_cotton_mill_1920",
            "source_page":"https://commons.wikimedia.org/wiki/File:Filature_et_Tissage_du_coton_(1920).webm"}
        registry=json.loads((ROOT/"config"/"storia_rivive_v133_rejected_films.json").read_text())
        # This V133 fixture deliberately tests only the original cotton source.
        registry["rejected"]=[x for x in registry["rejected"] if x["candidate_id"]=="france_cotton_mill_1920"]
        order=auto.build_work_order({"candidates":[candidate]},
                                   "2026-10-31T09:00:00Z",PROFILE,registry)
        self.assertEqual(order["status"],"SOURCE_REJECTED_ALL_KNOWN")
        self.assertEqual(order["episode_id"],"no_eligible_source")
        self.assertIsNone(order["source_page"])
        self.assertTrue(order["skip_source_acquisition"])
        self.assertFalse(order["video_completed"])
        self.assertFalse(order["publish_permitted"])

    def test_v133_stale_or_forged_rejection_is_fail_closed(self):
        bank={"candidates":[{"id":"france_cotton_mill_1920",
            "source_page":"https://commons.wikimedia.org/wiki/File:Changed.webm"}]}
        registry=json.loads((ROOT/"config"/"storia_rivive_v133_rejected_films.json").read_text())
        # This V133 fixture deliberately tests only the original cotton source.
        registry["rejected"]=[x for x in registry["rejected"] if x["candidate_id"]=="france_cotton_mill_1920"]
        with self.assertRaisesRegex(ValueError,"STALE_REJECTION"):
            auto.build_work_order(bank,"2026-10-31T09:00:00Z",PROFILE,registry)
        bank["candidates"][0]["source_page"]=registry["rejected"][0]["source_page"]
        registry["rejected"][0]["film_sha256"]="not-verified"
        with self.assertRaisesRegex(ValueError,"REJECTION_EVIDENCE_INVALID"):
            auto.build_work_order(bank,"2026-10-31T09:00:00Z",PROFILE,registry)

    def test_v133_duplicate_and_missing_rejection_evidence_blocked(self):
        bank={"candidates":[{"id":"france_cotton_mill_1920",
            "source_page":"https://commons.wikimedia.org/wiki/File:Filature_et_Tissage_du_coton_(1920).webm"}]}
        registry=json.loads((ROOT/"config"/"storia_rivive_v133_rejected_films.json").read_text())
        # This V133 fixture deliberately tests only the original cotton source.
        registry["rejected"]=[x for x in registry["rejected"] if x["candidate_id"]=="france_cotton_mill_1920"]
        registry["rejected"].append(dict(registry["rejected"][0]))
        with self.assertRaisesRegex(ValueError,"UNKNOWN_OR_DUPLICATE"):
            auto.build_work_order(bank,"2026-10-31T09:00:00Z",PROFILE,registry)
        registry["rejected"].pop()
        registry["rejected"][0]["evidence_url"]="https://example.com/not-a-run"
        with self.assertRaisesRegex(ValueError,"REJECTION_EVIDENCE_INVALID"):
            auto.build_work_order(bank,"2026-10-31T09:00:00Z",PROFILE,registry)

    def test_cycle_is_stable(self):
        a=auto.build_work_order(BANK,"2026-10-30T15:01:00Z",PROFILE)
        b=auto.build_work_order(BANK,"2026-10-30T17:59:59Z",PROFILE)
        self.assertEqual(a["cycle_id"],b["cycle_id"])
        self.assertEqual(a["episode_id"],b["episode_id"])
    def test_no_fictional_approval(self):
        a=auto.build_work_order(BANK,"2026-10-30T15:00:00Z",PROFILE)
        self.assertFalse(a["human_approved"])
        self.assertFalse(a["publish_permitted"])
        self.assertEqual(a["credits_spent"],0)
        self.assertTrue(a["blocking_issues"])
    def test_paid_enabled_is_rejected(self):
        with self.assertRaises(ValueError):
            auto.build_work_order(BANK,"2026-10-30T15:00:00Z",{**PROFILE,"paid_calls_allowed":True})
    def test_source_host_allowlist(self):
        x=auto.candidate_issues({"source_page":"https://untrusted.invalid/film.webm"})
        self.assertIn("SOURCE_PAGE_NOT_ALLOWLISTED",x)
        with self.assertRaises(ValueError):scout.metadata("https://untrusted.invalid/file.webm")
    def test_unknown_historical_flag_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                flag.produce({"flag":"US","place":"NEW YORK","year":1906},str(Path(temp)/"bad.png"))
    def test_french_tricolor_render(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"title.png"
            flag.produce({"flag":"FR","place":"PARIS","year":1918},str(p))
            image=Image.open(p)
            self.assertEqual(image.size,(720,1280))
            self.assertEqual(image.getpixel((52,65))[:3],(0,35,149))
            self.assertEqual(image.getpixel((10,10))[3],0)
    def test_quality_rank_does_not_forge_approved_photos(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as temp:
            for i in range(12):
                im=Image.new("RGB",(1280,720),(40+i*5,75+i*3,125))
                im.save(Path(temp)/("frame_%02d.png"%i))
            result=frame_rank.rank(temp)
            self.assertEqual(len(result["preselected"]),5)
            self.assertEqual(result["approved_restored_photos"],0)
            self.assertTrue(all(x["approved_for_i2i"] is False for x in result["preselected"]))
            self.assertTrue(all(x["source_native_detail_sufficient"] for x in result["preselected"]))
    def test_rank_rejects_low_detail_480p_before_i2i(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as temp:
            for i in range(12):
                Image.new("RGB",(720,480),(40+i*5,70,100)).save(
                    Path(temp)/("frame_%02d.png"%i))
            result=frame_rank.rank(temp)
            self.assertEqual(result["status"],"SOURCE_NATIVE_DETAIL_INSUFFICIENT_FOR_FIVE_SHOTS")
            self.assertEqual(result["preselected"],[])
            self.assertEqual(result["eligible_native_detail_frames"],0)

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"),"FFmpeg required")
    def test_scout_pts_are_actual_redecodable_source_frames(self):
        """A real synthetic VIDEO decode must reproduce a sampled PNG by PTS."""
        from PIL import Image, ImageChops
        with tempfile.TemporaryDirectory() as temp:
            d=Path(temp)
            film=d/"test_original.mp4"
            frames=d/"original_frames";frames.mkdir()
            subprocess.run([
                "ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y",
                "-f","lavfi","-i","testsrc2=size=1280x720:rate=6:duration=13",
                "-c:v","mpeg4","-q:v","6",str(film)
            ],check=True,timeout=80)
            provenance=scout.extract_pts_locked_frames(film,frames,13.0)
            self.assertEqual(len(provenance),12)
            self.assertEqual([x["extraction_index"] for x in provenance],list(range(12)))
            self.assertTrue(all(x["source_pts_logged_from_decode"] for x in provenance))
            self.assertTrue(all(a["source_pts_time_s"]<b["source_pts_time_s"]
                                for a,b in zip(provenance,provenance[1:])))
            self.assertTrue(all(not x["exact_source_timecode_verified"] for x in provenance))
            selected=provenance[6]
            independently_decoded=d/"redecoded.png"
            subprocess.run([
                "ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y",
                "-i",str(film),"-vf",f"select='eq(pts,{selected['source_pts']})'",
                "-fps_mode","vfr","-frames:v","1",str(independently_decoded)
            ],check=True,timeout=80)
            with Image.open(frames/selected["filename"]) as a,Image.open(independently_decoded) as b:
                self.assertIsNone(ImageChops.difference(a.convert("RGB"),b.convert("RGB")).getbbox())
            self.assertEqual(selected["sha256"],i2i.sha(frames/selected["filename"]))


    def test_v113_rank_selects_one_frame_per_detected_segment(self):
        from PIL import Image,ImageDraw
        with tempfile.TemporaryDirectory() as temp:
            d=Path(temp);frames=d/"original_frames";frames.mkdir()
            for i in range(12):
                im=Image.new("RGB",(1280,720),(85,85,85))
                ImageDraw.Draw(im).rectangle((i*80,80,i*80+100,630),fill=(220,220,220))
                im.save(frames/("frame_%02d.png"%i))
            def report(segments):
                cuts=[2.0,4.0,6.0,8.0,10.0]
                # Every synthetic freeze is >=1.3s into its proposed segment.
                times=[1.3+2*(i//2)+0.5*(i%2) for i in range(12)]
                (d/"SCOUT_REPORT.json").write_text(json.dumps({
                    "shot_boundary_analysis":{"version":"V113_FFMPEG_SCENE_CANDIDATES",
                        "status":"FIVE_SEGMENTS_POSSIBLE_REVIEW_REQUIRED",
                        "cut_candidate_times_s":cuts},
                    "frame_provenance":[{"filename":"frame_%02d.png"%i,
                        "source_pts":round(times[i]*1000),
                        "source_pts_time_s":times[i],"source_time_base":"1/1000",
                        "shot_candidate_segment_index":segment}
                        for i,segment in enumerate(segments)]}))
            report([i//2 for i in range(12)])
            good=frame_rank.rank(frames)
            self.assertEqual(len(good["preselected"]),5)
            self.assertEqual(len(set(good["selected_shot_candidate_segments"])),5)
            self.assertFalse(good["preselected"][0]["historical_shot_distinctness_verified"])
            report([0]*12)
            blocked=frame_rank.rank(frames)
            self.assertEqual(blocked["status"],"INSUFFICIENT_PRE_FREEZE_SOURCE_WINDOWS")
            self.assertEqual(blocked["preselected"],[])

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"),"FFmpeg required")
    def test_v113_cut_candidates_come_from_real_video_not_frame_differences(self):
        """Five hard-cut segments versus one continuous shot, decoded from actual MP4."""
        with tempfile.TemporaryDirectory() as temp:
            d=Path(temp)
            def encode(colors,filename):
                cmd=["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y"]
                for color in colors:
                    cmd+=["-f","lavfi","-i",f"color=c={color}:s=640x360:r=6:d=2"]
                cmd+=["-filter_complex",
                      "".join(f"[{i}:v]" for i in range(len(colors)))+
                      f"concat=n={len(colors)}:v=1:a=0[v]",
                      "-map","[v]","-c:v","mpeg4","-q:v","4",str(d/filename)]
                subprocess.run(cmd,check=True,timeout=70)
                return d/filename
            cuts=encode(["black","white","black","white","black"],"five_shots.mp4")
            result=shot.detect_cut_candidates(cuts,10.0,"a"*64)
            self.assertEqual(result["status"],"FIVE_SEGMENTS_POSSIBLE_REVIEW_REQUIRED")
            self.assertEqual(result["cut_candidate_times_s"],[2.0,4.0,6.0,8.0])
            self.assertFalse(result["historical_camera_shots_verified"])
            single=encode(["black"],"single_shot.mp4")
            blocked=shot.detect_cut_candidates(single,2.0,"b"*64)
            self.assertEqual(blocked["status"],"INSUFFICIENT_CUT_CANDIDATES")
            self.assertEqual(blocked["cut_candidate_count"],0)

    def test_v113_i2i_rejects_five_distinct_pngs_from_only_four_segments(self):
        from PIL import Image,ImageDraw
        with tempfile.TemporaryDirectory() as temp:
            d=Path(temp);(d/"original_frames").mkdir()
            (d/"ORIGINAL_ARCHIVE.webm").write_bytes(b"synthetic fixture, not a real film")
            (d/"SCOUT_REPORT.json").write_text(json.dumps({
                "status":"REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW",
                "original_sha256":i2i.sha(d/"ORIGINAL_ARCHIVE.webm")}))
            for i in range(1,6):
                im=Image.new("RGB",(1280,720),(35,35,35))
                ImageDraw.Draw(im).rectangle((i*190,80,i*190+110,640),fill=(225,225,225))
                im.save(d/"original_frames"/("frame_%02d.png"%i))
            bind_scout_frame_hashes(d)
            report_path=d/"SCOUT_REPORT.json"
            report=json.loads(report_path.read_text())
            report["shot_boundary_analysis"]["cut_candidate_times_s"]=[0.5,1.5,2.5,9.5]
            for entry in report["frame_provenance"]:
                entry["shot_candidate_segment_index"]=shot.segment_for_time(
                    entry["source_pts_time_s"],[0.5,1.5,2.5,9.5])
            report_path.write_text(json.dumps(report))
            order={"contract":"LA_STORIA_RIVIVE_V101_SAFE_AUTOPILOT",
                   "cycle_id":"storia-test-v113","episode_id":"synthetic_shots",
                   "paid_api_call_permitted":False,"publish_permitted":False,
                   "blocking_issues":[]}
            selection={"status":"FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW",
                       "preselected":[{"filename":"frame_%02d.png"%i} for i in range(1,6)]}
            with self.assertRaisesRegex(ValueError,"FIVE_DISTINCT_SHOT_CANDIDATES_NOT_FOUND"):
                i2i.build(order,selection,d)
            report["shot_boundary_analysis"]["source_sha256"]="0"*64
            report_path.write_text(json.dumps(report))
            with self.assertRaisesRegex(ValueError,"SHOT_BOUNDARY_FILM_SHA_MISMATCH"):
                i2i.build(order,selection,d)
            report.pop("shot_boundary_analysis")
            report_path.write_text(json.dumps(report))
            with self.assertRaisesRegex(ValueError,"SHOT_BOUNDARY_EVIDENCE_MISSING_OR_LEGACY"):
                i2i.build(order,selection,d)

    def test_v114_pts_clock_rejects_forged_freeze_time(self):
        # FFmpeg PTS 90 at time_base 1001/30000 is 3.003s.
        self.assertTrue(i2i.verify_pts_timebase_consistency(90,3.003,"1001/30000"))
        self.assertTrue(i2i.verify_pts_timebase_consistency(90,3.00300004,"1001/30000"))
        with self.assertRaisesRegex(ValueError,"SOURCE_PTS_TIME_BASE_MISMATCH"):
            i2i.verify_pts_timebase_consistency(90,3.0,"1001/30000")
        with self.assertRaisesRegex(ValueError,"SOURCE_PTS_CLOCK_INVALID"):
            i2i.verify_pts_timebase_consistency(90,3.003,"0/1000")
        with self.assertRaisesRegex(ValueError,"SOURCE_PTS_CLOCK_INVALID"):
            i2i.verify_pts_timebase_consistency(True,3.003,"1001/30000")

    def test_i2i_rejects_duplicate_or_forged_pts_evidence(self):
        from PIL import Image,ImageDraw
        with tempfile.TemporaryDirectory() as temp:
            d=Path(temp);(d/"original_frames").mkdir()
            (d/"ORIGINAL_ARCHIVE.webm").write_bytes(b"synthetic test film")
            (d/"SCOUT_REPORT.json").write_text(json.dumps({
                "status":"REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW",
                "original_sha256":i2i.sha(d/"ORIGINAL_ARCHIVE.webm")}))
            for i in range(1,6):
                im=Image.new("RGB",(1280,720),(35,35,35))
                ImageDraw.Draw(im).rectangle((i*170,80,i*170+130,630),fill=(230,230,230))
                im.save(d/"original_frames"/("frame_%02d.png"%i))
            bind_scout_frame_hashes(d)
            order={"contract":"LA_STORIA_RIVIVE_V101_SAFE_AUTOPILOT",
                   "cycle_id":"storia-test-pts","episode_id":"test_pts",
                   "paid_api_call_permitted":False,"publish_permitted":False,
                   "blocking_issues":[]}
            selection={"status":"FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW",
                       "preselected":[{"filename":"frame_%02d.png"%i} for i in range(1,6)]}
            report_path=d/"SCOUT_REPORT.json"
            report=json.loads(report_path.read_text())
            report["frame_provenance"][2]["source_pts"]=report["frame_provenance"][1]["source_pts"]
            report_path.write_text(json.dumps(report))
            with self.assertRaisesRegex(ValueError,"SELECTED_SOURCE_PTS_DUPLICATE_OR_NON_MONOTONIC"):
                i2i.build(order,selection,d)
            report["frame_provenance"][2]["source_pts"]=2000
            report["frame_provenance"][2]["source_pts_logged_from_decode"]=False
            report_path.write_text(json.dumps(report))
            with self.assertRaisesRegex(ValueError,"SOURCE_PTS_PROVENANCE_INVALID"):
                i2i.build(order,selection,d)
            report["frame_provenance"][2]["source_pts_logged_from_decode"]=True
            # Tamper the displayed timestamp but keep the PNG SHA and cut segment.
            # V113 segment membership alone would accept 2.4s in the same segment.
            report["frame_provenance"][2]["source_pts_time_s"]=2.4
            report_path.write_text(json.dumps(report))
            with self.assertRaisesRegex(ValueError,"SOURCE_PTS_TIME_BASE_MISMATCH"):
                i2i.build(order,selection,d)
            report["frame_provenance"][2]["source_pts_time_s"]=2.0
            report["frame_provenance_version"]="V111_EXTRACTED_FRAME_SHA256"
            report_path.write_text(json.dumps(report))
            with self.assertRaisesRegex(ValueError,"SOURCE_PTS_PROVENANCE_VERSION_MISSING_OR_LEGACY"):
                i2i.build(order,selection,d)

    def test_i2i_manifest_locks_five_real_source_frames(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as temp:
            d=Path(temp);(d/"original_frames").mkdir()
            (d/"ORIGINAL_ARCHIVE.webm").write_bytes(b"synthetic test only")
            (d/"SCOUT_REPORT.json").write_text(json.dumps({
                "status":"REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW",
                "original_sha256":i2i.sha(d/"ORIGINAL_ARCHIVE.webm")}))
            from PIL import ImageDraw
            for i in range(1,6):
                im=Image.new("RGB",(1280,720),(40,40,40))
                draw=ImageDraw.Draw(im)
                x=80+(i-1)*230
                draw.rectangle((x,70,x+150,650),fill=(220,220,220))
                draw.ellipse((110,180+(i-1)*60,450,400+(i-1)*60),fill=(110,110,110))
                im.save(d/"original_frames"/("frame_%02d.png"%i))
            bind_scout_frame_hashes(d)
            order={"contract":"LA_STORIA_RIVIVE_V101_SAFE_AUTOPILOT",
                   "cycle_id":"storia-20261030-1200","episode_id":"beirut_1919_street",
                   "paid_api_call_permitted":False,"publish_permitted":False,
                   "blocking_issues":[]}
            selection={"status":"FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW",
                       "preselected":[{"filename":"frame_%02d.png"%i} for i in range(1,6)]}
            result=i2i.build(order,selection,d)
            self.assertEqual(len(result["original_frame_jobs"]),5)
            self.assertEqual(result["photos_generated"],0)
            self.assertEqual(result["provider_requests_sent"],0)
            self.assertTrue(all(x["source_sha256"] and x["request_sent"] is False for x in result["original_frame_jobs"]))
            self.assertEqual(result["source_video_sha256"],i2i.sha(d/"ORIGINAL_ARCHIVE.webm"))
            self.assertEqual(result["visual_duplicate_guard"]["status"],
                             "NO_OBVIOUS_VISUAL_DUPLICATES_REVIEW_REQUIRED")
            self.assertFalse(result["historical_shot_distinctness_verified"])
            self.assertEqual(result["original_frame_jobs"][0]["source_pts_time_s"],0.0)
            self.assertTrue(result["original_frame_jobs"][0]["source_pts_logged_from_decode"])

    def test_i2i_blocks_exposure_variants_of_same_historical_shot(self):
        from PIL import Image,ImageDraw,ImageEnhance
        with tempfile.TemporaryDirectory() as temp:
            d=Path(temp);(d/"original_frames").mkdir()
            (d/"ORIGINAL_ARCHIVE.webm").write_bytes(b"synthetic test only")
            (d/"SCOUT_REPORT.json").write_text(json.dumps({
                "status":"REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW",
                "original_sha256":i2i.sha(d/"ORIGINAL_ARCHIVE.webm")}))
            original=Image.new("RGB",(1280,720),(45,45,45))
            draw=ImageDraw.Draw(original)
            draw.ellipse((100,80,640,650),fill=(200,200,200))
            draw.rectangle((710,100,1180,510),fill=(100,100,100))
            for i in range(1,6):
                ImageEnhance.Brightness(original).enhance(0.95+i*.02).save(
                    d/"original_frames"/("frame_%02d.png"%i))
            bind_scout_frame_hashes(d)
            order={"contract":"LA_STORIA_RIVIVE_V101_SAFE_AUTOPILOT",
                   "cycle_id":"storia-20261030-1200","episode_id":"beirut_1919_street",
                   "paid_api_call_permitted":False,"publish_permitted":False,
                   "blocking_issues":[]}
            selection={"status":"FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW",
                       "preselected":[{"filename":"frame_%02d.png"%i} for i in range(1,6)]}
            with self.assertRaisesRegex(ValueError,"VISUAL_NEAR_DUPLICATE_SOURCE_FRAMES"):
                i2i.build(order,selection,d)

    def test_i2i_rejects_source_frame_modified_after_scout_hash(self):
        from PIL import Image, ImageDraw
        with tempfile.TemporaryDirectory() as temp:
            d=Path(temp);(d/"original_frames").mkdir()
            (d/"ORIGINAL_ARCHIVE.webm").write_bytes(b"synthetic film bytes")
            (d/"SCOUT_REPORT.json").write_text(json.dumps({
                "status":"REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW",
                "original_sha256":i2i.sha(d/"ORIGINAL_ARCHIVE.webm")}))
            for i in range(1,6):
                im=Image.new("RGB",(1280,720),(35,35,35))
                ImageDraw.Draw(im).rectangle((i*170,60,i*170+120,650),fill=(200,200,200))
                im.save(d/"original_frames"/("frame_%02d.png"%i))
            bind_scout_frame_hashes(d)
            Image.new("RGB",(1280,720),(123,123,123)).save(
                d/"original_frames"/"frame_03.png")
            order={"contract":"LA_STORIA_RIVIVE_V101_SAFE_AUTOPILOT",
                   "cycle_id":"storia-20261030-1200","episode_id":"test_film",
                   "paid_api_call_permitted":False,"publish_permitted":False,
                   "blocking_issues":[]}
            selection={"status":"FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW",
                       "preselected":[{"filename":"frame_%02d.png"%i} for i in range(1,6)]}
            with self.assertRaisesRegex(ValueError,"SOURCE_FRAME_SHA_MISMATCH_WITH_SCOUT"):
                i2i.build(order,selection,d)

    def test_i2i_rejects_legacy_scout_without_frame_provenance(self):
        with tempfile.TemporaryDirectory() as temp:
            d=Path(temp)
            (d/"ORIGINAL_ARCHIVE.webm").write_bytes(b"synthetic film bytes")
            (d/"SCOUT_REPORT.json").write_text(json.dumps({
                "status":"REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW",
                "original_sha256":i2i.sha(d/"ORIGINAL_ARCHIVE.webm")}))
            order={"contract":"LA_STORIA_RIVIVE_V101_SAFE_AUTOPILOT",
                   "cycle_id":"storia-20261030-1200","episode_id":"test_film",
                   "paid_api_call_permitted":False,"publish_permitted":False,
                   "blocking_issues":[]}
            selection={"status":"FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW",
                       "preselected":[{"filename":"frame_%02d.png"%i} for i in range(1,6)]}
            with self.assertRaisesRegex(ValueError,"FRAME_PROVENANCE_FILM_SHA_MISMATCH_OR_MISSING"):
                i2i.build(order,selection,d)

    def test_i2i_preflight_blocks_unverified_italian_rights(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError,"V101_SOURCE_PREFLIGHT_BLOCKED"):
                i2i.build({"contract":"LA_STORIA_RIVIVE_V101_SAFE_AUTOPILOT",
                    "paid_api_call_permitted":False,"publish_permitted":False,
                    "blocking_issues":["ITALY_AND_RESIDUAL_RIGHTS_NEED_REVIEW"]},
                    {"status":"FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW",
                     "preselected":[{"filename":"frame_%02d.png"%i} for i in range(1,6)]},
                    Path(temp))

    def test_i2i_preflight_blocks_480p_and_duplicate_bytes(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as temp:
            d=Path(temp);(d/"original_frames").mkdir()
            (d/"ORIGINAL_ARCHIVE.webm").write_bytes(b"synthetic test only")
            (d/"SCOUT_REPORT.json").write_text(json.dumps({
                "status":"REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW",
                "original_sha256":i2i.sha(d/"ORIGINAL_ARCHIVE.webm")}))
            order={"contract":"LA_STORIA_RIVIVE_V101_SAFE_AUTOPILOT",
                   "cycle_id":"storia-20261030-1200","episode_id":"beirut_1919_street",
                   "paid_api_call_permitted":False,"publish_permitted":False,
                   "blocking_issues":[]}
            selection={"status":"FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW",
                       "preselected":[{"filename":"frame_%02d.png"%i} for i in range(1,6)]}
            for i in range(1,6):
                Image.new("RGB",(720,480),(20*i,40,70)).save(d/"original_frames"/("frame_%02d.png"%i))
            bind_scout_frame_hashes(d)
            with self.assertRaisesRegex(ValueError,"SOURCE_NATIVE_DETAIL_INSUFFICIENT"):
                i2i.build(order,selection,d)
            for i in range(1,6):
                Image.new("RGB",(1280,720),(20,40,70)).save(d/"original_frames"/("frame_%02d.png"%i))
            bind_scout_frame_hashes(d)
            with self.assertRaisesRegex(ValueError,"DUPLICATE_SOURCE_FRAME_BYTES"):
                i2i.build(order,selection,d)
            (d/"SCOUT_REPORT.json").write_text(json.dumps({
                "status":"REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW",
                "original_sha256":"0"*64}))
            with self.assertRaisesRegex(ValueError,"SCOUT_FILM_SHA_MISMATCH"):
                i2i.build(order,selection,d)

    def test_i2i_manifest_blocks_missing_source_frame(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as temp:
            d=Path(temp);(d/"original_frames").mkdir()
            (d/"ORIGINAL_ARCHIVE.webm").write_bytes(b"synthetic test only")
            (d/"SCOUT_REPORT.json").write_text(json.dumps({
                "status":"REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW",
                "original_sha256":i2i.sha(d/"ORIGINAL_ARCHIVE.webm")}))
            for i in range(1,5):
                Image.new("RGB",(1280,720),(i*30,40,70)).save(
                    d/"original_frames"/("frame_%02d.png"%i))
            bind_scout_frame_hashes(d)
            with self.assertRaisesRegex(ValueError,"Missing original source frame"):
                i2i.build({"contract":"LA_STORIA_RIVIVE_V101_SAFE_AUTOPILOT",
                    "cycle_id":"storia-20261030-1200","episode_id":"beirut_1919_street",
                    "paid_api_call_permitted":False,"publish_permitted":False,
                    "blocking_issues":[]},
                    {"status":"FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW",
                     "preselected":[{"filename":"frame_%02d.png"%i} for i in range(1,6)]},d)

    def test_i2i_manifest_blocks_missing_preflight_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError,"V101_SOURCE_PREFLIGHT_MISSING"):
                i2i.build({"contract":"LA_STORIA_RIVIVE_V101_SAFE_AUTOPILOT",
                    "paid_api_call_permitted":False,"publish_permitted":False},
                    {"status":"FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW",
                     "preselected":[{"filename":"frame_%02d.png"%i} for i in range(1,6)]},Path(temp))
    def test_source_rights_not_self_approved(self):
        a=auto.build_work_order(BANK,"2026-10-30T15:00:00Z",PROFILE)
        self.assertIn("ITALY_AND_RESIDUAL_RIGHTS_NEED_REVIEW",a["blocking_issues"])

    def test_v138_real_audited_rejections_are_omitted_from_autopilot(self):
        """Three films failed real source audits: no silent return to bad footage."""
        catalog=json.loads((ROOT/"queue/storia_rivive_candidates_v58.json").read_text())
        registry=json.loads((ROOT/"config/storia_rivive_v133_rejected_films.json").read_text())
        expected={"france_cotton_mill_1920","white_house_1917_1921",
                  "versailles_treaty_1919"}
        self.assertEqual(auto.rejected_source_ids(catalog["candidates"],registry), expected)
        order=auto.build_work_order(catalog,"2026-10-31T12:00:00Z",PROFILE,registry)
        self.assertTrue(expected.issubset(set(order["excluded_sha_bound_sources"])))
        self.assertNotIn(order["episode_id"],expected)
        self.assertFalse(order["paid_api_call_permitted"])
        self.assertFalse(order["publish_permitted"])

    def test_v138_when_only_rejected_films_remain_skip_download(self):
        catalog=json.loads((ROOT/"queue/storia_rivive_candidates_v58.json").read_text())
        registry=json.loads((ROOT/"config/storia_rivive_v133_rejected_films.json").read_text())
        selected=[x for x in catalog["candidates"]
                  if x["id"] in {r["candidate_id"] for r in registry["rejected"]}]
        result=auto.build_work_order({"candidates":selected},
                                     "2026-10-31T12:00:00Z",PROFILE,registry)
        self.assertEqual(result["status"],"SOURCE_REJECTED_ALL_KNOWN")
        self.assertTrue(result["skip_source_acquisition"])
        self.assertFalse(result["video_completed"])
        self.assertFalse(result["human_approved"])

    def test_v138_rejection_needs_exact_validated_audit_status(self):
        catalog=json.loads((ROOT/"queue/storia_rivive_candidates_v58.json").read_text())
        registry=json.loads((ROOT/"config/storia_rivive_v133_rejected_films.json").read_text())
        for status in ("ERROR","SOURCE_RESEARCH_REVIEW_REQUIRED",
                       "SOURCE_REJECTED_V136", "", None):
            bad=json.loads(json.dumps(registry))
            bad["rejected"][-1]["audit_status"]=status
            with self.assertRaisesRegex(ValueError,"V133_REJECTION_EVIDENCE_INVALID"):
                auto.rejected_source_ids(catalog["candidates"],bad)

    def test_v138_rejection_is_bound_to_exact_candidate_page_and_sha(self):
        catalog=json.loads((ROOT/"queue/storia_rivive_candidates_v58.json").read_text())
        registry=json.loads((ROOT/"config/storia_rivive_v133_rejected_films.json").read_text())
        changed=json.loads(json.dumps(registry))
        changed["rejected"][-1]["film_sha256"]="not-verified"
        with self.assertRaisesRegex(ValueError,"V133_REJECTION_EVIDENCE_INVALID"):
            auto.rejected_source_ids(catalog["candidates"],changed)
        changed=json.loads(json.dumps(registry))
        changed["rejected"][-1]["source_page"]="https://commons.wikimedia.org/wiki/File:Some_other_film.webm"
        with self.assertRaisesRegex(ValueError,"V133_STALE_REJECTION_SOURCE_CHANGED"):
            auto.rejected_source_ids(catalog["candidates"],changed)

if __name__=="__main__":unittest.main()
