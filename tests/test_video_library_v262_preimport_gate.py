"""V262 test the actual outer artifact ZIP bytes, no R2/network/provider."""
from pathlib import Path
import io
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from video_library_v262_preimport_gate import inspect

D = (
    "Fiesole 1912: le persone intrecciano cappelli di paglia, filmate da una "
    "vera cinepresa d'epoca. Il colore è una ricostruzione artistica "
    "dalla pellicola. Si vedono i materiali, le mani e gli strumenti "
    "nella lavorazione artigianale storica."
)
POSTS = {
    "POST_FACEBOOK.txt": D + " Vi raccontiamo il contesto sociale e le fonti dei mestieri fiorentini.",
    "POST_INSTAGRAM.txt": D + " Concentrati sui piccoli gesti delle mani e sulle fibre intrecciate.",
    "POST_TIKTOK.txt": D + " Guarda il momento in cui l'intreccio prende forma davanti alla camera.",
    "POST_YOUTUBE.txt": D + " Nell'episodio esteso spieghiamo la fabbricazione artigianale.",
}

class V262Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.archive = Path(self.tmp.name) / "action-artifact.zip"
        self.files = {
            "FIESOLE_MASTER.mp4": b"synthetic MP4 test bytes, not media " * 200,
            "COPERTINA.jpg": b"\xff\xd8\xff" + b"photo" * 400,
            "FONTI_E_DIRITTI.md":
                (b"Source https://commons.wikimedia.org/wiki/File:Archive.webm; "
                 b"licensing must be inspected in Italy before actual publication."),
            **{k: v.encode("utf-8") for k,v in POSTS.items()},
        }

    def pack(self):
        with zipfile.ZipFile(self.archive, "w", zipfile.ZIP_DEFLATED) as z:
            for name, content in self.files.items():
                z.writestr("DIRECT_DELIVERY/" + name, content)

    def test_byte_complete_qualifies_but_never_approves_publication(self):
        self.pack()
        audit = inspect(self.archive)
        self.assertTrue(audit["passed"], audit)
        self.assertEqual(audit["separate_artistic_approval"], "REQUIRED")
        self.assertEqual(audit["website_upload_authorization"], "NOT_INFERRED")

    def test_missing_facebook_is_blocked(self):
        self.files.pop("POST_FACEBOOK.txt")
        self.pack()
        audit = inspect(self.archive)
        self.assertFalse(audit["passed"])
        self.assertIn("POST_FACEBOOK.txt", str(audit.get("delivery_errors", [])))

    def test_four_essential_posts_cannot_be_identical(self):
        for platform in POSTS:
            self.files[platform] = POSTS["POST_FACEBOOK.txt"].encode("utf-8")
        self.pack()
        audit = inspect(self.archive)
        self.assertFalse(audit["passed"])
        self.assertIn("POST_DUPLICATED_OR_NEAR_DUPLICATE", str(audit.get("delivery_errors", [])))

    def test_nested_only_package_does_not_count_as_outer_upload(self):
        with tempfile.TemporaryDirectory() as folder:
            nested = Path(folder) / "DELIVERY.zip"
            self.pack()
            nested.write_bytes(self.archive.read_bytes())
            self.files = {
                "FIESOLE_MASTER.mp4": self.files["FIESOLE_MASTER.mp4"],
                "ARTVISION_CONTRACT_V25.json": b'{"reviews":{"full_watch":{"passed":true}}}',
                "COMPLETE_DELIVERY.zip": nested.read_bytes(),
            }
            self.pack()
            audit = inspect(self.archive)
            self.assertFalse(audit["passed"])
            self.assertIn("POST_FACEBOOK.txt", str(audit.get("delivery_errors", [])))

    def test_two_actual_masters_are_ambiguous(self):
        self.files["OTHER_MASTER.mp4"] = b"additional different video bytes " * 180
        self.pack()
        self.assertEqual(inspect(self.archive)["reason"], "EXACTLY_ONE_OUTER_MP4_REQUIRED")

    def test_contact_sheet_does_not_substitute_cover(self):
        self.files.pop("COPERTINA.jpg")
        self.files["SAMPLE_CONTACT_SHEET.jpg"] = b"\\xff\\xd8\\xff" + b"sample" * 400
        self.pack()
        self.assertIn("REAL_JPEG_COVER_MISSING",
                      str(inspect(self.archive).get("delivery_errors", [])))

    def test_missing_cover_is_blocked(self):
        self.files.pop("COPERTINA.jpg")
        self.pack()
        self.assertIn("REAL_JPEG_COVER_MISSING", str(inspect(self.archive).get("delivery_errors", [])))

    def test_missing_rights_dossier_is_blocked(self):
        self.files.pop("FONTI_E_DIRITTI.md")
        self.pack()
        self.assertIn("SOURCE_RIGHTS_DOSSIER_MISSING_OR_DUPLICATED",
                      str(inspect(self.archive).get("delivery_errors", [])))

    def test_corrupt_archive_is_blocked(self):
        self.archive.write_bytes(b"not a zip")
        self.assertFalse(inspect(self.archive)["passed"])

if __name__ == "__main__":
    unittest.main()
