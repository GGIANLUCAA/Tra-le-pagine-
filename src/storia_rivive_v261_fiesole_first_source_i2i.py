#!/usr/bin/env python3
"""V261: first genuine Fiesole 1912 frame -> one free CPU InstructPix2Pix candidate.
Reuses proven V257 inference without changing its original source or previous results.
No final video, no credits, no publication.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import storia_rivive_v257_fiesole_third_source_i2i as engine

SOURCE_SHA="3ebabe8a57ce3cf386681255ad4d896ab540d31005bfbfd1087474f62af714cb"
SOURCE_NAME="frame_03.png"
SHOT=1
SEED=261
PROMPT=(
    "Restore natural photographic color and truthful documentary detail in this "
    "EXACT 1912 Fiesole workshop frame, showing the existing straw-processing "
    "machinery. Keep every machine component, container, straw fiber, background "
    "and perspective unchanged. No invented humans, hats, tools or architectural "
    "features. Natural neutral light, realistic metal, wood and straw tones. "
    "No orange cast, no plastic texture, no stylization or text."
)

def verify_manifest(path:Path,source:Path)->dict:
    manifest=json.loads(path.read_text(encoding="utf-8"))
    if (manifest.get("version")!="V251_FIESOLE_SOURCE_LOCKED_PHOTO_HANDOFF"
        or manifest.get("source_film_sha256")!="f87ca5d51a1ba4b60ffb0e5db6162f3b0afadcd3bf3b94393dcf66337a7af7fe"
        or manifest.get("episode")!="fiesole_straw_hats_1912_v220"):
        raise ValueError("V261_WRONG_FILM_OR_EPISODE")
    shots=manifest.get("shots",[])
    if len(shots)!=5:raise ValueError("V261_NOT_FIVE_SHOTS")
    if len({row.get("original_sha256") for row in shots}) != 5:
        raise ValueError("V261_DUPLICATED_SOURCE_SHA_IN_MANIFEST")
    shot=shots[SHOT-1]
    if (shot.get("shot")!=SHOT or shot.get("role")!="I2I_PHOTO_SOURCE"
        or shot.get("original_frame")!=SOURCE_NAME
        or shot.get("original_sha256")!=SOURCE_SHA
        or shot.get("archive_filename")!=source.name
        or shot.get("source_frame_locked") is not True):
        raise ValueError("V261_SHOT_FOUR_NOT_AUTHENTIC")
    if engine.sha(source)!=SOURCE_SHA:
        raise ValueError("V261_ORIGINAL_BYTES_CHANGED")
    return shot

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--manifest",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--offline",action="store_true")
    a=p.parse_args()
    shot=verify_manifest(a.manifest,a.source)
    engine.SOURCE_SHA=SOURCE_SHA
    engine.PROMPT=PROMPT
    engine.SEED=SEED
    engine.SOURCE_TIME_S=shot["source_time_s"]
    engine.main_args=None
    import sys
    sys.argv=[sys.argv[0],"--source",str(a.source),"--out",str(a.out)]
    if a.offline:sys.argv.append("--offline")
    engine.main()
    status_path=a.out/"V257_SOURCE_LOCKED_I2I_QA.json"
    status=json.loads(status_path.read_text())
    status.update(version="V261_FIRST_SOURCE_LOCAL_CPU_I2I",
                  original_source_sha256=SOURCE_SHA,source_frame=SOURCE_NAME,
                  source_time_s=shot["source_time_s"],seed=SEED,
                  new_final_episodes_delivered=0,italian_rights_verified=False,
                  artistic_approval=False,publish_allowed=False)
    status_path.write_text(json.dumps(status,indent=2)+"\n")

if __name__=="__main__":main()
