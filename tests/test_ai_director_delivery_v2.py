#!/usr/bin/env python3
"""No-network regressions for AI Director V2 delivery and safe artifact intake."""
import io
import json
import stat
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import ai_director_delivery_v2 as d
import ai_director_artifact_fetch_v2 as a


class DeliveryV2Tests(unittest.TestCase):
    def test_estimated_giuliano_timing_never_claims_real_asr(self):
        brief = d._timed_brief({"scenes": [
            {"asset_id": "gears", "narration": "Ingranaggi", "estimated_seconds": .8},
            {"asset_id": "moon", "narration": "La Luna", "estimated_seconds": 3.2}]},
            "giuliano", "Meccanismo di Anticitera")
        self.assertEqual(len(brief["scenes"]), 2)
        self.assertIn("estimated", brief["timecode_provenance"])
        self.assertEqual(brief["scenes"][0]["rights_status"], "pending_independent_proof")

    def test_real_artvision_storyboard_duration_s_and_start_s(self):
        payload = {"scenes": [
            {"shot": 1, "description": "Original painting", "start_s": 0.0,
             "duration_s": 4.8, "human_visual_review": "PENDING"},
            {"shot": 2, "description": "Close-up", "start_s": 4.8,
             "duration_s": 3.3, "human_visual_review": "PENDING"}]}
        brief = d._timed_brief(payload, "artvision_4x1", "Sleeping Beauty")
        self.assertEqual(len(brief["scenes"]), 2)
        self.assertEqual(brief["scenes"][1]["start_s"], 4.8)
        self.assertEqual(brief["scenes"][1]["end_s"], 8.1)
        self.assertEqual(brief["timecode_provenance"],
                         "manifest_declared_times_not_independent_ASR")

    def test_report_without_video_is_honest_and_android_readable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "input").mkdir()
            result = d.review(root / "input", root / "out", fmt="storia_rivive",
                              subject="Venezia 1896")
            self.assertEqual(result["variants"][0]["status"], "awaiting_real_video")
            self.assertFalse(result["automatic_publication"])
            self.assertFalse(result["source_rights_verified"])
            self.assertEqual(result["automatic_paid_calls"], 0)
            self.assertTrue((root / "out" / "INDEX.html").is_file())
            report = json.loads((root / "out" / "episode" / "REPORT.json").read_text())
            self.assertFalse(report["technical_video_checked"])
            self.assertFalse(report["human_artistic_approval"])

    def test_actual_mp4_diagnostics_are_not_artistic_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inp = root / "input"
            inp.mkdir()
            video = inp / "DOCUMENTARY_MASTER.mp4"
            video.write_bytes(b"0" * 130)
            (inp / "EP03_SCRIPT_SHOTMAP_V1.json").write_text(json.dumps({
                "schema": "giuliano-antikythera-episode-v1",
                "scenes": [{"asset_id": "a", "estimated_seconds": .55,
                            "narration": "Il relitto è antico."}] }))
            fake = {"status": "technical_review_only", "duration_s": 4.2,
                    "issues": [{"code": "POSSIBLE_BLINK_FRAME", "severity": "warning",
                                "message": "Review quick change"}]}
            with patch.object(d, "inspect_mp4", return_value=fake), patch.object(
                d, "inspect_black_tail", return_value=([], {"black_tail_scan": "done"})):
                d.review(inp, root / "out", fmt="giuliano", subject="Antikythera")
            report = json.loads((root / "out" / "episode" / "REPORT.json").read_text())
            self.assertTrue(report["technical_video_checked"])
            self.assertIn("MICRO_FLASH", [x["code"] for x in report["issues"]])
            self.assertFalse(report["finished_video_claim"])
            self.assertFalse(report["narration_alignment_verified"] if
                             "narration_alignment_verified" in report else
                             report["visual_diagnostics"].get("narration_alignment_verified", False))
            self.assertEqual(report["model_calls"], 0)
            self.assertFalse(report["publication_authorized"])
            self.assertTrue(report["director_and_critic_prompts_prepared"])
            self.assertFalse(report["independent_llm_reviews_executed"])
            prompt = json.loads((root / "out" / "episode" / "EDITORIAL_PROMPTS.json").read_text())
            self.assertIn("director", prompt)
            self.assertIn("critic", prompt)
            self.assertIn("POSSIBLE_BLINK_FRAME",
                          (root / "out" / "episode" / "ANDROID_REPORT.html").read_text())

    def test_four_variants_remain_separate_and_no_single_video_is_misattributed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inp = root / "files"
            inp.mkdir()
            (inp / "ARTVISION_4X1_PLAN.json").write_text(json.dumps({
                "schema": "artvision-4x1-v1", "topic": "The Goldfinch",
                "artist": "Carel Fabritius",
                "variants": {k: {"scenes": [{"duration_seconds": 3.3,
                       "spoken_line": "Il cardellino" if k.startswith("critico") else "",
                       "detail_id": "bird"}]} for k in (
                    "critico_standard", "critico_museum",
                    "cinema_standard", "cinema_museum")}}))
            result = d.review(inp, root / "out", fmt="artvision_4x1",
                              subject="The Goldfinch")
            self.assertEqual(len(result["variants"]), 4)
            self.assertTrue(all(not x["video_checked"] for x in result["variants"]))
            self.assertTrue((root / "out" / "critico_museum" / "REPORT.json").is_file())

    def test_manifest_path_outside_input_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inp = root / "input"
            inp.mkdir()
            (root / "evil.json").write_text("{}")
            with self.assertRaisesRegex(ValueError, "inside input"):
                d.review(inp, root / "out", fmt="giuliano", subject="Something",
                         manifest=root / "evil.json")

    def test_html_escapes_untrusted_video_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inp = root / "input"
            inp.mkdir()
            video = inp / "video_<script>alert(1).mp4"
            video.write_bytes(b"x" * 120)
            with patch.object(d, "inspect_mp4", return_value={
                    "status": "technical_review_only", "duration_s": 1,
                    "issues": []}), patch.object(
                         d, "inspect_black_tail", return_value=([], {})):
                d.review(inp, root / "out", fmt="wow_lab", subject="WOW")
            page = (root / "out" / "episode" / "ANDROID_REPORT.html").read_text()
            self.assertNotIn("<script>", page)
            self.assertIn("&lt;script&gt;", page)


class ArtifactV2Tests(unittest.TestCase):
    def test_reject_other_repo_or_paid_unapproved_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            def fake_get(url, key):
                return {"repository": {"full_name": "other/repo"},
                        "head_repository": {"full_name": "other/repo"},
                        "status": "completed", "conclusion": "success"}
            with self.assertRaisesRegex(ValueError, "another repository"):
                a.acquire("GGIANLUCAA/Tra-le-pagine-", 42, "",
                          Path(tmp), "fake", get=fake_get)

    def test_failed_producer_has_no_download(self):
        with tempfile.TemporaryDirectory() as tmp:
            def fake_get(url, key):
                return {"repository": {"full_name": "GGIANLUCAA/Tra-le-pagine-"},
                        "head_repository": {"full_name": "GGIANLUCAA/Tra-le-pagine-"},
                        "status": "completed", "conclusion": "failure"}
            r = a.acquire("GGIANLUCAA/Tra-le-pagine-", 42, "",
                          Path(tmp), "fake", get=fake_get)
            self.assertEqual(r["status"], "producer_not_successful")

    def test_signed_artifact_redirect_does_not_forward_github_token(self):
        import urllib.request
        original = urllib.request.Request(
            "https://api.github.com/repos/owner/repo/actions/artifacts/42/zip",
            headers={"Authorization": "Bearer private-token"})
        next_req = a._SafeArtifactRedirect().redirect_request(
            original, None, 302, "Found", {},
            "https://productionresultssa1.blob.core.windows.net/download?sig=abc")
        self.assertIsNotNone(next_req)
        self.assertNotIn("Authorization", next_req.headers)
        self.assertNotIn("Authorization", next_req.unredirected_hdrs)

    def test_zip_rejects_traversal_symlink_and_unrelated_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = root / "sample.zip"
            with zipfile.ZipFile(archive, "w") as z:
                z.writestr("../escape.mp4", b"not allowed")
                z.writestr("run.sh", b"echo dangerous")
                z.writestr("folder/QA.json", b'{"ok":true}')
                z.writestr("folder/VIDEO_ANDROID.mp4", b"a" * 140)
                link = zipfile.ZipInfo("links/bad.mp4")
                link.create_system = 3
                link.external_attr = (stat.S_IFLNK | 0o777) << 16
                z.writestr(link, "target")
            dest = root / "files"
            dest.mkdir()
            found = a._unpack(archive, dest)
            self.assertEqual({x["name"] for x in found}, {"QA.json", "VIDEO_ANDROID.mp4"})
            self.assertFalse((root / "escape.mp4").exists())
            self.assertFalse((dest / "run.sh").exists())

    def test_selection_downloads_one_and_provides_verified_media(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            def fake_get(url, key):
                if "/artifacts?" in url:
                    return {"artifacts": [{"name": "OWNER_ANDROID_REVIEW",
                                           "size_in_bytes": 1024,
                                           "archive_download_url": "https://api.github.com/fake",
                                           "expired": False}]}
                return {"repository": {"full_name": "GGIANLUCAA/Tra-le-pagine-"},
                        "head_repository": {"full_name": "GGIANLUCAA/Tra-le-pagine-"},
                        "status": "completed", "conclusion": "success"}
            def fake_download(url, token, target):
                with zipfile.ZipFile(target, "w") as z:
                    z.writestr("VIDEO_ANDROID.mp4", b"video" * 30)
                return target.stat().st_size
            r = a.acquire("GGIANLUCAA/Tra-le-pagine-", 101, "", root / "input",
                          "fake", get=fake_get, download=fake_download)
            self.assertEqual(r["status"], "extracted_for_readonly_review")
            self.assertEqual(r["artifact"], "OWNER_ANDROID_REVIEW")
            self.assertTrue((root / "input" / "VIDEO_ANDROID.mp4").exists())


if __name__ == "__main__":
    unittest.main()
