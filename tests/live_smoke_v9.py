#!/usr/bin/env python3
"""Public GitHub Pages availability + asset smoke test. Read-only, stdlib only."""
import argparse
import json
import ssl
import time
import urllib.error
import urllib.request
from urllib.parse import urljoin

DEFAULT_URL = "https://ggianlucaa.github.io/Tra-le-pagine-/"
CHECKS = {
    "index.html": (b"<title>Tra le Pagine", "text/html"),
    "app.js": (b"Tra le Pagine V9", "javascript"),
    "styles.css": (b":root", "text/css"),
    "manifest.webmanifest": (b"Tra le Pagine", "json"),
    "icon.svg": (b"<svg", "image/svg+xml"),
    "sw.js": (b"tra-le-pagine-v9", "javascript"),
}
HEADERS = {
    "User-Agent": "TraLePagine-PublicSmoke/1.0 (GitHub Actions)",
    "Accept": "*/*",
}


def check(url, needle, content_type, retries=3):
    error = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15, context=ssl.create_default_context()) as response:
                payload = response.read(2_000_000)
                typ = response.headers.get("Content-Type", "").lower()
                if response.status != 200:
                    raise ValueError("HTTP " + str(response.status))
                if content_type not in typ and not (
                    content_type == "javascript" and ("text/plain" in typ or "text/javascript" in typ)
                ):
                    raise ValueError("content-type inaspettato: " + typ)
                if needle not in payload:
                    raise ValueError("Contenuto V9 non trovato (possibile 404/HTML vecchio)")
                return {"url": url, "status": 200, "size": len(payload), "content_type": typ}
        except Exception as e:
            error = str(e)
            if i < retries - 1:
                time.sleep(4)
    raise RuntimeError(url + ": " + str(error))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--url", default=DEFAULT_URL)
    p.add_argument("--report", default="site_diagnostics.json")
    args = p.parse_args()
    root = args.url.rstrip("/") + "/"
    if not root.startswith("https://"):
        raise ValueError("Usare solo HTTPS.")
    print("TARGET:", root, flush=True)
    checks = []
    for name, (needle, typ) in CHECKS.items():
        full = urljoin(root, name)
        try:
            result = check(full, needle, typ)
            checks.append({"file":name, "ok":True, **result})
            print("OK", name, result["status"], result["size"], flush=True)
        except Exception as e:
            checks.append({"file":name, "ok":False,"reason":str(e)})
            print("FAIL", name, str(e), flush=True)
            # Fail quickly on index not being available.
            if name == "index.html":
                break
    report = {"url": root, "checks": checks, "success":len(checks)==len(CHECKS) and all(i["ok"] for i in checks)}
    with open(args.report, "w", encoding="utf-8") as f:
        json.dump(report,f,indent=2,ensure_ascii=False)
    if not report["success"]:
        raise SystemExit("SITO NON ANCORA CONFERMATO LIVE: guarda gli errori e GitHub Pages.")
    print("SITO V9 CONFERMATO LIVE: tutti i file essenziali rispondono via HTTPS.")


if __name__ == "__main__":
    main()
