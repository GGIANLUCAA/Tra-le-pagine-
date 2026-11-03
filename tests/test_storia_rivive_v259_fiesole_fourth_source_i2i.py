"""V259 fourth-frame source-lock regression tests; never count offline as photo."""
import json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import storia_rivive_v259_fiesole_fourth_source_i2i as m

class V259FourthSource(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.src=self.root/"original_shot_04_frame_07.png"
        Image.new("RGB",(1920,1080),"gray").save(self.src)
        self.sha=m.engine.sha(self.src)
        self.manifest=self.root/"manifest.json"
        self.data={"version":"V251_FIESOLE_SOURCE_LOCKED_PHOTO_HANDOFF",
            "episode":"fiesole_straw_hats_1912_v220",
            "source_film_sha256":"f87ca5d51a1ba4b60ffb0e5db6162f3b0afadcd3bf3b94393dcf66337a7af7fe",
            "shots":[{"shot":i,"role":"I2I_PHOTO_SOURCE",
                      "original_frame":"frame_07.png" if i==4 else "other.png",
                      "original_sha256":self.sha if i==4 else "0"*64,
                      "archive_filename":self.src.name if i==4 else "other.png",
                      "source_frame_locked":True,"source_time_s":float(i)}
                     for i in range(1,6)]}
        self.manifest.write_text(json.dumps(self.data))
    def test_real_sha_and_manifest_required(self):
        with patch.object(m,"SOURCE_SHA",self.sha):
            self.assertEqual(m.verify_manifest(self.manifest,self.src)["shot"],4)
    def test_reject_wrong_frame_sha(self):
        with self.assertRaisesRegex(ValueError,"SHOT_FOUR_NOT_AUTHENTIC"):
            m.verify_manifest(self.manifest,self.src)
    def test_reject_wrong_film(self):
        self.data["source_film_sha256"]="0"*64
        self.manifest.write_text(json.dumps(self.data))
        with patch.object(m,"SOURCE_SHA",self.sha):
            with self.assertRaisesRegex(ValueError,"WRONG_FILM_OR_EPISODE"):
                m.verify_manifest(self.manifest,self.src)
    def test_reject_different_shot(self):
        self.data["shots"][3]["shot"]=5
        self.manifest.write_text(json.dumps(self.data))
        with patch.object(m,"SOURCE_SHA",self.sha):
            with self.assertRaisesRegex(ValueError,"SHOT_FOUR_NOT_AUTHENTIC"):
                m.verify_manifest(self.manifest,self.src)

if __name__=="__main__":unittest.main()
