#!/usr/bin/env python3
"""V326: advisory director checks learned from five owner-supplied reels.

Pure storyboard analysis plus an optional real-MP4 black-tail scan. It is not an
AI originality detector, semantic vision model, rights clearance or approval.
No network access, new API bills, rendering, master changes or publishing.
"""
from __future__ import annotations

import re
import subprocess
from statistics import pstdev
from pathlib import Path

REFERENCE_IDS = ("57966", "57967", "57968", "57969", "57970")


def _note(code, message, scene=None):
    item = {"code": code, "message": message}
    if scene is not None:
        item["scene"] = scene
    return item


def analyze_scenes(scenes, *, short=False):
    """Return (blocking, warnings, facts) for *optional* timing fields.

    The existing V19 scene schema still works untouched. Duration is provided
    as seconds, or as start/end; explicit overlaps may represent fades and are
    warnings, not hard errors. Thresholds are prompts to review, not a recipe.
    """
    blocking, warnings, durations = [], [], []
    if not isinstance(scenes, list):
        return [_note("INVALID_SHOTS", "Inquadrature non in lista")], [], {}
    previous_end = None
    prev_signature = None
    same_run = 0
    quick = 0
    timed = 0
    for number, shot in enumerate(scenes, 1):
        if not isinstance(shot, dict):
            blocking.append(_note("INVALID_SHOT", "Inquadratura non valida", number))
            continue
        try:
            has_start = "start" in shot and "end" in shot
            if has_start:
                start, end = float(shot["start"]), float(shot["end"])
                seconds = end - start
                if start < 0 or end <= start:
                    raise ValueError("invalid timestamps")
                if previous_end is not None and start < previous_end - .08:
                    warnings.append(_note("TIMELINE_OVERLAP",
                                          "Sovrapposizione: verificare se dissolvenza prevista", number))
                if previous_end is not None and start > previous_end + .35:
                    warnings.append(_note("TIMELINE_GAP",
                                          "Intervallo non coperto da una scena", number))
                previous_end = end
            elif "duration" in shot:
                seconds = float(shot["duration"])
            else:
                seconds = None
            if seconds is not None and (seconds != seconds or seconds <= 0 or seconds > 1800):
                raise ValueError("invalid duration")
        except (TypeError, ValueError, OverflowError):
            blocking.append(_note("INVALID_TIMING", "Durata o timecode non valido", number))
            continue
        if seconds is not None:
            timed += 1
            durations.append(seconds)
            if seconds < 1.10:
                quick += 1
                if not shot.get("rhythm_justification"):
                    warnings.append(_note("FLASH_SHOT",
                                          "Inquadratura inferiore a 1,1s: leggere l'immagine è difficile", number))
            if short and seconds > 6.0 and shot.get("move") == "static" and not shot.get("rhythm_justification"):
                warnings.append(_note("LONG_STATIC_SHORT",
                                      "Piano statico prolungato nello short: verificarne la funzione", number))
            if shot.get("complex_detail") and seconds < 2.0 and not shot.get("rhythm_justification"):
                warnings.append(_note("COMPLEX_DETAIL_TOO_FAST",
                                      "Dettaglio complesso: tempo forse insufficiente", number))
            if shot.get("kind") == "end_card" and seconds > 2.5:
                warnings.append(_note("LONG_END_CARD",
                                      "Cartello conclusivo lungo: considerare chiusura sull'opera", number))
        signature = (shot.get("artwork"), shot.get("framing"), shot.get("move"))
        if signature == prev_signature and all(signature):
            same_run += 1
        else:
            same_run = 1
        if same_run == 3:
            warnings.append(_note("SAME_SHOT_PATTERN",
                                  "Tre inquadrature consecutive con opera, focale e movimento uguali", number))
        prev_signature = signature
        if shot.get("camera_reason") == "auto_zoom":
            warnings.append(_note("UNMOTIVATED_CAMERA",
                                  "Lo zoom predefinito non è una ragione registica", number))
        if shot.get("spoken_anchor") and not shot.get("visual_anchor"):
            warnings.append(_note("VISUAL_ANCHOR_MISSING",
                                  "La frase nominata richiede un dettaglio visibile preciso", number))
    if timed >= 5:
        if quick >= max(3, int(timed * .4 + .999)):
            warnings.append(_note("TOO_MANY_FLASHES",
                                  "Molti tagli sotto 1,1s: evitare i flash fotografici"))
        if pstdev(durations) < .18:
            warnings.append(_note("MECHANICAL_CADENCE",
                                  "Durate quasi uguali: motivare il ritmo con l'opera"))
    facts = {"shots": len(scenes), "timed_shots": timed,
             "durations_seconds": [round(x, 3) for x in durations],
             "timings_not_available": timed != len(scenes),
             "visual_truth_verified": False, "narration_alignment_verified": False,
             "artistically_approved": False,
             "reference_reels": list(REFERENCE_IDS)}
    return blocking, warnings, facts


BLACK_RE = re.compile(
    r"black_start:\s*([\d.]+)\s+black_end:\s*([\d.]+)\s+black_duration:\s*([\d.]+)"
)


def inspect_black_tail(video, duration):
    """Scan last six seconds of real MP4. Return warnings and bounded facts.

    Optical-content check only. Black may be intentional; require an actual
    viewer to determine whether it is appropriate. ffmpeg failure is reported.
    """
    warnings = []
    if duration <= .1:
        return [_note("TAIL_UNCHECKED", "Durata non disponibile")], {"black_tail_scan": "unavailable"}
    tail_length = min(6.0, duration)
    start = max(0.0, duration - tail_length)
    cmd = ["ffmpeg", "-hide_banner", "-nostats", "-ss", f"{start:.3f}",
           "-i", str(Path(video)), "-t", f"{tail_length:.3f}", "-an",
           "-vf", "blackdetect=d=0.45:pix_th=0.08:pic_th=0.98",
           "-f", "null", "-"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True,
                                timeout=90, check=False)
        if result.returncode != 0:
            raise RuntimeError("ffmpeg returned non-zero")
        spans = [tuple(float(v) for v in match)
                 for match in BLACK_RE.findall(result.stderr)]
        trailing = [span for span in spans
                    if span[1] >= tail_length - .30 and span[2] >= .70]
        if trailing:
            longest = max(x[2] for x in trailing)
            warnings.append(_note("BLACK_TAIL",
                                  f"Coda quasi nera di ~{longest:.1f}s: controllare il finale reale"))
        facts = {"black_tail_scan": "last_six_seconds",
                 "tail_window_seconds": round(tail_length, 2),
                 "detected_black_intervals": len(spans),
                 "black_end_warning": bool(trailing)}
    except (OSError, subprocess.TimeoutExpired, RuntimeError):
        warnings.append(_note("BLACK_TAIL_SCAN_UNAVAILABLE",
                              "Verifica coda MP4 non riuscita: necessaria revisione reale"))
        facts = {"black_tail_scan": "unavailable"}
    return warnings, facts
