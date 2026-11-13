#!/usr/bin/env python3
"""Second artist-gallery production: three independent source-verified reviews.

Reuses first-five renderer without changing its validated script, files, or
prior Gold content. A new job is created per artist and never auto-published.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT / "scripts/artist_gallery_first_five_v1.py"
CONFIG = ROOT / "config/artist_gallery_next_three_20261113.json"
OUT = ROOT / "output/artist-gallery-next-three-20261113"

SEEDS = {
    "bocklin": [
      "Arnold Böcklin - Die Toteninsel III (Alte Nationalgalerie, Berlin).jpg",
      "Arnold Böcklin - Self-Portrait with Death as a Fiddler - WGA3033.jpg",
      "Böcklin - Selbstbildnis mit fiedelndem Tod, 1872, A I 633.jpg",
      "Arnold Böcklin - In der See (1883).jpg",
      "Böcklin - Die Toteninsel. 1883, NG 280.jpg",
      "Arnold Böcklin - The Isle of the Dead - WGA3029.jpg",
    ],
    "burne_jones": [
      "Edward coley burne-jones, the golden stairs, 1880.jpg",
      "Edward Burne-Jones (1833-1898) - The Tree of Forgiveness - LL 3635 - Lady Lever Art Gallery.jpg",
      "Edward Burne-Jones (1833-1898) - Laus Veneris - COMWG 560 - Watts Gallery.jpg",
      "Edward Burne-Jones (1833-1898) - Love and the Pilgrim - N05381 - National Gallery.jpg",
      "Edward Burne-Jones (1833-1898) - The Temple of Love - N03452 - National Gallery.jpg",
      "Edward Burne-Jones (1833-1898) - The Morning of the Resurrection - N04888 - National Gallery.jpg",
      "Edward Burne-Jones (1833-1898) - Stella Vespertina - O87 - William Morris Gallery.jpg",
      "Edward Burne-Jones (1833-1898) - Venus Concordia - PLYMG.1926.16 - The Box.jpg",
      "Edward Burne-Jones (1833-1898) - The Garden Court (from the Briar Rose series) - K928 - Bristol City Museum ^ Art Gallery.jpg",
      "The Heart of the Rose by Sir Edward Coley Burne-Jones, 1889.jpg",
    ],
    "von_stuck": [
      "Franz von Stuck - The Dance - Google Art Project.jpg",
      "Franz von Stuck - Dancing circle - M.Ob.2586 - National Museum in Warsaw.jpg",
      "Franz von Stuck - Die Wilde Jagd - G 1405 - Lenbachhaus.jpg",
      "Franz von Stuck - Faun and Nymph (Teasing) - O 15492 - National Gallery Prague.jpg",
      "Franz von Stuck - Mary Stuck, die Tochter des Künstlers - 7980 - Belvedere.jpg",
      "Franz von Stuck - Still Life with Poppies (15155228602).jpg",
      "Franz von Stuck Frühling c1900-1902.jpg",
      "Franz von Stuck Aschenbrödel 1899.jpg",
      "Franz von Stuck Eros mit Tamburin.jpg",
      "Franz von Stuck Forellenweiher 1890.jpg",
      "Salome, by Franz von Stuck.png",
      "Medea Franz von Stuck.jpg",
      "Haupt der Medusa by Franz von Stuck.jpg",
      "Herbstabend mit Reiter von Franz von Stuck.jpg",
    ],
}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--artist",required=True,choices=sorted(SEEDS))
    a=parser.parse_args()

    spec=importlib.util.spec_from_file_location("curated_gallery_renderer", PARENT)
    if spec is None or spec.loader is None:
        raise RuntimeError("Existing approved-gallery renderer is unavailable")
    m=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=m
    spec.loader.exec_module(m)
    m.SEEDS.update(SEEDS)

    cfg=json.loads(CONFIG.read_text(encoding="utf8"))
    profile=next(p for p in cfg["profiles"] if p["slug"]==a.artist)
    folder=OUT / a.artist
    folder.mkdir(parents=True,exist_ok=True)
    status={"artist":profile["artist"],"slug":a.artist,
            "format":"artist-gallery private review, not ArtVision 4x1",
            "published":False,"artistic_approval":False}
    try:
        works, errors=m.collect(profile,folder)
        outcome=m.make_gallery(profile,works,errors,folder)
        status.update(outcome)
    except Exception as exc:
        status.update({"status":"BLOCKED_NOT_RENDERED",
                       "reason":str(exc)[:800]})
        print("ARTIST_BLOCKED",a.artist,status["reason"],flush=True)
    (OUT/"SERIES_STATUS_"+a.artist+".json").write_text(
        json.dumps(status,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("ARTIST_RESULT",json.dumps(status,ensure_ascii=False),flush=True)
    return 0 if status["status"]=="TECHNICAL_PASS_ARTISTIC_PENDING" else 2

if __name__=="__main__":
    raise SystemExit(main())
