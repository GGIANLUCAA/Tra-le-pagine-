import hashlib
import io
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import Mock

import requests
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from artvision_image_acquisition import ImageStore, retry_after
from artvision_seed_image_archive import seed_bundle


class Response:
    def __init__(self, status=200, data=b'', headers=None, url='https://upload.wikimedia.org/a'):
        self.status_code = status
        self.data = data
        self.headers = headers or {'Content-Type': 'image/png'}
        self.url = url
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(str(self.status_code), response=self)
    def iter_content(self, size): yield self.data


class AcquisitionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        data = io.BytesIO()
        Image.new('RGB', (24, 32), 'red').save(data, format='PNG')
        self.data = data.getvalue()
        self.checks = dict(minimum=(20, 30), min_bytes=10)
        self.dest = self.root / 'out.jpg'
        self.get = Mock()
        self.sleep = Mock()
        self.store = ImageStore(self.root / 'cache', get=self.get, clock=lambda: 1000, sleep=self.sleep)
    def acquire(self, urls, **kwargs):
        return self.store.acquire('work-A', urls, self.dest, **self.checks, **kwargs)
    def test_reuse_without_network_and_source_preserved(self):
        self.get.return_value = Response(data=self.data)
        self.acquire(['https://museum.test/a'])
        self.get.reset_mock()
        self.dest.unlink()
        self.assertEqual(self.acquire([]), 'https://museum.test/a')
        self.get.assert_not_called()
        self.assertEqual(self.dest.read_bytes(), self.data)
    def test_corrupt_cache_reacquired(self):
        self.get.return_value = Response(data=self.data)
        self.acquire(['https://museum.test/a'])
        cached, _ = self.store.paths('work-A')
        cached.write_bytes(b'broken')
        self.acquire(['https://museum.test/a'])
        self.assertEqual(self.get.call_count, 2)
    def test_404_once_and_persisted_negative_cache(self):
        self.get.side_effect = [Response(404), Response(data=self.data)]
        self.acquire(['https://bad.test/a', 'https://bad.test/a', 'https://museum.test/a'])
        self.assertEqual(self.get.call_count, 2)
        second = ImageStore(self.root / 'cache', get=self.get, clock=lambda: 1001)
        with self.assertRaises(RuntimeError):
            second.acquire('work-B', ['https://bad.test/a'], self.dest, **self.checks)
        self.assertEqual(self.get.call_count, 2)
        self.sleep.assert_not_called()
    def test_429_skips_commons_family_then_independent_fallback(self):
        self.get.side_effect = [Response(429, headers={'Retry-After': '600'}), Response(data=self.data)]
        result = self.acquire(['https://upload.wikimedia.org/a', 'https://commons.wikimedia.org/redirect', 'https://museum.test/a'])
        self.assertEqual(result, 'https://museum.test/a')
        self.assertEqual(self.get.call_count, 2)
        self.assertEqual(self.store.failures['origin:wikimedia.org'], 1600)
        self.sleep.assert_not_called()
    def test_expired_cooldown_allows_request(self):
        self.store.failures['origin:museum.test'] = 999
        self.get.return_value = Response(data=self.data)
        self.acquire(['https://museum.test/a'])
        self.get.assert_called_once()
    def test_5xx_bounded_retry(self):
        self.get.side_effect = [Response(503), Response(data=self.data)]
        self.acquire(['https://museum.test/a'])
        self.assertEqual(self.get.call_count, 2)
        self.sleep.assert_called_once_with(2)
    def test_timeout_bounded_retry_then_fallback(self):
        self.get.side_effect = [requests.Timeout(), requests.Timeout(), Response(data=self.data)]
        self.acquire(['https://bad.test/a', 'https://museum.test/a'])
        self.assertEqual(self.get.call_count, 3)
    def test_html_rejected_without_retry(self):
        self.get.return_value = Response(data=b'<html>', headers={'Content-Type': 'text/html'})
        with self.assertRaises(RuntimeError): self.acquire(['https://museum.test/a'])
        self.get.assert_called_once()
        self.assertFalse(self.dest.exists())
    def test_wrong_hash_rejected(self):
        self.get.return_value = Response(data=self.data)
        with self.assertRaises(RuntimeError): self.acquire(['https://museum.test/a'], expected='0'*64)
        self.assertFalse(self.dest.exists())
    def test_wrong_dimensions_rejected(self):
        self.get.return_value = Response(data=self.data)
        with self.assertRaises(RuntimeError):
            self.store.acquire('A', ['https://museum.test/a'], self.dest, minimum=(100, 100), min_bytes=10)
    def test_identity_isolation(self):
        self.get.return_value = Response(data=self.data)
        self.acquire(['https://museum.test/a'])
        with self.assertRaises(RuntimeError):
            self.store.acquire('different-work', [], self.dest, **self.checks)
    def test_retry_after_http_date(self):
        self.assertEqual(retry_after('Thu, 01 Jan 1970 00:20:00 GMT', 1000), 200)
        self.assertEqual(retry_after(None, 1000), 300)
    def test_archive_wrong_identity_rejected_before_seed(self):
        bundle = self.root / 'bundle.zip'
        with zipfile.ZipFile(bundle, 'w') as z:
            z.writestr('SOURCES_AND_RIGHTS.md', 'Source file: other\n')
            z.writestr('ORIGINAL_ARTWORK.jpg', self.data)
        with self.assertRaises(ValueError):
            seed_bundle(bundle, {'source_page': 'correct'}, self.store)
    def test_archive_real_size_and_hash_checked(self):
        image = self.root / 'large.jpg'
        Image.effect_noise((1900, 1100), 80).convert('RGB').save(image, quality=95)
        checksum = hashlib.sha256(image.read_bytes()).hexdigest()
        bundle = self.root / 'bundle.zip'
        with zipfile.ZipFile(bundle, 'w') as z:
            z.writestr('SOURCES_AND_RIGHTS.md', f'Source file: work-A\nOriginal image successfully downloaded: https://museum.test/a\nImage SHA256: {checksum}\n')
            z.write(image, 'ORIGINAL_ARTWORK.jpg')
        seed_bundle(bundle, {'source_page': 'work-A', 'art_candidates': ['https://museum.test/a']}, self.store)
        self.acquire([])
        self.get.assert_not_called()

if __name__ == '__main__': unittest.main()

class BundledSimbergTests(unittest.TestCase):
    def test_production_adapter_uses_pinned_original_without_network(self):
        import importlib.util
        import os
        from unittest.mock import patch
        root = Path(__file__).resolve().parents[1]
        spec = importlib.util.spec_from_file_location('image_adapter_test', root / 'scripts/artvision_cinema_duo_v30.py')
        engine = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(engine)
        brief = next(iter(json.loads((root / 'config/artvision_autoproduction_20261024_2315.json').read_text())['subjects'].values()))
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {'ARTVISION_ASSET_CACHE': str(Path(tmp)/'cache')}), patch('requests.get', side_effect=AssertionError('Network not allowed')) as get:
            dest = Path(tmp) / 'original.jpg'
            self.assertEqual(engine.fetch_authentic_image(brief, dest), brief['local_image_source_url'])
            self.assertEqual(hashlib.sha256(dest.read_bytes()).hexdigest(), brief['image_sha256'])
            get.assert_not_called()
