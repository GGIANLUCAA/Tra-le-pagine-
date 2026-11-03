import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from storia_rivive_v255_real_i2i_byte_qa import assess

class V255RealI2IByteTests(unittest.TestCase):
    def fixtures(self,root,output_color=True):
        src=root/"source.png"
        dst=root/"candidate.png"
        Image.new("RGB",(512,896),(120,120,120)).save(src)
        if output_color:
            img=Image.new("RGB",(512,896),(90,145,185))
        else:
            img=Image.new("RGB",(512,896),(120,120,120))
        img.save(dst)
        manifest={"status":"ONE_TRUE_LOCAL_I2I_PHOTO_NEEDS_ARTISTIC_REVIEW_NOT_FINAL",
                  "new_generated_i2i":1,"provider_requests":0,"vidu_credit_spend":0,
                  "publish_allowed":False,"final_mp4":False,
                  "source_crop_sha256":hashlib.sha256(src.read_bytes()).hexdigest(),
                  "candidate_sha256":hashlib.sha256(dst.read_bytes()).hexdigest()}
        report=root/"manifest.json"
        report.write_text(json.dumps(manifest))
        return src,dst,report

    def test_real_color_candidate_passes_technical_not_artistic(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            src,dst,report=self.fixtures(root)
            result=assess(src,dst,report,root/"qa.json")
            self.assertTrue(result["technical_candidate_pass"])
            self.assertFalse(result["human_artistic_approved"])
            self.assertFalse(result["final_mp4"])
            self.assertFalse(result["publish_allowed"])
            self.assertEqual(result["new_final_episodes_delivered"],0)

    def test_grayscale_unchanged_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            src,dst,report=self.fixtures(root,False)
            result=assess(src,dst,report,root/"qa.json")
            self.assertFalse(result["technical_candidate_pass"])

    def test_tampered_generated_image_fails_sha(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            src,dst,report=self.fixtures(root)
            Image.new("RGB",(512,896),(1,2,3)).save(dst)
            with self.assertRaisesRegex(ValueError,"HASH_MISMATCH"):
                assess(src,dst,report,root/"qa.json")

    def test_unverified_generation_cannot_pass(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            src,dst,report=self.fixtures(root)
            obj=json.loads(report.read_text())
            obj["new_generated_i2i"]=0
            report.write_text(json.dumps(obj))
            with self.assertRaisesRegex(ValueError,"NO_VERIFIED_REAL"):
                assess(src,dst,report,root/"qa.json")

if __name__=="__main__":unittest.main()
