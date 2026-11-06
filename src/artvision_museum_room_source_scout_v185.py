#!/usr/bin/env python3
"""Read-only Commons source scout for five pending ArtVision Museum works.

Collects candidate metadata; NEVER approves a room, frame, license or video.
Run: python src/artvision_museum_room_source_scout_v185.py --out /tmp/artvision_room_candidates.json
No paid APIs, rendering, publishing or mutation of masters.
"""
import argparse
import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone

API = "https://commons.wikimedia.org/w/api.php"
WORKS = {
    "rebel_angels": ["The Fall of the Rebel Angels Bruegel museum", "Chute des anges rebelles musée cadre"],
    "garden_of_death": ["Hugo Simberg Garden of Death Ateneum framed", "Kuoleman puutarha Ateneum kehys"],
    "triumph_of_death": ["Triumph of Death Bruegel Prado room", "Triunfo de la Muerte Bruegel sala Prado"],
    "magic_circle": ["John William Waterhouse Magic Circle Tate frame", "The Magic Circle Waterhouse gallery"],
    "ghost_of_a_flea": ["William Blake Ghost of a Flea Tate frame", "Ghost of a Flea gallery framed"],
}

def api(params):
    url = API + "?" + urllib.parse.urlencode({"format": "json", "formatversion": 2, **params})
    req = urllib.request.Request(url, headers={"User-Agent": "ArtVisionSourceScout/1.0 (source metadata review; no bulk download)"})
    with urllib.request.urlopen(req, timeout=25) as response:
        return json.load(response)

def collect():
    result = {"generated_utc": datetime.now(timezone.utc).isoformat(), "status": "CANDIDATES_ONLY_NOT_LICENSE_OR_MUSEUM_APPROVED", "works": {}}
    for work, queries in WORKS.items():
        candidates = {}
        for query in queries:
            try:
                data = api({"action": "query", "generator": "search", "gsrsearch": query, "gsrnamespace": 6, "gsrlimit": 15,
                            "prop": "imageinfo", "iiprop": "url|size|mime|sha1|extmetadata", "iiextmetadatafilter": "LicenseShortName|LicenseUrl|Artist|DateTimeOriginal|Credit"})
                for page in data.get("query", {}).get("pages", []):
                    infos = page.get("imageinfo", [])
                    if not infos:
                        continue
                    info = infos[0]
                    title = page["title"]
                    metadata = info.get("extmetadata", {})
                    candidates[title] = {
                        "commons_page": info.get("descriptionurl"),
                        "original_url": info.get("url"),
                        "width": info.get("width"), "height": info.get("height"),
                        "mime": info.get("mime"), "sha1_commons": info.get("sha1"),
                        "license_label_unverified": metadata.get("LicenseShortName", {}).get("value"),
                        "license_url_unverified": metadata.get("LicenseUrl", {}).get("value"),
                        "query": query,
                        "gate": "REQUIRES_MANUAL_EXACT_WORK_FRAME_ROOM_SCALE_AND_RIGHTS_REVIEW",
                    }
            except (OSError, ValueError) as exc:
                result.setdefault("errors", []).append({"work": work, "query": query, "error": str(exc)})
        result["works"][work] = list(candidates.values())
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(collect(), handle, ensure_ascii=False, indent=2)
    print(args.out)
