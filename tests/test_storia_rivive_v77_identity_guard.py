import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np

P = Path(__file__).resolve().parents[1] / 'src' / 'storia_rivive_v77_identity_guard.py'
spec = importlib.util.spec_from_file_location('v77', P)
v77 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v77)


class IdentityGuardTests(unittest.TestCase):
    def setUp(self):
        self.src = np.full((480, 270, 3), 155, np.uint8)
        # Original old image: building/ladder/vehicle elements, no people.
        cv2.rectangle(self.src, (15, 60), (255, 340), (100, 100, 100), -1)
        cv2.line(self.src, (95, 90), (95, 330), (30, 30, 30), 10)
        cv2.line(self.src, (138, 90), (138, 330), (30, 30, 30), 10)
        for yy in range(100, 330, 27):
            cv2.line(self.src, (95, yy), (138, yy), (25, 25, 25), 5)
        self.fake = self.src.copy()
        # Invented person's head/body over part of the ladder.
        cv2.circle(self.fake, (170, 155), 39, (95, 150, 185), -1)
        cv2.rectangle(self.fake, (139, 191), (203, 319), (60, 80, 130), -1)

    def test_global_correlation_does_not_approve_a_person(self):
        qa, risk = v77.inspect(self.src, self.fake)
        self.assertIs(qa['semantic_object_identity_verified'], False)
        self.assertTrue(qa['human_review_required'])
        self.assertGreater(qa['suspicious_tiles'], 0)
        self.assertEqual(risk.shape, self.src.shape[:2])

    def test_source_locked_avoids_luminance_hallucination(self):
        qa, risk = v77.inspect(self.src, self.fake)
        locked, meta = v77.source_locked_composite(self.src, self.fake, risk, [], .78)
        src_l = cv2.cvtColor(self.src, cv2.COLOR_BGR2LAB)[:, :, 0].astype('float32')
        fake_l = cv2.cvtColor(self.fake, cv2.COLOR_BGR2LAB)[:, :, 0].astype('float32')
        lock_l = cv2.cvtColor(locked, cv2.COLOR_BGR2LAB)[:, :, 0].astype('float32')
        yy,xx=slice(115,315),slice(140,220)
        self.assertLess(np.mean(np.abs(lock_l[yy,xx]-src_l[yy,xx])),
                        np.mean(np.abs(fake_l[yy,xx]-src_l[yy,xx])))
        self.assertGreaterEqual(meta['base_fraction_original_luminance'], .78)

    def test_curator_protects_unknown_ladder_region(self):
        qa, risk = v77.inspect(self.src, self.fake)
        center = {'label':'ladder','bbox_px':[88,90,212,325]}
        normal, _ = v77.source_locked_composite(self.src, self.fake, risk, [], .60)
        protected, _ = v77.source_locked_composite(self.src, self.fake, risk, [center], .60)
        src_l = cv2.cvtColor(self.src, cv2.COLOR_BGR2LAB)[:, :, 0].astype('float32')
        normal_l = cv2.cvtColor(normal, cv2.COLOR_BGR2LAB)[:, :, 0].astype('float32')
        prot_l = cv2.cvtColor(protected, cv2.COLOR_BGR2LAB)[:, :, 0].astype('float32')
        roi=np.s_[120:300,130:200]
        self.assertLess(np.mean(np.abs(prot_l[roi]-src_l[roi])),
                        np.mean(np.abs(normal_l[roi]-src_l[roi])))

    def test_rejects_wrong_aspect_ratio(self):
        with self.assertRaisesRegex(ValueError, 'ASPECT_MISMATCH'):
            v77.inspect(self.src, self.fake[:, 40:])

    def test_protected_regions_and_bbox_validation(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'regions.json'
            p.write_text(json.dumps({'regions':[{'label':'car wheel','bbox':[.1,.2,.5,.7],'normalized':True}]}))
            got=v77.load_regions(p,(480,270))
            self.assertEqual(got[0]['bbox_px'],[27,96,135,336])
            p.write_text(json.dumps({'regions':[{'bbox':[5,10,5,20]}]}))
            with self.assertRaisesRegex(ValueError, 'Empty'):
                v77.load_regions(p,(480,270))

if __name__=='__main__':
    unittest.main()