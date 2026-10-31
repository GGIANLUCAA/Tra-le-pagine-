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
