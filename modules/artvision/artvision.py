#!/usr/bin/env python3
"""ArtVision: museum-sourced silent-voice art reels; no Gemini, no paid APIs."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import subprocess
import time
import unicodedata
import wave
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

USER_AGENT = "TraLePagine-ArtVision/1.0 (open-access cultural video; GitHub GGIANLUCAA/Tra-le-pagine-)"
CC0 = "https://creativecommons.org/publicdomain/zero/1.0/"
HTTP_PAUSE = 0.30


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()).strip()


def fetch(url, timeout=28, binary=False):
    last = None
    for retry in range(3):
        try:
            with urlopen(Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"}), timeout=timeout) as res:
                payload = res.read(16_000_000 if binary else 3_000_000)
            time.sleep(HTTP_PAUSE)
            return payload if binary else json.loads(payload.decode("utf-8"))
        except Exception as exc:
            last = exc
            time.sleep(1.5 * (retry + 1))
    raise RuntimeError(f"Download impossibile: {url[:105]} ({last})")


def artist_match(value, artist):
    target = norm(artist)
    value = norm(value)
    return bool(target and (target in value or value == target))


def discover_artic(artist):
    # Official museum API: only artworks explicitly marked public domain.
    fields = "id,title,artist_title,date_display,image_id,is_public_domain,copyright_notice,thumbnail"
    query = urlencode({"q": artist, "limit": "90", "fields": fields})
    payload = fetch("https://api.artic.edu/api/v1/artworks/search?" + query)
    root = payload.get("config", {}).get("iiif_url", "https://www.artic.edu/iiif/2")
    result = []
    for r in payload.get("data", []):
        if not (r.get("is_public_domain") is True and r.get("image_id")):
            continue
        if not artist_match(r.get("artist_title", ""), artist):
            continue
        image_url = f"{root}/{r['image_id']}/full/1686,/0/default.jpg"
        result.append({"source": "Art Institute of Chicago", "id": str(r["id"]),
                       "title": r.get("title") or "Senza titolo", "artist": r.get("artist_title"),
                       "year": r.get("date_display", ""), "url": f"https://www.artic.edu/artworks/{r['id']}",
                       "image_url": image_url, "license": "Public Domain / museum policy",
                       "license_url": "https://www.artic.edu/image-licensing"})
    return result


def discover_cleveland(artist):
    query = urlencode({"artists": artist, "limit": 100, "skip": 0})
    payload = fetch("https://openaccess-api.clevelandart.org/api/artworks/?" + query)
    result = []
    for r in payload.get("data", []):
        if r.get("share_license_status") != "CC0":
            continue
        authors = ", ".join((a.get("name") or a.get("description") or "") for a in r.get("creators", []) if isinstance(a, dict))
        if not authors:
            authors = ", ".join(a.get("name", "") for a in r.get("artists", []) if isinstance(a, dict))
        if not artist_match(authors, artist):
            continue
        pictures = r.get("images") or {}
        url = (pictures.get("print") or pictures.get("web") or {}).get("url", "")
        if not url:
            continue
        result.append({"source": "Cleveland Museum of Art", "id": str(r["id"]),
                       "title": r.get("title") or "Senza titolo", "artist": authors,
                       "year": r.get("creation_date", ""), "url": r.get("url") or f"https://www.clevelandart.org/art/{r['id']}",
                       "image_url": url, "license": "CC0", "license_url": CC0})
    return result


def discover_met(artist):
    query = urlencode({"q": artist, "artistOrCulture": "true", "hasImages": "true", "offset": 0, "limit": 70})
    ids = fetch("https://collectionapi.metmuseum.org/public/collection/v1.1/search?" + query).get("objectIDs") or []
    result = []
    for oid in ids[:55]:
        try:
            r = fetch(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{oid}")
        except Exception as err:
            print("MET skip", oid, err, flush=True)
            continue
        if not (r.get("isPublicDomain") is True and r.get("primaryImage")):
            continue
        if not artist_match(r.get("artistDisplayName", ""), artist):
            continue
        result.append({"source": "The Metropolitan Museum of Art", "id": str(oid),
                       "title": r.get("title") or "Senza titolo",
                       "artist": r.get("artistDisplayName"), "year": r.get("objectDate", ""),
                       "url": r.get("objectURL") or f"https://www.metmuseum.org/art/collection/search/{oid}",
                       "image_url": r["primaryImage"],
                       "license": "CC0", "license_url": CC0})
        if len(result) >= 25:
            break
    return result


def collect(artist, limit=38):
    found, errors = [], {}
    for name, method in [("Art Institute", discover_artic),
                         ("Cleveland", discover_cleveland), ("Met", discover_met)]:
        try:
            items = method(artist)
            print(f"{name}: {len(items)} opere verificabili", flush=True)
            found += items
        except Exception as exc:
            errors[name] = str(exc)
            print(f"Archivio {name} non disponibile: {exc}", flush=True)
    # Prefer museum-provenanced image records and avoid same title from multiple archives.
    unique, seen = [], set()
    for item in found:
        key = (norm(item["title"]), norm(item.get("year", "")))
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique[:limit], errors


def download_pictures(records, directory, max_works):
    directory.mkdir(parents=True, exist_ok=True)
    saved, failures = [], []
    for item in records:
        if len(saved) >= max_works:
            break
        name = hashlib.sha256(item["image_url"].encode()).hexdigest()[:15]
        path = directory / (name + ".jpg")
        try:
            if not path.exists():
                raw = fetch(item["image_url"], timeout=42, binary=True)
                if not raw or len(raw) < 7_000:
                    raise ValueError("file immagine troppo piccolo")
                path.write_bytes(raw)
            with Image.open(path) as im:
                im.verify()
            with Image.open(path) as im:
                if min(im.size) < 400:
                    raise ValueError(f"risoluzione insufficiente {im.size}")
                size = im.size
            entry = dict(item)
            entry.update({"file": str(path), "width": size[0], "height": size[1],
                          "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
            saved.append(entry)
            print(f"Immagine {len(saved)}/{max_works}: {item['title']}", flush=True)
        except Exception as exc:
            path.unlink(missing_ok=True)
            failures.append({"title": item["title"], "error": str(exc)})
        time.sleep(0.8 if item["source"] == "Art Institute of Chicago" else 0)
    return saved, failures


def font(size, bold=False):
    paths = (["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"] if bold else
             ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"])
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def canvas(path, size=(720, 1280)):
    with Image.open(path) as original:
        photo = ImageOps.exif_transpose(original).convert("RGB")
    bg = ImageOps.fit(photo, size, Image.Resampling.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(52))
    bg = Image.blend(bg, Image.new("RGB", size, (10, 13, 19)), 0.66)
    front = ImageOps.contain(photo, (size[0] - 44, size[1] - 190), Image.Resampling.LANCZOS)
    x, y = (size[0] - front.width) // 2, (size[1] - front.height) // 2
    bg.paste(front, (x, y))
    return bg


def cover(photo, artist, path, size=(720, 1280)):
    img = canvas(photo, size)
    shade = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(shade)
    draw.rectangle((0, 0, size[0], size[1]), fill=(5, 8, 16, 140))
    img = Image.alpha_composite(img.convert("RGBA"), shade)
    d = ImageDraw.Draw(img)
    d.line((80, 220, size[0]-80, 220), fill=(216, 187, 124), width=3)
    def center(text, y, f, color):
        bbox = d.textbbox((0, 0), text, font=f)
        d.text(((size[0] - (bbox[2]-bbox[0])) / 2, y), text, font=f, fill=color)
    center("A R T V I S I O N", 155, font(26, True), (231, 208, 157))
    words = artist.upper().split()
    lines, curr = [], ""
    for word in words:
        test = (curr + " " + word).strip()
        if len(test) > 17 and curr:
            lines.append(curr); curr = word
        else:
            curr = test
    if curr: lines.append(curr)
    y = 540 - len(lines)*42
    for line in lines:
        fsize = min(65, int(600 / max(1, len(line)*0.63)))
        center(line, y, font(fsize, True), (251, 247, 235))
        y += 86
    center("L'ARTE IN MOVIMENTO", 1020, font(24), (237, 218, 176))
    center("OPERE ORIGINALI  •  NESSUNA VOCE", 1080, font(18), (221, 221, 223))
    img.convert("RGB").save(path, quality=94)


def ambient_audio(path, seconds, sample_rate=22050):
    """Original, algorithmic chord progression. No copyrighted recordings."""
    chords = [(174.61, 220.0, 261.63), (146.83, 196.0, 246.94),
              (130.81, 174.61, 220.0), (155.56, 196.0, 233.08)]
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        for start in range(0, math.ceil(seconds)):
            n = min(sample_rate, max(0, int((seconds-start)*sample_rate)))
            if not n: break
            t = start + np.arange(n, dtype=np.float64) / sample_rate
            signal = np.zeros(n, dtype=np.float64)
            for j, chord in enumerate(chords):
                # Crossfade neighboring chords across a 24-second cycle.
                weight = np.maximum(0, 1 - np.abs(((t / 24.0 - j + 2) % 4) - 2))
                for k, f in enumerate(chord):
                    signal += weight * (0.06/k if k else 0.09) * (np.sin(2*np.pi*f*t) + 0.18*np.sin(4*np.pi*f*t))
            bell = np.sin(2*np.pi*(t*0.5 % 1) * 0.5)
            signal += 0.016 * np.sin(2*np.pi*523.25*t) * np.maximum(0, bell)**8
            env = np.minimum(1, t / 3) * np.minimum(1, (seconds-t)/4)
            signal = np.clip(signal * np.maximum(0, env), -0.75, 0.75)
            stereo = np.column_stack((signal, signal*0.95))
            wav.writeframes((stereo * 32767).astype("<i2").tobytes())


def run(cmd):
    r = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if r.returncode:
        raise RuntimeError("FFmpeg: " + r.stderr[-3000:])
    return r


def make_video(images, artist, duration, out, size=(720,1280), fps=24):
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise RuntimeError("FFmpeg e ffprobe richiesti")
    tmp = out / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    intro = out / "COPERTINA.jpg"
    cover(images[0]["file"], artist, intro, size)
    shots = [(intro, 5.0, "intro")]
    available = duration-9
    count = min(22, max(14, len(images)*2))
    for i in range(count):
        rec = images[i % len(images)]
        rendered = tmp / f"frame_{i:03d}.jpg"
        canvas(rec["file"], size).save(rendered, quality=94, subsampling=0)
        shots.append((rendered, available/count, "opera"))
    shots.append((intro, 4.0, "finale"))
    clips, timeline = [], []
    offset = 0.0
    for index, (img, secs, kind) in enumerate(shots):
        nframes = max(2, round(secs*fps))
        secs = nframes/fps
        clip = tmp / f"clip_{index:03d}.mp4"
        vfilter = (f"zoompan=z='min(zoom+0.00019,1.07)':"
                   f"x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={nframes}:"
                   f"s={size[0]}x{size[1]}:fps={fps},format=yuv420p,"
                   f"fade=t=in:st=0:d=0.35,fade=t=out:st={max(0,secs-0.40):.3f}:d=0.40")
        run(["ffmpeg","-hide_banner","-loglevel","error","-y","-loop","1","-framerate","1",
             "-i",str(img),"-vf",vfilter,"-frames:v",str(nframes),"-an",
             "-c:v","libx264","-preset","ultrafast","-crf","23",
             "-pix_fmt","yuv420p","-movflags","+faststart",str(clip)])
        clips.append(clip)
        timeline.append({"index":index,"start":round(offset,2),"end":round(offset+secs,2),"type":kind,
                         "title": images[(index-1)%len(images)]["title"] if kind=="opera" else artist})
        offset += secs
        print(f"Montaggio {index+1}/{len(shots)}", flush=True)
    listing = tmp / "join.txt"
    listing.write_text("".join("file '"+str(p.resolve()).replace("'","'\\''")+"'\n" for p in clips), encoding="utf-8")
    soundtrack = tmp / "musica_originale.wav"
    ambient_audio(soundtrack, offset)
    final = out/"ARTVISION_VIDEO.mp4"
    run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0",
         "-i",str(listing),"-i",str(soundtrack),"-c:v","copy",
         "-c:a","aac","-b:a","160k","-shortest","-movflags","+faststart",str(final)])
    probe = json.loads(run(["ffprobe","-v","error","-show_entries",
                            "format=duration,size:stream=codec_type,width,height","-of","json",str(final)]).stdout)
    length = float(probe["format"]["duration"])
    if abs(length - duration) > 2.0 or {s["codec_type"] for s in probe["streams"]} != {"audio","video"}:
        raise RuntimeError(f"Controllo durata/audio/video fallito: {probe}")
    return final, timeline, probe


def main():
    ap = argparse.ArgumentParser(description="ArtVision, authentic museum images to silent-voice reels")
    ap.add_argument("--artist", default="Vincent van Gogh")
    ap.add_argument("--duration", type=int, default=150)
    ap.add_argument("--max-works", type=int, default=16)
    ap.add_argument("--out", default="output/artvision")
    ap.add_argument("--research-only", action="store_true")
    args = ap.parse_args()
    if not (18 <= args.duration <= 180):
        ap.error("Durata: da 18 a 180 secondi; formato finale 120-180")
    if not 4 <= args.max_works <= 32:
        ap.error("Numero massimo opere: 4-32")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    records, errors = collect(args.artist)
    if len(records) < 6:
        raise SystemExit(f"Opere con licenze adeguate insufficienti: {len(records)}. {errors}")
    art, failures = download_pictures(records, out/"immagini", args.max_works)
    if len(art) < 6:
        raise SystemExit(f"Download di opere autentiche insufficiente: {len(art)}. {failures[:5]}")
    manifest = {"series":"ArtVision","artist":args.artist,
                "created_utc":datetime.now(timezone.utc).isoformat(),
                "license_policy":"Only explicit museum CC0 or public domain images, verify local law/terms before publishing",
                "publication_approved":False,"works":art,"provider_errors":errors,"image_failures":failures}
    (out/"OPERE_FONTI_E_DIRITTI.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    credits = [f"{p['title']} ({p['year']}) — {p['artist']} | {p['source']} | {p['license']} | {p['url']}" for p in art]
    (out/"CREDITI_E_FONTI.txt").write_text("\n".join(credits)+"\n",encoding="utf-8")
    (out/"DESCRIZIONE_SOCIAL.txt").write_text(
        f"{args.artist} — un viaggio visivo tra le sue opere originali. 🎨\n"
        "Immagini provenienti da collezioni museali open access. Fonti e attribuzioni nel file CREDITI_E_FONTI.txt.\n"
        "#arte #artvision #pittura #museo\n",encoding="utf-8")
    if args.research_only:
        print(f"Ricerca completata: {len(art)} immagini autentiche. Nessun MP4 richiesto.")
        return
    mp4,timeline,probe = make_video(art,args.artist,args.duration,out)
    (out/"MONTAGGIO.json").write_text(json.dumps(timeline,ensure_ascii=False,indent=2),encoding="utf-8")
    report = {"artist":args.artist,"video":str(mp4),"works":len(art),
              "shots":len(timeline),"duration":probe["format"]["duration"],
              "bytes":int(probe["format"]["size"]),"wall_seconds":round(time.perf_counter()-start,2),
              "external_paid_apis_used":0,"voice":"off",
              "soundtrack":"algorithmic original, generated locally",
              "publication_approved":False}
    (out/"REPORT_PRODUZIONE.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print("ARTVISION OK:",json.dumps(report,ensure_ascii=False),flush=True)
    shutil.rmtree(out/"tmp",ignore_errors=True)
    shutil.rmtree(out/"immagini",ignore_errors=True)


if __name__ == "__main__":
    main()
