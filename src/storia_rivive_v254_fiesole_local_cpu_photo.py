#!/usr/bin/env python3
"""V254: one locally generated REAL diffusers I2I photo from Fiesole V251.
No paid API, no third-party inference, no Vidu, no publishing or final claims.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import os
import zipfile
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
from storia_rivive_v249_fiesole_short_motion_selection import CANDIDATES, FILM_SHA

MODEL = "SG161222/Realistic_Vision_V5.1_noVAE"
VAE = "stabilityai/sd-vae-ft-mse"
EPISODE = "fiesole_straw_hats_1912_v220"
EXPECTED_SOURCE_ARTIFACT_RUN = 41635322340
TARGET_SIZE = (512, 896)
PROMPT = (
    "Authentic color documentary photograph in natural daylight from Fiesole Italy, "
    "1912, historical artisan straw-hat manufacture. The exact historical camera "
    "composition in the reference image, its people, tools, straw bundles, furniture "
    "and architecture remain recognizable. Natural faces and anatomically sensible "
    "hands, authentic period garments, photorealistic woven straw texture and wood "
    "details, believable muted natural colors, photographic clarity, beautiful "
    "cinematography without glamour retouching. This is a color photographic "
    "restoration of the supplied archival frame, not a newly invented scene."
)
NEGATIVE = (
    "painting, illustration, drawing, cartoon, CGI, orange filter, sepia, neon colors, "
    "blurry, wax skin, doll, malformed hands, extra fingers, duplicate person, "
    "extra props, modern machinery, added text, watermark, surreal"
)
STEPS = 20
STRENGTH = .58
GUIDANCE = 6.0
SEED = 1912

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def extract_source(archive: Path, out: Path, shot_index: int = 2) -> dict:
    """Require exact known archival frame, not trust labels in ZIP alone."""
    if archive.is_symlink() or not archive.is_file() or not 1 <= shot_index <= 4:
        raise ValueError("V254_SOURCE_ARCHIVE_OR_SHOT_INVALID")
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:
            raise ValueError("V254_ZIP_CRC_FAILED")
        names = z.namelist()
        if len(names) != 7 or len(set(names)) != 7:
            raise ValueError("V254_UNEXPECTED_SOURCE_ZIP_CONTENTS")
        manifest = json.loads(z.read("V251_SOURCE_MANIFEST_NOT_FINAL.json"))
        if (manifest.get("episode") != EPISODE
            or manifest.get("source_film_sha256") != FILM_SHA
            or manifest.get("version") != "V251_FIESOLE_SOURCE_LOCKED_PHOTO_HANDOFF"
            or manifest.get("status") != "SOURCE_FRAMES_FOR_FOUR_I2I_AND_ONE_VIDU_NOT_FINAL"
            or len(manifest.get("shots", [])) != 5):
            raise ValueError("V254_WRONG_SOURCE_MANIFEST")
        shot = manifest["shots"][shot_index-1]
        allowed = dict(CANDIDATES)
        if (shot.get("shot") != shot_index
            or shot.get("role") != "I2I_PHOTO_SOURCE"
            or shot.get("source_frame_locked") is not True
            or shot.get("original_frame") not in allowed
            or shot.get("original_sha256") != allowed[shot["original_frame"]]):
            raise ValueError("V254_UNVERIFIED_FRAME_IDENTITY")
        filename = shot.get("archive_filename")
        if (not isinstance(filename,str)
            or filename != f"original_shot_{shot_index:02d}_{shot['original_frame']}"
            or filename not in names):
            raise ValueError("V254_SOURCE_FRAME_NAME_MISMATCH")
        payload = z.read(filename)
        if digest(payload) != shot["original_sha256"]:
            raise ValueError("V254_SOURCE_FRAME_BYTES_MISMATCH")
    with Image.open(io.BytesIO(payload)) as original:
        if original.format != "PNG" or original.size != (1920,1080):
            raise ValueError("V254_SOURCE_FRAME_DIMENSIONS_MISMATCH")
        image = ImageOps.fit(original.convert("RGB"),TARGET_SIZE,
                             method=Image.Resampling.LANCZOS)
    out.mkdir(parents=True, exist_ok=True)
    source = out/"V254_FIESOLE_ORIGINAL_PORTRAIT_CROP.png"
    image.save(source)
    return {"source_crop_path": str(source), "original_frame_sha256": digest(payload),
            "source_crop_sha256": digest(source.read_bytes()),
            "original_frame": shot["original_frame"], "source_time_s": shot["source_time_s"],
            "shot_index": shot_index, "source_film_sha256": FILM_SHA}

def generate_photo(crop:Path, target:Path, factory=None) -> dict:
    """One LOCAL CPU diffusion inference; no POST to any image inference provider."""
    import torch
    if factory is None:
        from diffusers import AutoencoderKL, StableDiffusionImg2ImgPipeline
        vae = AutoencoderKL.from_pretrained(VAE, torch_dtype=torch.float32)
        pipeline = StableDiffusionImg2ImgPipeline.from_pretrained(
            MODEL, vae=vae, torch_dtype=torch.float32, use_safetensors=True,
            safety_checker=None, feature_extractor=None, low_cpu_mem_usage=True)
    else:
        pipeline = factory()
    torch.set_num_threads(2)
    pipeline = pipeline.to("cpu")
    pipeline.enable_attention_slicing()
    with Image.open(crop) as im:
        img = im.convert("RGB")
    generator = torch.Generator(device="cpu").manual_seed(SEED)
    with torch.inference_mode():
        output = pipeline(prompt=PROMPT,negative_prompt=NEGATIVE,image=img,
                          num_inference_steps=STEPS,strength=STRENGTH,
                          guidance_scale=GUIDANCE,generator=generator,
                          num_images_per_prompt=1).images[0]
    if not isinstance(output,Image.Image) or output.size!=TARGET_SIZE:
        raise ValueError("V254_NO_VALID_GENERATED_PHOTO")
    output.save(target)
    with Image.open(target) as photo:
        photo.verify()
    if target.stat().st_size < 10000:
        raise ValueError("V254_GENERATED_PHOTO_TOO_SMALL")
    return {"candidate_sha256":digest(target.read_bytes()),
            "candidate_dimensions":list(TARGET_SIZE),
            "candidate_bytes":target.stat().st_size}

def make_comparison(source:Path,candidate:Path,out:Path)->None:
    sheet=Image.new("RGB",(1056,954),"#191919")
    draw=ImageDraw.Draw(sheet)
    for x,p,label in ((8,source,"SOURCE: 1912 REAL FRAME"),
                      (536,candidate,"LOCAL I2I: NEEDS ARTISTIC QA")):
        with Image.open(p) as image:sheet.paste(image.convert("RGB"),(x,43))
        draw.text((x,14),label,fill="white")
    sheet.save(out,quality=93)

def run(archive:Path,out:Path,offline:bool=False,factory=None) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    report={"version":"V254_FIESOLE_LOCAL_CPU_REAL_I2I_TRIAL",
            "model":MODEL,"vae":VAE,"steps":STEPS,
            "seed":SEED,"strength":STRENGTH,"source_artifact_run":EXPECTED_SOURCE_ARTIFACT_RUN,
            "provider_requests":0,"vidu_credit_spend":0,"new_generated_i2i":0,
            "four_i2i_approved":0,"vidu_generated":False,
            "italian_rights_verified":False,"human_artistic_approved":False,
            "final_mp4":False,"final_zip":False,
            "new_final_episodes_delivered":0,"publish_allowed":False,
            "status":"SOURCE_VERIFICATION_PENDING"}
    path=out/"V254_REAL_PHOTO_CANDIDATE_STATUS.json"
    path.write_text(json.dumps(report,indent=2)+"\n")
    try:
        report.update(extract_source(archive,out))
        report["status"]="SOURCE_SHA_LOCKED_NO_GENERATION"
        path.write_text(json.dumps(report,indent=2)+"\n")
        if not offline:
            target=out/"V254_FIESOLE_ONE_LOCALLY_GENERATED_I2I_CANDIDATE.png"
            report["local_cpu_inference_attempted"]=True
            path.write_text(json.dumps(report,indent=2)+"\n")
            report.update(generate_photo(Path(report["source_crop_path"]),target,factory))
            make_comparison(Path(report["source_crop_path"]),target,
                            out/"V254_SOURCE_VS_REAL_I2I_REVIEW_ONLY.jpg")
            report["new_generated_i2i"]=1
            report["status"]="ONE_TRUE_LOCAL_I2I_PHOTO_NEEDS_ARTISTIC_REVIEW_NOT_FINAL"
    except Exception as exc:
        report["status"]="BLOCKED_NO_VERIFIED_NEW_I2I_PHOTO"
        report["error_type"]=type(exc).__name__
        path.write_text(json.dumps(report,indent=2)+"\n")
        raise
    finally:
        path.write_text(json.dumps(report,indent=2)+"\n")
    return report

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-zip",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--offline",action="store_true")
    args=parser.parse_args()
    result=run(args.source_zip,args.out,offline=args.offline)
    print(result["status"],"NEW_FINAL_0_OF_4")
