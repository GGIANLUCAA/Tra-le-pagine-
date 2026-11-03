"""Offline V262 tests: concise prompt, fail closed, unchanged model safety."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import storia_rivive_v262_fiesole_first_retry as v262


class V262SafeRetry(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.out = Path(self.temp.name)

    def report(self, **values):
        (self.out / v262.QA_NAME).write_text(json.dumps(values), encoding="utf-8")

    def test_prompt_short_and_no_safety_bypass(self):
        self.assertLess(len(v262.PROMPT.split()), 47)
        self.assertIn("Preserve all existing objects", v262.PROMPT)
        self.assertNotIn("safety_checker=None", Path(v262.__file__).read_text())
        self.assertNotIn("requires_safety_checker=False", Path(v262.__file__).read_text())

    def test_failure_report_is_still_zero(self):
        self.report(status="LOCAL_CPU_DIFFUSION_NO_VALID_PHOTO", actual_generated_photos=0)
        v262.stamp_report(self.out)
        data=json.loads((self.out / v262.QA_NAME).read_text())
        self.assertEqual(data["actual_generated_photos"],0)
        self.assertEqual(data["new_final_episodes_delivered"],0)
        self.assertFalse(data["safety_checker_disabled"])
        self.assertFalse(data["publish_allowed"])
        self.assertFalse(data["artistic_approval"])

    def test_no_output_flag_fails_closed(self):
        with patch.object(sys,"argv",["script"]):
            with self.assertRaisesRegex(ValueError,"OUTPUT_PATH_REQUIRED"):
                v262.main()

    def test_inference_failure_still_stamps_report(self):
        def blocked():
            self.report(status="LOCAL_CPU_DIFFUSION_NO_VALID_PHOTO",
                        actual_generated_photos=0)
            raise ValueError("V257_NO_ACTUAL_MODEL_PHOTO")
        with patch.object(sys,"argv",["script","--out",str(self.out)]):
            with patch.object(v262.first,"main",side_effect=blocked):
                with self.assertRaisesRegex(ValueError,"V257_NO_ACTUAL_MODEL_PHOTO"):
                    v262.main()
        report=json.loads((self.out / v262.QA_NAME).read_text())
        self.assertEqual(report["version"],v262.VERSION)
        self.assertEqual(report["actual_generated_photos"],0)
        self.assertFalse(report["publish_allowed"])


if __name__=="__main__":
    unittest.main()
