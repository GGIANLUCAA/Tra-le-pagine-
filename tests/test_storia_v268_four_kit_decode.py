"""Offline regression for the real-byte V268 inventory, no provider calls."""
import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch
from subprocess import CompletedProcess

SCRIPT = Path(__file__).resolve().parents[1] / "tools/storia_v267_four_kit_byte_inventory.py"
spec = importlib.util.spec_from_file_location("storia_inventory", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class FourKitInventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.ids = ["one", "two", "three", "four"]
        for episode in self.ids:
            folder = self.root / episode
            folder.mkdir()
            mp4 = folder / (episode + ".mp4")
            mp4.write_bytes(b"dummy MP4 for mocked probe")
            with zipfile.ZipFile(folder / (episode + ".zip"), "w") as z:
                z.write(mp4, mp4.name)
                for name in ("cover.png", "social_posts.json", "qa_report.json"):
                    z.writestr(name, "{}")

    def run_inventory(self, streams, decode_return=0):
        def fake_run(cmd, **kwargs):
            if cmd[0] == "ffprobe":
                return CompletedProcess(cmd, 0, stdout=json.dumps({
                    "format": {"duration": "25.0"}, "streams": streams
                }))
            if cmd[0] == "ffmpeg":
                return CompletedProcess(cmd, decode_return)
            raise AssertionError(cmd)
        with patch.object(module.subprocess, "run", side_effect=fake_run):
            return module.inspect(self.root, self.ids)

    def test_h264_aac_decode_success_is_technical_only(self):
        result = self.run_inventory([
            {"codec_type": "video", "codec_name": "h264"},
            {"codec_type": "audio", "codec_name": "aac"},
        ])
        self.assertEqual(result["technical_kits_present"], 4)
        self.assertEqual(result["final_approved_count"], 0)

    def test_missing_audio_fails(self):
        result = self.run_inventory([{"codec_type": "video", "codec_name": "h264"}])
        self.assertEqual(result["technical_kits_present"], 0)
        self.assertIn("missing_aac_audio", result["episodes"][0]["errors"])

    def test_decode_error_fails(self):
        result = self.run_inventory([
            {"codec_type": "video", "codec_name": "h264"},
            {"codec_type": "audio", "codec_name": "aac"},
        ], decode_return=1)
        self.assertEqual(result["technical_kits_present"], 0)
        self.assertIn("mp4_full_decode_failed", result["episodes"][0]["errors"])

    def test_missing_real_kits_fails(self):
        for episode in self.ids:
            (self.root / episode / (episode + ".mp4")).unlink()
        result = module.inspect(self.root, self.ids)
        self.assertEqual(result["technical_kits_present"], 0)


if __name__ == "__main__":
    unittest.main()
