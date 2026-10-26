import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from creative_reveals_experimental import create_demo_image, recommend, render


class CreativeRevealsTest(unittest.TestCase):
    def test_director_is_conservative(self):
        self.assertEqual(recommend("libri", "fiaba")[0], "watercolor")
        self.assertEqual(recommend("libri", "mistero")[0], "ink")
        self.assertEqual(recommend("libri", "illustrato")[0], "line_art")
        self.assertEqual(recommend("libri", "neutro")[0], "none")
        self.assertEqual(recommend("artvision_cinema", "fiaba")[0], "none")

    def test_preview_preserves_source_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "original.png"
            create_demo_image(source, 180, 320)
            before = hashlib.sha256(source.read_bytes()).hexdigest()
            target = root / "test.mp4"
            info = render(source, target, fmt="libri", mood="fiaba",
                          duration=1., fps=12, width=180, height=320)
            self.assertEqual(before, hashlib.sha256(source.read_bytes()).hexdigest())
            self.assertEqual(info["director_suggestion"], "watercolor")
            self.assertTrue(target.stat().st_size > 1000)
            self.assertTrue(target.with_suffix(".json").is_file())
            with self.assertRaises(FileExistsError):
                render(source, target, duration=1., fps=12, width=180, height=320)

    def test_line_art_same_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "original.png"
            create_demo_image(source, 120, 220)
            info = render(source, root/"test.mp4", effect="line_art",
                          duration=.5, fps=12, width=120, height=220)
            self.assertEqual(info["frames"], 6)
            self.assertTrue(info["source_untouched"])

if __name__ == "__main__":
    unittest.main()
