"""V122: V101 must actually reuse a successful SHA-bound archival scout cache.

Offline structural regression: a restore/save key mismatch silently forces
new 60–160 MiB downloads on every three-hour cycle. No API or media access.
"""
import re
import unittest
from pathlib import Path

WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/storia-rivive-v101-auto-3h.yml"


class V122ArchivalCacheContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_restore_and_save_use_identical_versioned_cache_key(self):
        keys = re.findall(
            r"^\s+key:\s*(storia-v101-archival-scout-[^\n]+)$",
            self.workflow,
            flags=re.MULTILINE,
        )
        self.assertEqual(len(keys), 2, "Expected exactly one restore and one save key")
        self.assertEqual(keys[0], keys[1], "Cache miss every cycle: restore/save key mismatch")
        self.assertIn("v7-native-raster-preflight", keys[0])

    def test_restore_and_save_share_same_candidate_directory(self):
        paths = re.findall(
            r"^\s+path:\s*(output/storia_v101/source-cache/[^\n]+)$",
            self.workflow,
            flags=re.MULTILINE,
        )
        self.assertEqual(len(paths), 2)
        self.assertEqual(paths[0], paths[1])
        self.assertIn("STORIA_EPISODE_ID", paths[0])

    def test_cache_saves_only_verified_original_media(self):
        self.assertIn("steps.scout_status.outputs.ready == 'true'", self.workflow)
        self.assertIn("steps.film_cache.outputs.cache-hit != 'true'", self.workflow)
        self.assertIn("V118 reject nonmoving source windows", self.workflow)


if __name__ == "__main__":
    unittest.main()
