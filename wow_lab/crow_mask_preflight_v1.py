#!/usr/bin/env python3
"""WOW LAB only — high resolution visual source and mask scout; NO rendering."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

import engine

OBJECT_ID = 56706
ROOT = Path(__file__).resolve().parent


def build(out: Path):
    config = engine.read_config(ROOT / "config.json")
    assert config["no_vidu"] and config["no_paid_services"] and config["no_social_publish"]
    base = (ROOT / "runs").resolve()
    out = out.resolve()
    if base not in out.parents:
        raise RuntimeError("Output escapes WOW LAB runs")
    out.mkdir(parents=True, exist_ok=True)

    # Only Met official metadata & original source; strictly read-only GET.
    rec = engine.get_json(engine.object_url(OBJECT_ID))
    if rec.get("objectID") != OBJECT_ID or not engine.valid_object(rec):
        raise RuntimeError("Official record is not a CC0 print with an image")
    source, url, digest = engine.save_original(rec, out, config)
    w, h = source.size
    if w < 850 or h < 600:
        raise RuntimeError("Source below minimum size")

    # Initial conservative candidate mask only: human visual approval is REQUIRED.
    # It is not a segmentation approval and MUST NOT authorize a render.
    rgb = np.asarray(source)
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    y0, y1 = int(h * .18), int(h * .97)
    x0, x1 = int(w * .16), int(w * .86)
    dark = np.uint8(gray < 118) * 255
    roi = np.zeros((h, w), np.uint8)
    roi[y0:y1, x0:x1] = 255
    dark = cv2.bitwise_and(dark, roi)
    # Work on the authentic high-res pixels, not a 512px image search thumbnail.
    dark = cv2.morphologyEx(dark, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    n, labels, stats, centers = cv2.connectedComponentsWithStats(dark, 8)
    ids = [i for i in range(1, n) if stats[i, cv2.CC_STAT_AREA] > w*h*.0005]
    ids.sort(key=lambda i: stats[i, cv2.CC_STAT_AREA], reverse=True)
    if not ids:
        raise RuntimeError("No plausible dark silhouette; fail closed")
    best = ids[0]
    candidate = np.uint8(labels == best) * 255
    # Preserve the original silhouette for audit; do not invent missing limbs.
    contour, _ = cv2.findContours(candidate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contour:
        raise RuntimeError("Empty silhouette contour")
    x, y, cw, ch = cv2.boundingRect(max(contour, key=cv2.contourArea))
    area = float(stats[best, cv2.CC_STAT_AREA]) / (w*h)
    note = {
        "status": "MASK_CANDIDATE_NOT_APPROVED",
        "object_id": OBJECT_ID,
        "title": rec.get("title"),
        "artist": rec.get("artistDisplayName"),
        "source": rec.get("objectURL"),
        "image_url": url,
        "source_sha256": digest,
        "source_resolution": [w, h],
        "isPublicDomain": rec.get("isPublicDomain"),
        "license": "The Met Open Access CC0",
        "segment_pixel_area_ratio": area,
        "segment_box": [x, y, cw, ch],
        "mask_approved": False,
        "render_allowed": False,
        "paid_api_cost": 0,
        "notes": "Review full-resolution candidate; check beak, eye, tail, claws, source background and double-subject risk. No rendering or automatic art approval.",
    }
    Image.fromarray(candidate).save(out / "MASK_CANDIDATE_FULL.png")
    overlay = rgb.copy()
    cs, _ = cv2.findContours(candidate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(overlay, cs, -1, (255, 48, 42), max(3, w // 500))
    audit = Image.fromarray(overlay)
    audit.thumbnail((1300, 1700))
    audit.save(out / "MASK_AUDIT.jpg", quality=91)
    side = Image.new("RGB", (800, 600), (242, 238, 228))
    left = source.copy(); left.thumbnail((400, 580))
    center = Image.new("RGB", source.size, (244, 239, 229))
    center.paste(source, (0,0), Image.fromarray(candidate))
    center.thumbnail((400, 580))
    side.paste(left, ((400-left.width)//2, (600-left.height)//2))
    side.paste(center, (400+(400-center.width)//2, (600-center.height)//2))
    side.save(out / "SOURCE_VS_EXTRACTED_PREVIEW.jpg", quality=91)
    (out / "SOURCE_AND_MASK_QA.json").write_text(json.dumps(note, ensure_ascii=False, indent=2)+"\n",encoding="utf8")
    print(json.dumps(note, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    raise SystemExit(build(Path(args.out)))
