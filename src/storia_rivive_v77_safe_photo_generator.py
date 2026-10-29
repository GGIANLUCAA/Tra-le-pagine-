#!/usr/bin/env python3
"""V77 future producer: source-locked generative photo, zero paid credits.

This is an on-demand module, NOT an automatic batch workflow. It does not
silently retry or publish. Its product is always PENDING_HUMAN_SEMANTIC_REVIEW.

The operator must inspect the source plus several neighboring original frames,
write an object inventory and optionally mark protected regions before use.

Usage:
 python src/storia_rivive_v77_safe_photo_generator.py \
   --source original_frame.png \
   --verified-objects '1 carriage, 2 horses, street, stone building; NO more people confirmed' \
   --outdir output/candidate_photo --regions regions.json
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import storia_rivive_v77_identity_guard as guard


def build_color_input(original: np.ndarray, out: Path) -> dict:
    """Deterministic original-luminance DDColor pre-colorization; no geometry changes."""
    sp = importlib.util.spec_from_file_location('ddcolor', ROOT / 'src/storia_rivive_real_ai_v60.py')
    dd = importlib.util.module_from_spec(sp)
    assert sp.loader is not None
    sp.loader.exec_module(dd)
    session, meta = dd.download_model()
    source_h, source_w = original.shape[:2]
    # Keep original geometry; only color is inferred by DDColor.
    frame = cv2.resize(original, (720, 576), interpolation=cv2.INTER_AREA)
    ab = dd.infer_ab(session, frame)
    ab = cv2.resize(ab, (source_w, source_h), interpolation=cv2.INTER_CUBIC)
    l = dd.l_channel(original)
    rgb = np.clip(cv2.cvtColor(
        np.dstack((l, np.clip(ab * 1.0, -110, 110))).astype('float32'),
        cv2.COLOR_LAB2RGB) * 255, 0, 255).astype('uint8')
    base_bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    output = cv2.resize(base_bgr, (576, 1024), interpolation=cv2.INTER_CUBIC)
    cv2.imwrite(str(out), output, [cv2.IMWRITE_JPEG_QUALITY, 95])
    return meta


def run_candidate(source_path: Path, outdir: Path, verified_objects: str,
                  protected_regions: Path | None, denoise_strength: float) -> dict:
    if not .08 <= denoise_strength <= .27:
        raise ValueError('DENOISE_EXCEEDS_SAFE_LIMIT: V77 max 0.27; previous V71 used 0.53')
    if len(verified_objects.strip()) < 12:
        raise ValueError('VERIFIED_OBJECT_INVENTORY_REQUIRED: write actual humans/objects from ORIGINAL film')
    from gradio_client import Client, handle_file

    outdir.mkdir(parents=True, exist_ok=True)
    original = guard.read_bgr(source_path)
    if original.shape[0] < 300:
        raise ValueError('LOW_SOURCE_RESOLUTION: choose more detailed original frame or human review')
    base = outdir / 'PRE_COLORIZED_SOURCE.jpg'
    model_meta = build_color_input(original, base)
    prompt = (
        'Restore EXACT SAME photographed scene and EXACT verified number and type of objects. '
        'Objects verified from the true moving archival film: ' + verified_objects + '. '
        'STRICT identity and category preservation: keep every person a person, '
        'every carriage/car part a carriage/car part, every ladder a ladder, every '
        'rail, wheel, horse, building and sign in the same position and size. '
        'NEVER reinterpret ambiguous shadows, spokes, rails, wheels, stairs, '
        'clouds or cracks as human faces, heads, bodies or limbs. '
        'Do not add or remove anyone or anything. '
        'No fictional faces, no fake historical artifacts. '
        'Natural historic colors, source-accurate shapes, modest optical detail. '
        'A restrained photoreal restoration, NOT a recreation or illustration.'
    )
    negative = (
        'new human, extra pedestrian, person from car, person from ladder, '
        'face in wheel, head from railing, new arm, new leg, missing horse, '
        'changed person, changed vehicle, converted objects, altered silhouette, '
        'new architecture, fictional details, hallucination, artistic repaint, '
        'illustration, plastic skin, stylized face, added writing, anime, cartoon'
    )
    # On the documented Space the previous pilot used 0.53 denoise. At that
    # strength diffusion can freely reinterpret small silhouettes as people.
    # V77 deliberately limits it, strengthens structural conditioning and uses
    # fewer prompt-driven changes. One call only; no quota-wasting retries.
    client = Client('finegrain/finegrain-image-enhancer', verbose=False)
    response = client.predict(handle_file(str(base)), prompt, negative,
                              77, 2, 1.30, 1.0, 5, 112, 144,
                              denoise_strength, 18, 'DDIM', api_name='/process')
    result = response[1] if isinstance(response, (tuple, list)) else response
    if isinstance(result, dict):
        result = result.get('path')
    if not result or not Path(str(result)).is_file():
        raise RuntimeError('NO_GENERATIVE_CANDIDATE_FROM_FREE_SPACE; stop, no substitute')
    candidate = outdir / 'FOTO_GENERATIVA_CANDIDATA.png'
    restored = cv2.imread(str(result))
    if restored is None:
        raise RuntimeError('INVALID_MODEL_OUTPUT')
    restored = cv2.resize(restored, (original.shape[1], original.shape[0]))
    cv2.imwrite(str(candidate), restored, [cv2.IMWRITE_PNG_COMPRESSION, 3])

    inspection, risk_map = guard.inspect(original, restored)
    regions = guard.load_regions(protected_regions, restored.shape[:2])
    locked, blend = guard.source_locked_composite(original, restored, risk_map, regions, .78)
    safer = outdir / 'FOTO_RICOSTRUITA_V77_DA_VERIFICARE.png'
    cv2.imwrite(str(safer), locked, [cv2.IMWRITE_PNG_COMPRESSION, 3])
    preview = outdir / 'CONFRONTO_PER_REVISIONE.jpg'
    guard.make_review_preview(original, restored, locked, risk_map, preview)
    report = {
        'status': 'PENDING_HUMAN_SEMANTIC_REVIEW',
        'automatic_publication_allowed': False,
        'verified_objects_are_operator_provided': verified_objects,
        'operator_must_check_adjacent_source_frames': True,
        'input_sha256': guard.sha256(source_path),
        'candidate_sha256': guard.sha256(candidate),
        'source_locked_sha256': guard.sha256(safer),
        'candidate_model': 'finegrain/finegrain-image-enhancer',
        'controls': {'denoise_strength': denoise_strength,
                     'controlnet_scale': 1.30, 'upscale_factor': 2,
                     'number_of_model_calls': 1,
                     'no_automatic_retries': True,
                     'paid_credits_used': 0,
                     'same_original_scene_required': True},
        'known_pitfall': 'High global correlation can hide converting ladder/car/railing to new people.',
        'regions_protected': regions,
        'inspection': inspection,
        'source_luminance_lock': blend,
        'required_next_step': 'Visual approval of each object and person by curator before MP4 export',
        'warning': 'The word generative/photo-real does NOT certify photographic truth.'
    }
    (outdir/'OBJECT_IDENTITY_QA_V77.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    return report


def main():
    a = argparse.ArgumentParser()
    a.add_argument('--source', type=Path, required=True)
    a.add_argument('--outdir', type=Path, required=True)
    a.add_argument('--verified-objects', required=True)
    a.add_argument('--regions', type=Path)
    a.add_argument('--denoise-strength', type=float, default=.22)
    args = a.parse_args()
    report = run_candidate(args.source, args.outdir, args.verified_objects,
                           args.regions, args.denoise_strength)
    print(json.dumps({'status': report['status'], 'risk': report['inspection']['automatic_risk'],
                      'needs_human_review': True},ensure_ascii=False))


if __name__=='__main__':
    main()