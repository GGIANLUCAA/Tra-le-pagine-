"""Conservative WOW LAB subject mask proposal; CPU-only, fail-closed.

This is not semantic segmentation and cannot approve a video. The CLI writes
candidate_mask.png, mask_before_render.jpg and subject_preflight.json before
any rendering. The existing mask_audit and visual review are mandatory.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import cv2
import numpy as np


def propose_mask(source: np.ndarray) -> tuple[np.ndarray | None, dict]:
    if source is None or source.ndim != 3 or source.shape[2] != 3:
        return None, {"pass": False, "reasons": ["invalid_source"]}
    h, w = source.shape[:2]
    if min(h, w) < 240:
        return None, {"pass": False, "reasons": ["source_too_small"]}
    lab = cv2.cvtColor(source, cv2.COLOR_BGR2LAB).astype(np.float32)
    border = max(6, int(min(h, w) * 0.035))
    rim = np.zeros((h, w), np.uint8)
    rim[:border] = 1
    rim[-border:] = 1
    rim[:, :border] = 1
    rim[:, -border:] = 1
    background = np.median(lab[rim != 0], axis=0)
    spread = np.linalg.norm(lab[rim != 0] - background, axis=1)
    q90 = float(np.percentile(spread, 90))
    if q90 > 23:
        return None, {"pass": False, "reasons": ["nonuniform_background"],
                      "border_lab_p90": round(q90, 2)}
    distance = np.linalg.norm(lab - background, axis=2)
    threshold = max(18., q90 * 2.4)
    preliminary = np.uint8(distance > threshold) * 255
    preliminary[:border] = 0
    preliminary[-border:] = 0
    preliminary[:, :border] = 0
    preliminary[:, -border:] = 0
    preliminary = cv2.morphologyEx(preliminary, cv2.MORPH_CLOSE,
                                   np.ones((3, 3), np.uint8))
    count, labels, stats, _ = cv2.connectedComponentsWithStats(preliminary, 8)
    components = sorted([(int(stats[i, cv2.CC_STAT_AREA]), i)
                         for i in range(1, count)], reverse=True)
    if not components or components[0][0] < 0.015 * w * h:
        return None, {"pass": False, "reasons": ["no_confident_subject"]}
    major = [x for x in components
             if x[0] >= max(0.003 * w * h, components[0][0] * 0.14)]
    if len(major) > 1:
        return None, {"pass": False, "reasons": ["multiple_ambiguous_components"],
                      "major_components": len(major)}
    foreground = np.uint8(labels == components[0][1]) * 255
    foreground = cv2.morphologyEx(foreground, cv2.MORPH_CLOSE,
                                  np.ones((3, 3), np.uint8))
    ys, xs = np.where(foreground > 0)
    if (xs.min() <= border + 2 or xs.max() >= w-border-3 or
            ys.min() <= border+2 or ys.max() >= h-border-3):
        return None, {"pass": False, "reasons": ["subject_near_border"]}
    seed = cv2.erode(foreground, np.ones((5, 5), np.uint8))
    if np.count_nonzero(seed) < 0.005 * w * h:
        return None, {"pass": False, "reasons": ["weak_foreground_seed"]}
    gc = np.full((h, w), cv2.GC_PR_BGD, np.uint8)
    gc[distance > threshold * 0.8] = cv2.GC_PR_FGD
    gc[foreground > 0] = cv2.GC_PR_FGD
    gc[seed > 0] = cv2.GC_FGD
    gc[rim != 0] = cv2.GC_BGD
    gc[distance < max(7., q90 * 1.2)] = cv2.GC_BGD
    gc[seed > 0] = cv2.GC_FGD
    try:
        cv2.grabCut(source, gc, None, np.zeros((1, 65), np.float64),
                    np.zeros((1, 65), np.float64), 4, cv2.GC_INIT_WITH_MASK)
    except cv2.error:
        return None, {"pass": False, "reasons": ["grabcut_failed"]}
    result = np.uint8(np.isin(gc, [cv2.GC_FGD, cv2.GC_PR_FGD])) * 255
    n, labels2, stats2, _ = cv2.connectedComponentsWithStats(result, 8)
    sizes = sorted([int(stats2[i, cv2.CC_STAT_AREA])
                    for i in range(1, n)], reverse=True)
    if not sizes or sizes[0] < 0.015 * w * h:
        return None, {"pass": False, "reasons": ["segmentation_collapsed"]}
    if len(sizes) > 1 and sizes[1] >= max(0.002*w*h, 0.07*sizes[0]):
        return None, {"pass": False, "reasons": ["multiple_extracted_subjects"]}
    index = max(range(1, n), key=lambda i: stats2[i, cv2.CC_STAT_AREA])
    result = np.uint8(labels2 == index) * 255
    bg_like = float(np.mean(distance[result != 0] < max(9., q90 * 1.3)))
    if bg_like > 0.20:
        return None, {"pass": False, "reasons": ["background_in_mask_suspected"],
                      "background_like_fraction": round(bg_like, 3)}
    return result, {"pass": True, "reasons": [],
                    "border_lab_p90": round(q90, 2),
                    "foreground_threshold_lab": round(threshold, 2),
                    "background_like_fraction": round(bg_like, 3),
                    "semantic_completeness_verified": False,
                    "requires_visual_review": True}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="Rights-verified image; rights not checked here")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    output = Path(args.out).resolve()
    root = Path(__file__).resolve().parent
    if output != root and root not in output.parents:
        parser.error("Output must remain inside wow_lab/")
    output.mkdir(parents=True, exist_ok=True)
    source = cv2.imread(args.source, cv2.IMREAD_COLOR)
    mask, proposal = propose_mask(source)
    if mask is None:
        report = {"pass": False, "proposal": proposal}
    else:
        from mask_audit import audit
        geometry = audit(source, mask)
        report = {"pass": bool(proposal["pass"] and geometry["pass"]),
                  "proposal": proposal, "geometry": geometry,
                  "artistic_approval": False}
        cv2.imwrite(str(output / "candidate_mask.png"), mask)
        preview = source.copy()
        preview[mask == 0] = (preview[mask == 0].astype(np.float32) * 0.25).astype(np.uint8)
        cv2.imwrite(str(output / "mask_before_render.jpg"), preview)
    (output / "subject_preflight.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report))
    raise SystemExit(0 if report["pass"] else 2)


if __name__ == "__main__":
    main()
