#!/usr/bin/env python3
"""Acquisizione e tavola provini da Wikimedia Commons. SOLO file con CC0 dichiarata.
Nessuna generazione AI, spesa, video finale, voce o pubblicazione.
"""
import argparse
import hashlib
import json
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path

ENDPOINT = "https://commons.wikimedia.org/w/api.php"
UA = "TraLePagineStoriaRivive/0.1 (https://github.com/GGIANLUCAA/Tra-le-pagine-)"
PRESETS = {"beirut1919": "File:Scènes de rue - AI13347.webm"}


def request(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60)


def fetch_cc0(filename, output):
    query = urllib.parse.urlencode({
        "action": "query", "format": "json", "formatversion": "2",
        "prop": "imageinfo", "titles": filename,
        "iiprop": "url|size|mime|extmetadata",
        "iiextmetadatafilter": "LicenseShortName|LicenseUrl|Artist|ImageDescription"
    })
    with request(ENDPOINT + "?" + query) as res:
        data = json.load(res)
    pages = data.get("query", {}).get("pages", [])
    if not pages or pages[0].get("missing") or not pages[0].get("imageinfo"):
        raise ValueError("Sorgente mancante: non scaricare copie casuali")
    info = pages[0]["imageinfo"][0]
    meta = info.get("extmetadata", {})
    get = lambda key: (meta.get(key) or {}).get("value", "")
    lic, url = get("LicenseShortName"), get("LicenseUrl")
    if not ("cc0" in lic.lower().replace(" ", "") or "publicdomain/zero/" in url.lower()):
        raise ValueError("Solo CC0 ammessa nel downloader automatico: licenza " + lic)
    if not info.get("mime", "").startswith("video/"):
        raise ValueError("La fonte non e' un video")
    if info.get("size", 0) > 100 * 1024 * 1024:
        raise ValueError("File >100MB: richiede selezione manuale per evitare sprechi")
    output.mkdir(parents=True, exist_ok=True)
    target = output / "FONTE_ORIGINALE.webm"
    h = hashlib.sha256()
    count = 0
    with request(info["url"]) as src, target.open("wb") as dst:
        while True:
            chunk = src.read(1024 * 1024)
            if not chunk:
                break
            count += len(chunk)
            if count > 100 * 1024 * 1024:
                target.unlink(missing_ok=True)
                raise ValueError("File supera 100MB")
            h.update(chunk)
            dst.write(chunk)
    record = {
        "source_title": filename, "source_page": info.get("descriptionurl"),
        "archive_description": get("ImageDescription"), "artist": get("Artist"),
        "license": lic, "license_url": url, "source_file": target.name,
        "source_sha256": h.hexdigest(), "download_size_bytes": count,
        "rights_status": "CC0_on_Commons_page__additional_rights_and_historical_content_unreviewed",
        "status": "SOURCE_ACQUIRED_NOT_AN_APPROVED_VIDEO"
    }
    (output / "FONTE.json").write_text(json.dumps(record, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    return target, record


def make_contact(file, output):
    command = ["ffmpeg","-nostdin","-y","-hide_banner","-loglevel","error",
               "-i",str(file),"-vf","fps=1/18,scale=400:-2,tile=3x3",
               "-frames:v","1",str(output / "PROVINI_ORIGINALE.jpg")]
    subprocess.run(command, check=True, timeout=180)
    probe = subprocess.run(["ffprobe","-v","error","-show_streams","-show_format",
                            "-of","json",str(file)], capture_output=True, text=True, check=True)
    (output / "TECNICA_ORIGINALE.json").write_text(
        json.dumps(json.loads(probe.stdout), ensure_ascii=False, indent=2)+"\n",encoding="utf-8")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--preset",choices=tuple(PRESETS),default="beirut1919")
    p.add_argument("--out",type=Path,default=Path("output/storia_rivive"))
    args = p.parse_args()
    target, meta = fetch_cc0(PRESETS[args.preset], args.out)
    make_contact(target, args.out)
    print("SOURCE ACQUIRED. Only source and contact sheet exist, NOT a finished video.")
    print(meta["source_sha256"])


if __name__ == "__main__":
    main()
