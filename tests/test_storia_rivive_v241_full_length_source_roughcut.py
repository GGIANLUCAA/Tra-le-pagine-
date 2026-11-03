import tempfile,subprocess,unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from storia_rivive_v241_full_length_source_roughcut import build

class RoughcutTests(unittest.TestCase):
    def test_reject_duplicate_timecodes(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/"test.mp4";source.write_bytes(b"x")
            with self.assertRaisesRegex(ValueError,"DUPLICATE"):
                build(source,[0,0,1,2,3],Path(tmp)/"out.mp4")
    def test_real_decodable_24s_roughcut(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/"test.mp4"
            subprocess.run(["ffmpeg","-nostdin","-loglevel","error","-y",
                "-f","lavfi","-i","testsrc2=size=640x360:rate=24:duration=27",
                "-c:v","libx264","-preset","ultrafast",str(source)],check=True)
            output=Path(tmp)/"rough.mp4"
            report=build(source,[0,5,10,15,20],output)
            self.assertTrue(output.is_file())
            self.assertGreater(report["duration_s"],23)
            self.assertLess(report["duration_s"],25)
            self.assertFalse(report["has_vidu"])
            self.assertFalse(report["publication_permitted"])
if __name__=="__main__":unittest.main()
