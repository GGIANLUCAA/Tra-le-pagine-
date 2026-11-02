import subprocess,sys,tempfile,unittest
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from storia_rivive_v235_kodachrome_reference import inspect,color_score

class TestV235RealSource(unittest.TestCase):
    def test_color_vs_grayscale(self):
        self.assertEqual(color_score(Image.new("RGB",(120,90),(90,90,90))),0)
        self.assertGreater(color_score(Image.new("RGB",(120,90),(210,90,30))),5)

    def test_rejects_fake_sha(self):
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp)/"fake.webm";f.write_bytes(b"0"*2048)
            with self.assertRaisesRegex(ValueError,"SOURCE_SHA1_MISMATCH"):
                inspect(f,Path(tmp)/"out")

    def test_real_ffmpeg_source_never_approved_or_published(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/"real.mp4"
            subprocess.run(["ffmpeg","-nostdin","-v","error","-y","-f","lavfi",
                "-i","testsrc2=size=960x720:rate=15:duration=42",
                "-c:v","mpeg4","-q:v","8",str(source)],check=True,timeout=60)
            r=inspect(source,root/"out",samples=8,strict=False)
            self.assertEqual(len(r["frames"]),8)
            self.assertTrue((root/"out"/"V235_REAL_1926_COLOR_CONTACT.jpg").is_file())
            self.assertEqual(r["four_real_i2i_photos"],0)
            self.assertEqual(r["real_vidu_clips"],0)
            self.assertEqual(r["final_episodes"],0)
            self.assertFalse(r["italian_rights_verified"])
            self.assertFalse(r["publish_allowed"])
            self.assertTrue(r["not_a_4_plus_1_episode"])

if __name__=="__main__":unittest.main()
