"""Conservative V119 assertions: fake approvals and legacy galleries must fail."""
import importlib.util
import json
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "museum_guard", ROOT / "src" / "artvision_museum_v119_guard.py")
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)

class TestMuseumV119(unittest.TestCase):
    def setUp(self):
        self.catalog = json.loads((ROOT / "config" / "artvision_museum_library_v119.json").read_text())

    def test_catalog_is_valid_but_not_approved(self):
        self.assertEqual(guard.check_catalog(self.catalog), [])
        self.assertEqual(sum(r["status"] == "approved" for r in self.catalog["rooms"]), 0)

    def test_unknown_preset_cannot_pass(self):
        self.assertIn("room_preset_not_in_catalog", guard.check_work(self.catalog, {
            "room_preset_id": "MADE_UP",
            "frame_status": "unverified",
        }, str(ROOT / "src" / "artvision_four_original_v116.py")))

    def test_legacy_v116_renderer_always_fails(self):
        self.assertEqual(guard.check_real_render(ROOT / "src" / "artvision_four_original_v116.py"),
                         ["legacy_bitmap_museum_renderer_forbidden"])

    def test_legacy_v117_renderer_always_fails(self):
        self.assertEqual(guard.check_real_render(ROOT / "src" / "artvision_missing_critico_v117.py"),
                         ["legacy_bitmap_museum_renderer_forbidden"])

    def test_fake_approval_fails_catalog(self):
        room = self.catalog["rooms"][0]
        room["status"] = "approved"
        room["artistic_approval"] = True
        self.assertIn("GAL01_approved_without_real_asset_and_mp4", guard.check_catalog(self.catalog))

    def test_missing_dimensions_and_frame_fail(self):
        problems = guard.check_work(self.catalog, {
            "room_preset_id": "GAL01",
            "frame_preset_or_bespoke_id": "FRA01",
            "frame_status": "unverified",
            "width_cm": 0, "height_cm": 100
        }, "not_real_renderer.py")
        self.assertIn("width_cm_invalid", problems)
        self.assertIn("unverified_frame_needs_specific_owner_approval", problems)
        self.assertIn("room_not_yet_approved", problems)
        self.assertIn("frame_preset_not_yet_approved", problems)

    def test_simple_raster_room_not_allowed(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "fake.py"
            p.write_text("def room_card(im): return im\n", encoding="utf8")
            self.assertIn("raster_room_card_renderer_forbidden", guard.check_real_render(p))

if __name__ == "__main__":
    unittest.main()
