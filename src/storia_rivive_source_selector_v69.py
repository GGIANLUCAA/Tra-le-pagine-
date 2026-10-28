#!/usr/bin/env python3
"""V69: Score TRUE archival source frames for restoration feasibility, then actual AI outputs.
Only measurement and QA: no paid models, no restorer calls, no publication.
Numerical sharpness is NOT verified facial identity or evidence of historically real details.
"""
import argparse, json, math
from pathlib import Path
import cv2, numpy as np

def clamp(x): return max(0.,min(1.,float(x)))

def image(path):
    im=cv2.imread(str(path))
    if im is None:raise ValueError("Image unavailable: "+str(path))
    return im

def source_metrics(frame,subject_box=None):
    h,w=frame.shape[:2]
    if min(h,w)<20:raise ValueError("Image too small")
    gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    if w>640:gray=cv2.resize(gray,(640,round(h*640/w)),interpolation=cv2.INTER_AREA)
    lap=float(cv2.Laplacian(gray,cv2.CV_32F).var())
    dx=cv2.Sobel(gray,cv2.CV_32F,1,0,ksize=3)
    dy=cv2.Sobel(gray,cv2.CV_32F,0,1,ksize=3)
    grad=float(np.sqrt(dx*dx+dy*dy).mean())
    detail=clamp(.55*(math.log1p(lap)-2.7)/3.9+.45*(grad-11)/34)
    lo,hi=np.percentile(gray,[2,98])
    clip=float(np.mean((gray<9)|(gray>247)))
    exposure=clamp((hi-lo)/140)*clamp(1-clip/.3)
    # Actual pixels after a full-height vertical crop, NOT artificially exported resolution.
    cropwidth=min(w,round(h*9/16))
    crop_pixels=cropwidth*h
    raster=clamp(math.log2(max(1,crop_pixels)/(324*576))/4+.28)
    subject_pixels=[0,0];subject_scale=0.;occupancy=0.
    if subject_box is not None:
        if len(subject_box)!=4:raise ValueError("subject_box needs [x,y,width,height] normalized")
        x,y,bw,bh=map(float,subject_box)
        if min(x,y,bw,bh)<0 or bw<=0 or bh<=0 or x+bw>1.001 or y+bh>1.001:
            raise ValueError("Invalid subject_box")
        subject_pixels=[int(w*bw),int(h*bh)]
        subject_scale=clamp(min(subject_pixels[0]/90,subject_pixels[1]/140))
        occupancy=clamp(bw*bh*7)
    # Face detector is ONLY advisory, never a source identity verification.
    faces=[]
    if hasattr(cv2,"data") and hasattr(cv2,"CascadeClassifier"):
        cascade=cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_frontalface_default.xml")
        if not cascade.empty():
            for x,y,fw,fh in cascade.detectMultiScale(gray,1.18,5,minSize=(25,25)):
                faces.append(int(fw*w/gray.shape[1]))
    face=clamp(max(faces,default=0)/80)
    score=100*(.20*raster+.23*detail+.11*exposure+.18*subject_scale+
               .14*occupancy+.14*face)
    return {"original_raster_px":[w,h],"usable_vertical_crop_px":[cropwidth,h],
        "crop_source_pixels":crop_pixels,"normalized_detail":round(detail,3),
        "exposure":round(exposure,3),"original_crop_resolution":round(raster,3),
        "subject_original_pixels":subject_pixels,"subject_pixel_scale":round(subject_scale,3),
        "subject_occupancy":round(occupancy,3),
        "faces_detected_advisory":len(faces),"detected_face_width_px":faces,
        "source_quality_score_100":round(score,1),
        "warning":"Pixel count and automatic sharpness do not certify real detail, identity, or restoration WOW."}

def structure(source,restored):
    def coarse(im):
        im=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
        im=cv2.resize(im,(72,128),interpolation=cv2.INTER_AREA)
        return cv2.GaussianBlur(im,(9,9),0).astype(np.float32)
    a,b=coarse(source),coarse(restored)
    if a.std()<.01 or b.std()<.01:return 0.
    return round(float(np.corrcoef(a.ravel(),b.ravel())[0,1]),4)

REVIEW_WEIGHTS={"faces":.22,"skin_hair_clothes":.16,"objects_architecture":.11,
                "natural_photograph":.16,"same_people_geometry":.22,"wow_emotion":.13}
def review_score(r):
    if r.get("actually_compared_by_reviewer") is not True or r.get("no_new_people") is not True:
        raise ValueError("Image-level review / no invented people confirmation is required")
    for key in REVIEW_WEIGHTS:
        if key not in r or not isinstance(r[key],(float,int)) or not 0<=r[key]<=5:
            raise ValueError("Real 0..5 human review missing: "+key)
    if r["same_people_geometry"]<3:
        raise ValueError("Photo changes people/poses too much; refuse")
    return round(20*sum(r[k]*v for k,v in REVIEW_WEIGHTS.items()),1)

def evaluate(plan):
    results=[]
    for c in plan["candidates"]:
        id=c["id"]
        # Fail closed: PD-USA alone does not automatically clear Italian publication.
        if not c.get("rights_territories_checked") or c.get("license") not in ("CC0","PDM","PUBLIC_DOMAIN"):
            results.append({"id":id,"eligible":False,"why":"License/territory not verified"});continue
        if c.get("true_scan_vs_upscale_checked") is not True:
            results.append({"id":id,"eligible":False,"why":"Unverified original scan vs software upscaling"});continue
        if c.get("actuality_not_staged") is not True:
            results.append({"id":id,"eligible":False,"why":"Cinema fiction/reconstruction must not be misrepresented as actuality"});continue
        source=image(c["source_frame_path"])
        base=source_metrics(source,c.get("subject_box"))
        hook=c.get("editorial_wow_0_5")
        if not isinstance(hook,(int,float)) or not 0<=hook<=5:
            raise ValueError("editorial_wow_0_5 required, 0..5")
        scout=round(.65*base["source_quality_score_100"]+.35*hook*20,1)
        ai_score=None;struct=None
        if c.get("restored_image_path"):
            struct=structure(source,image(c["restored_image_path"]))
            if struct<.80:
                results.append({"id":id,"eligible":False,"why":"Generative output significantly changed source geometry","structural_similarity":struct});continue
            ai_score=review_score(c.get("actual_restoration_review") or {})
        final=round(.35*base["source_quality_score_100"]+.55*ai_score+.10*hook*20,1) if ai_score is not None else None
        results.append({"id":id,"eligible":True,"quality":base,
            "editorial_wow_assessment":hook,
            "pre_restoration_scout_score_100":scout,
            "after_real_ai_and_human_review_100":final,
            "structural_similarity":struct,
            "stage":"REVIEWED_AI_CANDIDATE" if final is not None else "SCOUT_ONLY_UNAPPROVED"})
    results.sort(key=lambda c:(c.get("after_real_ai_and_human_review_100") is not None,
                 c.get("after_real_ai_and_human_review_100") or c.get("pre_restoration_scout_score_100",0)),reverse=True)
    return {"selector":"STORIA_RIVIVE_V69","results":results,
        "approval":"Only a completed actual AI restoration and visual review may authorize final production.",
        "cost":"No API requests or paid inference."}

def main():
    p=argparse.ArgumentParser(description="Choose historical source frames for future wow restoration")
    p.add_argument("--plan",required=True);p.add_argument("--out")
    a=p.parse_args()
    report=evaluate(json.loads(Path(a.plan).read_text(encoding="utf-8")))
    txt=json.dumps(report,ensure_ascii=False,indent=2)+"\n"
    if a.out:Path(a.out).write_text(txt,encoding="utf-8")
    print(txt)

if __name__=="__main__":main()
