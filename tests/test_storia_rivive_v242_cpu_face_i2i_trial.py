import sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import storia_rivive_v242_cpu_face_i2i_trial as m

class V242FreeCpuI2I(unittest.TestCase):
    def test_source_lock_rejects_tampering(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"s.png"
            Image.new("L",(608,1080),128).save(p)
            with self.assertRaisesRegex(ValueError,"SHA_MISMATCH"):
                m.verify_source(p)
    def test_actual_image_output_not_identity_no_fake_final(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"s.png";r=Path(d)/"out.png"
            Image.new("L",(608,1080),130).save(p)
            Image.new("RGB",(608,1080),(70,100,130)).save(r)
            with patch.object(m,"SOURCE_SHA",m.digest(p)):
                data=m.verify_result(p,r)
            self.assertEqual(data["real_cpu_model_candidate"],1)
            self.assertFalse(data["final_episode"])
            self.assertFalse(data["artistic_QA_approved"])
            self.assertFalse(data["publish_allowed"])
    def test_provider_cannot_pass_through_source(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"s.png"
            Image.new("L",(608,1080),140).save(p)
            with patch.object(m,"SOURCE_SHA",m.digest(p)):
                with self.assertRaisesRegex(ValueError,"ORIGINAL_NOT_I2I"):
                    m.verify_result(p,p)
    def test_api_output_not_fabricated_from_bad_response(self):
        with self.assertRaisesRegex(ValueError,"NO_DOWNLOADABLE_IMAGE"):
            m.unwrap_result({"foo":"bar"})
if __name__=="__main__":unittest.main()
