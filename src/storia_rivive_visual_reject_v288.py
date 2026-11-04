#!/usr/bin/env python3
"""La Storia Rivive V288: SHA-locked, visually verified rejection of bad restorations.

Designed to fail closed on a KNOWN bad source (human/animal fusion).
No claim to automatically detect all errors in future frames.
No provider requests, purchases, publishing, or false human approvals.
"""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path

DEFAULT_LEDGER=Path(__file__).resolve().parents[1]/"queue"/"storia_rivive_rejected_visual_frames_v288.json"
SHA=re.compile(r"^[0-9a-f]{64}$")
EPISODE=re.compile(r"^[a-z0-9][a-z0-9_]{5,100}$")

def file_sha(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()

def read_ledger(path:Path=DEFAULT_LEDGER)->dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError("V288_VISUAL_REJECTION_LEDGER_MISSING")
    ledger=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(ledger,dict) or ledger.get("version")!="V288_EDITORIAL_REJECTION_LEDGER":
        raise ValueError("V288_REJECTION_LEDGER_UNTRUSTED")
    entries=ledger.get("rejections")
    if not isinstance(entries,list):
        raise ValueError("V288_REJECTIONS_NOT_LIST")
    for entry in entries:
        if not isinstance(entry,dict):
            raise ValueError("V288_INVALID_REJECTION_ENTRY")
        if not EPISODE.fullmatch(str(entry.get("episode_id",""))):
            raise ValueError("V288_BAD_EPISODE")
        if any(not SHA.fullmatch(str(entry.get(k,""))) for k in
           ("original_frame_sha256","rejected_restored_photo_sha256")):
            raise ValueError("V288_BAD_SOURCE_OR_IMAGE_SHA")
        if (entry.get("block_photo_reveal") is not True or
            entry.get("block_vidu_source_for_paid_generation") is not True or
            entry.get("human_artistic_approved") is not False or
            entry.get("publication_approved") is not False):
            raise ValueError("V288_UNSAFE_REJECTION_POLICY")
    return ledger

def inspect(episode_id:str,source_sha256:str,photo_sha256:str|None=None,role="photo",
            ledger_path:Path=DEFAULT_LEDGER)->dict:
    if not EPISODE.fullmatch(episode_id) or not SHA.fullmatch(source_sha256):
        raise ValueError("V288_BAD_SOURCE_IDENTITY")
    if photo_sha256 is not None and not SHA.fullmatch(photo_sha256):
        raise ValueError("V288_BAD_PHOTO_SHA")
    if role not in ("photo","vidu_source","original_bw_motion"):
        raise ValueError("V288_BAD_MEDIA_ROLE")
    entries=read_ledger(ledger_path)["rejections"]
    hits=[r for r in entries if r["episode_id"]==episode_id and (
        r["original_frame_sha256"]==source_sha256 or (
            photo_sha256 is not None and
            r["rejected_restored_photo_sha256"]==photo_sha256))]
    if not hits:
        return {"status":"UNKNOWN_NEEDS_ARTISTIC_VISUAL_QA",
                "known_bad_match":False,"approved":False,"publish_allowed":False}
    decision=hits[0]
    if role=="original_bw_motion" and decision.get("allow_original_black_and_white_motion_only") is True:
        return {"status":"ORIGINAL_BW_MOTION_ONLY_WITHOUT_COLOR_APPROVAL",
                "known_bad_match":True,"approved":False,"publish_allowed":False}
    return {"status":"REJECT_REPLACE_FRAME",
            "known_bad_match":True,"approved":False,"publish_allowed":False,
            "error":"HUMAN_ANIMAL_HEAD_AND_SHOULDER_FUSION",
            "next_step":decision["what_to_do"]}

def require_safe_for_photo(episode_id,source_sha256,photo_sha256,
                           ledger_path:Path=DEFAULT_LEDGER)->None:
    result=inspect(episode_id,source_sha256,photo_sha256,"photo",ledger_path)
    if result["known_bad_match"]:
        raise ValueError("V288_REJECTED_VISIBLE_HUMAN_ANIMAL_FUSION_REPLACE_FRAME")
    # No automatic approval: unknown frames still require visual inspection.

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--episode",required=True)
    p.add_argument("--source-sha256",required=True)
    p.add_argument("--photo-file",type=Path)
    p.add_argument("--role",choices=["photo","vidu_source","original_bw_motion"],default="photo")
    p.add_argument("--ledger",type=Path,default=DEFAULT_LEDGER)
    a=p.parse_args()
    photo_sha=None
    if a.photo_file:
        if not a.photo_file.is_file() or a.photo_file.is_symlink():
            raise ValueError("V288_PHOTO_FILE_MISSING")
        photo_sha=file_sha(a.photo_file)
    result=inspect(a.episode,a.source_sha256,photo_sha,a.role,a.ledger)
    print(json.dumps(result,ensure_ascii=False,sort_keys=True))
    return 2 if result["status"]=="REJECT_REPLACE_FRAME" else 0

if __name__=="__main__":
    raise SystemExit(main())
