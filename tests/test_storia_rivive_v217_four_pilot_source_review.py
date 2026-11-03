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

    def test_v225_french_title_rejected_and_new_source_only_research(self):
        import storia_rivive_v210_shot_aware_selection as v210
        ids = {item["id"] for item in self.source["episodes"]}
        self.assertNotIn("french_fashion_birds_1922_v220", ids)
        self.assertIn("early_cinema_sorrows_1910_v225", ids)
        new = next(x for x in self.source["episodes"]
                   if x["id"] == "early_cinema_sorrows_1910_v225")
        self.assertIn("fiction", new["visual_risks"][0].lower())
        self.assertIn("ITALIAN_RIGHTS_NOT_REVIEWED", new["rights_status"])
        self.assertFalse(self.source["italian_rights_approved"])
        config = json.loads((MANIFEST.parents[1] / "config" /
                             "storia_rivive_v221_source_frame_exclusions.json").read_text())
        french_original_sha = ("cd4143f53b5af364af169fa4483ca141fe50923"
                               "c36f5ed4bcf891890f01a91d4")
        excluded, reason = v210.source_review_exclusions(config, french_original_sha)
        self.assertEqual(excluded, {"frame_01.png"})
        self.assertIn("opening title", reason)
        other, _ = v210.source_review_exclusions(config, "0" * 64)
        self.assertEqual(other, set())

    def test_v228_source_locked_timecode_uses_same_index_as_real_photo_job(self):
        # Regression: Delhi V227 photo job index 1 was paired with index 2
        # timecode (104.345s instead of frame_04's 66.401s).
        selection = {"status": v217.SELECTION_READY,
                     "preselected": [{"filename": f"frame_{i:02d}.png"}
                                     for i in (1, 4, 6, 11, 12)],
                     "candidate_segment_times_s": [9.486, 66.401, 104.345,
                                                    199.204, 218.176]}
        alignment = {"checks": [
            {"source_frame": row["filename"],
             "source_frame_sha256": ("%064x" % (i + 1)),
             "selected_timecode_s": selection["candidate_segment_times_s"][i],
             "endpoint_visually_aligned": True}
            for i, row in enumerate(selection["preselected"])]}
        lock = v217.selected_i2i_source_lock(selection, alignment, "frame_04.png")
        self.assertEqual(lock["selected_index"], 1)
        self.assertEqual(lock["source_timecode_s"], 66.401)
        self.assertNotEqual(lock["source_timecode_s"], 104.345)
        self.assertEqual(lock["source_frame_sha256"], alignment["checks"][1]["source_frame_sha256"])
        broken = copy.deepcopy(alignment)
        broken["checks"][1]["selected_timecode_s"] = 104.345
        with self.assertRaisesRegex(ValueError, "TIMECODE_MISMATCH"):
            v217.selected_i2i_source_lock(selection, broken, "frame_04.png")
        with self.assertRaisesRegex(ValueError, "NOT_A_UNIQUE_I2I_FRAME"):
            v217.selected_i2i_source_lock(selection, alignment, "frame_12.png")

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


    def test_v224_four_real_source_frame_i2i_jobs_and_unique_episode_ids(self):
        # The handoff is a real, byte-hashed request manifest, NOT four
        # generated photographs or permission to spend Vidu credits.
        from PIL import Image
        import storia_rivive_i2i_prepare_v102 as v102
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            frames = root / "original_frames"
            frames.mkdir()
            (root / "ORIGINAL_ARCHIVE.webm").write_bytes(b"offline test archive")
            for i in range(1, 6):
                Image.new("RGB", (1280, 720),
                          (i * 29, i * 19, i * 11)).save(
                              frames / f"frame_{i:02d}.png")
            selection = {
                "status": "FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW",
                "preselected": [{"filename": f"frame_{i:02d}.png"}
                                for i in range(1, 6)],
            }
            orders = [v217.prepare(self.source, item["id"], root / item["id"])
                      for item in self.source["episodes"]]
            self.assertEqual(len({o["cycle_id"] for o in orders}), 4)
            first = v102.build(orders[0], selection, root)
            second = v102.build(orders[1], selection, root)
            self.assertEqual(first["photo_jobs_prepared"], 4)
            self.assertEqual(first["photos_generated"], 0)
            self.assertEqual(first["provider_requests_sent"], 0)
            self.assertEqual(first["vidu_calls"], 0)
            self.assertFalse(first["publication_permitted"])
            self.assertEqual(len(first["original_frame_jobs"]), 5)
            self.assertEqual(sum(j["target_kind"] == "REAL_SOURCE_LOCKED_I2I_PHOTOGRAPH"
                                 for j in first["original_frame_jobs"]), 4)
            self.assertEqual(sum(j["target_kind"] == "VIDU_SOURCE_ANCHOR_NO_I2I"
                                 for j in first["original_frame_jobs"]), 1)
            self.assertTrue(all(len(j["source_sha256"]) == 64
                                for j in first["original_frame_jobs"]))
            self.assertTrue(set(j["job_id"] for j in first["original_frame_jobs"])
                              .isdisjoint(j["job_id"] for j in second["original_frame_jobs"]))


if __name__ == "__main__":
    unittest.main()
