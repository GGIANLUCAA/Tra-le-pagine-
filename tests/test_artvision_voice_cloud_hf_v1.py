import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "cloud_voice", ROOT / "src/artvision_voice_cloud_hf_v1.py")
voice = importlib.util.module_from_spec(spec)
spec.loader.exec_module(voice)
CFG = json.loads((ROOT / "config/artvision_voice_profiles_v1.json").read_text())


class CloudVoiceTests(unittest.TestCase):
    def request(self, **extras):
        values = {"work_id": "painting_001", "format": "critico_standard",
                  "allow_paid_api": False, "auto_publish": False}
        values.update(extras)
        return values

    def test_candidate_never_auto_replaces_approved_voice(self):
        p = voice.plan(self.request(), CFG)
        self.assertEqual(p["state"], "WAITING_OWNER_APPROVAL")
        self.assertEqual(p["paid_api_calls"], 0)

    def test_review_is_only_by_explicit_request(self):
        p = voice.plan(self.request(review_only=True), CFG)
        self.assertEqual(p["state"], "REVIEW_ONLY")
        self.assertEqual(p["engine"], "hf_zerogpu")
        self.assertEqual(len(p["shared_variants"]), 2)

    def test_production_requires_approval(self):
        local = json.loads(json.dumps(CFG))
        local["profiles"]["qwen_hf_candidate"]["approved"] = True
        p = voice.plan(self.request(), local)
        self.assertEqual(p["state"], "READY_CLOUD")

    def test_paid_or_autopublish_denied(self):
        with self.assertRaises(ValueError):
            voice.plan(self.request(allow_paid_api=True), CFG)
        with self.assertRaises(ValueError):
            voice.plan(self.request(auto_publish=True), CFG)

    def test_format_validation_and_path_traversal(self):
        with self.assertRaises(ValueError):
            voice.plan(self.request(format="documentario"), CFG)
        with self.assertRaises(ValueError):
            voice.script_path("../../../../etc/passwd")

    def test_segment_text_preservation(self):
        text = ("Il dipinto apre una finestra sul tempo. "
                "Una luce lenta attraversa il paesaggio. ") * 12
        result = voice.segments(text, limit=112)
        self.assertGreater(len(result), 2)
        self.assertEqual(" ".join(result), text.strip())


if __name__ == "__main__":
    unittest.main()
