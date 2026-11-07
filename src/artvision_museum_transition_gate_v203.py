#!/usr/bin/env python3
"""V203 automatic Museum transition QA. This gate is NOT human artistic approval."""
import argparse
import json
from pathlib import Path

def analyze(path, entry_end, exit_start, limit=18.0):
    import cv2
    import numpy as np
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open MP4: {path}")
    count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    assert 1 <= entry_end < exit_start < count
    result = {}
    for boundary in (entry_end, exit_start):
        pair = []
        for index in (boundary - 1, boundary):
            cap.set(cv2.CAP_PROP_POS_FRAMES, index)
            ok, frame = cap.read()
            if not ok:
                raise RuntimeError(f"Missing frame {index}")
            pair.append(cv2.resize(frame, (180, 320), interpolation=cv2.INTER_AREA))
        difference = float(np.mean(np.abs(pair[0].astype(np.float32) - pair[1].astype(np.float32))))
        result[str(boundary)] = {"frame_before": boundary - 1, "frame_after": boundary,
                                 "mean_abs_rgb_jump": round(difference, 3), "pass": difference <= limit}
    cap.release()
    return {"schema": "artvision-museum-transition-v203", "mp4": path.name,
            "frame_count": count, "max_allowed_mean_abs_rgb_jump": limit,
            "boundaries": result, "automatic_transition_gate": "PASS" if all(v["pass"] for v in result.values()) else "FAIL",
            "human_artistic_approval": "NOT_PERFORMED"}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mp4", type=Path)
    parser.add_argument("--entry-end", type=int, required=True)
    parser.add_argument("--exit-start", type=int, required=True)
    parser.add_argument("--limit", type=float, default=18.0)
    parser.add_argument("--output", type=Path)
    a = parser.parse_args()
    result = analyze(a.mp4, a.entry_end, a.exit_start, a.limit)
    if a.output:
        a.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result["automatic_transition_gate"] == "PASS" else 2)

if __name__ == "__main__":
    main()
