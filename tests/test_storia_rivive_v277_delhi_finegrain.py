"""V277: verify source SHA, bounded single Finegrain call and no fake final."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image,ImageOps

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import storia_rivive_v277_delhi_finegrain_v98_method as v

class V277(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.root=Path(self.t.name)
        self.src=self.root/"V273_ACTUAL_DELHI_ORIGINAL_CROP.png"
        self.base=self.root/"DELHI_1910_SHOT03_ONE_TRUE_I2I_CANDIDATE_NOT_FINAL.png"
        self.manifest=self.root/"DELHI_V273_REAL_I2I_TRIAL_NOT_FINAL.json"
        orig=Image.effect_noise((608,1080),22).convert("RGB")
        orig.save(self.src)
        pre=ImageOps.colorize(Image.effect_noise((448,800),22).convert("L"),black="#2d3c26",white="#aabb86")
        pre.save(self.base)
        self.shas=(v.sha(self.src),v.sha(self.base))
        self.m={
            "version":"V273_DELHI_REAL_CPU_I2I_REVIEW_ONLY","episode":v.EPISODE,
            "source_metadata":{"film_sha256":v.FILM_SHA,
              "original_frame_sha256":v.ORIGINAL_FRAME_SHA,"source_shot":3},
            "source_crop_sha256":self.shas[0],
            "generated_sha256":self.shas[1],
            "generated_photos":1,
            "artistically_approved":False,"publish_allowed":False}
        self.manifest.write_text(json.dumps(self.m))
    def source_patch(self):
        from contextlib import ExitStack
        stack=ExitStack()
        stack.enter_context(patch.object(v,"SOURCE_CROP_SHA",self.shas[0]))
        stack.enter_context(patch.object(v,"V273_BASE_SHA",self.shas[1]))
        return stack

    def test_true_source_lock_passes(self):
        with self.source_patch():
            info=v.verified_sources(self.src,self.base,self.manifest)
        self.assertEqual(info["real_base_i2i_sha256"],self.shas[1])

    def test_forged_original_crop_bytes_are_rejected(self):
        with self.source_patch():
            Image.new("RGB",(608,1080),"gray").save(self.src)
            with self.assertRaisesRegex(ValueError,"SOURCE_SHA_CHANGED"):
                v.verified_sources(self.src,self.base,self.manifest)

    def test_offline_never_calls_provider_or_claims_approved(self):
        with self.source_patch():
            report=v.run(self.src,self.base,self.manifest,self.root/"out",offline=True,
                         predict=lambda _:self.fail("remote model called"))
        self.assertEqual(report["provider_calls_attempted"],0)
        self.assertFalse(report["photo_generated"])
        self.assertFalse(report["artistic_approval"])
        self.assertEqual(report["new_final_episodes_delivered"],0)

    def test_one_real_candidate_still_not_final(self):
        third=self.root/"fake_finegrain_new.png"
        ImageOps.colorize(Image.effect_noise((448,800),22).convert("L"),
                          black="#265344",white="#dac6a7").save(third)
        with self.source_patch():
            report=v.run(self.src,self.base,self.manifest,self.root/"out",
                         predict=lambda _:third)
        self.assertEqual(report["provider_calls_attempted"],1)
        self.assertTrue(report["photo_generated"])
        self.assertEqual(report["new_final_episodes_delivered"],0)
        self.assertFalse(report["artistic_approval"])
        self.assertFalse(report["italian_rights_verified"])
        self.assertFalse(report["published"])
        self.assertTrue((self.root/"out"/v.PHOTO_NAME).stat().st_size>20000)
        self.assertTrue((self.root/"out"/"V277_DELHI_SOURCE_V273_V98_FINEGRAIN_COMPARISON.jpg").is_file())

    def test_missing_result_fails_closed_with_report(self):
        with self.source_patch():
            with self.assertRaisesRegex(ValueError,"NO_PROVIDER_IMAGE"):
                v.run(self.src,self.base,self.manifest,self.root/"out",
                      predict=lambda _:self.root/"no-png")
        report=json.loads((self.root/"out"/v.QA_NAME).read_text())
        self.assertEqual(report["provider_calls_attempted"],1)
        self.assertEqual(report["status"],"FREE_FINEGRAIN_FAILED_NO_NEW_APPROVED_I2I")
        self.assertFalse(report["final_video_created"])

if __name__=="__main__":unittest.main()
