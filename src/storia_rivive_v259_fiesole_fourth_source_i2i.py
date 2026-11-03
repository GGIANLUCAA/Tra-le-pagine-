#!/usr/bin/env python3
"""V259: fourth genuine Fiesole 1912 frame -> one free CPU InstructPix2Pix candidate.
Reuses proven V257 inference without changing its original source or previous results.
No final video, no credits, no publication.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import storia_rivive_v257_fiesole_third_source_i2i as engine

SOURCE_SHA="1d77c757e3193bc9c046f2ae10baebb49a3b71fe379ed359b18e761956f4afb0"
SOURCE_NAME="frame_07.png"
SHOT=4
SEED=259
PROMPT=(
    "Carefully colorize and photographically restore this EXACT archival frame "
    "from the 1912 Fiesole straw hat factory. Preserve the precise number and "
    "locations of workers, straw hats, weaving tools, machinery, windows and "
    "every silhouette and architectural line. Add subtle believable natural "
    "period colors and photographic texture to EXISTING objects only. "
    "Do not add people, faces, limbs, furniture, objects, words or signs. "
    "Realistic skin, straw, cloth, wood and metal, neutral daylight."
)

def verify_manifest(path:Path,source:Path)->dict:
    manifest=json.loads(path.read_text(encoding="utf-8"))
    if (manifest.get("version")!="V251_FIESOLE_SOURCE_LOCKED_PHOTO_HANDOFF"
        or manifest.get("source_film_sha256")!="f87ca5d51a1ba4b60ffb0e5db6162f3b0afadcd3bf3b94393dcf66337a7af7fe"
        or manifest.get("episode")!="fiesole_straw_hats_1912_v220"):
        raise ValueError("V259_WRONG_FILM_OR_EPISODE")
    shots=manifest.get("shots",[])
    if len(shots)!=5:raise ValueError("V259_NOT_FIVE_SHOTS")
    shot=shots[SHOT-1]
    if (shot.get("shot")!=SHOT or shot.get("role")!="I2I_PHOTO_SOURCE"
        or shot.get("original_frame")!=SOURCE_NAME
        or shot.get("original_sha256")!=SOURCE_SHA
        or shot.get("archive_filename")!=source.name
        or shot.get("source_frame_locked") is not True):
        raise ValueError("V259_SHOT_FOUR_NOT_AUTHENTIC")
    if engine.sha(source)!=SOURCE_SHA:
        raise ValueError("V259_ORIGINAL_BYTES_CHANGED")
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
    status.update(version="V259_FOURTH_SOURCE_LOCAL_CPU_I2I",
                  original_source_sha256=SOURCE_SHA,source_frame=SOURCE_NAME,
                  source_time_s=shot["source_time_s"],seed=SEED,
                  new_final_episodes_delivered=0,italian_rights_verified=False,
                  artistic_approval=False,publish_allowed=False)
    status_path.write_text(json.dumps(status,indent=2)+"\n")

if __name__=="__main__":main()
