import hashlib
import json
import sys
import tempfile
import unittest
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import voice_recovery_gate_v16 as gate


class VoiceRecoveryGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "cache/voice/ep").mkdir(parents=True)

    def tearDown(self):
        self.temp.cleanup()

    def entry(self, wav_hash):
        return {
            "episode": "ep",
            "status": "historical_metadata_only",
            "target_cache_dir": "cache/voice/ep",
            "wav_sha256": wav_hash,
            "sample_rate": 24000,
            "channels": 1,
            "duration_seconds": 1.0,
        }

    def test_metadata_without_bytes_is_blocked(self):
        result = gate.inspect_entry(self.root, self.entry("0" * 64))
        self.assertFalse(result["render_cache_ready"])
        self.assertIn("exact_local_wav_missing", result["blockers"])

    def test_exact_wav_and_all_adapter_files_are_ready(self):
        cache = self.root / "cache/voice/ep"
        with wave.open(str(cache / "VOCE.wav"), "wb") as audio:
            audio.setnchannels(1)
            audio.setsampwidth(2)
            audio.setframerate(24000)
            audio.writeframes(b"\0\0" * 24000)
        for name in gate.ADAPTER_FILES[1:]:
            (cache / name).write_text("{}", encoding="utf-8")
        digest = hashlib.sha256((cache / "VOCE.wav").read_bytes()).hexdigest()
        result = gate.inspect_entry(self.root, self.entry(digest))
        self.assertTrue(result["render_cache_ready"], result["blockers"])

    def test_path_escape_is_rejected(self):
        entry = self.entry("0" * 64)
        entry["target_cache_dir"] = "../outside"
        with self.assertRaises(ValueError):
            gate.inspect_entry(self.root, entry)


if __name__ == "__main__":
    unittest.main()
