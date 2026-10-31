#!/usr/bin/env python3
"""V153: ONE no-cost experimental I2I photo from authentic V151 scene 02.

This is NOT the V101/V102 production pipeline and NEVER turns V152
provider_jobs_may_start=false into true. The five-film editorial preflight
remains BLOCKED. Experiment is limited to one authentic B/W source and one
public, zero-price Finegrain image-to-image request, no credentials or retries.
An unsuccessful/quota-blocked request is recorded, not replaced by DDColor.
If a genuine candidate passes coarse technical gates, render a short B/W ->
exact-source freeze -> AI-photo moving/still A/B clip, NOT a finished film.
Human artistic QA, rights Italy, a coherent episode and Vidu remain pending.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import pathlib
import shutil
import subprocess
from typing import Callable

import cv2
import numpy as np
from PIL import Image, ImageDraw

from src.storia_rivive_v149_authentic_bw_proxy import sha256_file

SCENE = 2
SOURCE_ID = "girl_cat_1900"
SOURCE_SHA = "37da59961c75fddea7609ab2d29302f0171dd2c45f9e823ebc8059b7ab810534"
CROP_SHA = "209320b0bcf9b734e28f5160542c6d99a4043dedf09d0ed36e84833d4a367b25"
FILM_SHA = "d586cd2542ca3652e142a25d64778664d77ceeb76276707a940ce857381918ad"
FREE_MODEL = "finegrain/finegrain-image-enhancer"
PROMPT = (
    "Convert this EXACT historic 1900 motion-picture frame of a small girl "
    "beside a black long-haired cat into a genuine natural-color sharply focused "
    "documentary photograph. Keep the SAME CAT muzzle, whiskers, paws, fur "
    "and body, the girl's visible arm, face outline, clothing and framing; "
    "no invented eyes or fingers. Preserve original count, perspective, "
    "background and poses. Natural believable wool, fur and skin colors, "
    "photographic material textures; not an illustration. This is an "
    "interpretive reconstruction of original monochrome historical film."
)
NEGATIVE = (
    "invented faces, second cat, altered muzzle, additional whiskers, "
    "changed hand, added fingers, modern clothes, cat transformed into a toy, "
    "plastic skin, over-sharpened fur, fantasy, orange tint, sepia, grayscale, "
    "watercolor, letters, signs, image borders, camera movement"
)


def verify_source(root: pathlib.Path):
    manifest = json.loads((root / "V151_SOURCE_LOCKED_HANDOFF.json").read_text(encoding="utf-8"))
    editorial = json.loads((root / "V152_EDITORIAL_PREFLIGHT.json").read_text(encoding="utf-8"))
    if (manifest.get("version") != "V151" or
            manifest.get("real_source_frames_sha_verified") != 5 or
            manifest.get("candidate_i2i_jobs") != 4 or
            manifest.get("real_restored_photos_generated") != 0 or
            manifest.get("real_vidu_clips_generated") != 0 or
            manifest.get("provider_requests_sent") != 0 or
            manifest.get("paid_api_calls") != 0 or
            manifest.get("publish_permitted") is not False or
            manifest.get("rights_italy_verified") is not False or
            manifest.get("artistic_approved") is not False):
        raise ValueError("V153_INVALID_V151_REAL_SOURCE_HANDOFF")
    if (editorial.get("status") != "V152_EDITORIAL_SOURCE_COHERENCE_BLOCKED"
            or editorial.get("provider_jobs_may_start") is not False
            or editorial.get("rights_italy_verified") is not False):
        raise ValueError("V153_V152_EDITORIAL_STATUS_MODIFIED")
    rows = manifest.get("freeze_frames")
    if not isinstance(rows, list) or len(rows) != 5:
        raise ValueError("V153_MISSING_FIVE_REAL_SCENE_ROWS")
    row = rows[SCENE-1]
    if (row.get("scene") != SCENE or row.get("source_id") != SOURCE_ID
            or row.get("role") != "I2I_PHOTO_CANDIDATE_NOT_GENERATED"
            or row.get("native_original_frame_sha256") != SOURCE_SHA
            or row.get("vertical_review_sha256") != CROP_SHA
            or row.get("source_film_sha256") != FILM_SHA
            or row.get("native_original_frame_pts") != 21800
            or row.get("native_time_base") != "1/1000"
            or row.get("vertical_review_raster") != [720,1280]
            or any(row.get(k) is not False for k in (
                "image_to_image_sent", "vidu_request_sent",
                "source_subject_artistically_reviewed", "face_and_object_fidelity_verified",
                "rights_italy_verified", "provider_credit_budget_approved"))):
        raise ValueError("V153_EXACT_SOURCE_FRAME_OR_ROLE_CHANGED")
    native = root / "native_frames" / "scene_02_NATIVE_FREEZE.png"
    crop = root / "review_crops" / "scene_02_SOURCE_CROP_720x1280.png"
    for file, sha in ((native,SOURCE_SHA),(crop,CROP_SHA)):
        if not file.is_file() or file.is_symlink() or sha256_file(file) != sha:
            raise ValueError("V153_PHOTO_BYTES_NOT_AUTHENTIC")
        with Image.open(file) as image:
            image.verify()
    with Image.open(crop) as photo:
        if photo.size != (720,1280):
            raise ValueError("V153_CROP_RASTER_CHANGED")
    return crop, row


def ddcolor_base(image: pathlib.Path, dest: pathlib.Path):
    """DDColor is only the COLOR INPUT to real I2I, never the output."""
    from src import storia_rivive_real_ai_v60 as dd
    model, model_info = dd.download_model()
    original = cv2.imread(str(image))
    if original is None:
        raise ValueError("V153_INVALID_ORIGINAL_SOURCE_CROP")
    reduced = cv2.resize(original,(720,576),interpolation=cv2.INTER_AREA)
    ab = dd.infer_ab(model, reduced)
    l = dd.l_channel(original)
    chroma = cv2.resize(ab, (720,1280), interpolation=cv2.INTER_CUBIC)
    lab = np.dstack((l,np.clip(chroma*1.08,-110,110))).astype(np.float32)
    rgb = np.clip(cv2.cvtColor(lab,cv2.COLOR_LAB2RGB)*255,0,255).astype(np.uint8)
    Image.fromarray(rgb).save(dest, quality=95)
    return {"base_is_ddcolor_only_not_i2i":True,"base_sha256":sha256_file(dest),
            "model_sha256":model_info["sha256"]}


def finegrain_once(base: pathlib.Path):
    """Exactly one free public Space request. No HF or Vidu token, no retry."""
    from gradio_client import Client, handle_file
    client = Client(FREE_MODEL, verbose=False)
    response = client.predict(
        handle_file(str(base)), PROMPT, NEGATIVE,
        1900, 2, 1.14, .97, 6, 112, 144, .45, 18,
        "DDIM", api_name="/process"
    )
    item = response[1] if isinstance(response,(tuple,list)) and len(response)>1 else response
    if isinstance(item, dict):
        item=item.get("path")
    if not isinstance(item, str):
        raise RuntimeError("V153_FREE_PROVIDER_NO_REAL_PHOTO_FILE")
    path=pathlib.Path(item)
    if not path.is_file() or path.stat().st_size < 5000:
        raise RuntimeError("V153_FREE_PROVIDER_EMPTY_PHOTO")
    return path


def metrics(original: pathlib.Path, proposed: pathlib.Path):
    a=cv2.imread(str(original))
    b=cv2.imread(str(proposed))
    if a is None or b is None:
        raise ValueError("V153_PHOTO_DECODE_FAILED")
    def coarse(image):
        gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        return cv2.GaussianBlur(cv2.resize(gray,(90,160)),(9,9),0).astype(np.float32).ravel()
    a0,b0=coarse(a),coarse(b)
    correlation = float(np.corrcoef(a0,b0)[0,1]) if a0.std()>1 and b0.std()>1 else 0
    saturation = float(np.mean(cv2.cvtColor(b,cv2.COLOR_BGR2HSV)[:,:,1]))
    return {
        "coarse_luma_structure_correlation":round(correlation,4) if math.isfinite(correlation) else 0,
        "mean_saturation":round(saturation,2),
        "technical_candidate_pass":bool(math.isfinite(correlation) and correlation>=.83
                                        and 15 <= saturation <= 158),
        "faces_hands_cat_identity_artistically_verified":False,
    }


def mini_movie(bw_clip, freeze, photo, out):
    """True B/W film + EXACT native freeze + true I2I result (review only)."""
    bw = cv2.VideoCapture(str(bw_clip))
    if not bw.isOpened():
        raise ValueError("V153_BW_FILM_NOT_DECODABLE")
    w,h,fps=bw.get(cv2.CAP_PROP_FRAME_WIDTH),bw.get(cv2.CAP_PROP_FRAME_HEIGHT),bw.get(cv2.CAP_PROP_FPS)
    if (int(w),int(h)) != (720,1280) or not 29.5 <= fps <= 30.5:
        bw.release()
        raise ValueError("V153_BW_FILM_WRONG_FORMAT")
    orig = cv2.imread(str(freeze))
    result = cv2.imread(str(photo))
    if orig is None or result is None:
        bw.release()
        raise ValueError("V153_MISSING_ACTUAL_FREEZE_OR_PHOTO")
    if (orig.shape[1],orig.shape[0]) != (720,1280):
        bw.release()
        raise ValueError("V153_FREEZE_NOT_PORTRAIT")
    result = cv2.resize(result,(720,1280),interpolation=cv2.INTER_AREA)
    cmd=["ffmpeg","-nostdin","-y","-hide_banner","-loglevel","error",
         "-f","rawvideo","-pix_fmt","bgr24","-s","720x1280","-r","30",
         "-i","-","-an","-c:v","libx264","-preset","veryfast","-crf","20",
         "-pix_fmt","yuv420p","-movflags","+faststart",str(out)]
    process=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    count=0
    try:
        while True:
            ok,frame=bw.read()
            if not ok:break
            process.stdin.write(frame.tobytes());count+=1
            if count > 90:raise ValueError("V153_UNEXPECTED_LONG_ORIGINAL_CLIP")
        if not 65 <= count <= 78:
            raise ValueError("V153_ORIGINAL_BW_PREVIEW_LENGTH_CHANGED")
        for _ in range(7):
            process.stdin.write(orig.tobytes());count+=1
        for i in range(10):
            alpha=(i+1)/10
            mix=cv2.addWeighted(orig,1-alpha,result,alpha,0)
            process.stdin.write(mix.tobytes());count+=1
        for _ in range(48):
            process.stdin.write(result.tobytes());count+=1
    finally:
        bw.release()
        process.stdin.close()
        err=process.stderr.read().decode(errors="replace")
        rc=process.wait(timeout=90)
        if rc:
            raise RuntimeError("V153_FFMPEG_ENCODE_FAILURE_"+err[-200:])
    subprocess.run(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(out),
                    "-f","null","-"],check=True,timeout=90,capture_output=True)
    return round(count/30,3)


def run(root, out, *, base_colorizer=ddcolor_base, generator=finegrain_once,
        allow_one_free_public_request=True):
    root=pathlib.Path(root);out=pathlib.Path(out);out.mkdir(parents=True,exist_ok=True)
    crop,row=verify_source(root)
    result={
        "version":"V153","scene":SCENE,"source_id":SOURCE_ID,
        "source_frame_sha256":SOURCE_SHA,"source_crop_sha256":CROP_SHA,
        "source_film_sha256":FILM_SHA,
        "purpose":"ONE_FREE_NON_PUBLISHABLE_EXPERIMENT_ON_MIXED_FILM_PROVINENCE",
        "production_v152_editorial_gate_still_blocked":True,
        "source_episode_coherence_verified":False,
        "rights_italy_verified":False,"artistically_approved":False,
        "photo_restoration_model":FREE_MODEL,
        "real_i2i_generated":False,"technical_candidate_pass":False,
        "vidu_calls":0,"paid_calls":0,"social_published":False,
        "website_published":False,"finished_video":False,
        "output_video_is_short_technical_preview_only":True,
        "free_provider_requests_sent":0,"status":"V153_EXPERIMENT_NOT_STARTED"
    }
    status=out/"V153_EXPERIMENT_REPORT.json"
    def save():
        status.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    save()
    base=out/"SCENE02_DDCOLOR_BASE_NOT_RESTORED.jpg"
    try:
        info=base_colorizer(crop,base)
        if not base.is_file():
            raise ValueError("V153_COLOR_REFERENCE_NOT_CREATED")
        result["ddcolor_is_only_input_not_output"]=True
        result["ddcolor_sha256"]=sha256_file(base)
        result["color_base_model_sha256"]=info.get("model_sha256")
    except Exception as exc:
        result["status"]="V153_FREE_BASE_MODEL_OR_COLOR_PREP_UNAVAILABLE"
        result["error_type"]=type(exc).__name__
        save()
        return result
    if not allow_one_free_public_request:
        result["status"]="V153_EXPERIMENT_PROVIDER_NOT_REQUESTED"
        save();return result
    result["free_provider_requests_sent"]=1
    save()  # Persist intent before the one external request.
    try:
        candidate=generator(base)
        if not pathlib.Path(candidate).is_file():
            raise ValueError("V153_I2I_RETURN_NOT_A_REAL_FILE")
        with Image.open(candidate) as image:
            image.verify()
        with Image.open(candidate) as image:
            if min(image.size) < 500:
                raise ValueError("V153_I2I_RESULT_TOO_SMALL")
            image.convert("RGB").resize((720,1280),Image.Resampling.LANCZOS).save(
                out/"SCENE02_FREE_I2I_CANDIDATE.png",format="PNG")
        photo=out/"SCENE02_FREE_I2I_CANDIDATE.png"
        result["real_i2i_generated"]=True
        result["i2i_candidate_sha256"]=sha256_file(photo)
        computed=metrics(crop,photo)
        result["photo_technical_metrics"]=computed
        result["technical_candidate_pass"]=computed["technical_candidate_pass"]
        pair=Image.new("RGB",(720*2,1280),(16,18,22))
        for idx,p in enumerate([crop,photo]):
            with Image.open(p) as image:
                pair.paste(image.convert("RGB").resize((720,1280)),(idx*720,0))
        pair.resize((720,640)).save(out/"SCENE02_BW_VS_FREE_I2I_REVIEW.jpg",quality=90)
        if result["technical_candidate_pass"]:
            video= root/"scene_02_V150_BW_LONGER.mp4"
            if video.is_file() and sha256_file(video)==row["source_bw_video_sha256"]:
                movie=out/"SCENE02_BW_FREEZE_REAL_I2I_REVIEW_ONLY.mp4"
                seconds=mini_movie(video,crop,photo,movie)
                result["technical_video_preview_sha256"]=sha256_file(movie)
                result["technical_video_preview_duration_s"]=seconds
            result["status"]="V153_REAL_I2I_CANDIDATE_TECHNICAL_PASS_ART_QA_PENDING"
        else:
            result["status"]="V153_REAL_I2I_GENERATED_BUT_TECHNICAL_REJECT"
    except Exception as exc:
        result["status"]="V153_ONE_FREE_I2I_CALL_FAILED_OR_QUOTA_REACHED"
        result["error_type"]=type(exc).__name__
        # No retry, no fallback masquerading as a new photograph.
    save()
    return result


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-artifact",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    report=run(args.source_artifact,args.out)
    print("V153",report["status"],"one_free_request",report["free_provider_requests_sent"],
          "real_I2I",report["real_i2i_generated"],"Vidu",0,"paid",0,
          "final",False,flush=True)
