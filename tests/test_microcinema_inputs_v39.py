"""Verify V39 Android ZIP/image selection without external services."""
import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from microcinema_inputs_v39 import prepare_asset


class InputV39Tests(unittest.TestCase):
    def setUp(self):
        self.old_cwd = Path.cwd()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        os.chdir(self.tmp.name)
        self.addCleanup(lambda: os.chdir(self.old_cwd))
        self.folder = Path("episodes/test_book")
        self.folder.mkdir(parents=True)
        self.zip = self.folder/"scene_premium.zip"
        with zipfile.ZipFile(self.zip,"w") as z:
            z.writestr("nested/scena_01.png", b"fake image for extraction test")
            z.writestr("../../bad-file.txt", b"malicious path")
        self.output = Path("output")

    def test_safe_extract_exact_scene(self):
        result = prepare_asset(str(self.zip), 1, self.output)
        self.assertEqual(result.name, "scena_01.png")
        self.assertEqual(result.read_bytes(), b"fake image for extraction test")
        self.assertFalse(Path("bad-file.txt").exists())

    def test_reject_traversal_and_other_archives(self):
        with self.assertRaises(ValueError):
            prepare_asset("../secret.png", 1, self.output)
        with self.assertRaises(ValueError):
            prepare_asset(str(self.folder/"scene_other.zip"), 1, self.output)

    def test_missing_or_wrong_scene(self):
        with self.assertRaises(ValueError):
            prepare_asset(str(self.zip), 8, self.output)
        with self.assertRaises(ValueError):
            prepare_asset(str(self.zip), 36, self.output)

    def test_no_overwrite_extracted_file(self):
        prepare_asset(str(self.zip), 1, self.output)
        with self.assertRaises(ValueError):
            prepare_asset(str(self.zip), 1, self.output)


if __name__ == "__main__":
    unittest.main()
