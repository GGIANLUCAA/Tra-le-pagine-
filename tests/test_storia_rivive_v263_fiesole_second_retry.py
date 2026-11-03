"""V263 fail-closed original source tests; no diffusion or credits."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import storia_rivive_v263_fiesole_second_retry as v

class SourceTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.root=Path(self.t.name)
        self.image=self.root/"original_shot_02_frame_04.png"
        Image.new("RGB",(1920,1080),"grey").save(self.image)
        self.digest=hashlib.sha256(self.image.read_bytes()).hexdigest()
        self.rows=[dict(shot=i,original_sha256=(self.digest if i==2 else f"{i:064x}"),
            role="I2I_PHOTO_SOURCE" if i<5 else "VIDU_SOURCE",
            archive_filename=self.image.name if i==2 else f"frame_{i}.png",
            original_frame="frame_04.png",source_frame_locked=True,
            source_time_s=float(i)) for i in range(1,6)]
        self.manifest=self.root/"manifest.json"
        self.write()
    def write(self):
        self.manifest.write_text(json.dumps(dict(version="V251_FIESOLE_SOURCE_LOCKED_PHOTO_HANDOFF",
            episode=v.EPISODE,source_film_sha256=v.FILM_SHA,shots=self.rows)))
    def test_authentic_second_shot(self):
        source,row=v.verify(self.manifest,self.root)
        self.assertEqual(source,self.image)
        self.assertEqual(row["shot"],2)
    def test_reject_duplicate_shot(self):
        self.rows[2]["original_sha256"]=self.digest
        self.write()
        with self.assertRaisesRegex(ValueError,"UNIQUE"):v.verify(self.manifest,self.root)
    def test_reject_wrong_film(self):
        m=json.loads(self.manifest.read_text());m["source_film_sha256"]="0"*64
        self.manifest.write_text(json.dumps(m))
        with self.assertRaisesRegex(ValueError,"WRONG_ORIGINAL"):v.verify(self.manifest,self.root)
    def test_reject_tampered_source(self):
        self.image.write_bytes(b"not png")
        with self.assertRaisesRegex(ValueError,"SOURCE_BYTES_CHANGED"):v.verify(self.manifest,self.root)
    def test_reject_unsafe_path(self):
        self.rows[1]["archive_filename"]="../outside.png"
        self.write()
        with self.assertRaisesRegex(ValueError,"SHOT_TWO_INVALID"):v.verify(self.manifest,self.root)
    def test_no_paid_generation_or_false_approval(self):
        s=Path(v.__file__).read_text()
        self.assertIn("artistic_approval=False",s)
        self.assertIn("paid_credits_spent=0",s)
        self.assertNotIn("safety_checker=None",s)

if __name__=="__main__":unittest.main()
