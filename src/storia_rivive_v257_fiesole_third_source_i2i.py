#!/usr/bin/env python3
"""V257: one actual, unpaid, local diffusion image-to-image test on authentic Fiesole 1912.

Source: V251 exact film frame, t=62.639s, hands weaving straw. Unlike
DDColor/GFPGAN this is a true instruction-guided diffusion I2I model.
Uses GitHub CPU runner (no Vidu, ZeroGPU, HF paid credits or secret).
Editorial candidate only: source rights / model hallucinations / final QA pending.
"""
from __future__ import annotations
import argparse,hashlib,json,os,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps,ImageStat

SOURCE_SHA="e2bdfc9ece63e4f66e4ddf62c438551e4cbf72badd013e1b774ed5be4a9bb8ee"
SOURCE_DIMS=(1920,1080)
SOURCE_TIME_S=None  # exact source time read from V251 shot manifest at workflow level
MODEL="timbrooks/instruct-pix2pix"
MODEL_LICENSE="mit"
PROMPT=("Subtly restore natural historical colors and realistic photographic detail "
        "to this exact archival 1912 Fiesole straw hat manufacturing frame. "
        "Retain ALL objects, silhouettes, number of people, tools, positions, "
        "architecture, and original camera geometry exactly as in the reference. "
        "Improve the existing photographed straw, cloth, wood and metal textures "
        "only where visible. Natural skin colors only if real faces or hands "
        "exist in the source; do not invent humans or change the scene. "
        "Neutral realistic daylight, no orange cast, no added objects, "
        "no new hands, no illustration, no text.")
SEED=257
MODEL_DIMS=(448,800)

def sha(p:Path)->str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()

def check_source(p:Path)->None:
    if p.is_symlink() or not p.is_file() or sha(p)!=SOURCE_SHA:
        raise ValueError("V257_SOURCE_FRAME_SHA_MISMATCH")
    with Image.open(p) as img:
        if img.format!="PNG" or img.size!=SOURCE_DIMS:
            raise ValueError("V257_SOURCE_FRAME_DIMENSIONS_CHANGED")
        img.verify()

def crop_source(p:Path,output:Path)->str:
    check_source(p)
    with Image.open(p) as img:
        src=img.convert("RGB")
        cropped=src.crop((656,0,1264,1080))
        if cropped.size!=(608,1080):
            raise ValueError("V257_CROP_GEOMETRY_CHANGED")
        cropped.save(output)
    return sha(output)

def inspect_candidate(source_crop:Path,gen_image:Path)->dict:
    if not gen_image.is_file() or gen_image.is_symlink() or gen_image.stat().st_size<10000:
        raise ValueError("V257_NO_ACTUAL_MODEL_PHOTO")
    with Image.open(source_crop) as i, Image.open(gen_image) as o:
        a=i.convert("RGB").resize(MODEL_DIMS,Image.Resampling.LANCZOS)
        b=o.convert("RGB")
        if b.size != MODEL_DIMS:
            raise ValueError("V257_GENERATED_IMAGE_WRONG_DIMENSIONS")
        a_small=ImageOps.grayscale(a).resize((112,200),Image.Resampling.BILINEAR)
        b_small=ImageOps.grayscale(b).resize((112,200),Image.Resampling.BILINEAR)
        x=list(a_small.getdata());y=list(b_small.getdata())
        import math
        mx=sum(x)/len(x);my=sum(y)/len(y)
        cov=sum((u-mx)*(v-my) for u,v in zip(x,y))
        xx=sum((u-mx)**2 for u in x)
        yy=sum((v-my)**2 for v in y)
        corr=cov/max(1.0,math.sqrt(xx*yy))
        mae=sum(abs(u-v) for u,v in zip(x,y))/len(x)
        sat=ImageStat.Stat(b.convert("HSV")).mean[1]
        srcsat=ImageStat.Stat(a.convert("HSV")).mean[1]
    return {"generated_sha256":sha(gen_image),
            "generated_size_px":list(MODEL_DIMS),
            "original_luma_correlation":round(corr,4),
            "original_to_candidate_luma_mae":round(mae,3),
            "source_saturation_mean":round(srcsat,2),
            "photo_saturation_mean":round(sat,2),
            "genuine_diffusion_i2i":True,
            "structural_alignment_certified":False,
            "human_artistic_approved":False,
            "italy_rights_verified":False,
            "vidu_count":0,"final_video":False,"publish_allowed":False}

def make_comparison(source:Path,gen:Path,out:Path)->None:
    with Image.open(source) as i,Image.open(gen) as g:
        a=ImageOps.fit(i.convert("RGB"),(448,800))
        b=g.convert("RGB").resize((448,800))
    sheet=Image.new("RGB",(896,830),(25,25,25))
    sheet.paste(a,(0,30));sheet.paste(b,(448,30))
    d=ImageDraw.Draw(sheet)
    d.text((10,7),"FIESOLE 1912 ORIGINAL REAL FRAME",fill="white")
    d.text((460,7),"CPU DIFFUSION I2I - NOT APPROVED",fill="white")
    sheet.save(out,quality=91)

def run_one_real_i2i(input_png:Path,output_png:Path):
    # Single CPU diffusion invocation; if OOM/timeout, stop. No quota or paid endpoint.
    import torch
    from diffusers import StableDiffusionInstructPix2PixPipeline
    torch.set_num_threads(min(4,os.cpu_count() or 2))
    pipe=StableDiffusionInstructPix2PixPipeline.from_pretrained(
        MODEL,torch_dtype=torch.float32,use_safetensors=True)
    pipe.to("cpu")
    pipe.enable_attention_slicing()
    with Image.open(input_png) as i:
        image=i.convert("RGB").resize(MODEL_DIMS,Image.Resampling.LANCZOS)
    generator=torch.Generator(device="cpu").manual_seed(SEED)
    with torch.inference_mode():
        new_image=pipe(prompt=PROMPT,image=image,generator=generator,
                       num_inference_steps=18,guidance_scale=7.5,
                       image_guidance_scale=2.7).images[0]
    if not isinstance(new_image,Image.Image) or new_image.size!=MODEL_DIMS:
        raise ValueError("V257_NOT_A_VALID_GENERATED_IMAGE")
    new_image.save(output_png)
    del pipe

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--offline",action="store_true")
    a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=True)
    source_crop=a.out/"V257_GENUINE_1912_SOURCE_CROP.png"
    crop_hash=crop_source(a.source,source_crop)
    report={"version":"V257_ONE_LOCAL_CPU_DIFFUSION_I2I_TRIAL",
      "source_film":"Manufacture de chapeaux de paille a Fiesole (1912)",
      "original_source_sha256":SOURCE_SHA,"source_time_s":SOURCE_TIME_S,
      "source_crop_sha256":crop_hash,"source_crop_px":[608,1080],
      "generator":MODEL,"model_license":MODEL_LICENSE,"seed":SEED,
      "inference_steps":18,"image_guidance_scale":2.7,
      "actual_generated_photos":0,"real_vidu_clips":0,
      "paid_credits_spent":0,"new_final_episodes_delivered":0,
      "artistic_approval":False,"italian_rights_verified":False,
      "publish_allowed":False,"status":"ORIGINAL_SOURCE_READY_NO_MODEL_CALL"}
    rp=a.out/"V257_SOURCE_LOCKED_I2I_QA.json"
    rp.write_text(json.dumps(report,indent=2)+"\n")
    if a.offline:
        print("V257_SOURCE_SHA_PASS_NO_GENERATION_NO_FINAL")
        return
    try:
        result=a.out/"V257_ONE_TRUE_DIFFUSION_I2I_NOT_APPROVED.png"
        run_one_real_i2i(source_crop,result)
        report.update(inspect_candidate(source_crop,result))
        make_comparison(source_crop,result,a.out/"V257_BEFORE_AFTER_ACTUAL_I2I.jpg")
        report["actual_generated_photos"]=1
        report["status"]="REAL_CPU_DIFFUSION_PHOTO_GENERATED_ARTISTIC_QA_PENDING_NOT_FINAL"
    except Exception as e:
        report["status"]="LOCAL_CPU_DIFFUSION_NO_VALID_PHOTO"
        report["error_type"]=type(e).__name__
        raise
    finally:
        rp.write_text(json.dumps(report,indent=2)+"\n")
    print("V257_REAL_DIFFUSION_I2I_CANDIDATE_NOT_FINAL",sha(result))

if __name__=="__main__":
    main()
