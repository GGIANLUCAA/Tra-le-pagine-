"""Archivio V7: test offline, senza API o credenziali."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from archivio_media_v7 import (allowed_media_url, attribution, check_signature,
    discover, download_approved, image_from_openverse, pexels_from_video, render_html, lookup)


def sample_openverse(**extra):
    data = {
        "id": "00000000-0000-4000-8000-000000000001",
        "license": "by",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "creator": "Fotografo",
        "title": "Fiume",
        "url": "https://upload.wikimedia.org/wikipedia/commons/a/ab/fiume.jpg",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/fiume.jpg",
        "foreign_landing_url": "https://commons.wikimedia.org/wiki/File:Fiume.jpg",
    }
    data.update(extra)
    return data


class ArchivioV7Tests(unittest.TestCase):
    def test_cc_by_creates_provenance(self):
        result = image_from_openverse(sample_openverse())
        self.assertEqual(result["license"], "BY")
        self.assertIn("Fotografo", attribution(result))
        self.assertTrue(result["needs_manual_rights_check"])

    def test_nonderivative_and_noncommercial_excluded(self):
        for lic in ("by-nc", "by-nd", "by-sa", "sampling+", ""):
            self.assertIsNone(image_from_openverse(sample_openverse(license=lic)))

    def test_cc0_is_included_only_with_correct_url(self):
        self.assertIsNotNone(image_from_openverse(sample_openverse(
            license="cc0", license_url="https://creativecommons.org/publicdomain/zero/1.0/")))
        self.assertIsNone(image_from_openverse(sample_openverse(
            license="cc0", license_url="https://example.com/not-cc0")))

    def test_import_domains_and_redirect_are_restricted(self):
        self.assertTrue(allowed_media_url(
            "https://upload.wikimedia.org/wikipedia/commons/example.png", "openverse", "image"))
        self.assertFalse(allowed_media_url("http://upload.wikimedia.org/x", "openverse", "image"))
        self.assertFalse(allowed_media_url(
            "https://localhost/admin", "openverse", "image"))
        self.assertFalse(allowed_media_url(
            "https://evil.org/a.jpg", "openverse", "image"))
        self.assertFalse(allowed_media_url(
            "https://images.pexels.com/a.mp4", "pexels", "video"))

    def test_reject_bad_fake_video(self):
        self.assertFalse(check_signature(b"<html>not a movie</html>", "video"))
        self.assertTrue(check_signature(b"\x00\x00\x00\x18ftypisom", "video"))
        self.assertTrue(check_signature(b"\xff\xd8\xff\xe0", "image"))

    def test_html_escaping_and_no_auto_approve(self):
        r = image_from_openverse(sample_openverse(title="<script>alert(1)</script>"))
        h = render_html([r], "openverse", "fiume")
        self.assertNotIn("<script>", h)
        self.assertIn("&lt;script&gt;", h)
        self.assertIn("Nessuna importazione automatica", h)

    def test_pexels_video_metadata(self):
        v = pexels_from_video({
            "id": 1, "video_files": [
                {"file_type": "video/mp4", "width": 1920, "height": 1080,
                 "link": "https://videos.pexels.com/a.mp4"}],
            "user": {"name": "Autrice"}, "url": "https://www.pexels.com/video/1/",
            "image": "https://images.pexels.com/video.jpg"})
        self.assertEqual(v["author"], "Autrice")
        self.assertEqual(v["kind"], "video")

    @patch("archivio_media_v7.api_json")
    def test_discover_restricted_license(self, get):
        get.return_value = {"results": [sample_openverse(),
                           sample_openverse(id="00000000-0000-4000-8000-000000000002",
                                           license="by-nc")]}
        results = discover("openverse", "image", "river", 8)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["license"], "BY")

    def test_no_unapproved_hosts_downloaded(self):
        r = image_from_openverse(sample_openverse(url="https://random.example/file.jpg"))
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                download_approved(r, Path(td))
            self.assertEqual(list(Path(td).iterdir()), [])

    def test_no_openverse_video_search(self):
        with self.assertRaises(ValueError):
            discover("openverse", "video", "river", 8)

    def test_pexels_secret_not_hardcoded(self):
        with self.assertRaises(ValueError):
            discover("pexels", "image", "river", 8, api_key="")


if __name__ == "__main__":
    unittest.main()
