"""V173 tests: no false native-HD, no unsafe archive URLs, no paid media."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

FILE = Path(__file__).resolve().parents[1] / "src" / "storia_rivive_v173_fashion1917_source_scout.py"
spec = importlib.util.spec_from_file_location("storia_v173", FILE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class V173ArchiveTests(unittest.TestCase):
    def test_exact_archival_license_only(self):
        self.assertTrue(m.public_domain_label({"licenseurl": "http://creativecommons.org/licenses/publicdomain/"}))
        self.assertFalse(m.public_domain_label({"licenseurl": "https://creativecommons.org/licenses/by/4.0/"}))
        self.assertFalse(m.public_domain_label({}))
        self.assertFalse(m.public_domain_label({"licenseurl": "http://creativecommons.org/licenses/publicdomain/anything"}))

    def test_refuse_urls_slashes_traversal_images(self):
        for value in ("../evil.mp4", "/etc/passwd", "evil.mp4?query=1", "image.jpg", "x;touch.mp4", "bad\\back.mp4", ".bad.mp4"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                m.safe_filename(value)
        self.assertEqual(m.safe_filename("Modes of the Moment 1917.ogv"), "Modes of the Moment 1917.ogv")

    def test_bounded_selection_does_not_claim_resolution(self):
        files = [
            {"name": "small.mp4", "size": "1000", "source": "derivative", "format": "MPEG4"},
            {"name": "source.mpg", "size": "32000000", "source": "original", "format": "MPEG2"},
            {"name": "huge.mov", "size": str(m.MAX_BYTES + 1), "source": "original", "format": "ProRes"},
            {"name": "not_a_video.jpg", "size": "100", "source": "original", "format": "JPEG"},
        ]
        candidates = m.candidate_files(files)
        self.assertEqual(len(candidates), 3)
        selected = m.choose_bounded(candidates)
        self.assertEqual(selected["name"], "source.mpg")
        self.assertNotIn("resolution", selected)
        self.assertFalse(candidates[0]["under_160mib_cap"])

    def test_no_licensed_media_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            fake = {"metadata": {"identifier": "Modesoft1917", "licenseurl": ""}, "files": [
                {"name": "valid.mp4", "size": "987654", "source": "original"}]}
            with patch.object(m, "get_metadata", return_value=fake), patch.object(m, "stream_original", side_effect=AssertionError("UNEXPECTED_DOWNLOAD")):
                result = m.run(Path(td), do_download=True)
                self.assertEqual(result["status"], "BLOCKED_EXACT_ARCHIVE_PUBLIC_DOMAIN_MARK_MISSING")
                self.assertEqual(result["paid_calls"], 0)
                self.assertFalse(result["licensed_for_italian_publication"])

    def test_metadata_only_cannot_be_called_native_hd(self):
        with tempfile.TemporaryDirectory() as td:
            fake = {"metadata": {"identifier": "Modesoft1917", "licenseurl": "http://creativecommons.org/licenses/publicdomain/"}, "files": [
                {"name": "original.mpg", "size": "2000000", "source": "original", "format": "MPEG2"}]}
            with patch.object(m, "get_metadata", return_value=fake):
                result = m.run(Path(td), do_download=False)
                self.assertEqual(result["status"], "METADATA_ONLY_REAL_RASTER_UNVERIFIED")
                self.assertNotIn("actual_ffprobe", result)
                self.assertFalse(result["no_new_video_master_claimed"] is False)
                self.assertTrue((Path(td)/"V173_FASHION_SOURCE_QUALITY_AUDIT.json").is_file())

    def test_all_high_size_blocks_cost_free(self):
        with tempfile.TemporaryDirectory() as td:
            fake = {"metadata": {"identifier": "Modesoft1917", "licenseurl": "http://creativecommons.org/licenses/publicdomain/"}, "files": [
                {"name": "huge.mpg", "size": str(m.MAX_BYTES + 1), "source": "original"}]}
            with patch.object(m, "get_metadata", return_value=fake):
                result=m.run(Path(td),do_download=True)
                self.assertEqual(result["status"], "BLOCKED_NO_VIDEO_UNDER_160MIB_NO_DOWNLOAD")


if __name__ == "__main__":
    unittest.main()
