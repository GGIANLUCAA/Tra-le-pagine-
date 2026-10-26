"""No external services: test master integrity, MP4 audio/video, ZIP and mobile fallback."""
import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from src.video_download_fallback_v36 import deliver, zip_only_video


class DownloadFallbackTests(unittest.TestCase):
    def test_zip_always_contains_exactly_original_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            fake_video = root / 'EXAMPLE.mp4'
            payload = b'example-inert-raw-bytes' * 3000
            fake_video.write_bytes(payload)
            record = zip_only_video(fake_video, root / 'SOLO_VIDEO.zip')
            self.assertEqual(record['size_bytes'], (root / 'SOLO_VIDEO.zip').stat().st_size)
            with zipfile.ZipFile(root / 'SOLO_VIDEO.zip') as z:
                self.assertEqual(z.namelist(), ['EXAMPLE.mp4'])
                self.assertIsNone(z.testzip())
                self.assertEqual(z.read('EXAMPLE.mp4'), payload)

    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),
                         'ffmpeg absent on CI; full MP4 integration verified separately')
    def test_mp4_zip_integrity_and_mobile_video(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            original = root / 'TRA_LE_PAGINE_EPTEST.mp4'
            subprocess.run(['ffmpeg', '-hide_banner', '-v', 'error', '-y',
                            '-f', 'lavfi', '-i', 'testsrc2=size=240x426:rate=24',
                            '-f', 'lavfi', '-i', 'sine=frequency=440:sample_rate=44100',
                            '-t', '2.5', '-c:v', 'libx264', '-preset', 'ultrafast',
                            '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', str(original)],
                           check=True)
            before = hashlib.sha256(original.read_bytes()).hexdigest()
            record = deliver(original, root / 'delivery', android=True)
            self.assertEqual(record['status'], 'verified_locally_not_remote_link')
            self.assertEqual(record['master']['sha256'], before)
            self.assertEqual(hashlib.sha256(original.read_bytes()).hexdigest(), before)
            self.assertEqual(len(record['downloads']), 3)
            self.assertFalse(record['warnings'])
            for row in record['downloads']:
                f = root / 'delivery' / row['filename']
                self.assertGreater(f.stat().st_size, 10000)
                self.assertEqual(hashlib.sha256(f.read_bytes()).hexdigest(), row['sha256'])
            with zipfile.ZipFile(root / 'delivery' / 'TRA_LE_PAGINE_EPTEST_SOLO_VIDEO.zip') as z:
                self.assertEqual(z.namelist(), [original.name])
                self.assertEqual(hashlib.sha256(z.read(original.name)).hexdigest(), before)
            manifest = json.loads((root / 'delivery' / 'VERIFICA_DOWNLOAD.json').read_text())
            self.assertTrue(manifest['master']['untouched'])
            self.assertTrue((root / 'delivery' / 'TRA_LE_PAGINE_EPTEST_ANDROID_480p.mp4').is_file())
            print('PASS V36: original master preserved, zip complete, Android MP4 ready, zero API')


if __name__ == '__main__':
    unittest.main()
