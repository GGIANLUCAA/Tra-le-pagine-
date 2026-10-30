#!/usr/bin/env python3
"""V102: prepare immutable source-locked image-to-image jobs from REAL native film frames.

No provider calls, no AI image output claims, no publication. The result can be
consumed by a future free/approved image-to-image worker.
"""
from __future__ import annotations
import argparse, bisect, hashlib, json, math, re
from itertools import combinations
from pathlib import Path
from PIL import Image, ImageOps

PROMPT=(
    "Restore THIS EXACT archival film frame into a realistic, high-detail modern "
    "documentary photograph. Preserve all existing people, facial identity only "
    "as supported by original pixels, pose, clothes, architecture, vehicles, "
    "objects, framing and perspective. Period-appropriate natural colors. "
    "Never invent eyes, faces, limbs, signs, people or objects. "
    "This is an interpretive color reconstruction, not an original color photograph."
)
NEGATIVE=(
    "face swap, invented identity, extra people, extra limbs, changing objects, "
    "modern cars, plastic skin, cartoon, AI painting, hallucinated text, "
    "wrong era, inaccurate architecture, cropped faces, excessive saturation"
)
def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()

def visual_near_duplicate_guard(paths, threshold=0.055):
    """Detect same-composition frames despite brightness, contrast or byte changes.

    This is only a conservative duplicate blocker, NOT proof of five genuine
    historical camera shots. Human shot-boundary review remains mandatory.
    """
    if len(paths)!=5:
        raise ValueError("V110_EXPECTS_FIVE_ARCHIVAL_FRAMES")
    signatures=[]
    for path in paths:
        with Image.open(path) as source:
            gray=ImageOps.grayscale(source).resize((64,64),Image.Resampling.BILINEAR)
        values=list(gray.tobytes())
        mean=sum(values)/len(values)
        variance=sum((v-mean)**2 for v in values)/len(values)
        scale=max(8.0,variance**0.5)
        signatures.append(tuple(max(-3.0,min(3.0,(v-mean)/scale)) for v in values))
    pairs=[]
    for a,b in combinations(range(5),2):
        distance=sum(abs(x-y) for x,y in zip(signatures[a],signatures[b]))/4096
        if distance<=threshold:
            pairs.append({"frame_a":paths[a].name,"frame_b":paths[b].name,
                          "normalized_visual_distance":round(distance,5)})
    return {"version":"V110","status":"VISUAL_NEAR_DUPLICATE_SOURCE_FRAMES" if pairs
            else "NO_OBVIOUS_VISUAL_DUPLICATES_REVIEW_REQUIRED",
            "near_duplicate_pairs":pairs,
            "threshold":threshold,
            "historical_shot_distinctness_verified":False,
            "warning":"No obvious duplicates does NOT prove five different camera shots."}

def verified_source_preflight(order, source_dir):
    """Fail closed before preparing a provider-consumable source-locked job."""
    issues=order.get("blocking_issues")
    if not isinstance(issues,list):
        raise ValueError("V101_SOURCE_PREFLIGHT_MISSING")
    if issues:
        raise ValueError("V101_SOURCE_PREFLIGHT_BLOCKED: "+", ".join(str(i) for i in issues)[:160])
    report_path=source_dir/"SCOUT_REPORT.json"
    if not report_path.is_file():
        raise ValueError("SCOUT_REPORT_MISSING")
    report=json.loads(report_path.read_text(encoding="utf-8"))
    if report.get("status")!="REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW":
        raise ValueError("SCOUT_SOURCE_NOT_READY")
    source=source_dir/"ORIGINAL_ARCHIVE.webm"
    if not source.is_file():
        raise ValueError("ORIGINAL_ARCHIVE_MISSING")
    film_sha=sha(source)
    if report.get("original_sha256")!=film_sha:
        raise ValueError("SCOUT_FILM_SHA_MISMATCH")
    # V111: an old or tampered cached contact sheet must never become I2I input.
    if report.get("frame_provenance_source_sha256")!=film_sha:
        raise ValueError("FRAME_PROVENANCE_FILM_SHA_MISMATCH_OR_MISSING")
    if report.get("frame_provenance_version")!="V112_SOURCE_PTS_FROM_FFMPEG_SHOWINFO":
        raise ValueError("SOURCE_PTS_PROVENANCE_VERSION_MISSING_OR_LEGACY")
    entries=report.get("frame_provenance")
    if not isinstance(entries,list) or not entries:
        raise ValueError("FRAME_PROVENANCE_MISSING")
    # V113: scene-cut evidence must come from a separate real-film FFmpeg pass.
    # Candidate segments alone do NOT prove genuine historical camera changes.
    cuts_report=report.get("shot_boundary_analysis")
    if not isinstance(cuts_report,dict) or cuts_report.get("version")!="V113_FFMPEG_SCENE_CANDIDATES":
        raise ValueError("SHOT_BOUNDARY_EVIDENCE_MISSING_OR_LEGACY")
    if cuts_report.get("source_sha256")!=film_sha:
        raise ValueError("SHOT_BOUNDARY_FILM_SHA_MISMATCH")
    cuts=cuts_report.get("cut_candidate_times_s")
    if (not isinstance(cuts,list) or len(cuts)<4 or len(cuts)>999
            or cuts_report.get("status")!="FIVE_SEGMENTS_POSSIBLE_REVIEW_REQUIRED"
            or cuts_report.get("historical_camera_shots_verified") is not False
            or any(type(t) not in (int,float) or not math.isfinite(t) or t<=0 for t in cuts)
            or any(a>=b for a,b in zip(cuts,cuts[1:]))):
        raise ValueError("INSUFFICIENT_OR_INVALID_SHOT_BOUNDARY_CANDIDATES")
    frame_map={}
    for entry in entries:
        if not isinstance(entry,dict):
            raise ValueError("INVALID_FRAME_PROVENANCE")
        name=entry.get("filename")
        digest=entry.get("sha256")
        pts=entry.get("source_pts")
        pts_time=entry.get("source_pts_time_s")
        base=entry.get("source_time_base")
        if (not isinstance(name,str) or not re.fullmatch(r"frame_\d{2}\.png",name)
                or not isinstance(digest,str) or not re.fullmatch(r"[0-9a-f]{64}",digest)
                or name in frame_map or type(pts) is not int
                or type(pts_time) not in (int,float) or not math.isfinite(pts_time)
                or not isinstance(base,str) or not re.fullmatch(r"\d+/[1-9]\d*",base)
                or entry.get("source_pts_logged_from_decode") is not True
                or type(entry.get("extraction_index")) is not int):
            raise ValueError("SOURCE_PTS_PROVENANCE_INVALID")
        segment=entry.get("shot_candidate_segment_index")
        if type(segment) is not int or segment!=bisect.bisect_right(cuts,pts_time):
            raise ValueError("SHOT_SEGMENT_PROVENANCE_MISMATCH: "+name)
        frame_map[name]=entry
    return film_sha,frame_map,cuts_report

def build(order,selection,source_dir):
    if order.get("contract")!="LA_STORIA_RIVIVE_V101_SAFE_AUTOPILOT":
        raise ValueError("Not an authenticated V101 work-order schema")
    if order.get("paid_api_call_permitted") is not False or order.get("publish_permitted") is not False:
        raise ValueError("Unsafe work-order permissions")
    source_video_sha,frame_provenance,shot_analysis=verified_source_preflight(order,source_dir)
    if selection.get("status")!="FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW":
        raise ValueError("No five candidate source frames")
    chosen=selection.get("preselected",[])
    if len(chosen)!=5:raise ValueError("Need five genuine distinct frame positions")
    names=[r["filename"] for r in chosen]
    if len(set(names))!=5:raise ValueError("Duplicate frames")
    jobs=[]
    seen_frame_hashes=set()
    last_pts_time=None
    seen_source_pts=set()
    for n,row in enumerate(chosen):
        name=row["filename"]
        if not re.fullmatch(r"frame_\d{2}\.png",name):raise ValueError("Unsafe source filename")
        path=source_dir/"original_frames"/name
        if not path.is_file():raise ValueError("Missing original source frame")
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            width,height=image.size
        native_crop_w=min(width,round(height*9/16))
        if native_crop_w<400 or height<720:
            raise ValueError(
                f"SOURCE_NATIVE_DETAIL_INSUFFICIENT: {name} "
                f"crop={native_crop_w}px height={height}px; need >=400px crop and >=720px height"
            )
        frame_sha=sha(path)
        recorded=frame_provenance.get(name)
        if recorded is None:
            raise ValueError("SOURCE_FRAME_NOT_IN_SCOUT_PROVENANCE: "+name)
        if recorded["sha256"]!=frame_sha:
            raise ValueError("SOURCE_FRAME_SHA_MISMATCH_WITH_SCOUT: "+name)
        pts=recorded["source_pts"]
        pts_time=recorded["source_pts_time_s"]
        if pts in seen_source_pts or (last_pts_time is not None and pts_time<=last_pts_time):
            raise ValueError("SELECTED_SOURCE_PTS_DUPLICATE_OR_NON_MONOTONIC")
        seen_source_pts.add(pts)
        last_pts_time=pts_time
        if frame_sha in seen_frame_hashes:
            raise ValueError("DUPLICATE_SOURCE_FRAME_BYTES: "+name)
        seen_frame_hashes.add(frame_sha)
        jobs.append({
          "job_id":f"{order['cycle_id']}_photo_{n+1:02d}",
          "source_file":str(path),"source_sha256":frame_sha,
          "source_film_sha256":source_video_sha,
          "extraction_index":recorded["extraction_index"],
          "source_pts":recorded["source_pts"],
          "source_pts_time_s":recorded["source_pts_time_s"],
          "source_time_base":recorded["source_time_base"],
          "source_pts_logged_from_decode":True,
          "exact_source_timecode_verified":False,
          "source_raster_px":[width,height],
          "target_raster_px":[720,1280],
          "target_kind":"REAL_SOURCE_LOCKED_I2I_PHOTOGRAPH",
          "role":"VIDU_SOURCE_ANCHOR_NOT_RENDERED" if n==4 else "STATIC_COLOR_REVEAL",
          "prompt":PROMPT,"negative_prompt":NEGATIVE,
          "allow_source_reframing":False,"allow_invented_people":False,
          "provider":"NOT_SELECTED_NO_CALL","request_sent":False,
          "result_file":None,"restored_photo_approved":False,
          "human_face_fidelity":"PENDING","source_geometry_gate":"PENDING",
          "scene_distinctness_gate":"PENDING","rights_gate":"PENDING"
        })
    segments=[job["shot_candidate_segment_index"] for job in jobs]
    if len(set(segments))!=5:
        raise ValueError("FIVE_DISTINCT_SHOT_CANDIDATES_NOT_FOUND: "+str(segments))
    visual_guard=visual_near_duplicate_guard([source_dir/"original_frames"/name for name in names])
    if visual_guard["near_duplicate_pairs"]:
        raise ValueError("VISUAL_NEAR_DUPLICATE_SOURCE_FRAMES: "+json.dumps(visual_guard["near_duplicate_pairs"][:2]))
    return {"version":"V102_SOURCE_LOCKED_I2I_JOBS",
      "cycle_id":order["cycle_id"],"episode_id":order["episode_id"],
      "source_video_sha256":source_video_sha,
      "frame_provenance_guard":"V112_SOURCE_PTS_AND_PNG_SHA256_MATCH_SCOUT",
      "original_frame_jobs":jobs,"photos_requested":5,
      "visual_duplicate_guard":visual_guard,
      "historical_shot_distinctness_verified":False,
      "photos_generated":0,"photos_approved":0,
      "provider_requests_sent":0,"paid_api_calls":0,
      "vidu_calls":0,"publication_permitted":False,
      "status":"I2I_INPUTS_PREPARED_NO_AI_GENERATION",
      "warning":"These are five source frames, not five verified distinct camera shots."}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--order",required=True);p.add_argument("--selection",required=True)
    p.add_argument("--source-dir",required=True);p.add_argument("--out",required=True)
    a=p.parse_args()
    output=Path(a.out);output.parent.mkdir(parents=True,exist_ok=True)
    try:
        data=build(json.loads(Path(a.order).read_text()),
                   json.loads(Path(a.selection).read_text()),Path(a.source_dir))
    except Exception as e:
        data={"version":"V102_SOURCE_LOCKED_I2I_JOBS","status":"I2I_INPUTS_BLOCKED",
              "reason":type(e).__name__+": "+str(e)[:220],
              "photos_generated":0,"provider_requests_sent":0,"paid_api_calls":0,
              "vidu_calls":0,"publication_permitted":False}
    output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("V102_I2I_PREP",data["status"],"provider_requests",data["provider_requests_sent"])
if __name__=="__main__":main()
