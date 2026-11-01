#!/usr/bin/env python3
"""Boecklin ASR-grounded sentence/frame QA: 19 midpoint screenshots, no video render.

Read-only: no network, TTS, paid API, or changes to any source MP4. This
produces visual evidence for human review; it cannot certify artistic sync.
"""
import argparse
import hashlib
import json
import math
import textwrap
from pathlib import Path

import cv2
from PIL import Image, ImageDraw, ImageFont

B_WAV = 'f567835c07ae952c5d7390122f08ad44a2e3d99d694592ec04de8a30bc6821e5'


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for part in iter(lambda: f.read(1048576), b''):
            h.update(part)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--video', type=Path, required=True)
    p.add_argument('--asr-cache', type=Path, required=True)
    p.add_argument('--output-dir', type=Path, required=True)
    p.add_argument('--expected-video-sha256', required=True)
    p.add_argument('--voice-delay-seconds', type=float, default=5.0)
    a = p.parse_args()
    if sha256(a.video) != a.expected_video_sha256:
        raise ValueError('MP4 SHA mismatch; refusing to sample unverified video')
    cache = json.loads(a.asr_cache.read_text(encoding='utf-8'))
    alignment = cache.get('alignment') or {}
    if (cache.get('wav_sha256') != B_WAV or
        alignment.get('method') != 'asr_with_interpolation' or
        (alignment.get('matched_fraction') or 0) < .85):
        raise ValueError('Require verified original WAV and recovered ASR alignment, not estimated timings')
    timed = cache.get('timed')
    if not isinstance(timed, list) or len(timed) != 19:
        raise ValueError('Expected exactly 19 timed narration sentences')
    cap = cv2.VideoCapture(str(a.video))
    fps = cap.get(cv2.CAP_PROP_FPS)
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if not 19.99 <= fps <= 20.01 or n != 2213:
        raise ValueError('Unexpected Böcklin MP4 frame count or fps')
    a.output_dir.mkdir(parents=True, exist_ok=True)
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 13)
    samples = []
    for i, item in enumerate(timed):
        if len(item) != 3:
            raise ValueError('Malformed ASR timing row')
        sentence, start, end = item
        if not 0 <= start < end <= n / fps:
            raise ValueError('Invalid ASR timestamp')
        middle = a.voice_delay_seconds + (start + end) / 2
        frame_number = min(n - 1, round(middle * fps))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ok, frame = cap.read()
        if not ok:
            raise RuntimeError(f'Cannot read frame {frame_number}')
        thumb = Image.fromarray(cv2.cvtColor(cv2.resize(frame, (200, 356)), cv2.COLOR_BGR2RGB))
        samples.append((i, sentence, middle, frame_number, thumb))
    cap.release()
    sheets = []
    for page in range(math.ceil(len(samples) / 7)):
        group = samples[page * 7:(page + 1) * 7]
        cw, ch, cols = 240, 475, 4
        sheet = Image.new('RGB', (cw * cols, ch * math.ceil(len(group) / cols)), (28, 28, 28))
        draw = ImageDraw.Draw(sheet)
        for j, (i, sentence, middle, frame_number, thumb) in enumerate(group):
            x, y = (j % cols) * cw, (j // cols) * ch
            sheet.paste(thumb, (x + 20, y + 28))
            draw.text((x + 7, y + 5), f'Frase {i + 1} | {middle:.2f}s', font=font, fill='white')
            for k, line in enumerate(textwrap.wrap(sentence, width=30)[:5]):
                draw.text((x + 6, y + 393 + k * 16), line, font=font, fill='white')
        target = a.output_dir / f'BOECKLIN_V111_ASR_SENTENCES_{page + 1}.jpg'
        sheet.save(target, quality=88)
        sheets.append(target.name)
    result = {
        'version': 'V111_ASR_SENTENCE_VISUAL_QA_ONLY',
        'artwork': 'Arnold Boecklin, Die Toteninsel, 1883, NG 2/80',
        'video_sha256': sha256(a.video),
        'source_asr_cache_sha256': sha256(a.asr_cache),
        'wav_sha256': B_WAV,
        'asr_method': alignment['method'],
        'asr_matched_fraction': alignment['matched_fraction'],
        'voice_delay_seconds': a.voice_delay_seconds,
        'sampled_sentences': [
            {'sentence_index': i + 1, 'text': s, 'midpoint_video_seconds': round(t, 3), 'frame_index': f}
            for i, s, t, f, _ in samples
        ],
        'contact_sheets': sheets,
        'qa_scope': '19 actual ASR sentence midpoint frames; human full-speed/audio review still required',
        'no_new_video': True, 'source_mp4_unchanged': True,
        'V25_Gold': False, 'R2_Android_playback_verified': False,
        'new_TTS_AI_API_calls': 0, 'social_published': False,
    }
    out = a.output_dir / 'BOECKLIN_V111_ASR_SENTENCE_QA.json'
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'qa_json': str(out), 'sheets': sheets,
                      'sampled_sentences': len(samples),
                      'video_sha256': result['video_sha256']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
