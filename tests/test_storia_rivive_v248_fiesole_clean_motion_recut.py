import tempfile
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from storia_rivive_v248_fiesole_clean_motion_recut import choose, verified_input

def row(frame, t, flagged=False, mae=3.0):
    return {"frame": frame, "timestamp_s": t, "title_flags": [False, flagged, False, False],
            "endpoint_mae": mae, "original_sha256": "a" * 64}

class V248FiesoleTests(unittest.TestCase):
    def test_reselect_five_distinct_clean_windows(self):
        windows = [row("frame_03.png", 24.09), row("frame_04.png", 33.72),
                   row("frame_06.png", 53.0, True),
                   row("frame_07.png", 62.64), row("frame_10.png", 91.55),
                   row("frame_11.png", 101.18)]
        # Four clean windows are NOT enough. No imaginary fifth photo.
        with self.assertRaisesRegex(ValueError,"FEWER_THAN_FIVE"):
            choose(windows)
        windows[2]["title_flags"] = [False] * 4
        chosen = choose(windows)
        self.assertEqual(len(chosen), 5)
        self.assertEqual(chosen[0]["frame"], "frame_03.png")
        self.assertEqual(chosen[-1]["frame"], "frame_10.png")

    def test_reject_endpoint_mismatch_without_substitute(self):
        windows = [row(f"frame_{i:02d}.png", float(i*8)) for i in range(3,9)]
        windows[0]["endpoint_mae"] = 50.0
        selected = choose(windows)
        self.assertNotIn("frame_03.png", [r["frame"] for r in selected])
        windows[1]["title_flags"] = [True]
        with self.assertRaisesRegex(ValueError,"FEWER_THAN_FIVE"):
            choose(windows)

    def test_source_wrong_sha_fails_closed_before_frame_review(self):
        with tempfile.TemporaryDirectory() as directory:
            film=Path(directory)/"source.webm"
            film.write_bytes(b"not our archival source")
            with self.assertRaisesRegex(ValueError,"ORIGINAL_FILM_SHA_MISMATCH"):
                verified_input(film,Path(directory)/"scout.json",Path(directory))

if __name__=="__main__":
    unittest.main()
