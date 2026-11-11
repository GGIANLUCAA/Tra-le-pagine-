"""V186: offline tests and real synthetic 720p MP4 sampling; no Wikimedia download."""
import hashlib
from io import BytesIO
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import storia_rivive_v186_commons_preview as v186


class Response(BytesIO):
    def __init__(self, value, url, length=None):
        super().__init__(value)
        self._url = url
        self.headers = {} if length is None else {"Content-Length": str(length)}
    def geturl(self):
        return self._url


class V186Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.url = "https://upload.wikimedia.org/wikipedia/commons/transcoded/test.webm"

    def test_select_full_hd_derivative_not_sd_or_external(self):
        result = v186.select_1080_derivative([
            {"src": "https://evil.example/hd.webm", "width": 1920, "height": 1080},
            {"src": self.url, "width": 1280, "height": 963},
            {"src": "https://upload.wikimedia.org/low.webm", "width": 854, "height": 480},
        ])
        self.assertEqual(result["url"], self.url)
        self.assertIn("DERIVATIVE", result["kind"])

    def test_no_hd_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "NO_TRUSTED_HD"):
            v186.select_1080_derivative([{"src": self.url, "width": 480, "height": 360}])

    def test_discovery_reads_real_derivative_metadata_shape(self):
        payload = {"query": {"pages": {"123": {"videoinfo": [
            {"derivatives": [{"src": self.url, "width": 1280, "height": 963}]}]}}}}
        def fake(req, timeout):
            self.assertIn("commons.wikimedia.org", req.full_url)
            return Response(json.dumps(payload).encode(), req.full_url)
        self.assertEqual(v186.discover_derivative(fake)["url"], self.url)

    def test_download_stream_sha_and_no_overwrite(self):
        data = b"video-test" * 100
        def fake(req, timeout):
            return Response(data, self.url, len(data))
        target = self.root / "video.webm"
        info = v186.bounded_download(self.url, target, opener=fake, max_bytes=2048)
        self.assertEqual(info["sha256"], hashlib.sha256(data).hexdigest())
        self.assertEqual(target.read_bytes(), data)
        with self.assertRaisesRegex(ValueError, "DESTINATION_EXISTS"):
            v186.bounded_download(self.url, target, opener=fake, max_bytes=2048)

    def test_download_oversize_before_write(self):
        target = self.root / "oversize.webm"
        def fake(req, timeout):
            return Response(b"payload", self.url, length=99999)
        with self.assertRaisesRegex(ValueError, "DOWNLOAD_LIMIT"):
            v186.bounded_download(self.url, target, opener=fake, max_bytes=4)
        self.assertFalse(target.exists())
        self.assertFalse((self.root / "oversize.webm.part").exists())

    def test_redirect_to_external_blocked(self):
        target = self.root / "bad.webm"
        def fake(req, timeout):
            return Response(b"payload", "https://evil.example/other.webm")
        with self.assertRaisesRegex(ValueError, "UNTRUSTED_MEDIA_REDIRECT"):
            v186.bounded_download(self.url, target, opener=fake)
        self.assertFalse(target.exists())

    def test_rejects_external_direct_url(self):
        with self.assertRaisesRegex(ValueError, "UNTRUSTED_MEDIA_URL"):
            v186.bounded_download("https://example.org/a.webm", self.root / "a.webm")

    def test_full_sample_on_synthetic_real_encoded_video_bytes(self):
        clips = []
        for index, color in enumerate(["red", "green", "blue", "yellow", "magenta"]):
            output = self.root / ("clip" + str(index) + ".mp4")
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y",
                            "-f", "lavfi", "-i", "color=c=" + color + ":s=1280x720:r=1",
                            "-t", "8", "-c:v", "libx264", "-preset", "ultrafast",
                            "-pix_fmt", "yuv420p", str(output)],
                           check=True, timeout=80)
            clips.append(output)
        listing = self.root / "concat.txt"
        listing.write_text("".join("file '" + str(c) + "'\n" for c in clips))
        movie = self.root / "synthetic.mp4"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat",
                        "-safe", "0", "-i", str(listing), "-c", "copy", str(movie)],
                       check=True, timeout=80)
        sha = hashlib.sha256(movie.read_bytes()).hexdigest()
        result = v186.sample_five(movie, sha, self.root / "five")
        self.assertEqual(len(result["previews"]), 5)
        self.assertEqual(len({p["sha256"] for p in result["previews"]}), 5)
        for preview in result["previews"]:
            file = self.root / "five" / preview["filename"]
            self.assertTrue(file.exists())
            self.assertEqual(hashlib.sha256(file.read_bytes()).hexdigest(), preview["sha256"])


if __name__ == "__main__":
    unittest.main()
