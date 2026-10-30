"""Isolated fail-closed silhouette audit for WOW LAB; no rendering or publishing.

Usage: python wow_lab/mask_audit.py source.png mask.png --out wow_lab/audits/test
A PASS is geometric only; artistic review remains mandatory.
"""
import argparse
import json
from pathlib import Path
import cv2
import numpy as np

def audit(source, mask):
    if source is None or mask is None:
        return {"pass": False, "reasons": ["missing_source_or_mask"]}
    h, w = source.shape[:2]
    if mask.shape[:2] != (h, w):
        return {"pass": False, "reasons": ["dimension_mismatch"]}
    if mask.ndim == 3:
        mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(binary)
    parts = sorted([int(s[cv2.CC_STAT_AREA]) for s in stats[1:] if s[cv2.CC_STAT_AREA] >= 0.002*w*h], reverse=True)
    area = int(np.count_nonzero(binary))
    ratio = area / (w*h)
    edges = cv2.Canny(binary, 80, 160)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    perimeter = sum(cv2.arcLength(c, True) for c in contours)
    border = int(np.count_nonzero(binary[0,:])+np.count_nonzero(binary[-1,:])+np.count_nonzero(binary[1:-1,0])+np.count_nonzero(binary[1:-1,-1]))
    reasons = []
    if not 0.025 <= ratio <= 0.62: reasons.append("implausible_subject_area")
    if len(parts) != 1: reasons.append("multiple_or_missing_subject_components")
    if border > 0: reasons.append("mask_touches_image_border")
    if perimeter > 0 and perimeter**2 / max(area,1) > 250: reasons.append("irregular_or_fragmented_outline")
    if area and np.count_nonzero(edges) == 0: reasons.append("no_detectable_contour")
    return {"pass": not reasons, "reasons": reasons, "subject_area_ratio": round(ratio,5), "large_components":len(parts), "border_pixels":border, "outline_complexity":round(perimeter**2/max(area,1),2)}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("source"); p.add_argument("mask"); p.add_argument("--out",required=True)
    a=p.parse_args()
    out=Path(a.out)
    out.mkdir(parents=True,exist_ok=True)
    src=cv2.imread(a.source)
    mask=cv2.imread(a.mask,cv2.IMREAD_GRAYSCALE)
    report=audit(src,mask)
    (out/"mask_audit.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    if src is not None and mask is not None and src.shape[:2]==mask.shape[:2]:
        overlay=src.copy()
        overlay[mask<128]=(overlay[mask<128]*0.25).astype(np.uint8)
        cv2.imwrite(str(out/"mask_preview.png"),overlay)
    print(json.dumps(report))
    raise SystemExit(0 if report["pass"] else 2)

if __name__=="__main__": main()
