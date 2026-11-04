import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from storia_rivive_v291_final_motion_window_qa import check


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg required")
class RealShortEditWindowTests(unittest.TestCase):
    def produce(self, root, black=False):
        video = root / "source.mp4"
        source = "color=c=black:s=720x1280:r=24" if black else "testsrc2=s=720x1280:r=24"
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "lavfi", "-i", source,
                        "-frames:v", "575", "-c:v", "libx264", "-preset", "ultrafast",
                        "-crf", "32", str(video)], check=True, timeout=120)
        manifest = root / "source.json"
        manifest.write_text(json.dumps({"version": "V243_ARCHIVAL_FREEZE_ENDPOINT_REVIEW",
            "shots": [{"source_frame": f"frame_{i:02}.png", "sha256": "a" * 64}
                      for i in range(1, 6)]}))
        return video, manifest

    def test_all_five_actual_motion_windows_keep_source_endpoints(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            video, manifest = self.produce(root)
            report = check(video, manifest, root / "report.json", root / "edit.mp4")
            self.assertEqual(report["status"],
                             "FIVE_REAL_1P5S_EDIT_WINDOWS_PASS_NOT_ARTISTIC_APPROVAL")
            self.assertEqual(report["frames_in_final_short_preview"], 180)
            self.assertEqual([x["original_decoded_frame_range"] for x in report["shots"]],
                             [[79, 114], [194, 229], [309, 344], [424, 459], [539, 574]])
            self.assertEqual([x["trimmed_leading_frames"] for x in report["shots"]], [0] * 5)
            self.assertTrue((root / "edit.mp4").stat().st_size > 3000)
            self.assertFalse(report["finished_mp4"])
            self.assertFalse(report["publish_permitted"])

    def test_black_static_source_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            video, manifest = self.produce(root, black=True)
            report = check(video, manifest, root / "report.json", root / "edit.mp4")
            self.assertEqual(report["status"], "REJECT_SHORT_EDIT_WINDOW_ARTISTIC_REVIEW_REQUIRED")
            self.assertFalse((root / "edit.mp4").exists())
            self.assertEqual(report["new_final_videos_delivered"], 0)

    def test_missing_shots_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            video, manifest = self.produce(root)
            manifest.write_text(json.dumps({"version": "V243_ARCHIVAL_FREEZE_ENDPOINT_REVIEW",
                                            "shots": []}))
            with self.assertRaisesRegex(ValueError, "INVALID_SOURCE_REVIEW_MANIFEST"):
                check(video, manifest, root / "report.json", root / "edit.mp4")


if __name__ == "__main__":
    unittest.main()
