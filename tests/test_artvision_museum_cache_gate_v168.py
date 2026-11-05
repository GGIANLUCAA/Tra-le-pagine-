"""V168 fail-closed cache gate for future Museum renderer adoption.

No video generation, paid APIs, publication or master modifications.
Run with: python -m unittest tests.test_artvision_museum_cache_gate_v168 -v
"""
import importlib.util
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "artvision_lady_shalott_critico_museum_v164.py"

class MuseumCacheGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Fail CLOSED: a missing dependency must never count as regression PASS.
        import cv2
        import numpy as np
        from PIL import Image
        cls.cv2, cls.np = cv2, np
        spec = importlib.util.spec_from_file_location("museum_v164_gate", SRC)
        cls.renderer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.renderer)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.renderer._museum_static_assets.cache_clear()

    def photo(self, name, seed):
        p = pathlib.Path(self.tmp.name) / name
        rng = self.np.random.default_rng(seed)
        a = rng.integers(0, 256, (360, 480, 3), dtype=self.np.uint8)
        self.assertTrue(self.cv2.imwrite(str(p), a))
        return p

    def test_cached_background_is_never_mutated_by_render(self):
        p = self.photo("a.jpg", 1)
        before = self.renderer._museum_static_assets(str(p))[3].copy()
        for t in [0, .05, .13, .20, .40, .65, .80, 1]:
            self.renderer.staged(p, t)
        after = self.renderer._museum_static_assets(str(p))[3]
        self.assertTrue(self.np.array_equal(before, after))

    def test_cache_is_bounded_and_different_photos_remain_distinct(self):
        a, b, c = [self.photo(f"{i}.jpg", i) for i in range(3)]
        fa = self.renderer.staged(a, .4)
        fb = self.renderer.staged(b, .4)
        fc = self.renderer.staged(c, .4)
        self.assertFalse(self.np.array_equal(fa, fb))
        self.assertFalse(self.np.array_equal(fb, fc))
        info = self.renderer._museum_static_assets.cache_info()
        self.assertLessEqual(info.currsize, 2)
        self.assertEqual(info.misses, 3)
        # First photo must have been evicted: same pixels on fresh decode.
        self.assertTrue(self.np.array_equal(fa, self.renderer.staged(a, .4)))
        self.assertEqual(self.renderer._museum_static_assets.cache_info().misses, 4)

if __name__ == "__main__":
    unittest.main()
