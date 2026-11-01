#!/usr/bin/env python3
"""V101: rank authentic original frames for likely restorable detail.
No facial identification, generation, source-frame timecode assertion or artistic approval.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from PIL import Image,ImageOps,ImageFilter,ImageStat

def measure(path):
    with Image.open(path) as raw:
        w,h=raw.size
        gray=ImageOps.grayscale(raw).resize((256,256))
    contrast=ImageStat.Stat(gray).stddev[0]
    detail=ImageStat.Stat(gray.filter(ImageFilter.FIND_EDGES)).stddev[0]
    mean=ImageStat.Stat(gray).mean[0]
    exposure=max(0.0,1-abs(mean-126)/126)
    native_crop_w=min(w,round(h*9/16))
    source_pixel_ratio=min(1.0,(native_crop_w*h)/(720*1280))
    score=round(0.28*min(1,contrast/75)+0.30*min(1,detail/75)+
                0.12*exposure+0.30*source_pixel_ratio,4)
    return {"filename":path.name,"raster_px":[w,h],"native_portrait_crop_px":[native_crop_w,h],
            "contrast_advisory":round(contrast,2),"edge_detail_advisory":round(detail,2),
            "source_visual_quality_score":score,"face_identity_verified":False,
            "historical_shot_distinctness_verified":False,"approved_for_i2i":False}

def portrait_dhash(path):
    """64-bit visual fingerprint of the actual central 9:16 crop.

    This is a conservative duplicate-screening heuristic, NOT evidence that
    two film frames belong to different camera shots. Brightness-only changes
    intentionally retain the same fingerprint.
    """
    with Image.open(path) as raw:
        gray=ImageOps.grayscale(raw)
        w,h=gray.size
        crop_w=min(w,round(h*9/16))
        x=(w-crop_w)//2
        pixels=list(gray.crop((x,0,x+crop_w,h)).resize(
            (9,8),Image.Resampling.LANCZOS).getdata())
    value=0
    for y in range(8):
        for x in range(8):
            value=(value<<1)|int(pixels[y*9+x]>pixels[y*9+x+1])
    return value


def rank(folder):
    folder=Path(folder)
    imgs=sorted(folder.glob("frame_*.png"))
    if not imgs:raise ValueError("No native archival source PNG frames to evaluate")
    scored=[measure(p) for p in imgs]
    fingerprints=[portrait_dhash(p) for p in imgs]
    # Reserve different time positions; scores do not prove distinct camera shots.
    ranked=sorted(range(len(scored)),key=lambda n:(-scored[n]["source_visual_quality_score"],n))
    chosen=[]
    separation=max(1,len(scored)//6)
    for idx in ranked:
        if (all(abs(idx-v)>=separation for v in chosen) and
                all((fingerprints[idx]^fingerprints[v]).bit_count()>=12 for v in chosen)):
            chosen.append(idx)
        if len(chosen)>=5:break
    if len(chosen)<5:
        return {"status":"SOURCE_TOO_FEW_VISUALLY_DIVERSE_CANDIDATE_FRAMES",
                "candidates":scored,"preselected":[],
                "approved_restored_photos":0,
                "visual_diversity_is_only_a_heuristic":True,
                "next":"Find a more visually varied authentic film or manually review five real moving shots; do not start I2I or Vidu"}
    selected=[scored[n] for n in sorted(chosen)]
    return {"status":"FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW",
            "original_source_frames":len(scored),"preselected":selected,
            "all_candidates":scored,"approved_restored_photos":0,
            "selection_is_not_verified_distinct_film_shots":True,
            "visual_diversity_heuristic":"central 9:16 64-bit dHash, minimum Hamming distance 12; NOT shot verification",
            "next":"Review authentic source clip for five distinct moving shots, true timecodes and facial details before I2I"}

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--frames",required=True);p.add_argument("--out",required=True)
    a=p.parse_args();out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    try:data=rank(a.frames)
    except Exception as e:data={"status":"SOURCE_FRAME_SELECTION_BLOCKED","error":str(e)[:300],"preselected":[]}
    out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
    print(data["status"],len(data["preselected"]))
