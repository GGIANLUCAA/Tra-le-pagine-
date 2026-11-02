"""V217: test 4-source launch without network, credits, or false final videos."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import storia_rivive_v217_four_pilot_source_review as v217

MANIFEST = Path(__file__).resolve().parents[1] / "queue" / "storia_rivive_four_pilots_v217.json"


class FourPilotSourceReviewTest(unittest.TestCase):
    def setUp(self):
        self.source = v217.read_manifest(MANIFEST)

    def test_four_original_unique_source_projects_and_no_authorizations(self):
        self.assertEqual(len(self.source["episodes"]), 4)
        self.assertFalse(self.source["credit_spend_allowed"])
        self.assertFalse(self.source["publish_allowed"])
        for item in self.source["episodes"]:
            self.assertIn("ITALIAN_RIGHTS_NOT_REVIEWED", item["rights_status"])

    def test_duplicate_sources_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = copy.deepcopy(self.source)
            manifest["episodes"][1]["source_page"] = manifest["episodes"][0]["source_page"]
            path = Path(tmp) / "manifest.json"
            path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "DUPLICATED"):
                v217.read_manifest(path)

    def test_false_permissions_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = copy.deepcopy(self.source)
            manifest["credit_spend_allowed"] = True
            path = Path(tmp) / "manifest.json"
            path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "UNSAFE_PERMISSIONS"):
                v217.read_manifest(path)

    def test_forged_italian_rights_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = copy.deepcopy(self.source)
            manifest["episodes"][0]["rights_status"] = "ITALIAN_RIGHTS_APPROVED"
            path = Path(tmp) / "manifest.json"
            path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "CANNOT_BE_PREAPPROVED"):
                v217.read_manifest(path)

    def test_prepare_and_failed_scout_never_called_final(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            episode_id = self.source["episodes"][0]["id"]
            order = v217.prepare(self.source, episode_id, folder / "result")
            self.assertIs(order["paid_api_call_permitted"], False)
            self.assertIs(order["publish_permitted"], False)
            report = v217.finish(self.source, episode_id, folder / "source",
                                 folder / "result")
            self.assertEqual(report["status"], "SOURCE_REJECTED")
            self.assertIs(report["finished_mp4"], False)
            self.assertIs(report["finished_zip"], False)
            self.assertIs(report["publish_permitted"], False)

    def test_real_motion_preview_is_file_only_and_never_final(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            film = root / "ORIGINAL_ARCHIVE.webm"
            subprocess.run([
                "ffmpeg", "-nostdin", "-v", "error", "-y",
                "-f", "lavfi", "-i", "testsrc2=size=640x360:rate=24:duration=13",
                "-an", "-c:v", "libvpx-vp9", "-b:v", "600k", str(film)],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=60)
            times = [1.5, 3.8, 6.0, 8.4, 11.0]
            references = []
            for i, t in enumerate(times, 1):
                frame = root / ("frame_%02d.png" % i)
                subprocess.run([
                    "ffmpeg", "-nostdin", "-v", "error", "-y",
                    "-ss", str(t), "-i", str(film), "-frames:v", "1", str(frame)],
                    check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=30)
                references.append(frame)
            review = v217.render_source_only_preview(
                film, times, root / "review", references)
            self.assertTrue((root / "review" / "SOURCE_ENDPOINT_ALIGNMENT_V223.json").is_file())
            evidence = json.loads((root / "review" /
                                   "SOURCE_ENDPOINT_ALIGNMENT_V223.json").read_text())
            self.assertEqual(len(evidence["checks"]), 5)
            self.assertTrue(all(x["endpoint_visually_aligned"] for x in evidence["checks"]))
            self.assertEqual(review["source_shots"], 5)
            self.assertTrue((root / "review" / review["review_preview"]).is_file())
            self.assertEqual(review["width"], 720)
            self.assertEqual(review["height"], 1280)
            self.assertFalse(review["has_i2i_photos"])
            self.assertFalse(review["has_vidu_clip"])
            self.assertFalse(review["final_video"])


    def test_v223_wrong_original_frame_blocks_source_preview(self):
        # A card or different shot must never be accepted as a matching
        # endpoint simply because the selected timecode is numerically valid.
        from PIL import Image
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            film = root / "ORIGINAL_ARCHIVE.webm"
            subprocess.run([
                "ffmpeg", "-nostdin", "-v", "error", "-y",
                "-f", "lavfi", "-i", "testsrc2=size=640x360:rate=24:duration=13",
                "-an", "-c:v", "libvpx-vp9", "-b:v", "600k", str(film)],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=60)
            references = []
            for i in range(1, 6):
                frame = root / ("frame_%02d.png" % i)
                Image.new("RGB", (640, 360), (255, 255, 255)).save(frame)
                references.append(frame)
            with self.assertRaisesRegex(ValueError, "SOURCE_PREVIEW_FRAME_MISMATCH"):
                v217.render_source_only_preview(
                    film, [1.5, 3.8, 6.0, 8.4, 11.0], root / "review", references)
            evidence = json.loads((root / "review" /
                                   "SOURCE_ENDPOINT_ALIGNMENT_V223.json").read_text())
            self.assertEqual(len(evidence["checks"]), 5)
            self.assertTrue(any(not x["endpoint_visually_aligned"]
                                for x in evidence["checks"]))

    def test_v223_rejects_non_source_reference_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            frame = root / "untrusted.png"
            frame.write_bytes(b"not an archive frame")
            with self.assertRaisesRegex(ValueError, "INVALID_SOURCE_REFERENCE_FRAME"):
                v217.endpoint_alignment(root / "clip.mp4", frame)


if __name__ == "__main__":
    unittest.main()
