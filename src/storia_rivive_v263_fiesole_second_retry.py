#!/usr/bin/env python3
"""V263: retry Fiesole shot 02 from the V251 original frame, free CPU I2I only.

V254 candidate altered a machine into a person: never treat this retry as approved.
No Vidu, no publishing, no paid provider.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
import storia_rivive_v257_fiesole_third_source_i2i as engine

FILM_SHA="f87ca5d51a1ba4b60ffb0e5db6162f3b0afadcd3bf3b94393dcf66337a7af7fe"
EPISODE="fiesole_straw_hats_1912_v220"
PROMPT=("Conservatively colorize this exact archival 1912 documentary frame. "
        "Preserve every original contour, object and machine silhouette without "
        "changing the subject. Natural photographic color, faithful geometry, "
        "neutral daylight, no new figures or objects.")
SEED=263
VERSION="V263_SECOND_SHOT_RETRY_ARTISTIC_QA_PENDING_NOT_FINAL"

def verify(manifest_path:Path, original_dir:Path)->tuple[Path,dict]:
    m=json.loads(manifest_path.read_text(encoding="utf-8"))
    if (m.get("version")!="V251_FIESOLE_SOURCE_LOCKED_PHOTO_HANDOFF"
        or m.get("episode")!=EPISODE or m.get("source_film_sha256")!=FILM_SHA):
        raise ValueError("V263_WRONG_ORIGINAL_FILM")
    shots=m.get("shots",[])
    if len(shots)!=5 or [s.get("shot") for s in shots]!=list(range(1,6)):
        raise ValueError("V263_NOT_FIVE_ORDERED_SHOTS")
    hashes=[s.get("original_sha256") for s in shots]
    if len(set(hashes))!=5 or any(not isinstance(h,str) or len(h)!=64 for h in hashes):
        raise ValueError("V263_NOT_FIVE_UNIQUE_FRAMES")
    row=shots[1]
    name=row.get("archive_filename")
    if (row.get("role")!="I2I_PHOTO_SOURCE" or row.get("source_frame_locked") is not True
        or not isinstance(name,str) or Path(name).name!=name or name.startswith(".")):
        raise ValueError("V263_SHOT_TWO_INVALID")
    source=original_dir/name
    if source.is_symlink() or not source.is_file() or engine.sha(source)!=row["original_sha256"]:
        raise ValueError("V263_SOURCE_BYTES_CHANGED")
    with engine.Image.open(source) as im:
        if im.format!="PNG" or im.size!=(1920,1080):
            raise ValueError("V263_SOURCE_DIMENSIONS")
        im.verify()
    return source,row

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--original-dir",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--offline",action="store_true")
    a=p.parse_args()
    source,row=verify(a.manifest,a.original_dir)
    engine.SOURCE_SHA=row["original_sha256"]
    engine.SOURCE_TIME_S=row["source_time_s"]
    engine.SEED=SEED
    engine.PROMPT=PROMPT
    argv=sys.argv
    try:
        sys.argv=[argv[0],"--source",str(source),"--out",str(a.out)]
        if a.offline:sys.argv.append("--offline")
        engine.main()
    finally:
        sys.argv=argv
    report=a.out/"V257_SOURCE_LOCKED_I2I_QA.json"
    data=json.loads(report.read_text(encoding="utf-8"))
    data.update(version=VERSION,source_frame=row["original_frame"],
        source_time_s=row["source_time_s"],source_shot=2,seed=SEED,
        previous_v254_artistic_rejection="MACHINE_BECAME_PERSON",
        artistic_approval=False,italian_rights_verified=False,
        new_final_episodes_delivered=0,publish_allowed=False,paid_credits_spent=0)
    report.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")

if __name__=="__main__":
    main()
