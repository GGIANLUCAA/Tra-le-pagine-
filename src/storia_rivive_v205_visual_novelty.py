#!/usr/bin/env python3
"""V205: reject visually redundant 9:16 source frames before any I2I/Vidu.

Uses genuine PNG bytes already verified by V202/V204. This is a conservative
near-duplicate preflight, NOT a certificate of five distinct camera shots,
Italian copyright, photo realism or permission to spend credits.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageOps, ImageStat

READY_V204 = "FIVE_FRAMES_REEXTRACTED_FROM_FILM_REVIEW_PENDING"
READY_V205 = "FIVE_VISUALLY_NONREDUNDANT_FRAMES_SHOT_REVIEW_PENDING"
MAX_PNG_PIXELS = 24_000_000


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def fingerprint(path: Path):
    with Image.open(path) as raw:
        if raw.format != "PNG" or raw.width * raw.height > MAX_PNG_PIXELS:
            raise ValueError("Unsupported source image")
        rgb = raw.convert("RGB")
        pixel_sha = hashlib.sha256(rgb.tobytes()).hexdigest()
        # Only the pixels actually visible in a center-cropped vertical reel.
        w, h = rgb.size
        crop_w = min(w, h * 9 // 16)
        left = (w - crop_w) // 2
        portrait = rgb.crop((left, 0, left + crop_w, h))
        gray = ImageOps.grayscale(portrait).resize((96, 96), Image.Resampling.BILINEAR)
        normalized = ImageOps.autocontrast(gray)
        small = normalized.resize((9, 8), Image.Resampling.BILINEAR)
        px = list(small.getdata())
        dhash = sum((1 << (y * 8 + x)) for y in range(8) for x in range(8)
                    if px[y * 9 + x] > px[y * 9 + x + 1])
        return pixel_sha, gray, normalized, dhash


def inspect(manifest: dict, provenance: dict, cache: Path) -> dict:
    result = {
        "version": "V205_VISUAL_NOVELTY",
        "status": "VISUAL_NOVELTY_BLOCKED",
        "reason": "UNKNOWN",
        "provider_calls_permitted": False,
        "publish_permitted": False,
        "five_distinct_shots_approved": False,
        "italian_rights_approved": False,
        "credits_spent": 0,
    }

    def block(reason):
        result["reason"] = reason
        return result

    if not isinstance(manifest, dict) or not isinstance(provenance, dict):
        return block("INVALID_INPUT")
    if provenance.get("status") != READY_V204:
        return block("V204_PROVENANCE_NOT_VERIFIED")
    if provenance.get("source_film_sha256") != manifest.get("source_video_sha256"):
        return block("PROVENANCE_FILM_MISMATCH")
    jobs = manifest.get("original_frame_jobs")
    if not isinstance(jobs, list) or len(jobs) != 5:
        return block("NOT_FIVE_SOURCE_JOBS")
    names = provenance.get("selected_frame_names")
    hashes = provenance.get("selected_frame_pixel_sha256")
    if not isinstance(names, list) or not isinstance(hashes, list) or len(names) != 5 or len(hashes) != 5:
        return block("V204_FRAME_BINDING_MISSING")
    fingerprints = []
    frame_names = []
    for job in jobs:
        if not isinstance(job, dict):
            return block("INVALID_JOB")
        path_text = job.get("source_file")
        if not isinstance(path_text, str):
            return block("INVALID_SOURCE_PATH")
        path = Path(path_text)
        expected = cache / "original_frames" / path.name
        if (path.is_symlink() or expected.is_symlink() or not path.is_file()
                or path.resolve() != expected.resolve()):
            return block("SOURCE_OUTSIDE_VERIFIED_CACHE")
        if digest(path) != job.get("source_sha256"):
            return block("SOURCE_BYTES_CHANGED_AFTER_V204")
        try:
            pixels, gray, normalized, dhash = fingerprint(path)
        except (OSError, ValueError, Image.DecompressionBombError):
            return block("SOURCE_IMAGE_DECODE_FAILED")
        if pixels != job.get("source_pixel_sha256"):
            return block("SOURCE_PIXELS_CHANGED_AFTER_V204")
        fingerprints.append((gray, normalized, dhash))
        frame_names.append(path.name)
    if frame_names != names or [j["source_pixel_sha256"] for j in jobs] != hashes:
        return block("V204_FRAME_BINDING_MISMATCH")
    comparisons = []
    for i in range(5):
        for j in range(i + 1, 5):
            gray_a, norm_a, hash_a = fingerprints[i]
            gray_b, norm_b, hash_b = fingerprints[j]
            raw_mad = ImageStat.Stat(ImageChops.difference(gray_a, gray_b)).mean[0]
            normalized_mad = ImageStat.Stat(ImageChops.difference(norm_a, norm_b)).mean[0]
            hash_distance = (hash_a ^ hash_b).bit_count()
            comparisons.append({
                "frames": [frame_names[i], frame_names[j]],
                "raw_mad": round(raw_mad, 2),
                "normalized_mad": round(normalized_mad, 2),
                "dhash_distance": hash_distance,
            })
            if min(raw_mad, normalized_mad) < 8 or (hash_distance <= 5 and normalized_mad < 20):
                result["suspect_pair"] = comparisons[-1]
                return block("NEAR_DUPLICATE_VISIBLE_PORTRAIT_FRAMES")
    result.update({
        "status": READY_V205,
        "reason": "NO_NEAR_DUPLICATE_VISIBLE_FRAMES; FIVE_CAMERA_SHOTS_STILL_REQUIRE_HUMAN_REVIEW",
        "checked_pairs": len(comparisons),
        "pairwise_advisory": comparisons,
        "shot_review_required": True,
    })
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", required=True)
    p.add_argument("--provenance", required=True)
    p.add_argument("--cache", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    try:
        report = inspect(json.loads(Path(a.manifest).read_text()),
                         json.loads(Path(a.provenance).read_text()), Path(a.cache))
    except (OSError, ValueError, TypeError):
        report = {"version": "V205_VISUAL_NOVELTY", "status": "VISUAL_NOVELTY_BLOCKED",
                  "reason": "INVALID_OR_MISSING_INPUT", "provider_calls_permitted": False,
                  "publish_permitted": False, "credits_spent": 0}
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(report["status"], report["reason"])
    if report["status"] != READY_V205:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
