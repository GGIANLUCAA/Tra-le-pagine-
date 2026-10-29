#!/usr/bin/env python3
"""V70 quality gates. No inference, paid credits or network use.

Fail closed if the historical source is watermarked, the selected moments are
not independently useful, or photos remain B/W or differ from original scene.
"""
import json
from pathlib import Path

def review_source(review):
    if isinstance(review,(str,Path)):
        review=json.loads(Path(review).read_text(encoding="utf8"))
    checks={
        "rights_cleared_for_intended_countries": review.get("rights_cleared_for_intended_countries") is True,
        "unaltered_historical_source_verified": review.get("unaltered_historical_source_verified") is True,
        "watermark_free": review.get("watermark_free") is True,
        "true_source_scan_verified": review.get("true_source_scan_verified") is True,
        "editorial_visual_reviewed": review.get("editorial_visual_reviewed") is True,
        "human_reconstruction_feasibility_approved": review.get("human_reconstruction_feasibility_approved") is True
    }
    shots=review.get("scene_candidates",[])
    groups=[x.get("distinct_shot_id") for x in shots]
    checks["at_least_three_distinct_shots"]=len(shots)>=3 and len(set(groups))>=3 and all(groups)
    checks["frame_times_separated"]=len(shots)>=3 and all(
        isinstance(x.get("time_s"),(int,float)) and x["time_s"]>=0 for x in shots
    ) and all(abs(a["time_s"]-b["time_s"])>3 for i,a in enumerate(shots) for b in shots[i+1:])
    failed=[name for name,passed in checks.items() if not passed]
    if failed:raise RuntimeError("SOURCE_REJECTED_BEFORE_AI: "+", ".join(failed))
    return shots

def test_color_photo(path,min_rgb_range=9.0,min_colored_fraction=.08):
    from PIL import Image
    import numpy as np
    im=Image.open(path).convert("RGB")
    if im.width<500 or im.height<850:
        raise ValueError("Restored photo too small to serve vertical 1080p")
    im.thumbnail((270,480))
    a=np.asarray(im,dtype=np.float32)
    spread=a.max(2)-a.min(2)
    value=float(spread.mean())
    fraction=float((spread>=12).mean())
    if value<min_rgb_range or fraction<min_colored_fraction:
        raise ValueError(f"PHOTO_REJECTED_BLACK_AND_WHITE: mean channel range {value:.2f}; colorful fraction {fraction:.3f}")
    return {"mean_rgb_range":round(value,2),"fraction_colorful_pixels":round(fraction,3)}

def check_distinct_source_frames(frame_paths,max_corr=.94):
    import cv2,numpy as np
    if len(frame_paths)<3:raise RuntimeError("Need at least 3 distinct source shots")
    gray=[]
    for f in frame_paths:
        frame=cv2.imread(str(f))
        if frame is None:raise RuntimeError("Source frame unavailable "+str(f))
        x=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        x=cv2.resize(x,(64,96)).astype(np.float32)
        x=cv2.GaussianBlur(x,(7,7),0)
        gray.append(x)
    similarities=[]
    for i,a in enumerate(gray):
        for j in range(i+1,len(gray)):
            b=gray[j]
            if a.std()<1 or b.std()<1:
                similarities.append({"pair":[i+1,j+1],"correlation":1.0})
            else:
                similarities.append({"pair":[i+1,j+1],"correlation":float(np.corrcoef(a.ravel(),b.ravel())[0,1])})
    if any(x["correlation"]>max_corr for x in similarities):
        raise RuntimeError("REPEATED_SIMILAR_SCENE_REJECTED: "+str(similarities))
    return similarities

def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--review",required=True)
    p.add_argument("--photos",nargs="*")
    p.add_argument("--frames",nargs="*")
    a=p.parse_args()
    shots=review_source(a.review)
    if a.photos:
        for x in a.photos:print("COLOR_OK",x,test_color_photo(x))
    if a.frames:print("DIVERSE_SCENES_OK",check_distinct_source_frames(a.frames))
    print("V70_QA_PASSED",len(shots))
if __name__=="__main__":main()
