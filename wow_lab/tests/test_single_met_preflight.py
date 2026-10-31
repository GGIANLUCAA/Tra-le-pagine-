"""Offline checks for the independent, no-render Met mask preflight."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import json
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

    def test_failed_source_download_writes_blocked_report_without_video(self):
        (ROOT / "runs").mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / "runs") as parent:
            out = Path(parent) / "single-candidate"
            record = {
                "objectID": 400112, "isPublicDomain": True,
                "objectName": "Drawing", "title": "A Moth",
                "primaryImage": "https://images.metmuseum.org/CRDImages/dp/original/DP820071.jpg",
            }
            with (patch.object(module.engine, "get_json", return_value=record),
                  patch.object(module.engine, "save_original",
                               side_effect=RuntimeError("source host unavailable"))):
                with self.assertRaisesRegex(RuntimeError, "source host unavailable"):
                    module.run(400112, out)
            report = json.loads((out / "PREFLIGHT_RESULT.json").read_text())
            self.assertEqual(report["status"], "source_acquisition_blocked")
            self.assertFalse(report["publishable"])
            self.assertFalse(list(out.glob("*.mp4")))

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
