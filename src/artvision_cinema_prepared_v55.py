#!/usr/bin/env python3
"""Offline Cinema Standard renderer for prepared, rights-reviewed ArtVision assets.

No downloads, provider calls, synthetic artwork, museum reconstruction, voice,
release approval or social publication. V13/V54 gates remain in the V16 adapter.
"""
from __future__ import annotations
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

SCHEMA = 'artvision-cinema-prepared-v55-v1'
W, H, FPS = 1080, 1920, 24
ALLOWED_LICENSES = {'CC0', 'CC BY 4.0', 'Public Domain'}


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def safe_file(folder, relative):
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ValueError('Prepared asset path must be relative')
    path = (folder / relative).resolve()
    if not path.is_relative_to(folder.resolve()) or not path.is_file() or path.is_symlink():
        raise ValueError('Missing/unsafe prepared asset: ' + relative)
    return path


def validate(plan, assets_dir, approved_assets):
    """Fail closed: local originals, exact hashes, provenance and distinct storyboard."""
    if plan.get('schema') != SCHEMA or plan.get('variant') != 'cinema_standard':
        raise ValueError('Only Cinema Standard prepared V55 is supported; no fake Museum')
    if not isinstance(plan.get('title'), str) or len(plan['title'].strip()) < 4:
        raise ValueError('Exact English artwork title required')
    if not isinstance(plan.get('artist'), str) or len(plan['artist'].strip()) < 4:
        raise ValueError('Artist name required')
    music = plan.get('music')
    if not isinstance(music, dict) or music.get('license') not in ALLOWED_LICENSES:
        raise ValueError('Recording license missing or unsupported')
    for field in ('recording_title', 'recording_artist', 'source_url', 'license_url'):
        value = music.get(field)
        if not isinstance(value, str) or len(value.strip()) < 3:
            raise ValueError('Recording attribution incomplete: ' + field)
        if field.endswith('_url') and not value.startswith('https://'):
            raise ValueError('Recording source and license must use HTTPS')
    def check_asset(rec):
        if not isinstance(rec, dict):
            raise ValueError('Invalid asset record')
        path = safe_file(assets_dir, rec.get('file'))
        if path not in approved_assets:
            raise ValueError('Asset not in V13 preflight: ' + rec['file'])
        expected = rec.get('sha256')
        if not isinstance(expected, str) or not re.fullmatch('[a-f0-9]{64}', expected) or sha256(path) != expected:
            raise ValueError('Asset SHA256 mismatch: ' + rec['file'])
        return path
    music_path = check_asset(music)
    if music_path.suffix.lower() not in ('.mp3', '.wav', '.flac', '.ogg'):
        raise ValueError('Audio file type not supported')
    shots = plan.get('shots')
    if not isinstance(shots, list) or len(shots) < 4 or len(shots) > 24:
        raise ValueError('Four to twenty-four purposeful shots required')
    details, previous, resolved = set(), None, []
    for shot in shots:
        if not isinstance(shot, dict):
            raise ValueError('Invalid shot')
        path = check_asset(shot)
        if path.suffix.lower() not in ('.jpg', '.jpeg', '.png', '.webp'):
            raise ValueError('Authentic raster painting required')
        seconds = shot.get('duration_seconds')
        if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) or not math.isfinite(seconds) or not 1.5 <= seconds <= 12:
            raise ValueError('Invalid shot duration')
        if shot.get('mode') not in ('detail', 'whole'):
            raise ValueError('Unsupported shot mode')
        focus = shot.get('focus')
        if not isinstance(focus, list) or len(focus) != 2 or any(type(x) not in (int, float) or not math.isfinite(x) or not 0.05 <= x <= 0.95 for x in focus):
            raise ValueError('Normalized semantic focus required')
        if not isinstance(shot.get('purpose'), str) or len(shot['purpose'].strip()) < 25:
            raise ValueError('Each shot needs a meaningful editorial purpose')
        detail = shot.get('detail_id')
        if not isinstance(detail, str) or len(detail.strip()) < 3:
            raise ValueError('Authentic artwork detail ID required')
        identity = (path, shot['mode'], tuple(round(x, 2) for x in focus))
        if identity == previous:
            raise ValueError('Consecutive duplicate shot')
        previous = identity
        if shot['mode'] == 'detail':
            details.add(detail)
        resolved.append((shot, path))
    if len(details) < 3 or shots[0]['mode'] != 'detail' or shots[-1]['mode'] != 'whole':
        raise ValueError('Three specific details, opening hook and final whole artwork required')
    if sum(s['duration_seconds'] for s in shots) > 180:
        raise ValueError('Unmotivated excessive duration')
    return music_path, resolved


def font(size, serif=False):
    file = '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf' if serif else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    return ImageFont.truetype(file, size)


def shot_image(source, shot, title, artist, opening):
    with Image.open(source) as original:
        art = ImageOps.exif_transpose(original).convert('RGB')
    iw, ih = art.size
    if min(iw, ih) < 600:
        raise ValueError('Source artwork too small for a quality crop')
    if shot['mode'] == 'whole':
        canvas = Image.new('RGB', (W, H), '#15191c')
        art.thumbnail((int(W * .94), int(H * .76)), Image.Resampling.LANCZOS)
        canvas.paste(art, ((W-art.width)//2, (H-art.height)//2))
    else:
        # Crop only authentic pixels; never edge-stretch or hallucinate borders.
        target_ratio = W/H
        if iw/ih > target_ratio:
            crop_h, crop_w = ih, int(ih*target_ratio)
        else:
            crop_w, crop_h = iw, int(iw/target_ratio)
        fx, fy = shot['focus']
        left = max(0, min(iw-crop_w, round(fx*iw-crop_w/2)))
        top = max(0, min(ih-crop_h, round(fy*ih-crop_h/2)))
        canvas = art.crop((left, top, left+crop_w, top+crop_h)).resize((W, H), Image.Resampling.LANCZOS)
    if opening:
        # Fixed cover identity on the first 3+ seconds; no text over later scenes.
        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        d.rounded_rectangle((55, H-490, W-55, H-170), radius=22, fill=(8, 11, 15, 226))
        title_font = font(50, True)
        while d.textbbox((0,0), title, font=title_font)[2] > W-150 and title_font.size > 28:
            title_font = font(title_font.size-2, True)
        if d.textbbox((0,0), title, font=title_font)[2] > W-150:
            raise ValueError('Exact English title too long for single-line layout; adapt cover manually')
        artist_font = font(30)
        while d.textbbox((0,0), artist, font=artist_font)[2] > W-160 and artist_font.size > 20:
            artist_font = font(artist_font.size-2)
        if d.textbbox((0,0), artist, font=artist_font)[2] > W-160:
            raise ValueError('Artist too long for approved layout')
        d.text((W//2, H-385), title, anchor='mm', font=title_font, fill='#f7f3e9')
        d.line((130, H-310, W-130, H-310), fill='#bda980', width=3)
        d.text((W//2, H-250), artist.upper(), anchor='mm', font=artist_font, fill='#f0e6d2')
        canvas = Image.alpha_composite(canvas.convert('RGBA'), layer).convert('RGB')
    return canvas


def render(plan, assets_dir, approved_assets, out):
    assets_dir, out = Path(assets_dir).resolve(), Path(out).resolve()
    music, shots = validate(plan, assets_dir, approved_assets)
    out.mkdir(parents=True, exist_ok=True)
    slug = re.sub('[^A-Z0-9]+', '_', plan['artist'].upper()).strip('_')[:36]
    video = out / ('ARTVISION_' + slug + '_CINEMA_STANDARD_V55_REVIEW.mp4')
    if video.exists():
        raise ValueError('Original MP4 exists; never overwrite or simulate a new variant')
    stills = out / 'PREPARED_SHOTS_V55'
    if stills.exists():
        raise ValueError('Prepared shots directory already exists; use fresh output')
    stills.mkdir()
    durations = []
    for i, (shot, source) in enumerate(shots):
        image = shot_image(source, shot, plan['title'], plan['artist'], opening=(i == 0))
        image.save(stills / f'{i:02d}.jpg', quality=94, subsampling=0)
        durations.append(round(float(shot['duration_seconds'])*FPS)/FPS)
    (out/'COPERTINA.jpg').write_bytes((stills/'00.jpg').read_bytes())
    command = ['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-y']
    for i, duration in enumerate(durations):
        command += ['-loop','1','-framerate',str(FPS),'-t',str(duration),'-i',str(stills/f'{i:02d}.jpg')]
    command += ['-stream_loop','-1','-i',str(music)]
    filters = []
    for i, duration in enumerate(durations):
        filters.append(f'[{i}:v]zoompan=z=\'min(zoom+0.00009,1.035)\':d=1:fps={FPS}:s={W}x{H},trim=duration={duration},setpts=PTS-STARTPTS[v{i}]')
    filters.append(''.join(f'[v{i}]' for i in range(len(shots)))+f'concat=n={len(shots)}:v=1:a=0[v]')
    total = sum(durations)
    fade_out = max(0, total-1.8)
    command += ['-filter_complex',';'.join(filters),'-map','[v]','-map',f'{len(shots)}:a:0',
                '-t',str(total),'-r',str(FPS),'-c:v','libx264','-preset','veryfast','-crf','21',
                '-pix_fmt','yuv420p','-c:a','aac','-b:a','160k',
                '-af',f'afade=t=in:st=0:d=0.4,afade=t=out:st={fade_out}:d=1.8',
                '-movflags','+faststart',str(video)]
    subprocess.run(command, check=True, timeout=1200)
    (out/'STORYBOARD_CINEMA_V55.json').write_text(json.dumps({
        'schema':SCHEMA,'variant':'cinema_standard','title':plan['title'],
        'artist':plan['artist'],'shots':plan['shots'],
        'music':plan['music'],'video_sha256':sha256(video),
        'review_state':'rendered_needs_review',
        'notes':'Technical render only; no artistic review, approval or archive upload.'
    }, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return video, out/'COPERTINA.jpg'
