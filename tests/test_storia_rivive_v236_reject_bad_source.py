import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from storia_rivive_v236_reject_bad_source import gate,REJECTED_SHA256

class BadSourceGate(unittest.TestCase):
    def test_watermark_cannot_be_overridden_by_rights_or_shots(self):
        x=gate(REJECTED_SHA256,5,True,True)
        self.assertFalse(x["allow_generation"])
        self.assertIn("FRAMEPOOL_WATERMARKED_TRANSFER_REJECTED_V235",x["reasons"])
    def test_unverified_source_stays_blocked(self):
        x=gate("a"*64,5,False,False)
        self.assertFalse(x["allow_generation"])
        self.assertFalse(x["credits_allowed"])
    def test_qualified_clean_source_is_eligible_only_not_spend_approved(self):
        x=gate("b"*64,5,True,True)
        self.assertTrue(x["allow_generation"])
        self.assertFalse(x["credits_allowed"])
        self.assertFalse(x["publication_allowed"])
if __name__=="__main__": unittest.main()
