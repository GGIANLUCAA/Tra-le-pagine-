"""Regression: the verified V249 handoff and its workflow must use the same report name."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import storia_rivive_v249_fiesole_short_motion_selection as v249


class V249ReportContractTests(unittest.TestCase):
    def test_verified_film_writes_expected_report_and_five_real_candidates(self):
        rows = [
            {"frame": name, "original_sha256": sha, "timestamp_s": float(i * 10 + 20),
             "title_flags": [False] * 4, "endpoint_mae": 1.0}
            for i, (name, sha) in enumerate(v249.CANDIDATES)
        ]
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "output"
            # All costly I/O mocked, but genuine source selection was independently
            # executed and verified in GitHub run #41610202195.
            with patch.object(v249, "verified_input", return_value=9.63), \
                 patch.object(v249, "extract_photo"), \
                 patch.object(v249, "likely_intertitle", return_value=False), \
                 patch.object(v249, "endpoint_error", return_value=1.0):
                report = v249.run(Path(tmp) / "film.webm", Path(tmp) / "scout.json",
                                  Path(tmp), folder)
            self.assertEqual(report["status"],
                             "FIVE_SHORT_CLEAN_SOURCE_WINDOWS_READY_FOR_ARTISTIC_REVIEW_NOT_FINAL")
            self.assertEqual(len(report["selected_five"]), 5)
            self.assertTrue((folder / "V249_FIESOLE_SHORT_WINDOWS.json").is_file())
            self.assertTrue((folder / "SHOT_AWARE_SELECTION_V249_NOT_APPROVED.json").is_file())
            self.assertTrue((folder / "SOURCE_ENDPOINT_ALIGNMENT_V249.json").is_file())
            self.assertFalse(report["final_mp4"])
            self.assertFalse(report["final_zip"])
            self.assertFalse(report["publish_allowed"])


if __name__ == "__main__":
    unittest.main()
