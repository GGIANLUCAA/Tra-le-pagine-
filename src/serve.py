#!/usr/bin/env python3
"""Static file server with HTTP/1.1 keep-alive and Range support.

Python's built-in http.server speaks HTTP/1.0 and ignores Range requests,
which makes large video downloads fail through some proxies. This adds:
  - HTTP/1.1 (keep-alive)
  - byte-range requests (206 Partial Content) for seeking / resumable downloads

Usage: serve.py [port] [directory]
"""
import os, re, sys, gzip, io
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from shutil import copyfileobj

RANGE_RE = re.compile(r"bytes=(\d*)-(\d*)")
TEXT_EXT = (".html", ".js", ".css", ".json", ".svg", ".txt", ".webmanifest", ".md")
GZIP_MIN = 1024  # only gzip text files above this size


class _LimitedReader:
    """Wrap a file object so copyfileobj stops after `length` bytes."""

    def __init__(self, f, length):
        self.f, self.left = f, length

    def read(self, n=-1):
        if self.left <= 0:
            return b""
        if n is None or n < 0:
            n = self.left
        data = self.f.read(min(n, self.left))
        self.left -= len(data)
        return data

    def close(self):
        self.f.close()


class RangeHandler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def end_headers(self):
        if not any(b"Accept-Ranges" in h for h in self._headers_buffer):
            self.send_header("Accept-Ranges", "bytes")
        path = self.translate_path(self.path).lower()
        if path.endswith((".html", "/")):
            self.send_header("Cache-Control", "no-cache")
        else:
            self.send_header("Cache-Control", "public, max-age=604800")
        super().end_headers()

    def send_head(self):
        rng = self.headers.get("Range")
        if not rng:
            return super().send_head()

        path = self.translate_path(self.path)
        if os.path.isdir(path):
            return super().send_head()
        try:
            f = open(path, "rb")
        except OSError:
            self.send_error(404, "File not found")
            return None

        fs = os.fstat(f.fileno())
        size = fs.st_size
        m = RANGE_RE.match(rng)
        if not m:
            f.close()
            return super().send_head()
        start = int(m.group(1)) if m.group(1) else 0
        end = int(m.group(2)) if m.group(2) else size - 1
        if start > end or start >= size:
            f.close()
            self.send_error(416, "Requested Range Not Satisfiable")
            return None
        end = min(end, size - 1)
        length = end - start + 1

        self.send_response(206)
        self.send_header("Content-type", self.guess_type(path))
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(length))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        f.seek(start)
        return _LimitedReader(f, length)

    def do_GET(self):
        if self._try_gzip():
            return
        f = self.send_head()
        if f:
            try:
                copyfileobj(f, self.wfile)
            except (BrokenPipeError, ConnectionResetError):
                pass  # client closed early (normal for video preload)
            finally:
                f.close()

    def _try_gzip(self):
        """Serve a gzipped copy of large text files when the client supports it."""
        if self.headers.get("Range") or "gzip" not in self.headers.get("Accept-Encoding", ""):
            return False
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            path = os.path.join(path, "index.html")
        if not (os.path.isfile(path) and path.lower().endswith(TEXT_EXT)):
            return False
        try:
            raw = open(path, "rb").read()
        except OSError:
            return False
        if len(raw) < GZIP_MIN:
            return False
        body = gzip.compress(raw, 6)
        self.send_response(200)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Encoding", "gzip")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Vary", "Accept-Encoding")
        self.send_header("Last-Modified", self.date_time_string(os.stat(path).st_mtime))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)
        return True

    def handle_error(self, request, client_address):
        pass  # keep the log clean; disconnects are expected


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8082
    directory = sys.argv[2] if len(sys.argv) > 2 else "/workspace/output"
    handler = partial(RangeHandler, directory=directory)
    httpd = ThreadingHTTPServer(("0.0.0.0", port), handler)
    print(f"serving {directory} on http://0.0.0.0:{port}/ (HTTP/1.1 + Range)", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
