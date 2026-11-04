import json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image,ImageOps
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import storia_rivive_v283_delhi_shot5_photo_anchor as mod

class FifthPhoto(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.d=Path(self.tmp.name)
        self.src=self.d/mod.FRAME
        Image.effect_noise((1920,1080),19).convert("RGB").save(self.src)
        self.hash=mod.sha(self.src)
    def test_source_wrong_sha_fails(self):
        with self.assertRaisesRegex(ValueError,"SOURCE_FIFTH_FRAME_SHA_INVALID"):
            mod.source_check(self.src)
    def test_exact_crop_free_plan_never_authorizes(self):
        with patch.object(mod,"FRAME_SHA",self.hash):
            o=mod.run(self.src,self.d/"out",offline=True)
        self.assertEqual(o["original_crop_bbox_px"],[750,0,1358,1080])
        self.assertEqual(o["original_source_frame_sha256"],self.hash)
        self.assertFalse(o["five_second_vidu_clip_generated"])
        self.assertFalse(o["credit_balance_approved"])
        self.assertFalse(o["subject_reviewed_by_user"])
        self.assertEqual(o["master_videos_finished"],0)
        self.assertFalse(o["publication_allowed"])
        with Image.open(self.d/"out"/"DELHI_1910_SHOT05_EXACT_SOURCE_BW_FOR_VIDU_REVIEW.jpg") as im:
            self.assertEqual(im.size,(720,1280))
    def test_real_candidate_image_does_not_approve_or_claim_vidu(self):
        def base(inp,out):
            Image.new("RGB",(540,960),(128,131,136)).save(out)
        def fake_predict(img,prompt,seed):
            self.assertLessEqual(seed,10000)
            result=self.d/"result.jpg"
            Image.effect_noise((720,1280),30).convert("RGB").save(result,quality=95)
            return result
        with patch.object(mod,"FRAME_SHA",self.hash):
            status=mod.run(self.src,self.d/"photos",predict=fake_predict,make_base=base)
        self.assertTrue(status["scene5_photo_generated"])
        self.assertEqual(status["vidu_credits_spent"],0)
        self.assertFalse(status["five_second_vidu_clip_generated"])
        self.assertFalse(status["scene5_photo_artistically_approved"])
        self.assertFalse(status["subject_reviewed_by_user"])
        self.assertEqual(status["master_videos_finished"],0)
        self.assertTrue((self.d/"photos"/"DELHI_V283_ACTUAL_ORIGINAL_VS_NEW_PHOTO_QA.jpg").is_file())
        self.assertEqual(mod.sha(self.d/"photos"/status["generated_photo_filename"]),status["generated_photo_sha256"])

if __name__=="__main__":unittest.main()
