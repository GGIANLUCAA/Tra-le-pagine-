import hashlib
import io
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from studio_integrity_v9 import (audit_master, sha_file, valid_master, verify_zip,
                                 MAX_MEDIA_BYTES)

BODY = b"mocked-real-video-bytes" * 100
SHA = hashlib.sha256(BODY).hexdigest()


class MemoryResponse:
    def __init__(self, status, headers, body):
        self.status = status
        self.headers = headers
        self.io = io.BytesIO(body)
    def read(self, size=-1):
        return self.io.read(size)
    def __enter__(self):
        return self
    def __exit__(self, *args):
        self.io.close()


class MemoryOpener:
    def __init__(self, *, corrupt=False, wrong_range=False, redirect=False, extra=False):
        self.calls = []
        self.corrupt = corrupt
        self.wrong_range = wrong_range
        self.redirect = redirect
        self.extra = extra
    def open(self, request, timeout=None):
        self.calls.append(request)
        self.assert_request(request)
        body = BODY + (b"extra" if self.extra else b"")
        if len(self.calls) == 1:
            headers = {
                "Content-Range": f"bytes 0-1023/{len(BODY)+1 if self.wrong_range else len(BODY)}",
                "Content-Length": "1024", "Content-Type": "video/mp4",
                "Content-Disposition": "attachment; filename=VIDEO.mp4"
            }
            return MemoryResponse(206 if not self.redirect else 302,
                                  headers, BODY[:1024])
        headers = {
            "Content-Type": "video/mp4",
            "Content-Disposition": "attachment; filename=VIDEO.mp4",
            "Content-Length": str(len(body))
        }
        if self.corrupt:
            body = bytes([body[0] ^ 1]) + body[1:]
        return MemoryResponse(200, headers, body)
    def assert_request(self, request):
        assert request.get_method() == "GET"
        assert request.full_url.startswith(
            "https://video-library-studio.600led.workers.dev/download/")
        assert request.get_header("User-agent").startswith("Mozilla/5.0")


def row():
    return {"name": "VIDEO.mp4", "bytes": len(BODY), "sha256": SHA,
            "work": "Fixture", "slot": "critico_standard_v1"}


class IntegrityTests(unittest.TestCase):
    def test_exact_bytes_sha_and_range(self):
        opener = MemoryOpener()
        r = audit_master(row(), opener)
        self.assertTrue(r["mp4_full_download_verified"])
        self.assertTrue(r["range_verified"])
        self.assertTrue(r["bytes_verified"])
        self.assertTrue(r["sha256_verified"])
        self.assertEqual(r["actual_bytes"], len(BODY))
        self.assertEqual(len(opener.calls), 2)
        self.assertEqual(opener.calls[0].get_header("Range"), "bytes=0-1023")
        self.assertFalse(r["owner_approved"])
        self.assertFalse(r["publish_authorized"])
        self.assertFalse(r["zip_verified"])

    def test_wrong_range_fails_without_full_download(self):
        opener = MemoryOpener(wrong_range=True)
        x = audit_master(row(), opener)
        self.assertFalse(x["mp4_full_download_verified"])
        self.assertEqual(x["failure"], "RANGE_RESPONSE_UNEXPECTED")
        self.assertEqual(len(opener.calls), 1)

    def test_sha_mismatch_is_not_master(self):
        x = audit_master(row(), MemoryOpener(corrupt=True))
        self.assertTrue(x["bytes_verified"])
        self.assertFalse(x["sha256_verified"])
        self.assertEqual(x["failure"], "INCOMPLETE_OR_DIFFERENT_MASTER")

    def test_overlong_download_never_passes(self):
        x = audit_master(row(), MemoryOpener(extra=True))
        self.assertFalse(x["mp4_full_download_verified"])
        self.assertEqual(x["failure"], "DOWNLOAD_CONTENT_LENGTH_MISMATCH")

    def test_redirect_is_rejected(self):
        x = audit_master(row(), MemoryOpener(redirect=True))
        self.assertEqual(x["failure"], "RANGE_RESPONSE_UNEXPECTED")

    def test_filename_and_sha_constrained(self):
        for changes in ({"name": "../VIDEO.mp4"}, {"name": "a/b.mp4"},
                        {"bytes": True}, {"bytes": MAX_MEDIA_BYTES+1},
                        {"sha256": "not-sha"}):
            y = row()
            y.update(changes)
            with self.assertRaises(ValueError):
                valid_master(y)

    def make_zip(self, path, *, include_social=True, traversal=False):
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr("PACCHETTO/01_VIDEO/VIDEO.mp4", BODY)
            z.writestr("PACCHETTO/02_COPERTINA/COPERTINA.jpg", b"jpeg")
            z.writestr("PACCHETTO/04_FONTI_E_RICETTA/FONTI_E_DIRITTI.txt", b"source")
            if include_social:
                for social in ("FACEBOOK", "INSTAGRAM", "TIKTOK", "YOUTUBE"):
                    z.writestr("PACCHETTO/03_POST_SOCIAL/POST_"+social+".txt", b"text")
            if traversal:
                z.writestr("../outside.txt", b"unsafe")

    def test_real_zip_crc_sha_structure_and_no_approval(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "package.zip"
            self.make_zip(path)
            r = verify_zip(path, sha_file(path))
            self.assertTrue(r["zip_full_read_verified"])
            self.assertTrue(r["zip_crc_verified"])
            self.assertTrue(r["zip_contents_complete"])
            self.assertFalse(r["owner_approved"])
            self.assertFalse(r["publish_authorized"])

    def test_zip_missing_post_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "package.zip"
            self.make_zip(path, include_social=False)
            r = verify_zip(path, sha_file(path))
            self.assertEqual(r["failure"], "ZIP_V55_DELIVERY_MISSING_COMPONENTS")

    def test_zip_path_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "package.zip"
            self.make_zip(path, traversal=True)
            r = verify_zip(path, sha_file(path))
            self.assertEqual(r["failure"], "ZIP_UNSAFE_MEMBER")

    def test_zip_wrong_sha_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "package.zip"
            self.make_zip(path)
            r = verify_zip(path, "f"*64)
            self.assertEqual(r["failure"], "ZIP_SHA256_MISMATCH")
            self.assertFalse(r["zip_full_read_verified"])

    def test_truncated_zip_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "package.zip"
            self.make_zip(path)
            raw = path.read_bytes()
            path.write_bytes(raw[:-10])
            r = verify_zip(path, sha_file(path))
            self.assertEqual(r["failure"], "ZIP_READ_ERROR")

if __name__ == "__main__":
    unittest.main()
