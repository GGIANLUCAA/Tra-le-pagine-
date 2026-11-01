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

if __name__=='__main__':unittest.main()