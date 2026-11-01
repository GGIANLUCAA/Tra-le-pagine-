"""Fail-closed source/visual behavior tests for Paris photo-guided real motion."""
import importlib.util
import unittest
from pathlib import Path
import cv2
import numpy as np

MODULE=Path(__file__).resolve().parents[1]/'src/storia_rivive_v163_photo_guided_real_motion.py'
spec=importlib.util.spec_from_file_location('v163',MODULE)
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)

class MotionPhotoTests(unittest.TestCase):
    def setUp(self):
        yy,xx=np.indices((576,720),dtype=np.float32)
        p=(72+45*np.sin(xx/22)+38*np.sin(yy/26)).astype(np.uint8)
        self.anchor=cv2.cvtColor(p,cv2.COLOR_GRAY2BGR)
        cv2.rectangle(self.anchor,(200,180),(330,330),(180,180,180),-1)
        self.current=np.roll(self.anchor,4,axis=1)
        self.photo=self.anchor.copy()
        mask=np.zeros((576,720),dtype=np.uint8)
        cv2.rectangle(mask,(200,180),(330,330),255,-1)
        self.photo[mask>0]=(30,80,190)
        self.engine=cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_FAST)

    def test_photo_guided_motion_adds_chroma_without_faking_frame(self):
        out,confidence,_=v.transfer_color_motion(self.current,self.anchor,self.photo,self.engine)
        self.assertEqual(out.shape,(576,720,3))
        self.assertGreater(confidence,.45)
        color=cv2.cvtColor(out,cv2.COLOR_BGR2HSV)
        self.assertGreater(float(np.mean(color[190:320,215:340,1])),12)
        # structure of real moving image must survive enhancement
        source_gray=cv2.cvtColor(self.current,cv2.COLOR_BGR2GRAY)
        output_gray=cv2.cvtColor(out,cv2.COLOR_BGR2GRAY)
        self.assertGreater(float(np.corrcoef(source_gray.ravel(),output_gray.ravel())[0,1]),.90)

    def test_alignment_at_freeze_is_identity_flow(self):
        out,confidence,_=v.transfer_color_motion(self.anchor,self.anchor,self.photo,self.engine,near_anchor=True)
        self.assertGreater(confidence,.95)
        self.assertGreater(float(np.mean(cv2.cvtColor(out,cv2.COLOR_BGR2HSV)[190:320,215:340,1])),12)

    def test_wrong_geometry_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'GEOMETRY'):
            v.transfer_color_motion(self.current[:500],self.anchor,self.photo,self.engine)


    def test_motion_clip_sha_contract_six_real_assets(self):
        self.assertEqual(len(v.MOTION_CLIP_SHA),6)
        self.assertEqual(len(set(v.MOTION_CLIP_SHA.values())),6)
        self.assertEqual(sum(k.endswith('/real_original_motion.mp4') for k in v.MOTION_CLIP_SHA),5)
        self.assertIn('scene_05/real_original_after_freeze.mp4',v.MOTION_CLIP_SHA)

    def test_reject_replaced_moving_frames_with_same_final_anchor(self):
        import hashlib
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as root:
            expected={}
            for key in v.MOTION_CLIP_SHA:
                p=Path(root)/key
                p.parent.mkdir(parents=True,exist_ok=True)
                # Identical anchor suffix across two possible source clips;
                # only the earlier real moving content differs.
                p.write_bytes(key.encode()+b' ORIGINAL_MOVING_FRAMES | SAME_LAST_FREEZE')
                expected[key]=hashlib.sha256(p.read_bytes()).hexdigest()
            self.assertEqual(v.verify_motion_clips(root,expected),expected)
            changed=Path(root)/'scene_03/real_original_motion.mp4'
            changed.write_bytes(b'FAKE_ZOOMED_PHOTO | SAME_LAST_FREEZE')
            with self.assertRaisesRegex(ValueError,'SOURCE_MOTION_SHA_CHANGED'):
                v.verify_motion_clips(root,expected)
            changed.unlink()
            with self.assertRaisesRegex(ValueError,'SOURCE_MOTION_CLIP_MISSING'):
                v.verify_motion_clips(root,expected)

    def test_motion_manifest_rejects_duplicate_or_unsafe_paths(self):
        import tempfile
        with tempfile.TemporaryDirectory() as root:
            invalid=dict(v.MOTION_CLIP_SHA)
            invalid['scene_01/real_original_motion.mp4']=invalid['scene_02/real_original_motion.mp4']
            with self.assertRaisesRegex(ValueError,'MANIFEST_INVALID'):
                v.verify_motion_clips(root,invalid)
            invalid=dict(v.MOTION_CLIP_SHA)
            invalid['../outside.mp4']=invalid.pop('scene_01/real_original_motion.mp4')
            with self.assertRaisesRegex(ValueError,'PATH_UNSAFE'):
                v.verify_motion_clips(root,invalid)

    def test_scene_source_fingerprint_contract(self):
        self.assertEqual(len(v.SOURCE_FREEZE_SHA),5)
        self.assertEqual(len(set(v.SOURCE_FREEZE_SHA.values())),5)
        self.assertEqual(len(set(v.PHOTO_SHA.values())),3)
        self.assertEqual(len(v.DDCOLOR_SHA),2)


    def test_photo_sha_selects_real_i2i_without_eager_missing_ddcolor_lookup(self):
        # Regression: dict.get(i, sha(NEURAL_DDCOLOR_i)) evaluated sha() for
        # scenes 1..3 even when PHOTO_SHA[i] existed, crashing full render.
        import hashlib
        import tempfile
        with tempfile.TemporaryDirectory() as root:
            for i in (1, 2, 3):
                self.assertEqual(v.scene_photo_sha(i,root),v.PHOTO_SHA[i])
            for i in (4, 5):
                payload=f'actual neural source {i}'.encode()
                (Path(root)/f'NEURAL_DDCOLOR_{i:02d}.png').write_bytes(payload)
                self.assertEqual(v.scene_photo_sha(i,root),hashlib.sha256(payload).hexdigest())
            with self.assertRaises(FileNotFoundError):
                v.scene_photo_sha(4,Path(root)/'missing')
            with self.assertRaisesRegex(ValueError,'UNKNOWN_INDEX'):
                v.scene_photo_sha(6,root)

    def test_all_stills_preflight_validates_ten_real_decoded_pngs(self):
        import hashlib
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            base=Path(td)/'source'
            photos=Path(td)/'photos'
            photos.mkdir()
            freeze_sha={}; i2i_sha={}; dd_sha={}
            for i in range(1,6):
                folder=base/f'scene_{i:02d}'
                folder.mkdir(parents=True)
                freeze=folder/'EXACT_MP4_LAST_MOTION_FRAME.png'
                color=(photos/f'PHOTO_I2I_{i:02d}.png' if i<=3
                       else photos/f'NEURAL_DDCOLOR_{i:02d}.png')
                frame=np.full((576,720,3),i*19,dtype=np.uint8)
                self.assertTrue(cv2.imwrite(str(freeze),frame))
                frame[:,:,1]=i*29
                self.assertTrue(cv2.imwrite(str(color),frame))
                digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
                freeze_sha[i]=digest(freeze)
                (i2i_sha if i<=3 else dd_sha)[i]=digest(color)
            args=(base,photos,freeze_sha,i2i_sha,dd_sha)
            verified=v.verify_still_assets(*args)
            self.assertEqual(len(verified),10)
            self.assertEqual(verified['4_color'],dd_sha[4])

            # Even one changed image must fail before an encoder is started.
            target=photos/'NEURAL_DDCOLOR_04.png'
            target.write_bytes(b'tampered')
            with self.assertRaisesRegex(ValueError,'STILL_ASSET_SHA_CHANGED_4_color'):
                v.verify_still_assets(*args)
            # Matching SHA of an invalid PNG must not bypass real decoding.
            dd_sha[4]=digest(target)
            with self.assertRaisesRegex(ValueError,'STILL_ASSET_GEOMETRY_INVALID_4_color'):
                v.verify_still_assets(*args)
            target.unlink()
            with self.assertRaisesRegex(ValueError,'STILL_ASSET_MISSING_OR_LINK_4_color'):
                v.verify_still_assets(*args)

    def test_still_preflight_rejects_incomplete_manifests(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError,'STILL_ASSET_MANIFEST_INVALID'):
                v.verify_still_assets(td,td,{1:'0'*64},{1:'0'*64},{4:'0'*64})

    def test_streamed_scenes_preserve_exact_frame_order_and_pixels(self):
        import io
        a=np.zeros((v.H,v.W,3),dtype=np.uint8)
        b=a.copy()
        b[120:150,240:310]=(10,80,220)
        sink=io.BytesIO()
        end=v.stream_scene_frames([a,b],sink,0)
        expected=v.title_frame(a).tobytes()+v.title_frame(b).tobytes()
        self.assertEqual(end,2)
        self.assertEqual(sink.getvalue(),expected)

    def test_repeated_hold_is_encoded_without_repeated_title_render(self):
        import tempfile
        from unittest.mock import patch
        from PIL import Image
        class CountingSink:
            def __init__(self): self.byte_count=0
            def write(self,data): self.byte_count+=len(data)
        still=np.full((v.H,v.W,3),95,dtype=np.uint8)
        sink=CountingSink()
        with tempfile.TemporaryDirectory() as td:
            cover=Path(td)/'cover.jpg'
            with patch.object(v,'title_frame',wraps=v.title_frame) as mock_title:
                count=v.stream_scene_frames([still]*24,sink,0,cover)
            self.assertEqual(mock_title.call_count,1)
            self.assertEqual(count,24)
            self.assertEqual(sink.byte_count,24*v.H*v.W*3)
            self.assertTrue(cover.is_file())
            with Image.open(cover) as img:
                self.assertEqual(img.size,(v.W,v.H))

    def test_stream_rejects_wrong_shape_and_dtype(self):
        import io
        with self.assertRaisesRegex(ValueError,'STREAM_FRAME_GEOMETRY_INVALID'):
            v.stream_scene_frames([np.zeros((50,50,3),dtype=np.uint8)],io.BytesIO(),0)
        with self.assertRaisesRegex(ValueError,'STREAM_FRAME_GEOMETRY_INVALID'):
            v.stream_scene_frames([np.zeros((v.H,v.W,3),dtype=np.float32)],io.BytesIO(),0)

    def test_real_ffmpeg_streaming_roundtrip_four_frames(self):
        import shutil
        import subprocess
        import tempfile
        self.assertTrue(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'FFMPEG_REQUIRED_FOR_STREAMING_QA')
        with tempfile.TemporaryDirectory() as td:
            output=Path(td)/'stream.mp4'
            cmd=['ffmpeg','-nostdin','-y','-v','error','-f','rawvideo',
                 '-pix_fmt','bgr24','-s',f'{v.W}x{v.H}','-r','30','-i','-',
                 '-an','-c:v','libx264','-preset','ultrafast','-pix_fmt','yuv420p',str(output)]
            proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
            try:
                still=np.full((v.H,v.W,3),105,dtype=np.uint8)
                self.assertEqual(v.stream_scene_frames([still]*4,proc.stdin,0),4)
                proc.stdin.close()
                error=proc.stderr.read().decode(errors='replace')
                self.assertEqual(proc.wait(timeout=40),0,error[-500:])
            finally:
                if proc.poll() is None: proc.kill()
                if proc.stdin and not proc.stdin.closed: proc.stdin.close()
                proc.stderr.close()
                proc.wait()
            decoded=subprocess.run(['ffprobe','-v','error','-count_frames','-select_streams','v:0',
                                    '-show_entries','stream=nb_read_frames','-of','csv=p=0',str(output)],
                                   capture_output=True,text=True,check=True,timeout=30)
            self.assertEqual(decoded.stdout.strip(),'4')


    def test_v169_single_frame_stream_matches_buffered_bytes(self):
        # The production renderer now streams one frame at a time. Its encoded
        # pixel input must be byte-for-byte identical to the old per-scene batch.
        import io
        a=np.full((v.H,v.W,3),72,dtype=np.uint8)
        b=a.copy();b[320:370,220:280]=(18,88,210)
        c=b.copy();c[550:590,300:345]=(125,155,180)
        frames=[a,b,c]
        old=io.BytesIO()
        self.assertEqual(v.stream_scene_frames(frames,old,0),3)
        new=io.BytesIO()
        idx=0
        for frame in frames:
            idx=v.stream_scene_frames((frame,),new,idx)
        self.assertEqual(idx,3)
        self.assertEqual(new.getvalue(),old.getvalue())

    def test_v169_repeated_photo_generator_is_not_recomposed(self):
        import io
        from unittest.mock import patch
        still=np.full((v.H,v.W,3),94,dtype=np.uint8)
        sink=io.BytesIO()
        with patch.object(v,'title_frame',wraps=v.title_frame) as titled:
            count=v.stream_scene_frames((still for _ in range(5)),sink,30)
        self.assertEqual(count,35)
        self.assertEqual(titled.call_count,1)
        self.assertEqual(len(sink.getvalue()),5*v.H*v.W*3)

    def test_v169_renderer_does_not_buffer_composed_scenes(self):
        # Protect against reintroducing hundreds of 720x1280 BGR arrays.
        source=MODULE.read_text(encoding='utf-8')
        self.assertNotIn('whole.append(',source)
        self.assertNotIn('whole.extend(',source)
        self.assertNotIn('whole=[]',source)
        self.assertIn('stream_scene_frames((shown,),proc.stdin',source)
        self.assertIn('stream_scene_frames((frozen for _ in range(n))',source)


    def test_v170_scan_and_stream_same_last_frame_without_source_buffer(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'real_motion.avi'
            writer=cv2.VideoWriter(str(path),cv2.VideoWriter_fourcc(*'MJPG'),30,(720,576))
            self.assertTrue(writer.isOpened())
            try:
                for i in range(32):
                    frame=np.full((576,720,3),i*5,dtype=np.uint8)
                    cv2.rectangle(frame,(80+i,100),(180+i,200),(20,180,240),-1)
                    writer.write(frame)
            finally:
                writer.release()
            count,anchor=v.scan_clip(path)
            self.assertEqual(count,32)
            last=None
            decoded=0
            for last in v.iter_clip(path,count):
                decoded+=1
            self.assertEqual(decoded,32)
            np.testing.assert_array_equal(anchor,last)
            with self.assertRaisesRegex(ValueError,'SECOND_PASS_COUNT_MISMATCH'):
                list(v.iter_clip(path,count+1))

    def test_v170_source_scan_rejects_short_or_wrong_geometry(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            for filename,dimensions,frames in [('short.avi',(720,576),20),('wrong.avi',(320,240),32)]:
                path=Path(td)/filename
                writer=cv2.VideoWriter(str(path),cv2.VideoWriter_fourcc(*'MJPG'),30,dimensions)
                self.assertTrue(writer.isOpened())
                try:
                    for i in range(frames):
                        writer.write(np.full((dimensions[1],dimensions[0],3),i*5,dtype=np.uint8))
                finally:
                    writer.release()
                with self.assertRaisesRegex(ValueError,'NO_ACTUAL_MOVING_FRAMES' if frames<30 else 'SOURCE_CLIP_GEOMETRY_INVALID'):
                    v.scan_clip(path)

    def test_v171_muxed_movie_decodes_exact_frames_and_soundtrack(self):
        # Real FFmpeg/H264/AAC bytes, not mocked ffprobe metadata. A valid
        # container with a missing soundtrack or truncated reel must fail.
        import shutil
        import subprocess
        import tempfile
        self.assertTrue(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'FFMPEG_REQUIRED_FOR_MUX_QA')
        with tempfile.TemporaryDirectory() as td:
            good=Path(td)/'good.mp4'
            command=['ffmpeg','-nostdin','-y','-v','error',
                     '-f','lavfi','-i','color=c=black:s=720x1280:r=30:d=0.5',
                     '-f','lavfi','-i','sine=frequency=440:sample_rate=48000:duration=0.5',
                     '-c:v','libx264','-preset','ultrafast','-threads','2',
                     '-pix_fmt','yuv420p','-c:a','aac','-shortest',str(good)]
            subprocess.run(command,check=True,capture_output=True,timeout=60)
            verified=v.verify_muxed_movie(good,15)
            self.assertEqual(verified['decoded_video_frames'],15)
            self.assertAlmostEqual(verified['audio_duration_seconds'],.5,delta=.08)
            with self.assertRaisesRegex(ValueError,'MUX_VIDEO_FRAME_COUNT_MISMATCH'):
                v.verify_muxed_movie(good,16)
            silent=Path(td)/'silent.mp4'
            subprocess.run(['ffmpeg','-nostdin','-y','-v','error','-i',str(good),
                            '-c:v','copy','-an',str(silent)],
                           check=True,capture_output=True,timeout=30)
            with self.assertRaisesRegex(ValueError,'MUX_VIDEO_AUDIO_STREAM_COUNT_INVALID'):
                v.verify_muxed_movie(silent,15)
            short_audio=Path(td)/'short_audio.mp4'
            subprocess.run(['ffmpeg','-nostdin','-y','-v','error',
                            '-f','lavfi','-i','color=c=black:s=720x1280:r=30:d=0.5',
                            '-f','lavfi','-i','sine=frequency=440:sample_rate=48000:duration=0.15',
                            '-c:v','libx264','-preset','ultrafast','-threads','2',
                            '-pix_fmt','yuv420p','-c:a','aac',str(short_audio)],
                           check=True,capture_output=True,timeout=60)
            with self.assertRaisesRegex(ValueError,'MUX_AUDIO_TRUNCATED'):
                v.verify_muxed_movie(short_audio,15)

    def test_v170_renderer_has_no_full_source_frame_lists(self):
        source=MODULE.read_text(encoding='utf-8')
        self.assertNotIn('load_clip(',source)
        self.assertNotIn('real_frames=',source)
        self.assertNotIn('after_frames=',source)
        self.assertIn('iter_clip(motion_path,original_motion_frames)',source)
        self.assertIn('iter_clip(after_path,after_count)',source)

    def test_v172_runtime_snapshot_records_measured_seconds_and_peak_rss(self):
        import time
        metrics=v.render_performance_snapshot(time.perf_counter()-.1,[.012,.024,.036,.048,.06])
        self.assertEqual(len(metrics['scene_wall_seconds']),5)
        self.assertGreaterEqual(metrics['wall_seconds'],.09)
        self.assertGreater(metrics['peak_renderer_rss_mib'],0)
        self.assertGreaterEqual(metrics['peak_reaped_child_rss_mib'],0)
        self.assertIn('NOT simultaneous total RAM',metrics['rss_semantics'])
        self.assertIn('six_real_clips',metrics['benchmark_scope'])

    def test_v172_runtime_snapshot_rejects_unmeasurable_values(self):
        import time
        for times in ([-1.0],[float('nan')],[float('inf')],'five scenes'):
            with self.subTest(times=times):
                with self.assertRaisesRegex(ValueError,'SCENE_TIMES_INVALID'):
                    v.render_performance_snapshot(time.perf_counter(),times)


if __name__=='__main__':unittest.main()