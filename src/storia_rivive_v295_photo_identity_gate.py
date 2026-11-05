#!/usr/bin/env python3
"""Fail-closed identity gate for La Storia Rivive photo restorations.

This gate does not certify artistic quality.  It only rejects candidates that
cannot be reviewed as faithful colour restorations because they changed the
frame geometry, remained essentially monochrome, or lost too much of the
source's large-scale structure.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _structure_correlation(source: Image.Image, candidate: Image.Image) -> float:
    size = (96, 96)
    src = np.asarray(
        source.convert("L").resize(size, Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(1.0)),
        dtype=np.float32,
    )
    dst = np.asarray(
        candidate.convert("L").resize(size, Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(1.0)),
        dtype=np.float32,
    )
    src -= float(src.mean())
    dst -= float(dst.mean())
    denominator = float(np.linalg.norm(src) * np.linalg.norm(dst))
    return 0.0 if denominator == 0 else float(np.sum(src * dst) / denominator)


def evaluate(source_path: Path, candidate_path: Path) -> dict:
    with Image.open(source_path) as source_raw, Image.open(candidate_path) as candidate_raw:
        source = source_raw.convert("RGB")
        candidate = candidate_raw.convert("RGB")
        src_w, src_h = source.size
        out_w, out_h = candidate.size
        src_ratio = src_w / src_h
        out_ratio = out_w / out_h
        aspect_delta = abs(src_ratio - out_ratio) / src_ratio

        hsv = np.asarray(candidate.convert("HSV"), dtype=np.uint8)
        saturation = hsv[..., 1]
        mean_saturation = float(saturation.mean())
        coloured_fraction = float(np.mean(saturation >= 18))
        source_saturation = np.asarray(source.convert("HSV"), dtype=np.uint8)[..., 1]
        source_mean_saturation = float(source_saturation.mean())
        source_coloured_fraction = float(np.mean(source_saturation >= 18))
        structure = _structure_correlation(source, candidate)

    checks = {
        "source_is_monochrome": source_mean_saturation <= 20.0 and source_coloured_fraction <= 0.40,
        "same_aspect_ratio": aspect_delta <= 0.015,
        # A faint sepia cast is not a colour restoration.  The thresholds are
        # intentionally conservative and only admit candidates with material
        # chroma across a substantial part of the frame.
        "real_colour_present": mean_saturation >= 28.0 and coloured_fraction >= 0.45,
        "source_structure_retained": structure >= 0.72,
    }
    blockers = [name for name, passed in checks.items() if not passed]
    return {
        "schema": "storia_rivive_photo_identity_gate_v295",
        "ready_for_artistic_review": not blockers,
        "release_approved": False,
        "status": "IDENTITY_GATE_PASSED_NEEDS_ARTISTIC_REVIEW" if not blockers else "REJECTED_IDENTITY_GATE",
        "blockers": blockers,
        "checks": checks,
        "metrics": {
            "source_size": [src_w, src_h],
            "candidate_size": [out_w, out_h],
            "relative_aspect_delta": round(aspect_delta, 6),
            "source_mean_saturation_0_255": round(source_mean_saturation, 3),
            "source_coloured_fraction": round(source_coloured_fraction, 6),
            "mean_saturation_0_255": round(mean_saturation, 3),
            "coloured_fraction": round(coloured_fraction, 6),
            "structure_correlation": round(structure, 6),
        },
        "source_sha256": _sha256(source_path),
        "candidate_sha256": _sha256(candidate_path),
        "paid_calls": 0,
        "social_published": False,
        "note": "A pass permits human visual review only; it is not a final, approval, rights clearance or archive sync.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report = evaluate(args.source, args.candidate)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "blockers": report["blockers"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
