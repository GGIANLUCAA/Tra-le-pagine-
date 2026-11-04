#!/usr/bin/env python3
"""V265: ONE real color-forward I2I retry for the rejected Fiesole shot 01.

Uses the exact source-locked V251 original and public MIT InstructPix2Pix
model on local GitHub CPU. A near-monochrome result must never be counted.
No Vidu, provider HTTP inference, paid credit, publication or auto-approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

from PIL import Image, ImageStat

import storia_rivive_v261_fiesole_first_source_i2i as first
import storia_rivive_v257_fiesole_third_source_i2i as engine

SOURCE_SHA = first.SOURCE_SHA
SEED = 1265
# A SHORT prompt prevents the CLIP 77-token truncation observed previously.
PROMPT = (
    "Colorize this 1912 Fiesole workshop photograph with realistic rich natural "
    "daylight colors. Straw honey-gold, wooden machinery warm brown, iron gray, "
    "fabric muted blue and cream. Keep exact camera framing, machines, "
    "objects, people and outlines unchanged. No new people or objects."
)
GUIDANCE_SCALE = 10.0
IMAGE_GUIDANCE_SCALE = 2.15  # V262 at 2.7 held source but remained monochrome
STEPS = 20
MODEL = "timbrooks/instruct-pix2pix"
VERSION = "V265_FIRST_FIESOLE_TRUE_COLOR_FORWARD_I2I_NOT_FINAL"
NAME = "V265_SHOT_01_REAL_COLOR_I2I_CANDIDATE_NOT_APPROVED.png"
REPORT = "V265_FIRST_SHOT_COLOR_I2I_QA.json"
MIN_SATURATION = 36.0
MIN_COLORED_PIXEL_RATIO = 0.08

def colored_fraction(pic: Image.Image) -> float:
    """Pixels with meaningful RGB separation, not a subtle sepia tint."""
    rgb = pic.convert("RGB")
    # Resize only for inexpensive QA; never replace the output with this.
    small = rgb.resize((112, 200), Image.Resampling.BILINEAR)
    pixels = list(small.getdata())
    return round(sum(max(p) - min(p) >= 30 for p in pixels) / len(pixels), 4)

def color_evidence(source_crop: Path, output: Path) -> dict:
    with Image.open(output) as p, Image.open(source_crop) as original:
        if p.format != "PNG" or p.size != engine.MODEL_DIMS:
            raise ValueError("V265_GENERATED_IMAGE_FORMAT_OR_SIZE_MISMATCH")
        generated = p.convert("RGB")
        src = original.convert("RGB").resize(engine.MODEL_DIMS)
        sat = ImageStat.Stat(generated.convert("HSV")).mean[1]
        source_sat = ImageStat.Stat(src.convert("HSV")).mean[1]
        chroma = colored_fraction(generated)
    return {
        "actual_png_sha256": engine.sha(output),
        "original_mean_hsv_saturation": round(source_sat, 2),
        "candidate_mean_hsv_saturation": round(sat, 2),
        "candidate_rgb_spread_ge30_ratio": chroma,
        "minimal_natural_color_evidence": bool(
            sat >= MIN_SATURATION and chroma >= MIN_COLORED_PIXEL_RATIO
        ),
        "artistic_approval": False,
        "human_visual_review": "PENDING",
        "italian_rights_verified": False,
        "final_mp4": False,
        "new_final_episodes_delivered": 0,
        "vidu_credit_spent": 0,
    }

def generate_local(source_crop: Path, output: Path) -> None:
    import torch
    from diffusers import StableDiffusionInstructPix2PixPipeline
    torch.set_num_threads(min(4, os.cpu_count() or 2))
    pipe = StableDiffusionInstructPix2PixPipeline.from_pretrained(
        MODEL, torch_dtype=torch.float32, use_safetensors=True)
    pipe.to("cpu")
    pipe.enable_attention_slicing()
    with Image.open(source_crop) as im:
        original = im.convert("RGB").resize(engine.MODEL_DIMS)
    with torch.inference_mode():
        result = pipe(
            prompt=PROMPT, image=original, num_inference_steps=STEPS,
            guidance_scale=GUIDANCE_SCALE,
            image_guidance_scale=IMAGE_GUIDANCE_SCALE,
            generator=torch.Generator(device="cpu").manual_seed(SEED),
        ).images[0]
    if not isinstance(result, Image.Image) or result.size != engine.MODEL_DIMS:
        raise ValueError("V265_NO_VALID_GENERATED_IMAGE")
    result.save(output)

def run(manifest: Path, source: Path, out: Path, *, offline=False, generator=None) -> dict:
    row = first.verify_manifest(manifest, source)
    out.mkdir(parents=True, exist_ok=True)
    crop = out / "V265_GENUINE_1912_SOURCE_FRAME_CROP.png"
    engine.SOURCE_SHA = SOURCE_SHA
    engine.crop_source(source, crop)
    report = {
        "version": VERSION,
        "episode": "fiesole_straw_hats_1912_v220",
        "source_shot": 1,
        "source_frame": "frame_03.png",
        "original_source_sha256": SOURCE_SHA,
        "source_time_s": row.get("source_time_s"),
        "crop_sha256": engine.sha(crop),
        "prompt_sha256": hashlib.sha256(PROMPT.encode("utf-8")).hexdigest(),
        "model": MODEL, "seed": SEED, "steps": STEPS,
        "guidance_scale": GUIDANCE_SCALE,
        "image_guidance_scale": IMAGE_GUIDANCE_SCALE,
        "prior_candidate_v262_rejected": "ALMOST_MONOCHROME",
        "status": "SOURCE_LOCKED_READY_NO_GENERATION",
        "actual_generated_photos": 0,
        "approved_real_i2i_photos": 0,
        "artistic_approval": False,
        "italian_rights_verified": False,
        "vidu_credit_spent": 0,
        "new_final_episodes_delivered": 0,
        "publish_allowed": False,
    }
    rp = out / REPORT
    rp.write_text(json.dumps(report, indent=2) + "\n")
    if offline:
        return report
    target = out / NAME
    try:
        if generator is None:
            generate_local(crop, target)
        else:
            generator(crop, target)
        report.update(engine.inspect_candidate(crop, target))
        report.update(color_evidence(crop, target))
        engine.make_comparison(crop, target, out / "V265_REAL_COLOR_BEFORE_AFTER_REVIEW_ONLY.jpg")
        report["actual_generated_photos"] = 1
        report["status"] = ("ONE_REAL_COLOR_I2I_VISUAL_QA_REQUIRED_NOT_FINAL"
                            if report["minimal_natural_color_evidence"]
                            else "REJECTED_INSUFFICIENT_COLOR_NOT_FINAL")
    except Exception as exc:
        report.update(status="LOCAL_CPU_I2I_FAILED_NOT_FINAL",
                      error_type=type(exc).__name__)
        raise
    finally:
        rp.write_text(json.dumps(report, indent=2) + "\n")
    return report

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", required=True, type=Path)
    p.add_argument("--source", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--offline", action="store_true")
    args = p.parse_args()
    result = run(args.manifest, args.source, args.out, offline=args.offline)
    print(result["status"], "NEW_FINAL_0_OF_4")
    if not args.offline and not result["minimal_natural_color_evidence"]:
        raise SystemExit("V265_NEAR_MONOCHROME_COLOR_BENCHMARK_REJECTED")
