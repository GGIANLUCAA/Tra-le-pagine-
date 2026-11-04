"""V265 offline safety and source-lock tests. No model calls or credits."""
import ast
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import storia_rivive_v265_fiesole_first_fullcolor_cpu as v


class SafeFiesoleFullColor(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.out = Path(self.tmp.name)

    def test_specific_color_instructions_are_not_monochrome(self):
        self.assertIn("golden yellow", v.PROMPT)
        self.assertIn("wooden machines brown", v.PROMPT)
        self.assertIn("Keep identical machines", v.PROMPT)
        self.assertLess(len(v.PROMPT.split()), 55)

    def test_no_safety_checker_disabled_in_model_constructor(self):
        source = Path(v.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Attribute)
                 and n.func.attr == "from_pretrained"]
        self.assertEqual(len(calls), 1)
        forbidden = {"safety_checker", "requires_safety_checker", "feature_extractor"}
        self.assertFalse(forbidden.intersection(
            {kw.arg for kw in calls[0].keywords}
        ))

    def test_report_never_claims_approval_even_if_photo_generated(self):
        p = self.out / v.REPORT
        p.write_text(json.dumps({"status": "REAL_CPU_DIFFUSION_PHOTO_GENERATED",
                                 "actual_generated_photos": 1,
                                 "artistic_approval": True,
                                 "publish_allowed": True}), encoding="utf-8")
        v.stamp_report(self.out)
        doc = json.loads(p.read_text(encoding="utf-8"))
        self.assertEqual(doc["source_shot"], 1)
        self.assertFalse(doc["artistic_approval"])
        self.assertFalse(doc["publish_allowed"])
        self.assertFalse(doc["italian_rights_verified"])
        self.assertFalse(doc["safety_checker_disabled"])
        self.assertEqual(doc["new_final_episodes_delivered"], 0)
        self.assertEqual(doc["actual_generated_photos"], 1)

    def test_failed_inference_stays_failed_and_restores_shared_engine(self):
        p = self.out / v.REPORT
        original = v.engine.run_one_real_i2i
        old_prompt, old_seed = v.first.PROMPT, v.first.SEED
        def blocked():
            p.write_text(json.dumps({"status":"LOCAL_CPU_DIFFUSION_NO_VALID_PHOTO",
                                     "actual_generated_photos":0}), encoding="utf-8")
            raise ValueError("V257_NO_ACTUAL_MODEL_PHOTO")
        with patch.object(sys, "argv", ["v265", "--source", "a.png",
                                          "--manifest", "m.json",
                                          "--out", str(self.out)]):
            with patch.object(v.first, "main", side_effect=blocked):
                with self.assertRaisesRegex(ValueError, "V257_NO_ACTUAL_MODEL_PHOTO"):
                    v.main()
        doc = json.loads(p.read_text(encoding="utf-8"))
        self.assertEqual(doc["actual_generated_photos"], 0)
        self.assertEqual(doc["new_final_episodes_delivered"], 0)
        self.assertIs(v.engine.run_one_real_i2i, original)
        self.assertEqual(v.first.PROMPT, old_prompt)
        self.assertEqual(v.first.SEED, old_seed)

    def test_source_gate_reused(self):
        source = Path(v.__file__).read_text(encoding="utf-8")
        self.assertIn("first.main()", source)
        self.assertIn("storia_rivive_v261_fiesole_first_source_i2i", source)


if __name__ == "__main__":
    unittest.main()
