"""V41 image selection tests: no traversal, output review, no source overwrite."""
import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"src"))
from i2v_scene_v41 import select


class SceneV41Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.before=Path.cwd()
        self.addCleanup(lambda:os.chdir(self.before))
        os.chdir(self.temp.name)
        self.root=Path("episodes/test_book")
        self.root.mkdir(parents=True)
        self.out=Path("output")
        with zipfile.ZipFile(self.root/"scene_premium.zip","w") as f:
            f.writestr("nested/scena_01.png",b"image"*300)
            f.writestr("../../attack.txt",b"unsafe")
    def test_zip_scene_only(self):
        path=select("test_book",1,self.out)
        self.assertEqual(path.name,"scena_01.png")
        self.assertTrue(path.exists())
        self.assertFalse(Path("attack.txt").exists())
    def test_image_preferred_over_zip(self):
        path=self.root/"images/scena_01.jpg"
        path.parent.mkdir()
        path.write_bytes(b"j"*2500)
        self.assertEqual(select("test_book",1,self.out),path)
    def test_reject_traversal_and_bad_cues(self):
        for slug in ("../oops","/home","a/b"):
            with self.assertRaises(ValueError):
                select(slug,1,self.out)
        with self.assertRaises(ValueError):
            select("test_book",36,self.out)
        with self.assertRaises(ValueError):
            select("test_book",2,self.out)
    def test_preserve_output(self):
        select("test_book",1,self.out)
        with self.assertRaises(ValueError):
            select("test_book",1,self.out)


if __name__=="__main__":unittest.main()
