import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image, ImageOps

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
import storia_rivive_v265_fiesole_first_true_color_i2i as v265

class V265Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.source=self.root/"original_shot_01_frame_03.png"
        Image.new("RGB",(1920,1080),(90,90,90)).save(self.source)
        self.manifest=self.root/"V251_SOURCE_MANIFEST_NOT_FINAL.json"
        self.manifest.write_text(json.dumps({"do_not_trust_this_mock":True}))

    def local_crop(self,source,crop):
        Image.new("RGB",(608,1080),(90,90,90)).save(crop)
        return v265.engine.sha(crop)

    def run_trial(self,photo_color,offline=False):
        def fake_cpu_model(crop,target):
            # High-detail synthetic photograph-sized PNG, not a compressed
            # flat RGB tile rejected by V257's >10KB byte integrity threshold.
            noise = Image.effect_noise(v265.engine.MODEL_DIMS, 35)
            dark = tuple(max(0, c-35) for c in photo_color)
            light = tuple(min(255, c+35) for c in photo_color)
            ImageOps.colorize(noise.convert("L"), black=dark, white=light).save(target)
        with patch.object(v265.first,"verify_manifest",return_value={"source_time_s":24.092}),(
             patch.object(v265.engine,"crop_source",side_effect=self.local_crop)):
            return v265.run(self.manifest,self.source,self.root/"out",
                            offline=offline,generator=fake_cpu_model)

    def test_offline_source_handoff_never_claims_generation(self):
        audit=self.run_trial((180,90,20),offline=True)
        self.assertEqual(audit["actual_generated_photos"],0)
        self.assertFalse(audit["artistic_approval"])
        self.assertFalse(audit["publish_allowed"])
        self.assertEqual(audit["new_final_episodes_delivered"],0)

    def test_real_color_candidate_still_never_automatically_approved(self):
        audit=self.run_trial((190,130,54))
        self.assertEqual(audit["actual_generated_photos"],1)
        self.assertTrue(audit["minimal_natural_color_evidence"])
        self.assertEqual(audit["status"],"ONE_REAL_COLOR_I2I_VISUAL_QA_REQUIRED_NOT_FINAL")
        self.assertFalse(audit["artistic_approval"])
        self.assertFalse(audit["italian_rights_verified"])
        self.assertEqual(audit["vidu_credit_spent"],0)
        self.assertFalse(audit["publish_allowed"])
        self.assertTrue((self.root/"out"/v265.NAME).is_file())

    def test_near_monochrome_rejected_not_approved(self):
        audit=self.run_trial((94,93,92))
        self.assertEqual(audit["actual_generated_photos"],1)
        self.assertFalse(audit["minimal_natural_color_evidence"])
        self.assertEqual(audit["status"],"REJECTED_INSUFFICIENT_COLOR_NOT_FINAL")
        self.assertFalse(audit["artistic_approval"])

    def test_original_sha_failure_stops_before_model(self):
        with patch.object(v265.first,"verify_manifest",side_effect=ValueError("V261_ORIGINAL_BYTES_CHANGED")):
            with self.assertRaisesRegex(ValueError,"V261_ORIGINAL_BYTES_CHANGED"):
                v265.run(self.manifest,self.source,self.root/"out",generator=lambda *args:self.fail("model called"))
        self.assertFalse((self.root/"out"/v265.NAME).exists())

    def test_generated_file_wrong_dimensions_rejected(self):
        def fake_bad(crop,target):
            noise = Image.effect_noise((128,128), 35)
            ImageOps.colorize(noise.convert("L"), black=(90,30,30), white=(210,90,70)).save(target)
        with patch.object(v265.first,"verify_manifest",return_value={"source_time_s":24.092}),(
             patch.object(v265.engine,"crop_source",side_effect=self.local_crop)):
            with self.assertRaisesRegex(ValueError,"WRONG_DIMENSIONS"):
                v265.run(self.manifest,self.source,self.root/"out",generator=fake_bad)
        report=json.loads((self.root/"out"/v265.REPORT).read_text())
        self.assertEqual(report["actual_generated_photos"],0)
        self.assertFalse(report["publish_allowed"])

if __name__=="__main__":unittest.main()
