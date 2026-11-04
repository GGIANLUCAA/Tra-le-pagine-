import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import storia_rivive_visual_reject_v288 as gate

EP="delhi_ruins_1910_v217"
SRC="28a71dff0d65a4529a946fbe1d531626c70dca389d344e4d17f7646022fc8ca2"
BAD="556c432960bea3fd58663ac85ad77e792463fbcca1a92f3bb1b0616195a10264"
GOOD="a"*64

class EditorialV288(unittest.TestCase):
    def test_real_user_rejected_anatomical_fusion_blocks_photo(self):
        result=gate.inspect(EP,SRC,BAD)
        self.assertEqual(result["status"],"REJECT_REPLACE_FRAME")
        self.assertFalse(result["approved"])
        with self.assertRaisesRegex(ValueError,"V288_REJECTED_VISIBLE_HUMAN_ANIMAL_FUSION"):
            gate.require_safe_for_photo(EP,SRC,BAD)

    def test_switching_model_or_photo_does_not_reapprove_same_unsafe_source(self):
        result=gate.inspect(EP,SRC,GOOD)
        self.assertEqual(result["status"],"REJECT_REPLACE_FRAME")

    def test_original_bw_film_can_still_be_used_without_approving_restoration(self):
        result=gate.inspect(EP,SRC,role="original_bw_motion")
        self.assertEqual(result["status"],"ORIGINAL_BW_MOTION_ONLY_WITHOUT_COLOR_APPROVAL")
        self.assertFalse(result["approved"])

    def test_vidu_source_is_blocked_until_new_safer_frame(self):
        self.assertEqual(gate.inspect(EP,SRC,role="vidu_source")["status"],"REJECT_REPLACE_FRAME")

    def test_unknown_frame_not_spuriously_approved(self):
        result=gate.inspect(EP,GOOD,GOOD)
        self.assertEqual(result["status"],"UNKNOWN_NEEDS_ARTISTIC_VISUAL_QA")
        self.assertFalse(result["approved"])
        self.assertFalse(result["publish_allowed"])

    def test_tampered_ledger_rejected(self):
        data=gate.read_ledger()
        data["rejections"][0]["human_artistic_approved"]=True
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"fake.json"
            p.write_text(json.dumps(data),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"V288_UNSAFE_REJECTION_POLICY"):
                gate.inspect(EP,SRC,BAD,ledger_path=p)

    def test_untrusted_role_and_hash_do_not_pass(self):
        with self.assertRaises(ValueError):
            gate.inspect(EP,"none",role="photo")
        with self.assertRaises(ValueError):
            gate.inspect(EP,SRC,role="auto_approved")

if __name__=="__main__":
    unittest.main()
