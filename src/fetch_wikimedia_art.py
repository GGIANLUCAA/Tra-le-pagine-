#!/usr/bin/env python3
"""Fetch public-domain artwork images from Wikimedia Commons.

Searches Commons for each work and downloads the highest-resolution public
domain candidate (preferring "Google Art Project" scans when available) at up
to 2600 px on the long side. Used to (re)build the local image set for the
social reel renderer.

Usage: fetch_wikimedia_art.py
"""
import json, subprocess, urllib.parse
from pathlib import Path

OUT = Path("/tmp/vangogh")
OUT.mkdir(parents=True, exist_ok=True)

# output filename -> Commons search query
WORKS = {
    "Starry_Night.jpg": "Vincent van Gogh Starry Night",
    "Wheatfield_Cypresses.jpg": "Vincent van Gogh Wheat Field with Cypresses",
    "Sunflowers.jpg": "Vincent van Gogh Sunflowers",
    "Irises.jpg": "Vincent van Gogh Irises",
    "Almond_Blossoms.jpg": "Vincent van Gogh Almond Blossom",
    "The_Sower.jpg": "Vincent van Gogh The Sower",
    "Cafe_Terras.jpg": "Vincent van Gogh Cafe Terrace at Night",
    "Yellow_House.jpg": "Vincent van Gogh The Yellow House",
    "Bedroom_Arles.jpg": "Vincent van Gogh The Bedroom",
    "Potato_Eaters.jpg": "Vincent van Gogh The Potato Eaters",
    "Self_Portrait.jpg": "Vincent van Gogh Self-Portrait 1889",
    "Wheatfield_Crows.jpg": "Vincent van Gogh Wheatfield with Crows",
}

API = "https://commons.wikimedia.org/w/api.php"


def _get(url):
    return subprocess.run(["curl", "-s", "--max-time", "40", url],
                          capture_output=True, text=True, check=True).stdout


def search(query, limit=6):
    params = {
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": f"File: {query}", "gsrlimit": str(limit),
        "prop": "imageinfo", "iiprop": "url|size|mime",
        "iiurlwidth": "2600",
    }
    data = json.loads(_get(f"{API}?{urllib.parse.urlencode(params)}"))
    pages = (data.get("query") or {}).get("pages") or {}
    out = []
    for p in pages.values():
        ii = (p.get("imageinfo") or [{}])[0]
        if not ii.get("url") or ii.get("mime") not in ("image/jpeg", "image/png"):
            continue
        out.append({
            "title": p["title"],
            "width": ii.get("width", 0),
            "height": ii.get("height", 0),
            "url": ii.get("thumburl") or ii["url"],
        })
    return out


def pick(cands):
    # prefer high-res Google Art Project scans, else the widest image
    gap = [c for c in cands if "google art project" in c["title"].lower() and c["width"] >= 1500]
    pool = gap or cands
    return max(pool, key=lambda c: c["width"] * c["height"], default=None)


def main():
    for fn, query in WORKS.items():
        cands = [c for c in search(query) if c["width"] >= 1000]
        c = pick(cands)
        if not c:
            print(f"MISS {fn}: no candidate for '{query}'")
            continue
        dst = OUT / fn
        subprocess.run(["curl", "-s", "-L", "--max-time", "120", "-o", str(dst), c["url"]], check=True)
        print(f"OK   {fn:26s} {c['width']}x{c['height']}  {c['title']}")


if __name__ == "__main__":
    main()
