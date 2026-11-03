"""V233 no fake final, exact source and source-locked I2I only."""
import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import storia_rivive_v233_three_real_i2i_visual_review as v

class V233ReviewContract(unittest.TestCase):
    def test_duration_and_photo_timing(self):
        self.assertEqual(v.DURATION,28.5)
        self.assertAlmostEqual(v.LEAD+v.HOLD+v.PHOTO,v.SCENE)
        self.assertGreaterEqual(v.PHOTO,2.5)
    def test_reject_tampered_source_video(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"test.mp4";p.write_bytes(b"fake")
            with self.assertRaisesRegex(ValueError,"V231_SOURCE_VIDEO_SHA_CHANGED"):
                v.verify(p,{"video_sha256":"0"*64},{},{},Path(td))
    def test_no_fake_four_i2i_approval(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"test.mp4";p.write_bytes(b"fake")
            report={"video_sha256":v.sha(p),"film_sha256":"abc","episode_id":"test",
                    "source_starts_s":[1,2,3,4,5]}
            lock={"film_sha256":"abc","episode_id":"test",
                  "frames":[{"frame":"x"}]*4,"italian_rights_approved":False}
            results={"episode_id":"test","target_photos":4,"real_i2i_candidates":4,
                     "vidu_clips":0,"final_4_plus_1_mp4":False}
            with self.assertRaisesRegex(ValueError,"UNSAFE_REVIEW_STATE"):
                v.verify(p,report,lock,results,Path(td))
if __name__=="__main__":unittest.main()
