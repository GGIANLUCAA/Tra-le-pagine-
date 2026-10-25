#!/usr/bin/env python3
"""Import exact original bytes from a trusted successful production ZIP, never extractall."""
import argparse
import json
import re
import sys
import tempfile
import zipfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from artvision_image_acquisition import ImageStore


def seed_bundle(bundle, brief, store):
    with zipfile.ZipFile(bundle) as archive:
        rights_info = archive.getinfo('SOURCES_AND_RIGHTS.md')
        image_info = archive.getinfo('ORIGINAL_ARTWORK.jpg')
        if rights_info.file_size > 1000000 or image_info.file_size > 100 * 1024 * 1024:
            raise ValueError('oversized archive member')
        rights = archive.read(rights_info).decode('utf-8')
        source = re.search(r'^Source file: (.+)$', rights, re.M)
        image_url = re.search(r'^Original image successfully downloaded: (.+)$', rights, re.M)
        checksum = re.search(r'^Image SHA256: ([0-9a-f]{64})$', rights, re.M)
        if not source or source[1].strip() != brief['source_page']:
            raise ValueError('archive belongs to a different artwork')
        if not image_url or image_url[1].strip() not in brief['art_candidates'] or not checksum:
            raise ValueError('archive source/hash missing or not configured')
        with tempfile.TemporaryDirectory() as tmp:
            image = Path(tmp) / 'original.jpg'
            image.write_bytes(archive.read(image_info))
            store.seed(brief['source_page'], image, image_url[1].strip(), checksum[1])
    print('ARCHIVE_IMAGE_VERIFIED', brief['source_page'], checksum[1])


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--archive-dir', required=True)
    ap.add_argument('--config', required=True)
    ap.add_argument('--painting', required=True)
    args = ap.parse_args()
    brief = json.loads(Path(args.config).read_text())['subjects'][args.painting]
    bundles = list(Path(args.archive_dir).rglob('*COMPLETE.zip'))
    if len(bundles) != 1:
        raise SystemExit('Expected one trusted production bundle')
    seed_bundle(bundles[0], brief, ImageStore())
