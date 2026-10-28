#!/usr/bin/env python3
"""ArtVision offline learning ledger: evidence-led critique, no auto-approval.

This tool DOES NOT watch movies, evaluate emotions, publish, render or pay APIs.
It records a review that an actual reviewer conducted on an exact local MP4,
and suggests one experimental improvement without overwriting master presets.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

SCHEMA = "artvision-self-critique-v1"
VARIANTS = ("critico_standard", "critico_museum", "cinema_standard", "cinema_museum")
SEVERITIES = ("minor", "major", "blocking")


def sha256_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def clean_text(value, min_length=10):
    return isinstance(value, str) and len(value.strip()) >= min_length


def validate_review(review, real_video=None):
    errors = []
    if not isinstance(review, dict):
        return ["Review JSON non valido"]
    if review.get("schema") != SCHEMA:
        errors.append("Schema di autocritica errato")
    if review.get("variant") not in VARIANTS:
        errors.append("Variante non riconosciuta")
    if not clean_text(review.get("painting_id"), 3):
        errors.append("painting_id richiesto")
    digest = review.get("video_sha256")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        errors.append("SHA256 esatto del video richiesto")
    if real_video is None:
        errors.append("Passare --video per provare l'esistenza del filmato analizzato")
    else:
        video = Path(real_video)
        if not video.is_file() or video.stat().st_size == 0:
            errors.append("MP4 originale inesistente o vuoto")
        elif isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest):
            if sha256_file(video) != digest:
                errors.append("Il file MP4 non coincide con l'hash della recensione")
    inspection = review.get("inspection")
    if not isinstance(inspection, dict):
        inspection = {}
    if inspection.get("watched_full_video") is not True:
        errors.append("Autocritica fattuale: bisogna aver visto davvero l'intero MP4")
    if inspection.get("listened_audio") is not True:
        errors.append("Autocritica fattuale: ascoltare davvero l'audio")
    if inspection.get("reviewer") not in ("agent", "human"):
        errors.append("Indicare se il revisore è agente o umano")
    findings = review.get("findings")
    if not isinstance(findings, list):
        findings = []
    if not 2 <= len(findings) <= 3:
        errors.append("Annotare 2-3 difetti osservati, senza riempitivi")
    for i, finding in enumerate(findings, 1):
        if not isinstance(finding, dict):
            errors.append(f"Difetto {i}: struttura non valida")
            continue
        if finding.get("severity") not in SEVERITIES:
            errors.append(f"Difetto {i}: severità non valida")
        for field in ("problem", "specific_evidence", "likely_cause",
                      "next_change", "verification"):
            if not clean_text(finding.get(field), 15):
                errors.append(f"Difetto {i}: {field} troppo generico")
        seconds = finding.get("at_second")
        if (isinstance(seconds, bool) or not isinstance(seconds, (int, float))
                or seconds < 0 or seconds != seconds):
            errors.append(f"Difetto {i}: secondi del problema richiesti")
    experiment = review.get("next_experiment")
    if not isinstance(experiment, dict):
        experiment = {}
    for field in ("one_variable", "hypothesis", "verification"):
        if not clean_text(experiment.get(field), 15):
            errors.append(f"Esperimento futuro: {field} mancante")
    if review.get("claims_gold_master") is True:
        errors.append("Un'analisi autonoma non può approvare Gold Master")
    if review.get("user_approved") is True and inspection.get("reviewer") != "human":
        errors.append("Un agente non può inventare approvazione umana")
    return errors


def record(review, video, ledger):
    errors = validate_review(review, video)
    if errors:
        return {"saved": False, "blockers": errors}
    ledger = Path(ledger)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    if ledger.is_file():
        rows = [json.loads(s) for s in ledger.read_text(encoding="utf-8").splitlines() if s.strip()]
    token = (review["video_sha256"], review["variant"])
    if any((row.get("video_sha256"), row.get("variant")) == token for row in rows):
        return {"saved": False, "blockers": ["Recensione identica già registrata per questo MP4"]}
    # Record observations, not approval or objective emotion scores.
    evidence = dict(review)
    evidence["review_status"] = "observed_by_" + review["inspection"]["reviewer"]
    evidence["auto_approved"] = False
    rows.append(evidence)
    tmp = ledger.with_name(ledger.name + ".tmp")
    tmp.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n"
                           for row in rows), encoding="utf-8")
    tmp.replace(ledger)
    return {"saved": True, "records": len(rows), "auto_approved": False}


def next_lesson(ledger):
    ledger = Path(ledger)
    if not ledger.is_file():
        return {"status": "no_verified_reviews", "suggestion": None}
    rows = [json.loads(s) for s in ledger.read_text(encoding="utf-8").splitlines() if s.strip()]
    candidates = []
    counts = Counter()
    for review in rows:
        if review.get("review_status") not in ("observed_by_agent", "observed_by_human"):
            continue
        for item in review.get("findings", []):
            key = str(item.get("likely_cause", "")).strip().lower()
            if key:
                counts[key] += 1
            candidates.append((item, review))
    if not candidates:
        return {"status": "no_verified_reviews", "suggestion": None}
    # Repeated problems and severe issues first. Only one change per next cycle.
    rank = {"minor": 1, "major": 2, "blocking": 3}
    item, review = max(candidates, key=lambda x: (
        rank.get(x[0].get("severity"), 0),
        counts[str(x[0].get("likely_cause", "")).strip().lower()]))
    return {
        "status": "proposed_not_proven",
        "based_on_video_sha256": review["video_sha256"],
        "variant": review["variant"],
        "observed_problem": item.get("problem"),
        "suggested_single_change": item.get("next_change"),
        "how_to_verify": item.get("verification"),
        "note": "Confrontare prima/dopo e ottenere feedback; non cambiare i preset approvati automaticamente.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    cmds = parser.add_subparsers(dest="command", required=True)
    rec = cmds.add_parser("record")
    rec.add_argument("--review", type=Path, required=True)
    rec.add_argument("--video", type=Path, required=True)
    rec.add_argument("--ledger", type=Path, required=True)
    lesson = cmds.add_parser("next")
    lesson.add_argument("--ledger", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "record":
        result = record(json.loads(args.review.read_text(encoding="utf-8")),
                        args.video, args.ledger)
    else:
        result = next_lesson(args.ledger)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.command == "record" and not result["saved"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
