"""Offline checks for the independent, no-render Met mask preflight."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "experiments" / "preflight_single_met.py"
spec = importlib.util.spec_from_file_location("wow_single_met_preflight", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SingleMetPreflightTests(unittest.TestCase):
    def test_preflight_rejects_paths_outside_isolated_runs(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "wow_lab/runs"):
                module.run(400112, Path(directory) / "outside")

    def test_contact_sheet_shows_source_mask_and_clean_plate(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            for name in ("SOURCE_MET_ORIGINAL.jpg", "SUBJECT_MASK.png",
                         "MASK_BEFORE_RENDER.jpg", "CLEAN_PLATE_SYNTHETIC.jpg"):
                Image.new("RGB", (200, 300), (130, 140, 150)).save(
                    folder / name, format="PNG" if name.endswith(".png") else "JPEG")
            self.assertEqual(module.contact_sheet(folder), "MASK_CONTACT_SHEET.jpg")
            with Image.open(folder / "MASK_CONTACT_SHEET.jpg") as sheet:
                self.assertEqual(sheet.size, (800, 940))


if __name__ == "__main__":
    unittest.main()
