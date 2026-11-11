#!/usr/bin/env python3
"""V188: SHA-locked, no-upscale 9:16 review crops from V187 archival PNGs.

All outputs are previews of the *compressed Commons derivative*, not I2I,
not native scans, not proof of five distinct shots or publishable rights.
No network, AI providers, credits, or automated approval.
"""
import argparse
import hashlib
import json
import re
import subprocess
import zipfile
from pathlib import Path

EXPECTED_FILM_SHA = 'eacbb947105f9143632e3d4e933ee5e200ba98f5d588c11c552dfb94787de1d9'
MAX_ZIP_BYTES = 32 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 70 * 1024 * 1024
MAX_PNG_BYTES = 12 * 1024 * 1024
REQUIRED_FILES = {'SOURCE_PROVENANCE.json', 'shot_catalog/V187_SHOT_CATALOG.json'}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def verify_zip(archive):
    """Validate *all* members before trusting bytes, paths, or PNGs."""
    archive = Path(archive)
    if archive.is_symlink() or not archive.is_file() or archive.stat().st_size > MAX_ZIP_BYTES:
        raise ValueError('ARCHIVE_MISSING_SYMLINK_OR_TOO_LARGE')
    with zipfile.ZipFile(archive) as z:
        members = z.infolist()
        names = [m.filename for m in members]
        if len(names) != len(set(names)) or len(names) > 24:
            raise ValueError('DUPLICATE_OR_EXCESS_MEMBERS')
        if not REQUIRED_FILES.issubset(names):
            raise ValueError('MISSING_PROVENANCE_OR_CATALOG')
        if sum(m.file_size for m in members) > MAX_UNCOMPRESSED_BYTES:
            raise ValueError('UNCOMPRESSED_LIMIT_EXCEEDED')
        for m in members:
            if (m.filename.startswith('/') or '..' in Path(m.filename).parts or
                    '\\' in m.filename or m.is_dir() or (m.external_attr >> 16) & 0o170000 == 0o120000):
                raise ValueError('UNSAFE_ZIP_MEMBER')
            if m.filename not in REQUIRED_FILES and m.filename != 'V187_CONTACT_SHEET.jpg' and not re.fullmatch(r'shot_catalog/shot_\d\d\.png', m.filename):
                raise ValueError('UNEXPECTED_ZIP_MEMBER')
        provenance = json.loads(z.read('SOURCE_PROVENANCE.json'))
        catalog = json.loads(z.read('shot_catalog/V187_SHOT_CATALOG.json'))
        if (provenance.get('sha256') != EXPECTED_FILM_SHA or
                catalog.get('source_sha256') != EXPECTED_FILM_SHA or
                provenance.get('native_scan') is not False or
                provenance.get('provider_jobs_may_start') is not False or
                catalog.get('status') != 'DIVERSE_CUT_CANDIDATES_NEED_VISUAL_REVIEW'):
            raise ValueError('UNTRUSTED_SOURCE_PROVENANCE')
        candidates = catalog.get('candidates', [])
        if not 5 <= len(candidates) <= 20:
            raise ValueError('INVALID_CANDIDATE_COUNT')
        seen = set()
        frames = []
        for candidate in candidates:
            name = candidate.get('png_filename', '')
            if not re.fullmatch(r'shot_\d\d\.png', name) or name in seen:
                raise ValueError('INVALID_OR_DUPLICATE_PNG_NAME')
            seen.add(name)
            path = 'shot_catalog/' + name
            if path not in names or z.getinfo(path).file_size > MAX_PNG_BYTES:
                raise ValueError('MISSING_OR_OVERSIZED_PNG')
            data = z.read(path)
            if sha256(data) != candidate.get('png_sha256'):
                raise ValueError('PNG_SHA_MISMATCH:' + name)
            frames.append((candidate, data))
        return frames, provenance


def probe_png(path):
    p = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                        '-show_entries', 'stream=width,height,codec_name',
                        '-of', 'json', str(path)], check=True, capture_output=True,
                       text=True, timeout=30)
    stream = json.loads(p.stdout)['streams'][0]
    if stream.get('codec_name') != 'png':
        raise ValueError('NOT_A_PNG')
    return int(stream['width']), int(stream['height'])


def geometry(width, height):
    """Exact 9:16 pixels without resizing, three different horizontal offsets."""
    if width < 640 or height < 720:
        raise ValueError('SOURCE_TOO_SMALL_FOR_CROP_REVIEW')
    crop_h = min((height // 16) * 16, (width // 9) * 16)
    crop_w = crop_h * 9 // 16
    if crop_w <= 0 or crop_h <= 0:
        raise ValueError('INVALID_CROP_GEOMETRY')
    return {'width': crop_w, 'height': crop_h,
            'y': (height - crop_h) // 2,
            'x_offsets': {'left': 0, 'center': (width - crop_w) // 2,
                          'right': width - crop_w}}


def luma_grid(path):
    p = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', str(path),
                        '-frames:v', '1', '-vf', 'scale=9:8,format=gray',
                        '-f', 'rawvideo', '-'], check=True, capture_output=True, timeout=30)
    if len(p.stdout) != 72:
        raise ValueError('LUMA_GRID_DECODE_FAILED')
    return list(p.stdout)


def audit(archive, output):
    output = Path(output)
    if output.exists() or any(p.is_symlink() for p in output.parents):
        raise ValueError('OUTPUT_EXISTS_OR_SYMLINK_PARENT')
    frames, provenance = verify_zip(archive)
    output.mkdir(parents=True)
    report = {'version': 'V188', 'status': 'PORTRAIT_CROPS_NEED_VISUAL_REVIEW',
              'source_sha256': EXPECTED_FILM_SHA,
              'source_kind': 'WIKIMEDIA_COMPRESSED_DERIVATIVE_NOT_NATIVE_SCAN',
              'source_page': provenance.get('source_page'), 'candidates': [],
              'rights_italy_verified': False, 'five_distinct_shots_verified': False,
              'freeze_pts_verified': False, 'human_visual_qa_approved': False,
              'provider_jobs_may_start': False, 'publish_permitted': False,
              'blocking_issues': ['NATIVE_SCAN_UNVERIFIED', 'FIVE_DISTINCT_SHOTS_UNVERIFIED',
                                  'PORTRAIT_READABILITY_NEEDS_HUMAN_REVIEW',
                                  'ITALIAN_RIGHTS_UNVERIFIED', 'I2I_AND_VIDU_MISSING']}
    for candidate, data in frames:
        name = candidate['png_filename']
        source = output / name
        source.write_bytes(data)
        width, height = probe_png(source)
        if (width, height) != (1436, 1080):
            raise ValueError('UNEXPECTED_SOURCE_FRAME_DIMENSIONS:' + name)
        g = geometry(width, height)
        grid = luma_grid(source)
        dark = sum(grid) / 72 < 20 and sum(x < 35 for x in grid) / 72 >= .85
        row = {'png_filename': name, 'source_png_sha256': sha256(data),
               'sample_seconds': candidate['sample_seconds'],
               'source_frame_width': width, 'source_frame_height': height,
               'dark_or_intertitle_like': dark,
               'source_crop_pixels': [g['width'], g['height']],
               'crop_width_below_720px': g['width'] < 720, 'crops': []}
        if dark:
            row['review_note'] = 'REJECT_NEAR_BLACK_OR_INTERTITLE_LIKE'
        else:
            for position, x in g['x_offsets'].items():
                dest = output / (name[:-4] + '_' + position + '_9x16.png')
                subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', str(source),
                                '-frames:v', '1', '-vf',
                                f"crop={g['width']}:{g['height']}:{x}:{g['y']}",
                                str(dest)], check=True, capture_output=True, timeout=50)
                if probe_png(dest) != (g['width'], g['height']):
                    raise ValueError('CROP_DIMENSION_MISMATCH')
                row['crops'].append({'position': position, 'filename': dest.name,
                                     'x': x, 'y': g['y'],
                                     'sha256': sha256(dest.read_bytes())})
        report['candidates'].append(row)
        source.unlink()  # only verified crop previews remain, original is in V187 artifact
    (output / 'V188_PORTRAIT_AUDIT.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--artifact-zip', required=True)
    p.add_argument('--out-dir', required=True)
    args = p.parse_args()
    r = audit(args.artifact_zip, args.out_dir)
    print(json.dumps({'status': r['status'], 'candidates': len(r['candidates']),
                      'dark_rejected': sum(c['dark_or_intertitle_like'] for c in r['candidates']),
                      'crops': sum(len(c['crops']) for c in r['candidates'])}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
