"""V188: archive integrity, no-upscale geometry, and real decoded PNG tests."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import storia_rivive_v188_portrait_audit as v188


class V188Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.zip = self.root / 'v187.zip'
        self.out = self.root / 'crops'
        self.candidates = []
        self.frames = {}
        for i, color in enumerate(['red', 'green', 'yellow', 'cyan', 'white'], 1):
            p = self.root / f'shot_{i:02}.png'
            subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'lavfi',
                            '-i', f'color=c={color}:s=1436x1080:r=1',
                            '-frames:v', '1', str(p)], check=True, timeout=30)
            data = p.read_bytes()
            self.frames[f'shot_catalog/shot_{i:02}.png'] = data
            self.candidates.append({'png_filename': p.name,
                                    'png_sha256': hashlib.sha256(data).hexdigest(),
                                    'sample_seconds': i * 12.5})
        self.provenance = {'sha256': v188.EXPECTED_FILM_SHA, 'native_scan': False,
                           'provider_jobs_may_start': False,
                           'source_page': 'https://commons.wikimedia.org/test'}
        self.catalog = {'source_sha256': v188.EXPECTED_FILM_SHA,
                        'status': 'DIVERSE_CUT_CANDIDATES_NEED_VISUAL_REVIEW',
                        'candidates': self.candidates}
        self.write_zip()

    def write_zip(self, extras=None):
        with zipfile.ZipFile(self.zip, 'w', compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr('SOURCE_PROVENANCE.json', json.dumps(self.provenance))
            z.writestr('shot_catalog/V187_SHOT_CATALOG.json', json.dumps(self.catalog))
            for name, data in self.frames.items():
                z.writestr(name, data)
            for name, data in extras or []:
                z.writestr(name, data)

    def test_9_16_native_geometry_no_upscale(self):
        g = v188.geometry(1436, 1080)
        self.assertEqual((g['width'], g['height']), (603, 1072))
        self.assertEqual(g['width'] * 16, g['height'] * 9)
        self.assertEqual(g['x_offsets'], {'left': 0, 'center': 416, 'right': 833})

    def test_full_synthetic_png_archive_produces_real_crops_without_approval(self):
        r = v188.audit(self.zip, self.out)
        self.assertEqual(len(r['candidates']), 5)
        self.assertFalse(r['provider_jobs_may_start'])
        self.assertFalse(r['publish_permitted'])
        self.assertFalse(r['five_distinct_shots_verified'])
        self.assertEqual(sum(len(c['crops']) for c in r['candidates']), 15)
        for c in r['candidates']:
            self.assertEqual(c['source_crop_pixels'], [603, 1072])
            self.assertTrue(c['crop_width_below_720px'])
            for crop in c['crops']:
                p = self.out / crop['filename']
                self.assertEqual(v188.probe_png(p), (603, 1072))
                self.assertEqual(v188.sha256(p.read_bytes()), crop['sha256'])
        self.assertTrue((self.out / 'V188_PORTRAIT_AUDIT.json').exists())

    def test_hash_mismatch_fails_before_output_creation(self):
        self.catalog['candidates'][0]['png_sha256'] = '0' * 64
        self.write_zip()
        with self.assertRaisesRegex(ValueError, 'PNG_SHA_MISMATCH'):
            v188.audit(self.zip, self.out)
        self.assertFalse(self.out.exists())

    def test_wrong_film_sha_fails_closed(self):
        self.provenance['sha256'] = '1' * 64
        self.write_zip()
        with self.assertRaisesRegex(ValueError, 'UNTRUSTED_SOURCE_PROVENANCE'):
            v188.audit(self.zip, self.out)

    def test_zip_traversal_rejected(self):
        self.write_zip(extras=[('../outside.txt', b'bad')])
        with self.assertRaisesRegex(ValueError, 'UNSAFE_ZIP_MEMBER'):
            v188.verify_zip(self.zip)

    def test_duplicate_zip_member_rejected(self):
        self.write_zip(extras=[('shot_catalog/shot_01.png', b'bad')])
        with self.assertRaisesRegex(ValueError, 'DUPLICATE_OR_EXCESS_MEMBERS'):
            v188.verify_zip(self.zip)

    def test_existing_output_not_overwritten(self):
        self.out.mkdir()
        (self.out / 'keep').write_text('original')
        with self.assertRaisesRegex(ValueError, 'OUTPUT_EXISTS'):
            v188.audit(self.zip, self.out)
        self.assertEqual((self.out / 'keep').read_text(), 'original')

    def test_black_intertitle_rejected_without_fake_crop(self):
        black = self.root / 'black.png'
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'lavfi',
                        '-i', 'color=c=black:s=1436x1080:r=1',
                        '-frames:v', '1', str(black)], check=True, timeout=30)
        data = black.read_bytes()
        self.frames['shot_catalog/shot_05.png'] = data
        self.catalog['candidates'][4]['png_sha256'] = v188.sha256(data)
        self.write_zip()
        r = v188.audit(self.zip, self.out)
        self.assertTrue(r['candidates'][4]['dark_or_intertitle_like'])
        self.assertEqual(r['candidates'][4]['crops'], [])
        self.assertFalse(r['human_visual_qa_approved'])


if __name__ == '__main__':
    unittest.main()
