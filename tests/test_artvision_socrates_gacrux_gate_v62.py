import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
GATE=ROOT/"src/artvision_socrates_gacrux_gate_v62.py"
class GacruxSafetyTests(unittest.TestCase):
    def test_exact_script_and_free_gate_do_not_spend_or_create_audio(self):
        with tempfile.TemporaryDirectory() as d:
            out=pathlib.Path(d)/"GATE.json"
            cache=pathlib.Path(d)/"cache"
            env=os.environ.copy()
            env.update(GEMINI_TTS_FREE_QUOTA_CONFIRMED="false",
                       GEMINI_TTS_PROJECT_BILLING_DISABLED_CONFIRMED="false",
                       GEMINI_API_KEY="dummy_does_not_authorize_any_call")
            subprocess.run([sys.executable,str(GATE),"--out",str(out),"--cache",str(cache)],
                           env=env,cwd=ROOT,check=True,capture_output=True)
            report=json.loads(out.read_text())
            self.assertEqual(report["status"],"blocked_voice_free_tier_not_verified")
            self.assertEqual(report["paid_tts_calls"],0)
            self.assertEqual(report["slots"],["critico_standard","critico_museum"])
            self.assertFalse((cache/"VOCE.wav").exists())
    def test_exact_master_still_contains_10_story_beats(self):
        script=(ROOT/"docs/productions/2026-10-29-socrates-critico-master-v60/COPIONE_GACRUX_V62.txt").read_text().strip()
        self.assertEqual(len(script.split()),366)
        self.assertEqual(len(script.split("\n\n")),10)
        self.assertIn("Platone",script)
        self.assertIn("cicuta",script)
if __name__=="__main__":
    unittest.main()
