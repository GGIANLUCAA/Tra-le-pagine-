import importlib.util
import tempfile
import unittest
from pathlib import Path

import numpy as np

FILE = Path(__file__).resolve().parents[1] / 'src' / 'storia_rivive_v165_reference_audit.py'
spec = importlib.util.spec_from_file_location('v165', FILE)
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class TestReferenceVisualAudit(unittest.TestCase):
    def test_reference_sha_registry(self):
        self.assertEqual(set(v.REFERENCE_SHA256), {'43055', '43056'})
        self.assertTrue(all(len(s) == 64 for s in v.REFERENCE_SHA256.values()))

    def test_must_use_original_reference_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'fake43055.mp4'
            path.write_bytes(b'wrong video')
            with self.assertRaisesRegex(ValueError, 'HASH_MISMATCH'):
                v.verify_private_reference('43055', path)
            with self.assertRaisesRegex(ValueError, 'UNKNOWN_REFERENCE'):
                v.verify_private_reference('garbage', path)
            with self.assertRaises(FileNotFoundError):
                v.verify_private_reference('43056', Path(td) / 'not-found.mp4')

    def test_letterboxed_content_detects_small_active_area(self):
        rng = np.random.default_rng(129)
        core = rng.integers(45, 200, size=(100, 80, 3), dtype=np.uint8)
        full = np.tile(core, (4, 1, 1))
        letterboxed = np.full_like(full, 9)
        letterboxed[140:260] = np.tile(core, (2, 1, 1))[:120]
        self.assertGreater(v.content_row_fraction(full), .9)
        self.assertLess(v.content_row_fraction(letterboxed), .35)

    def test_metrics_require_actual_frame(self):
        with self.assertRaisesRegex(ValueError, 'FRAME_TOO_SMALL'):
            v.content_row_fraction(np.zeros((10, 10, 3), dtype=np.uint8))
        with self.assertRaisesRegex(ValueError, 'COLOR_FRAME_REQUIRED'):
            v.content_row_fraction(np.zeros((100, 100), dtype=np.uint8))

    def test_missing_candidate_cannot_be_approved(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(FileNotFoundError):
                v.compare(Path(td) / 'a.mp4', Path(td) / 'b.mp4', Path(td) / 'c.mp4', Path(td) / 'out')


if __name__ == '__main__':
    unittest.main()
