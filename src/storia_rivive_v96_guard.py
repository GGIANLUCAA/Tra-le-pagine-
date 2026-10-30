#!/usr/bin/env python3
"""La Storia Rivive V96 — fail-closed artistic/technical delivery gate.

Guardrail against the recurring V92/V95 defects: colorization-only photographs,
overlong stills, unrelated Vidu cut, 4+1 without a genuine fifth historical shot,
overlaid title covering subjects, and 'codec passed => final approved' fallacy.

Runs with no video provider credentials or paid services.
The human-review fields must be supplied from a REAL visual inspection.
It never asserts that a face looks real or historically faithful automatically.
"""
from __future__ import annotations
import argparse,hashlib,json,math,re
from pathlib import Path

HEX64=re.compile(r"^[0-9a-f]{64}$")
ID=re.compile(r"^[A-Za-z0-9_-]{8,}$")
TRUE=lambda x:x is True

def sha_ok(v):
    return isinstance(v,str) and bool(HEX64.fullmatch(v))

def inspect(data, actual_duration=None):
    failures=[]; warnings=[]
    def need(cond,code):
        if not cond:failures.append(code)
    if not isinstance(data,dict):
        return ["MANIFEST_IS_NOT_JSON_OBJECT"],[]
    need(data.get("format")=="storia_rivive","WRONG_OR_MISSING_HISTORY_FORMAT")
    need(data.get("quality_policy_version") in ("V94","V94+V96","V96"),"V96_QUALITY_POLICY_NOT_ENFORCED")
    # The V94 policy applies at the same time; the official combined manifest
    # keeps quality_policy_version=V94 and adds project_format=4classic_1vidu.
    # V91 actually invokes this V96 gate, so the check cannot be skipped via tag.
    need(data.get("project_format")=="4classic_1vidu","WRONG_FIVE_SCENE_PRESET")
    need(isinstance(data.get("episode_id"),str) and len(data["episode_id"])>=8,"UNIQUE_EPISODE_ID_MISSING")
    need(TRUE(data.get("copyright_italy_checked")),"TERRITORIAL_RIGHTS_REVIEW_PENDING")
    need(TRUE(data.get("source_visual_reference_compared")),"REAL_REFERENCE_QUALITY_NOT_COMPARED")
    need(TRUE(data.get("full_video_watched_with_audio")),"FINAL_FILM_NOT_WATCHED_WITH_AUDIO")
    need(TRUE(data.get("artistic_final_approved")),"HUMAN_ARTISTIC_FINAL_APPROVAL_NOT_PRESENT")
    need(TRUE(data.get("four_posts_cover_and_zip_verified")),"COMPLETE_SOCIAL_DELIVERY_NOT_CHECKED")
    need(TRUE(data.get("music_continuous_no_interruptions")),"MUSIC_CONTINUITY_UNVERIFIED")
    title=data.get("titles",{})
    if not isinstance(title,dict):title={}
    need(TRUE(title.get("faces_hands_main_objects_unobscured")),"TITLE_OBSCURES_PEOPLE_OR_OBJECTS")
    occupy=title.get("opaque_background_frame_fraction")
    need(type(occupy) in (int,float) and 0<=occupy<=.08,"TITLE_OPAQUE_BAND_EXCEEDS_8_PERCENT")
    need(type(title.get("appears_s")) in (int,float) and title.get("appears_s",999)<=1.75,
         "TITLE_VISIBLE_TOO_LATE")
    scenes=data.get("scenes")
    if not isinstance(scenes,list):
        return failures+["SCENE_BY_SCENE_TIMELINE_MISSING"],warnings
    need(len(scenes)==5,"EXACTLY_5_SCENES_REQUIRED")
    classics=[x for x in scenes if isinstance(x,dict) and x.get("kind")=="classic_photo"]
    videos=[x for x in scenes if isinstance(x,dict) and x.get("kind")=="vidu_motion"]
    need(len(classics)==4,"FOUR_REAL_SOURCE_TO_PHOTO_CYCLES_REQUIRED")
    need(len(videos)==1,"EXACTLY_ONE_REAL_VIDU_MOVING_SCENE_REQUIRED")
    distinct=set()
    intervals=[]
    for i,sc in enumerate(scenes):
        tag="SCENE_%d_"%(i+1)
        if not isinstance(sc,dict):
            need(False,tag+"INVALID");continue
        duration=sc.get("duration_s")
        start=sc.get("start_s")
        need(type(start) in (int,float) and type(duration) in (int,float) and 0<=start and duration>0,
             tag+"TIMING_INVALID")
        if type(start) in (int,float) and type(duration) in (int,float):
            intervals.append((float(start),float(start+duration),tag))
        source=sc.get("source")
        if not isinstance(source,dict):
            need(False,tag+"REAL_FILM_SOURCE_RECORD_MISSING");continue
        need(sha_ok(source.get("film_sha256")),tag+"ORIGINAL_FILM_SHA256_MISSING")
        need(sha_ok(source.get("exact_frame_sha256")),tag+"ORIGINAL_FREEZE_FRAME_SHA256_MISSING")
        ident=(source.get("film_sha256"),source.get("source_timecode_s"))
        need(ident not in distinct,tag+"REPEATS_PREVIOUS_SOURCE_SHOT")
        distinct.add(ident)
        need(type(source.get("source_timecode_s")) in (float,int),tag+"ORIGINAL_TIMECODE_MISSING")
        need(TRUE(source.get("shot_real_film_moving")) ,tag+"SOURCE_FILM_NOT_ACTUALLY_MOVING")
        need(TRUE(sc.get("original_people_objects_checked")),tag+"SOURCE_PEOPLE_OBJECTS_NOT_REVIEWED")
        if sc.get("kind")=="classic_photo":
            photo=sc.get("photo",{})
            if not isinstance(photo,dict):photo={}
            need(sha_ok(photo.get("color_photo_sha256")),tag+"EXACT_RESTORED_PHOTO_HASH_MISSING")
            need(photo.get("method")=="real_image_to_image_photographic_restoration",
                 tag+"DDCOLOR_ONLY_IS_NOT_PHOTOGRAPHIC_RESTORATION")
            need(TRUE(photo.get("same_real_source_frame_and_geometry")),tag+"PHOTO_GEOMETRY_NOT_SOURCE_LOCKED")
            need(TRUE(photo.get("human_photographic_quality_approved")),tag+"PHOTO_NOT_VISUALLY_APPROVED")
            need(TRUE(photo.get("all_faces_objects_identity_verified")),tag+"PEOPLE_OR_OBJECTS_UNVERIFIED")
            bw=sc.get("bw_motion_s");fade=sc.get("reveal_s");hold=sc.get("color_photo_hold_s")
            need(type(bw) in (int,float) and .45<=bw<=2.5,tag+"BW_MOVEMENT_TIME_NOT_DIRECTED")
            need(type(fade) in (int,float) and .12<=fade<=.95,tag+"RESTORATION_REVEAL_TIME_WRONG")
            need(type(hold) in (int,float) and .9<=hold<=3.05,tag+"PHOTO_HOLD_TOO_LONG_OR_TOO_SHORT")
            if type(duration) in (float,int) and all(type(v) in (float,int) for v in (bw,fade,hold)):
                need(abs(duration-(bw+fade+hold))<=.20,tag+"TIMELINE_DOES_NOT_MATCH_COMPONENTS")
            if sc.get("faces_visible") is True:
                need(TRUE(photo.get("eyes_skin_hair_and_expression_checked")),tag+"MODERN_PHOTO_FACE_DETAIL_UNVERIFIED")
                need(TRUE(photo.get("adjacent_archival_frames_identity_checked")),tag+"RESTORED_FACE_IDENTITY_UNVERIFIED")
                face=photo.get("useful_native_face_width_px")
                need(type(face) in (float,int) and face>=65 or TRUE(photo.get("documented_exception")),
                     tag+"NATIVE_FACE_HAS_TOO_FEW_SOURCE_PIXELS")
        elif sc.get("kind")=="vidu_motion":
            v=sc.get("vidu",{})
            if not isinstance(v,dict):v={}
            need(sha_ok(v.get("actual_videofile_sha256")),tag+"ACTUAL_VIDU_MP4_NOT_VERIFIED")
            need(isinstance(v.get("task_id"),str) and bool(ID.fullmatch(v.get("task_id",""))),
                 tag+"REAL_PAID_VIDU_TASK_NOT_VERIFIED")
            need(v.get("provider_state")=="success",tag+"VIDU_TASK_NOT_SUCCESS")
            need(v.get("paid_post_count")==1,tag+"EXACT_ONE_PAID_GENERATION_REQUIRED")
            need(type(v.get("credits_spent")) in (int,float) and 0<v.get("credits_spent",0)<=16,
                 tag+"UNVERIFIED_OR_EXCESSIVE_VIDU_SPEND")
            need(TRUE(v.get("start_real_original_bw_motion_present")),
                 tag+"VIDU_MUST_BEGIN_WITH_REAL_ORIGINAL_BW_FILM")
            src_bw=v.get("original_bw_motion_s")
            need(type(src_bw) in (float,int) and .45<=src_bw<=2.3,
                 tag+"VIDU_MISSING_SAME_SHOT_ARCHIVAL_BW_MOTION")
            generated=v.get("generated_live_video_s")
            need(type(generated) in (float,int) and 4.5<=generated<=5.5,
                 tag+"VIDU_MISSING_FIVE_SECONDS_OF_REAL_GENERATED_MOTION")
            if type(duration) in (int,float) and type(src_bw) in (int,float) and type(generated) in (int,float):
                need(abs(duration-src_bw-generated)<.24,tag+"VIDU_LENGTH_ORIGINAL_PLUS_AI_MISMATCH")
            need(type(v.get("color_reveal_by_s")) in (int,float) and v.get("color_reveal_by_s",999)<=1.15,
                 tag+"VIDU_COLOR_REVEAL_TOO_LATE")
            need(TRUE(v.get("real_motion_in_color_after_reveal")),
                 tag+"VIDU_IS_STILL_PHOTO_NOT_REAL_MOVING_COLOR_VIDEO")
            need(TRUE(v.get("first_vidu_frame_matches_same_real_source_shot")),
                 tag+"VIDU_ABRUPTLY_JUMPS_TO_A_DIFFERENT_SCENE")
            need(TRUE(v.get("no_people_or_object_morphs_reviewed")),
                 tag+"VIDU_ANATOMY_OR_OBJECT_REVIEW_MISSING")
            need(TRUE(v.get("photo_and_vidu_palette_visually_matched")),
                 tag+"ORANGE_PALETTE_OR_LIGHTING_MISMATCH_WITH_PHOTOS")
            need(TRUE(v.get("full_five_second_video_reviewed")),
                 tag+"FULL_VIDU_SHOT_NOT_WATCHED")
        else:
            failures.append(tag+"UNKNOWN_KIND")
    intervals.sort()
    for j,(begin,end,label) in enumerate(intervals):
        if j==0:need(abs(begin)<=.12,"SCENE_TIMELINE_DOES_NOT_START_AT_ZERO")
        elif abs(begin-intervals[j-1][1])>.15:failures.append("SCENE_TIMELINE_HAS_GAP_OVERLAP_AT_"+label)
    if intervals:
        last=intervals[-1][1]
        if actual_duration is not None:
            need(abs(last-actual_duration)<=.15,"VIDEO_DURATION_NOT_EQUAL_TO_FIVE_SCENE_TIMELINE")
        need(14<=last<=35,"VIDEO_DURATION_OUTSIDE_HISTORICAL_FORMAT")
    return failures,warnings

def inspect_video(path,scene_records):
    import cv2
    import numpy as np
    cap=cv2.VideoCapture(str(path))
    if not cap.isOpened():return [{"error":"VIDEO_NOT_DECODABLE"}]
    fps=cap.get(cv2.CAP_PROP_FPS);duration=cap.get(cv2.CAP_PROP_FRAME_COUNT)/max(fps,1)
    def read(t):
        cap.set(cv2.CAP_PROP_POS_MSEC,max(0,t)*1000)
        ok,f=cap.read()
        if not ok:return None
        return cv2.resize(f,(180,320))
    samples=[]
    for i,sc in enumerate(scene_records):
        if not isinstance(sc,dict):continue
        begin=sc.get("start_s");end=sc.get("duration_s")
        if type(begin) not in (float,int) or type(end) not in (float,int):continue
        d=float(begin+end)
        mid=begin+min(end*.66,end-.1)
        f=read(mid)
        if f is None:continue
        hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
        samples.append({"scene":i+1,"t_s":round(mid,2),"kind":sc.get("kind"),
                        "median_hsv_saturation":round(float(np.median(hsv[:,:,1])),2),
                        "colored_pixel_fraction":round(float(np.mean(hsv[:,:,1]>35)),3)})
    cap.release()
    return {"duration_s":duration,"scene_color_samples":samples,
            "note":"Saturation is a warning, NOT evidence of real photographic restoration or identical historical people."}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",required=True)
    p.add_argument("--video")
    p.add_argument("--report",required=True)
    a=p.parse_args()
    data=json.loads(Path(a.manifest).read_text(encoding="utf8"))
    duration=None
    if a.video:
        import cv2
        c=cv2.VideoCapture(a.video)
        if c.isOpened():duration=c.get(cv2.CAP_PROP_FRAME_COUNT)/max(c.get(cv2.CAP_PROP_FPS),1)
        c.release()
    failures,warnings=inspect(data,actual_duration=duration)
    evidence=inspect_video(a.video,data.get("scenes",[])) if a.video else {}
    report={"policy":"LaStoriaRivive-V96","passed":not failures,"failures":failures,
            "warnings":warnings,"observations":evidence,
            "no_paid_provider_calls":True,
            "note":"No video can be called finished solely because H264/AAC, saturation, or MP4 decoding passes. Human approval flags require actual visual review."}
    target=Path(a.report);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"passed":not failures,"failures":failures},ensure_ascii=False,indent=2))
    return 0 if not failures else 2
if __name__=="__main__":raise SystemExit(main())
