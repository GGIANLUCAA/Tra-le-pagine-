"""Delivery V55 tests are offline and never import or publish videos."""
import hashlib
import json
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from src.artvision_delivery_v55 import (
    pack, validate_social, validate_opening_review, check_site,
)


class DeliveryV55Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.video = self.root / "ArtVision_Test.mp4"
        subprocess.run([
            "ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "lavfi",
            "-i", "color=c=blue:s=180x320:r=12:d=8.4",
            "-f", "lavfi", "-i", "sine=frequency=330:duration=8.4",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-shortest", str(self.video),
        ], check=True, capture_output=True)
        self.cover = self.root / "ArtVision_Test_COVER.jpg"
        Image.new("RGB", (720, 1280), color=(30, 40, 60)).save(self.cover)
        self.posts = {}
        for key in ("facebook", "instagram", "tiktok", "youtube"):
            dest = self.root / ("POST_" + key + ".txt")
            dest.write_text(
                "Una breve storia documentata sul dipinto, con un dettaglio vero "
                f"scelto per il pubblico di {key}. Questa descrizione è distinta e pertinente.",
                encoding="utf-8",
            )
            self.posts[key] = dest
        self.rights = self.root / "SOURCES_AND_RIGHTS.md"
        self.rights.write_text("Fonti e diritti per il test tecnico, da verificare prima della pubblicazione.")
        self.recipe = self.root / "RECIPE.json"
        self.recipe.write_text('{"schema":"test-recipe"}', encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_full_local_bundle_and_integrity_without_false_delivery_claim(self):
        out = self.root / "delivery"
        report = pack(self.video, self.cover, self.posts,
                      self.rights, self.recipe, out)
        self.assertTrue(report["local_verified"])
        self.assertFalse(report["delivery"]["complete_across_channels"])
        self.assertEqual(report["delivery"]["archive_video"], "not_checked")
        self.assertEqual(report["delivery"]["chatgpt_mp4_link"], "not_tested_by_host")
        self.assertTrue(report["release_gate"]["opening_blockers"])
        self.assertEqual(len(report["first_seconds"]["actual_frames_extracted"]), 5)
        z = out / report["local_files"]["zip"]
        with zipfile.ZipFile(z) as archive:
            self.assertIsNone(archive.testzip())
            names = set(archive.namelist())
            self.assertIn("05_PRIMI_7_SECONDI/APERTURA_PRIMI_7_SECONDI.jpg", names)
            self.assertIn("02_COPERTINA/COPERTINA.jpg", names)
            self.assertIn("04_FONTI_E_RICETTA/RICETTA.json", names)
            for key in ("FACEBOOK", "INSTAGRAM", "TIKTOK", "YOUTUBE"):
                self.assertIn("03_POST_SOCIAL/POST_" + key + ".txt", names)
        self.assertEqual(hashlib.sha256((out / report["local_files"]["mp4"]).read_bytes()).hexdigest(),
                         report["video_sha256"])
        with self.assertRaisesRegex(ValueError, "non vuota"):
            pack(self.video, self.cover, self.posts, self.rights, self.recipe, out)

    def test_duplicates_and_missing_cover_are_rejected(self):
        self.posts["instagram"].write_text(self.posts["facebook"].read_text(encoding="utf-8"),
                                           encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Post duplicati"):
            validate_social(self.posts)
        self.cover.unlink()
        with self.assertRaisesRegex(ValueError, "inesistente"):
            pack(self.video, self.cover, self.posts, self.rights,
                 self.recipe, self.root / "delivery")

    def test_video_hash_specific_review_required(self):
        sha = hashlib.sha256(self.video.read_bytes()).hexdigest()
        review = {
            "video_sha256": sha,
            "reviewer": "agent",
            "specific_observation":
                "Il primo fotogramma mostra il dettaglio autentico, in posizione centrale.",
        }
        for field in ("watched_first_7_seconds", "title_and_artist_legible",
                      "mobile_safe_composition", "authentic_specific_visual_hook",
                      "no_accidental_black_frames", "voice_or_music_starts_appropriately"):
            review[field] = True
        self.assertEqual(validate_opening_review(review, sha), [])
        review_path = self.root / "opening.json"
        review_path.write_text(json.dumps(review), encoding="utf-8")
        self.assertEqual(pack(self.video, self.cover, self.posts, self.rights,
                              self.recipe, self.root / "approved-open")["first_seconds"]
                         ["human_or_agent_visual_review"], "self_attested")
        review["video_sha256"] = "0" * 64
        self.assertTrue(validate_opening_review(review, sha))

    def test_site_catalog_missing_is_not_falsely_confirmed(self):
        class FakeResponse:
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self, *args): return b'{"items":[]}'
        with patch("src.artvision_delivery_v55.urllib.request.urlopen", return_value=FakeResponse()):
            report = check_site("Missing.mp4")
        self.assertFalse(report["catalog_visible"])
        self.assertFalse(report["playback_range_verified"])
        self.assertFalse(report["post_social_saved_verified"])
        self.assertFalse(report["zip_site_verified"])

    def test_site_key_cannot_escape_media_path(self):
        with self.assertRaises(ValueError):
            check_site("../untrusted.mp4")


if __name__ == "__main__":
    unittest.main()
