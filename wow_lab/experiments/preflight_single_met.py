#!/usr/bin/env python3
"""WOW LAB: one authentic Met CC0 subject, mask-first audit, NO rendering.

Usage:
  python wow_lab/experiments/preflight_single_met.py --object-id 400112 \
      --out wow_lab/runs/preflight-400112-unique

Never creates video, release, social publication, or paid API usage.
The source and technical mask may pass without artistic approval.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import engine
from subject_popout import preflight_source, PreflightRejected


def contact_sheet(folder: Path):
    names = ("SOURCE_MET_ORIGINAL.jpg", "SUBJECT_MASK.png",
             "MASK_BEFORE_RENDER.jpg", "CLEAN_PLATE_SYNTHETIC.jpg")
    available = [name for name in names if (folder / name).is_file()]
    if not available:
        return None
    cell_w, cell_h = 400, 470
    sheet = Image.new("RGB", (cell_w * 2, cell_h * 2), (24, 24, 24))
    pen = ImageDraw.Draw(sheet)
    for index, name in enumerate(names):
        x, y = index % 2 * cell_w, index // 2 * cell_h
        if name not in available:
            pen.text((x + 12, y + 12), name + " (not available)", fill="white")
            continue
        with Image.open(folder / name) as im:
            picture = im.convert("RGB")
            picture.thumbnail((cell_w - 20, cell_h - 45), Image.Resampling.LANCZOS)
            sheet.paste(picture, (x + (cell_w - picture.width) // 2,
                                  y + 8 + (cell_h - 45 - picture.height) // 2))
        pen.text((x + 12, y + cell_h - 30), name, fill="white")
    sheet.save(folder / "MASK_CONTACT_SHEET.jpg", quality=91)
    return "MASK_CONTACT_SHEET.jpg"


def run(object_id: int, out: Path) -> int:
    out = out.resolve()
    sandbox = (ROOT / "runs").resolve()
    if sandbox not in out.parents:
        raise ValueError("Output must be a unique folder under wow_lab/runs/")
    if out.exists():
        raise RuntimeError("WOW_LAB_PREFLIGHT_DIRECTORY_ALREADY_EXISTS")
    config = engine.read_config(ROOT / "config.json")
    record = engine.get_json(engine.object_url(object_id))
    if record.get("objectID") != object_id or not engine.valid_object(record):
        raise RuntimeError("WOW_LAB_SOURCE_RIGHTS_OR_IMAGE_UNVERIFIED")
    out.mkdir(parents=True, exist_ok=False)
    try:
        image, url, digest = engine.save_original(record, out, config)
    except Exception as exc:
        failure = {
            "object_id": object_id,
            "status": "source_acquisition_blocked",
            "reason": str(exc)[:500],
            "rendered": False,
            "artistic_approval": False,
            "publishable": False,
        }
        (out / "PREFLIGHT_RESULT.json").write_text(
            json.dumps(failure, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
        raise
    result = {
        "object_id": object_id, "title": record.get("title"),
        "artist": record.get("artistDisplayName"),
        "museum_url": record.get("objectURL"), "image_url": url,
        "source_sha256": digest, "source_license": "Met Open Access CC0",
        "is_public_domain": True, "rendered": False,
        "artistic_approval": False, "publishable": False,
    }
    try:
        preflight_source(image, out)
        result["status"] = "technical_mask_pass_needs_visual_review"
        code = 0
    except PreflightRejected as err:
        result["status"] = "mask_rejected"
        result["reason"] = str(err)
        code = 2
    result["contact_sheet"] = contact_sheet(out)
    (out / "PREFLIGHT_RESULT.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--object-id", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        raise SystemExit(run(args.object_id, args.out))
    except Exception as exc:
        print("WOW_LAB_PREFLIGHT_FAIL_CLOSED: " + str(exc), file=sys.stderr)
        raise SystemExit(2)
