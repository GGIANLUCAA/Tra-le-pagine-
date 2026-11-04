#!/usr/bin/env python3
"""V193 ONE genuinely generative I2I photo test from verified V191 film frame.

Use a PUBLIC anonymous ZeroGPU Space only (no token, no payment), submit
exactly ONE photograph-edit call, NEVER retry; fail closed on quota/errors.
No Vidu, no final film, no editorial approval. Preserve source SHA chain.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil

from PIL import Image, ImageOps, ImageFilter, ImageStat

SCENE = 3  # banquet: real distinct historical-film shot
SCENE_NAME = "03_banquet_last_real_film_frame.png"
SOURCE_SHA = "927dd324df4f88ef0dd12b31ccf0aade9fa901875ffcc5b688f74ecc57e1d32f"
SPACE = "JEYASEKHAR/QWEN_EDIT_IMAGE"
PROMPT = (
    "Carefully image-edit THIS EXACT 1909 monochrome banquet movie frame into a"
    " natural-color ultra-photorealistic historic documentary photograph. The"
    " SAME guests, SAME facial identities and poses, hands, serving utensils,"
    " tablecloth and flowers, and the SAME background painting must occupy the"
    " EXACT same positions and proportions. Authentic early-1900s clothing,"
    " delicately lifelike skin and natural color under soft room light. Restore"
    " only recoverable real detail and gently clean film dirt. It is critical"
    " NOT to change anyone's face, mouth, fingers, gaze, head, expression,"
    " clothing or location. Maintain identical original perspective, DO NOT"
    " invent people, objects, architecture, or change the composition. NO"
    " orange tint, sepia, illustration, unrealistic sharpened textures,"
    " letters or logos. Natural photorealism, film historical restoration."
)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verified_source(source, handoff):
    source = Path(source)
    if source.is_symlink() or not source.is_file() or source.name != SCENE_NAME:
        raise ValueError("ORIGINAL_BANQUET_SOURCE_MISSING_OR_UNTRUSTED")
    data=json.loads(Path(handoff).read_text(encoding="utf-8"))
    if (data.get("version")!="V191_TRUE_PHOTOGRAPHIC_I2I_PREPARATION"
        or data.get("i2i_generated") != 0 or data.get("vidu_generated") != 0
        or data.get("publish_permitted") is not False
        or data.get("source_raster_effective_unscaled_pixels") != [603,1072]
        or data.get("film_source_sha256")!="eacbb947105f9143632e3d4e933ee5e200ba98f5d588c11c552dfb94787de1d9"):
        raise ValueError("V191_SOURCE_HANDOFF_INVALID")
    entry = data.get("photo_i2i_jobs",[])[SCENE-1]
    if entry.get("scene")!=SCENE or entry.get("source_file")!=SCENE_NAME:
        raise ValueError("SOURCE_ROLE_CHANGED")
    if sha(source)!=entry.get("source_sha256") or sha(source)!=SOURCE_SHA:
        raise ValueError("SOURCE_FRAME_SHA_CHANGED")
    with Image.open(source) as im:
        im.verify()
    with Image.open(source) as im:
        if im.size != (720,1280):
            raise ValueError("SOURCE_PNG_DIMENSIONS_INVALID")
    return entry


def source_similarity(source, output):
    with Image.open(source) as a, Image.open(output) as b:
        if b.format != "PNG" and b.format != "JPEG" and b.format != "WEBP":
            raise ValueError("I2I_NOT_IMAGE")
        if min(b.size)<850:
            raise ValueError("I2I_TOO_SMALL")
        a=a.convert("RGB").resize((120,214))
        b=b.convert("RGB").resize((120,214))
        gray_a=ImageOps.grayscale(a).filter(ImageFilter.GaussianBlur(2.0))
        gray_b=ImageOps.grayscale(b).filter(ImageFilter.GaussianBlur(2.0))
        import numpy as np
        x=np.asarray(gray_a,dtype="float64").ravel()
        y=np.asarray(gray_b,dtype="float64").ravel()
        corr=float(np.corrcoef(x,y)[0,1]) if x.std()>0 and y.std()>0 else 0.
        saturation=float(ImageStat.Stat(b.convert("HSV")).mean[1])
    return {"low_frequency_luma_correlation":round(corr,4),
            "mean_saturation_0_255":round(saturation,1),
            "structure_needs_visual_review":True,
            "subject_identity_artistically_verified":False,
            "technical_color_candidate_only":corr>=.65 and saturation>=12}


def run(source, handoff, out):
    source=Path(source);out=Path(out)
    if out.exists() or any(p.is_symlink() for p in out.parents):
        raise ValueError("OUTPUT_EXISTS_OR_SYMLINK")
    verified_source(source,handoff)
    out.mkdir(parents=True)
    report={"version":"V193","scene":SCENE,"status":"FREE_I2I_NOT_SUBMITTED",
        "source_file":SCENE_NAME,"source_sha256":SOURCE_SHA,
        "provider_model":"Qwen-Image-Edit-2511","space":SPACE,
        "unauthenticated_public_zero_gpu":True,"provider_calls":0,
        "paid_provider_calls":0,"credits_spent":0,
        "real_generatively_restored_photo":False,
        "artistically_approved":False,"same_faces_hands_objects_verified":False,
        "rights_italy_verified":False,"final_video_created":False,
        "publish_permitted":False,
        "error_type":None,
        "blocking_issues":["SINGLE_I2I_EXPERIMENT_ONLY",
            "THREE_MORE_I2I_MISSING","VIDU_MISSING",
            "HUMAN_VISUAL_FIDELITY_REVIEW_PENDING",
            "ITALY_RIGHTS_PENDING","FINAL_QA_MISSING"]}
    def save():
        (out/"V193_ONE_REAL_I2I_RESULT.json").write_text(json.dumps(report,indent=2)+"\n")
    save()
    report["provider_calls"]=1  # persist BEFORE external submit; NEVER auto retry.
    report["status"]="FREE_PUBLIC_I2I_ONE_REQUEST_IN_PROGRESS"
    save()
    try:
        from gradio_client import Client, handle_file
        client=Client(SPACE,verbose=False)
        result=client.predict(
            image=handle_file(str(source)),prompt=PROMPT,
            lora_adapter="",image2=None,seed=191,randomize_seed=False,
            guidance_scale=1.0,steps=4,preserve_identity=True,
            identity_strength=90,output_size=1024,fix_hands=False,
            api_name="/edit")
        target = result[0] if isinstance(result,(list,tuple)) else result
        if isinstance(target,dict):
            target=target.get("path")
        if not isinstance(target,str):
            raise ValueError("GENERATOR_DID_NOT_RETURN_AN_IMAGE_FILE")
        file=Path(target)
        if not file.is_file() or file.stat().st_size<15000:
            raise ValueError("GENERATOR_RETURN_MISSING_OR_EMPTY")
        with Image.open(file) as im:
            im.verify()
        with Image.open(file) as im:
            im.convert("RGB").save(out/"SCENE03_REAL_GENERATIVE_I2I_CANDIDATE.png",format="PNG")
        photo=out/"SCENE03_REAL_GENERATIVE_I2I_CANDIDATE.png"
        metrics=source_similarity(source,photo)
        report["technical_metrics"]=metrics
        report["photo_sha256"]=sha(photo)
        report["real_generatively_restored_photo"]=True
        report["status"]="REAL_I2I_CANDIDATE_ART_QA_PENDING" if metrics["technical_color_candidate_only"] else "REAL_I2I_CANDIDATE_TECH_REJECT"
        # A technically generated image is NEVER an approved restoration.
        original=Image.open(source).convert("RGB").resize((360,640))
        restored=Image.open(photo).convert("RGB").resize((360,640))
        sheet=Image.new("RGB",(720,640),"#131313")
        sheet.paste(original,(0,0));sheet.paste(restored,(360,0))
        sheet.save(out/"V193_BW_VS_TRUE_I2I_COMPARISON.jpg",quality=89)
    except Exception as exc:
        report["status"]="FREE_ZERO_GPU_UNAVAILABLE_OR_ERROR_NO_RETRY"
        report["error_type"]=type(exc).__name__
        report["error_summary"]=str(exc)[:200]
    save()
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--handoff",required=True)
    p.add_argument("--out",required=True)
    x=p.parse_args()
    r=run(x.source,x.handoff,x.out)
    print("V193",r["status"],"real_i2i",r["real_generatively_restored_photo"],
          "free_attempts",r["provider_calls"],"paid_calls",r["paid_provider_calls"])
    return 0  # a failed provider request is a meaningful recorded result, NOT success.


if __name__=="__main__":
    raise SystemExit(main())
