#!/usr/bin/env python3
"""Bruegel Critico V144: sentence-specific experimental shot map.

Grounded in the original authored chapter focus anchors and actual ASR sentence
timecodes. Distinct from a semantic vision review; every area remains
PENDING HUMAN FRAME INSPECTION. No generated/counterfeit painting content.
"""
from __future__ import annotations

import bisect
import copy
import math
import re

# 18 existing sentences in the original, authenticated Gacrux recording.
# source_chapter refers to a camera target already in the V144 artwork recipe.
# WIDE intentionally refers to the genuine whole painting.
# This editorial plan is limited to THIS artwork; never copy coordinates to another.
BEATS = [
    ("detail",0,"locked","Visual hook: turmoil; omit static title opening"),
    ("detail",0,"hold_push","Show authentic central collision while angels/monsters are mentioned"),
    ("wide",1,"locked","Identify the exact whole painting"),
    ("wide",1,"locked","Do not invent imagery of an unverified museum"),
    ("detail",2,"hold_push","Michael central painted figure"),
    ("wide",2,"locked","Relate the angel's action to the larger battle"),
    ("detail",3,"hold_pan_left","Light sky and upper angels"),
    ("wide",3,"locked","Show sky-to-lower-dark contrast in the entire authentic work"),
    ("detail",4,"locked","Introduce the creatures"),
    ("detail",4,"hold_pull","Contextualize the many hybrids using original detail"),
    ("detail",5,"hold_push","Mouth open at the left/lower region"),
    ("detail",5,"hold_pull","Revisit the neighboring parts with more context"),
    ("detail",6,"locked","Butterfly-winged creature"),
    ("detail",6,"hold_pull","Relation of butterfly figure to nearby forms"),
    ("detail",7,"hold_pan_right","Bosch link and Bruegel visual order"),
    ("wide",7,"locked","Contrast of light and shadow across whole work"),
    ("wide",8,"locked","Whole painting for final interpretation"),
    ("wide",8,"locked","Final question, finish in one unaltered full painting")
]


def sentence_plan(timed, chapters, voice_offset_s, wav_sha256, image_sha256):
    if len(BEATS)!=18 or not isinstance(timed,list) or len(timed)!=len(BEATS):
        raise ValueError("Only the known authentic V144 18-sentence voice is supported")
    if not isinstance(chapters,list) or len(chapters)!=9:
        raise ValueError("Missing exact 9 source-locked chapter camera anchors")
    if any(not isinstance(h,str) or not re.fullmatch("[a-f0-9]{64}",h)
           for h in (wav_sha256,image_sha256)):
        raise ValueError("WAV and art exact SHA required")
    if not (type(voice_offset_s) in (int,float) and math.isfinite(voice_offset_s)
            and voice_offset_s>=0):
        raise ValueError("Actual voice offset required")
    shots=[]
    prev=0
    for idx,(entry,edit) in enumerate(zip(timed,BEATS)):
        if not isinstance(entry,(list,tuple)) or len(entry)!=3:
            raise ValueError("Invalid ASR timestamp")
        speech,a,b=entry
        if (not isinstance(speech,str) or not speech.strip()
                or type(a) not in (int,float) or type(b) not in (int,float)
                or not math.isfinite(a) or not math.isfinite(b) or not 0<=a<b
                or a<prev-.06):
            raise ValueError("ASR spans must be real, ordered and non-empty")
        prev=b
        kind,chapter_index,mode,why=edit
        ch=chapters[chapter_index]
        if not all(k in ch for k in ("cx","cy","crop_height_px","focus")):
            raise ValueError("Cannot direct a scene without the existing artwork anchor")
        shots.append({
            "id":f"sentence_{idx+1:02d}",
            "actual_spoken_text":speech,
            "voice_start_s":round(a,3),
            "voice_end_s":round(b,3),
            "video_start_s":round(voice_offset_s+a,3),
            "video_end_s":round(voice_offset_s+b,3),
            "camera_area":kind,"source_chapter":chapter_index,
            "camera_mode":mode,
            "reason":why,
            "original_focus":ch["focus"],
            "subject_bbox_verified":False,
            "artistic_review":"PENDING"
        })
    return {
        "schema":"artvision-bruegel-sentence-montage-v3",
        "source_artwork_sha256":image_sha256,
        "source_wav_sha256":wav_sha256,
        "time_base":"real_ASR_cache_plus_measured_voice_offset",
        "shots":shots,
        "candidate_only":True,"published":False,"artistic_approved":False,
        "no_new_voice_calls":True,"changes_original_mp4":False
    }


def sentence_index(timed, spoken_s):
    if not timed:
        raise ValueError("Empty real voice timings")
    # Display the next subject slightly ahead of the spoken phrase if a real pause
    # exists, without cutting away while the previous sentence is being spoken.
    ends=[r[2] for r in timed]
    ix=min(len(timed)-1,bisect.bisect_right(ends,spoken_s))
    if ix+1<len(timed) and ends[ix]<spoken_s:
        next_start=timed[ix+1][1]
        if next_start-spoken_s<=.15:
            ix+=1
    return ix
