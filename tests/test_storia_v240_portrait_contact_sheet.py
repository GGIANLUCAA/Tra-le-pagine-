import json,sys,tempfile,unittest
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from storia_v240_portrait_contact_sheet import make_sheet

class TestV240(unittest.TestCase):
    def test_five_original_frames_and_duplicate_block(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); frames=root/"frames";frames.mkdir()
            rows=[]
            for i in range(1,6):
                name=f"frame_{i:02d}.png"
                Image.new("RGB",(640,480),(i*25,i*20,i*15)).save(frames/name)
                rows.append({"filename":name})
            manifest=root/"selection.json"
            def write():
                manifest.write_text(json.dumps({"status":"FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW","preselected":rows}))
            write()
            result=make_sheet(manifest,frames,root/"out")
            self.assertEqual(len(result),5)
            self.assertTrue((root/"out/FIVE_PORTRAIT_SOURCE_CROPS_V240.jpg").is_file())
            report=json.loads((root/"out/FIVE_PORTRAIT_SOURCE_CROPS_V240.json").read_text())
            self.assertFalse(report["rights_approved"])
            self.assertFalse(report["vidu_generated"])
            rows[4]=rows[0];write()
            with self.assertRaisesRegex(ValueError,"DUPLICATE"):
                make_sheet(manifest,frames,root/"out")
if __name__=="__main__":unittest.main()
