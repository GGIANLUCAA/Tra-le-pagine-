import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np

SCRIPT = Path(__file__).resolve().parent.parent / "src" / "microcinema_v39.py"
spec = importlib.util.spec_from_file_location("microcinema_v39", SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class MicrocinemaV39Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        yy, xx = np.mgrid[:256, :160]
        img = np.stack([xx * 255 // 160, yy * 255 // 256,
                        255 - xx * 255 // 160], axis=-1).astype(np.uint8)
        self.image = self.root / "scene.png"
        cv2.imwrite(str(self.image), img)

    def test_policy_artvision(self):
        with self.assertRaises(ValueError):
            m.render(self.image, self.root / "out.mp4", "depth_layers",
                     "artvision_cinema", 5, 320, 568, 12)
        with self.assertRaises(ValueError):
            m.render(self.image, self.root / "out.mp4", "light_travel",
                     "artvision_critico", 5, 320, 568, 12)

    def test_no_overwrite_or_too_short(self):
        out = self.root / "old.mp4"
        out.write_bytes(b"unchanged")
        with self.assertRaises(ValueError):
            m.render(self.image, out, "slow_push", "libri", 5, 320, 568, 12)
        self.assertEqual(out.read_bytes(), b"unchanged")
        with self.assertRaises(ValueError):
            m.render(self.image, self.root / "new.mp4", "slow_push",
                     "libri", 2, 320, 568, 12)

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"),
                         "FFmpeg required")
    def test_real_h264_and_manifest(self):
        out = self.root / "scene.mp4"
        result = m.render(self.image, out, "focus_reveal",
                          "libri", 5, 320, 568, 12)
        self.assertTrue(out.is_file() and out.stat().st_size > 1000)
        self.assertTrue(out.with_suffix(".json").is_file())
        self.assertEqual(result["status"], "rendered_needs_review")
        self.assertAlmostEqual(result["technical"]["duration_seconds"], 5, delta=0.15)

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"),
                         "FFmpeg required")
    def test_layered_foreground_same_scene(self):
        plate = cv2.imread(str(self.image))
        fg = np.zeros((*plate.shape[:2], 4), dtype=np.uint8)
        fg[50:155, 30:100, :3] = 255
        fg[50:155, 30:100, 3] = 255
        fg_path = self.root / "subject.png"
        cv2.imwrite(str(fg_path), fg)
        out = self.root / "layered.mp4"
        result = m.render(self.image, out, "depth_layers",
                          "libri", 5, 320, 568, 12, fg_path)
        self.assertEqual(result["effect"], "depth_layers")
        self.assertTrue(result["foreground_sha256"])


if __name__ == "__main__":
    unittest.main()
