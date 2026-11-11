#!/usr/bin/env python3
"""V189: five true-film motion clips + pixel-matched freezes (BLACK AND WHITE ONLY).

One source locked Commons derivative, five pre-reviewed DISTINCT cut intervals,
no generated reconstruction, no Vidu, no soundtrack, no rights assertion.
Proof MP4 must NOT be represented as an approved finished historical restoration.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import zipfile

from storia_rivive_v184_source_intake import inspect_local
from storia_rivive_v188_portrait_audit import EXPECTED_FILM_SHA, verify_zip, geometry

# Human-looked-at DIFFERENT SETTINGS in V187; this is editorial PRESELECTION,
# not a claim of five independently authenticated camera shots or quality.
SELECTED = [
    ('shot_03.png', 'left', 'office-financier'),
    ('shot_04.png', 'center', 'exchange-crowd'),
    ('shot_06.png', 'center', 'banquet'),
    ('shot_07.png', 'center', 'farm-family'),
    ('shot_08.png', 'right', 'granary-worker'),
]
MOTION_SECONDS = 2.15
FREEZE_SECONDS = 0.75
FPS = 25


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def ffmpeg(*args, timeout=150):
    return subprocess.run(['ffmpeg', '-hide_banner', '-nostdin', '-loglevel', 'error', '-y',
                           *map(str, args)], capture_output=True, check=True, timeout=timeout)


def ffprobe(path, count_frames=False):
    cmd = ['ffprobe', '-v', 'error', '-select_streams', 'v:0']
    if count_frames:
        cmd += ['-count_frames']
    cmd += ['-show_entries', 'stream=codec_name,width,height,nb_read_frames,r_frame_rate',
            '-show_entries', 'format=duration', '-of', 'json', str(path)]
    r = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=60)
    data = json.loads(r.stdout)
    stream = data['streams'][0]
    return {'width': int(stream['width']), 'height': int(stream['height']),
            'duration': float(data.get('format', {}).get('duration', 0) or 0),
            'codec': stream['codec_name'],
            'frames': int(stream['nb_read_frames']) if count_frames else None}


def check_plan(archive):
    frames, provenance = verify_zip(archive)  # V188 validates source + 10 PNG SHA
    candidates = {c['png_filename']: c for c, _ in frames}
    selected = []
    for name, position, label in SELECTED:
        if name not in candidates:
            raise ValueError('SELECTED_SOURCE_FRAME_MISSING:' + name)
        c = candidates[name]
        if c['interval_end_seconds'] - c['interval_start_seconds'] < 4.0:
            raise ValueError('SOURCE_INTERVAL_TOO_SHORT')
        if not (c['interval_start_seconds'] + 2.2 < c['sample_seconds'] < c['interval_end_seconds'] - 0.1):
            raise ValueError('SOURCE_ANCHOR_TOO_CLOSE_TO_CUT')
        if not re.fullmatch('[0-9a-f]{64}', c['png_sha256']):
            raise ValueError('INVALID_ANCHOR_SHA')
        selected.append(dict(c, crop_position=position, editorial_label=label))
    if len({s['shot_interval_index'] for s in selected}) != 5:
        raise ValueError('DUPLICATED_CUT_INTERVAL')
    if sorted(s['sample_seconds'] for s in selected) != [s['sample_seconds'] for s in selected]:
        raise ValueError('SCENES_NOT_CHRONOLOGICAL')
    return selected, provenance


def grayscale_motion_metric(video):
    """True frame-to-frame changes on decoded film; not optical-flow animation."""
    p = subprocess.run(['ffmpeg', '-hide_banner', '-nostdin', '-loglevel', 'error',
                        '-i', str(video), '-vf', 'fps=5,scale=64:64,format=gray',
                        '-f', 'rawvideo', '-'], check=True, capture_output=True, timeout=80)
    size = 64 * 64
    count = len(p.stdout) // size
    if count < 6 or len(p.stdout) % size:
        raise ValueError('INSUFFICIENT_DECODED_FILM_FRAMES')
    frames = [p.stdout[i * size:(i+1)*size] for i in range(count)]
    diffs = []
    for a, b in zip(frames, frames[1:]):
        diffs.append(sum(abs(x-y) for x, y in zip(a,b)) / size)
    return {'sampled_frames': count, 'mean_luma_delta': round(sum(diffs) / len(diffs), 4),
            'max_luma_delta': round(max(diffs), 4)}


def render_scene(source, row, index, out):
    width, height = 1436, 1080
    g = geometry(width, height)  # 603x1072 source pixels; 720 output is ENCODE upscaling
    x = g['x_offsets'][row['crop_position']]
    start = round(row['sample_seconds'] - MOTION_SECONDS, 3)
    if start < row['interval_start_seconds'] or row['sample_seconds'] >= row['interval_end_seconds']:
        raise ValueError('MOTION_OUTSIDE_AUTHENTIC_SHOT_INTERVAL')
    stem = f'{index:02d}_{row["editorial_label"]}'
    clip = out / (stem + '_real_film_bw.mp4')
    freeze = out / (stem + '_last_real_film_frame.png')
    filtergraph = (f'crop={g["width"]}:{g["height"]}:{x}:{g["y"]},'
                   'scale=720:1280:flags=lanczos,format=yuv420p')
    ffmpeg('-ss', f'{start:.3f}', '-i', source, '-t', f'{MOTION_SECONDS:.3f}',
           '-map', '0:v:0', '-an', '-vf', filtergraph, '-r', FPS,
           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', 22,
           '-pix_fmt', 'yuv420p', '-movflags', '+faststart', clip)
    media = ffprobe(clip, count_frames=True)
    if media['width'] != 720 or media['height'] != 1280 or media['frames'] < 25:
        raise ValueError('FILM_CLIP_INVALID')
    motion = grayscale_motion_metric(clip)
    if motion['mean_luma_delta'] < 0.08:  # Reject static frames; threshold is minimal
        raise ValueError('FILM_MOTION_NOT_PROVEN')
    ffmpeg('-i', clip, '-vf', f'select=eq(n\,{media["frames"]-1})',
           '-vsync', '0', '-frames:v', 1, freeze)
    fmeta = ffprobe(freeze)
    if fmeta['width'] != 720 or fmeta['height'] != 1280:
        raise ValueError('FREEZE_INVALID_DIMENSIONS')
    return {'index': index, 'label': row['editorial_label'],
            'v187_png': row['png_filename'], 'v187_sha256': row['png_sha256'],
            'v187_sample_seconds': row['sample_seconds'],
            'v187_interval': [row['interval_start_seconds'], row['interval_end_seconds']],
            'source_crop_px': [g['width'], g['height']],
            'output_encoder_upscaled': True, 'crop_position': row['crop_position'],
            'motion_start_seconds_requested': start, 'motion_seconds_requested': MOTION_SECONDS,
            'motion_mp4': clip.name, 'motion_mp4_sha256': sha(clip),
            'motion_decoded_frames': media['frames'], 'motion': motion,
            'exact_last_decoded_frame_sha256': sha(freeze), 'freeze_png': freeze.name,
            'freeze_from_last_encoded_motion_frame': True,
            'v187_png_is_not_the_frozen_frame': True}


def make_reel(out, shots):
    # Real motion and 0.75s matching black/white freeze; no fake I2I/animation.
    entries = []
    for r in shots:
        clip = out / r['motion_mp4']
        freeze = out / r['freeze_png']
        still = out / (f'{r["index"]:02d}_freeze_bw.mp4')
        ffmpeg('-loop', 1, '-framerate', FPS, '-i', freeze,
               '-t', str(FREEZE_SECONDS), '-an', '-c:v', 'libx264',
               '-pix_fmt', 'yuv420p', '-preset', 'veryfast', '-crf', 22, still)
        entries.extend([clip, still])
    listing = out / 'V189_CONCAT_LIST.txt'
    # All entries created here, no unsafe external filenames.
    listing.write_text(''.join(f"file '{x.name}'\n" for x in entries), encoding='utf-8')
    reel = out / 'V189_TRUE_BW_MOTION_FIVE_SCENES_PROOF_NOT_FINAL.mp4'
    ffmpeg('-f', 'concat', '-safe', '0', '-i', listing, '-an',
           '-c:v', 'libx264', '-crf', 22, '-preset', 'veryfast',
           '-pix_fmt', 'yuv420p', '-movflags', '+faststart', reel, timeout=240)
    metadata = ffprobe(reel, count_frames=True)
    if metadata['codec'] != 'h264' or metadata['width'] != 720 or metadata['height'] != 1280:
        raise ValueError('PROOF_VIDEO_CODEC_OR_DIMENSIONS_BAD')
    if not 14 <= metadata['duration'] <= 35:
        raise ValueError('PROOF_VIDEO_DURATION_OUT_OF_RANGE')
    ffmpeg('-v', 'error', '-i', reel, '-f', 'null', '-', timeout=120)
    return {'name': reel.name, 'sha256': sha(reel), **metadata}


def produce(source, expected_sha, catalog_zip, out):
    out = Path(out)
    if out.exists() or any(p.is_symlink() for p in (out, *out.parents)):
        raise ValueError('OUTPUT_EXISTS_OR_SYMLINK')
    rows, provenance = check_plan(catalog_zip)
    intake = inspect_local(source, expected_sha)
    if intake['status'] != 'ASSETS_PENDING' or expected_sha != EXPECTED_FILM_SHA:
        raise ValueError('SOURCE_SHA_OR_RESOLUTION_INVALID')
    out.mkdir(parents=True)
    report = {'version': 'V189', 'status': 'MOTION_PROOF_BLOCKED',
              'source_sha256': expected_sha, 'source_page': provenance['source_page'],
              'source_kind': 'WIKIMEDIA_COMPRESSED_DERIVATIVE_NOT_NATIVE_SCAN',
              'not_a_restoration': True, 'four_real_i2i': 0, 'real_vidu_clips': 0,
              'real_soundtrack': False, 'rights_italy_verified': False,
              'human_approved': False, 'publish_permitted': False,
              'provider_jobs_may_start': False, 'scenes': [],
              'blocking_issues': ['FOUR_GENERATIVE_I2I_NOT_PRODUCED',
                                  'VIDU_NOT_PRODUCED', 'ARTISTIC_QA_PENDING',
                                  'ITALIAN_RIGHTS_NOT_CLEARED',
                                  'NATIVE_SCAN_NOT_VERIFIED',
                                  'V91_V94_V96_V99_FINAL_NOT_RUN']}
    try:
        for i, row in enumerate(rows, 1):
            report['scenes'].append(render_scene(source, row, i, out))
        report['proof'] = make_reel(out, report['scenes'])
        report['status'] = 'REAL_BW_MOTION_PROOF_REVIEW_ONLY'
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        report['blocking_issues'].append(type(exc).__name__ + ':' + str(exc)[:160])
        raise
    finally:
        (out / 'V189_REAL_MOTION_PROOF_REPORT.json').write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--file', required=True)
    parser.add_argument('--expected-sha256', required=True)
    parser.add_argument('--catalog-zip', required=True)
    parser.add_argument('--out-dir', required=True)
    a = parser.parse_args()
    r = produce(a.file, a.expected_sha256, a.catalog_zip, a.out_dir)
    print(json.dumps({'status': r['status'], 'duration': r['proof']['duration'],
                      'scenes': len(r['scenes']), 'source': r['source_sha256']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
