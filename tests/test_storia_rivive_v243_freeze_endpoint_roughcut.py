import hashlib,json,sys,tempfile,unittest
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from storia_rivive_v243_freeze_endpoint_roughcut import load_plan

class FreezeEndpointTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.frames=self.root/"frames";self.frames.mkdir()
        self.rows=[];self.checks=[]
        self.times=[10.,20.,30.,40.,50.]
        for i,t in enumerate(self.times,1):
            name=f"frame_{i:02d}.png"
            path=self.frames/name
            Image.new("RGB",(640,360),(i*20,60,70)).save(path)
            digest=hashlib.sha256(path.read_bytes()).hexdigest()
            self.rows.append({"filename":name})
            self.checks.append({"source_frame":name,"source_frame_sha256":digest,
                                "endpoint_visually_aligned":True,"selected_timecode_s":t})
        self.selection=self.root/"selection.json";self.alignment=self.root/"alignment.json"
        self.write()
    def write(self):
        self.selection.write_text(json.dumps({"status":"FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW",
                                              "preselected":self.rows,
                                              "candidate_segment_times_s":self.times}))
        self.alignment.write_text(json.dumps({"checks":self.checks}))
    def test_motion_ends_at_exact_selected_frame(self):
        p=load_plan(self.selection,self.alignment,self.frames)
        self.assertEqual([x["start_s"] for x in p],[5.2,15.2,25.2,35.2,45.2])
        self.assertEqual([x["freeze_timecode_s"] for x in p],self.times)
    def test_mismatched_frame_digest_fails_closed(self):
        self.checks[1]["source_frame_sha256"]="0"*64;self.write()
        with self.assertRaisesRegex(ValueError,"ALIGNMENT"):
            load_plan(self.selection,self.alignment,self.frames)
    def test_unaligned_frame_fails_closed(self):
        self.checks[0]["endpoint_visually_aligned"]=False;self.write()
        with self.assertRaisesRegex(ValueError,"ALIGNMENT"):
            load_plan(self.selection,self.alignment,self.frames)
    def test_overlapping_motion_fails_closed(self):
        self.times[1]=12.;self.checks[1]["selected_timecode_s"]=12.;self.write()
        with self.assertRaisesRegex(ValueError,"OVERLAPPING"):
            load_plan(self.selection,self.alignment,self.frames)
    def test_too_early_for_full_motion_fails_closed(self):
        self.times[0]=3.;self.checks[0]["selected_timecode_s"]=3.;self.write()
        with self.assertRaisesRegex(ValueError,"INSUFFICIENT"):
            load_plan(self.selection,self.alignment,self.frames)

if __name__=="__main__":unittest.main()
