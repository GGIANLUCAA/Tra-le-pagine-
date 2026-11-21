import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "artvision_voice_autopilot", ROOT / "src/artvision_voice_autopilot_v1.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

SETTINGS = {
    "default_by_format": {"critico_standard": "gacrux", "critico_museum": "gacrux"},
    "profiles": {
        "gacrux": {"engine": "existing_gemini", "approved": True, "model": "gemini"},
        "qwen": {"engine": "qwen_local", "approved": False, "model": "qwen"}
    }
}


class VoiceAutopilotTests(unittest.TestCase):
    def job(self, **kw):
        return dict({"work_id": "painting_001", "format": "critico_standard",
                     "allow_paid_api": False, "auto_publish": False}, **kw)

    def test_existing_approved_voice_preserved(self):
        p = mod.plan_job(self.job(), SETTINGS)
        self.assertEqual(p["state"], "EXISTING_GACRUX_PIPELINE_UNCHANGED")

    def test_new_voice_needs_owner_approval(self):
        p = mod.plan_job(self.job(voice_profile="qwen"), SETTINGS)
        self.assertEqual(p["state"], "PENDING_OWNER_VOICE_APPROVAL")

    def test_new_voice_after_approval_is_local_only(self):
        import copy
        s = copy.deepcopy(SETTINGS)
        s["profiles"]["qwen"]["approved"] = True
        p = mod.plan_job(self.job(voice_profile="qwen"), s)
        self.assertEqual(p["state"], "READY_LOCAL")
        self.assertEqual(p["paid_api_calls"], 0)
        self.assertEqual(len(p["shared_variants"]), 2)

    def test_paid_api_and_publication_forbidden(self):
        for override in ({"allow_paid_api": True}, {"auto_publish": True}):
            j = self.job()
            j.update(override)
            with self.assertRaises(ValueError):
                mod.plan_job(j, SETTINGS)

    def test_path_traversal_forbidden(self):
        with self.assertRaises(ValueError):
            mod.safe_repo_file("../../etc/passwd")

    def test_chunking_no_words_lost(self):
        original = "Il quadro è silenzioso. Eppure racconta una storia. " * 15
        chunks = mod.chunks(original, limit=75)
        self.assertGreater(len(chunks), 3)
        self.assertEqual(" ".join(chunks), original.strip())


if __name__ == "__main__":
    unittest.main()
