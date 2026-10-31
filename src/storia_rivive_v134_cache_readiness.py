#!/usr/bin/env python3
"""V134: verify actual cached scout bytes before ranking or source-locked I2I.

This is a FREE integrity gate, not a native-HD, five-shot, rights or artistic approval.
Never repairs/accepts a missing source by trusting JSON status alone.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def assess(cache_dir, order):
    """Bind cached bytes to the *current* candidate and exact archival page.

    SHA-valid bytes from a different film are not an acceptable cache hit.
    This remains research-only; rights and scene quality are NOT approved.
    """
    root = Path(cache_dir)
    blocked = {"ready": False, "status": "SOURCE_CACHE_INTEGRITY_BLOCKED",
               "paid_api_call_permitted": False, "publish_permitted": False}
    try:
        if (not isinstance(order, dict)
                or order.get("contract") != "LA_STORIA_RIVIVE_V101_SAFE_AUTOPILOT"
                or order.get("episode_id") != root.name
                or not isinstance(order.get("source_page"), str)
                or not order["source_page"].startswith("https://commons.wikimedia.org/wiki/File:")):
            return {**blocked, "reason": "CURRENT_WORK_ORDER_SOURCE_BINDING_INVALID"}
        report_path = root / "SCOUT_REPORT.json"
        if not report_path.is_file() or report_path.is_symlink():
            return {**blocked, "reason": "SCOUT_REPORT_MISSING"}
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if not isinstance(report, dict) or report.get("status") != "REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW":
            return {**blocked, "reason": "SCOUT_NOT_READY"}
        if report.get("source_page") != order["source_page"]:
            return {**blocked, "reason": "CACHED_FILM_SOURCE_PAGE_MISMATCH"}
        film = root / "ORIGINAL_ARCHIVE.webm"
        if not film.is_file() or film.is_symlink():
            return {**blocked, "reason": "ORIGINAL_FILM_MISSING"}
        film_sha = report.get("original_sha256")
        if (not isinstance(film_sha, str)
                or not re.fullmatch(r"[0-9a-f]{64}", film_sha)
                or digest(film) != film_sha
                or report.get("frame_provenance_source_sha256") != film_sha
                or report.get("frame_provenance_version") != "V112_SOURCE_PTS_FROM_FFMPEG_SHOWINFO"):
            return {**blocked, "reason": "FILM_OR_PROVENANCE_SHA_MISMATCH"}
        shot = report.get("shot_boundary_analysis")
        if not isinstance(shot, dict) or shot.get("source_sha256") != film_sha:
            return {**blocked, "reason": "SHOT_AUDIT_FILM_SHA_MISMATCH"}
        rows = report.get("frame_provenance")
        if (not isinstance(rows, list) or not 5 <= len(rows) <= 12
                or report.get("source_frames_extracted") != len(rows)):
            return {**blocked, "reason": "FRAME_PROVENANCE_COUNT_INVALID"}
        folder = root / "original_frames"
        files = sorted(folder.glob("frame_*.png"))
        if len(files) != len(rows):
            return {**blocked, "reason": "SOURCE_PNG_COUNT_MISMATCH"}
        seen = set()
        for row in rows:
            if not isinstance(row, dict):
                return {**blocked, "reason": "SOURCE_PNG_PROVENANCE_INVALID"}
            name, expected = row.get("filename"), row.get("sha256")
            if (not isinstance(name, str) or not re.fullmatch(r"frame_[0-9]{2}[.]png", name)
                    or name in seen or not isinstance(expected, str)
                    or not re.fullmatch(r"[0-9a-f]{64}", expected)
                    or row.get("source_pts_logged_from_decode") is not True
                    or type(row.get("source_pts")) is not int
                    or type(row.get("source_pts_time_s")) not in (int, float)
                    or not math.isfinite(row["source_pts_time_s"])):
                return {**blocked, "reason": "SOURCE_PNG_PROVENANCE_INVALID"}
            seen.add(name)
            p = folder / name
            if not p.is_file() or p.is_symlink() or digest(p) != expected:
                return {**blocked, "reason": "SOURCE_PNG_SHA_MISMATCH"}
        if set(p.name for p in files) != seen:
            return {**blocked, "reason": "SOURCE_PNG_NAME_MISMATCH"}
        return {"ready": True, "status": "SOURCE_CACHE_BYTES_VERIFIED_REVIEW_REQUIRED",
                "verified_source_png_count": len(rows),
                "candidate_id": order["episode_id"],
                "source_page_sha256": hashlib.sha256(order["source_page"].encode("utf-8")).hexdigest(),
                "paid_api_call_permitted": False, "publish_permitted": False,
                "note": "Byte integrity only; not proof of native detail, five shots or rights."}
    except (OSError, ValueError, TypeError, OverflowError, KeyError, json.JSONDecodeError):
        return {**blocked, "reason": "CACHE_READ_OR_SCHEMA_INVALID"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-dir", required=True)
    parser.add_argument("--order", required=True, help="Current V101 WORK_ORDER.json")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    order = json.loads(Path(args.order).read_text(encoding="utf-8"))
    result = assess(args.cache_dir, order)
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("V134_SOURCE_READINESS", result["status"], result.get("reason", "OK"))


if __name__ == "__main__":
    main()
