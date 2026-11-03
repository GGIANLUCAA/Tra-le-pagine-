"""V260 regressions on archive bytes, not flags. No provider calls."""
from pathlib import Path
import tempfile
import unittest
import zipfile
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "src/storia_rivive_v260_delivery_bundle_gate.py"
spec = importlib.util.spec_from_file_location("delivery_v260", MODULE)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

DESCRIPTION = (
    "Fiesole nel 1912: un viaggio tra persone e mestieri d'epoca, "
    "con una ricostruzione digitale a colori creata dalle riprese originali. "
    "Scopri come venivano realizzati i cappelli di paglia e osserva ogni gesto in movimento. "
    "Il filmato archivistico rimane la fonte storica, il restauro è una ricostruzione AI."
)
RIGHTS = (
    "Fonte originale: https://commons.wikimedia.org/wiki/File:Manufacture_de_chapeaux_de_paille_a_Fiesole.webm "
    "Licenza e riutilizzo italiano ancora in verifica; non pubblicare prima della verifica."
)

class TestV260(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        self.movie = self.folder / "FIESOLE.mp4"
        self.movie.write_bytes(b"fake-mp4-for-archive-only-test" * 100)
        self.archive = self.folder / "DELIVERY.zip"
        self.files = {
            "FIESOLE.mp4": self.movie.read_bytes(),
            "COVER.jpg": b"\xff\xd8\xff" + b"photo" * 350,
            "SOURCES_AND_RIGHTS.md": RIGHTS.encode(),
        }
        self.files.update({name: DESCRIPTION.encode() for name in gate.REQUIRED_POSTS})

    def pack(self):
        with zipfile.ZipFile(self.archive, "w", zipfile.ZIP_DEFLATED) as z:
            for name, data in self.files.items():
                z.writestr("FIESOLE_1912/" + name, data)

    def test_valid_materials(self):
        self.pack()
        report = gate.inspect(self.movie)
        self.assertFalse(report["errors"], report)
        self.assertTrue(report["checks"]["identical_final_mp4_inside_zip"])

    def test_missing_facebook_post_blocks_even_with_manifest_flag(self):
        self.files.pop("POST_FACEBOOK.txt")
        self.pack()
        self.assertTrue(any("POST_FACEBOOK" in e for e in gate.inspect(self.movie)["errors"]))

    def test_placeholder_post_rejected(self):
        self.files["POST_INSTAGRAM.txt"] = b"TODO"
        self.pack()
        self.assertTrue(any("POST_EMPTY" in e for e in gate.inspect(self.movie)["errors"]))

    def test_wrong_mp4_in_zip_rejected(self):
        self.files["FIESOLE.mp4"] = b"other-video" * 200
        self.pack()
        self.assertIn("FINAL_MP4_ZIP_BYTES_MISMATCH",
                      gate.inspect(self.movie)["errors"])

    def test_cover_required(self):
        self.files.pop("COVER.jpg")
        self.pack()
        self.assertIn("REAL_JPEG_COVER_MISSING",
                      gate.inspect(self.movie)["errors"])

    def test_rights_dossier_required(self):
        self.files.pop("SOURCES_AND_RIGHTS.md")
        self.pack()
        self.assertIn("SOURCE_RIGHTS_DOSSIER_MISSING_OR_DUPLICATED",
                      gate.inspect(self.movie)["errors"])

    def test_missing_archive_rejected(self):
        self.assertIn("DELIVERY_ZIP_MISSING_OR_AMBIGUOUS",
                      gate.inspect(self.movie)["errors"])

    def test_multiple_archives_rejected_without_explicit_selection(self):
        self.pack()
        (self.folder / "SECOND.zip").write_bytes(self.archive.read_bytes())
        self.assertIn("DELIVERY_ZIP_MISSING_OR_AMBIGUOUS",
                      gate.inspect(self.movie)["errors"])

if __name__ == "__main__":
    unittest.main()
