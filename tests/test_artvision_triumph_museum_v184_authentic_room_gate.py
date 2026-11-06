"""V184 regression: authentic framed-photo != authenticated museum room.
Run: python -m unittest tests/test_artvision_triumph_museum_v184_authentic_room_gate.py
No rendering, credits, publication or master mutation.
"""
import ast
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
RENDERERS = (
    "src/artvision_bruegel_triumph_cinema_museum_v182.py",
    "src/artvision_bruegel_triumph_critico_museum_v183.py",
)

class MuseumAuthenticityGate(unittest.TestCase):
    def test_museum_requires_photographed_room_not_generated_background(self):
        for rel in RENDERERS:
            source = (ROOT / rel).read_text(encoding="utf-8")
            tree = ast.parse(source, filename=rel)
            staged = next((n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "staged"), None)
            self.assertIsNotNone(staged, rel)
            asset = next((n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_museum_static_assets"), None)
            self.assertIsNotNone(asset, rel)
            # Existing scripts draw the real framed photograph onto an invented gradient.
            # This is a valid editorial proof, but not the V80/V118/V119 real museum room.
            gradient = any(
                isinstance(n, ast.Call)
                and isinstance(n.func, ast.Attribute)
                and n.func.attr == "full"
                and isinstance(n.func.value, ast.Name)
                and n.func.value.id == "np"
                for n in ast.walk(asset)
            )
            self.assertTrue(gradient, f"{rel}: update this regression when a documented room source replaces synthetic background")
            self.assertIn("museum_approved':False", source, rel)
            self.assertIn("'human_artistic_review':'PENDING'", source, rel)

    def test_no_claim_of_final_museum_delivery(self):
        for rel in RENDERERS:
            source = (ROOT / rel).read_text(encoding="utf-8")
            self.assertIn("'Gold_V25':False", source, rel)
            self.assertIn("'social_published':False", source, rel)
            self.assertIn("PHOTO_SHA=", source, rel)

if __name__ == "__main__":
    unittest.main()
