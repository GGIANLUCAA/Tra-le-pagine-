import json,sys,tempfile,unittest,hashlib,wave
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import storia_rivive_v281_delhi_real_movement_stage as subject

class V281(unittest.TestCase):
    def test_no_false_vidu_and_identity_count(self):
        self.assertEqual(len(subject.FRAMES),5)
        self.assertEqual(len(set(subject.FRAME_HASHES)),5)
        self.assertTrue(all(len(x)==64 for x in subject.FRAME_HASHES))
        self.assertTrue(14 <= 4*sum(subject.RUNTIME[:3])+subject.RUNTIME[3] <=35)
    def test_audio_is_real_decodable_original_wave(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"original.wav"
            subject.audio(p,0.5)
            with wave.open(str(p)) as w:
                self.assertEqual(w.getframerate(),16000)
                self.assertEqual(w.getnchannels(),1)
                self.assertEqual(w.getsampwidth(),2)
                self.assertGreater(w.getnframes(),5000)
    def test_cover_has_correct_size(self):
        with tempfile.TemporaryDirectory() as t:
            source=Path(t)/"photo.jpg"; dest=Path(t)/"cover.jpg"
            Image.new("RGB",(720,1280),"gray").save(source)
            subject.make_cover(source,dest)
            with Image.open(dest) as im:
                self.assertEqual(im.size,(720,1280))
                self.assertEqual(im.format,"JPEG")
    def test_ffmpeg_concat_list_uses_linebreak_separator(self):
        # A double-escaped backslash-n produced mp4nfile and broke the real
        # V281 runner after all source segments were rendered.
        import inspect
        source=inspect.getsource(subject.main)
        target='+'"'+"'"+'\\'+'n'+'" for f in parts'
        self.assertIn(target, source)
        self.assertNotIn('+'"'+"'"+'\\'+'\\'+'n'+'" for f in parts', source)

    def test_untrusted_hash_fails_closed_before_any_render(self):
        with tempfile.TemporaryDirectory() as t:
            r=Path(t)
            film=r/"fake.webm";film.write_bytes(b"WRONG FILM")
            with self.assertRaisesRegex(ValueError,"ORIGINAL_1910_FILM_SHA_MISMATCH"):
                subject.verify_inputs(film,r,r,r/"nonexistent.json")

if __name__=="__main__":
    unittest.main()
