#!/usr/bin/env python3
"""V276: one genuine local CPU image-to-image candidate from Delhi film shot 02.

Exactly frame_04 from the verified V272 archival 1910 film; strictly review-only.
No substitute sources, synthetic 5th shot, Vidu request, rights approval or release.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps
import storia_rivive_v257_fiesole_third_source_i2i as metrics

EPISODE = "delhi_ruins_1910_v217"
SOURCE_PAGE = "https://commons.wikimedia.org/wiki/File:Ruins_of_Delhi_(1910).webm"
FILM_SHA = "0a0de7b032cdb19e34d4dac5a6efca02dfa4b00260411aa82290c54b2899f278"
FRAMES = ["frame_01.png", "frame_04.png", "frame_06.png", "frame_11.png", "frame_12.png"]
SHOT_INDEX = 1
FRAME_SHA = "8771b50f5a26b3e27eadf00ad085f998bfe2d552daa7f8492027a4c40c6c2a71"
SHOT_TIME = 66.401
MODEL = "timbrooks/instruct-pix2pix"
SEED = 276
PROMPT = (
    "Turn this exact grayscale 1910 Delhi archival film frame into a realistic "
    "FULL-COLOR contemporary-looking documentary photograph, while keeping the "
    "original historic view. Preserve the exact camera perspective, repeating "
    "steel bridge lattice, walkway planks, one real elephant, one real rider, "
    "their position, proportions, limbs, clothing, and every visible object. "
    "Lifelike detailed dark gray elephant skin, natural warm human skin tones, "
    "muted authentic cotton clothing colors, distinct neutral gray metallic "
    "bridge structure and earthy walkway, realistic daylight and physically "
    "plausible subtle color differences. Sharp yet natural photograph, "
    "not sepia, not monochrome, no brown/orange color cast, no illustration, "
    "no new people, animals, structures, props, lettering or decorative details."
)
OUT_NAME = "DELHI_1910_SHOT02_TRUE_I2I_CANDIDATE_NOT_FINAL.png"
REPORT_NAME = "DELHI_V276_SHOT02_ACTUAL_I2I_NOT_FINAL.json"
SHEET_NAME = "DELHI_V276_SHOT02_ORIGINAL_VS_I2I_REVIEW_ONLY.jpg"

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for part in iter(lambda: f.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()

def verify(scout: Path, selection: Path, original: Path) -> None:
    source = json.loads(scout.read_text(encoding="utf-8"))
    chosen = json.loads(selection.read_text(encoding="utf-8"))
    if (source.get("source_page") != SOURCE_PAGE
            or source.get("original_sha256") != FILM_SHA
            or source.get("status") != "REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW"):
        raise ValueError("V276_ARCHIVE_SOURCE_REJECTED")
    preselected = chosen.get("preselected", [])
    times = chosen.get("candidate_segment_times_s", [])
    if (chosen.get("status") != "FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW"
            or [x.get("filename") for x in preselected] != FRAMES
            or len(set(FRAMES)) != 5 or len(times) != 5
            or abs(times[SHOT_INDEX] - SHOT_TIME) > .005
            or chosen.get("approved_restored_photos") != 0
            or chosen.get("publish_permitted") is not False):
        raise ValueError("V276_SOURCE_SELECTION_CHANGED")
    if original.name != FRAMES[SHOT_INDEX] or original.is_symlink() or not original.is_file() or sha(original) != FRAME_SHA:
        raise ValueError("V276_FRAME_HASH_MISMATCH")
    with Image.open(original) as im:
        if im.format != "PNG" or im.size != (1920, 1080):
            raise ValueError("V276_FRAME_GEOMETRY_MISMATCH")
        im.verify()

def exact_crop(original: Path, target: Path) -> None:
    with Image.open(original) as im:
        im.convert("RGB").crop((656, 0, 1264, 1080)).save(target)
    with Image.open(target) as im:
        if im.size != (608, 1080):
            raise ValueError("V276_CROP_CHANGED")

def generate(crop: Path, result: Path) -> None:
    import torch
    from diffusers import StableDiffusionInstructPix2PixPipeline
    torch.set_num_threads(min(4, os.cpu_count() or 2))
    pipe = StableDiffusionInstructPix2PixPipeline.from_pretrained(
        MODEL, torch_dtype=torch.float32, use_safetensors=True
    ).to("cpu")
    pipe.enable_attention_slicing()
    with Image.open(crop) as im:
        starting = im.convert("RGB").resize(metrics.MODEL_DIMS, Image.Resampling.LANCZOS)
    generator = torch.Generator(device="cpu").manual_seed(SEED)
    with torch.inference_mode():
        photo = pipe(
            prompt=PROMPT, image=starting, generator=generator,
            num_inference_steps=23, guidance_scale=8.0,
            image_guidance_scale=1.8
        ).images[0]
    if not isinstance(photo, Image.Image) or photo.size != metrics.MODEL_DIMS:
        raise ValueError("V276_MODEL_DID_NOT_RETURN_PHOTO")
    photo.save(result)

def comparison(original_crop: Path, photo: Path, result: Path) -> None:
    with Image.open(original_crop) as inp, Image.open(photo) as out:
        a = ImageOps.fit(inp.convert("RGB"), metrics.MODEL_DIMS)
        b = out.convert("RGB")
    sheet = Image.new("RGB", (896, 830), (24, 24, 24))
    sheet.paste(a, (0, 30))
    sheet.paste(b, (448, 30))
    brush = ImageDraw.Draw(sheet)
    brush.text((12, 8), "DELHI 1910 | REAL ORIGINAL SHOT 02", fill="white")
    brush.text((457, 8), "V276 TRUE I2I | QA PENDING", fill="white")
    sheet.save(result, quality=94)

def run(scout: Path, selection: Path, original: Path, destination: Path,
        offline: bool = False, generator=None) -> dict:
    verify(scout, selection, original)
    destination.mkdir(parents=True, exist_ok=True)
    crop = destination / "V276_DELHI_REAL_FRAME04_EXACT_CROP.png"
    exact_crop(original, crop)
    report = {
        "version": "V276_DELHI_SHOT02_REAL_LOCAL_I2I_REVIEW_ONLY",
        "episode": EPISODE, "source_page": SOURCE_PAGE,
        "film_sha256": FILM_SHA, "source_frame": FRAMES[SHOT_INDEX],
        "source_frame_sha256": FRAME_SHA, "source_time_s": SHOT_TIME,
        "source_crop_sha256": sha(crop),
        "model": MODEL, "seed": SEED,
        "prompt_sha256": hashlib.sha256(PROMPT.encode()).hexdigest(),
        "inference_steps": 23, "image_guidance_scale": 1.8,
        "generated_photos": 0, "real_vidu_clips": 0, "paid_credits_spent": 0,
        "artistically_approved": False, "italian_rights_verified": False,
        "publication_allowed": False, "new_finished_mp4_zip": 0,
        "status": "SOURCE_ONLY_NO_PHOTO"
    }
    report_path = destination / REPORT_NAME
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if offline:
        return report
    try:
        photo = destination / OUT_NAME
        (generator or generate)(crop, photo)
        report.update(metrics.inspect_candidate(crop, photo))
        comparison(crop, photo, destination / SHEET_NAME)
        report["generated_photos"] = 1
        report["status"] = "ONE_TRUE_I2I_PHOTO_NEEDS_ACTUAL_ARTISTIC_QA_NOT_FINAL"
    except Exception as exc:
        report["status"] = "REJECTED_OR_FAILED_NO_VALID_PHOTO"
        report["error_type"] = type(exc).__name__
        raise
    finally:
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--scout", required=True, type=Path)
    parser.add_argument("--selection", required=True, type=Path)
    parser.add_argument("--original", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    data = run(args.scout, args.selection, args.original, args.out, args.offline)
    print(data["status"], "FINAL_EPISODES_DELIVERED_0_OF_4")
