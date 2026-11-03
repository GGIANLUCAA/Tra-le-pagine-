import sys,tempfile,json,unittest
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from storia_rivive_v251_fiesole_photo_source_handoff import export

class TestV251(unittest.TestCase):
    def test_fail_closed_without_real_five_shot_selection(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/"s.json").write_text(json.dumps({"status":"NOT_FINAL","preselected":[]}))
            (root/"a.json").write_text(json.dumps({"checks":[]}))
            with self.assertRaisesRegex(ValueError,"FIVE_REAL_V249_SOURCE_SHOTS_REQUIRED"):
                export(root/"s.json",root/"a.json",root,root/"out")
    def test_reject_fake_source_hash_before_any_export(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            frames=root/"frames";frames.mkdir()
            for i in range(5):
                Image.new("RGB",(1280,720),"white").save(frames/f"frame_{i}.png")
            rows=[{"filename":f"frame_{i}.png"} for i in range(5)]
            checks=[{"source_frame":f"frame_{i}.png","source_frame_sha256":"0"*64,
                     "selected_timecode_s":10+i,"endpoint_visually_aligned":True} for i in range(5)]
            (root/"s.json").write_text(json.dumps({"status":"FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW",
                    "preselected":rows,"candidate_segment_times_s":[10+i for i in range(5)]}))
            (root/"a.json").write_text(json.dumps({"checks":checks}))
            with self.assertRaisesRegex(ValueError,"SOURCE_IMAGE_HASH_MISMATCH"):
                export(root/"s.json",root/"a.json",frames,root/"out")
            self.assertFalse((root/"out"/"FIESOLE_V251_FIVE_AUTHENTIC_SOURCE_FRAMES_NOT_FINAL.zip").exists())

if __name__=="__main__":unittest.main()
