#!/usr/bin/env python3
"""Read-only bridge from Quality Director V17 reports to Studio status artifacts.

No raw logs, tokens, video frames or private comments leave this module. It does
not attest a video has been watched: a QA report alone never grants approval.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from studio_autonomy_gate_v1 import safe_run_url

SCHEMA = "studio-autonomy-qa-bridge-v1"
CODES = re.compile(r"^[A-Z][A-Z0-9_]{1,70}$")


def issue_codes(items: object) -> list[str]:
    if not isinstance(items, list):
        return ["INVALID_REPORT_ISSUES"]
    codes = []
    for item in items[:30]:
        candidate = item.get("code") if isinstance(item, dict) else None
        if isinstance(candidate, str) and CODES.fullmatch(candidate) and candidate not in codes:
            codes.append(candidate)
    return codes


def summarize(report: dict, run_url: str | None = None) -> dict:
    if not isinstance(report, dict) or report.get("schema") != "quality-director-v17":
        raise ValueError("QUALITY_REPORT_V17.json required")
    qa_status = report.get("status")
    if qa_status not in ("needs_artistic_review", "needs_review_with_warnings",
                         "technical_blocked"):
        raise ValueError("Unknown Quality Director V17 status")
    blockers = issue_codes(report.get("blocking"))
    warnings = issue_codes(report.get("warnings"))
    if blockers == ["INVALID_REPORT_ISSUES"] or warnings == ["INVALID_REPORT_ISSUES"]:
        raise ValueError("Invalid QA issue list")
    # The report's video field is only a reference. Its existence, SHA and
    # decodability must be established outside this bridge before release.
    video_declared = isinstance(report.get("video"), str) and bool(report["video"].strip())
    if blockers or qa_status == "technical_blocked":
        state, action = "technical_blocked", "inspect_and_repair_video"
    elif not video_declared:
        state, action = "needs_real_mp4_evidence", "run_quality_review_on_actual_mp4"
    else:
        state, action = "pending_artistic_review", "inspect_actual_mp4_and_owner_approve"
    normalized_url = safe_run_url(run_url)
    output = {
        "schema": SCHEMA,
        "kind": "qa_report_only",
        "state": state,
        "next_action": action,
        "quality_director_status": qa_status,
        "blocker_codes": blockers,
        "warning_codes": warnings,
        "video_reference_present": video_declared,
        "mp4_bytes_verified_by_bridge": False,
        "video_sha256_verified_by_bridge": False,
        "archive_reachable_verified_by_bridge": False,
        "owner_approved": False,
        "publish_authorized": False,
        "auto_patch_authorized": False,
        "paid_calls_authorized": False,
        "run_url": normalized_url,
        "policy_note": "Requires independent MP4/SHA/rights checks, format-specific gates and owner review.",
    }
    output["repair_gpt_prompt"] = diagnosis(output)
    return output


def diagnosis(status: dict) -> str:
    # Not even raw QA messages or external URLs: public CI artifact is safe.
    parts = [
        "Controlla PR, job e log REALI in GGIANLUCAA/Tra-le-pagine-.",
        "Leggi AGENTS.md, START_HERE_GPT.md e docs/REGOLE_ATTIVE.md.",
        "Rispetta i gate V55, V80/V118, V91/V94/V96/V99 secondo il formato.",
        "Niente nuovi crediti API, render, merge, approvazioni o pubblicazioni implicite.",
        "Stato QA: " + status["state"],
        "Bloccanti: " + (", ".join(status["blocker_codes"]) or "nessuno dichiarato"),
        "Avvisi: " + (", ".join(status["warning_codes"]) or "nessuno dichiarato"),
        "Esecuzione GitHub: " + (status["run_url"] or "non disponibile"),
        "Verifica eventuali MP4 e SHA reali prima di dichiarare il lavoro finito.",
        "Proponi correzioni isolate e test prima di toccare la produzione.",
    ]
    return "\n".join(parts) + "\n"


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--quality-report", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--run-url")
    args = p.parse_args()
    report = json.loads(args.quality_report.read_text(encoding="utf-8"))
    status = summarize(report, args.run_url)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out/"STUDIO_AUTONOMY_STATUS_V1.json").write_text(
        json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (args.out/"RIPARA_CON_GPT.txt").write_text(
        status["repair_gpt_prompt"], encoding="utf-8"
    )
    print(json.dumps({"state": status["state"], "next": status["next_action"]},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
