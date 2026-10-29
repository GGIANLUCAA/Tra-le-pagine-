#!/usr/bin/env python3
"""Acquire exact Met Open Access painting + pinned CC BY recording for V55.

No rendering, network upload, paid API, social publishing or V25 approval.
The manifest records downloaded bytes; V13/V54 gates must still be run.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path
from PIL import Image

MET_API = 'https://collectionapi.metmuseum.org/public/collection/v1/objects/'
MUSIC_URL = 'https://incompetech.com/music/royalty-free/mp3-royaltyfree/Water%20Lily.mp3'
MUSIC_PAGE = 'https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1400035'
MUSIC_SHA256 = 'b8c4f3b03a50af34c01a3f3b986a3d411f56a6c0c9a5b00807ccb5d83c74e8c6'
USER_AGENT = 'ArtVision/55 (authentic museum Open Access image; no paid API)'


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1048576), b''):
            h.update(chunk)
    return h.hexdigest()


def allowed(url, hosts):
    u = urllib.parse.urlsplit(url)
    return u.scheme == 'https' and u.hostname in hosts and not u.username and not u.password and u.port in (None, 443)


def fetch_json(url, opener=urllib.request.urlopen):
    if not allowed(url, {'collectionapi.metmuseum.org'}):
        raise ValueError('Museum metadata URL is not the official Met API')
    request = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    with opener(request, timeout=45) as response:
        if response.status != 200:
            raise ValueError('Met API HTTP status '+str(response.status))
        payload = response.read(1_000_001)
        if len(payload) > 1_000_000:
            raise ValueError('Met metadata too large')
    return json.loads(payload)


def download(url, destination, hosts, max_bytes, opener=urllib.request.urlopen):
    if not allowed(url, hosts):
        raise ValueError('Unexpected asset origin; refuse redirects or unknown hosts')
    destination = Path(destination)
    if destination.exists():
        raise FileExistsError('Refuse overwrite: '+str(destination))
    request = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    temp = None
    try:
        with opener(request, timeout=90) as response:
            final_url = response.geturl()
            if response.status != 200 or not allowed(final_url, hosts):
                raise ValueError('HTTP status/redirect origin not permitted')
            with tempfile.NamedTemporaryFile(dir=destination.parent, prefix='.artvision-', delete=False) as output:
                temp = Path(output.name)
                count = 0
                while True:
                    chunk = response.read(1048576)
                    if not chunk:
                        break
                    count += len(chunk)
                    if count > max_bytes:
                        raise ValueError('Asset exceeds maximum permitted bytes')
                    output.write(chunk)
        if count < 100_000:
            raise ValueError('Downloaded file is unexpectedly small')
        os.replace(temp, destination)
        temp = None
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)
    return destination


def prepare(object_id, destination, *, expected_title, expected_artist, metadata=None, fetcher=download):
    """Fail-closed acquisition, no preflight or artistic approval implied."""
    if type(object_id) is not int or object_id <= 0:
        raise ValueError('Positive Met object ID required')
    if not expected_title.strip() or not expected_artist.strip():
        raise ValueError('Exact title and artist required')
    destination = Path(destination).resolve()
    if destination.exists():
        raise FileExistsError('Refuse existing output directory: '+str(destination))
    meta = metadata if metadata is not None else fetch_json(MET_API+str(object_id))
    if meta.get('objectID') != object_id or meta.get('isPublicDomain') is not True:
        raise ValueError('Met object identity / public-domain gate failed')
    if meta.get('title', '').strip().casefold() != expected_title.strip().casefold():
        raise ValueError('Met title differs; verify exact work before acquisition')
    if expected_artist.casefold() not in meta.get('artistDisplayName', '').casefold():
        raise ValueError('Met artist differs; verify attribution')
    art_url = meta.get('primaryImage')
    if not isinstance(art_url, str) or not allowed(art_url, {'images.metmuseum.org', 'collectionapi.metmuseum.org'}):
        raise ValueError('Missing/non-official Met original primaryImage')
    destination.mkdir(parents=True)
    art = fetcher(art_url, destination/'met_original.jpg', {'images.metmuseum.org', 'collectionapi.metmuseum.org'}, 40_000_000)
    with Image.open(art) as im:
        im.verify()
    with Image.open(art) as im:
        width, height = im.size
    if min(width, height) < 900:
        raise ValueError('Met original has insufficient resolution for 9:16 detail crops')
    music = fetcher(MUSIC_URL, destination/'water_lily_original.mp3', {'incompetech.com'}, 12_000_000)
    music_hash = digest(music)
    if music_hash != MUSIC_SHA256:
        raise ValueError('Music bytes differ from documented licensed recording')
    record = {
        'schema': 'artvision-met-prepared-assets-v55-v1', 'status': 'assets_verified_only',
        'object_id': object_id, 'museum_record': f'https://www.metmuseum.org/art/collection/search/{object_id}',
        'met_api': MET_API+str(object_id), 'title': meta['title'], 'artist': meta['artistDisplayName'],
        'object_date': meta.get('objectDate'), 'dimensions_text': meta.get('dimensions'),
        'artwork': {'file': art.name, 'source_url': art_url, 'sha256': digest(art),
                    'width_px': width, 'height_px': height, 'rights': 'Met isPublicDomain=true / Open Access'},
        'music': {'file': music.name, 'source_url': MUSIC_URL, 'recording_page': MUSIC_PAGE,
                  'sha256': music_hash, 'license': 'CC BY 4.0',
                  'license_url': 'https://creativecommons.org/licenses/by/4.0/',
                  'attribution': 'Water Lily — Kevin MacLeod'},
        'prerender_gates': ['V32 three-subject comparison', 'V54 four-variant dossier',
                            'V13 source/rights and scene preflight', 'V55 artwork-specific shot plan'],
        'artistic_approval': False, 'v25_approved': False, 'rendered_mp4': False,
        'paid_api_calls': 0
    }
    (destination/'PREPARED_ASSETS_V55.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--met-object-id', type=int, required=True)
    parser.add_argument('--title', required=True)
    parser.add_argument('--artist', required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.met_object_id, args.out, expected_title=args.title,
                             expected_artist=args.artist), indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
