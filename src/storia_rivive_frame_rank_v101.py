#!/usr/bin/env python3
"""V101: rank authentic original frames for likely restorable detail.
No facial identification, generation, source-frame timecode assertion or artistic approval.
"""
from __future__ import annotations
import argparse,bisect,json,math
from fractions import Fraction
from pathlib import Path
from PIL import Image,ImageOps,ImageFilter,ImageStat

try:
    from src.storia_rivive_motion_window_v115 import check_source_window
except ModuleNotFoundError:
    from storia_rivive_motion_window_v115 import check_source_window


def pre_freeze_window_evidence(entry, cuts):
    """V122: check the exact PTS window within its proposed source segment.

    Does not decode motion or certify a camera cut; V118 still independently
    rechecks source PNG/film SHA and FFmpeg pixel motion before provider use.
    """
    if not isinstance(entry, dict) or not isinstance(cuts, list):
        return {"eligible": False, "reason": "SOURCE_PTS_OR_CUTS_MISSING"}
    pts, seconds, base = (entry.get("source_pts"), entry.get("source_pts_time_s"),
                          entry.get("source_time_base"))
    if type(pts) is not int or pts < 0 or type(seconds) not in (int, float) or not math.isfinite(seconds):
        return {"eligible": False, "reason": "SOURCE_PTS_OR_CLOCK_INVALID"}
    if not isinstance(base, str) or base.count("/") != 1:
        return {"eligible": False, "reason": "SOURCE_PTS_TIME_BASE_INVALID"}
    try:
        numerator, denominator = map(int, base.split("/"))
        if numerator <= 0 or denominator <= 0:
            raise ValueError("nonpositive time base")
        period = Fraction(numerator, denominator)
        exact_seconds = pts * period
    except (ValueError, ZeroDivisionError, OverflowError):
        return {"eligible": False, "reason": "SOURCE_PTS_TIME_BASE_INVALID"}
    if abs(float(exact_seconds) - seconds) > 0.0001:
        return {"eligible": False, "reason": "SOURCE_PTS_CLOCK_MISMATCH"}
    segment = bisect.bisect_right(cuts, seconds)
    if type(entry.get("shot_candidate_segment_index")) is not int or entry["shot_candidate_segment_index"] != segment:
        return {"eligible": False, "reason": "SOURCE_PTS_SEGMENT_MISMATCH"}
    segment_start = cuts[segment - 1] if segment else 0.0
    start_seconds = max(0.0, segment_start + 0.05, seconds - 1.35)
    start_pts = math.ceil(Fraction(str(start_seconds)) / period)
    valid, reason = check_source_window(start_pts, pts, base)
    return {"eligible": valid, "reason": ("SOURCE_PRE_FREEZE_WINDOW_PTS_VALID_MOTION_NOT_YET_TESTED"
                                           if valid else reason),
            "start_pts": start_pts, "freeze_pts": pts, "time_base": base,
            "candidate_segment_index": segment}


def measure(path):
    with Image.open(path) as raw:
        w,h=raw.size
        gray=ImageOps.grayscale(raw).resize((256,256))
    contrast=ImageStat.Stat(gray).stddev[0]
    detail=ImageStat.Stat(gray.filter(ImageFilter.FIND_EDGES)).stddev[0]
    mean=ImageStat.Stat(gray).mean[0]
    exposure=max(0.0,1-abs(mean-126)/126)
    native_crop_w=min(w,round(h*9/16))
    # V109: a 480p film becomes only ~270 px wide in a 9:16 crop.
    # Learned upscaling cannot recover missing historical facial evidence.
    native_detail_ok=native_crop_w>=400 and h>=720
    source_pixel_ratio=min(1.0,(native_crop_w*h)/(720*1280))
    score=round(0.28*min(1,contrast/75)+0.30*min(1,detail/75)+
                0.12*exposure+0.30*source_pixel_ratio,4)
    return {"filename":path.name,"raster_px":[w,h],"native_portrait_crop_px":[native_crop_w,h],
            "contrast_advisory":round(contrast,2),"edge_detail_advisory":round(detail,2),
            "source_visual_quality_score":score,
            "source_native_detail_sufficient":native_detail_ok,
            "source_native_detail_rejection":None if native_detail_ok else "NATIVE_PORTRAIT_CROP_BELOW_400PX_OR_HEIGHT_BELOW_720PX",
            "face_identity_verified":False,
            "historical_shot_distinctness_verified":False,"approved_for_i2i":False}

def rank(folder):
    folder=Path(folder)
    imgs=sorted(folder.glob("frame_*.png"))
    if not imgs:raise ValueError("No native archival source PNG frames to evaluate")
    scored=[measure(p) for p in imgs]
    # V113: when a real scout report exists, pick no more than one frame from
    # each independently detected source segment. Never assert camera-shot proof.
    report_path=folder.parent/"SCOUT_REPORT.json"
    segment_by_name=None
    if report_path.is_file():
        report=json.loads(report_path.read_text(encoding="utf-8"))
        analysis=report.get("shot_boundary_analysis",{})
        provenance=report.get("frame_provenance",[])
        if (analysis.get("version")!="V113_FFMPEG_SCENE_CANDIDATES"
                or analysis.get("status")!="FIVE_SEGMENTS_POSSIBLE_REVIEW_REQUIRED"
                or not isinstance(provenance,list)):
            return {"status":"INSUFFICIENT_DISTINCT_SHOT_CANDIDATES",
                    "preselected":[],"all_candidates":scored,
                    "approved_restored_photos":0,
                    "next":"Reject this source or acquire footage with five genuine separate camera shots."}
        cuts=analysis.get("cut_candidate_times_s")
        if (not isinstance(cuts,list) or len(cuts)<4
                or any(type(t) not in (int,float) or not math.isfinite(t) or t<=0 for t in cuts)
                or any(a>=b for a,b in zip(cuts,cuts[1:]))):
            return {"status":"SHOT_BOUNDARY_PTS_EVIDENCE_INVALID",
                    "preselected":[],"all_candidates":scored,"approved_restored_photos":0}
        by_name={entry.get("filename"):entry for entry in provenance if isinstance(entry,dict)}
        segment_by_name={name:entry.get("shot_candidate_segment_index")
                         for name,entry in by_name.items()}
        if (len(by_name)!=len(provenance)
                or any(type(segment_by_name.get(p.name)) is not int for p in imgs)):
            return {"status":"SHOT_SEGMENT_PROVENANCE_INCOMPLETE",
                    "preselected":[],"all_candidates":scored,
                    "approved_restored_photos":0}
        for row in scored:
            row["shot_candidate_segment_index"]=segment_by_name[row["filename"]]
            evidence=pre_freeze_window_evidence(by_name[row["filename"]],cuts)
            row["pre_freeze_window_viable"]=evidence["eligible"]
            row["pre_freeze_window_reason"]=evidence["reason"]
            if evidence["eligible"]:
                row["pre_freeze_window_pts"]={
                    "start_pts":evidence["start_pts"],
                    "freeze_pts":evidence["freeze_pts"],
                    "time_base":evidence["time_base"]}
    # Reserve different time positions; cut candidates do not prove camera shots.
    ranked=sorted(
        (n for n in range(len(scored)) if scored[n]["source_native_detail_sufficient"]
         and scored[n].get("pre_freeze_window_viable",True)),
        key=lambda n:(-scored[n]["source_visual_quality_score"],n))
    chosen=[]
    used_segments=set()
    separation=max(1,len(scored)//6)
    for idx in ranked:
        segment=segment_by_name[imgs[idx].name] if segment_by_name is not None else None
        if segment_by_name is not None and segment in used_segments:
            continue
        if segment_by_name is not None or all(abs(idx-v)>=separation for v in chosen):
            chosen.append(idx)
            if segment_by_name is not None:
                used_segments.add(segment)
        if len(chosen)>=5:break
    if len(chosen)<5:
        native_count=sum(row["source_native_detail_sufficient"] for row in scored)
        reason=("SOURCE_NATIVE_DETAIL_INSUFFICIENT_FOR_FIVE_SHOTS"
                if native_count<5 else
                "INSUFFICIENT_PRE_FREEZE_SOURCE_WINDOWS"
                if len(ranked)<5 and segment_by_name is not None else
                "INSUFFICIENT_DISTINCT_SHOT_CANDIDATES")
        return {"status":reason,
                "original_source_frames":len(scored),"eligible_native_detail_frames":len(ranked),
                "minimum_native_portrait_crop_px":400,"minimum_native_height_px":720,
                "all_candidates":scored,"preselected":[],
                "approved_restored_photos":0,
                "next":"Need five source frames with true 0.9-2.5s pre-freeze windows inside separate proposed shots, then real motion and legal review."}
    selected=[scored[n] for n in sorted(chosen)]
    return {"status":"FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW",
            "original_source_frames":len(scored),"preselected":selected,
            "all_candidates":scored,"approved_restored_photos":0,
            "selection_is_not_verified_distinct_film_shots":True,
            "selected_shot_candidate_segments":([segment_by_name[imgs[n].name] for n in sorted(chosen)]
                                                if segment_by_name is not None else None),
            "next":"Review authentic source clip for five distinct moving shots, true timecodes and facial details before I2I"}

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--frames",required=True);p.add_argument("--out",required=True)
    a=p.parse_args();out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    try:data=rank(a.frames)
    except Exception as e:data={"status":"SOURCE_FRAME_SELECTION_BLOCKED","error":str(e)[:300],"preselected":[]}
    out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
    print(data["status"],len(data["preselected"]))
