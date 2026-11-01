"""Reference-style V163 tests. Synthetic frame bytes; no copyrighted clips in CI."""
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np

from src.storia_rivive_v163_rapid_reveal_qa import analyze,inspect


def synthetic_frames(*, scenes=8, move=True, repeat=False, trailing_black=0):
    """8x1.75s authentic-style BW->color cycles at 4 samples/s = 14s."""
    result=[]
    y,x=np.mgrid[:128,:72]
    for scene in range(scenes):
        rng=np.random.default_rng(5 if repeat else 100+scene)
        source=np.full((128,72),125,dtype=np.uint8)
        for i in range(8):
            x0=int(rng.integers(4,60));y0=int(rng.integers(4,120))
            cv2.rectangle(source,(x0,y0),(min(x0+int(rng.integers(5,20)),71),min(y0+int(rng.integers(5,17)),127)),int(rng.integers(35,240)),-1)
        for i in range(7):
            original=source.copy()
            offset=(i*9 if move else 0)
            cv2.circle(original,(9+offset,64),15,205,-1)
            if i<3: rgb=cv2.cvtColor(original,cv2.COLOR_GRAY2RGB)
            else:
                rgb=np.stack([original, np.clip(original.astype('float32')*.66,0,255).astype('uint8'),np.clip(original.astype('float32')*.31,0,255).astype('uint8')],axis=-1)
            result.append(rgb)
    result.extend([np.zeros((128,72,3),dtype=np.uint8) for _ in range(trailing_black)])
    return np.array(result,dtype=np.uint8)


class ReferenceRhythmQA(unittest.TestCase):
    def test_8_real_moving_bw_to_color_cycles_are_detected(self):
        result=inspect(synthetic_frames(),duration=14.0,mode='reference')
        self.assertEqual(result['reveal_count'],8)
        self.assertGreaterEqual(result['different_b_w_appearances'],5)
        self.assertTrue(result['checks']['every_counted_reveal_preceded_by_observed_bw_motion'])
        self.assertEqual(result['status'],'V163_CADENCE_TECHNICAL_PASS_NOT_ARTISTIC_APPROVAL')
        self.assertFalse(result['claims_genuine_ai_i2i'])
        self.assertFalse(result['user_artistic_approval'])

    def test_cat_style_one_long_photo_rejected(self):
        frames=synthetic_frames(scenes=1)
        color=frames[-1]
        seq=np.concatenate((frames,np.tile(color,(52,1,1,1))),axis=0)
        r=inspect(seq,duration=len(seq)/4,mode='reference')
        self.assertLess(r['reveal_count'],5)
        self.assertEqual(r['status'],'V163_NOT_LIKE_USER_REFERENCE_BLOCK_FINAL_DELIVERY')

    def test_repeating_same_bw_scene_cannot_pretend_to_be_eight_distinct_shots(self):
        r=inspect(synthetic_frames(repeat=True),duration=14.0,mode='reference')
        self.assertEqual(r['reveal_count'],8)
        self.assertLess(r['different_b_w_appearances'],5)
        self.assertFalse(r['checks']['at_least_5_distinct_monochrome_sources'])

    def test_motionless_archival_source_fails_even_with_eight_color_reveals(self):
        r=inspect(synthetic_frames(move=False),duration=14.0,mode='reference')
        self.assertEqual(r['reveal_count'],8)
        self.assertFalse(r['checks']['every_counted_reveal_preceded_by_observed_bw_motion'])
        self.assertEqual(r['status'],'V163_NOT_LIKE_USER_REFERENCE_BLOCK_FINAL_DELIVERY')

    def test_reference_end_card_allowed_for_comparison_but_blocked_in_deliverable(self):
        frames=synthetic_frames(trailing_black=16)
        ref=inspect(frames,duration=18.0,mode='reference')
        self.assertEqual(ref['status'],'V163_CADENCE_TECHNICAL_PASS_NOT_ARTISTIC_APPROVAL')
        deliver=inspect(frames,duration=18.0,video={'width':720,'height':1280},audios=[{'codec_name':'aac'}],mode='delivery')
        self.assertGreaterEqual(deliver['black_endcard_s'],3.5)
        self.assertFalse(deliver['checks']['no_long_black_end_card'])
        self.assertEqual(deliver['status'],'V163_NOT_LIKE_USER_REFERENCE_BLOCK_FINAL_DELIVERY')

    def test_audioless_output_rejected_even_when_cadence_passes(self):
        frames=synthetic_frames()
        out=inspect(frames,duration=14.0,video={'width':720,'height':1280},audios=[],mode='delivery')
        self.assertFalse(out['checks']['aac_audio_present'])
        self.assertEqual(out['status'],'V163_NOT_LIKE_USER_REFERENCE_BLOCK_FINAL_DELIVERY')

    def test_wrong_raster_does_not_count_as_delivery_ready(self):
        frames=synthetic_frames()
        out=inspect(frames,duration=14.0,video={'width':144,'height':256},audios=[{'codec_name':'aac'}],mode='delivery')
        self.assertFalse(out['checks']['h264_vertical_720x1280'])

    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),'requires ffmpeg')
    def test_decoded_real_mp4_bytes_not_just_dummy_metadata(self):
        frames=synthetic_frames()
        with tempfile.TemporaryDirectory() as d:
            media=Path(d)/'synthetic_input.mp4'
            raw=Path(d)/'real.raw';raw.write_bytes(frames.tobytes())
            subprocess.run(['ffmpeg','-nostdin','-y','-v','error','-f','rawvideo','-pixel_format','rgb24','-video_size','72x128','-framerate','4','-i',str(raw),'-c:v','libx264','-pix_fmt','yuv420p',str(media)],check=True,timeout=30,capture_output=True)
            result=analyze(media,'reference')
            self.assertEqual(result['status'],'V163_CADENCE_TECHNICAL_PASS_NOT_ARTISTIC_APPROVAL')
            self.assertEqual(result['reveal_count'],8)
            self.assertEqual(len(result['analyzed_video_sha256']),64)

if __name__=='__main__':unittest.main()