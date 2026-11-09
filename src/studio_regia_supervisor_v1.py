#!/usr/bin/env python3
"""Shared, offline directorial PRE-FLIGHT for every video series.

Checks only evidence DECLARED in a scene-level shotlist. Does not watch an MP4,
identify objects in a painting, prove rights, spend credits, render or publish.
An automatic pass is never an artistic approval. Existing per-format gates win.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter
from pathlib import Path

SCHEMA = "studio-regia-shotlist-v1"
NARRATED = {"libri", "artvision_critico", "controluce", "documentario", "giuliano"}
CAMERAS = {"locked", "slow_push", "slow_pull", "slow_pan_x", "slow_pan_y"}
TRANSITIONS = {"cut", "match_cut", "fade_to_black", "none"}
HASH = re.compile(r"^[a-f0-9]{64}$")
FIXES = {
    "INVALID_TIMELINE": "Ricostruire una timeline continua dai veri timecode; non correggere con tagli casuali.",
    "SCENE_OVERLAP": "Rimuovere la sovrapposizione: evitare immagini fantasma o scene doppie.",
    "IMAGE_GAP": "Colmare solo con una pausa intenzionale e verificata, non con immagini riempitive.",
    "REUSED_VISUAL": "Sostituire con una scoperta visiva realmente diversa oppure motivare l'inquadratura ferma.",
    "SUBJECT_MISMATCH": "Riposizionare/tagliare il piano sul soggetto citato senza alterare il WAV.",
    "SUBJECT_LATE": "Anticipare il soggetto visibile rispetto alla frase, dopo riscontro sui veri frame.",
    "LOW_EFFECTIVE_PIXELS": "Aprire l'inquadratura o scegliere una scansione migliore; non inventare nitidezza.",
    "CAMERA_NOT_DIRECTED": "Camera ferma oppure movimento lento unidirezionale con motivo semantico.",
    "REPEATED_CAMERA_MOVE": "Alternare movimento e tenuta solo quando la storia lo richiede.",
    "BAD_TRANSITION": "Usare taglio opaco o match cut reale; non sovrapporre due immagini.",
    "SOURCE_NOT_VERIFIED": "Controllare origine, immagine autentica, licenza e ritaglio prima del render.",
    "SHOT_TOO_BRIEF": "Dare tempo di lettura al soggetto o eliminare il dettaglio superfluo.",
    "NO_HOOK": "Far vedere un elemento significativo già nei primi secondi.",
    "SPEECH_TIMECODES_UNVERIFIED": "Allineare la voce WAV reale con ASR/ascolto prima di progettare le scene.",
    "MISSING_SUBJECT_EVIDENCE": "Associare a ogni frase soggetti/aree realmente verificati sull'immagine.",
    "LARGE_EYE_JUMP": "Usare una ripresa di relazione o un raccordo che guidi lo sguardo.",
    "UNIFORM_TIMING": "Variare solo dove il contenuto chiede un respiro diverso; non montare con uno stampino.",
    "VISUAL_STALL": "Verificare sul vero MP4 se la tenuta lunga aggiunge scoperta, altrimenti anticipare il raccordo.",
}


def num(x):
    return type(x) in (float, int) and math.isfinite(x)


def box(x):
    return (isinstance(x, list) and len(x) == 4 and all(num(v) for v in x)
            and 0 <= x[0] < x[2] <= 1 and 0 <= x[1] < x[3] <= 1)


def inspect(data):
    issues = []
    def flag(level, code, shot=None, second=None, detail=""):
        item = {"level": level, "code": code, "fix": FIXES.get(code, "Verificare il piano con il filmato reale.")}
        if shot is not None:
            item["shot"] = shot
        if second is not None and num(second):
            item["second"] = round(second, 3)
        if detail:
            item["detail"] = detail
        issues.append(item)

    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        return {"schema": "studio-regia-supervisor-v1", "status": "blocked_plan",
                "blocking": [{"level": "block", "code": "INVALID_SCHEMA",
                              "fix": "Fornire uno shotlist studio-regia-shotlist-v1."}],
                "warnings": [], "artistic_approved": False, "rendered": False}
    fmt = str(data.get("format") or "").lower().strip()
    if not fmt:
        flag("block", "MISSING_FORMAT")
    length = data.get("video_duration_s")
    if not num(length) or length <= 0:
        flag("block", "INVALID_TIMELINE")
        length = 0
    shots = data.get("shots")
    if not isinstance(shots, list) or not shots:
        flag("block", "NO_SHOTS")
        shots = []
    previous = None
    names = set()
    serial = []
    last_camera = None
    cameras_in_row = 0
    for i, s in enumerate(shots):
        label = i + 1
        if not isinstance(s, dict):
            flag("block", "INVALID_SHOT", label)
            continue
        sid = s.get("id")
        if not isinstance(sid, str) or not sid.strip() or sid in names:
            flag("block", "INVALID_SHOT_ID", label)
        else:
            names.add(sid)
        a, b = s.get("start_s"), s.get("end_s")
        if not num(a) or not num(b) or a < 0 or b <= a or b > length + .1:
            flag("block", "INVALID_TIMELINE", label, a)
            continue
        if previous:
            if a < previous["end_s"] - .1:
                flag("block", "SCENE_OVERLAP", label, a)
            if a > previous["end_s"] + .4:
                flag("review", "IMAGE_GAP", label, a)
        elif a > .35:
            flag("review", "NO_HOOK", label, a, "Il primo piano non inizia subito.")
        if not s.get("source_verified") or not s.get("rights_verified"):
            flag("block", "SOURCE_NOT_VERIFIED", label, a)
        if not str(s.get("reason") or "").strip() or not str(s.get("visual_subject") or "").strip():
            flag("review", "MISSING_SUBJECT_EVIDENCE", label, a)
        if b - a < 1.3 and s.get("visual_complexity") in (4, 5):
            flag("review", "SHOT_TOO_BRIEF", label, a)
        if b - a > 10 and s.get("shot_type") in ("detail", "closeup") and s.get("visual_change_verified") is not True:
            flag("review", "VISUAL_STALL", label, a)
        transition = str(s.get("transition_in") or "cut").lower()
        if transition not in TRANSITIONS:
            flag("block", "BAD_TRANSITION", label, a)
        c = s.get("camera", {"move": "locked"})
        if isinstance(c, str):
            c = {"move": c}
        if not isinstance(c, dict) or c.get("move", "locked") not in CAMERAS:
            flag("block", "CAMERA_NOT_DIRECTED", label, a)
            mode = None
        else:
            mode = c.get("move", "locked")
            if mode != "locked" and not str(s.get("reason") or "").strip():
                flag("review", "CAMERA_NOT_DIRECTED", label, a)
            if mode == last_camera and mode != "locked":
                cameras_in_row += 1
                if cameras_in_row >= 3:
                    flag("review", "REPEATED_CAMERA_MOVE", label, a)
            else:
                cameras_in_row = 1
        last_camera = mode
        crop = s.get("crop_xyxy")
        native = s.get("source_resolution_px")
        target = data.get("delivery_resolution_px")
        if crop is not None and not box(crop):
            flag("block", "INVALID_CROP", label, a)
        if (box(crop) and isinstance(native, list) and len(native) == 2
                and isinstance(target, list) and len(target) == 2
                and all(num(v) and v > 0 for v in native + target)):
            w = native[0] * (crop[2] - crop[0])
            h = native[1] * (crop[3] - crop[1])
            if min(w / target[0], h / target[1]) < .8:
                flag("review", "LOW_EFFECTIVE_PIXELS", label, a,
                     "Il ritaglio ha meno pixel nativi del master richiesto.")
        prev_focus = previous.get("focus_xy") if previous else None
        cur_focus = s.get("focus_xy")
        if (isinstance(prev_focus, list) and isinstance(cur_focus, list)
                and len(prev_focus) == len(cur_focus) == 2
                and all(num(v) and 0 <= v <= 1 for v in prev_focus + cur_focus)
                and math.dist(prev_focus, cur_focus) > .48
                and s.get("shot_type") not in ("wide", "establishing")
                and previous.get("shot_type") not in ("wide", "establishing")):
            flag("review", "LARGE_EYE_JUMP", label, a)
        ident = (s.get("asset_id"), s.get("composition_group"), s.get("visual_subject"))
        serial.append(ident)
        if len(serial) >= 3 and len(set(serial[-3:])) == 1:
            flag("review", "REUSED_VISUAL", label, a)
        previous = s

    if previous and length - previous["end_s"] > .4:
        flag("review", "IMAGE_GAP", len(shots), previous["end_s"])

    # Diagnose a mechanical editing template, never mandate an arbitrary cut count.
    shot_lengths = [s["end_s"] - s["start_s"] for s in shots
                    if isinstance(s, dict) and num(s.get("start_s"))
                    and num(s.get("end_s")) and s["end_s"] > s["start_s"]]
    if len(shot_lengths) >= 4 and max(shot_lengths) - min(shot_lengths) < .15:
        flag("review", "UNIFORM_TIMING", detail="Quattro o piu scene hanno durate quasi identiche.")

    narration = data.get("narration", {})
    if not isinstance(narration, dict):
        narration = {}
    if fmt in NARRATED:
        wav = narration.get("wav_sha256")
        if not isinstance(wav, str) or not HASH.fullmatch(wav) or narration.get("timing_verified") is not True:
            flag("block", "SPEECH_TIMECODES_UNVERIFIED")
        spans = narration.get("segments")
        if not isinstance(spans, list) or not spans:
            flag("block", "NO_SPEECH_SEGMENTS")
        else:
            for j, segment in enumerate(spans):
                if not isinstance(segment, dict):
                    flag("block", "INVALID_SPEECH_SEGMENT")
                    continue
                a, b = segment.get("start_s"), segment.get("end_s")
                if not num(a) or not num(b) or not 0 <= a < b <= length + .1:
                    flag("block", "INVALID_SPEECH_SEGMENT", second=a)
                    continue
                subject = segment.get("subject_id")
                if not isinstance(subject, str) or not subject:
                    flag("review", "MISSING_SUBJECT_EVIDENCE", second=a)
                    continue
                relevant = []
                first = None
                for shot in shots:
                    if not isinstance(shot, dict) or not num(shot.get("start_s")) or not num(shot.get("end_s")):
                        continue
                    visible = shot.get("visible_subject_ids", [])
                    if not isinstance(visible, list) or subject not in visible:
                        continue
                    lo, hi = max(a, shot["start_s"]), min(b, shot["end_s"])
                    if hi > lo:
                        relevant.append((lo, hi))
                        first = lo if first is None else min(first, lo)
                # Timeline can contain overlapping invalid shots: use union, not sum.
                relevant.sort()
                covered = 0
                last = a
                for lo, hi in relevant:
                    covered += max(0, hi - max(lo, last))
                    last = max(last, hi)
                if covered / (b - a) < .8:
                    flag("block", "SUBJECT_MISMATCH", second=a, detail=subject)
                if first is not None and first > a + .35:
                    flag("review", "SUBJECT_LATE", second=a, detail=subject)

    by_code = Counter(x["code"] for x in issues)
    blocking = [x for x in issues if x["level"] == "block"]
    warnings = [x for x in issues if x["level"] == "review"]
    return {
        "schema": "studio-regia-supervisor-v1",
        "format": fmt,
        "status": "blocked_plan" if blocking else "plan_needs_real_video_and_artistic_review",
        "blocking": blocking, "warnings": warnings,
        "summary": {"shots_checked": len(shots), "codes": dict(by_code)},
        "priority_fixes": (blocking + warnings)[:5],
        "review_basis": "Declared metadata only; source, speech, frame content and audio are NOT independently verified here.",
        "handoff": {
            "real_mp4_qa": "src/quality_director_v17.py",
            "spoken_subject_qa": "src/artvision_narrative_focus_gate.py for ArtVision Critico",
            "history_final_gate": "src/storia_rivive_final_gate_v91.py for La Storia Rivive",
            "museum_final_gate": "V80/V118/V119 physical frame, room and real MP4 review",
        },
        "artistic_approved": False, "rendered": False, "can_publish": False,
        "paid_calls": 0,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--shotlist", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    report = inspect(json.loads(args.shotlist.read_text(encoding="utf-8")))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "blocking": len(report["blocking"]),
                      "warnings": len(report["warnings"])}, ensure_ascii=False))
    return 2 if report["blocking"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
