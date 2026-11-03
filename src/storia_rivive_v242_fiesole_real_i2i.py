#!/usr/bin/env python3
"""V242: one source-locked FREE Qwen I2I trial on real Fiesole 1912 straw work.
One anonymous free provider request at most; NOT final, NOT artistically approved.
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import io
import json
from pathlib import Path
from PIL import Image, ImageOps

FILM_FRAME_SHA = "6ff2b0dde222cd85f97873271488ee0aabd79a2cb340f8f8e37ba016f8190d20"
PORTRAIT_SHA = "6f1f06b7cb9c5f91757e972fd213818d132e965382a9955cf1a743bd80c01435"
SPACE = "prithivMLmods/Qwen-Image-Edit-2511-LoRAs-Fast"
PROMPT = (
    "Historical documentary reconstruction, Fiesole Italy 1912, processing straw "
    "for handmade straw hats. Restore and naturally colorize THIS EXACT photographed "
    "frame. Preserve the precise positions and number of hands, individual fingers, "
    "bundles of straw, woven strands, wooden tools and background; use the original "
    "black-and-white pixels as an immutable composition blueprint. Natural neutral "
    "daylight, physically plausible period colors and lifelike textures, detailed "
    "photographic material surfaces. No new people, fingers, hands, objects, signs, "
    "text or machinery. No change of camera angle, crop, gesture or perspective. "
    "No orange/sepia cast, plastic look, beauty retouching or illustration."
)

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def source_crop(source: Path, out: Path) -> Path:
    if source.is_symlink() or not source.is_file() or sha256(source) != FILM_FRAME_SHA:
        raise ValueError("V242_ORIGINAL_FRAME_HASH_MISMATCH")
    with Image.open(source) as image:
        if image.format != "PNG" or image.size != (1920, 1080):
            raise ValueError("V242_ORIGINAL_FRAME_GEOMETRY_MISMATCH")
        portrait = ImageOps.fit(image.convert("RGB"), (608, 1080),
                                method=Image.Resampling.LANCZOS)
    out.mkdir(parents=True, exist_ok=True)
    target = out / "FIESOLE_1912_FRAME_05_EXACT_CROP.png"
    portrait.save(target)
    if sha256(target) != PORTRAIT_SHA:
        raise ValueError("V242_PORTRAIT_SOURCE_HASH_MISMATCH")
    return target

def decode_response(value: dict, target: Path) -> dict:
    if not isinstance(value, dict) or value.get("status") != "success":
        raise ValueError("V242_PROVIDER_NO_SUCCESS")
    raw = value.get("image")
    if not isinstance(raw, str) or not raw.startswith("data:image/png;base64,"):
        raise ValueError("V242_PROVIDER_NO_PNG")
    coded = raw.partition(",")[2]
    if len(coded) > 35_000_000:
        raise ValueError("V242_PROVIDER_RESULT_TOO_LARGE")
    blob = base64.b64decode(coded, validate=True)
    if len(blob) < 10000:
        raise ValueError("V242_PROVIDER_IMAGE_TOO_SMALL")
    with Image.open(io.BytesIO(blob)) as image:
        if image.format != "PNG" or min(image.size) < 512:
            raise ValueError("V242_PROVIDER_INVALID_IMAGE")
        w, h = image.size
        if abs(w / h - 608 / 1080) > 0.025:
            raise ValueError("V242_PROVIDER_IMAGE_ASPECT_DRIFT")
        image.verify()
    target.write_bytes(blob)
    return {"candidate_sha256": sha256(target), "candidate_px": [w, h]}

def try_free_once(source: Path, target: Path, client_factory=None) -> dict:
    if sha256(source) != PORTRAIT_SHA:
        raise ValueError("V242_UNVERIFIED_PORTRAIT_SOURCE")
    if client_factory is None:
        from gradio_client import Client
        client_factory = Client
    client = client_factory(SPACE, verbose=False)
    encoded = "data:image/png;base64," + base64.b64encode(source.read_bytes()).decode("ascii")
    # Only ONE free anonymous request, never retry a rejected/ambiguous POST.
    result = client.predict(images_b64_json=json.dumps([encoded]), prompt=PROMPT,
                            lora_adapter="Anything2Real", seed=42,
                            randomize_seed=False, guidance_scale=1.0,
                            steps=4, api_name="/edit_image")
    return decode_response(result, target)

def comparison(original: Path, generated: Path, out: Path) -> None:
    canvas = Image.new("RGB", (760, 720), "#151515")
    from PIL import ImageDraw
    draw = ImageDraw.Draw(canvas)
    for idx, path in enumerate([original, generated]):
        with Image.open(path) as photo:
            view = ImageOps.fit(photo.convert("RGB"), (350, 620))
        x = idx * 390 + 10
        canvas.paste(view, (x, 50))
        draw.text((x, 15),
                  "AUTHENTIC 1912 FRAME" if idx == 0 else "GENERATIVE CANDIDATE - NOT APPROVED",
                  fill="white")
    canvas.save(out, quality=90)

def run(original: Path, folder: Path, offline: bool = False, client_factory=None) -> dict:
    folder.mkdir(parents=True, exist_ok=True)
    report = {"version": "V242_FIESOLE_SOURCE_LOCKED_REAL_I2I",
              "original_frame_sha256": FILM_FRAME_SHA, "portrait_sha256": PORTRAIT_SHA,
              "episode": "fiesole_straw_hats_1912_v220",
              "provider_attempts": 0, "paid_credits_spent": 0,
              "real_i2i_candidates": 0, "four_photos_complete": False,
              "vidu_generated": False, "italian_rights_verified": False,
              "human_artistic_approved": False, "final_mp4": False, "final_zip": False,
              "new_final_episodes_delivered": 0, "publish_allowed": False,
              "status": "SOURCE_ONLY"}
    report_path = folder / "V242_REAL_MEDIA_STATUS.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    portrait = source_crop(original, folder)
    if not offline:
        report["provider_attempts"] = 1
        try:
            result_path = folder / "FIESOLE_1912_ONE_REAL_I2I_CANDIDATE.png"
            result = try_free_once(portrait, result_path, client_factory)
            report.update(result)
            comparison(portrait, result_path, folder / "SOURCE_VS_I2I_QA_NOT_APPROVED.jpg")
            report["real_i2i_candidates"] = 1
            report["status"] = "REAL_I2I_CANDIDATE_NEEDS_ARTISTIC_REVIEW"
        except Exception as e:
            report["status"] = "FREE_PROVIDER_FAILED_NO_NEW_PHOTO"
            report["failure_type"] = type(e).__name__
            raise
        finally:
            report_path.write_text(json.dumps(report, indent=2) + "\n")
    else:
        report_path.write_text(json.dumps(report, indent=2) + "\n")
    return report

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--offline", action="store_true")
    options = ap.parse_args()
    result = run(options.source, options.out, options.offline)
    print("V242_STATUS", result["status"], "NEW_FINAL_0_OF_4")
