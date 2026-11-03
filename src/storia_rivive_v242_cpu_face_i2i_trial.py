#!/usr/bin/env python3
"""V242: one FREE CPU GFPGAN facial restoration on authentic Lusitania 1915 frame.
Experimental scene component only; no claim of 4+1, colour, rights or final video.
Public HF CPU Space; no ZeroGPU, Vidu, paid key or retry.
"""
from __future__ import annotations
import argparse, hashlib, json, shutil, os
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw

SOURCE_SHA="716a886ab8583f87d2f9c28e7cb7a236f4243f029e95f29e2cfed85ddf029f10"
SOURCE_DIMS=(608,1080)
SPACE="tkawano/face-restoration"

def digest(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verify_source(path:Path)->None:
    if not path.is_file() or path.is_symlink() or digest(path)!=SOURCE_SHA:
        raise ValueError("V242_ORIGINAL_SOURCE_SHA_MISMATCH")
    with Image.open(path) as im:
        if im.format!="PNG" or im.size!=SOURCE_DIMS:
            raise ValueError("V242_ORIGINAL_SOURCE_IMAGE_INVALID")
        im.verify()

def verify_result(source:Path,result:Path)->dict:
    verify_source(source)
    if not result.is_file() or result.is_symlink() or result.stat().st_size<20000:
        raise ValueError("V242_NO_REAL_GENERATIVE_OUTPUT")
    with Image.open(result) as im:
        im.load()
        dims=im.size
        if min(dims)<512:
            raise ValueError("V242_GENERATED_IMAGE_TOO_SMALL")
        if abs(dims[0]/dims[1]-SOURCE_DIMS[0]/SOURCE_DIMS[1])>.035:
            raise ValueError("V242_RESULT_REFRAMED")
        if im.mode not in ("RGB","RGBA","L"):
            raise ValueError("V242_RESULT_IMAGE_INVALID")
    if digest(source)==digest(result):
        raise ValueError("V242_PROVIDER_RETURNED_ORIGINAL_NOT_I2I")
    return {"result_sha256":digest(result),"result_dimensions":list(dims),
            "real_cpu_model_candidate":1,"color_restoration_complete":False,
            "final_episode":False,"rights_italy_approved":False,
            "vidu_generated":False,"new_final_episodes_delivered":0,
            "artistic_QA_approved":False,"publish_allowed":False}

def unwrap_result(obj):
    if isinstance(obj,str):return Path(obj)
    if isinstance(obj,dict):
        for k in ("path","name","value"):
            if isinstance(obj.get(k),str):return Path(obj[k])
    if isinstance(obj,(tuple,list)):
        for item in obj:
            try:
                p=unwrap_result(item)
                if p.is_file():return p
            except (ValueError,TypeError):pass
    raise ValueError("V242_PROVIDER_NO_DOWNLOADABLE_IMAGE")

def one_call(source:Path,output:Path)->dict:
    verify_source(source)
    from gradio_client import Client,handle_file
    c=Client(SPACE,verbose=False)
    # API metadata is free and allows matching required non-image defaults.
    schema=c.view_api(return_format="dict")
    if not isinstance(schema,dict):
        raise ValueError("V242_PROVIDER_SCHEMA_UNAVAILABLE")
    endpoints=schema.get("named_endpoints",{})
    key="/predict" if "/predict" in endpoints else next(iter(endpoints),"")
    if not key:raise ValueError("V242_NO_PUBLIC_PREDICT_API")
    params=endpoints[key].get("parameters",[])
    if not params or len(params)>5:
        raise ValueError("V242_UNSUPPORTED_PROVIDER_PARAMETERS")
    values=[];has_image=False
    for p in params:
        desc=(str(p.get("component",""))+" "+str(p.get("label",""))+" "+
              str(p.get("parameter_name",""))+" "+str(p.get("type",""))).lower()
        if not has_image and ("image" in desc or "input" in desc or "photo" in desc):
            values.append(handle_file(str(source)));has_image=True
        elif "default" in p and p["default"] is not None:
            values.append(p["default"])
        else:
            raise ValueError("V242_REQUIRED_PROVIDER_PARAMETER_NOT_IDENTIFIED")
    if not has_image:raise ValueError("V242_NO_IMAGE_INPUT")
    result=c.predict(*values,api_name=key)   # exactly ONE external generative request
    actual=unwrap_result(result)
    if not actual.is_file():raise ValueError("V242_PROVIDER_RESULT_NOT_LOCAL")
    shutil.copy2(actual,output)
    return verify_result(source,output)

def comparison(src:Path,generated:Path,out:Path)->None:
    a=Image.open(src).convert("RGB")
    b=Image.open(generated).convert("RGB")
    w=500;h=round(w*SOURCE_DIMS[1]/SOURCE_DIMS[0])
    sheet=Image.new("RGB",(2*w,h+48),(15,15,15))
    sheet.paste(ImageOps.fit(a,(w,h)),(0,48))
    sheet.paste(ImageOps.fit(b,(w,h)),(w,48))
    d=ImageDraw.Draw(sheet)
    d.text((10,12),"ORIGINAL SOURCE 1915 - FRAME SHA LOCKED",fill="white")
    d.text((w+10,12),"CPU GFPGAN I2I - ARTISTIC QA PENDING",fill="white")
    sheet.save(out,quality=92)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",required=True,type=Path)
    ap.add_argument("--out",required=True,type=Path)
    ap.add_argument("--offline",action="store_true")
    a=ap.parse_args()
    a.out.mkdir(parents=True,exist_ok=True)
    verify_source(a.source)
    report={"version":"V242_SOURCE_LOCKED_CPU_GENERATIVE_FACE_RESTORATION_TRIAL",
            "model_space":SPACE,"original_source_sha256":SOURCE_SHA,
            "paid_credits_spent":0,"provider_requests":0,"successful_new_images":0,
            "status":"OFFLINE_SOURCE_CHECK_ONLY","new_final_episodes_delivered":0,
            "publish_allowed":False}
    report_path=a.out/"V242_REAL_MEDIA_QA_NOT_FINAL.json"
    report_path.write_text(json.dumps(report,indent=2)+"\n")
    if a.offline:return
    report["provider_requests"]=1
    try:
        output=a.out/"V242_REAL_CPU_GFP_GAN_FACE_I2I.png"
        report.update(one_call(a.source,output))
        comparison(a.source,output,a.out/"V242_COMPARE_AUTHENTIC_VS_CPU_MODEL.jpg")
        report["successful_new_images"]=1
        report["status"]="NEW_GENUINE_CPU_GENERATIVE_FACE_I2I_NEEDS_VISUAL_REVIEW"
    except Exception as e:
        report["status"]="FREE_CPU_PROVIDER_UNAVAILABLE_NO_NEW_I2I"
        report["error_type"]=type(e).__name__
        # Never re-call the provider on ambiguous outcomes.
        raise
    finally:
        report_path.write_text(json.dumps(report,indent=2)+"\n")
    print(report["status"],"FINAL_EPISODES_0_OF_4")

if __name__=="__main__":main()
