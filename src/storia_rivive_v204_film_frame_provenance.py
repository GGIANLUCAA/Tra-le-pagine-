#!/usr/bin/env python3
"""V204: prove V101 source PNGs really decode from the SHA-locked archival film.

The V202 byte gate checks the cache, but a matching PNG hash alone does NOT
establish that a cached PNG was extracted from the film. Reproduce the exact
V101 FFmpeg fps extraction and compare decoded RGB pixels for all five jobs.
Research-only; this does not establish distinct shots, rights or artistic QA.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

MAX_FILM_BYTES = 160 * 1024 * 1024
FRAME_NAME = re.compile(r"frame_(0[1-9]|1[0-2])\.png\Z")


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha_pixels(path: Path) -> str:
    with Image.open(path) as image:
        if image.format != "PNG":
            raise ValueError("Not a PNG")
        rgb = image.convert("RGB")
        return hashlib.sha256(rgb.tobytes()).hexdigest()


def inspect(manifest: dict, report: dict, cache: Path) -> dict:
    result = {
        "version": "V204_FILM_FRAME_PROVENANCE",
        "status": "FILM_FRAME_PROVENANCE_BLOCKED",
        "reason": "UNKNOWN",
        "verified_film_extracted_frames": 0,
        "provider_calls_permitted": False,
        "credits_spent": 0,
        "publish_permitted": False,
        "five_distinct_shots_approved": False,
        "italian_rights_approved": False,
    }

    def block(reason: str) -> dict:
        result["reason"] = reason
        return result

    if not isinstance(manifest, dict) or not isinstance(report, dict):
        return block("INVALID_INPUT_SCHEMA")
    if manifest.get("version") != "V102_SOURCE_LOCKED_I2I_JOBS":
        return block("INVALID_V102_MANIFEST")
    if report.get("status") != "REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW":
        return block("SCOUT_NOT_READY")
    expected = report.get("original_sha256")
    if not isinstance(expected, str) or not re.fullmatch(r"[a-fA-F0-9]{64}", expected):
        return block("INVALID_SCOUT_FILM_SHA")
    if manifest.get("source_video_sha256") != expected.lower():
        return block("MANIFEST_FILM_SHA_MISMATCH")
    film = cache / "ORIGINAL_ARCHIVE.webm"
    if film.is_symlink() or not film.is_file() or not 0 < film.stat().st_size <= MAX_FILM_BYTES:
        return block("FILM_MISSING_OR_UNSAFE")
    if sha_file(film) != expected.lower():
        return block("FILM_BYTES_SHA_MISMATCH")
    duration = report.get("duration_s")
    if isinstance(duration, bool) or not isinstance(duration, (float, int)):
        return block("INVALID_SCOUT_DURATION")
    duration = float(duration)
    if not math.isfinite(duration) or not 1 <= duration <= 10000:
        return block("INVALID_SCOUT_DURATION")
    count = report.get("source_frames_extracted")
    if type(count) is not int or not 5 <= count <= 12:
        return block("INVALID_SCOUT_FRAME_COUNT")
    jobs = manifest.get("original_frame_jobs")
    if not isinstance(jobs, list) or len(jobs) != 5:
        return block("INVALID_FIVE_SOURCE_JOBS")

    selected = []
    for job in jobs:
        if not isinstance(job, dict):
            return block("INVALID_SOURCE_JOB")
        source = job.get("source_file")
        if not isinstance(source, str):
            return block("INVALID_SOURCE_PATH")
        path = Path(source)
        if not FRAME_NAME.fullmatch(path.name):
            return block("INVALID_SOURCE_FRAME_NAME")
        expected_path = cache / "original_frames" / path.name
        if (path.is_symlink() or expected_path.is_symlink() or not path.is_file()
                or path.resolve() != expected_path.resolve()):
            return block("SOURCE_FRAME_OUTSIDE_CACHE")
        if not isinstance(job.get("source_sha256"), str) or sha_file(path) != job["source_sha256"]:
            return block("SOURCE_FRAME_BYTES_SHA_MISMATCH")
        selected.append((path.name, path, job.get("source_pixel_sha256")))
    if len({name for name, _, _ in selected}) != 5:
        return block("REUSED_SOURCE_FRAME")

    # V101 scout uses this exact fps filter, count and naming convention.
    # A mismatched decoder/version fails safely rather than certifying fake provenance.
    period = max(1.0, duration / 12)
    fps_filter = "fps=1/" + str(round(period, 4))
    try:
        with tempfile.TemporaryDirectory(prefix="storia-v204-") as tmp:
            output = Path(tmp)
            command = [
                "ffmpeg", "-nostdin", "-y", "-v", "error", "-i", str(film),
                "-vf", fps_filter, "-frames:v", "12",
                str(output / "frame_%02d.png"),
            ]
            subprocess.run(command, check=True, capture_output=True, timeout=180)
            regenerated = sorted(output.glob("frame_*.png"))
            if len(regenerated) != count:
                return block("SCOUT_REEXTRACTION_FRAME_COUNT_MISMATCH")
            for name, source, expected_pixels in selected:
                reference = output / name
                if not reference.is_file():
                    return block("SELECTED_FRAME_NOT_IN_FILM_EXTRACTION")
                if (not isinstance(expected_pixels, str)
                        or sha_pixels(source) != expected_pixels
                        or sha_pixels(reference) != expected_pixels):
                    return block("FRAME_NOT_FROM_SHA_LOCKED_FILM")
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError, ValueError):
        return block("SCOUT_REEXTRACTION_FAILED")

    result.update({
        "status": "FIVE_FRAMES_REEXTRACTED_FROM_FILM_REVIEW_PENDING",
        "reason": "FIVE_EXACT_FILM_FRAME_PIXELS_MATCH; SHOTS_AND_RIGHTS_UNREVIEWED",
        "verified_film_extracted_frames": 5,
        "source_film_sha256": expected.lower(),
        "fps_filter": fps_filter,
    })
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--scout-report", required=True)
    parser.add_argument("--cache", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    try:
        data = inspect(
            json.loads(Path(args.manifest).read_text(encoding="utf-8")),
            json.loads(Path(args.scout_report).read_text(encoding="utf-8")),
            Path(args.cache),
        )
    except (OSError, ValueError, TypeError) as exc:
        data = {
            "version": "V204_FILM_FRAME_PROVENANCE",
            "status": "FILM_FRAME_PROVENANCE_BLOCKED",
            "reason": "INVALID_OR_MISSING_INPUT_" + type(exc).__name__,
            "verified_film_extracted_frames": 0,
            "provider_calls_permitted": False,
            "credits_spent": 0,
            "publish_permitted": False,
        }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(data["status"], data["reason"])
    if data["status"] != "FIVE_FRAMES_REEXTRACTED_FROM_FILM_REVIEW_PENDING":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
