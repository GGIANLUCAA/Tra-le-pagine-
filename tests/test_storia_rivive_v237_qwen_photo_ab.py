import sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import storia_rivive_v237_qwen_photo_ab as m

class V237PhotoABTests(unittest.TestCase):
    def test_no_auto_approval_or_credit(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            source=p/'source.png';prior=p/'prior.png'
            Image.new('RGB',(608,1080),'gray').save(source)
            Image.new('RGB',(608,1080),'orange').save(prior)
            with patch.object(m,'SOURCE_SHA256',m.sha(source)),patch.object(m,'PRIOR_SHA256',m.sha(prior)):
                r=m.baseline_report(source,prior)
                self.assertFalse(r['paid_credit_spend_allowed'])
                self.assertFalse(r['final_mp4'])
                self.assertFalse(r['publish_allowed'])
                self.assertEqual(r['new_final_episodes_delivered'],0)
                self.assertEqual(r['mode'],'ANONYMOUS_PUBLIC_SPACE_FREE_QUOTA_ONLY_NO_HF_TOKEN')
    def test_sha_lock_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);a=p/'a.png';b=p/'b.png'
            Image.new('RGB',(608,1080),'gray').save(a)
            Image.new('RGB',(608,1080),'gray').save(b)
            with self.assertRaisesRegex(ValueError,'SHA_CHANGED'):
                m.check_source(a,b)
    def test_real_image_comparison_only_after_byte_check(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);a=p/'a.png';b=p/'b.png';c=p/'c.png'
            Image.new('RGB',(608,1080),'gray').save(a)
            Image.new('RGB',(608,1080),'orange').save(b)
            Image.effect_noise((768,1365),45).convert('RGB').save(c)
            result=m.make_ab(a,b,c,p)
            self.assertEqual(result['new_real_i2i_candidates'],1)
            self.assertTrue((p/'V237_REAL_QWEN_VS_REJECTED_FINEGRAIN.jpg').is_file())
            self.assertEqual(result['images'][2]['sha256'],m.sha(c))
if __name__=='__main__':unittest.main()
