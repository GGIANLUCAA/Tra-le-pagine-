"""V187: offline algorithm and real encoded synthetic film tests."""
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import storia_rivive_v187_shot_catalog as v187


class V187Tests(unittest.TestCase):
    def test_select_distinct_cut_intervals(self):
        options = v187.choose_intervals([6, 12, 18, 24, 30, 36], 42, count=6)
        self.assertEqual(len(options), 6)
        self.assertEqual(len({x['shot_interval_index'] for x in options}), 6)

    def test_no_fake_shots_from_single_take(self):
        with self.assertRaisesRegex(ValueError, 'FEWER_THAN_FIVE'):
            v187.choose_intervals([], 40)

    def test_duplicate_signatures_rejected(self):
        a = [100] * 72
        self.assertTrue(v187.near_duplicate(a, [103]*72))
        self.assertFalse(v187.near_duplicate(a, [150]*72))

    def test_bad_signature_rejected(self):
        with self.assertRaisesRegex(ValueError, 'INVALID_SIGNATURE'):
            v187.near_duplicate([1], [1])

    def test_near_black_intertitle_rejected_without_false_approval(self):
        self.assertTrue(v187.dark_or_title_like([4]*72))
        self.assertFalse(v187.dark_or_title_like([80]*72))
        self.assertFalse(v187.dark_or_title_like([8]*40 + [150]*32))

    def test_out_dir_never_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'existing'
            p.mkdir()
            (p/'keep').write_text('yes')
            r = v187.catalog(Path(d)/'missing.mp4', '0'*64, p)
            self.assertEqual(r['status'], 'CATALOG_BLOCKED')
            self.assertIn('OUTPUT_DIR_ALREADY_EXISTS', str(r['blocking_issues']))
            self.assertEqual((p/'keep').read_text(), 'yes')

    def test_real_encoded_film_cut_detection_and_native_pngs(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            clips = []
            for n, color in enumerate(['red','blue','yellow','green','magenta','cyan','white']):
                p = root/f'c{n}.mp4'
                subprocess.run(['ffmpeg','-loglevel','error','-y','-f','lavfi','-i',
                                f'color=c={color}:s=1280x720:r=2','-t','5','-c:v',
                                'libx264','-preset','ultrafast','-pix_fmt','yuv420p',str(p)],
                               check=True,timeout=90)
                clips.append(p)
            txt = root/'list.txt'
            txt.write_text(''.join(f"file '{p}'\n" for p in clips))
            film = root/'film.mp4'
            subprocess.run(['ffmpeg','-loglevel','error','-y','-f','concat','-safe','0',
                            '-i',str(txt),'-c','copy',str(film)],check=True,timeout=90)
            sha = hashlib.sha256(film.read_bytes()).hexdigest()
            report = v187.catalog(film,sha,root/'shots',count=6,threshold=0.08)
            self.assertEqual(report['status'],'DIVERSE_CUT_CANDIDATES_NEED_VISUAL_REVIEW',report)
            self.assertGreaterEqual(len(report['candidates']),5)
            self.assertFalse(report['five_distinct_shots_verified'])
            self.assertFalse(report['publish_permitted'])
            for item in report['candidates']:
                p = root/'shots'/item['png_filename']
                self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),item['png_sha256'])


if __name__=='__main__':
    unittest.main()
