"""Verified byte reuse and bounded image acquisition (no authenticity/rights inference)."""
import hashlib
import json
import os
import shutil
import time
from datetime import timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlsplit

import requests
from PIL import Image


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(524288), b''):
            h.update(block)
    return h.hexdigest()


def origin(url):
    host = (urlsplit(url).hostname or '').lower()
    if host == 'wikimedia.org' or host.endswith('.wikimedia.org'):
        return 'wikimedia.org'
    if host in ('wsrv.nl', 'images.weserv.nl'):
        return 'weserv.nl'
    return host


def validate(path, minimum=(1000, 1850), min_bytes=200000, ordered=False, expected=None):
    if Path(path).stat().st_size < min_bytes:
        raise ValueError('image too small in bytes')
    with Image.open(path) as im:
        im.verify()
    with Image.open(path) as im:
        im.load()
        dimensions = im.size
    measured = dimensions if ordered else tuple(sorted(dimensions))
    if any(a < b for a, b in zip(measured, minimum)):
        raise ValueError('image resolution below required minimum')
    checksum = digest(path)
    if expected and checksum != expected:
        raise ValueError('image SHA256 mismatch')
    return dimensions, checksum


def retry_after(value, now):
    try:
        return max(1, float(value))
    except (TypeError, ValueError):
        try:
            dt = parsedate_to_datetime(value)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return max(1, dt.timestamp() - now)
        except (TypeError, ValueError, OverflowError):
            return 300


class ImageStore:
    def __init__(self, root=None, get=None, clock=None, sleep=None):
        self.root = Path(root or os.environ.get('ARTVISION_ASSET_CACHE', '.artvision-assets'))
        self.root.mkdir(parents=True, exist_ok=True)
        self.get = get or requests.get
        self.clock = clock or time.time
        self.sleep = sleep or time.sleep
        try:
            self.failures = json.loads((self.root / 'failures.json').read_text())
        except (OSError, ValueError):
            self.failures = {}

    def paths(self, identity):
        key = hashlib.sha256(identity.encode()).hexdigest()
        return self.root / (key + '.jpg'), self.root / (key + '.json')

    def block(self, key, seconds):
        self.failures[key] = self.clock() + seconds
        self._json(self.root / 'failures.json', self.failures)

    @staticmethod
    def _json(path, data):
        tmp = path.with_suffix('.json.tmp')
        tmp.write_text(json.dumps(data, indent=2) + '\n')
        tmp.replace(path)

    def seed(self, identity, image, source_url, expected, **checks):
        dimensions, checksum = validate(image, expected=expected, **checks)
        cached, manifest = self.paths(identity)
        tmp = cached.with_suffix('.part')
        shutil.copyfile(image, tmp)
        tmp.replace(cached)
        self._json(manifest, dict(identity=identity, source_url=source_url,
                                 sha256=checksum, dimensions=dimensions,
                                 validation='byte_integrity_only_not_rights_approval'))

    def acquire(self, identity, urls, destination, expected=None, **checks):
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        cached, manifest = self.paths(identity)
        errors = []
        try:
            meta = json.loads(manifest.read_text())
            if meta['identity'] != identity or not meta.get('sha256') or not meta.get('source_url'):
                raise ValueError('invalid cached provenance')
            validate(cached, expected=expected or meta['sha256'], **checks)
            if digest(cached) != meta['sha256']:
                raise ValueError('cached manifest mismatch')
            shutil.copyfile(cached, destination)
            print('IMAGE_CACHE_OK', identity, meta['source_url'], meta['sha256'], flush=True)
            return meta['source_url']
        except (OSError, ValueError, KeyError):
            pass
        for url in dict.fromkeys(urls):
            group = origin(url)
            if any(self.failures.get(k, 0) > self.clock() for k in ('url:' + url, 'origin:' + group)):
                errors.append(url + ': cooldown; no request')
                print('IMAGE_SKIP_COOLDOWN', url, flush=True)
                continue
            tmp = destination.with_suffix('.download.part')
            for attempt in range(2):
                try:
                    with self.get(url, headers={'User-Agent': 'ArtVisionAssetStore/1.0 (github.com/GGIANLUCAA/Tra-le-pagine-)'},
                                  timeout=(15, 72), stream=True, allow_redirects=True) as response:
                        status = response.status_code
                        if status == 429:
                            delay = retry_after(response.headers.get('Retry-After'), self.clock())
                            self.block('origin:' + group, delay)
                            self.block('origin:' + origin(response.url), delay)
                        elif 400 <= status < 500:
                            self.block('url:' + url, 86400)
                        response.raise_for_status()
                        if not response.headers.get('Content-Type', '').lower().startswith('image/'):
                            raise ValueError('response is not image MIME')
                        total = 0
                        with tmp.open('wb') as out:
                            for chunk in response.iter_content(524288):
                                total += len(chunk)
                                if total > 100 * 1024 * 1024:
                                    raise ValueError('image exceeds 100 MiB limit')
                                out.write(chunk)
                    dimensions, checksum = validate(tmp, expected=expected, **checks)
                    self.seed(identity, tmp, url, checksum, **checks)
                    tmp.replace(destination)
                    print('AUTHENTIC_IMAGE_OK', url, dimensions, checksum, flush=True)
                    return url
                except (requests.RequestException, ValueError, OSError) as exc:
                    errors.append(url + ': ' + str(exc))
                    print('IMAGE_FETCH_FAILED', url, type(exc).__name__, str(exc), flush=True)
                    response = getattr(exc, 'response', None)
                    transient = isinstance(exc, (requests.Timeout, requests.ConnectionError)) or (
                        response is not None and response.status_code >= 500)
                    if not transient or attempt == 1:
                        break
                    self.sleep(2)
                finally:
                    tmp.unlink(missing_ok=True)
        raise RuntimeError('NO_VERIFIED_ORIGINAL_IMAGE: ' + ' | '.join(errors))
