"""Offline regression: only the verified Met 400112 IIIF image may be used as fallback."""
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import engine


class MetIiifFallbackTests(unittest.TestCase):
    def record(self):
        return {
            "objectID": 400112,
            "title": "A Moth",
            "objectName": "Drawing",
            "isPublicDomain": True,
            "primaryImage": "https://images.metmuseum.org/CRDImages/dp/original/DP820071.jpg",
        }

    def test_fallback_uses_exact_official_iiif_when_original_fails(self):
        image = Image.new("RGB", (900, 900), (242, 239, 223))
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        payload = buffer.getvalue()
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(engine, "get_bytes",
                              side_effect=[RuntimeError("image host unavailable"), payload]) as fetch:
                result, url, digest = engine.save_original(
                    self.record(), Path(folder),
                    {"min_image_width": 850, "min_image_height": 600})
            self.assertEqual(result.size, (900, 900))
            self.assertEqual(
                url,
                "https://collectionapi.metmuseum.org/api/collection/v1/iiif/400112/770372/main-image")
            self.assertEqual(fetch.call_count, 2)
            self.assertEqual((Path(folder) / "SOURCE_MET_ORIGINAL.jpg").read_bytes(), payload)
            self.assertEqual(len(digest), 64)

    def test_non_public_domain_never_downloaded(self):
        record = self.record()
        record["isPublicDomain"] = False
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(engine, "get_bytes") as fetch:
                with self.assertRaisesRegex(RuntimeError, "SOURCE_RIGHTS_UNVERIFIED"):
                    engine.save_original(record, Path(folder), {})
                fetch.assert_not_called()

    def test_unverified_object_id_never_gets_moth_fallback(self):
        record = self.record()
        record["objectID"] = 400116
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(engine, "get_bytes", side_effect=RuntimeError("offline")) as fetch:
                with self.assertRaisesRegex(RuntimeError, "source acquisition unavailable"):
                    engine.save_original(record, Path(folder),
                                         {"min_image_width": 850, "min_image_height": 600})
                self.assertEqual(fetch.call_count, 1)


if __name__ == "__main__":
    unittest.main()
