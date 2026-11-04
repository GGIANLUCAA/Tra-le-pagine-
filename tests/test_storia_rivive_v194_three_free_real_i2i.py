"""V194: offline real-PNG verification tests, no provider call."""
import json,sys,tempfile,hashlib
from pathlib import Path
import unittest
from PIL import Image

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import storia_rivive_v194_three_free_real_i2i as v194


class V194Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        entries=[]
        for s in (1,2,3,4):
            name=f"scene_{s:02}.png"
            path=self.root/name
            im=Image.new("RGB",(720,1280),(s*40,100,130))
            im.save(path)
            entries.append({"scene":s,"source_file":name,
                            "source_sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
        self.manifest={"version":"V191_TRUE_PHOTOGRAPHIC_I2I_PREPARATION",
                       "film_source_sha256":v194.FILM_SHA,
                       "i2i_generated":0,"vidu_generated":0,
                       "publish_permitted":False,"photo_i2i_jobs":entries}
        (self.root/"V191_PRODUCTION_HANDOFF.json").write_text(json.dumps(self.manifest))
    def test_real_four_png_sha_source_locked(self):
        rows=v194.verify_handoff(self.root)
        self.assertEqual(set(v194.SCENES),{1,2,4})
        self.assertEqual(set(rows),{1,2,3,4})
    def test_tampered_source_rejected(self):
        (self.root/"scene_04.png").write_bytes(b"garbage")
        with self.assertRaisesRegex(ValueError,"SOURCE_SHA_MISMATCH"):
            v194.verify_handoff(self.root)
    def test_fake_approved_status_rejected(self):
        self.manifest["i2i_generated"]=4
        (self.root/"V191_PRODUCTION_HANDOFF.json").write_text(json.dumps(self.manifest))
        with self.assertRaisesRegex(ValueError,"V191_HANDOFF_INVALID"):
            v194.verify_handoff(self.root)
    def test_comparison_real_png_no_auto_approval(self):
        src=self.root/"scene_01.png"
        out=self.root/"photo.png"
        Image.new("RGB",(720,1280),(70,150,65)).save(out)
        m=v194.assess(src,out)
        self.assertFalse(m["scene_identity_visual_qa_approved"])
        self.assertIn("coarse_luma_correlation",m)
        self.assertIn("mean_saturation",m)

if __name__=="__main__":
    unittest.main()
