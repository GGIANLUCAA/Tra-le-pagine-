#!/usr/bin/env python3
"""V44: fail-closed release gate for a newly animated scene in an existing video.

This tool does not render video or spend credits. Structural checks NEVER
certify visual beauty or that a human really watched the result.
Never automatically pre-populate reviews with passing values.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

SCHEMA = "animated-video-release-v44"
CHECKS = (
    "full_watch_and_listen",
    "requested_action_actually_visible",
    "narration_matches_action_timing",
    "faces_hands_and_objects_stable",
    "no_warped_gears_or_artifacts",
    "transitions_and_audio_continuous",
    "visual_improvement_over_original",
)
REJECTED_WORDS = ("auto", "placeholder", "not checked", "to verify", "n/a", "pass", "ok")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for buf in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(buf)
    return h.hexdigest()


def draft(original: Path, candidate: Path, inserted_clip: Path,
          medium: str, spoken_line: str, action: str) -> dict:
    for p in (original, candidate, inserted_clip):
        if not p.is_file() or p.stat().st_size < 100:
            raise ValueError("File sorgente/candidato/clip assente o vuoto: " + str(p))
    if medium not in ("generative_i2v", "local_motion"):
        raise ValueError("Medium sconosciuto")
    if len(spoken_line.strip()) < 8 or len(action.strip()) < 15:
        raise ValueError("Fase narrativa e azione richieste")
    return {
        "schema": SCHEMA,
        "status": "rendered_needs_review",
        "medium_requested": medium,
        "original": {"path": str(original), "sha256": sha256(original)},
        "candidate": {"path": str(candidate), "sha256": sha256(candidate)},
        "inserted_clip": {"path": str(inserted_clip), "sha256": sha256(inserted_clip)},
        "provenance": {
            "kind": "unverified",
            "provider": "",
            "task_id": "",
            "source_image_sha256": "",
            "approval_fingerprint": "",
            "billed_credits_verified": False,
        },
        "scene": {"spoken_line": spoken_line, "requested_action": action,
                  "time_start_seconds": None, "time_end_seconds": None},
        "reviews": {key: {"passed": False, "evidence": ""}
                    for key in CHECKS},
        "reviewer": {
            "kind": "pending", "name": "", "decision": "pending",
            "reason": "", "reviewed_video_sha256": "",
        },
    }


def _substantial(text: object, minimum: int = 30) -> bool:
    if not isinstance(text, str) or len(text.strip()) < minimum:
        return False
    low = text.strip().lower()
    return not any(low == bad or low.startswith(bad + " ") for bad in REJECTED_WORDS)


def check(d: dict, original: Path, candidate: Path, inserted_clip: Path,
          required_medium: str = "generative_i2v") -> list[str]:
    problems = []
    if d.get("schema") != SCHEMA:
        problems.append("Manifest V44 mancante.")
    if d.get("status") != "approved_for_final_delivery":
        problems.append("Il video non e approvato: non chiamarlo FINALE o pronto per la pubblicazione.")
    if d.get("medium_requested") != required_medium:
        problems.append("Tipo di animazione diverso dalla richiesta dell'utente.")

    for name, path in (("original", original), ("candidate", candidate),
                       ("inserted_clip", inserted_clip)):
        record = d.get(name) or {}
        if not path.is_file() or path.stat().st_size < 100:
            problems.append(name + ": file inesistente o vuoto.")
            continue
        if sha256(path) != record.get("sha256"):
            problems.append(name + ": SHA-256 diverso dalla revisione.")
    if original.exists() and candidate.exists() and sha256(original) == sha256(candidate):
        problems.append("Filmato invariato rispetto al master: nessuna miglioria dimostrata.")

    scene = d.get("scene") or {}
    if not _substantial(scene.get("requested_action"), 15):
        problems.append("L'azione visiva deve essere descritta specificamente.")
    if not isinstance(scene.get("spoken_line"), str) or len(scene["spoken_line"].strip()) < 8:
        problems.append("Manca la frase narrata associata.")
    a = scene.get("time_start_seconds")
    b = scene.get("time_end_seconds")
    if (type(a) not in (int, float) or type(b) not in (int, float)
            or not 0 <= a < b):
        problems.append("Mancano i secondi reali della scena da revisionare.")

    provenance = d.get("provenance") or {}
    if required_medium == "generative_i2v":
        if provenance.get("kind") != "provider_i2v":
            problems.append("BLOCCATO: effetto locale/crop/warp NON e generazione I2V reale.")
        for key in ("provider", "task_id", "source_image_sha256", "approval_fingerprint"):
            if not isinstance(provenance.get(key), str) or not provenance[key].strip():
                problems.append("Provenienza generativa non verificata: " + key)
        # A recorded spend is not proof of a real charge. Manual balance audit is separate.
    else:
        if provenance.get("kind") != "local_motion":
            problems.append("Provenienza locale non dichiarata.")

    reviews = d.get("reviews") or {}
    for key in CHECKS:
        review = reviews.get(key) or {}
        if review.get("passed") is not True or not _substantial(review.get("evidence")):
            problems.append("Revisione artistica mancante/fallita: " + key)

    reviewer = d.get("reviewer") or {}
    if reviewer.get("kind") not in ("user", "human_editor"):
        problems.append("Serve revisore reale, non autoapprovazione dello script.")
    if reviewer.get("decision") != "approved":
        problems.append("Il revisore non ha approvato il risultato.")
    if not _substantial(reviewer.get("reason"), 35):
        problems.append("Motivazione artistica del revisore mancante.")
    if reviewer.get("reviewed_video_sha256") != (d.get("candidate") or {}).get("sha256"):
        problems.append("La revisione non e legata allo SHA del video esatto.")
    return problems


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("action", choices=("draft", "check"))
    p.add_argument("--original", type=Path, required=True)
    p.add_argument("--candidate", type=Path, required=True)
    p.add_argument("--clip", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--medium", choices=("generative_i2v", "local_motion"),
                   default="generative_i2v")
    p.add_argument("--spoken-line", default="")
    p.add_argument("--requested-action", default="")
    a = p.parse_args()

    if a.action == "draft":
        if a.manifest.exists():
            raise SystemExit("Non sovrascrivere una revisione esistente.")
        info = draft(a.original, a.candidate, a.clip,
                     a.medium, a.spoken_line, a.requested_action)
        a.manifest.parent.mkdir(parents=True, exist_ok=True)
        a.manifest.write_text(json.dumps(info, ensure_ascii=False, indent=2) + "\n",
                              encoding="utf8")
        print(json.dumps({"status": "rendered_needs_review",
                          "approved": False, "manifest": str(a.manifest)}))
    else:
        d = json.loads(a.manifest.read_text(encoding="utf8"))
        problems = check(d, a.original, a.candidate, a.clip, a.medium)
        print(json.dumps({"approved": not bool(problems),
                          "problems": problems}, ensure_ascii=False, indent=2))
        if problems:
            sys.exit(3)


if __name__ == "__main__":
    main()
