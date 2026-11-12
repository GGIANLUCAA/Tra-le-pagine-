#!/usr/bin/env python3
"""Read-only handoff from existing archival research cycles to their owners.

Turns ONLY existing V4/V101 JSON reports into a small, truthful checkpoint.
It does not schedule, start, retry, render, approve, charge or publish anything.
Missing/malformed evidence stays UNKNOWN; a research PASS is never an MP4.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
try:
    from .studio_quality_memory_v1 import load as load_quality_memory, project_summary
except ImportError:
    from studio_quality_memory_v1 import load as load_quality_memory, project_summary

SCHEMA = "studio-cycle-handoff-v1"
ID = re.compile(r"^[A-Za-z0-9_:-]{3,120}$")
CODE = re.compile(r"^[A-Z0-9_]{2,90}$")
GITHUB_RUN = re.compile(r"^[0-9]{1,20}$")
RESEARCH_STATES = {
    "RESEARCH_CANDIDATES_PENDING_REVIEW",
    "NO_MATCH",
    "API_FAILED_NO_RETRY",
    "PLANNED_NOT_QUERIED",
}
STORIA_CONTRACT = "LA_STORIA_RIVIVE_V101_SAFE_AUTOPILOT"


def load(path: Path | None) -> dict | None:
    """Absent evidence is not a successful result."""
    if path is None or not path.is_file():
        return None
    try:
        content = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError, UnicodeError):
        return None
    return content if isinstance(content, dict) else None


def safe_id(value: object) -> str | None:
    return value if isinstance(value, str) and ID.fullmatch(value) else None


def safe_code(value: object) -> str:
    return value if isinstance(value, str) and CODE.fullmatch(value) else "UNKNOWN"


def research_summary(data: dict | None, project: str) -> dict:
    result = {"state": "MISSING_OR_INVALID", "candidate_count": 0,
              "rights_verified": False, "item_id": None, "cycle_id": None,
              "cycle_utc": None}
    if not isinstance(data, dict) or data.get("schema") != "source-cycle-companion-v4":
        return result
    if data.get("project") != project:
        return result
    if data.get("owner") != ({"artvision": "ARTVISION_OWNER_SELECTED_TEN_V128",
                                 "storia": "STORIA_RIVIVE_V101_SOURCE_ORDER"}[project]):
        return result
    if (data.get("auto_render") is not False
            or data.get("auto_publish") is not False
            or data.get("auto_download") is not False
            or data.get("paid_api_calls") != 0
            or data.get("approved_assets") != 0
            or data.get("rights_checked") is not False):
        return result
    state = data.get("status")
    candidates = data.get("candidates")
    item = safe_id(data.get("item_id"))
    cycle = safe_id(data.get("cycle_id"))
    cycle_utc = data.get("cycle_utc")
    if state not in RESEARCH_STATES or not isinstance(candidates, list) or len(candidates) > 1:
        return result
    if (not item or not cycle or not isinstance(cycle_utc, str)
            or not 10 <= len(cycle_utc) <= 40):
        return result
    for candidate in candidates:
        if (not isinstance(candidate, dict)
                or candidate.get("rights_review") != "pending"
                or candidate.get("approved") is not False
                or candidate.get("review_required") is not True):
            return result
    if state == "RESEARCH_CANDIDATES_PENDING_REVIEW" and len(candidates) != 1:
        return result
    if state != "RESEARCH_CANDIDATES_PENDING_REVIEW" and candidates:
        return result
    return {"state": state, "candidate_count": len(candidates),
            "rights_verified": False, "item_id": item, "cycle_id": cycle,
            "cycle_utc": cycle_utc}


def handoff(project: str, research: dict | None,
            order: dict | None = None, cycle: dict | None = None,
            run_id: str | None = None) -> dict:
    if project not in ("artvision", "storia"):
        raise ValueError("Only existing ArtVision and La Storia research owners are supported")
    source = research_summary(research, project)
    proof = {"research_report": source["state"] != "MISSING_OR_INVALID",
             "work_order": False, "cycle_status": False}
    state = "EVIDENCE_INCOMPLETE"
    action = "inspect_existing_workflow_and_reports"
    item_id = source["item_id"]
    cycle_id = source["cycle_id"]
    blockers = []

    if project == "storia":
        if isinstance(order, dict) and order.get("contract") == STORIA_CONTRACT:
            order_id = safe_id(order.get("episode_id"))
            order_cycle = safe_id(order.get("cycle_id"))
            if (order_id and order_cycle
                    and order.get("video_completed") is False
                    and order.get("publish_permitted") is False
                    and order.get("paid_api_call_permitted") is False):
                proof["work_order"] = True
                item_id = order_id
                cycle_id = order_cycle
                blockers = [
                    safe_code(b) for b in (order.get("blocking_issues") or [])[:25]
                ] if isinstance(order.get("blocking_issues"), list) else ["UNKNOWN"]
        if (isinstance(cycle, dict) and proof["work_order"]
                and cycle.get("cycle_id") == cycle_id
                and cycle.get("candidate") == item_id
                and cycle.get("finished_mp4") is False
                and cycle.get("published") is False
                and cycle.get("charged_api_requests") == 0
                and cycle.get("status") == "RESEARCH_PREPARATION_ONLY"):
            proof["cycle_status"] = True

        if (proof["research_report"] and proof["work_order"]
                and source["item_id"] == item_id
                and source["cycle_utc"] == order.get("cycle_utc")
                and cycle.get("source_research_v4_status") == source["state"]
                and proof["cycle_status"]):
            if source["state"] == "RESEARCH_CANDIDATES_PENDING_REVIEW":
                state, action = ("SOURCE_CANDIDATE_NEEDS_REVIEW",
                                 "verify_file_rights_and_native_frames")
            elif source["state"] == "NO_MATCH":
                state, action = "NO_SOURCE_MATCH", "try_next_independent_source"
            else:
                state, action = "RESEARCH_NOT_READY", "inspect_source_research_result"
        elif proof["work_order"] and proof["cycle_status"]:
            # The companion source lookup is noncritical; keep a truthful
            # work-order checkpoint when the optional lookup fails.
            state, action = "PREPARATION_ONLY_NO_VERIFIED_RESEARCH", "inspect_optional_research"
    else:
        if proof["research_report"]:
            if source["state"] == "RESEARCH_CANDIDATES_PENDING_REVIEW":
                state, action = ("SOURCE_CANDIDATE_NEEDS_REVIEW",
                                 "verify_museum_image_frame_rights_and_dimensions")
            elif source["state"] == "NO_MATCH":
                state, action = "NO_SOURCE_MATCH", "try_next_independent_source"
            else:
                state, action = "RESEARCH_NOT_READY", "inspect_source_research_result"

    url = ("https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/" + run_id
           if isinstance(run_id, str) and GITHUB_RUN.fullmatch(run_id) else None)
    return {
        "schema": SCHEMA, "project": project, "scope": "research_handoff_only",
        "state": state, "next_action": action,
        "item_id": item_id, "cycle_id": cycle_id,
        "source_research_state": source["state"],
        "candidate_count": source["candidate_count"],
        "reported_blocker_codes": [x for x in blockers if x != "UNKNOWN"],
        "evidence": proof, "run_url": url,
        # Only a checklist inherited by the owner, never a completed edit or render.
        "quality_memory": project_summary(load_quality_memory(), project),
        "source_rights_verified_by_handoff": False,
        "master_mp4_verified_by_handoff": False,
        "zip_verified_by_handoff": False,
        "new_finished_mp4": 0,
        "owner_artistic_approved": False, "auto_publish_authorized": False,
        "paid_api_calls_authorized": False, "automatic_retry_started": False,
        "auto_render_started": False,
        "disclaimer": ("Research and preflight are not final media. "
                       "Consult the independent owner workflow and full video QA."),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, choices=["artvision", "storia"])
    parser.add_argument("--research", type=Path, required=True)
    parser.add_argument("--work-order", type=Path)
    parser.add_argument("--cycle-status", type=Path)
    parser.add_argument("--run-id")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    report = handoff(args.project, load(args.research),
                     load(args.work_order), load(args.cycle_status),
                     args.run_id)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    print(json.dumps({"status": report["state"], "next": report["next_action"],
                      "new_mp4": 0, "item": report["item_id"]},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
