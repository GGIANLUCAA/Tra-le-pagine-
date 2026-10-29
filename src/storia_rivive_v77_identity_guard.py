#!/usr/bin/env python3
"""La Storia Rivive V77 — source-identity-preserving image QA and conservative composite.

Purpose:
* Flag risks of generative model inventing people, altering ladders/cars/horses, etc.
* Preserve the SOURCE luminance/shape in output, especially in low-confidence tiles
  and curator-annotated bounding boxes.
* NEVER claim semantic correctness based only on image statistics. Human inspection
  of before/after (and neighbouring source frames) remains mandatory.

Install: pip install opencv-python-headless numpy
Example:
 python src/storia_rivive_v77_identity_guard.py \
   --source frame.png --candidate photo_ai.png --output photo_guarded.png \
   --report v77_review.json --preview before_after.jpg \
   --regions regions.json

Supported regions.json:
 {"regions":[{"label":"ladder","bbox":[100,200,180,340],"normalized":false},
             {"label":"uncertain human silhouette","bbox":[0.1,0.2,0.4,0.55],"normalized":true}]}

Coordinates refer to GENERATED photo dimensions. The label is metadata for
human review, not a model-predicted classification.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def read_bgr(path: Path) -> np.ndarray:
    img = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if img is None or min(img.shape[:2]) < 100:
        raise ValueError(f'Cannot read valid source/candidate: {path}')
    return img


def _normalize_reference(reference: np.ndarray, generated: np.ndarray) -> np.ndarray:
    h, w = generated.shape[:2]
    ratio_ref = reference.shape[1] / reference.shape[0]
    ratio_generated = w / h
    if abs(ratio_ref / ratio_generated - 1) > 0.024:
        raise ValueError('SOURCE_AND_GENERATED_ASPECT_MISMATCH: wrong crop / framing')
    return cv2.resize(reference, (w, h), interpolation=cv2.INTER_CUBIC)


def _safe_corr(a: np.ndarray, b: np.ndarray) -> float | None:
    a = a.astype(np.float32).reshape(-1)
    b = b.astype(np.float32).reshape(-1)
    if min(float(a.std()), float(b.std())) < 3.0:
        return None
    a -= a.mean()
    b -= b.mean()
    n = float(np.sqrt((a * a).sum() * (b * b).sum()))
    return float((a * b).sum() / n) if n > 1e-8 else None


def inspect(reference: np.ndarray, generated: np.ndarray,
            cols: int = 6, rows: int = 10) -> tuple[dict, np.ndarray]:
    """Conservative risk screen; NOT a person/object classifier."""
    reference = _normalize_reference(reference, generated)
    h, w = generated.shape[:2]
    src = cv2.cvtColor(reference, cv2.COLOR_BGR2GRAY)
    dst = cv2.cvtColor(generated, cv2.COLOR_BGR2GRAY)
    src_blur = cv2.GaussianBlur(src, (0, 0), 1.6)
    dst_blur = cv2.GaussianBlur(dst, (0, 0), 1.6)
    src_edges = cv2.Canny(src_blur, 35, 95)
    dst_edges = cv2.Canny(dst_blur, 35, 95)
    global_corr = _safe_corr(cv2.resize(cv2.GaussianBlur(src, (0, 0), 3), (96, 168)),
                             cv2.resize(cv2.GaussianBlur(dst, (0, 0), 3), (96, 168)))
    eps = 1e-5
    edge_growth = float((np.count_nonzero(dst_edges) + 1) / (np.count_nonzero(src_edges) + 1))
    edge_map = np.zeros((h, w), dtype=np.uint8)
    tile_results = []
    flagged = []
    for yi in range(rows):
        y0 = int(h * yi / rows)
        y1 = int(h * (yi + 1) / rows)
        for xi in range(cols):
            x0 = int(w * xi / cols)
            x1 = int(w * (xi + 1) / cols)
            s = src_blur[y0:y1, x0:x1]
            g = dst_blur[y0:y1, x0:x1]
            correlation = _safe_corr(s, g)
            s_count = int(np.count_nonzero(src_edges[y0:y1, x0:x1]))
            g_count = int(np.count_nonzero(dst_edges[y0:y1, x0:x1]))
            # Don't divide by ~zero when original is a blank sky; use a
            # separate rule for hallucinated high-detail texture in blank areas.
            growth = float((g_count + 12) / (s_count + 12))
            mean_src_contrast = float(s.std())
            suspicious_new_texture = (s_count < 42 and g_count > 130)
            suspicious_growth = (growth > 1.55 and g_count > 140)
            suspicious_structure = (correlation is not None and correlation < 0.65
                                    and mean_src_contrast > 7)
            risk = bool(suspicious_growth or suspicious_new_texture or suspicious_structure)
            flags = []
            if suspicious_growth:
                flags.append('ADDED_OR_ALTERED_EDGES')
            if suspicious_new_texture:
                flags.append('NEW_DETAIL_WHERE_SOURCE_IS_AMBIGUOUS')
            if suspicious_structure:
                flags.append('LOCAL_STRUCTURE_CHANGE')
            item = {
                'bbox_px': [x0, y0, x1, y1],
                'local_luminance_correlation': None if correlation is None else round(correlation, 3),
                'source_edges': s_count,
                'candidate_edges': g_count,
                'edge_growth': round(growth, 2),
                'warning_codes': flags,
            }
            tile_results.append(item)
            if risk:
                flagged.append(item)
                edge_map[y0:y1, x0:x1] = 255
    flag_ratio = len(flagged) / max(1, len(tile_results))
    # 
    # A full photo can match globally at 0.99 while still hallucinating a
    # person in one region. Therefore global correlation NEVER constitutes
    # approval. All candidates require visual approval, even without warnings.
    high_risk = flag_ratio > 0.32 or edge_growth > 1.7
    report = {
        'global_luminance_correlation': None if global_corr is None else round(global_corr, 4),
        'global_edge_growth': round(edge_growth, 3),
        'total_tiles': len(tile_results),
        'suspicious_tiles': len(flagged),
        'suspicious_tile_fraction': round(flag_ratio, 3),
        'automatic_risk': 'HIGH' if high_risk else ('REVIEW' if flagged else 'UNVERIFIED'),
        'semantic_object_identity_verified': False,
        'human_review_required': True,
        'warnings': flagged,
        'limitations': [
            'Statistics detect some structural abnormalities but CANNOT distinguish a ladder from a person.',
            'A high global similarity cannot prove that local objects retained their identity.',
            'Inspect faces, hands, clothing, railings, ladders, vehicles, horses and background silhouettes manually.',
            'The final still must be checked against the original AND its nearby moving frames.'
        ],
    }
    return report, edge_map


def load_regions(path: Path | None, shape: tuple[int, int]) -> list[dict]:
    if path is None:
        return []
    data = json.loads(path.read_text(encoding='utf-8'))
    result = []
    h, w = shape
    for item in data.get('regions', []):
        bbox = item.get('bbox')
        if not isinstance(bbox, list) or len(bbox) != 4:
            raise ValueError('Invalid curator region bbox')
        if item.get('normalized', False):
            x0, y0, x1, y1 = [int(v * dim) for v, dim in zip(bbox, [w, h, w, h])]
        else:
            x0, y0, x1, y1 = map(int, bbox)
        x0, x1 = sorted((max(0, min(w, x0)), max(0, min(w, x1))))
        y0, y1 = sorted((max(0, min(h, y0)), max(0, min(h, y1))))
        if x1 <= x0 or y1 <= y0:
            raise ValueError('Empty curator-protected bbox')
        result.append({'label': str(item.get('label', 'uncertain object')), 'bbox_px': [x0, y0, x1, y1]})
    return result


def source_locked_composite(source: np.ndarray, generated: np.ndarray,
                            risk_map: np.ndarray, protected_regions: list[dict],
                            base_source_weight: float = 0.78) -> tuple[np.ndarray, dict]:
    """Keep source shape/identity defined by original light and shadow.

    Retain generated chroma, not invented luminance, and bias further toward
    original source in anomalous areas / curator-protected objects. It cannot
    fully undo hallucinated chroma: a human must still approve the result.
    """
    original = _normalize_reference(source, generated)
    h, w = generated.shape[:2]
    src_lab = cv2.cvtColor(original.astype(np.float32) / 255., cv2.COLOR_BGR2LAB)
    gen_lab = cv2.cvtColor(generated.astype(np.float32) / 255., cv2.COLOR_BGR2LAB)
    src_weight = np.full((h, w), base_source_weight, dtype=np.float32)
    # Soft interpolation prevents visible checkerboard tile boundaries.
    blurred_risk = cv2.GaussianBlur(risk_map.astype(np.float32) / 255, (0, 0), 26)
    src_weight = np.maximum(src_weight, 0.93 * blurred_risk)
    for region in protected_regions:
        mask = np.zeros((h, w), dtype=np.float32)
        x0, y0, x1, y1 = region['bbox_px']
        mask[y0:y1, x0:x1] = 1
        mask = cv2.GaussianBlur(mask, (0, 0), 12)
        src_weight = np.maximum(src_weight, 0.98 * mask)
    src_weight = np.clip(src_weight, base_source_weight, 0.98)
    new_lab = np.empty_like(gen_lab)
    new_lab[:, :, 0] = src_weight * src_lab[:, :, 0] + (1 - src_weight) * gen_lab[:, :, 0]
    # Chroma as smooth, cautious color hypotheses, preserving 100% source
    # brightness structure in important regions. Avoid tiny chroma face-like
    # invented features from the generative output.
    color_a = cv2.GaussianBlur(gen_lab[:, :, 1], (0, 0), 2.0)
    color_b = cv2.GaussianBlur(gen_lab[:, :, 2], (0, 0), 2.0)
    new_lab[:, :, 1] = color_a * 0.90
    new_lab[:, :, 2] = color_b * 0.90
    out = np.clip(cv2.cvtColor(new_lab, cv2.COLOR_LAB2BGR) * 255, 0, 255).astype('uint8')
    meta = {
        'method': 'source-luminance-preserving colored composite',
        'base_fraction_original_luminance': base_source_weight,
        'protected_region_target_source_luminance': 0.98,
        'auto_warning_region_target_source_luminance': 0.93,
        'color_is_interpretive': True,
        'no_guarantee_of_semantic_identity': True,
    }
    return out, meta


def make_review_preview(source: np.ndarray, generated: np.ndarray, guarded: np.ndarray,
                        risk_map: np.ndarray, path: Path) -> None:
    h, w = generated.shape[:2]
    original = _normalize_reference(source, generated)
    # All columns are visually identical sizes, so curator can compare exact objects.
    cols = []
    for frame, label in [(original, 'SOURCE FRAME'), (generated, 'GENERATIVE CANDIDATE'),
                         (guarded, 'SOURCE-LOCKED PHOTO')]:
        panel = cv2.resize(frame, (360, 640))
        panel = cv2.copyMakeBorder(panel, 36, 0, 0, 0, cv2.BORDER_CONSTANT, value=(22, 22, 22))
        cv2.putText(panel, label, (8, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.50,
                    (245, 245, 245), 1, cv2.LINE_AA)
        cols.append(panel)
    warnings = cv2.resize(generated, (360, 640))
    heat = cv2.resize(risk_map, (360, 640), interpolation=cv2.INTER_NEAREST)
    red = warnings.copy()
    red[:, :, 2] = np.maximum(red[:, :, 2], heat)
    warnings = cv2.addWeighted(warnings, .67, red, .33, 0)
    warnings = cv2.copyMakeBorder(warnings, 36, 0, 0, 0, cv2.BORDER_CONSTANT, value=(22, 22, 22))
    cv2.putText(warnings, 'AREAS TO REVIEW', (8, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.50,
                (245, 245, 245), 1, cv2.LINE_AA)
    path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), np.concatenate(cols + [warnings], axis=1),
                [cv2.IMWRITE_JPEG_QUALITY, 93])


def main() -> None:
    p = argparse.ArgumentParser(description='V77 conservative historical photo identity guard')
    p.add_argument('--source', required=True, type=Path)
    p.add_argument('--candidate', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--report', required=True, type=Path)
    p.add_argument('--preview', type=Path)
    p.add_argument('--regions', type=Path)
    p.add_argument('--minimum-source-weight', type=float, default=0.78)
    args = p.parse_args()
    if not .60 <= args.minimum_source_weight <= .95:
        raise ValueError('--minimum-source-weight must be between 0.60 and 0.95')
    source = read_bgr(args.source)
    candidate = read_bgr(args.candidate)
    inspection, risk_map = inspect(source, candidate)
    regions = load_regions(args.regions, candidate.shape[:2])
    result, edit_info = source_locked_composite(source, candidate, risk_map, regions,
                                               args.minimum_source_weight)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(args.output), result, [cv2.IMWRITE_PNG_COMPRESSION, 3]):
        raise RuntimeError('Failed to write photo')
    if args.preview:
        make_review_preview(source, candidate, result, risk_map, args.preview)
    report = {
        'v': 'V77',
        'state': 'PENDING_HUMAN_SEMANTIC_REVIEW',
        'is_automatically_approved': False,
        'source_path': str(args.source),
        'source_sha256': sha256(args.source),
        'candidate_path': str(args.candidate),
        'candidate_sha256': sha256(args.candidate),
        'source_locked_path': str(args.output),
        'source_locked_sha256': sha256(args.output),
        'regions_explicitly_protected': regions,
        'source_lock': edit_info,
        'inspection': inspection,
        'checklist': [
            'Source frame and adjacent 3-5 real film frames show the SAME person/horse/car/ladder.',
            'No figure, face, arm or leg has appeared where there was a vehicle or building element.',
            'No vehicle, ladder or railing has been converted into a person or vice versa.',
            'Object counts, approximate positions, clothing, hands and structures agree with the source.',
            'Unclear subjects remain visibly uncertain; no invented historical details presented as fact.'
        ]
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'state': report['state'], 'report': str(args.report),
                      'candidate_global_corr': inspection['global_luminance_correlation'],
                      'suspicious_tiles': inspection['suspicious_tiles'],
                      'total_tiles': inspection['total_tiles'],
                      'source_locked_photo': str(args.output)}, ensure_ascii=False))


if __name__ == '__main__':
    main()