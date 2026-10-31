"""Real FFmpeg-encoded fixture tests for source-motion guard (zero API)."""
import hashlib
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from src.storia_rivive_motion_window_v115 import check_source_window, inspect_source_motion


class WindowMetadataTests(unittest.TestCase):
    def test_valid(self):
        self.assertTrue(check_source_window(0, 45, '1/30')[0])

    def test_short(self):
        self.assertEqual(check_source_window(0, 12, '1/30')[1], 'PRE_FREEZE_WINDOW_TOO_SHORT')

    def test_long(self):
        self.assertEqual(check_source_window(0, 120, '1/30')[1], 'PRE_FREEZE_WINDOW_TOO_LONG')

    def test_clock(self):
        self.assertEqual(check_source_window(0, 45, '1/0')[1], 'INVALID_TIME_BASE')

    def test_bool_pts(self):
        self.assertEqual(check_source_window(True, 45, '1/30')[1], 'INVALID_PTS_TYPE')

    def test_reverse(self):
        self.assertEqual(check_source_window(45, 30, '1/30')[1], 'NO_PRE_FREEZE_SOURCE_WINDOW')


@unittest.skipUnless(shutil.which('ffmpeg'), 'FFmpeg unavailable')
class DecodedSourceMotionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.static = Path(cls.tmp.name) / 'static.mp4'
        cls.moving = Path(cls.tmp.name) / 'moving.mp4'
        for kind, path in [('color=c=gray:size=128x128:rate=30', cls.static),
                           ('testsrc2=size=128x128:rate=30', cls.moving)]:
            subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
                            '-f', 'lavfi', '-i', kind, '-t', '3', '-an',
                            '-c:v', 'mpeg4', '-q:v', '3', str(path)],
                           check=True, timeout=30)
        # V120: an unmoving checkerboard with drastic global exposure flicker.
        # Encoded frames REALLY differ; raw interframe pixel delta alone passes.
        cls.flicker = Path(cls.tmp.name) / 'flicker.mp4'
        raw = Path(cls.tmp.name) / 'flicker.gray'
        low = bytes(60 + 40 * ((x // 16 + y // 16) % 2)
                    for y in range(128) for x in range(128))
        high = bytes(v + 100 for v in low)
        with raw.open('wb') as output:
            for n in range(90):
                output.write(high if (n // 4) % 2 else low)
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
                        '-f', 'rawvideo', '-pixel_format', 'gray',
                        '-video_size', '128x128', '-framerate', '30',
                        '-i', str(raw), '-c:v', 'mpeg4', '-q:v', '3',
                        str(cls.flicker)], check=True, timeout=30)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    @staticmethod
    def sha(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def test_actual_motion_passes(self):
        evidence = inspect_source_motion(self.moving, self.sha(self.moving), 0, 45, '1/30')
        self.assertEqual(evidence['status'], 'MOTION_EVIDENCE_PASS', evidence)
        self.assertGreaterEqual(evidence['changed_pairs'], 2)

    def test_static_film_fails(self):
        evidence = inspect_source_motion(self.static, self.sha(self.static), 0, 45, '1/30')
        self.assertEqual(evidence['reason'], 'SOURCE_WINDOW_STATIC_OR_TOO_LITTLE_MOTION', evidence)

    def test_global_exposure_flicker_does_not_count_as_motion(self):
        evidence = inspect_source_motion(self.flicker, self.sha(self.flicker),
                                         0, 45, '1/30')
        self.assertEqual(evidence['status'], 'BLOCKED', evidence)
        self.assertEqual(evidence['reason'], 'SOURCE_WINDOW_EXPOSURE_FLICKER_NOT_MOTION', evidence)
        self.assertGreater(evidence['max_mean_pixel_delta'], 80, evidence)
        self.assertLess(evidence['max_spatial_pixel_delta'], 6, evidence)
        self.assertGreaterEqual(evidence['exposure_only_pairs'], 2)
        self.assertEqual(evidence['changed_pairs'], 0)

    def test_wrong_source_sha_fails_before_decode(self):
        evidence = inspect_source_motion(self.moving, '0' * 64, 0, 45, '1/30')
        self.assertEqual(evidence['reason'], 'SOURCE_VIDEO_SHA256_MISMATCH')

    def test_missing_source_fails(self):
        evidence = inspect_source_motion(Path(self.tmp.name) / 'missing.mp4', '0' * 64, 0, 45, '1/30')
        self.assertEqual(evidence['reason'], 'SOURCE_VIDEO_MISSING')

    def test_short_window_fails_without_decode(self):
        evidence = inspect_source_motion(self.moving, self.sha(self.moving), 0, 10, '1/30')
        self.assertEqual(evidence['reason'], 'PRE_FREEZE_WINDOW_TOO_SHORT')


if __name__ == '__main__':
    unittest.main()
