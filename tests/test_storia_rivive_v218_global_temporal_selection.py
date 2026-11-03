"""V218: regression for false rejection from greedy temporal scouting."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import storia_rivive_frame_rank_v101 as ranker


class GlobalFiveFrameSelectionTests(unittest.TestCase):
    def test_global_selection_finds_five_where_greedy_found_only_four(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            for i in range(1, 13):
                (folder / ("frame_%02d.png" % i)).write_bytes(b"synthetic test placeholder")
            def fake_measure(path):
                index = int(path.stem[-2:])
                # A greedy descending selection starts at 3,6,9,12;
                # their exclusion neighborhoods leave only four slots.
                priority = 0.99 if index in (3, 6, 9, 12) else 0.1
                return {"filename": path.name, "source_visual_quality_score": priority}
            with patch.object(ranker, "measure", side_effect=fake_measure):
                result = ranker.rank(folder)
            self.assertEqual(result["status"],
                             "FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW")
            selected = [int(row["filename"][6:8]) for row in result["preselected"]]
            self.assertEqual(len(selected), 5, selected)
            self.assertTrue(all(b-a >= 2 for a,b in zip(selected, selected[1:])))
            self.assertNotIn(1, selected)
            self.assertTrue(all(row["filename"].startswith("frame_") for row in result["preselected"]))

    def test_four_scout_samples_never_forged_into_five(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            for i in range(1,5):
                (folder / ("frame_%02d.png" % i)).touch()
            with patch.object(ranker,"measure",
                              side_effect=lambda path: {"filename":path.name,
                                   "source_visual_quality_score":0.5}):
                result=ranker.rank(folder)
            self.assertEqual(result["status"],"SOURCE_TOO_FEW_DISTINCT_CANDIDATE_FRAMES")
            self.assertEqual(result["preselected"],[])


if __name__ == "__main__":
    unittest.main()
