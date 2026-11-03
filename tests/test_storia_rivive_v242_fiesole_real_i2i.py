import base64
import hashlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import storia_rivive_v242_fiesole_real_i2i as mod

class V242SourceLockTests(unittest.TestCase):
    def test_reject_wrong_original_source_without_provider(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"bad.png"
            Image.new("RGB",(1920,1080),"gray").save(p)
            with self.assertRaisesRegex(ValueError,"HASH_MISMATCH"):
                mod.source_crop(p,Path(d)/"out")

    def test_crop_and_single_free_predict_only(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"source.png"
            # High-contrast patterns exercise a real 608x1080 PNG portrait crop.
            image=Image.new("RGB",(1920,1080))
            pixels=image.load()
            for y in range(1080):
                for x in range(1920):
                    pixels[x,y]=((x*7+y*3)%256,(x*2+y*11)%256,(x+y*13)%256)
            image.save(p)
            raw=ImageOps.fit(image,(608,1080),method=Image.Resampling.LANCZOS)
            expected_sha=hashlib.sha256(p.read_bytes()).hexdigest()
            buff=io.BytesIO()
            raw.save(buff,format="PNG")
            expected_crop=hashlib.sha256(buff.getvalue()).hexdigest()
            with patch.object(mod,"FILM_FRAME_SHA",expected_sha),patch.object(mod,"PORTRAIT_SHA",expected_crop):
                result=mod.run(p,Path(d)/"out",offline=True)
                self.assertEqual(result["provider_attempts"],0)
                self.assertFalse(result["final_mp4"])
                cropped=Path(d)/"out"/"FIESOLE_1912_FRAME_05_EXACT_CROP.png"
                self.assertEqual(mod.sha256(cropped),expected_crop)
                class Fake:
                    calls=0
                    def __init__(self,space,verbose=False):
                        self.space=space
                    def predict(self,**kwargs):
                        Fake.calls+=1
                        self.kwargs=kwargs
                        return {"status":"success","image":"data:image/png;base64,"+
                                base64.b64encode(buff.getvalue()).decode("ascii")}
                generated=Path(d)/"out"/"candidate.png"
                report=mod.try_free_once(cropped,generated,client_factory=Fake)
                self.assertEqual(Fake.calls,1)
                self.assertEqual(report["candidate_sha256"],expected_crop)
                self.assertTrue(generated.is_file())

    def test_reject_invalid_provider_payload(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/"bad.png"
            with self.assertRaisesRegex(ValueError,"NO_PNG"):
                mod.decode_response({"status":"success","image":"oops"},out)
            with self.assertRaisesRegex(ValueError,"NO_SUCCESS"):
                mod.decode_response({"status":"failed"},out)
            self.assertFalse(out.exists())

if __name__=="__main__":
    unittest.main()
