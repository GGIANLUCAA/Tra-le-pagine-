"""WOW LAB: fail-closed packaging gate for experimental outputs.

A technical preview must never be mislabeled as an artistically approved master.
This gate only verifies that required audit artifacts exist and agree.
"""
from __future__ import annotations
import json
from pathlib import Path

REQUIRED = (
    "SUBJECT_PREFLIGHT.json",
    "SUBJECT_MASK.png",
    "MASK_BEFORE_RENDER.jpg",
    "CLEAN_PLATE_AUDIT.json",
    "POPOUT_GEOMETRY_PREFLIGHT.json",
    "VIDEO_REVIEW.json",
    "VIDEO_CONTACT_SHEET.jpg",
    "WOW_LAB_PREVIEW.mp4",
    "COVER.jpg",
)

def validate_preview_package(directory: Path) -> dict:
    directory = Path(directory)
    missing = [name for name in REQUIRED if not (directory / name).is_file()
               or (directory / name).stat().st_size == 0]
    reasons = ["missing_or_empty:" + name for name in missing]
    # A non-empty placeholder is not an image or video. Reject invalid signatures
    # even when JSON reports claim a technical pass.
    signatures = {
        "SUBJECT_MASK.png": lambda b: b.startswith(b"\x89PNG\r\n\x1a\n"),
        "MASK_BEFORE_RENDER.jpg": lambda b: b.startswith(b"\xff\xd8\xff"),
        "VIDEO_CONTACT_SHEET.jpg": lambda b: b.startswith(b"\xff\xd8\xff"),
        "COVER.jpg": lambda b: b.startswith(b"\xff\xd8\xff"),
        "WOW_LAB_PREVIEW.mp4": lambda b: len(b) >= 12 and b[4:8] == b"ftyp",
    }
    for name, check in signatures.items():
        if name not in missing:
            try:
                with (directory / name).open("rb") as stream:
                    header = stream.read(32)
                if not check(header):
                    reasons.append("invalid_media_signature:" + name)
            except OSError:
                reasons.append("unreadable_media:" + name)
    reports = {}
    for name in ("SUBJECT_PREFLIGHT.json", "CLEAN_PLATE_AUDIT.json",
                 "POPOUT_GEOMETRY_PREFLIGHT.json", "VIDEO_REVIEW.json"):
        if name in missing:
            continue
        try:
            reports[name] = json.loads((directory / name).read_text(encoding="utf-8"))
        except (ValueError, OSError):
            reasons.append("invalid_json:" + name)
    for name, key in (
        ("SUBJECT_PREFLIGHT.json", "technical_pass"),
        ("CLEAN_PLATE_AUDIT.json", "pass"),
        ("POPOUT_GEOMETRY_PREFLIGHT.json", "pass"),
        ("VIDEO_REVIEW.json", "technical_pass"),
        ("VIDEO_REVIEW.json", "full_decode_pass"),
    ):
        if name in reports and reports[name].get(key) is not True:
            reasons.append("failed_gate:" + name + ":" + key)
    for name, report in reports.items():
        if report.get("artistic_approval") is True:
            reasons.append("unverified_artistic_approval:" + name)
    return {
        "technical_preview_package_pass": not reasons,
        "reasons": reasons,
        "artistic_approval": False,
        "approved_master": False,
        "release_as_success_allowed": False,
    }
