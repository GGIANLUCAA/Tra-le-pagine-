#!/usr/bin/env python3
"""V255: independent byte-level QA of V254's REAL locally generated I2I.
Never converts a candidate into a final episode or artistic approval.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
from PIL import Image, ImageChops, ImageFilter, ImageStat

def digest(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def assess(source:Path,candidate:Path,report:Path,out:Path)->dict:
    r=json.loads(report.read_text())
    if (r.get("status")!="ONE_TRUE_LOCAL_I2I_PHOTO_NEEDS_ARTISTIC_REVIEW_NOT_FINAL"
        or r.get("new_generated_i2i")!=1
        or r.get("provider_requests")!=0
        or r.get("vidu_credit_spend")!=0
        or r.get("publish_allowed") is not False
        or r.get("final_mp4") is not False):
        raise ValueError("V255_NO_VERIFIED_REAL_LOCAL_I2I_CANDIDATE")
    if source.is_symlink() or candidate.is_symlink() or not source.is_file() or not candidate.is_file():
        raise ValueError("V255_INVALID_MEDIA_PATH")
    if (digest(source)!=r.get("source_crop_sha256")
        or digest(candidate)!=r.get("candidate_sha256")):
        raise ValueError("V255_SOURCE_OR_OUTPUT_HASH_MISMATCH")
    with Image.open(source) as a, Image.open(candidate) as b:
        if a.format!="PNG" or b.format!="PNG" or a.size!=(512,896) or b.size!=(512,896):
            raise ValueError("V255_IMAGE_GEOMETRY_MISMATCH")
        src=a.convert("RGB")
        img=b.convert("RGB")
        src_gray=src.convert("L")
        img_gray=img.convert("L")
        rgb=ImageStat.Stat(img).mean
        color_diff=sum(ImageStat.Stat(ImageChops.difference(img.getchannel(c1),img.getchannel(c2))).mean[0] for c1,c2 in (("R","G"),("G","B"),("R","B")))/3
        delta=ImageStat.Stat(ImageChops.difference(src,img)).mean
        edges_a=src_gray.filter(ImageFilter.FIND_EDGES).resize((128,224))
        edges_b=img_gray.filter(ImageFilter.FIND_EDGES).resize((128,224))
        edge_mae=ImageStat.Stat(ImageChops.difference(edges_a,edges_b)).mean[0]
        brightness=sum(rgb)/3
        output={"version":"V255_REAL_I2I_BYTE_QA",
                "source_sha256":digest(source),"candidate_sha256":digest(candidate),
                "candidate_rgb_means":[round(x,2) for x in rgb],
                "color_channel_difference_mean":round(color_diff,3),
                "source_to_candidate_rgb_mae":round(sum(delta)/3,3),
                "source_to_candidate_edge_mae":round(edge_mae,3),
                "brightness":round(brightness,2),
                "has_visible_color":color_diff>3.0,
                "not_blank":10<brightness<245,
                "not_unchanged_source":sum(delta)/3>7.0,
                "human_artistic_approved":False,"italian_rights_verified":False,
                "final_mp4":False,"final_zip":False,"new_final_episodes_delivered":0,
                "publish_allowed":False}
        output["technical_candidate_pass"]=all(output[k] for k in ("has_visible_color","not_blank","not_unchanged_source"))
        output["status"]="TECHNICALLY_PLAUSIBLE_ARTISTIC_QA_PENDING" if output["technical_candidate_pass"] else "REJECTED_TECHNICAL_COLOR_OR_BLANKNESS"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(output,indent=2)+"\n")
    return output

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for name in ("source","candidate","report","out"):p.add_argument("--"+name,required=True,type=Path)
    a=p.parse_args()
    r=assess(a.source,a.candidate,a.report,a.out)
    print("V255",r["status"],"NEW_FINAL_0_OF_4")
    if not r["technical_candidate_pass"]:raise SystemExit(1)
