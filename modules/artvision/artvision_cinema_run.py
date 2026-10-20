#!/usr/bin/env python3
"""Run the new cinematic preset without changing the original ArtVision V1 module."""
from __future__ import annotations
import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from artvision import collect, download_pictures
from cinema_wow_v2 import make_video_cinematic

def main():
    ap=argparse.ArgumentParser(description="ArtVision V2: authentic art films with cinematic music-led editing")
    ap.add_argument("--artist", default="Vincent van Gogh")
    ap.add_argument("--duration", type=int, default=150)
    ap.add_argument("--max-works", type=int, default=16)
    ap.add_argument("--out", default="output/artvision")
    args=ap.parse_args()
    if not 18 <= args.duration <= 180:ap.error("duration 18-180 (social episodes 120-180)")
    if not 6 <= args.max_works <= 24:ap.error("max-works 6-24")
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    started=time.monotonic()
    records,errors=collect(args.artist)
    if len(records)<6:raise SystemExit(f"Not enough open-access works: {len(records)}. {errors}")
    art,failures=download_pictures(records,out/"immagini",args.max_works)
    if len(art)<6:raise SystemExit(f"Not enough valid high resolution downloads: {len(art)}. {failures[:5]}")
    manifest={"series":"ArtVision","style":"cinematic_wow","artist":args.artist,
       "created_utc":datetime.now(timezone.utc).isoformat(),
       "license_policy":"Museum-designated CC0/public domain imagery. Human check of applicable local laws and platform terms required.",
       "publication_approved":False,"works":art,"provider_errors":errors,"image_failures":failures}
    (out/"OPERE_FONTI_E_DIRITTI.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    (out/"CREDITI_E_FONTI.txt").write_text("\n".join(
       f"{p['title']} ({p['year']}) — {p['artist']} | {p['source']} | {p['license']} | {p['url']}" for p in art
    )+"\n",encoding="utf-8")
    (out/"DESCRIZIONE_SOCIAL.txt").write_text(
      f"{args.artist} — l'arte in movimento. Un film musicale fra opere autentiche.\n"
      "Fonti e condizioni d'uso: CREDITI_E_FONTI.txt.\n#ArtVision #Arte #Pittura\n",encoding="utf-8")
    final,plan,probe=make_video_cinematic(art,args.artist,args.duration,out)
    report={"artist":args.artist,"style":"cinematic_wow","video":str(final),
       "works":len(art),"shots":len(plan),"duration":float(probe["format"]["duration"]),
       "bytes":int(probe["format"]["size"]),"elapsed_seconds":round(time.monotonic()-started,1),
       "external_paid_apis_used":0,"voice":"off",
       "soundtrack":"Original algorithmic synthesis, musical sketch (not reference-video audio)",
       "publication_approved":False,
       "art_direction_guide":"modules/artvision/REGIA_CINEMA_WOW_V2.md"}
    (out/"REPORT_PRODUZIONE.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print("ARTVISION CINEMA V2 SUCCESS",json.dumps(report,ensure_ascii=False),flush=True)
    import shutil
    shutil.rmtree(out/"immagini",ignore_errors=True)

if __name__=="__main__":main()
