#!/usr/bin/env python3
"""Video Library Studio: continuità V1 (solo lettura / fail-closed).

Genera prossime azioni e un dossier per 'Ripara GPT' da uno snapshot esplicito.
Non avvia workflow, non modifica code, non approva video, non usa API a pagamento,
non esegue codice ricavato da log e non pubblica alcun contenuto.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "studio-continuity-snapshot-v1"
TRANSIENT = {"HTTP_429", "NETWORK_TIMEOUT", "HTTP_502", "HTTP_503", "HTTP_504"}
STATES = {"queued", "blocked", "rendered", "review_pending", "approved", "packaged", "delivered"}
SHA256 = re.compile(r"^[a-f0-9]{64}$")
SAFE_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_.:-]{0,95}$")
SAFE_GITHUB_RUN = re.compile(r"^https://github\.com/[\w.-]+/[\w.-]+/actions/runs/[0-9]+$")


def is_true(value):
    return value is True  # stringhe 'true' non costituiscono prove


def validate(snapshot):
    if not isinstance(snapshot, dict) or snapshot.get("schema") != SCHEMA:
        raise ValueError("Schema snapshot non riconosciuto")
    jobs = snapshot.get("jobs")
    if not isinstance(jobs, list) or len(jobs) > 2000:
        raise ValueError("jobs deve essere una lista limitata")
    seen = set()
    for job in jobs:
        if not isinstance(job, dict):
            raise ValueError("Job non valido")
        ident, category = job.get("id"), job.get("category")
        if not isinstance(ident, str) or not SAFE_ID.fullmatch(ident):
            raise ValueError("ID del job non sicuro o assente")
        if not isinstance(category, str) or not SAFE_ID.fullmatch(category):
            raise ValueError("Categoria del job non sicura o assente")
        if (category, ident) in seen:
            raise ValueError("Job duplicato: " + ident)
        seen.add((category, ident))
        if job.get("state") not in STATES:
            raise ValueError("Stato non valido: " + ident)
        priority = job.get("priority", 50)
        if type(priority) is not int or not 0 <= priority <= 100:
            raise ValueError("Priorità non valida: " + ident)
        for field in ("source_verified", "rights_verified", "technical_qa_passed",
                      "artistic_review_passed", "owner_approved", "package_verified",
                      "publication_approved", "paid_operation"):
            if field in job and type(job[field]) is not bool:
                raise ValueError(field + " richiede un booleano esplicito")
        digest = job.get("media_sha256")
        if digest is not None and (not isinstance(digest, str) or not SHA256.fullmatch(digest)):
            raise ValueError("SHA256 malformato: " + ident)
        error = job.get("error")
        if error is not None:
            if not isinstance(error, dict) or not isinstance(error.get("code"), str):
                raise ValueError("Errore non strutturato: " + ident)
            count = error.get("retry_count", 0)
            if type(count) is not int or not 0 <= count <= 50:
                raise ValueError("retry_count non valido")
        link = job.get("github_run_url")
        if link is not None and (not isinstance(link, str) or not SAFE_GITHUB_RUN.fullmatch(link)):
            raise ValueError("Collegamento GitHub non valido")
    return jobs


def classify(job):
    """Propone una sola prossima azione; nessun suggerimento è permesso d'esecuzione."""
    if job["state"] == "blocked":
        return "requires_manual_review", "blocco esplicito"
    error = job.get("error") or {}
    if error.get("active") is True:
        kind = error["code"]
        # Il retry gratuito è SOLO una proposta, non una chiamata automatica.
        # In caso di addebito incerto, bloccare anche i retry normalmente idempotenti.
        safe = (kind in TRANSIENT and error.get("retry_count", 0) < 2
                and error.get("charge_state") == "confirmed_no_charge"
                and not is_true(job.get("paid_operation")))
        return ("retry_candidate_needs_preflight" if safe else "requires_gpt_review",
                "errore attivo: " + kind)
    if not is_true(job.get("source_verified")) or not is_true(job.get("rights_verified")):
        return "source_rights_preflight", "fonti o diritti non verificati"
    if is_true(job.get("paid_operation")):
        return "requires_cost_approval", "operazione a pagamento: consenso specifico richiesto"
    if job["state"] == "queued":
        return "production_candidate_needs_preflight", "candidato; nessun render autorizzato"
    if job["state"] in {"rendered", "review_pending"}:
        if not is_true(job.get("technical_qa_passed")):
            return "technical_qa_required", "verifica sul file MP4 reale richiesta"
        if not is_true(job.get("artistic_review_passed")):
            return "artistic_review_required", "la riuscita tecnica non è un'approvazione"
        if not is_true(job.get("owner_approved")):
            return "owner_approval_required", "serve giudizio esplicito del proprietario"
    if job["state"] in {"approved", "rendered", "review_pending"}:
        if not is_true(job.get("owner_approved")):
            return "owner_approval_required", "l'etichetta di stato non prova il consenso"
        if not is_true(job.get("technical_qa_passed")) or not is_true(job.get("artistic_review_passed")):
            return "quality_gate_required", "gate tecnico e artistico obbligatori"
        if not is_true(job.get("package_verified")):
            return "delivery_verification_required", "verificare MP4, copertina e ZIP reali"
    if job["state"] in {"packaged", "delivered"}:
        if not all(is_true(job.get(k)) for k in ("technical_qa_passed", "artistic_review_passed",
                                                 "owner_approved", "package_verified")):
            return "reconcile_false_delivery", "non dichiarare consegna senza tutte le prove"
        return "archive_check_only", "nessuna pubblicazione automatica"
    return "reconcile_unknown", "riconciliare lo stato prima di procedere"


def build_report(snapshot):
    jobs = validate(snapshot)
    rows = []
    for job in jobs:
        action, reason = classify(job)
        error = job.get("error") or {}
        rows.append({
            "id": job["id"], "category": job["category"], "state": job["state"],
            "priority": job.get("priority", 50), "next_action": action, "reason": reason,
            "github_run_url": job.get("github_run_url"),
            "error_code": error.get("code") if error.get("active") is True else None,
            "media_sha256": job.get("media_sha256"),
            "render_started": False, "new_mp4_produced": False,
            "owner_approved_by_this_report": False, "published_by_this_report": False,
        })
    rows.sort(key=lambda x: (-x["priority"], x["category"], x["id"]))
    queue = [r for r in rows if r["next_action"] == "production_candidate_needs_preflight"]
    repairs = [r for r in rows if r["error_code"]]
    return {
        "schema": "studio-continuity-report-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "next_preflight_candidate": queue[0] if queue else None,
        "jobs_total": len(rows), "errors_active": len(repairs),
        "items": rows,
        "repair_contexts": [{
            "job_id": x["id"], "category": x["category"], "github_run_url": x["github_run_url"],
            "error_code": x["error_code"], "next_action": x["next_action"],
            "instruction": "Verifica log e job GitHub, diagnosi con prove, modifica sicura in PR e test; "
                           "non spendere, non pubblicare, non dichiarare il video approvato."
        } for x in repairs],
        "guarantees": {
            "read_only": True, "new_expenses": False, "social_autopublish": False,
            "automatic_artistic_approval": False, "modifies_existing_masters": False,
            "dispatches_workflows": False
        },
        "note": "Piano di lavoro, NON produzione attiva o video finiti."
    }


def inspect_mp4(path, require_audio=True):
    """Misura solo caratteristiche tecniche REALI; un PASS non prova voce o qualità artistica."""
    media = Path(path)
    if not media.is_file() or media.stat().st_size < 100_000:
        raise ValueError("File video mancante o troppo piccolo per una consegna")
    try:
        response = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "format=duration,size:stream=codec_type,codec_name,width,height",
             "-of", "json", str(media)],
            check=True, capture_output=True, text=True, timeout=35)
        data = json.loads(response.stdout)
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired,
            json.JSONDecodeError) as exc:
        raise ValueError("ffprobe non ha validato il vero MP4") from exc
    streams = data.get("streams") or []
    video = next((s for s in streams if s.get("codec_type") == "video"), {})
    audio = next((s for s in streams if s.get("codec_type") == "audio"), {})
    try:
        duration = float(data.get("format", {}).get("duration", 0))
    except (ValueError, TypeError) as exc:
        raise ValueError("Durata MP4 invalida") from exc
    technical_pass = (
        duration > 0 and video.get("codec_name") == "h264"
        and int(video.get("width") or 0) > 0 and int(video.get("height") or 0) > 0
        and (not require_audio or audio.get("codec_name") == "aac")
    )
    digest = hashlib.sha256()
    with media.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(block)
    return {
        "schema": "studio-video-technical-qa-v1", "file": media.name,
        "bytes": media.stat().st_size, "sha256": digest.hexdigest(),
        "duration_s": round(duration, 3), "width": video.get("width"),
        "height": video.get("height"), "video_codec": video.get("codec_name"),
        "audio_codec": audio.get("codec_name"), "technical_pass": technical_pass,
        "narration_verified": False, "scene_sync_verified": False,
        "artistic_approval": "PENDING", "rights_approval": "PENDING",
        "delivery_approved": False, "publication_approved": False,
        "note": "Serve QA visivo/sonoro sul filmato, diritti e giudizio umano separati."
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("plan")
    p.add_argument("--snapshot", required=True)
    p.add_argument("--out", required=True)
    q = sub.add_parser("qa")
    q.add_argument("--mp4", required=True)
    q.add_argument("--out", required=True)
    q.add_argument("--audio-optional", action="store_true")
    args = parser.parse_args()
    if args.command == "plan":
        result = build_report(json.loads(Path(args.snapshot).read_text(encoding="utf-8")))
    else:
        result = inspect_mp4(args.mp4, require_audio=not args.audio_optional)
    dest = Path(args.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"schema": result["schema"], "out": str(dest)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
