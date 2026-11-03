import io,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import storia_rivive_v256_fiesole_actual_i2i_geometry_qa as v

def inputs(root,shift=False):
    src=root/"original.png";candidate=root/"generated.png";report=root/"report.json"
    image=Image.new("RGB",(1920,1080))
    for y in range(1080):
        for x in range(656,1264,4):
            for xx in range(x,min(x+4,1264)):
                image.putpixel((xx,y),((x+y)//5%255,)*3)
    image.save(src)
    crop=image.crop((656,0,1264,1080)).resize((448,800))
    if shift:crop=Image.new("RGB",(448,800),(200,100,20))
    else:
        crop=crop.convert("RGB")
        # create realistic color without moving geometry
        r,g,b=crop.split()
        crop=Image.merge("RGB",(r,g.point(lambda x:min(255,int(x*.9+15))),b.point(lambda x:max(0,int(x*.75)))))
    crop.save(candidate)
    report.write_text(json.dumps({"original_source_sha256":v.sha(src),"source_time_s":v.SOURCE_TIME,
        "actual_generated_photos":1,"generated_sha256":v.sha(candidate),
        "real_vidu_clips":0,"artistic_approval":False,"publish_allowed":False}))
    return src,candidate,report

class TestV256(unittest.TestCase):
    def test_real_source_geometry_pass_does_not_approve(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            src,candidate,report=inputs(root)
            with patch.object(v,"ORIGINAL_SHA",v.sha(src)):
                result=v.assess(src,candidate,report,root/"out")
            self.assertTrue(result["source_geometry_screen_pass"])
            self.assertFalse(result["artistic_approval"])
            self.assertFalse(result["publish_allowed"])
            self.assertTrue((root/"out"/"V256_ACTUAL_V255_GEOMETRY_16_PATCH_REVIEW.jpg").is_file())
    def test_invented_scene_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            src,candidate,report=inputs(root,shift=True)
            with patch.object(v,"ORIGINAL_SHA",v.sha(src)):
                result=v.assess(src,candidate,report,root/"out")
            self.assertFalse(result["source_geometry_screen_pass"])
            self.assertEqual(result["new_final_episodes_delivered"],0)
    def test_modified_candidate_sha_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            src,candidate,report=inputs(root)
            candidate.write_bytes(candidate.read_bytes()+b"tamper")
            with patch.object(v,"ORIGINAL_SHA",v.sha(src)):
                with self.assertRaisesRegex(ValueError,"NOT_ONE_REAL_UNAPPROVED"):
                    v.assess(src,candidate,report,root/"out")
    def test_wrong_original_sha_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            src,candidate,report=inputs(root)
            with self.assertRaisesRegex(ValueError,"ORIGINAL_FRAME_SHA_MISMATCH"):
                v.assess(src,candidate,report,root/"out")
if __name__=="__main__":unittest.main()
