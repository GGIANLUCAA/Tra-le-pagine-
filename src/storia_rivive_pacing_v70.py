#!/usr/bin/env python3
"""La Storia Rivive V70: content-led adaptive pacing, no fixed montage template.
Requires real observations supplied by an editor/visual analysis step.
Does not inspect videos, generate AI stills, consume credits or publish.
"""
import argparse
import copy
import json
import math
from pathlib import Path

VERSION = "V70_2026_10_29"
MIN_TOTAL, MAX_TOTAL, TARGET = 14.0, 35.0, 25.0
BASE = {
    "face": (0.72, 0.31, 1.55),
    "action": (0.92, 0.33, 1.60),
    "wide": (1.06, 0.42, 1.85),
    "detail": (0.68, 0.30, 1.50),
    "climax": (0.92, 0.48, 2.10),
}
VARIATION = (-0.15, 0.13, 0.02, -0.10, 0.17, -0.04, 0.09)


def numeric(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def observation_errors(s, i):
    errors = []
    p = f"Scena {i+1}: "
    if s.get("scene_type") not in BASE:
        errors.append(p + "scene_type deve essere face/action/wide/detail/climax")
    for key in ("emotional_value", "visual_complexity", "motion_value", "image_quality"):
        v = s.get(key)
        if not numeric(v) or not 1 <= v <= 5:
            errors.append(p + key + " richiede punteggio motivato 1-5")
    for key in ("unique_event_id", "composition_group", "narrative_role"):
        if not isinstance(s.get(key), str) or not s[key].strip():
            errors.append(p + key + " mancante")
    if not isinstance(s.get("visual_evidence"), str) or len(s["visual_evidence"].strip()) < 20:
        errors.append(p + "mancano descrizione visiva e timecode della scena")
    if not numeric(s.get("source_frame_timecode_s")) or s["source_frame_timecode_s"] < 0:
        errors.append(p + "timecode esatto del frame congelato mancante")
    for key in ("source_visually_reviewed", "safe_crop_reviewed", "source_rights_verified"):
        if s.get(key) is not True:
            errors.append(p + key + " non verificato")
    if numeric(s.get("image_quality")) and s["image_quality"] < 3:
        errors.append(p + "qualita insufficiente: cambiare fonte, non accelerare")
    if numeric(s.get("emotional_value")) and s["emotional_value"] < 2:
        errors.append(p + "riempitivo poco interessante: scartare scena")
    return errors


def duration(shots):
    return round(sum(s["motion_s"] + s["transition_s"] + s["photo_hold_s"] for s in shots), 3)


def plan(project):
    obj = copy.deepcopy(project)
    shots = obj.get("shots")
    if not isinstance(shots, list) or not 3 <= len(shots) <= 20:
        raise ValueError("Servono 3-20 scene candidate osservate")
    errors = [msg for i, s in enumerate(shots) for msg in observation_errors(s, i)]
    if errors:
        raise ValueError("\n".join(errors))
    seen = set()
    for s in shots:
        event = s["unique_event_id"]
        if event in seen:
            raise ValueError("Evento duplicato: zoom e crop non sono nuove scene")
        seen.add(event)
    removed = []
    # Keep editorial/chronological order, but remove visual filler when repeated.
    while len(shots) > 4:
        k = next((i for i in range(2, len(shots))
                  if shots[i]["composition_group"] == shots[i-1]["composition_group"]
                  == shots[i-2]["composition_group"]), None)
        if k is None:
            break
        opts = [i for i in (k-2, k-1, k) if i not in (0, len(shots)-1)]
        drop = min(opts, key=lambda i: (shots[i]["image_quality"] + shots[i]["emotional_value"], i))
        removed.append(shots.pop(drop)["unique_event_id"])
    for i, s in enumerate(shots):
        bw, reveal, hold = BASE[s["scene_type"]]
        bw += 0.075 * (s["motion_value"] - 3)
        hold += 0.14 * (s["visual_complexity"] - 3)
        hold += 0.13 * (s["emotional_value"] - 3) + VARIATION[i % len(VARIATION)]
        if i == 0:
            bw = min(1.05, bw)
        bw = round(max(.58, min(1.65, bw)), 2)
        s["motion_s"] = bw
        s["transition_s"] = round(reveal, 2)
        s["photo_hold_s"] = round(max(1.05, min(2.95, hold)), 2)
        # NEVER move the AI photo to a different historical frame.
        start = round(s["source_frame_timecode_s"] - bw, 3)
        if start < 0:
            raise ValueError(f"Scena {i+1}: freeze troppo vicino a inizio fonte")
        s["start_s"] = start
        s["timing_reason"] = "Gesto in B/N, freeze autentico e ricompensa colore proporzionata a contenuto"
    # 25 seconds is a desired average, NOT a quota to pad with dull shots.
    while duration(shots) > MAX_TOTAL and len(shots) > 4:
        opts = range(1, len(shots)-1)
        idx = min(opts, key=lambda i: (1.8 * shots[i]["emotional_value"]
                        + shots[i]["image_quality"] + .6 * shots[i]["visual_complexity"], i))
        removed.append(shots.pop(idx)["unique_event_id"])
    if duration(shots) < MIN_TOTAL:
        # Longer hold only if the image is sufficiently rich. Otherwise fail.
        for i in sorted(range(len(shots)), key=lambda i:
                        shots[i]["visual_complexity"] + shots[i]["emotional_value"], reverse=True):
            if duration(shots) >= MIN_TOTAL:
                break
            s = shots[i]
            room = min(2.95 - s["photo_hold_s"], MIN_TOTAL - duration(shots))
            if room > 0 and s["visual_complexity"] >= 3:
                s["photo_hold_s"] = round(s["photo_hold_s"] + room, 2)
    # Make triples of almost identical edits less likely without fake scene creation.
    for i in range(2, len(shots)):
        trio = [sum(shots[j][k] for k in ("motion_s","transition_s","photo_hold_s"))
                for j in (i-2, i-1, i)]
        if max(trio) - min(trio) < .28:
            s = shots[i]
            if i + 1 < len(shots) and s["photo_hold_s"] >= 1.5 and shots[i+1]["photo_hold_s"] <= 2.6:
                s["photo_hold_s"] = round(s["photo_hold_s"] - .32, 2)
                shots[i+1]["photo_hold_s"] = round(shots[i+1]["photo_hold_s"] + .32, 2)
            elif s["photo_hold_s"] <= 2.55:
                s["photo_hold_s"] = round(s["photo_hold_s"] + .38, 2)
            elif s["photo_hold_s"] >= 1.55:
                s["photo_hold_s"] = round(s["photo_hold_s"] - .35, 2)
    obj["pacing_policy_version"] = VERSION
    obj["pacing_v70"] = {
        "status": "TIMING_PLANNED_NOT_VIDEO_QA",
        "target_average_s": TARGET,
        "allowed_duration_s": [MIN_TOTAL, MAX_TOTAL],
        "actual_planned_s": duration(shots),
        "unique_scenes": len(shots),
        "rejected_candidate_event_ids": removed,
        "method": "source-reviewed evidence and content type; no fixed scene count",
        "music_beat_alignment": "REQUIRES_ACTUAL_AUDIO_REVIEW",
        "manual_artistic_release_gate": "V64/V66 and V55 remain mandatory",
    }
    failures, warnings = check(obj)
    if failures:
        raise ValueError("Piano non conforme:\n" + "\n".join(failures))
    obj["pacing_v70"]["warnings"] = warnings
    return obj


def check(obj):
    errors, warnings = [], []
    if obj.get("pacing_policy_version") != VERSION:
        errors.append("Manca piano V70: eseguire il planner prima del render")
    shots = obj.get("shots")
    if not isinstance(shots, list) or not shots:
        return errors + ["Nessuna scena"], warnings
    ids = set()
    for i, s in enumerate(shots):
        errors += observation_errors(s, i)
        eid = s.get("unique_event_id")
        if eid in ids:
            errors.append(f"Scena {i+1}: evento duplicato")
        ids.add(eid)
        vals = [s.get(k) for k in ("motion_s","transition_s","photo_hold_s")]
        if not all(numeric(x) for x in vals):
            errors.append(f"Scena {i+1}: tempi mancanti")
            continue
        bw, transition, hold = vals
        if not .55 <= bw <= 1.8:
            errors.append(f"Scena {i+1}: B/N fuori .55-1.8s")
        if not .18 <= transition <= .8:
            errors.append(f"Scena {i+1}: reveal fuori .18-.8s")
        if not 1.05 <= hold <= 3.05:
            errors.append(f"Scena {i+1}: tempo colore fuori 1.05-3.05s")
        if not numeric(s.get("start_s")) or not numeric(s.get("source_frame_timecode_s")):
            errors.append(f"Scena {i+1}: timecode originale non ancorato")
        elif abs(s["start_s"] + bw - s["source_frame_timecode_s"]) > .035:
            errors.append(f"Scena {i+1}: freeze non sul fotogramma originale selezionato")
        if i >= 2 and s.get("composition_group") == shots[i-1].get("composition_group") == shots[i-2].get("composition_group"):
            errors.append(f"Scena {i+1}: tre composizioni uguali consecutive")
    if all(all(numeric(s.get(k)) for k in ("motion_s","transition_s","photo_hold_s")) for s in shots):
        length = duration(shots)
        if not MIN_TOTAL <= length <= MAX_TOTAL:
            errors.append(f"Durata {length}s fuori 14-35s: evitare filler")
        if shots[0]["motion_s"] + shots[0]["transition_s"] > 1.5:
            errors.append("Primo reveal troppo tardi (>1.5s)")
        if sum(s["photo_hold_s"] for s in shots) / length < .45:
            errors.append("Troppo poco colore: manca ricompensa visiva")
        for i in range(2, len(shots)):
            trio = [sum(shots[j][k] for k in ("motion_s","transition_s","photo_hold_s"))
                    for j in (i-2, i-1, i)]
            if max(trio) - min(trio) < .20:
                errors.append(f"Scena {i+1}: tre cicli temporali quasi uguali")
        if length < 20:
            warnings.append("Video breve: valido se materiale sufficiente, non obbligatorio arrivare a 25s")
        if length > 30:
            warnings.append("Video lungo: revisionare che ogni scena aggiunga una scoperta")
    if shots[0].get("emotional_value", 0) < 3:
        errors.append("Apertura non forte per un reel")
    if len(shots) >= 6 and max((s.get("emotional_value", 0) for s in shots[len(shots)//2:]), default=0) < 4:
        warnings.append("Seconda meta senza un altro payoff forte")
    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description="Preflight del ritmo storico, senza rendering")
    parser.add_argument("mode", choices=("plan", "check"))
    parser.add_argument("--input", required=True)
    parser.add_argument("--output")
    a = parser.parse_args()
    try:
        raw = json.loads(Path(a.input).read_text(encoding="utf-8"))
        if a.mode == "plan":
            if not a.output:
                parser.error("plan richiede --output")
            result = plan(raw)
            dst = Path(a.output)
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(json.dumps(result["pacing_v70"], ensure_ascii=False, indent=2))
        else:
            errors, warnings = check(raw)
            report = {"valid": not errors, "failures": errors, "warnings": warnings}
            if a.output:
                Path(a.output).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(json.dumps(report, ensure_ascii=False, indent=2))
            if errors:
                return 2
        return 0
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"valid": False, "error": str(e)}, ensure_ascii=False, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
