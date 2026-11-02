#!/usr/bin/env python3
"""Fail-closed ArtVision V128 gate for the ten owner-selected 4x1 works.

This tool does not render, spend money, call TTS, or approve museum presets.
Use 'validate' to check the editorial queue; 'render-check' needs independent
source/license/room/voice evidence before any rendering is attempted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

DEFAULT_QUEUE = Path("queue/artvision_owner_selected_ten_20261102.json")
REQUIRED_SLOTS = ("critico_standard", "critico_museum", "cinema_standard", "cinema_museum")


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_queue(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    works = data.get("works", [])
    ids = [w.get("id") for w in works]
    if data.get("owner_automation_id") != "6adca191603c8191a90d5190901cd034":
        raise ValueError("owner automation mismatch")
    if len(works) != 10 or len(set(ids)) != 10 or any(not item for item in ids):
        raise ValueError("expected exactly ten unique selected works")
    if data.get("existing_cinema_candidates_count") != sum(
        bool(w.get("preexisting_cinema_candidate")) for w in works
    ):
        raise ValueError("legacy Cinema deduplication count inconsistent")
    for w in works:
        if tuple(w.get("four_slots", [])) != REQUIRED_SLOTS:
            raise ValueError(f"four-slot contract mismatch: {w['id']}")
        if w.get("Gold_V25") or w.get("publication_authorized"):
            raise ValueError(f"automatic approval/publication forbidden: {w['id']}")
    dali = [w for w in works if "dali_temptation" in w["id"]]
    if len(dali) != 1 or dali[0].get("preflight_status") != "rights_blocked_no_render_no_distribution":
        raise ValueError("Dalí copyright block is missing")
    return data


def check_evidence(work: dict, ev: dict) -> list[str]:
    problems = []
    if work["preflight_status"] == "rights_blocked_no_render_no_distribution":
        return ["copyright_blocked_no_explicit_license"]

    rights = ev.get("rights", {})
    for key in ("image_reproduction_allowed_for_video",
                "commercial_reuse_allowed", "derivative_reuse_allowed",
                "music_recording_license_verified"):
        if rights.get(key) is not True:
            problems.append("rights." + key + "_not_verified")
    for key in ("image_license_url", "music_license_url"):
        if not rights.get(key):
            problems.append("rights." + key + "_missing")

    assets = ev.get("assets", {})
    for name in ("artwork", "music", "museum_room", "museum_frame", "critico_voice"):
        path, expected = assets.get(name + "_path"), assets.get(name + "_sha256")
        if not path or not expected:
            problems.append("assets." + name + "_path_or_sha_missing")
            continue
        if not Path(path).is_file():
            problems.append("assets." + name + "_file_missing")
        elif sha256_file(path) != expected:
            problems.append("assets." + name + "_sha_mismatch")

    museum = ev.get("museum", {})
    if museum.get("approved_preset") is not True:
        problems.append("museum.approved_preset_missing")
    if museum.get("visual_preview_review_passed") is not True:
        problems.append("museum.visual_preview_review_missing")
    if museum.get("exact_frame_documented_or_owner_exception") is not True:
        problems.append("museum.frame_evidence_missing")
    dimensions = museum.get("painting_cm", {})
    if (dimensions.get("height") != work["painting_cm"]["height"] or
            dimensions.get("width") != work["painting_cm"]["width"]):
        problems.append("museum.real_world_scale_mismatch")

    voice = ev.get("voice", {})
    if voice.get("single_cached_wav_for_both_critico") is not True:
        problems.append("voice.single_shared_recording_missing")
    if voice.get("billing_free_verified") is not True:
        problems.append("voice.free_billing_not_verified")

    if work.get("preexisting_cinema_candidate") and not ev.get("dedup", {}).get(
        "preserve_legacy_master_and_do_not_count_as_new", False
    ):
        problems.append("dedup.legacy_cinema_master_must_be_preserved")
    if ev.get("paid_api_calls") or ev.get("social_autopublish") or ev.get("gold_auto_approval"):
        problems.append("forbidden_spend_publication_or_auto_gold")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("validate", "render-check"))
    parser.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
    parser.add_argument("--id", help="selected artwork id for render-check")
    parser.add_argument("--evidence", type=Path, help="JSON containing actual file/license/room/voice evidence")
    args = parser.parse_args()
    try:
        data = load_queue(args.queue)
        if args.action == "validate":
            print(json.dumps({"status": "VALID", "works": len(data["works"]),
                              "legacy_cinema_candidates": data["existing_cinema_candidates_count"],
                              "new_4x1_produced": 0,
                              "copyright_blocked": [w["id"] for w in data["works"]
                                                    if w["preflight_status"].startswith("rights_blocked")]}))
            return 0
        if not args.id or not args.evidence:
            parser.error("render-check requires --id and --evidence")
        work = next((w for w in data["works"] if w["id"] == args.id), None)
        if work is None:
            raise ValueError("artwork not in owner-selected ten")
        ev = json.loads(args.evidence.read_text(encoding="utf-8"))
        problems = check_evidence(work, ev)
        print(json.dumps({"artwork_id": args.id, "render_authorized": not problems,
                          "blockers": problems}, ensure_ascii=False))
        return 0 if not problems else 2
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"status": "BLOCKED", "reason": str(error)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
