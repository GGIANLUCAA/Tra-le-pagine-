#!/usr/bin/env python3
"""Read-only V165 comparison of actual private user examples 43055/43056 vs a candidate.

NOT a face/identity-quality judge. The original user videos are never uploaded to GitHub.
Needs cv2, numpy, Pillow; prints no tokens. SHA checks prevent comparing random files.
Output is an evidence-only contact sheet and JSON; it NEVER approves a master.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

REFERENCE_SHA256 = {
    '43055': '86a7dd3d2db0d18ba51b601c3b9a0ad7befe180ff2a2f3e2176abce9c7692cae',
    '43056': '9db1bbebce888b5cbd9e4fb3dc0a5a4fd13a74a3aeccb188912bdee29a8cfcba',
}
REFERENCE_TIMES = {
    '43055': (3.6, 5.5, 10.7, 12.4, 14.1),
    '43056': (2.1, 5.7, 10.7, 12.2, 14.1),
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def verify_private_reference(name: str, path: Path) -> None:
    if name not in REFERENCE_SHA256:
        raise ValueError('UNKNOWN_REFERENCE')
    if not path.is_file():
        raise FileNotFoundError(f'PRIVATE_REFERENCE_MISSING_{name}')
    if digest(path) != REFERENCE_SHA256[name]:
        raise ValueError(f'PRIVATE_REFERENCE_HASH_MISMATCH_{name}')


def metadata(path: Path) -> dict:
    run = subprocess.run([
        'ffprobe', '-v', 'error', '-show_entries',
        'format=duration:stream=codec_name,width,height,avg_frame_rate',
        '-of', 'json', str(path),
    ], capture_output=True, text=True, timeout=45, check=True)
    data = json.loads(run.stdout)
    streams = data.get('streams', [])
    video = next((s for s in streams if s.get('width') and s.get('height')), None)
    if video is None:
        raise ValueError('NO_DECODABLE_VIDEO_STREAM')
    return {'duration_s': float(data['format']['duration']),
            'width': video['width'], 'height': video['height'],
            'video_codec': video['codec_name'],
            'audio_present': any(s.get('codec_name') == 'aac' for s in streams)}


def content_row_fraction(frame: np.ndarray) -> float:
    """Quick letterbox diagnostic; may include captions. NOT image quality score."""
    if frame.ndim != 3 or frame.shape[2] != 3:
        raise ValueError('COLOR_FRAME_REQUIRED')
    h, w = frame.shape[:2]
    if h < 40 or w < 40:
        raise ValueError('FRAME_TOO_SMALL')
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    core = gray[:, w // 10: w - w // 10]
    active = (core.std(axis=1) > 17.0) & (core.mean(axis=1) > 27.0)
    return float(np.mean(active))


def visual_metrics(frame: np.ndarray) -> dict:
    h, w = frame.shape[:2]
    region = frame[max(0, h // 10): max(1, h - h // 10),
                   max(0, w // 10): max(1, w - w // 10)]
    gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    return {
        'active_content_row_fraction_approx': round(content_row_fraction(frame), 3),
        'median_saturation_center': round(float(np.median(hsv[:, :, 1])), 1),
        'detail_proxy_laplacian_var_center': round(
            float(cv2.Laplacian(blur, cv2.CV_32F).var()), 1),
    }


def sample(path: Path, times: tuple[float, ...]) -> tuple[list[np.ndarray], list[dict]]:
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise ValueError('VIDEO_OPENCV_DECODE_FAILED')
    frames, metrics = [], []
    try:
        for sec in times:
            cap.set(cv2.CAP_PROP_POS_MSEC, sec * 1000.0)
            ok, frame = cap.read()
            if not ok:
                raise ValueError(f'MISSING_SAMPLE_AT_{sec:.3f}')
            frames.append(frame)
            metrics.append({'time_s': round(sec, 3), **visual_metrics(frame)})
    finally:
        cap.release()
    return frames, metrics


def review_sheet(groups: list[tuple[str, list[np.ndarray], list[dict]]], target: Path) -> None:
    thumb_w, thumb_h, label_h = 180, 320, 50
    n = max(len(frames) for _, frames, _ in groups)
    sheet = Image.new('RGB', (n * thumb_w, len(groups) * (thumb_h + label_h)), (20, 20, 20))
    draw = ImageDraw.Draw(sheet)
    for row, (title, frames, stats) in enumerate(groups):
        y = row * (thumb_h + label_h)
        for col, (frame, values) in enumerate(zip(frames, stats)):
            x = col * thumb_w
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pict = Image.fromarray(rgb).resize((thumb_w, thumb_h))
            sheet.paste(pict, (x, y + label_h))
            draw.text((x + 4, y + 4), title, fill=(255, 255, 255))
            draw.text((x + 4, y + 23), f"{values['time_s']}s active={values['active_content_row_fraction_approx']:.2f}", fill=(240, 240, 240))
    sheet.save(target, quality=90)


def compare(reference_55: Path, reference_56: Path, candidate: Path, outdir: Path) -> dict:
    verify_private_reference('43055', reference_55)
    verify_private_reference('43056', reference_56)
    if not candidate.is_file():
        raise FileNotFoundError('CANDIDATE_MP4_MISSING')
    outdir.mkdir(parents=True, exist_ok=True)
    sources = {'43055': reference_55, '43056': reference_56, 'candidate': candidate}
    summaries, groups = {}, []
    for key, video in sources.items():
        info = metadata(video)
        times = REFERENCE_TIMES[key] if key in REFERENCE_TIMES else tuple(
            round(float(t), 3) for t in np.linspace(.8, min(info['duration_s'] - .8, info['duration_s'] * .85), 5))
        frames, stats = sample(video, times)
        summaries[key] = {
            'sha256': digest(video), 'metadata': info, 'samples': stats,
            'median_active_content_row_fraction_approx': round(
                float(np.median([s['active_content_row_fraction_approx'] for s in stats])), 3),
        }
        groups.append((key, frames, stats))
    review_sheet(groups, outdir / 'VISUAL_COMPARE_PRIVATE.jpg')
    result = {
        'version': 'V165', 'type': 'PRIVATE_REFERENCE_QUALITY_AUDIT',
        'references_authenticated': True,
        'references': {k: summaries[k] for k in REFERENCE_SHA256},
        'candidate': summaries['candidate'],
        'caveats': [
            'Image area proxy includes some titles and cannot establish visual quality.',
            'Detail metrics depend on subject, camera motion, noise and compression; no universal pass threshold.',
            'Sampled reference frames may be black and white; palette measured in context, not scored in isolation.',
            'The 43055/43056 examples are creative/photorealistic target references, not source-identity or license evidence.',
            'Source-locked optical flow or DDColor-only is insufficient by itself for reference-level moving human detail.',
            'A 720x1280 encode never proves a 720x1280 native archival scan.',
        ],
        'mandatory_visual_checks': [
            'Human face/eyes/skin/hair convincingly photoreal during COLORED MOVEMENT',
            'Hands/limbs and period clothing stable without distortions across time',
            'Real motion not static photo zoom; no invented person or altered scene without explicit disclosure',
            'Image fills useful vertical composition; important humans not tiny or hidden by bars',
            'Color and photographic detail persist through motion, not only at still freeze',
            'First visual payoff fast; shot-by-shot coherent sound and historical setting',
        ],
        'human_artistic_review': 'REQUIRED',
        'user_approved_candidate': False,
        'final_quality_pass': False,
        'social_publication_permitted': False,
    }
    (outdir / 'V165_PRIVATE_REFERENCE_AUDIT.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return result


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--ref43055', type=Path, required=True)
    p.add_argument('--ref43056', type=Path, required=True)
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    report = compare(a.ref43055, a.ref43056, a.candidate, a.out)
    print(json.dumps({
        'status': 'REFERENCE_AUDIT_REVIEW_REQUIRED',
        'reference_sha256_checked': report['references_authenticated'],
        'sampled_content_area_reference_55': report['references']['43055']['median_active_content_row_fraction_approx'],
        'sampled_content_area_reference_56': report['references']['43056']['median_active_content_row_fraction_approx'],
        'sampled_content_area_candidate': report['candidate']['median_active_content_row_fraction_approx'],
        'approved': False,
    }))


if __name__ == '__main__':
    main()
