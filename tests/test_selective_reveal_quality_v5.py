"""Offline tests: original pixels and existing masters are never overwritten."""
import importlib.util,sys,tempfile,unittest
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
def load(path):
    spec=importlib.util.spec_from_file_location(path.stem,path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod
FX=load(ROOT/"experiments/creative_reveals/selective_nautilus_v5.py")
GATE=load(ROOT/"experiments/creative_reveals/reveal_quality_gate_v5.py")

class TestSelectiveReveal(unittest.TestCase):
    def source(self,root):
        path=Path(root)/"scene.png"
        base=np.empty((1536,1024,3),np.uint8)
        base[:,:]=(50,120,165)
        base[350:860,60:1015]=(155,124,83)
        Image.fromarray(base).save(path)
        return path
    def test_no_whole_image_replacement(self):
        with tempfile.TemporaryDirectory() as root:
            src=self.source(root)
            before=FX.checksum(src)
            loaded=FX.load_still(src)
            maps=FX.prepare(loaded)
            early=FX.frame(maps,0,"effect")
            late=FX.frame(maps,13,"effect")
            self.assertTrue(np.array_equal(FX.frame(maps,5,"clean"),loaded))
            self.assertTrue(np.array_equal(early[170,100],loaded[170,100]))
            self.assertFalse(np.array_equal(early[405,260],loaded[405,260]))
            self.assertEqual(FX.checksum(src),before)
            self.assertEqual(late.shape,(960,540,3))
    def test_reject_unreviewed_geometry(self):
        with tempfile.TemporaryDirectory() as root:
            src=Path(root)/"bad.png"
            Image.new("RGB",(1000,1000)).save(src)
            with self.assertRaises(ValueError):FX.load_still(src)
    def test_preserve_existing_output(self):
        with tempfile.TemporaryDirectory() as root:
            source=self.source(root);audio=Path(root)/"voice.wav";audio.write_bytes(b"demo")
            output=Path(root)/"approved.mp4";output.write_bytes(b"approved")
            with self.assertRaises(FileExistsError):FX.render(source,audio,output)
            self.assertEqual(output.read_bytes(),b"approved")
    def test_quality_gate_marks_estimated_timing(self):
        plan={"status":"experiment","source_is_master":False,
              "source_image_reviewed":True,"format":"libri",
              "voice_alignment":{"method":"estimated"},
              "scenes":[{"effect":"blueprint_to_color","story_reason":"submarine discovery",
              "narration_anchor":"Attraverso enormi finestre",
              "shot_duration_seconds":14.32,"effect_start_relative_seconds":1.65,
              "effect_duration_seconds":3.65,"effect_target":"whole_subject",
              "source_image_stays_opaque":True}]}
        result=GATE.evaluate(plan)
        self.assertTrue(result["private_preview_allowed"])
        self.assertFalse(result["voice_alignment_verified"])
        self.assertFalse(result["ready_for_publication"])
        plan["scenes"][0]["effect_duration_seconds"]=30
        self.assertFalse(GATE.evaluate(plan)["structural_pass"])
    def test_no_museum_repainting(self):
        plan={"status":"experiment","source_is_master":False,"source_image_reviewed":True,
              "format":"artvision_cinema","voice_alignment":{"method":"estimated"},
              "scenes":[{"effect":"object_reveal","story_reason":"test",
              "narration_anchor":"test","shot_duration_seconds":10,
              "effect_start_relative_seconds":1,"effect_duration_seconds":3,
              "effect_target":"whole_subject","source_image_stays_opaque":True}]}
        self.assertFalse(GATE.evaluate(plan)["private_preview_allowed"])

if __name__=="__main__":unittest.main()
