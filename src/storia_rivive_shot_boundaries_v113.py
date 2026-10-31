#!/usr/bin/env python3
"""V113: conservative FFmpeg cut-candidate evidence for historical film.

A cut detector can propose distinct *segments*, never certify genuine camera
shots. No network, no image generation, no Vidu, no user approvals.
"""
from __future__ import annotations

import bisect
import math
import re
import subprocess
from pathlib import Path

CUT_THRESHOLD = 0.30
SAMPLE_FPS = 2
MAX_CUT_CANDIDATES = 1000
SHOWINFO_PTS = re.compile(
    r"\[Parsed_showinfo_\d+\s+@[^\]]+\]\s+n:\s*\d+\s+pts:\s*-?\d+\s+pts_time:\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+))"
)


def segment_for_time(source_time_s, cut_times_s):
    """Return the zero-based segment inferred from FFmpeg cut candidates."""
    if not math.isfinite(float(source_time_s)):
        raise ValueError("INVALID_SOURCE_TIME_FOR_SHOT_SEGMENT")
    return bisect.bisect_right(cut_times_s, float(source_time_s))


def detect_cut_candidates(film: Path, duration_s: float, source_sha256: str):
    """Decode actual video and collect possible hard cuts, never invented shots.

    The 2 fps analysis deliberately favors avoiding spurious small movements.
    Dissolves and fast camera pans may be missed or misclassified: a human must
    review the original footage before any I2I or Vidu spend.
    """
    if not film.is_file() or not math.isfinite(duration_s) or duration_s <= 0:
        raise ValueError("SHOT_DETECTOR_INVALID_SOURCE")
    if not re.fullmatch(r"[0-9a-f]{64}", source_sha256):
        raise ValueError("SHOT_DETECTOR_INVALID_FILM_SHA")
    vf=f"fps={SAMPLE_FPS},scale=320:-2,select='gt(scene,{CUT_THRESHOLD})',showinfo"
    try:
        result=subprocess.run(
            ["ffmpeg","-nostdin","-hide_banner","-loglevel","info","-i",str(film),
             "-an","-sn","-vf",vf,"-fps_mode","vfr",
             "-frames:v",str(MAX_CUT_CANDIDATES),"-f","null","-"],
            capture_output=True,text=True,check=True,timeout=180)
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as exc:
        raise ValueError("SHOT_BOUNDARY_DETECTION_FAILED_OR_TIMED_OUT") from exc
    times=[]
    for raw in SHOWINFO_PTS.findall(result.stderr):
        t=float(raw)
        if not math.isfinite(t):
            raise ValueError("SHOT_BOUNDARY_INVALID_PTS")
        if 0.25<t<duration_s-0.25 and (not times or t>times[-1]+0.001):
            times.append(round(t,6))
    if len(times)>=MAX_CUT_CANDIDATES:
        raise ValueError("SHOT_BOUNDARY_TOO_MANY_CUT_CANDIDATES")
    return {
        "version":"V113_FFMPEG_SCENE_CANDIDATES",
        "source_sha256":source_sha256,
        "status":("FIVE_SEGMENTS_POSSIBLE_REVIEW_REQUIRED" if len(times)>=4
                  else "INSUFFICIENT_CUT_CANDIDATES"),
        "cut_candidate_times_s":times,
        "cut_candidate_count":len(times),
        "analysis_sample_fps":SAMPLE_FPS,
        "scene_score_threshold":CUT_THRESHOLD,
        "historical_camera_shots_verified":False,
        "warning":"Scene-score boundaries are not proof of five real camera shots. Human footage review is mandatory."
    }
