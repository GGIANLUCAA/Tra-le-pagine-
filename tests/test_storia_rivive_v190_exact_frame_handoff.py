"""V190: byte-real FFmpeg regressions, no network, no provider or credit use."""
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import storia_rivive_v190_exact_frame_handoff as v190


def run(*args):
    subprocess.run(['ffmpeg', '-hide_banner', '-nostdin', '-loglevel', 'error', '-y',
                    *map(str, args)], check=True, timeout=90)


def fixture(root):
    scenes = []
    for i in range(1, 6):
        name = f'{i:02d}_test-{i}'
        clip = root / (name + '_real_film_bw.mp4')
        freeze = root / (name + '_last_real_film_frame.png')
        run('-f', 'lavfi', '-i', f'testsrc2=s=320x240:r=25,eq=brightness={i / 100}',
            '-t', '1.2', '-an', '-c:v', 'libx264', '-preset', 'ultrafast',
            '-pix_fmt', 'yuv420p', clip)
        run('-i', clip, '-vf', 'select=eq(n\\,29)', '-vsync', '0', '-frames:v', '1', freeze)
        scenes.append({
            'index': i, 'label': name, 'v187_png': f'shot_{i:02d}.png',
            'v187_sha256': hashlib.sha256(f'shot-{i}'.encode()).hexdigest(),
            'v187_interval': [i * 10, i * 10 + 5],
            'v187_sample_seconds': i * 10 + 3,
            'motion_mp4': clip.name, 'motion_mp4_sha256': v190.sha(clip),
            'freeze_png': freeze.name, 'exact_last_decoded_frame_sha256': v190.sha(freeze),
            'source_crop_px': [250, 240],
            'freeze_from_last_encoded_motion_frame': True,
            'v187_png_is_not_the_frozen_frame': True,
        })
    report = {
        'version': 'V189', 'status': 'REAL_BW_MOTION_PROOF_REVIEW_ONLY',
        'four_real_i2i': 0, 'real_vidu_clips': 0, 'publish_permitted': False,
        'rights_italy_verified': False, 'provider_jobs_may_start': False,
        'source_sha256': 'a' * 64, 'source_page': 'https://commons.wikimedia.org/wiki/File:Example',
        'source_kind': 'WIKIMEDIA_COMPRESSED_DERIVATIVE_NOT_NATIVE_SCAN',
        'scenes': scenes,
    }
    return report


class V190Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)
        cls.report = fixture(cls.root)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_exact_last_decoded_frames_five_real_encoded_clips(self):
        data = v190.build(self.report, self.root, expected_dimensions=(320, 240))
        self.assertEqual(len(data['source_frames']), 5)
        self.assertEqual(len(data['i2i_requests']), 4)
        self.assertEqual(data['vidu_anchor']['scene'], 5)
        self.assertTrue(all(a['last_decoded_frame_pixel_identical_to_freeze'] for a in data['source_frames']))
        self.assertEqual(data['provider_requests_sent'], 0)
        self.assertFalse(data['publication_permitted'])
        self.assertFalse(data['vidu_anchor']['user_approved_this_exact_scene'])

    def test_tampered_freeze_sha_fails_closed(self):
        import copy
        r = copy.deepcopy(self.report)
        r['scenes'][0]['exact_last_decoded_frame_sha256'] = 'f' * 64
        with self.assertRaisesRegex(ValueError, 'ASSET_SHA_MISMATCH'):
            v190.build(r, self.root, expected_dimensions=(320, 240))

    def test_correct_sha_but_wrong_freeze_frame_fails_pixels(self):
        import copy
        r = copy.deepcopy(self.report)
        scene = r['scenes'][0]
        clip = self.root / scene['motion_mp4']
        wrong = self.root / '01_wrong_last_real_film_frame.png'
        run('-i', clip, '-vf', 'select=eq(n\\,0)', '-vsync', '0', '-frames:v', '1', wrong)
        scene['freeze_png'] = wrong.name
        scene['exact_last_decoded_frame_sha256'] = v190.sha(wrong)
        with self.assertRaisesRegex(ValueError, 'FREEZE_NOT_LAST_DECODED_FRAME'):
            v190.build(r, self.root, expected_dimensions=(320, 240))

    def test_duplicate_archive_shot_refused(self):
        import copy
        r = copy.deepcopy(self.report)
        r['scenes'][4]['v187_png'] = r['scenes'][0]['v187_png']
        with self.assertRaisesRegex(ValueError, 'DUPLICATE_ARCHIVE_SHOT'):
            v190.build(r, self.root, expected_dimensions=(320, 240))

    def test_duplicate_source_interval_refused(self):
        import copy
        r = copy.deepcopy(self.report)
        r['scenes'][4]['v187_interval'] = r['scenes'][0]['v187_interval']
        with self.assertRaisesRegex(ValueError, 'DUPLICATE_SOURCE_INTERVAL'):
            v190.build(r, self.root, expected_dimensions=(320, 240))

    def test_fake_permissions_refused(self):
        import copy
        r = copy.deepcopy(self.report)
        r['provider_jobs_may_start'] = True
        with self.assertRaisesRegex(ValueError, 'UNSAFE_PROOF_PERMISSIONS'):
            v190.build(r, self.root, expected_dimensions=(320, 240))

    def test_wrong_geometry_refused(self):
        with self.assertRaisesRegex(ValueError, 'MOTION_CLIP_CODEC_OR_GEOMETRY_INVALID'):
            v190.build(self.report, self.root)

    def test_path_traversal_refused(self):
        import copy
        r = copy.deepcopy(self.report)
        r['scenes'][0]['motion_mp4'] = '../secret.mp4'
        with self.assertRaisesRegex(ValueError, 'UNSAFE_ASSET_FILENAME'):
            v190.build(r, self.root, expected_dimensions=(320, 240))


if __name__ == '__main__':
    unittest.main()
