"""V278 offline fake-provider tests: no API or paid call, five exact source SHAs."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image,ImageOps

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import storia_rivive_v278_delhi_four_ddcolor_finegrain as v

class V278(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.frames=self.root/"frames"
        self.frames.mkdir()
        self.entries=[]
        for i in range(1,6):
            name=f"frame_{i:02d}.png"
            image=Image.effect_noise((1920,1080),36).convert("RGB")
            image.save(self.frames/name)
            self.entries.append((i,name,v.digest(self.frames/name),f"Real scene {i} from historic archive"))
        self.scout=self.root/"SCOUT_REPORT.json"
        self.scout.write_text(json.dumps({"status":"REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW",
            "source_page":v.PAGE,"original_sha256":"synthetic-test-film"}))
        self.selection=self.root/"SHOT_AWARE_SELECTION_V210.json"
        self.selection.write_text(json.dumps({
            "status":"FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW",
            "preselected":[{"filename":e[1]} for e in self.entries],
            "approved_restored_photos":0,"publish_permitted":False}))
    def patch_source(self):
        from contextlib import ExitStack
        stack=ExitStack()
        stack.enter_context(patch.object(v,"FILM_SHA","synthetic-test-film"))
        stack.enter_context(patch.object(v,"SHOTS",self.entries[:4]))
        stack.enter_context(patch.object(v,"VIDU_ANCHOR",self.entries[4][:3]))
        return stack

    def test_exact_five_frames_verified_and_not_auto_approved(self):
        with self.patch_source():
            x=v.verify_sources(self.frames,self.scout,self.selection)
        self.assertEqual(x["verified_unique_frames"],5)

    def test_modified_source_is_rejected_before_any_inference(self):
        with self.patch_source():
            Image.new("RGB",(1920,1080),"white").save(self.frames/"frame_01.png")
            with self.assertRaisesRegex(ValueError,"FRAME_SHA_CHANGED"):
                v.verify_sources(self.frames,self.scout,self.selection)

    def test_offline_does_not_generate_or_publish(self):
        with self.patch_source():
            r=v.run(self.frames,self.scout,self.selection,self.root/"out",offline=True)
        self.assertEqual(r["finegrain_provider_attempts"],0)
        self.assertEqual(len(r["real_photo_files"]),0)
        self.assertFalse(r["final_mp4"])
        self.assertFalse(r["publish_allowed"])

    def test_four_real_new_files_never_claim_human_approval(self):
        from PIL import ImageEnhance
        def fake_dd(src,out):
            with Image.open(src) as im:
                shade=ImageOps.colorize(ImageOps.grayscale(ImageOps.fit(im,(540,960))),black="#303742",white="#e6dfcf")
                shade.save(out)
        def fake_finegrain(base,prompt,seed):
            target=self.root/f"fake_{seed}.png"
            with Image.open(base) as im:
                ImageEnhance.Color(im).enhance(1.15).save(target)
            return target
        with self.patch_source():
            r=v.run(self.frames,self.scout,self.selection,self.root/"out",
                    make_base=fake_dd,model_predict=fake_finegrain)
        self.assertEqual(len(r["real_photo_files"]),4)
        self.assertEqual(r["finegrain_provider_attempts"],4)
        self.assertFalse(r["final_mp4"])
        self.assertFalse(r["final_zip"])
        self.assertFalse(r["italian_rights_verified"])
        self.assertFalse(r["artistic_approval"])
        self.assertEqual(r["vidu_credits_used"],0)
        self.assertEqual(r["new_final_episodes_delivered"],0)

if __name__=="__main__":
    unittest.main()
