"""WOW LAB fail-closed silhouette audit before any rendering.

This gate checks geometry, holes, and whether the mask follows a visible
source-image boundary. It cannot certify semantic completeness: visual review
of the full subject remains mandatory before any successful release.

Usage: python wow_lab/mask_audit.py source.png mask.png --out wow_lab/audits/<slot>
Exit: 0 = technical mask gate passed; 2 = rejected.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import cv2
import numpy as np

MIN_AREA_RATIO = 0.015
MAX_AREA_RATIO = 0.62
MIN_CONTRAST_LAB = 7.0
MAX_OUTLINE_COMPLEXITY = 250.0
MIN_COMPONENT_RATIO = 0.002

def audit(source: np.ndarray | None, mask: np.ndarray | None) -> dict:
    def reject(reason):
        return {"pass": False, "reasons": [reason]}
    if source is None or mask is None:
        return reject("missing_source_or_mask")
    if source.ndim != 3 or source.shape[2] != 3:
        return reject("invalid_source_channels")
    h, w = source.shape[:2]
    if min(h, w) < 120:
        return reject("source_too_small")
    if mask.shape[:2] != (h, w):
        return reject("dimension_mismatch")
    if mask.ndim == 3:
        if mask.shape[2] not in (3, 4):
            return reject("invalid_mask_channels")
        mask = cv2.cvtColor(mask, cv2.COLOR_BGRA2GRAY if mask.shape[2] == 4 else cv2.COLOR_BGR2GRAY)
    if mask.dtype != np.uint8:
        return reject("invalid_mask_dtype")
    binary = np.uint8(mask >= 128) * 255
    area = int(np.count_nonzero(binary))
    ratio = area / float(w * h)
    _, _, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
    parts = sorted((int(s[cv2.CC_STAT_AREA]) for s in stats[1:]
                    if s[cv2.CC_STAT_AREA] >= MIN_COMPONENT_RATIO * w * h), reverse=True)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    perimeter = sum(cv2.arcLength(c, True) for c in contours)
    complexity = perimeter * perimeter / max(area, 1)
    all_contours, hierarchy = cv2.findContours(binary, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    hole_threshold = max(12.0, area * 0.00025)
    holes = []
    if hierarchy is not None:
        holes = [float(cv2.contourArea(c)) for i, c in enumerate(all_contours)
                 if hierarchy[0][i][3] >= 0 and cv2.contourArea(c) >= hole_threshold]
    border_pixels = int(np.count_nonzero(binary[0, :]) + np.count_nonzero(binary[-1, :])
                        + np.count_nonzero(binary[1:-1, 0]) + np.count_nonzero(binary[1:-1, -1]))
    reasons = []
    if not MIN_AREA_RATIO <= ratio <= MAX_AREA_RATIO:
        reasons.append("implausible_subject_area")
    if len(parts) != 1:
        reasons.append("multiple_or_missing_subject_components")
    if border_pixels:
        reasons.append("mask_touches_image_border")
    if len(holes) > 2:
        reasons.append("internal_holes_subject_missing_patches")
    if complexity > MAX_OUTLINE_COMPLEXITY:
        reasons.append("irregular_or_fragmented_outline")
    # A smooth patch of paper may have acceptable geometry, but no actual
    # subject boundary. Compare the 5px inner/outer rings in CIELAB.
    k = np.ones((5, 5), dtype=np.uint8)
    inner = (binary != 0) & (cv2.erode(binary, k) == 0)
    outer = (binary == 0) & (cv2.dilate(binary, k) != 0)
    contrast = 0.0
    if np.count_nonzero(inner) >= 24 and np.count_nonzero(outer) >= 24:
        lab = cv2.cvtColor(source, cv2.COLOR_BGR2LAB).astype(np.float32)
        contrast = float(np.linalg.norm(np.mean(lab[inner], axis=0) - np.mean(lab[outer], axis=0)))
    if contrast < MIN_CONTRAST_LAB:
        reasons.append("weak_boundary_contrast_background_leak_risk")
    if contours:
        x, y, bw, bh = cv2.boundingRect(np.vstack(contours))
        bbox = [int(x), int(y), int(bw), int(bh)]
    else:
        bbox = None
    return {
        "pass": not reasons, "reasons": reasons,
        "subject_area_ratio": round(ratio, 5),
        "large_components": len(parts), "border_pixels": border_pixels,
        "internal_holes": len(holes),
        "outline_complexity": round(float(complexity), 2),
        "boundary_contrast_lab": round(contrast, 2),
        "subject_bbox_xywh": bbox,
        "semantic_completeness_verified": False,
        "requires_visual_review": True,
    }

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("mask")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    output = Path(args.out)
    output.mkdir(parents=True, exist_ok=True)
    source = cv2.imread(args.source, cv2.IMREAD_COLOR)
    mask = cv2.imread(args.mask, cv2.IMREAD_UNCHANGED)
    report = audit(source, mask)
    (output / "mask_audit.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    if source is not None and mask is not None and source.shape[:2] == mask.shape[:2]:
        if mask.ndim == 3:
            gray = cv2.cvtColor(mask, cv2.COLOR_BGRA2GRAY if mask.shape[2] == 4 else cv2.COLOR_BGR2GRAY)
        else:
            gray = mask
        binary = np.uint8(gray >= 128) * 255
        overlay = source.copy()
        overlay[binary == 0] = (overlay[binary == 0].astype(np.float32) * 0.25).astype(np.uint8)
        boundary = cv2.morphologyEx(binary, cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)) != 0
        overlay[boundary] = (0, 255, 255)
        cv2.imwrite(str(output / "mask_preview.png"), overlay)
    print(json.dumps(report, ensure_ascii=False))
    raise SystemExit(0 if report["pass"] else 2)

if __name__ == "__main__":
    main()
