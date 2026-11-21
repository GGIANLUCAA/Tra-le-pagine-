"""No network, no secrets, no paid calls. Verify strict preview isolation."""
import io
import json
import os
import sys
import tempfile
import unittest
import wave
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import artvision_qwen_oracle_tts_v1 as tts


def fake_wav():
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(24000)
        w.writeframes(b"\x00\x00" * 24000)
    return buf.getvalue()


class PreviewTests(unittest.TestCase):
    def test_remote_requires_tls_and_token(self):
        with self.assertRaisesRegex(ValueError, "HTTPS"):
            tts.generate_preview("Prova.", ".", base_url="http://example.com", token="a")
        with self.assertRaisesRegex(ValueError, "TOKEN"):
            tts.generate_preview("Prova.", ".", base_url="https://example.com", token="")
        with self.assertRaisesRegex(ValueError, "credenziali"):
            tts.generate_preview("Prova.", ".", base_url="https://user:pass@example.com", token="a")

    def test_invalid_speaker_and_empty_text(self):
        with self.assertRaisesRegex(ValueError, "Speaker"):
            tts.generate_preview("Test", ".", speaker="unknown")
        with self.assertRaisesRegex(ValueError, "Copione vuoto"):
            tts.generate_preview(" ", ".")

    def test_valid_preview_and_hash_cache_no_second_call(self):
        with tempfile.TemporaryDirectory() as root, patch.object(tts, "_fetch") as fetch, patch.object(tts.shutil, "which", return_value=None):
            fetch.side_effect = [b'{"status":"ok"}', fake_wav()]
            p = Path(root)
            (p / "VOCE.wav").write_bytes(b"APPROVED_VOICE_UNTOUCHED")
            first = tts.generate_preview("La luce racconta un volto.", p, base_url="https://tts.example.org", token="fake", speaker="ryan")
            self.assertEqual(first["duration_seconds"], 1.0)
            self.assertFalse(first["approved_for_critico"])
            self.assertEqual((p / "VOCE.wav").read_bytes(), b"APPROVED_VOICE_UNTOUCHED")
            self.assertEqual(fetch.call_count, 2)
            second = tts.generate_preview("La luce racconta un volto.", p, base_url="https://tts.example.org", token="fake")
            self.assertTrue(second["cached"])
            self.assertEqual(fetch.call_count, 2)
            self.assertTrue((p / tts.WAV_NAME).exists())
            self.assertNotIn("fake", (p / tts.MANIFEST_NAME).read_text())

    def test_non_wav_rejected_before_any_output(self):
        with tempfile.TemporaryDirectory() as root, patch.object(tts, "_fetch") as fetch:
            fetch.side_effect = [b'{"status":"ok"}', b"<html>error</html>"]
            with self.assertRaises(ValueError):
                tts.generate_preview("Nel dipinto.", root, base_url="https://tts.example.org", token="fake")
            self.assertFalse((Path(root) / tts.WAV_NAME).exists())

    def test_unhealthy_server_does_not_synthesize(self):
        with tempfile.TemporaryDirectory() as root, patch.object(tts, "_fetch", return_value=b'{"status":"unavailable"}') as fetch:
            with self.assertRaisesRegex(RuntimeError, "non pronto"):
                tts.generate_preview("Nel dipinto.", root, base_url="https://tts.example.org", token="fake")
            self.assertEqual(fetch.call_count, 1)


if __name__ == "__main__":
    unittest.main()
