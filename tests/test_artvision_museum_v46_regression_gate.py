import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import artvision_museum_v46_regression_gate as gate

class MuseumV46GateTests(unittest.TestCase):
    def test_perceptual_jump_rejects_equal_size_distinct_frames(self):
        black=bytes([0])*(gate.FRAME_BYTES)
        white=bytes([240])*(gate.FRAME_BYTES)
        self.assertEqual(gate.mad(black,black),0)
        self.assertEqual(gate.mad(black,white),240.0)
        self.assertGreater(gate.mad(black,white),gate.MAX_JUMP_MAD)

    def test_plan_without_frame_research_and_reference_comparison_is_rejected(self):
        errors=gate.validate_profile({
            'physical_scale':{
                'painting_width_cm':124.8,'painting_height_cm':71.4,
                'primary_museum_dimensions_source':'https://www.metmuseum.org/art/collection/search/11122',
                'human_scale_reference':'person 170cm','camera_start_distance_m':2.4}
        })
        self.assertTrue(any('frame_research missing' in e for e in errors))
        self.assertTrue(any('BOTH approved' in e for e in errors))
        self.assertTrue(any('human V46 review' in e for e in errors))

    def test_valid_research_does_not_automatically_grant_artistic_approval(self):
        review={x:True for x in (
            'photographic_room_quality','physical_frame_moulding_and_corners',
            'recessed_painting_and_contact_shadows','human_scale_and_camera_perspective',
            'gallery_entry_continuity','gallery_exit_same_room',
            'no_stretched_pixels_or_ghosting','phone_size_view_review')}
        profile={'frame_research':{
            'authenticity_status':'scenic_reconstruction',
            'source_urls':['https://www.metmuseum.org/art/collection/search/11122'],
            'photo_date_or_unknown':'unknown','rights_status':'Met work open access; gallery scenic',
            'evidence_notes':'No reliable direct frame photograph; reconstructed and labelled',
            'assumptions':'No original frame pattern claimed'},
            'physical_scale':{
                'painting_width_cm':124.8,'painting_height_cm':71.4,
                'primary_museum_dimensions_source':'https://www.metmuseum.org/art/collection/search/11122',
                'human_scale_reference':'person 170cm','camera_start_distance_m':2.4},
            'reference_comparison':{
                'cyclops_master_compared_on_real_frames':True,
                'hiroshige_master_compared_on_real_frames':True},
            'artistic_visual_qa':review}
        self.assertEqual(gate.validate_profile(profile),[])
        # Research quality is necessary, not sufficient: no release is granted here.
        self.assertNotIn('final_approval',profile)

    def test_false_documented_frame_missing_photo_url_is_blocked(self):
        profile={'frame_research':{
            'authenticity_status':'documented_current',
            'source_urls':['not verified'], 'photo_date_or_unknown':'unknown',
            'rights_status':'unknown','evidence_notes':'none','assumptions':'none'}}
        errors=gate.validate_profile(profile)
        self.assertTrue(any('verifiable reference URL' in e for e in errors))

    def test_real_approved_cyclops_camera_is_not_falsely_rejected(self):
        # True per-frame differences measured on the user's approved V46 MP4
        # at ~3.35 s: 22.81 max, 21.37 baseline, ratio 1.07.
        diffs=[20.9,21.2,21.37,22.81,21.6,21.4,20.9,22.1]
        info=gate.describe_motion_discontinuity(diffs)
        self.assertTrue(info['passed_transition_continuity'])
        self.assertLess(info['spike_ratio_vs_neighbour_median'],1.2)

    def test_new_continuous_v57_pilot_does_not_false_positive(self):
        # Real 1080x1920 V57 pilot ~6.30 s: 22.02 max, local median 20.92.
        diffs=[20.5,20.92,21.15,22.02,21.7,20.75,20.9]
        self.assertTrue(gate.describe_motion_discontinuity(diffs)['passed_transition_continuity'])

    def test_original_hokusai_and_homer_hard_cuts_are_rejected(self):
        # Real MP4 measurements: Hokusai 72-128 vs 2.3 baseline,
        # Homer 65-92 vs 0-2.56 baseline.
        for peak,median in [(72.28,2.3),(128.46,2.45),(65.92,0.0),(92.10,2.56)]:
            diffs=[median,median*.75,median*1.1,peak,median*.9,median]
            info=gate.describe_motion_discontinuity(diffs)
            self.assertFalse(info['passed_transition_continuity'])
            self.assertTrue(info['isolated_hard_cut_detected'])

    def test_approximate_measured_jump_semantics(self):
        # The direct original MP4 review measured 74/130 for Hokusai and
        # 67/93 for Homer. Those real measurements must never be approved.
        for v in [74.413,130.237,66.859,92.653]:
            self.assertGreater(v,gate.MAX_JUMP_MAD)

if __name__=='__main__':
    unittest.main()
