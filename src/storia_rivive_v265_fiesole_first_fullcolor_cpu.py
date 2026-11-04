#!/usr/bin/env python3
"""V265: photoreal FULL-color retry for authentic Fiesole shot 01 (CPU only).

The existing V261 SHA/manifest gate is reused unchanged. This is a single
offline-model editorial trial, NEVER an approved photo or completed video.
Model's safety checker is not removed, disabled or overridden.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import storia_rivive_v261_fiesole_first_source_i2i as first
import storia_rivive_v257_fiesole_third_source_i2i as engine
from PIL import Image

PROMPT = (
    "Colorize this exact 1912 archival workshop photograph into full natural color. "
    "Keep identical machines, straw, walls, people and perspective. Show straw pale "
    "golden yellow, wooden machines brown, metal grey, neutral daylight. Crisp authentic "
    "photographic texture. No added people, objects or changes to geometry."
)
SEED = 265
GUIDANCE = 9.0
IMAGE_GUIDANCE = 2.2
VERSION = "V265_FIESOLE_SHOT_01_FULL_COLOR_CPU_TRIAL_NOT_FINAL"
REPORT = "V257_SOURCE_LOCKED_I2I_QA.json"


def full_color_inference(source_crop: Path, result: Path) -> None:
    """Diffusion with different color/photo balance, with default safety retained."""
    import torch
    from diffusers import StableDiffusionInstructPix2PixPipeline

    torch.set_num_threads(min(4, os.cpu_count() or 2))
    pipeline = StableDiffusionInstructPix2PixPipeline.from_pretrained(
        engine.MODEL, torch_dtype=torch.float32, use_safetensors=True
    )
    # No safety_checker=None, no requires_safety_checker=False.
    pipeline.to("cpu")
    pipeline.enable_attention_slicing()
    with Image.open(source_crop) as loaded:
        image = loaded.convert("RGB").resize(engine.MODEL_DIMS, Image.Resampling.LANCZOS)
    generator = torch.Generator(device="cpu").manual_seed(SEED)
    with torch.inference_mode():
        restored = pipeline(
            prompt=PROMPT, image=image, generator=generator,
            num_inference_steps=18, guidance_scale=GUIDANCE,
            image_guidance_scale=IMAGE_GUIDANCE,
        ).images[0]
    if not isinstance(restored, Image.Image) or restored.size != engine.MODEL_DIMS:
        raise ValueError("V265_NO_ACTUAL_DIFFUSION_IMAGE")
    restored.save(result)


def stamp_report(out: Path) -> None:
    report = out / REPORT
    if not report.is_file():
        return
    obj = json.loads(report.read_text(encoding="utf-8"))
    obj.update(
        version=VERSION,
        source_shot=1,
        prompt_sha256=hashlib.sha256(PROMPT.encode("utf-8")).hexdigest(),
        inference_seed=SEED,
        guidance_scale=GUIDANCE,
        image_guidance_scale=IMAGE_GUIDANCE,
        safety_checker_disabled=False,
        prior_v262_artistic_rejection="ALMOST_MONOCHROME_NOT_V98",
        artistic_approval=False,
        italian_rights_verified=False,
        new_final_episodes_delivered=0,
        publish_allowed=False,
        paid_credits_spent=0,
    )
    report.write_text(json.dumps(obj, indent=2)+"\n", encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--offline", action="store_true")
    a = p.parse_args()
    # The first-frame SHA gate already asserts manifest unique five originals.
    old_prompt, old_seed = first.PROMPT, first.SEED
    old_run = engine.run_one_real_i2i
    old_argv = sys.argv
    first.PROMPT = PROMPT
    first.SEED = SEED
    engine.run_one_real_i2i = full_color_inference
    try:
        sys.argv = [old_argv[0], "--source", str(a.source),
                    "--manifest", str(a.manifest), "--out", str(a.out)]
        if a.offline:
            sys.argv.append("--offline")
        first.main()
    finally:
        sys.argv = old_argv
        first.PROMPT, first.SEED = old_prompt, old_seed
        engine.run_one_real_i2i = old_run
        stamp_report(a.out)


if __name__ == "__main__":
    main()
