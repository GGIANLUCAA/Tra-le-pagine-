"""V189 free offline QA on synthetic encoded film bytes, no provider and no rights claims."""
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

SRC = Path(__file__).resolve().parents[1] / 'src'
sys.path.insert(0, str(SRC))
# Repository CI has real source modules. Local isolated checks can use minimal
# compatible fixture modules, without changing the code shipped to GitHub.
if not (SRC / 'storia_rivive_v188_portrait_audit.py').exists():
    v188 = types.ModuleType('storia_rivive_v188_portrait_audit')
    v188.EXPECTED_FILM_SHA = 'eacbb947105f9143632e3d4e933ee5e200ba98f5d588c11c552dfb94787de1d9'
    v188.verify_zip = lambda p: ([], {})
    v188.geometry = lambda w, h: {'width':603,'height':1072,'y':4,
                                 'x_offsets':{'left':0,'center':416,'right':833}}
    sys.modules[v188.__name__] = v188
if not (SRC / 'storia_rivive_v184_source_intake.py').exists():
    v184 = types.ModuleType('storia_rivive_v184_source_intake')
    v184.inspect_local = lambda path, h: {'status':'ASSETS_PENDING', 'source_sha256':h}
    sys.modules[v184.__name__] = v184

import storia_rivive_v189_real_motion_proof as v189


def fake_rows():
    entries = []
    for (name, pos, label), index in zip(v189.SELECTED, range(5)):
        sample = (index + 1) * 14.0
        entries.append({'png_filename': name, 'png_sha256': ('a' * 64),
                        'sample_seconds': sample, 'interval_start_seconds': sample - 6.0,
                        'interval_end_seconds': sample + 5.0,
                        'shot_interval_index': index})
    return entries


class V189Tests(unittest.TestCase):
    def test_real_catalog_preselection_requires_five_distinct_intervals(self):
        rows = fake_rows()
        with patch.object(v189, 'verify_zip', return_value=([(r, b'png') for r in rows], {})):
            r, _ = v189.check_plan('fake.zip')
        self.assertEqual([x['png_filename'] for x in r], [a[0] for a in v189.SELECTED])
        self.assertEqual(len(set(x['shot_interval_index'] for x in r)), 5)

    def test_missing_one_original_frame_refused(self):
        rows = fake_rows()[:4]
        with patch.object(v189, 'verify_zip', return_value=([(r, b'png') for r in rows], {})):
            with self.assertRaisesRegex(ValueError, 'SELECTED_SOURCE_FRAME_MISSING'):
                v189.check_plan('fake.zip')

    def test_duplicate_cut_interval_refused(self):
        rows = fake_rows()
        rows[4]['shot_interval_index'] = 3
        with patch.object(v189, 'verify_zip', return_value=([(r, b'png') for r in rows], {})):
            with self.assertRaisesRegex(ValueError, 'DUPLICATED_CUT_INTERVAL'):
                v189.check_plan('fake.zip')

    def test_near_cut_anchor_rejected(self):
        rows = fake_rows()
        rows[2]['interval_start_seconds'] = rows[2]['sample_seconds'] - .1
        with patch.object(v189, 'verify_zip', return_value=([(r, b'png') for r in rows], {})):
            with self.assertRaisesRegex(ValueError, 'SOURCE_ANCHOR_TOO_CLOSE_TO_CUT'):
                v189.check_plan('fake.zip')

    def test_motion_metric_rejects_static_real_frames(self):
        with tempfile.TemporaryDirectory() as temp:
            movie = Path(temp) / 'still.mp4'
            subprocess.run(['ffmpeg','-loglevel','error','-y','-f','lavfi','-i',
                            'color=c=gray:s=720x1280:r=25','-t','3','-c:v',
                            'libx264','-preset','ultrafast',str(movie)],
                           check=True, timeout=100)
            score = v189.grayscale_motion_metric(movie)
            self.assertEqual(score['mean_luma_delta'], 0)

    def test_real_synthetic_motion_encode_and_last_frame_freeze_sha(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / 'real-synthetic-moving-film.mp4'
            subprocess.run(['ffmpeg','-loglevel','error','-y','-f','lavfi',
                            '-i','testsrc2=s=1436x1080:r=25','-t','5',
                            '-c:v','libx264','-preset','ultrafast',
                            '-pix_fmt','yuv420p',str(source)],
                           check=True, timeout=120)
            out = root / 'proof';out.mkdir()
            row = {'png_filename':'shot_03.png','png_sha256':'a'*64,
                   'sample_seconds':3.5,'interval_start_seconds':0.0,
                   'interval_end_seconds':5.0, 'crop_position':'left',
                   'editorial_label':'test-real-synthetic-motion'}
            rendered = v189.render_scene(source, row, 1, out)
            clip = out / rendered['motion_mp4']
            freeze = out / rendered['freeze_png']
            self.assertTrue(freeze.exists())
            self.assertEqual(v189.sha(clip), rendered['motion_mp4_sha256'])
            self.assertEqual(v189.sha(freeze), rendered['exact_last_decoded_frame_sha256'])
            self.assertGreater(rendered['motion']['mean_luma_delta'], .08)
            self.assertTrue(rendered['freeze_from_last_encoded_motion_frame'])
            self.assertFalse(rendered.get('four_i2i_completed', False))

    def test_source_gate_never_accepts_wrong_hash_even_with_archive(self):
        rows = fake_rows()
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / 'output'
            with patch.object(v189, 'check_plan', return_value=(rows, {'source_page':'a'})), \
                 patch.object(v189, 'inspect_local', return_value={'status':'ASSETS_PENDING'}):
                with self.assertRaisesRegex(ValueError, 'SOURCE_SHA_OR_RESOLUTION_INVALID'):
                    v189.produce('film.webm', '0'*64, 'v187.zip', out)
            self.assertFalse(out.exists())


if __name__ == '__main__':
    unittest.main()
