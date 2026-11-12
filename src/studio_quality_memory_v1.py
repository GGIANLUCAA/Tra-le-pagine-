#!/usr/bin/env python3
"""Persistent, evidence-aware production lessons. Pure offline preflight by default.

A feedback note is not proof of a fixed video. Only owner-approved/verified
rules are inherited by future plans, without autonomous renders or publication.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATH = ROOT / "quality" / "STUDIO_VIDEO_LESSONS_V1.json"
SCHEMA = "studio-video-lessons-v1"
ACTIVE = frozenset({"owner_approved", "verified_effective"})
STATES = frozenset({"reported", "trial", "owner_approved", "verified_effective", "rejected"})
FORMATS = frozenset({
    "libri", "artvision_critico", "artvision_cinema", "controluce",
    "visual_music", "hyperlumen", "storia_rivive", "wow",
})
PROJECT_TO_FORMATS = {
    "artvision": {"artvision_critico", "artvision_cinema"},
    "storia": {"storia_rivive"},
    "wow": {"wow"},
}
ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{3,95}$")
SHA = re.compile(r"^[0-9a-f]{64}$")
SLOT = frozenset({"critico_standard", "critico_museum", "cinema_standard", "cinema_museum"})
CATEGORIES = frozenset({"direction", "pacing", "audio", "visual", "authenticity",
                        "editorial", "download", "other"})


def _lesson_valid(row: object) -> bool:
    if not isinstance(row, dict):
        return False
    if (not ID.fullmatch(str(row.get("id", "")))
            or row.get("status") not in STATES
            or not isinstance(row.get("title"), str) or not row["title"].strip()
            or not isinstance(row.get("rule"), str) or not row["rule"].strip()
            or not isinstance(row.get("check"), str) or not row["check"].strip()
            or not isinstance(row.get("source"), str) or not row["source"].strip()
            or not isinstance(row.get("applies_to"), list)
            or not row["applies_to"]
            or any(not isinstance(fmt, str) or (fmt != "all" and fmt not in FORMATS)
                   for fmt in row["applies_to"])):
        return False
    if row.get("status") == "verified_effective":
        return (row.get("effectiveness_proven_by_new_video") is True
                and row.get("owner_confirmed") is True
                and isinstance(row.get("evidence_sha256"), str)
                and bool(SHA.fullmatch(row["evidence_sha256"]))
                and bool(row.get("comparison_report")))
    return True


def _history_valid(row: object) -> bool:
    if not isinstance(row, dict):
        return False
    if (not ID.fullmatch(str(row.get("id", "")))
            or not ID.fullmatch(str(row.get("work_id", "")))
            or not isinstance(row.get("note"), str)
            or not 4 <= len(row["note"].strip()) <= 1800
            or row.get("status") not in STATES
            or row.get("category") not in CATEGORIES):
        return False
    if row.get("slot_id") is not None and row.get("slot_id") not in SLOT:
        return False
    if row.get("status") == "verified_effective":
        return (row.get("owner_confirmed") is True
                and row.get("before_after_comparison") is True
                and isinstance(row.get("video_sha256"), str)
                and bool(SHA.fullmatch(row["video_sha256"]))
                and isinstance(row.get("qa_reference"), str)
                and bool(row["qa_reference"].strip()))
    return True


def load(path: str | Path = DEFAULT_PATH) -> dict | None:
    """Fail closed, never turn an absent or malformed ledger into approvals."""
    try:
        doc = json.loads(Path(path).read_text(encoding="utf-8"))
    except (ValueError, OSError, UnicodeError, TypeError):
        return None
    if (not isinstance(doc, dict) or doc.get("schema") != SCHEMA
            or not isinstance(doc.get("lessons"), list)
            or not isinstance(doc.get("history"), list)
            or len(doc["lessons"]) > 300 or len(doc["history"]) > 10000
            or not all(_lesson_valid(row) for row in doc["lessons"])
            or not all(_history_valid(row) for row in doc["history"])):
        return None
    keys = [row["id"] for row in doc["lessons"] + doc["history"]]
    if len(keys) != len(set(keys)):
        return None
    return doc


def applicable(doc: dict | None, fmt: str) -> list[dict]:
    if fmt not in FORMATS or not doc or doc.get("schema") != SCHEMA:
        return []
    return [
        {"id": row["id"], "title": row["title"], "rule": row["rule"],
         "check": row["check"], "source": row["source"], "status": row["status"],
         "effectiveness_proven_by_new_video":
             row.get("effectiveness_proven_by_new_video") is True}
        for row in doc["lessons"]
        if row["status"] in ACTIVE and ("all" in row["applies_to"] or fmt in row["applies_to"])
    ]


def project_summary(doc: dict | None, project: str) -> dict:
    fmts = PROJECT_TO_FORMATS.get(project, set())
    rows = [lesson for fmt in sorted(fmts) for lesson in applicable(doc, fmt)]
    unique = {row["id"]: row for row in rows}
    return {
        "ledger": "quality/STUDIO_VIDEO_LESSONS_V1.json",
        "state": "AVAILABLE" if doc is not None else "MISSING_OR_INVALID",
        "lesson_ids": sorted(unique),
        "lessons_inherited": len(unique),
        "proof_of_improvement_in_new_mp4": False,
        "feedback_history_records": len(doc["history"]) if doc else None,
        "does_not_render_or_publish": True,
    }


def record_feedback(doc: dict, entry: dict) -> dict:
    """Build a new candidate ledger; caller must commit it deliberately."""
    if load_object(doc) is None:
        raise ValueError("Invalid memory ledger")
    proposed = dict(entry)
    proposed["status"] = "reported"
    if not _history_valid(proposed):
        raise ValueError("Bad feedback record: needs stable work ID, category and note")
    if any(row["id"] == proposed["id"] for row in doc["history"] + doc["lessons"]):
        raise ValueError("Feedback id already exists")
    result = json.loads(json.dumps(doc))
    result["history"].append(proposed)
    return result


def promote_feedback(doc: dict, feedback_id: str, lesson: dict) -> dict:
    """Only a review with actual MP4/QA proof can become verified_effective."""
    if load_object(doc) is None:
        raise ValueError("Invalid memory ledger")
    rows = [h for h in doc["history"] if h["id"] == feedback_id]
    if len(rows) != 1 or rows[0]["status"] == "rejected":
        raise ValueError("Feedback not found or rejected")
    if (rows[0].get("status") != "verified_effective"
            or not _history_valid(rows[0])
            or not _lesson_valid(lesson)
            or lesson.get("status") != "verified_effective"):
        raise ValueError("Evidence and owner confirmation required")
    if any(row["id"] == lesson["id"] for row in doc["history"] + doc["lessons"]):
        raise ValueError("Lesson id already exists")
    result = json.loads(json.dumps(doc))
    result["lessons"].append(lesson)
    return result


def load_object(obj: object) -> dict | None:
    if not isinstance(obj, dict) or obj.get("schema") != SCHEMA:
        return None
    try:
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as folder:
            p = Path(folder) / "ledger.json"
            p.write_text(json.dumps(obj), encoding="utf-8")
            return load(p)
    except (ValueError, OSError, TypeError):
        return None


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ledger", type=Path, default=DEFAULT_PATH)
    p.add_argument("--format", choices=sorted(FORMATS))
    p.add_argument("--project", choices=sorted(PROJECT_TO_FORMATS))
    p.add_argument("--out", type=Path)
    p.add_argument("--feedback-json", type=Path,
                   help="Prepare a reported feedback entry; requires --out and a manual PR")
    args = p.parse_args()
    doc = load(args.ledger)
    if args.feedback_json:
        if not doc or not args.out:
            p.error("A valid ledger and --out are required to record feedback")
        proposed = json.loads(args.feedback_json.read_text(encoding="utf-8"))
        if not isinstance(proposed, dict):
            p.error("Feedback JSON must be an object")
        output = record_feedback(doc, proposed)
    elif args.format:
        output = {"schema": "studio-quality-checklist-v1", "format": args.format,
                  "ledger_state": "AVAILABLE" if doc else "MISSING_OR_INVALID",
                  "active_lessons": applicable(doc, args.format),
                  "video_quality_verified": False}
    elif args.project:
        output = project_summary(doc, args.project)
    else:
        output = {"schema": SCHEMA, "available": doc is not None,
                  "lessons": len(doc["lessons"]) if doc else None,
                  "history": len(doc["history"]) if doc else None}
    encoded = json.dumps(output, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")


if __name__ == "__main__":
    main()
