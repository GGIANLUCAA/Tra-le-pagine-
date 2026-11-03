"""V257: SHA lock, real candidate visual metrics, no fake final or spending."""
import json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image,ImageDraw
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import storia_rivive_v257_fiesole_local_cpu_diffusion_i2i as m

class V257LocalDiffusion(unittest.TestCase):
    def make_original(self,p):
        im=Image.effect_noise((1920,1080),70).convert("RGB")
        im.save(p)
    def test_reject_wrong_original(self):
        with tempfile.TemporaryDirectory() as t:
            src=Path(t)/"auth.png"
            self.make_original(src)
            with self.assertRaisesRegex(ValueError,"SOURCE_FRAME_SHA_MISMATCH"):
                m.check_source(src)
    def test_locked_original_creates_real_608x1080_crop(self):
        with tempfile.TemporaryDirectory() as t:
            src=Path(t)/"auth.png";out=Path(t)/"crop.png"
            self.make_original(src)
            with patch.object(m,"SOURCE_SHA",m.sha(src)):
                result=m.crop_source(src,out)
            self.assertEqual(result,m.sha(out))
            self.assertEqual(Image.open(out).size,(608,1080))
    def test_photo_qa_never_claims_final(self):
        with tempfile.TemporaryDirectory() as t:
            t=Path(t);src=t/"auth.png";out=t/"generated.png"
            Image.effect_noise((608,1080),75).convert("RGB").save(src)
            Image.effect_noise(m.MODEL_DIMS,78).convert("RGB").save(out)
            metrics=m.inspect_candidate(src,out)
            self.assertTrue(metrics["genuine_diffusion_i2i"])
            self.assertFalse(metrics["human_artistic_approved"])
            self.assertFalse(metrics["italy_rights_verified"])
            self.assertFalse(metrics["publish_allowed"])
            self.assertFalse(metrics["final_video"])
            self.assertEqual(metrics["vidu_count"],0)
    def test_missing_model_result_is_never_counted(self):
        with tempfile.TemporaryDirectory() as t:
            src=Path(t)/"src.png"
            Image.new("RGB",(608,1080),"white").save(src)
            with self.assertRaisesRegex(ValueError,"NO_ACTUAL_MODEL_PHOTO"):
                m.inspect_candidate(src,Path(t)/"not-generated.png")

if __name__=="__main__":unittest.main()
