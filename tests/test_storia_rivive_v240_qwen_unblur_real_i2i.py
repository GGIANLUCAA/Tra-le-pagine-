import base64,hashlib,io,random,sys,tempfile,unittest
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import storia_rivive_v240_qwen_fast_real_i2i as mod

class V240Test(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.src=self.root/"source.png"
        Image.new("RGB",(608,1080),"gray").save(self.src)
    def test_sha_lock_blocks_wrong_source(self):
        with self.assertRaisesRegex(ValueError,"SHA_MISMATCH"):
            mod.validate_source(self.src)
    def test_provider_result_must_be_decodable_image(self):
        with self.assertRaisesRegex(ValueError,"NOT_PNG_DATA_URI"):
            mod.extract_result({"status":"success","image":"hello"},self.root/"x.png")
        with self.assertRaisesRegex(ValueError,"NO_SUCCESSFUL_IMAGE"):
            mod.extract_result({"status":"error","image":None},self.root/"x.png")
    def test_one_predict_only_and_source_geometry(self):
        out=self.root/"result.png"
        b=io.BytesIO()
        pixels=random.Random(14).randbytes(608*1080*3)
        Image.frombytes("RGB",(608,1080),pixels).save(b,format="PNG")
        response={"status":"success","image":"data:image/png;base64,"+base64.b64encode(b.getvalue()).decode()}
        class Fake:
            calls=[]
            def __init__(self,space,verbose):self.space=space
            def predict(self,**kwargs):
                self.calls.append(kwargs)
                return response
        original=mod.validate_source
        try:
            mod.validate_source=lambda path:original(path,hashlib.sha256(path.read_bytes()).hexdigest())
            r=mod.one_free_attempt(self.src,out,client_factory=Fake)
        finally:
            mod.validate_source=original
        self.assertEqual(len(Fake.calls),1)
        self.assertEqual(Fake.calls[0]["api_name"],"/edit_image")
        self.assertEqual(Fake.calls[0]["lora_adapter"],"Unblur-Anything")
        self.assertEqual(Fake.calls[0]["steps"],4)
        self.assertEqual(r["generated_sha256"],hashlib.sha256(out.read_bytes()).hexdigest())
        self.assertEqual(r["new_real_i2i_candidates"],1)

if __name__=="__main__":unittest.main()
