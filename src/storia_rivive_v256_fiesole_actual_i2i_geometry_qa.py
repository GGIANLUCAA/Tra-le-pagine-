#!/usr/bin/env python3
"""V256: compare *actual* V255 Fiesole hands I2I with its source, region by region.
Reject invented scene geometry; never infer rights or artistic approval.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw,ImageOps,ImageStat

ORIGINAL_SHA="1d77c757e3193bc9c046f2ae10baebb49a3b71fe379ed359b18e761956f4afb0"
SOURCE_TIME=62.639
def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda:f.read(1048576),b""):h.update(chunk)
    return h.hexdigest()

def corr(a,b):
    x=list(a.getdata());y=list(b.getdata())
    n=len(x); ax=sum(x)/n;ay=sum(y)/n
    cov=sum((u-ax)*(v-ay) for u,v in zip(x,y))
    vx=sum((u-ax)**2 for u in x)
    vy=sum((v-ay)**2 for v in y)
    return cov/max(1.0,math.sqrt(vx*vy))

def assess(original:Path,candidate:Path,report:Path,out:Path):
    if any(p.is_symlink() or not p.is_file() for p in (original,candidate,report)):
        raise ValueError("V256_MISSING_OR_SYMLINK_MEDIA")
    if sha(original)!=ORIGINAL_SHA:raise ValueError("V256_ORIGINAL_FRAME_SHA_MISMATCH")
    r=json.loads(report.read_text())
    if (r.get("original_source_sha256")!=ORIGINAL_SHA
        or r.get("source_time_s")!=SOURCE_TIME
        or r.get("actual_generated_photos")!=1
        or r.get("generated_sha256")!=sha(candidate)
        or r.get("real_vidu_clips")!=0
        or r.get("artistic_approval") is not False
        or r.get("publish_allowed") is not False):
        raise ValueError("V256_NOT_ONE_REAL_UNAPPROVED_V255_IMAGE")
    with Image.open(original) as src,Image.open(candidate) as gen:
        if src.format!="PNG" or src.size!=(1920,1080) or gen.format!="PNG" or gen.size!=(448,800):
            raise ValueError("V256_IMAGE_FORMAT_OR_GEOMETRY")
        source=src.convert("RGB").crop((656,0,1264,1080)).resize((448,800),Image.Resampling.LANCZOS)
        generated=gen.convert("RGB")
    # Grayscale structural correlations by 4x4 local region: false new figures
    # cannot be hidden by globally plausible colors or attractive sharpness.
    a=ImageOps.grayscale(source).resize((112,200),Image.Resampling.BILINEAR)
    b=ImageOps.grayscale(generated).resize((112,200),Image.Resampling.BILINEAR)
    patches=[]
    for row in range(4):
        for col in range(4):
            box=(col*28,row*50,(col+1)*28,(row+1)*50)
            patches.append(round(corr(a.crop(box),b.crop(box)),4))
    global_corr=round(corr(a,b),4)
    weak=sum(x<0.15 for x in patches)
    color=round(ImageStat.Stat(generated.convert("HSV")).mean[1],2)
    # Conservative reject threshold: an AI may look photographic but change scene.
    # Even a pass is only permission to REVIEW, never auto-accept.
    plausible=global_corr>=0.48 and weak<=3 and min(patches)>=-0.1 and color>=12
    heat=ImageChops.difference(a,b).resize((448,800),Image.Resampling.NEAREST)
    sheet=Image.new("RGB",(1344,835),"#161616")
    for i,img in enumerate((source,generated,heat.convert("RGB"))):
        sheet.paste(img,(448*i,35))
    d=ImageDraw.Draw(sheet)
    for i,label in enumerate(("ORIGINAL FIESOLE 1912","V255 ACTUAL I2I - UNAPPROVED","GEOMETRY DIFFERENCE")):
        d.text((448*i+10,10),label,fill="white")
    for row in range(4):
        for col in range(4):
            v=patches[row*4+col]
            x=448+col*112;y=35+row*200
            d.rectangle((x,y,x+111,y+199),outline="#ff4444" if v<.15 else "#bbbbbb",width=2)
            d.text((x+6,y+6),f"{v:+.2f}",fill="white")
    out.mkdir(parents=True,exist_ok=True)
    sheet.save(out/"V256_ACTUAL_V255_GEOMETRY_16_PATCH_REVIEW.jpg",quality=90)
    status={"version":"V256_FIESOLE_V255_REAL_I2I_STRUCTURAL_QA",
        "original_sha256":sha(original),"candidate_sha256":sha(candidate),
        "global_luma_correlation":global_corr,"patch_correlations":patches,
        "weak_patch_count":weak,"candidate_saturation":color,
        "source_geometry_screen_pass":plausible,
        "status":"STRUCTURAL_SCREEN_PASS_ARTISTIC_QA_REQUIRED" if plausible else "REJECTED_OR_REVIEW_REQUIRED_SOURCE_GEOMETRY",
        "artistic_approval":False,"italian_rights_verified":False,
        "vidu_generated":False,"final_mp4":False,"final_zip":False,
        "publish_allowed":False,"new_final_episodes_delivered":0}
    (out/"V256_V255_SOURCE_GEOMETRY_QA_NOT_FINAL.json").write_text(json.dumps(status,indent=2)+"\n")
    return status

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for k in ("original","candidate","report","out"):p.add_argument("--"+k,required=True,type=Path)
    a=p.parse_args()
    result=assess(a.original,a.candidate,a.report,a.out)
    print(result["status"],"CORR",result["global_luma_correlation"],"WEAK",result["weak_patch_count"],"FINAL_0_OF_4")
