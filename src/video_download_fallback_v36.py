#!/usr/bin/env python3
"""Safe delivery from an existing MP4 master: verify bytes, ZIP and optional Android MP4.
This does NOT control ChatGPT sandbox URLs or publish anything. No external APIs.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import zipfile


def run(args):
    return subprocess.run(args, check=True, text=True, capture_output=True).stdout


def inspect(path):
    data = json.loads(run(['ffprobe', '-v', 'error', '-show_entries',
        'format=duration,size:stream=codec_type,codec_name,width,height,pix_fmt',
        '-of', 'json', str(path)]))
    types = [s.get('codec_type') for s in data.get('streams', [])]
    if not {'video', 'audio'}.issubset(types) or 'subtitle' in types:
        raise ValueError('MP4 must contain video+audio without subtitles: ' + path.name)
    if float(data['format']['duration']) < 1:
        raise ValueError('MP4 duration invalid')
    return data


def decode(path):
    subprocess.run(['ffmpeg', '-nostdin', '-hide_banner', '-v', 'error', '-xerror',
                    '-i', str(path), '-f', 'null', '-'], check=True)


def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1048576), b''):
            h.update(chunk)
    return h.hexdigest()


def zip_only_video(source, out):
    with tempfile.NamedTemporaryFile(dir=out.parent, suffix='.zip', delete=False) as t:
        tmp = Path(t.name)
    try:
        with zipfile.ZipFile(tmp, 'w', compression=zipfile.ZIP_STORED, allowZip64=True) as z:
            z.write(source, source.name)
        with zipfile.ZipFile(tmp) as z:
            if z.namelist() != [source.name] or z.testzip() is not None:
                raise ValueError('ZIP integrity check failed')
            if hashlib.sha256(z.read(source.name)).hexdigest() != digest(source):
                raise ValueError('Master/ZIP SHA256 mismatch')
        os.replace(tmp, out)
    finally:
        tmp.unlink(missing_ok=True)
    return dict(filename=out.name, size_bytes=out.stat().st_size, sha256=digest(out))


def mobile_copy(source, target):
    stream = next(s for s in inspect(source)['streams'] if s['codec_type'] == 'video')
    filt = 'scale=480:854:flags=lanczos'
    if stream.get('pix_fmt') == 'yuvj420p':
        filt += ':in_range=pc:out_range=tv'
    filt += ',format=yuv420p'
    with tempfile.NamedTemporaryFile(dir=target.parent, suffix='.mp4', delete=False) as t:
        tmp = Path(t.name)
    try:
        run(['ffmpeg', '-nostdin', '-hide_banner', '-v', 'error', '-y',
             '-i', str(source), '-map', '0:v:0', '-map', '0:a:0', '-sn', '-dn',
             '-vf', filt, '-c:v', 'libx264', '-preset', 'veryfast', '-profile:v', 'main',
             '-level:v', '3.0', '-r', '24', '-b:v', '330k', '-maxrate', '480k',
             '-bufsize', '780k', '-c:a', 'aac', '-ac', '2', '-ar', '44100',
             '-b:a', '64k', '-movflags', '+faststart', '-map_metadata', '-1', str(tmp)])
        inspect(tmp)
        decode(tmp)
        os.replace(tmp, target)
    finally:
        tmp.unlink(missing_ok=True)


def deliver(master, outdir, android=False):
    master = master.resolve()
    if master.suffix.lower() != '.mp4' or not master.is_file():
        raise ValueError('Existing .mp4 master required')
    outdir.mkdir(parents=True, exist_ok=True)
    metadata = inspect(master)
    decode(master)
    report = {'schema': 'download-fallback-v36',
              'status': 'verified_locally_not_remote_link',
              'message': 'Checks file bytes, not ChatGPT-hosted sandbox link functionality.',
              'master': {'filename': master.name, 'bytes': master.stat().st_size,
                         'duration_seconds': float(metadata['format']['duration']),
                         'sha256': digest(master), 'untouched': True},
              'downloads': [], 'warnings': []}
    report['downloads'].append(zip_only_video(master, outdir / (master.stem + '_SOLO_VIDEO.zip')))
    if android:
        fallback = outdir / (master.stem + '_ANDROID_480p.mp4')
        try:
            mobile_copy(master, fallback)
            report['downloads'].append({'filename': fallback.name,
                                        'size_bytes': fallback.stat().st_size,
                                        'sha256': digest(fallback)})
            report['downloads'].append(zip_only_video(
                fallback, outdir / (fallback.stem + '_SOLO_VIDEO.zip')))
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            report['warnings'].append('Could not make lightweight MP4: ' + str(exc))
    (outdir / 'VERIFICA_DOWNLOAD.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--input', type=Path)
    mode.add_argument('--source-dir', type=Path,
                      help='Find exactly one TRA_LE_PAGINE_EP*.mp4')
    p.add_argument('--output-dir', required=True, type=Path)
    p.add_argument('--android', action='store_true',
                   help='On demand only: creates 480p MP4 and ZIP; uses extra CPU/storage')
    args = p.parse_args()
    if args.input:
        file = args.input
    else:
        matches = sorted(args.source_dir.glob('TRA_LE_PAGINE_EP*.mp4'))
        if len(matches) != 1:
            p.error('Expected a single master MP4, found ' + str(len(matches)))
        file = matches[0]
    result = deliver(file, args.output_dir, android=args.android)
    print(json.dumps({'master': result['master']['filename'],
                      'downloads': [f['filename'] for f in result['downloads']],
                      'warnings': result['warnings']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
