#!/usr/bin/env python3
"""Read-only safety gate for Video Library Studio autonomy.

The gate consumes evidence supplied by existing runners; it never renders, retries,
commits, approves, publishes, spends credits or accesses APIs. Its output is a
recommendation/checkpoint, not proof of a completed or approved master.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlparse

SCHEMA = "studio-autonomy-checkpoint-v1"
SHA = re.compile(r"^[a-f0-9]{64}$")
JOB_ID = re.compile(r"^[a-zA-Z0-9_.:-]{3,100}$")
RETRYABLE = frozenset(("network_timeout", "github_503", "upstream_503", "rate_limit_429"))
VOICE_FORMATS = frozenset(("libri", "libri_narrati", "racconti", "fiabe", "critico"))
QUALITY_PASS = frozenset(("needs_artistic_review", "needs_review_with_warnings"))
QUALITY_BLOCK = frozenset(("technical_blocked",))


def safe_run_url(value: object) -> str | None:
    """Only GitHub Actions run URLs in the known repository; never trust log URLs."""
    if not isinstance(value, str) or len(value) > 250:
        return None
    parsed = urlparse(value)
    if (parsed.scheme != "https" or parsed.netloc != "github.com"
            or parsed.query or parsed.fragment):
        return None
    if not re.fullmatch(
        r"/GGIANLUCAA/Tra-le-pagine-/actions/runs/[0-9]+", parsed.path
    ):
        return None
    return value


def sha_ok(value: object) -> bool:
    return isinstance(value, str) and SHA.fullmatch(value) is not None


def result(job: dict, status: str, action: str, reasons: list[str],
           *, can_auto_continue: bool = False) -> dict:
    # Never advertise an automated patch, publication or human approval.
    response = {
        "schema": "studio-autonomy-decision-v1",
        "job_id": job["job_id"],
        "format": job["format"],
        "status": status,
        "suggested_action": action,
        "reasons": reasons,
        "can_auto_continue": can_auto_continue,
        "human_artistic_approval_granted_by_gate": False,
        "can_publish": False,
        "paid_calls_authorized_by_gate": False,
        "video_created_by_gate": False,
        "run_url": safe_run_url(job.get("run_url")),
        "basis": "untrusted supplied evidence; independently verify MP4, rights and owner review",
    }
    return response


def evaluate(job: dict) -> dict:
    """Choose exactly one safe next action from a format-aware checkpoint."""
    if not isinstance(job, dict):
        raise ValueError("Checkpoint must be a JSON object")
    if job.get("schema") != SCHEMA:
        raise ValueError("Unexpected checkpoint schema")
    if not isinstance(job.get("job_id"), str) or not JOB_ID.fullmatch(job["job_id"]):
        raise ValueError("Missing or unsafe job ID")
    if not isinstance(job.get("format"), str) or not 1 <= len(job["format"]) <= 60:
        raise ValueError("Missing format")
    stage = job.get("stage")
    if stage not in ("preflight", "rendered", "failed"):
        raise ValueError("Unknown stage")
    if job.get("completed_same_input") is True:
        return result(job, "duplicate", "skip_same_input", ["ALREADY_PROCESSED"])

    # A general instruction to be autonomous does not grant release or budget.
    if job.get("publish_requested") is True:
        return result(job, "owner_action_required", "request_publication_approval",
                      ["PUBLICATION_REQUIRES_EXPLICIT_OWNER_PERMISSION"])
    if job.get("paid_request_pending") is True:
        return result(job, "owner_action_required", "review_specific_cost_and_ledger",
                      ["NO_NEW_PAID_API_CALLS_FROM_CHECKPOINT"])

    if stage == "failed":
        error = job.get("error") if isinstance(job.get("error"), dict) else {}
        code = error.get("code")
        attempts = job.get("attempts", 0)
        if type(attempts) is not int or attempts < 0:
            raise ValueError("Invalid retry count")
        # Never reissue a possibly charged generation call; no double credits.
        if (code in RETRYABLE and attempts < 2
                and job.get("charge_uncertain") is False
                and job.get("failure_is_readonly") is True):
            return result(job, "safe_retry_candidate", "retry_existing_readonly_check",
                          ["TRANSIENT_READONLY_FAILURE", str(code)], can_auto_continue=True)
        return result(job, "repair_review_required", "prepare_gpt_diagnostic",
                      ["NO_UNATTENDED_PATCH", str(code or "UNKNOWN_FAILURE")])

    if (job.get("source_rights_verified") is not True
            or job.get("source_hash_verified") is not True):
        return result(job, "blocked", "collect_source_and_rights_evidence",
                      ["SOURCE_OR_RIGHTS_NOT_PROVEN"])

    if stage == "preflight":
        return result(job, "prepared_for_owner_pipeline", "continue_existing_owner_pipeline",
                      ["PREFLIGHT_ONLY_NOT_A_RENDER"], can_auto_continue=True)

    # No guessed formats: a nonstandard format must receive the owner-specific QA.
    format_name = job["format"]
    variant = job.get("variant", "")
    requires_voice = format_name in VOICE_FORMATS or (
        format_name == "artvision_4x1" and variant in
        ("critico_standard", "critico_museum"))
    if requires_voice and job.get("narration_verified") is not True:
        return result(job, "blocked", "repair_narration",
                      ["MANDATORY_NARRATION_NOT_VERIFIED"])
    if job.get("music_rights_verified") is not True:
        return result(job, "blocked", "verify_audio_rights",
                      ["AUDIO_RIGHTS_NOT_PROVEN"])

    media = job.get("delivery") if isinstance(job.get("delivery"), dict) else {}
    required = ("mp4_sha256", "zip_sha256")
    if not all(sha_ok(media.get(k)) for k in required):
        return result(job, "blocked", "verify_real_mp4_and_zip",
                      ["DELIVERY_HASHES_NOT_VERIFIED"])
    if (type(media.get("mp4_bytes")) is not int or media["mp4_bytes"] < 100000
            or type(media.get("zip_bytes")) is not int or media["zip_bytes"] < 100000
            or media.get("cover_verified") is not True
            or media.get("social_drafts_verified") is not True):
        return result(job, "blocked", "complete_delivery_package",
                      ["DELIVERY_PACKAGE_INCOMPLETE"])

    qa = job.get("technical_qa")
    if not isinstance(qa, dict) or qa.get("schema") != "quality-director-v17":
        return result(job, "blocked", "run_real_video_qa",
                      ["V17_QA_REPORT_REQUIRED"])
    if qa.get("status") in QUALITY_BLOCK or qa.get("blocking"):
        return result(job, "blocked", "repair_technical_qa",
                      ["TECHNICAL_QA_BLOCKED"])
    if qa.get("status") not in QUALITY_PASS:
        return result(job, "blocked", "inspect_qa_status",
                      ["QA_NOT_A_VERIFIED_PASS"])

    # Artistic review must be linked to this exact MP4. It cannot be inferred
    # from successful FFmpeg, completed GitHub Actions or a passed QA report.
    review = job.get("owner_review") if isinstance(job.get("owner_review"), dict) else {}
    if (review.get("decision") != "approved"
            or review.get("reviewer") != "owner"
            or review.get("mp4_sha256") != media["mp4_sha256"]):
        return result(job, "owner_review_required", "send_video_to_owner_review",
                      ["TECHNICAL_PASS_IS_NOT_ARTISTIC_APPROVAL"])

    return result(job, "approved_record_needs_release_check",
                  "prepare_manual_release_review",
                  ["OWNER_REVIEW_RECORDED_NOT_PUBLICATION_PERMISSION"])


def diagnostic(decision: dict, job: dict) -> str:
    """Brief sanitised packet for 'Ripara con GPT', never raw logs or secrets."""
    code = "unknown"
    if isinstance(job.get("error"), dict):
        raw = job["error"].get("code")
        if isinstance(raw, str) and re.fullmatch(r"[a-zA-Z0-9_-]{1,50}", raw):
            code = raw
    lines = [
        "Controlla lo stato attuale del repository GGIANLUCAA/Tra-le-pagine-.",
        "Leggi prima AGENTS.md, START_HERE_GPT.md e docs/REGOLE_ATTIVE.md.",
        "Non modificare master approvati, non spendere crediti, non pubblicare.",
        "Job: " + decision["job_id"],
        "Formato: " + decision["format"],
        "Stato: " + decision["status"],
        "Codice errore: " + code,
        "GitHub run: " + (decision["run_url"] or "non verificato"),
        "Verifica job/log reali prima di proporre o applicare una correzione sicura.",
        "Non considerare MP4/ZIP tecnicamente validi come approvazione artistica.",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    job = json.loads(args.checkpoint.read_text(encoding="utf-8"))
    decision = evaluate(job)
    decision["repair_gpt_prompt"] = diagnostic(decision, job)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(decision, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    print(json.dumps({"status": decision["status"],
                      "next": decision["suggested_action"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
