"""V129: synthetic FFmpeg video only; never claim archival-film or rights QA."""
import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from src.storia_rivive_v129_prefreeze_motion_strips import decode_proxy, run
from test_storia_rivive_v128_balanced_frame_review import make_case


class V129Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.video_dir = tempfile.TemporaryDirectory()
        cls.video = Path(cls.video_dir.name)/'synthetic.mp4'
        if not shutil.which('ffmpeg'):
            raise unittest.SkipTest('FFmpeg unavailable')
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-nostdin',
                        '-f','lavfi','-i','testsrc2=size=160x90:rate=4:duration=525',
                        '-an','-c:v','mpeg4','-q:v','12','-y',str(cls.video)],
                       check=True,timeout=40)
        cls.sha=hashlib.sha256(cls.video.read_bytes()).hexdigest()

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls,'video_dir'):
            cls.video_dir.cleanup()

    def fixture(self, root):
        balanced,motion,scout,frames,report,sheet=make_case(root)
        for file in (balanced,motion,scout):
            data=file.read_text().replace('a'*64,self.sha)
            file.write_text(data)
        return (self.video,balanced,motion,scout,frames,report,sheet)

    def test_real_ffmpeg_synthetic_video_five_triptychs(self):
        with tempfile.TemporaryDirectory() as root:
            args=self.fixture(root)
            result=run(*args)
            self.assertEqual(result['status'],'V129_FIVE_SOURCE_LOCKED_MOTION_STRIPS_REVIEW_ONLY')
            self.assertEqual(len(result['five_prefreeze_proxy_strips']),5)
            self.assertTrue(args[-1].is_file())
            self.assertFalse(result['five_genuine_camera_shots_verified'])
            self.assertFalse(result['italian_rights_verified'])
            self.assertFalse(result['video_finished'])
            self.assertEqual(result['paid_api_calls'],0)

    def test_source_film_sha_mismatch_blocks_before_ffmpeg(self):
        with tempfile.TemporaryDirectory() as root:
            args=list(self.fixture(root))
            tampered=Path(root)/'tampered.mp4'
            tampered.write_bytes(self.video.read_bytes()+b'x')
            args[0]=tampered
            decoder=Mock(side_effect=AssertionError('must not decode'))
            with self.assertRaisesRegex(ValueError,'V129_ORIGINAL_FILM_SHA_MISMATCH'):
                run(*args,decoder=decoder)
            decoder.assert_not_called()

    def test_forged_freeze_pts_blocks_before_ffmpeg(self):
        with tempfile.TemporaryDirectory() as root:
            args=self.fixture(root)
            data=json.loads(args[1].read_text())
            data['five_review_candidates'][1]['pre_freeze_window_pts']['freeze_pts']+=1
            args[1].write_text(json.dumps(data))
            decoder=Mock(side_effect=AssertionError('must not decode'))
            with self.assertRaisesRegex(ValueError,'V128_ORIGINAL_FREEZE_WINDOW_PTS_MISMATCH'):
                run(*args,decoder=decoder)
            decoder.assert_not_called()

    def test_missing_ffmpeg_is_blocked(self):
        with self.assertRaisesRegex(ValueError,'V129_FFMPEG_MISSING'):
            decode_proxy(self.video,21000,21135,'1/100',ffmpeg='ffmpeg_missing_binary_xyz')

    def test_insufficient_source_frames_are_blocked(self):
        with tempfile.TemporaryDirectory() as root:
            short=Path(root)/'short.mp4'
            subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-nostdin',
                            '-f','lavfi','-i','color=c=black:size=160x90:rate=1:duration=1',
                            '-an','-c:v','mpeg4','-y',str(short)],check=True,timeout=20)
            with self.assertRaisesRegex(ValueError,'V129_PRE_FREEZE_PROXY_STATIC_OR_TOO_SPARSE'):
                decode_proxy(short,0,100,'1/100')

    def test_no_false_approval_even_with_visual_motion(self):
        with tempfile.TemporaryDirectory() as root:
            args=self.fixture(root)
            result=run(*args)
            self.assertTrue(result['proxy_sampling_is_not_exact_freeze_pts'])
            for name in ('human_artistic_approved','four_i2i_approved','vidu_clip_approved','published'):
                self.assertFalse(result[name])

if __name__=='__main__':
    unittest.main()
