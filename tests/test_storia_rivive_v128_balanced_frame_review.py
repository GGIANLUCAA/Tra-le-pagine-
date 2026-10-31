"""V128 synthetic regressions (do NOT claim real archival-film verification)."""
import hashlib
import json
import math
import random
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

from PIL import Image
from src.storia_rivive_v128_balanced_frame_review import inspect

TIMES=[210.16,232.36,357.36,452.88,509.88]
CUTS=[205.,225.,340.,445.,500.]


def make_case(root, *, duplicate=False, flat=False):
    root=Path(root)
    frames=root/'original_frames'
    frames.mkdir()
    provenance=[]
    audit=[]
    review=[]
    rng=random.Random(84)
    first=None
    for i,t in enumerate(TIMES):
        name=f'frame_{i+1:02d}.png'
        if flat and i==2:
            pixels=[110]*(128*96)
        elif duplicate and i==4:
            pixels=[min(255,p+7) for p in first]
        else:
            pixels=[rng.randrange(10,220) for _ in range(128*96)]
        if i==0:
            first=pixels
        img=Image.new('L',(128,96))
        img.putdata(pixels)
        target=frames/name
        img.save(target)
        digest=hashlib.sha256(target.read_bytes()).hexdigest()
        pts=round(t*100)
        start=max(0.0,CUTS[i]+.05,t-1.35)
        start_pts=math.ceil(Fraction(str(start))*100)
        window={'start_pts':start_pts,'freeze_pts':pts,'time_base':'1/100'}
        provenance.append({'filename':name,'sha256':digest,'source_pts_logged_from_decode':True,
                           'source_pts':pts,'source_pts_time_s':t,'source_time_base':'1/100',
                           'shot_candidate_segment_index':i+1})
        audit.append({'filename':name,'source_time_s':t,'source_pts':pts,
                      'candidate_segment_index':i+1,'status':'MOTION_EVIDENCE_PASS',
                      'motion_verified':True,'changed_pairs':6,'sample_count':11,
                      'max_spatial_pixel_delta':12.0,**window})
        review.append({'filename':name,'source_pts_time_s':t,'source_pts':pts,
                       'source_time_base':'1/100','source_frame_sha256':digest,
                       'source_film_sha256':'a'*64,'candidate_segment_index':i+1,
                       'timeline_region':min(4,int(t*5/525.)),
                       'motion_verified_for_review':True,'genuine_camera_shot_verified':False,
                       'human_artistic_approved':False,'pre_freeze_window_pts':window})
    scout={'status':'REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW',
           'adaptive_research_version':'V124_UNAPPROVED_LONG_SEGMENT_TARGET_SAMPLING',
           'original_sha256':'a'*64,'frame_provenance_source_sha256':'a'*64,
           'historical_camera_shots_verified':False,'duration_s':525.,
           'frame_provenance':provenance,
           'shot_boundary_analysis':{'version':'V113_FFMPEG_SCENE_CANDIDATES',
                'source_sha256':'a'*64,'status':'FIVE_SEGMENTS_POSSIBLE_REVIEW_REQUIRED',
                'cut_candidate_times_s':CUTS}}
    motion={'version':'V125_REAL_BW_DECODED_SPATIAL_MOTION_UNAPPROVED',
            'status':'V125_MOTION_SOURCE_SELECTION_BLOCKED',
            'source_video_sha256':'a'*64,'source_duration_s':525.,
            'five_genuine_camera_shots_approved':False,'italian_rights_verified':False,
            'motion_audit':audit,'five_review_shots':[]}
    balanced={'version':'V126_FIVE_DIVERSE_MOVING_SHOTS_NOT_APPROVED',
              'status':'V126_FIVE_DIFFERENT_MOVING_SOURCE_CANDIDATES_REVIEW_ONLY',
              'source_film_sha256':'a'*64,'source_duration_s':525.,
              'five_real_camera_shots_verified':False,'human_artistic_approved':False,
              'italian_rights_verified':False,'video_finished':False,
              'five_review_candidates':review,'selected_timeline_regions':[2,3,4],
              'minimum_seconds_between_freezes':12.0}
    files=[]
    for name,data in [('balanced',balanced),('motion',motion),('scout',scout)]:
        file=root/(name+'.json')
        file.write_text(json.dumps(data),encoding='utf-8')
        files.append(file)
    return (*files, frames, root/'V128.json', root/'CONTACT_V128.jpg')


class V128Tests(unittest.TestCase):
    def test_source_locked_balanced_candidates_still_unapproved(self):
        with tempfile.TemporaryDirectory() as root:
            args=make_case(root)
            result=inspect(*args)
            self.assertEqual(result['status'],'V128_FIVE_BALANCED_FRAMES_VISUAL_REVIEW_REQUIRED')
            self.assertEqual([row['timeline_region'] for row in result['five_review_frames']],[2,2,3,4,4])
            self.assertTrue(result['original_pts_sha_motion_evidence_crosschecked'])
            self.assertFalse(result['genuine_camera_shots_verified'])
            self.assertFalse(result['italian_rights_verified'])
            self.assertEqual(result['paid_api_calls'],0)
            self.assertTrue(args[-1].is_file())

    def test_duplicate_even_with_brightness_change_blocks(self):
        with tempfile.TemporaryDirectory() as root:
            result=inspect(*make_case(root,duplicate=True))
            self.assertEqual(result['status'],'V128_NEAR_DUPLICATE_FRAMES_BLOCKED')
            self.assertEqual(result['near_duplicate_pairs'][0]['first'],'frame_01.png')

    def test_low_detail_blocks(self):
        with tempfile.TemporaryDirectory() as root:
            result=inspect(*make_case(root,flat=True))
            self.assertEqual(result['status'],'V128_LOW_CONTRAST_FRAMES_BLOCKED')

    def test_wrong_pts_against_original_ledger_fails(self):
        with tempfile.TemporaryDirectory() as root:
            args=make_case(root)
            path=args[0];data=json.loads(path.read_text())
            data['five_review_candidates'][2]['source_pts']+=1
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'TIMELINE_OR_APPROVAL_FORGED'):
                inspect(*args)

    def test_forged_motion_pass_fails(self):
        with tempfile.TemporaryDirectory() as root:
            args=make_case(root)
            path=args[1];data=json.loads(path.read_text())
            data['motion_audit'][3]['changed_pairs']=0
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'MOTION_EVIDENCE_MISSING'):
                inspect(*args)

    def test_tampered_png_fails(self):
        with tempfile.TemporaryDirectory() as root:
            args=make_case(root)
            (args[3]/'frame_02.png').write_bytes(b'tampered')
            with self.assertRaisesRegex(ValueError,'PNG_BYTES_MISSING_OR_CHANGED'):
                inspect(*args)

    def test_forged_rights_approval_fails(self):
        with tempfile.TemporaryDirectory() as root:
            args=make_case(root)
            path=args[0];data=json.loads(path.read_text())
            data['italian_rights_verified']=True
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'UNAPPROVED_STATE_INVALID'):
                inspect(*args)

    def test_wrong_region_fails(self):
        with tempfile.TemporaryDirectory() as root:
            args=make_case(root)
            path=args[0];data=json.loads(path.read_text())
            data['five_review_candidates'][0]['timeline_region']=0
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'TIMELINE_OR_APPROVAL_FORGED'):
                inspect(*args)

if __name__=='__main__':
    unittest.main()
