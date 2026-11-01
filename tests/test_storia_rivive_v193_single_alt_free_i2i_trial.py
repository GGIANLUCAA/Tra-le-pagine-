"""V193: safety, SHA chain and REAL image comparison without public provider calls."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import storia_rivive_v193_single_alt_free_i2i_trial as mod


def handoff():
    return {"version":"V191_TRUE_PHOTOGRAPHIC_I2I_PREPARATION",
            "i2i_generated":0,"vidu_generated":0,"publish_permitted":False,
            "source_raster_effective_unscaled_pixels":[603,1072],
            "film_source_sha256":"eacbb947105f9143632e3d4e933ee5e200ba98f5d588c11c552dfb94787de1d9",
            "photo_i2i_jobs":[
                {"scene":1},{"scene":2},
                {"scene":3,"source_file":mod.SCENE_NAME,"source_sha256":mod.SOURCE_SHA},
                {"scene":4}]
            }


class V193Tests(unittest.TestCase):
    def setUp(self):
        self.d=tempfile.TemporaryDirectory()
        self.addCleanup(self.d.cleanup)
        self.root=Path(self.d.name)
        self.source=self.root/mod.SCENE_NAME
        Image.new("RGB",(720,1280),(120,120,120)).save(self.source)
        self.manifest=self.root/"V191_PRODUCTION_HANDOFF.json"
        self.manifest.write_text(json.dumps(handoff()))
    def test_source_hash_constant_is_full_real_sha256(self):
        self.assertEqual(len(mod.SOURCE_SHA), 64)
        self.assertEqual(mod.SOURCE_SHA, "927dd324df4f88ef0dd12b31ccf0aade9fa901875ffcc5b688f74ecc57e1d32f")

    def test_actual_verification_requires_real_hash(self):
        with self.assertRaisesRegex(ValueError,"SOURCE_FRAME_SHA_CHANGED"):
            mod.verified_source(self.source,self.manifest)
    def test_strict_source_role(self):
        m=handoff();m['photo_i2i_jobs'][2]['scene']=4
        self.manifest.write_text(json.dumps(m))
        with patch.object(mod,'sha',return_value=mod.SOURCE_SHA):
            with self.assertRaisesRegex(ValueError,"SOURCE_ROLE_CHANGED"):
                mod.verified_source(self.source,self.manifest)
    def test_source_720x1280_probe(self):
        with patch.object(mod,'sha',return_value=mod.SOURCE_SHA):
            self.assertEqual(mod.verified_source(self.source,self.manifest)['scene'],3)
    def test_invalid_hand_off_cannot_start_provider(self):
        m=handoff();m['i2i_generated']=4
        self.manifest.write_text(json.dumps(m))
        with self.assertRaisesRegex(ValueError,"V191_SOURCE_HANDOFF_INVALID"):
            mod.verified_source(self.source,self.manifest)
    def test_run_wrong_source_no_directory_created_no_calls(self):
        with self.assertRaises(ValueError):
            mod.run(self.source,self.manifest,self.root/"out")
        self.assertFalse((self.root/"out").exists())
    def test_image_metric_on_real_local_png(self):
        original=self.root/"photo.png"
        Image.new("RGB",(1024,1536),(150,80,75)).save(original)
        measured=mod.source_similarity(self.source,original)
        self.assertIn("low_frequency_luma_correlation", measured)
        self.assertFalse(measured["subject_identity_artistically_verified"])
        self.assertGreaterEqual(measured["mean_saturation_0_255"],12)
    def test_reject_small_fake_i2i_png(self):
        small=self.root/"tiny.png"
        Image.new("RGB",(300,400),(255,0,0)).save(small)
        with self.assertRaisesRegex(ValueError,"I2I_TOO_SMALL"):
            mod.source_similarity(self.source,small)
    def test_never_assume_real_photo_or_user_approval(self):
        self.assertEqual(mod.SCENE,3)
        self.assertEqual(mod.SPACE,"JEYASEKHAR/QWEN_EDIT_IMAGE")


if __name__=="__main__":
    unittest.main()
