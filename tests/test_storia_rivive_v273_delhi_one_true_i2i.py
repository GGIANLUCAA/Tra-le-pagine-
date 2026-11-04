import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image,ImageOps

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import storia_rivive_v273_delhi_one_true_i2i as mod

class DelhiV273(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.original=self.root/mod.FRAME
        Image.effect_noise((1920,1080),30).convert("RGB").save(self.original)
        self.selection=self.root/"SELECTION.json"
        self.scout=self.root/"SCOUT.json"
        self.scout.write_text(json.dumps({
            "source_page":"https://commons.wikimedia.org/wiki/File:Ruins_of_Delhi_(1910).webm",
            "original_sha256":"test-film-sha",
            "status":"REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW"}))
        self.selection.write_text(json.dumps({
            "status":"FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW",
            "preselected":[{"filename":x} for x in mod.FRAME_ORDER],
            "candidate_segment_times_s":[9.486,66.401,mod.FRAME_TIME,199.204,218.176],
            "approved_restored_photos":0,"publish_permitted":False}))
        self.sha=mod.engine.sha(self.original)

    def patchsha(self):
        return (patch.object(mod,"FILM_SHA","test-film-sha"),
                patch.object(mod,"FRAME_SHA",self.sha))

    def test_source_preflight_five_distinct_actual_images_not_autoapproved(self):
        with self.patchsha()[0],self.patchsha()[1]:
            info=mod.verify_input(self.scout,self.selection,self.original)
        self.assertEqual(info["source_shot"],3)

    def test_forged_source_sha_rejected(self):
        with patch.object(mod,"FILM_SHA","test-film-sha"):
            with self.assertRaisesRegex(ValueError,"ORIGINAL_FRAME_SHA_CHANGED"):
                mod.verify_input(self.scout,self.selection,self.original)

    def test_changed_or_duplicated_selected_film_cut_rejected(self):
        selection=json.loads(self.selection.read_text())
        selection["preselected"][1]["filename"]=mod.FRAME
        self.selection.write_text(json.dumps(selection))
        with patch.object(mod,"FILM_SHA","test-film-sha"):
            with self.assertRaisesRegex(ValueError,"FIVE_SOURCE_SHOTS_CHANGED"):
                mod.verify_input(self.scout,self.selection,self.original)

    def test_one_genuine_image_bytes_does_not_certify_final(self):
        def fake_gen(crop,target):
            image=Image.effect_noise(mod.engine.MODEL_DIMS,35).convert("L")
            ImageOps.colorize(image,black="#443322",white="#d6c7ac").save(target)
        with patch.object(mod,"FILM_SHA","test-film-sha"),(
             patch.object(mod,"FRAME_SHA",self.sha)):
            report=mod.run(self.scout,self.selection,self.original,self.root/"out",fn=fake_gen)
        self.assertEqual(report["generated_photos"],1)
        self.assertEqual(report["status"],"ONE_TRUE_SOURCE_LOCKED_I2I_NEEDS_ARTISTIC_QA_NOT_FINAL")
        self.assertFalse(report["artistically_approved"])
        self.assertFalse(report["italian_rights_verified"])
        self.assertEqual(report["vidu_clips"],0)
        self.assertEqual(report["paid_credit_spend"],0)
        self.assertEqual(report["new_finished_mp4_zip"],0)
        self.assertFalse(report["publish_allowed"])

if __name__=="__main__":
    unittest.main()
