#!/usr/bin/env python3
"""V57: gate cromatico offline. Nessuna AI, API, rete, spesa o revisione artistica automatica."""
import argparse
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np

AI_METHODS = {"ddcolor_temporal", "reference_guided_video", "ai_video_restoration", "generative_recreation"}

def frame_metrics(bgr):
    height, width = bgr.shape[:2]
    hsv = cv2.cvtColor(bgr[int(height*.07):int(height*.91), int(width*.07):int(width*.93)], cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    eligible = (s > 40) & (v > 40) & (v < 250)
    if not np.any(eligible):
        return {"hue_entropy_bits": 0.0, "hue_bands": 0, "saturation": 0.0}
    counts = np.bincount((h[eligible] // 10).ravel(), minlength=18).astype(np.float64)
    p = counts / counts.sum()
    ent = float(-np.sum(p[p > 0] * np.log2(p[p > 0])))
    return {"hue_entropy_bits": round(ent, 4), "hue_bands": int(np.count_nonzero(p > .03)),
            "saturation": round(float(np.mean(s[eligible])), 2)}

def inspect(video, start, end, stride=.8):
    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        raise ValueError("MP4 non apribile")
    width, height = int(cap.get(3)), int(cap.get(4))
    fps, nframes = float(cap.get(5)), float(cap.get(7))
    duration = nframes / fps if fps > 0 else 0
    if not (0 <= start < end <= duration + .05):
        cap.release()
        raise ValueError("Intervallo segmento a colori fuori dal video")
    rows = []
    try:
        for second in np.arange(start, end, stride):
            cap.set(cv2.CAP_PROP_POS_MSEC, float(second * 1000))
            ok, frame = cap.read()
            if ok:
                rows.append({"second": round(float(second), 2), **frame_metrics(frame)})
    finally:
        cap.release()
    if len(rows) < 3:
        raise ValueError("Meno di tre fotogrammi colorizzati verificabili")
    entropies = [r["hue_entropy_bits"] for r in rows]
    return {"width": width, "height": height, "duration_s": round(duration, 3),
            "frames_reviewed": len(rows),
            "median_hue_entropy_bits": round(float(np.median(entropies)), 3),
            "p75_hue_entropy_bits": round(float(np.percentile(entropies, 75)), 3),
            "samples": rows}

def gates(info, method, model_id, claim_4k=False, preset="reference_modern_color"):
    errors, warnings = [], []
    if info["height"] <= info["width"] or abs(info["height"]/info["width"] - 16/9) > .06:
        errors.append("Formato non 9:16")
    if claim_4k and (info["width"], info["height"]) != (2160, 3840):
        errors.append("Output non 2160x3840: vietato chiamarlo 4K")
    if preset == "reference_modern_color":
        if method not in AI_METHODS:
            errors.append("V57: seppia/LUT/dissolvenza NON e' colorizzazione AI")
        elif len(model_id.strip()) < 3:
            errors.append("Modello AI non documentato")
        if info["median_hue_entropy_bits"] < 1.1 and info["p75_hue_entropy_bits"] < 1.4:
            errors.append("Colori quasi monocromatici, non comparabili ai riferimenti")
        if info["width"] < 1080:
            warnings.append("Risoluzione minore di 1080; richiede valutazione visiva su telefono")
    warnings.append("Gate cromatico solo tecnico: revisione di volti, movimento, colore storico, aperture e audio obbligatoria")
    return errors, warnings

def main():
    p = argparse.ArgumentParser(description="La Storia Rivive — V57 gate colori e risoluzione")
    p.add_argument("--video", required=True)
    p.add_argument("--color-start", type=float, required=True)
    p.add_argument("--color-end", type=float, required=True)
    p.add_argument("--method", required=True)
    p.add_argument("--model-id", default="")
    p.add_argument("--preset", default="reference_modern_color")
    p.add_argument("--claim-4k", action="store_true")
    p.add_argument("--out")
    a = p.parse_args()
    try:
        info = inspect(a.video, a.color_start, a.color_end)
        errors, warnings = gates(info, a.method, a.model_id, a.claim_4k, a.preset)
        sha = hashlib.sha256(Path(a.video).read_bytes()).hexdigest()
        result = {"ok": not errors, "video_sha256": sha, "method_declared": a.method,
                  "model_declared": a.model_id or "not_supplied", "errors": errors,
                  "warnings": warnings, "technical_metrics": info,
                  "artistic_approval": "NOT_CERTIFIED"}
    except (OSError, ValueError) as e:
        result = {"ok": False, "errors": [str(e)], "artistic_approval": "NOT_CERTIFIED"}
    output = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    print(output)
    if a.out:
        path = Path(a.out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(output, encoding="utf8")
    return 0 if result["ok"] else 2

if __name__ == "__main__":
    raise SystemExit(main())
