import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import storia_rivive_v276_delhi_shot02_true_i2i as v276

class DelhiV276(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.original = self.directory / "frame_04.png"
        Image.effect_noise((1920,1080),25).convert("RGB").save(self.original)
        self.source_hash = v276.sha(self.original)
        self.scout = self.directory / "SCOUT_REPORT.json"
        self.selection = self.directory / "SELECTION.json"
        self.scout.write_text(json.dumps({
            "source_page":v276.SOURCE_PAGE,
            "original_sha256":"test-film-sha",
            "status":"REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW"
        }))
        self.selection.write_text(json.dumps({
            "status":"FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW",
            "preselected":[{"filename":f} for f in v276.FRAMES],
            "candidate_segment_times_s":[9.486,66.401,104.345,199.204,218.176],
            "approved_restored_photos":0,
            "publish_permitted":False
        }))

    def test_exact_source_preflight_and_offline_has_zero_photos(self):
        with patch.object(v276,"FILM_SHA","test-film-sha"),patch.object(v276,"FRAME_SHA",self.source_hash):
            r=v276.run(self.scout,self.selection,self.original,self.directory/"out",offline=True)
        self.assertEqual(r["source_frame"],"frame_04.png")
        self.assertEqual(r["generated_photos"],0)
        self.assertEqual(r["new_finished_mp4_zip"],0)
        self.assertFalse(r["publication_allowed"])

    def test_wrong_frame_rejected(self):
        with patch.object(v276,"FILM_SHA","test-film-sha"):
            with self.assertRaisesRegex(ValueError,"V276_FRAME_HASH_MISMATCH"):
                v276.verify(self.scout,self.selection,self.original)

    def test_changed_frame_selection_rejected(self):
        m=json.loads(self.selection.read_text())
        m["preselected"][1]["filename"]="frame_06.png"
        self.selection.write_text(json.dumps(m))
        with patch.object(v276,"FILM_SHA","test-film-sha"),patch.object(v276,"FRAME_SHA",self.source_hash):
            with self.assertRaisesRegex(ValueError,"V276_SOURCE_SELECTION_CHANGED"):
                v276.verify(self.scout,self.selection,self.original)

    def test_real_image_bytes_never_claim_artistic_approval_or_video(self):
        def fake_real_image(crop,target):
            ImageOps.colorize(
                Image.effect_noise(v276.metrics.MODEL_DIMS,18).convert("L"),
                "#354954","#d5ad7a"
            ).save(target)
        with patch.object(v276,"FILM_SHA","test-film-sha"),patch.object(v276,"FRAME_SHA",self.source_hash):
            r=v276.run(self.scout,self.selection,self.original,self.directory/"out",generator=fake_real_image)
        self.assertEqual(r["generated_photos"],1)
        self.assertFalse(r["human_artistic_approved"])
        self.assertFalse(r["artistically_approved"])
        self.assertFalse(r["italian_rights_verified"])
        self.assertEqual(r["real_vidu_clips"],0)
        self.assertEqual(r["paid_credits_spent"],0)
        self.assertEqual(r["new_finished_mp4_zip"],0)
        self.assertTrue((self.directory/"out"/v276.SHEET_NAME).is_file())
        self.assertEqual(r["generated_sha256"],v276.sha(self.directory/"out"/v276.OUT_NAME))

if __name__=="__main__":
    unittest.main()
