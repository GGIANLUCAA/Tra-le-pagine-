#!/usr/bin/env python3
"""V126: balanced five moving archival candidates from genuine V125 evidence.

Offline review-only fallback when a film lacks moving source footage in
every fifth of its timeline. DOES NOT waive five real camera shots, V98, rights,
real I2I, Vidu authorization, human artistic QA or publication clearance.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

SOURCE_SHA = re.compile(r"[0-9a-f]{64}\Z")
MIN_SEPARATION_SECONDS = 12.0
MIN_REGION_COVERAGE = 3
MAX_PER_REGION = 2


def _validate_and_candidates(motion, rank, scout):
    digest = motion.get("source_video_sha256")
    if (not isinstance(digest, str) or SOURCE_SHA.fullmatch(digest) is None
            or rank.get("adaptive_frame_source_sha256") != digest
            or scout.get("original_sha256") != digest
            or scout.get("frame_provenance_source_sha256") != digest
            or motion.get("version") != "V125_REAL_BW_DECODED_SPATIAL_MOTION_UNAPPROVED"
            or motion.get("status") not in (
                "V125_FIVE_MOVING_PHOTO_REGIONS_REVIEW_REQUIRED",
                "V125_MOTION_SOURCE_SELECTION_BLOCKED")
            or rank.get("adaptive_review_only_not_camera_approval") is not True):
        raise ValueError("V126_SOURCE_REPORT_SHA_OR_STATE_MISMATCH")
    duration = motion.get("source_duration_s")
    if type(duration) not in (int, float) or not math.isfinite(duration) or duration <= 0:
        raise ValueError("V126_FILM_DURATION_INVALID")
    originals = scout.get("frame_provenance")
    if not isinstance(originals, list) or not 5 <= len(originals) <= 48:
        raise ValueError("V126_SOURCE_PROVENANCE_INCOMPLETE")
    source_by_name = {}
    for x in originals:
        if not isinstance(x, dict):
            raise ValueError("V126_SOURCE_PROVENANCE_INVALID")
        name=x.get("filename")
        if name in source_by_name or not isinstance(name, str):
            raise ValueError("V126_SOURCE_FRAME_PROVENANCE_DUPLICATED")
        source_by_name[name]=x
    ranked = rank.get("all_candidates")
    if not isinstance(ranked, list) or len(ranked) != len(source_by_name):
        raise ValueError("V126_RANKING_CANDIDATE_COUNT_MISMATCH")
    scored_by_name = {r.get("filename"):r for r in ranked if isinstance(r,dict)}
    if len(scored_by_name)!=len(ranked) or set(scored_by_name)!=set(source_by_name):
        raise ValueError("V126_RANKING_PROVENANCE_MISMATCH")
    audited = motion.get("motion_audit")
    if not isinstance(audited, list) or len(audited)>len(originals):
        raise ValueError("V126_MOTION_EVIDENCE_MISSING")
    eligible=[]
    seen=set()
    for result in audited:
        if not isinstance(result, dict):
            raise ValueError("V126_MOTION_ROW_INVALID")
        name=result.get("filename")
        if name in seen or name not in source_by_name:
            raise ValueError("V126_MOTION_ROW_UNKNOWN_OR_DUPLICATE")
        seen.add(name)
        if not (result.get("motion_verified") is True
                and result.get("status")=="MOTION_EVIDENCE_PASS"
                and type(result.get("changed_pairs")) is int
                and result["changed_pairs"]>=2
                and type(result.get("sample_count")) is int
                and result["sample_count"]>=5
                and type(result.get("max_spatial_pixel_delta")) in (int,float)
                and result["max_spatial_pixel_delta"]>=6):
            continue
        original=source_by_name[name]
        score=scored_by_name[name]
        if not (score.get("source_picture_content_eligible") is True
                and score.get("source_native_detail_sufficient") is True
                and score.get("pre_freeze_window_viable") is True):
            raise ValueError("V126_MOTION_PASS_BUT_PHOTOGRAPHIC_SOURCE_NOT_VALID")
        if (result.get("source_pts") != original.get("source_pts")
                or result.get("candidate_segment_index") != original.get("shot_candidate_segment_index")
                or result.get("source_time_s") != original.get("source_pts_time_s")):
            raise ValueError("V126_MOTION_PTS_OR_SEGMENT_MISMATCH")
        window = score.get("pre_freeze_window_pts")
        if (not isinstance(window, dict)
                or result.get("start_pts") != window.get("start_pts")
                or result.get("freeze_pts") != window.get("freeze_pts")
                or result.get("time_base") != window.get("time_base")):
            raise ValueError("V126_MOTION_SOURCE_WINDOW_MISMATCH")
        time = original.get("source_pts_time_s")
        if type(time) not in (int,float) or not math.isfinite(time) or not 0<=time<duration:
            raise ValueError("V126_SOURCE_FRAME_TIME_OUT_OF_BOUNDS")
        sha = original.get("sha256")
        if not isinstance(sha,str) or SOURCE_SHA.fullmatch(sha) is None:
            raise ValueError("V126_ORIGINAL_FRAME_SHA_MISSING")
        quality = score.get("source_visual_quality_score")
        if type(quality) not in (int,float) or not math.isfinite(quality) or not 0<=quality<=1.0:
            raise ValueError("V126_FRAME_SCORE_INVALID")
        eligible.append({
            "filename":name,
            "source_pts":original["source_pts"],
            "source_pts_time_s":time,
            "source_time_base":original["source_time_base"],
            "source_frame_sha256":sha,
            "source_film_sha256":digest,
            "candidate_segment_index":original["shot_candidate_segment_index"],
            "timeline_region":min(4,int(time*5/duration)),
            "quality_advisory":quality,
            "max_spatial_pixel_delta":result["max_spatial_pixel_delta"],
            "changed_pairs":result["changed_pairs"],
            "motion_verified_for_review":True,
            "pre_freeze_window_pts":window,
            "genuine_camera_shot_verified":False,
            "human_artistic_approved":False
        })
    return digest,duration,eligible


def choose_balanced_review(motion, rank, scout, *, minimum_separation=MIN_SEPARATION_SECONDS):
    """Prefer coverage of all observed regions, then fill five with capped repeats.

    Five different V113 candidate segments and temporal separation are useful
    evidence, NOT proof of five genuinely different original camera shots.
    """
    digest,duration,candidates = _validate_and_candidates(motion,rank,scout)
    result={
        "version":"V126_FIVE_DIVERSE_MOVING_SHOTS_NOT_APPROVED",
        "status":"V126_INSUFFICIENT_MOTION_SCENE_VARIETY",
        "source_film_sha256":digest,
        "source_duration_s":duration,
        "moving_photo_candidates":len(candidates),
        "covered_timeline_regions":sorted({x["timeline_region"] for x in candidates}),
        "minimum_different_timeline_regions":MIN_REGION_COVERAGE,
        "maximum_two_scenes_per_region":True,
        "minimum_seconds_between_freezes":minimum_separation,
        "five_review_candidates":[],
        "five_real_camera_shots_verified":False,
        "human_artistic_approved":False,
        "italian_rights_verified":False,
        "i2i_photos_generated":0,
        "vidu_clips_generated":0,
        "paid_api_calls":0,
        "video_finished":False,
        "published":False
    }
    if (type(minimum_separation) not in (int,float)
            or not math.isfinite(minimum_separation) or not 8<=minimum_separation<=40):
        raise ValueError("V126_INVALID_TIME_SEPARATION")
    regions=result["covered_timeline_regions"]
    if len(candidates)<5 or len(regions)<MIN_REGION_COVERAGE:
        return result
    chosen=[]
    used_segments=set()
    used_sha=set()
    counts={r:0 for r in range(5)}
    def add(item):
        region=item["timeline_region"]
        if counts[region] >= MAX_PER_REGION:
            return False
        if (item["candidate_segment_index"] in used_segments
                or item["source_frame_sha256"] in used_sha
                or any(abs(item["source_pts_time_s"]-x["source_pts_time_s"])
                       < minimum_separation for x in chosen)):
            return False
        chosen.append(item)
        counts[region]+=1
        used_segments.add(item["candidate_segment_index"])
        used_sha.add(item["source_frame_sha256"])
        return True
    # Cover all observed film regions before taking an extra similar shot.
    buckets = {region:sorted((x for x in candidates if x["timeline_region"]==region),
                             key=lambda x:(-x["quality_advisory"],x["source_pts_time_s"]))
               for region in regions}
    for region in regions:
        for item in buckets[region]:
            if add(item):
                break
        if len(chosen)>=5:
            break
    remaining=sorted(candidates,
                     key=lambda x:(-x["quality_advisory"],x["source_pts_time_s"]))
    for item in remaining:
        if len(chosen)>=5:
            break
        add(item)
    if len(chosen)!=5 or len({x["timeline_region"] for x in chosen})<MIN_REGION_COVERAGE:
        return result
    chosen.sort(key=lambda x:x["source_pts_time_s"])
    result["status"]="V126_FIVE_DIFFERENT_MOVING_SOURCE_CANDIDATES_REVIEW_ONLY"
    result["five_review_candidates"]=chosen
    result["selected_timeline_regions"]=sorted({x["timeline_region"] for x in chosen})
    return result


def run(motion_path, rank_path, scout_path, out_path):
    evidence=json.loads(Path(motion_path).read_text(encoding="utf-8"))
    ranked=json.loads(Path(rank_path).read_text(encoding="utf-8"))
    scout=json.loads(Path(scout_path).read_text(encoding="utf-8"))
    try:
        result=choose_balanced_review(evidence,ranked,scout)
    except (ValueError,TypeError,KeyError) as exc:
        result={"version":"V126_FIVE_DIVERSE_MOVING_SHOTS_NOT_APPROVED",
                "status":"V126_INSUFFICIENT_MOTION_SCENE_VARIETY",
                "reason":str(exc)[:240],"five_review_candidates":[],
                "human_artistic_approved":False,"italian_rights_verified":False,
                "paid_api_calls":0,"video_finished":False,"published":False}
    output=Path(out_path)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--motion",required=True)
    parser.add_argument("--rank",required=True)
    parser.add_argument("--scout",required=True)
    parser.add_argument("--out",required=True)
    args=parser.parse_args()
    res=run(args.motion,args.rank,args.scout,args.out)
    print("V126_REVIEW_ONLY",res["status"],
          "moving_photo_candidates",res.get("moving_photo_candidates",0),
          "five",len(res["five_review_candidates"]))


if __name__=="__main__":
    main()
