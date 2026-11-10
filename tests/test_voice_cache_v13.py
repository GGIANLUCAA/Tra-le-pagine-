"""Real WAV cache tests with no Google SDK, network or API key."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import gemini_voice as voice


class VoiceCacheTests(unittest.TestCase):
    text = "Anna apre la porta. Poi torna al mare."

    def seed(self, folder):
        path = Path(folder)
        wave = np.sin(np.arange(24000) * 2 * np.pi * 440 / 24000).astype(np.float32) * .1
        sf.write(path / "VOCE.wav", wave, 24000)
        phrases = voice.sentences(self.text)
        timed = voice._estimated_timing(phrases, 1.0)
        voice._json_write(path / "ALLINEAMENTO_VOCE.json", {"method": "estimated", "requires_sync_review": True})
        voice._save_voice_cache(self.text, path, timed)
        return timed

    def test_cached_voice_reused_without_key_or_sdk(self):
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ, {}, clear=True):
            expected = self.seed(d)
            with patch.object(voice, "align", side_effect=AssertionError("Must reuse timing")):
                audio, timed = voice.synthesize(self.text, d)
            self.assertEqual(len(audio), 24000)
            self.assertEqual([list(x) for x in expected], timed)
            self.assertTrue((Path(d) / "VOCE_NATURALE.mp3").is_file())

    def test_changed_text_or_profile_cannot_reuse(self):
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ, {}, clear=True):
            self.seed(d)
            with self.assertRaisesRegex(RuntimeError, "GEMINI_API_KEY"):
                voice.synthesize(self.text + " La storia cambia.", d)
            with patch.object(voice, "VOICE", "DifferentVoice"):
                self.assertIsNone(voice._cached_audio(self.text, Path(d)))

    def test_same_size_corrupted_wav_is_not_reused(self):
        with tempfile.TemporaryDirectory() as d:
            self.seed(d)
            path = Path(d) / "VOCE.wav"
            data = bytearray(path.read_bytes());data[-100] ^= 1;path.write_bytes(data)
            self.assertIsNone(voice._cached_audio(self.text, Path(d)))

    def test_interrupted_after_audio_recovers_alignment_without_tts(self):
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ, {}, clear=True):
            expected = self.seed(d)
            voice._save_voice_cache(self.text, Path(d))
            with patch.object(voice, "align", return_value=expected) as align:
                _, timed = voice.synthesize(self.text, d)
            align.assert_called_once()
            self.assertEqual(expected, timed)

    def test_missing_asr_is_explicit_not_silent_success(self):
        with tempfile.TemporaryDirectory() as d:
            self.seed(d)
            with patch.dict(sys.modules, {"faster_whisper": None}):
                timed = voice.align(voice.sentences(self.text), Path(d) / "VOCE.wav", 1.0)
            report = json.loads((Path(d) / "ALLINEAMENTO_VOCE.json").read_text())
            self.assertEqual(report["method"], "estimated")
            self.assertTrue(report["requires_sync_review"])
            self.assertAlmostEqual(timed[-1][2], 1.0)

    def test_new_voice_is_blocked_before_google_when_finale_is_a_template(self):
        stock = ("Il dipinto mostra molti mostri e figure.\n\n"
                 "E il quadro ci lascia una domanda: che cosa c'è dentro di noi?")
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ, {"GEMINI_API_KEY": "DO_NOT_USE_REAL_KEY"}):
            with self.assertRaisesRegex(RuntimeError, "EDITORIAL_V320_REVISION_REQUIRED"):
                voice.synthesize(stock, d)
            report = json.loads((Path(d) / "EDITORIAL_NATURALNESS_V320.json").read_text())
            self.assertEqual(report["status"], "revision_required")
            self.assertFalse((Path(d) / "VOCE.wav").exists())
            self.assertEqual(report["new_tts_calls"], 0)

    def test_legacy_verified_voice_cache_bypasses_new_preflight(self):
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ, {}, clear=True):
            self.seed(d)
            with patch.object(voice, "_human_tone_pre_tts",
                              side_effect=AssertionError("Do not recheck existing verified WAV")):
                data, timing = voice.synthesize(self.text, d)
            self.assertEqual(len(data), 24000)
            self.assertTrue(timing)
            self.assertFalse((Path(d) / "EDITORIAL_NATURALNESS_V320.json").exists())

    def test_invalid_or_missing_manifest_never_adopts_unknown_audio(self):
        with tempfile.TemporaryDirectory() as d:
            self.seed(d)
            (Path(d) / "VOICE_CACHE_V13.json").write_text("{}")
            self.assertIsNone(voice._cached_audio(self.text, Path(d)))


if __name__ == "__main__":
    unittest.main()
