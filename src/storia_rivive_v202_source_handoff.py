#!/usr/bin/env python3
"""V202: verify V102's four I2I inputs + fifth Vidu anchor against actual scout bytes.

Offline and read-only. This attests provenance, not shot distinctness, Italian
rights, generative restoration, human QA, provider authorization or publication.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from PIL import Image

READY = "REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW"
MAX_FILM_BYTES = 160 * 1024 * 1024
# V203: reject unusable native 9:16 crops before preparing paid I2I/Vidu.
# These are conservative technical floors, NOT a certification of face detail.
MIN_NATIVE_PORTRAIT_WIDTH = 400
MIN_NATIVE_HEIGHT = 720


def digest_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def inspect(manifest: dict, order: dict, report: dict, cache: Path) -> dict:
    result = {
        "version": "V202_SOURCE_HANDOFF",
        "status": "SOURCE_HANDOFF_BLOCKED",
        "reason": "UNKNOWN",
        "verified_photo_source_frames": 0,
        "verified_vidu_source_anchors": 0,
        "provider_calls_permitted": False,
        "credits_spent": 0,
        "photos_generated": 0,
        "vidu_clips_generated": 0,
        "publish_permitted": False,
        "artistic_review_pending": True,
        "italian_rights_review_pending": True,
    }

    def block(reason: str) -> dict:
        result["reason"] = reason
        return result

    if not all(isinstance(x, dict) for x in (manifest, order, report)):
        return block("INVALID_INPUT_SCHEMA")
    if order.get("contract") != "LA_STORIA_RIVIVE_V101_SAFE_AUTOPILOT":
        return block("INVALID_WORK_ORDER")
    if order.get("paid_api_call_permitted") is not False or order.get("publish_permitted") is not False:
        return block("UNSAFE_WORK_ORDER")
    if report.get("status") != READY or report.get("source_page") != order.get("source_page"):
        return block("SCOUT_REPORT_NOT_BOUND_TO_ORDER")
    if manifest.get("version") != "V102_SOURCE_LOCKED_I2I_JOBS":
        return block("INVALID_V102_MANIFEST")
    if manifest.get("cycle_id") != order.get("cycle_id") or manifest.get("episode_id") != order.get("episode_id"):
        return block("MANIFEST_WORK_ORDER_MISMATCH")
    if (manifest.get("source_frames_prepared") != 5 or manifest.get("photos_requested") != 4
            or manifest.get("photo_jobs_prepared") != 4):
        return block("INVALID_FOUR_PLUS_ONE_COUNTS")
    if (manifest.get("photos_generated") != 0 or manifest.get("photos_approved") != 0
            or manifest.get("provider_requests_sent") != 0 or manifest.get("paid_api_calls") != 0
            or manifest.get("vidu_calls") != 0 or manifest.get("publication_permitted") is not False):
        return block("UNVERIFIED_GENERATION_OR_PERMISSION_CLAIM")

    expected = report.get("original_sha256")
    if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", expected):
        return block("INVALID_SCOUT_FILM_SHA")
    film = cache / "ORIGINAL_ARCHIVE.webm"
    if film.is_symlink() or not film.is_file():
        return block("FILM_MISSING_OR_SYMLINK")
    if not 0 < film.stat().st_size <= MAX_FILM_BYTES:
        return block("FILM_SIZE_UNSAFE")
    film_sha = digest_file(film)
    if film_sha != expected.lower() or manifest.get("source_video_sha256") != film_sha:
        return block("FILM_BYTES_SHA_MISMATCH")

    jobs = manifest.get("original_frame_jobs")
    if not isinstance(jobs, list) or len(jobs) != 5:
        return block("MISSING_FIVE_SOURCE_JOBS")
    pixels_seen = set()
    geometry = None
    for index, job in enumerate(jobs):
        if not isinstance(job, dict):
            return block("INVALID_SOURCE_JOB")
        name = f"frame_{index + 1:02d}.png"
        # Selection may reorder frames; source paths must still be actual native
        # PNGs in the verified cache, not an arbitrary external file.
        supplied = job.get("source_file")
        if not isinstance(supplied, str):
            return block("MISSING_SOURCE_PATH")
        path = Path(supplied)
        if not re.fullmatch(r"frame_\d{2}\.png", path.name):
            return block("UNSAFE_SOURCE_FRAME_NAME")
        if path.is_symlink() or not path.is_file() or path.resolve().parent != (cache / "original_frames").resolve():
            return block("SOURCE_FRAME_OUTSIDE_VERIFIED_CACHE")
        if not isinstance(job.get("source_sha256"), str) or digest_file(path) != job["source_sha256"]:
            return block("SOURCE_FRAME_BYTES_SHA_MISMATCH")
        try:
            with Image.open(path) as im:
                if im.format != "PNG":
                    return block("SOURCE_NOT_PNG")
                rgb = im.convert("RGB")
                width, height = rgb.size
                pixel_sha = hashlib.sha256(rgb.tobytes()).hexdigest()
        except (OSError, ValueError):
            return block("SOURCE_PNG_DECODE_FAILED")
        if min(width, height) < 240 or job.get("source_raster_px") != [width, height]:
            return block("SOURCE_RASTER_MISMATCH")
        native_portrait_width = min(width, (height * 9) // 16)
        if height < MIN_NATIVE_HEIGHT or native_portrait_width < MIN_NATIVE_PORTRAIT_WIDTH:
            return block("SOURCE_NATIVE_PORTRAIT_CROP_TOO_SMALL")
        if geometry is None:
            geometry = (width, height)
        elif geometry != (width, height):
            return block("MIXED_FRAME_GEOMETRY")
        if pixel_sha in pixels_seen or job.get("source_pixel_sha256") != pixel_sha:
            return block("SOURCE_PIXELS_DUPLICATED_OR_MISMATCHED")
        pixels_seen.add(pixel_sha)
        if job.get("request_sent") is not False or job.get("result_file") is not None:
            return block("UNVERIFIED_PROVIDER_RESULT")
        if job.get("restored_photo_approved") is not False:
            return block("FORGED_PHOTO_APPROVAL")
        if index < 4:
            if (job.get("target_kind") != "REAL_SOURCE_LOCKED_I2I_PHOTOGRAPH"
                    or job.get("role") != "STATIC_COLOR_REVEAL"
                    or not isinstance(job.get("prompt"), str) or not job["prompt"]
                    or job.get("provider") != "NOT_SELECTED_NO_CALL"):
                return block("PHOTO_JOB_ROLE_INVALID")
        else:
            if (job.get("target_kind") != "VIDU_SOURCE_ANCHOR_NO_I2I"
                    or job.get("role") != "VIDU_SOURCE_ANCHOR_NOT_RENDERED"
                    or job.get("prompt") is not None or job.get("provider") != "NOT_APPLICABLE_NO_I2I"):
                return block("VIDU_ANCHOR_ROLE_INVALID")
        if job.get("allow_source_reframing") is not False or job.get("allow_invented_people") is not False:
            return block("UNSAFE_SOURCE_TRANSFORMATION_POLICY")

    anchor = manifest.get("vidu_source_anchor")
    fifth = jobs[4]
    if (not isinstance(anchor, dict)
            or anchor.get("source_file") != fifth["source_file"]
            or anchor.get("source_sha256") != fifth["source_sha256"]
            or anchor.get("source_pixel_sha256") != fifth["source_pixel_sha256"]
            or anchor.get("approved") is not False
            or anchor.get("vidu_request_sent") is not False):
        return block("VIDU_ANCHOR_NOT_BOUND_TO_FIFTH_FRAME")
    result.update({
        "status": "SOURCE_HANDOFF_BYTES_VERIFIED_REVIEW_PENDING",
        "reason": "FIVE_NATIVE_PNG_BYTES_AND_FILM_SHA_MATCH; NOT_FIVE_VERIFIED_SHOTS",
        "verified_photo_source_frames": 4,
        "verified_vidu_source_anchors": 1,
        "source_film_sha256": film_sha,
        "native_portrait_crop_px": [native_portrait_width, height],
        "native_crop_preflight_only": True,
    })
    return result


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", required=True)
    p.add_argument("--order", required=True)
    p.add_argument("--scout-report", required=True)
    p.add_argument("--cache", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    try:
        data = inspect(
            json.loads(Path(a.manifest).read_text(encoding="utf-8")),
            json.loads(Path(a.order).read_text(encoding="utf-8")),
            json.loads(Path(a.scout_report).read_text(encoding="utf-8")),
            Path(a.cache),
        )
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        data = {"version": "V202_SOURCE_HANDOFF", "status": "SOURCE_HANDOFF_BLOCKED",
                "reason": "INVALID_OR_MISSING_INPUT: " + type(exc).__name__,
                "provider_calls_permitted": False, "credits_spent": 0,
                "publish_permitted": False}
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(data["status"], data["reason"])
    if data["status"] != "SOURCE_HANDOFF_BYTES_VERIFIED_REVIEW_PENDING":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
