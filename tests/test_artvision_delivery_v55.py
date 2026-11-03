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
        social_examples = {
            "facebook": "Vi presentiamo la storia dell'opera con il contesto del museo, una curiosità storica documentata e il collegamento agli approfondimenti.",
            "instagram": "Osservate il gioco di luce sul dettaglio principale: la pennellata, la materia cromatica e il taglio di questa inquadratura raccontano la tecnica.",
            "tiktok": "Un particolare sorprendente cambia il modo di guardare questo dipinto: partiamo dall'angolo meno noto e scopriamo il simbolo nascosto.",
            "youtube": "Nel video analizziamo composizione, restauro, firma e cronologia: il percorso completo collega le scelte dell'artista alle fonti storiche.",
        }
        for key, body in social_examples.items():
            dest = self.root / ("POST_" + key + ".txt")
            dest.write_text(body, encoding="utf-8")
            self.posts[key] = dest
        self.rights = self.root / "SOURCES_AND_RIGHTS.md"
        self.rights.write_text("Fonte inventario museale di prova: https://example.org/archive/test; diritti da verificare prima della pubblicazione.")
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
                              self.recipe, self.root / "approved-open", opening_review=review_path)["first_seconds"]
                         ["human_or_agent_visual_review"], "self_attested")
        review["video_sha256"] = "0" * 64
        self.assertTrue(validate_opening_review(review, sha))

    def test_archive_contract_requires_exact_approved_video_sha(self):
        sha = hashlib.sha256(self.video.read_bytes()).hexdigest()
        contract_file = self.root / "ARTVISION_CONTRACT_V25.json"
        checks = {name: {"passed": True} for name in (
            "opening", "visual", "cover", "music", "rights",
            "full_watch", "replicability")}
        contract_file.write_text(json.dumps({
            "schema": "artvision-release-contract-v25",
            "review_video_sha256": "0"*64,
            "reviews": checks,
        }), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "contratto non approvato"):
            pack(self.video, self.cover, self.posts, self.rights, self.recipe,
                 self.root / "bad_contract", release_contract=contract_file)
        contract_file.write_text(json.dumps({
            "schema": "artvision-release-contract-v25",
            "review_video_sha256": sha,
            "reviews": checks,
        }), encoding="utf-8")
        # V122: older V25 checkboxes alone must no longer allow final handoff.
        with self.assertRaisesRegex(ValueError, "V122"):
            pack(self.video, self.cover, self.posts, self.rights,
                 self.recipe, self.root / "identity_missing", release_contract=contract_file)
        self.recipe.write_text(json.dumps({
            "schema": "test-recipe", "variant": "cinema_standard",
            "title": "The Goldfinch", "artist": "Carel Fabritius",
        }), encoding="utf-8")
        from src.artvision_identity_delivery_v122_guard import TEMPLATES, ROOT, sha256
        template = TEMPLATES["cinema_standard"]
        identity = {
            "video_sha256": sha,
            "cover_sha256": sha256(self.cover),
            "social_sha256": {key: sha256(path) for key, path in self.posts.items()},
            "template_path": template,
            "template_sha256": sha256(ROOT / template),
            "artwork_title_en": "The Goldfinch",
            "title_language": "en",
            "reviewer": "human",
            "specific_visual_observation":
                "Revisione sintetica di prova: verificati titolo, prima scena e confini del dipinto nel vero video.",
            "specific_social_observation":
                "Test sintetico dei quattro post social distinti e riferiti all'opera.",
            "reviewed_video_timecodes_seconds": [0.1, 3.0, 7.0],
            "english_title_readable_in_actual_video": True,
            "cover_matches_frozen_series_reference": True,
            "title_typography_matches_frozen_series_reference": True,
            "four_social_captions_checked_for_this_artwork": True,
        }
        contract_file.write_text(json.dumps({
            "schema": "artvision-release-contract-v25",
            "review_video_sha256": sha, "reviews": checks,
            "identity_v122": identity,
        }), encoding="utf-8")
        output = self.root / "valid_contract"
        result = pack(self.video, self.cover, self.posts, self.rights, self.recipe,
                      output, release_contract=contract_file)
        self.assertEqual(result["release_gate"]["identity_v122_status"],
                         "hash_bound_review_attested")
        self.assertEqual(result["delivery"]["site_import_V25_contract"],
                         "exact_sha_review_verified")
        full_zip = next(output.glob("*_COMPLETO.zip"))
        with zipfile.ZipFile(full_zip) as archive:
            self.assertIn("ARTVISION_CONTRACT_V25.json", archive.namelist())

    def test_museum_v46_is_required_before_v25_final_release(self):
        sha = hashlib.sha256(self.video.read_bytes()).hexdigest()
        self.recipe.write_text(json.dumps({
            "schema": "video-recipe-v13", "variant": "cinema_museum",
            "review_state": "rendered_needs_review",
        }), encoding="utf-8")
        contract_file = self.root / "ARTVISION_CONTRACT_V25.json"
        checks = {key: {"passed": True} for key in (
            "opening", "visual", "cover", "music", "rights", "full_watch", "replicability")}
        contract_file.write_text(json.dumps({
            "schema": "artvision-release-contract-v25",
            "review_video_sha256": sha, "reviews": checks,
        }), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "V46 Museum"):
            pack(self.video, self.cover, self.posts, self.rights,
                 self.recipe, self.root / "forbidden_release", release_contract=contract_file)
        review = pack(self.video, self.cover, self.posts, self.rights,
                      self.recipe, self.root / "review_only")
        self.assertEqual(review["release_gate"]["museum_v46_status"], "pending_or_blocked")
        self.assertEqual(review["delivery"]["site_import_V25_contract"], "missing_or_not_provided")

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

    def test_common_gate_rejects_four_near_duplicate_posts(self):
        common = (
            "Questa guida racconta l'opera attraverso la stessa inquadratura, "
            "la medesima narrazione e identici dettagli ripetuti senza "
            "adattamento al pubblico e al linguaggio di ogni piattaforma. " * 3
        )
        for key in self.posts:
            self.posts[key].write_text(common + " Post per " + key, encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "POST_DUPLICATED_OR_NEAR_DUPLICATE"):
            pack(self.video, self.cover, self.posts, self.rights,
                 self.recipe, self.root / "near_duplicates")

    def test_common_gate_rejects_missing_source_url(self):
        self.rights.write_text(
            "Documento non specifico, nessun URL della fonte presente per questa opera.",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "SOURCE_RIGHTS_DOSSIER_INCOMPLETE"):
            pack(self.video, self.cover, self.posts, self.rights,
                 self.recipe, self.root / "incomplete_rights")

    def test_site_key_cannot_escape_media_path(self):
        with self.assertRaises(ValueError):
            check_site("../untrusted.mp4")


if __name__ == "__main__":
    unittest.main()
