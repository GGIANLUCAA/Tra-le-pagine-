"""V209 boundary review tests on actual FFmpeg-generated and decoded media."""
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import storia_rivive_v209_shot_boundary_review as v209


def synthetic(cache: Path, multi=True) -> Path:
    film = cache / "ORIGINAL_ARCHIVE.webm"
    if multi:
        colors = ["black", "white", "blue", "white", "black"]
        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error"]
        for color in colors:
            cmd += ["-f", "lavfi", "-i", f"color={color}:size=640x480:rate=12:duration=2"]
        cmd += ["-filter_complex", "[0:v][1:v][2:v][3:v][4:v]concat=n=5:v=1:a=0,format=yuv420p[v]",
                "-map", "[v]"]
    else:
        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "lavfi",
               "-i", "color=white:size=640x480:rate=12:duration=10",
               "-vf", "format=yuv420p"]
    cmd += ["-c:v", "libvpx-vp9", "-b:v", "800k", "-y", str(film)]
    subprocess.run(cmd, capture_output=True, timeout=60, check=True)
    return film


def inputs(film: Path):
    hash_ = hashlib.sha256(film.read_bytes()).hexdigest()
    manifest = {"source_video_sha256": hash_,
                "original_frame_jobs": [{"source_file": f"frame_{i:02d}.png"} for i in range(2, 7)]}
    provenance = {"status": v209.READY_PROVENANCE, "source_film_sha256": hash_}
    motion = {"status": v209.READY_MOTION,
              "motion_evidence": [{"source_frame": f"frame_{i:02d}.png",
                                   "freeze_time_advisory_s": round(1.7+2*j, 3)}
                                  for j, i in enumerate(range(2, 7))]}
    scout = {"original_sha256": hash_, "duration_s": 10.0}
    return manifest, provenance, motion, scout


class ShotBoundaryReviewTests(unittest.TestCase):
    def test_five_real_video_segments_yield_review_pending_not_approval(self):
        with tempfile.TemporaryDirectory() as root:
            cache = Path(root)
            film = synthetic(cache)
            result = v209.inspect(*inputs(film), cache)
            self.assertEqual(result["status"], v209.REVIEW_PENDING, result)
            self.assertEqual(result["candidate_cut_times_s"], [2.0, 4.0, 6.0, 8.0])
            self.assertFalse(result["five_distinct_shots_approved"])
            self.assertFalse(result["provider_calls_permitted"])
            self.assertFalse(result["publish_permitted"])

    def test_single_continuous_shot_does_not_count_as_five_shots(self):
        with tempfile.TemporaryDirectory() as root:
            cache = Path(root)
            film = synthetic(cache, multi=False)
            result = v209.inspect(*inputs(film), cache)
            self.assertEqual(result["reason"], "FIVE_SEPARATE_CUT_SEGMENTS_NOT_DETECTED", result)

    def test_tampered_film_is_blocked_before_detection(self):
        with tempfile.TemporaryDirectory() as root:
            cache = Path(root)
            film = synthetic(cache)
            data = inputs(film)
            with film.open("ab") as f:
                f.write(b"corrupt")
            self.assertEqual(v209.inspect(*data, cache)["reason"], "SOURCE_FILM_BYTES_CHANGED")

    def test_film_cut_inside_lead_in_is_blocked(self):
        with tempfile.TemporaryDirectory() as root:
            cache = Path(root)
            film = synthetic(cache)
            manifest, provenance, motion, scout = inputs(film)
            motion["motion_evidence"][1]["freeze_time_advisory_s"] = 2.5
            result = v209.inspect(manifest, provenance, motion, scout, cache)
            self.assertEqual(result["reason"], "MOVING_LEADIN_CROSSES_CANDIDATE_SHOT_CUT", result)

    def test_wrong_hash_and_invalid_earlier_gate_blocked(self):
        with tempfile.TemporaryDirectory() as root:
            cache = Path(root)
            film = synthetic(cache)
            manifest, provenance, motion, scout = inputs(film)
            manifest["source_video_sha256"] = "0"*64
            self.assertEqual(v209.inspect(manifest, provenance, motion, scout, cache)["reason"],
                             "SOURCE_HASH_BINDING_MISMATCH")
            manifest["source_video_sha256"] = provenance["source_film_sha256"]
            motion["status"] = "BW_MOTION_BLOCKED"
            self.assertEqual(v209.inspect(manifest, provenance, motion, scout, cache)["reason"],
                             "PREVIOUS_FILM_GATES_NOT_VERIFIED")


if __name__ == "__main__":
    unittest.main()
