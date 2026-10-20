#!/usr/bin/env python3
"""Archivio Media V7: discovery and selective import of licensed media.
Works remotely on GitHub Actions; no phone installation, no TTS or renderer changes.
Only user-selected assets are downloaded; never uploads anything to social media.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

USER_AGENT = "TraLePagine-MediaResearch/1.0 (editorial preview; GitHub Actions)"
LICENSES = {"cc0", "by"}
ALLOWED_MEDIA_HOSTS = {"upload.wikimedia.org", "images.pexels.com", "videos.pexels.com",
                       "static-videos.pexels.com"}
MAX_IMAGE_BYTES = 12 * 1024 * 1024
MAX_VIDEO_BYTES = 45 * 1024 * 1024


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise ValueError("Redirect vietato sui download di materiale multimediale.")


def api_json(url, headers=None, timeout=18):
    request = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Accept": "application/json", **(headers or {})})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        if int(response.headers.get("Content-Length", "0")) > 2_000_000:
            raise ValueError("Risposta API troppo grande.")
        body = response.read(2_000_001)
        if len(body) > 2_000_000:
            raise ValueError("Risposta API troppo grande.")
        return json.loads(body)


def permitted_openverse(entry):
    lic = str(entry.get("license", "")).lower().strip()
    license_url = str(entry.get("license_url") or "")
    if lic not in LICENSES:
        return False
    if lic == "by":
        return license_url.startswith("https://creativecommons.org/licenses/by/")
    return license_url.startswith("https://creativecommons.org/publicdomain/zero/")


def image_from_openverse(entry):
    if not permitted_openverse(entry):
        return None
    uid = str(entry.get("id", ""))
    if not re.fullmatch(r"[0-9a-fA-F-]{36}", uid):
        return None
    return {
        "id": uid, "provider": "openverse", "kind": "image",
        "title": str(entry.get("title") or "Senza titolo")[:180],
        "author": str(entry.get("creator") or "Autore non indicato")[:160],
        "source_url": str(entry.get("foreign_landing_url") or ""),
        "preview_url": str(entry.get("thumbnail") or ""),
        "download_url": str(entry.get("url") or ""),
        "license": str(entry.get("license", "")).upper(),
        "license_url": str(entry.get("license_url", "")),
        "needs_manual_rights_check": True,
        "note": "Controllare originale, crediti, diritti delle persone e veridicità dei metadati."
    }


def pexels_from_photo(item):
    return {
        "id": str(item["id"]), "provider": "pexels", "kind": "image",
        "title": str(item.get("alt") or f"Foto {item['id']}")[:180],
        "author": str(item.get("photographer") or "Autore Pexels")[:160],
        "source_url": str(item.get("url") or ""),
        "preview_url": str(item.get("src", {}).get("medium") or ""),
        "download_url": str(item.get("src", {}).get("large2x") or ""),
        "license": "Pexels License", "license_url": "https://www.pexels.com/license",
        "needs_manual_rights_check": True,
        "note": "Non ridistribuire come file stock autonomo; citare autore e Pexels."
    }


def pexels_from_video(item):
    files = [f for f in item.get("video_files", []) if
             f.get("file_type") == "video/mp4" and f.get("link")]
    files.sort(key=lambda x: (abs(int(x.get("width") or 720) - 720),
                              abs(int(x.get("height") or 1280) - 1280)))
    return {
        "id": str(item["id"]), "provider": "pexels", "kind": "video",
        "title": f"Filmato Pexels {item['id']}",
        "author": str(item.get("user", {}).get("name") or "Autore Pexels")[:160],
        "source_url": str(item.get("url") or ""),
        "preview_url": str(item.get("image") or ""),
        "download_url": str(files[0].get("link") if files else ""),
        "license": "Pexels License", "license_url": "https://www.pexels.com/license",
        "duration": item.get("duration"), "needs_manual_rights_check": True,
        "note": "Scegliere filmati brevi, revisione editoriale e citazione fonte Pexels."
    }


def discover(provider, kind, query, limit, api_key=""):
    if not 1 <= limit <= 12 or not 2 <= len(query.strip()) <= 180:
        raise ValueError("Ricerca da 2 a 180 caratteri; massimo 12 risultati.")
    if provider == "openverse":
        if kind != "image":
            raise ValueError("Openverse V7 ricerca immagini; usa Pexels per filmati.")
        params = urllib.parse.urlencode({
            "q": query, "page_size": limit, "license": "cc0,by", "source": "wikimedia",
            "license_type": "commercial", "mature": "false"
        })
        data = api_json("https://api.openverse.org/v1/images/?" + params)
        found = [image_from_openverse(x) for x in data.get("results", [])]
        return [x for x in found if x]
    if provider == "pexels":
        if not api_key:
            raise ValueError("Manca PEXELS_API_KEY nei GitHub Actions Secrets; usa Openverse gratis.")
        path = "/v1/search" if kind == "image" else "/v1/videos/search"
        params = urllib.parse.urlencode({
            "query": query, "per_page": limit, "orientation": "portrait"})
        data = api_json("https://api.pexels.com" + path + "?" + params,
                        {"Authorization": api_key})
        if kind == "image":
            return [pexels_from_photo(i) for i in data.get("photos", [])]
        return [pexels_from_video(i) for i in data.get("videos", [])]
    raise ValueError("Fonte sconosciuta.")


def lookup(provider, kind, identifier, api_key=""):
    if provider == "openverse":
        if kind != "image" or not re.fullmatch(r"[0-9a-fA-F-]{36}", identifier):
            raise ValueError("ID Openverse non valido.")
        entry = api_json("https://api.openverse.org/v1/images/" + identifier + "/")
        item = image_from_openverse(entry)
        if not item:
            raise ValueError("Licenza Openverse non ammessa per l'import selettivo.")
        return item
    if provider == "pexels":
        if not api_key:
            raise ValueError("PEXELS_API_KEY non configurata.")
        if not re.fullmatch(r"[0-9]{1,14}", identifier):
            raise ValueError("ID Pexels non valido.")
        path = "/v1/photos/" if kind == "image" else "/v1/videos/videos/"
        data = api_json("https://api.pexels.com" + path + identifier,
                        {"Authorization": api_key})
        return pexels_from_photo(data) if kind == "image" else pexels_from_video(data)
    raise ValueError("Provider non valido.")


def allowed_media_url(url: str, provider: str, kind: str):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.username or parsed.password or parsed.port:
        return False
    host = (parsed.hostname or "").lower()
    if host not in ALLOWED_MEDIA_HOSTS:
        return False
    if provider == "openverse":
        return host == "upload.wikimedia.org" and kind == "image"
    if provider == "pexels":
        return host in (
            {"images.pexels.com"} if kind == "image" else
            {"videos.pexels.com", "static-videos.pexels.com"}
        )
    return False


def check_signature(head: bytes, kind: str):
    if kind == "image":
        return head.startswith(b"\xff\xd8\xff") or head.startswith(b"\x89PNG\r\n\x1a\n") or (
            len(head) > 12 and head[0:4] == b"RIFF" and head[8:12] == b"WEBP")
    return len(head) >= 12 and head[4:8] == b"ftyp"


def file_ext(head: bytes, kind: str):
    if kind == "video":
        return ".mp4"
    if head.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if head.startswith(b"\x89PNG"):
        return ".png"
    return ".webp"


def download_approved(item, destination: Path):
    url, provider, kind = item["download_url"], item["provider"], item["kind"]
    if not allowed_media_url(url, provider, kind):
        raise ValueError("Dominio non approvato. Non eseguo download da host sconosciuti.")
    dest = Path(destination)
    dest.mkdir(parents=True, exist_ok=True)
    limit = MAX_VIDEO_BYTES if kind == "video" else MAX_IMAGE_BYTES
    opener = urllib.request.build_opener(NoRedirect)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with opener.open(req, timeout=35) as response:
        if response.status != 200:
            raise ValueError("Risposta download inattesa.")
        if int(response.headers.get("Content-Length", "0")) > limit:
            raise ValueError("File supera dimensione massima.")
        blob = response.read(limit + 1)
    if len(blob) > limit or len(blob) < 500:
        raise ValueError("File troppo grande o sospettosamente piccolo.")
    if not check_signature(blob[:32], kind):
        raise ValueError("Il contenuto non è una vera immagine o MP4.")
    sha = hashlib.sha256(blob).hexdigest()
    ext = file_ext(blob[:32], kind)
    filename = f"{provider}_{item['id'][:48]}_{sha[:12]}{ext}"
    (dest / filename).write_bytes(blob)
    return {"file": filename, "sha256": sha, "bytes": len(blob)}


def attribution(item, modified=False):
    return (
        f"Titolo: {item['title']}\n"
        f"Autore: {item['author']}\n"
        f"Opera originale: {item['source_url']}\n"
        f"Fonte: {item['provider']}\n"
        f"Licenza dichiarata: {item['license']}\n"
        f"Testo licenza: {item['license_url']}\n"
        f"Modifiche: {'da documentare dopo il montaggio' if modified else 'nessuna in archivio'}\n"
        "AVVISO: metadati automatici; verifica manualmente copyright, persone, loghi e contesto.\n"
    )


def safe_url(url):
    parsed = urllib.parse.urlsplit(url)
    return url if parsed.scheme == "https" and parsed.netloc and not parsed.username else ""


def render_html(results, provider, query):
    cards = []
    for item in results:
        img = html.escape(safe_url(item.get("preview_url", "")), quote=True)
        landing = html.escape(safe_url(item.get("source_url", "")), quote=True)
        source = f'<a href="{landing}">Fonte originale</a>' if landing else ""
        cards.append(
            '<article>' + (f'<img loading="lazy" src="{img}" alt="Anteprima">' if img else "") +
            f'<h2>{html.escape(item["title"])}</h2>'
            f'<p><b>Autore:</b> {html.escape(item["author"])}<br>'
            f'<b>Licenza:</b> {html.escape(item["license"])}<br>'
            f'<b>ID da importare:</b> <code>{html.escape(item["id"])}</code></p>'
            f'<p>{source} — <a href="{html.escape(safe_url(item["license_url"]), quote=True)}">Licenza</a></p>'
            '<small>Da verificare prima dell’uso. Nessuna importazione automatica.</small></article>')
    return (
        '<!doctype html><html lang="it"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Tra le Pagine - Archivio media</title>'
        '<style>body{background:#0c2934;color:#f8f1e7;font:16px system-ui;padding:20px}'
        'main{max-width:1100px;margin:auto}.grid{display:grid;grid-template-columns:'
        'repeat(auto-fill,minmax(245px,1fr));gap:16px}article{border:1px solid #54707a;'
        'background:#193c4a;border-radius:12px;padding:12px;overflow-wrap:anywhere}'
        'img{width:100%;height:240px;object-fit:contain}a{color:#eac792}'
        'code{word-break:break-all}small{color:#b5c5c8}</style><main>'
        '<h1>Archivio media V7 — ricerca senza generazione AI</h1>'
        f'<p>Fonte: {html.escape(provider)} · Ricerca: {html.escape(query)} · '
        'Anteprima non approvata per pubblicazione</p><div class="grid">'
        + "".join(cards) + '</div><p>Da Android: annota l’ID scelto; poi avvia il workflow '
        'in modalità importa. Le immagini presenti nei vecchi episodi restano disponibili.</p>'
        '</main></html>'
    )


def main():
    parser = argparse.ArgumentParser(description="Media V7: ricerca e importazione selettiva con licenze.")
    parser.add_argument("--provider", choices=["openverse", "pexels"], default="openverse")
    parser.add_argument("--kind", choices=["image", "video"], default="image")
    parser.add_argument("--mode", choices=["discover", "import"], default="discover")
    parser.add_argument("--query", default="river landscape")
    parser.add_argument("--id", default="")
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--out", default="output/archivio_media_v7")
    args = parser.parse_args()
    dest = Path(args.out)
    dest.mkdir(parents=True, exist_ok=True)
    key = os.environ.get("PEXELS_API_KEY", "")
    if args.mode == "discover":
        items = discover(args.provider, args.kind, args.query, args.limit, key)
        payload = {"version": "V7", "provider": args.provider, "query": args.query,
                   "media_type": args.kind, "results": items,
                   "license_verified_by_human": False, "auto_publish": False,
                   "note": "Anteprime da approvare, non prova di licenza o autenticità."}
        (dest / "RISULTATI_V7.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (dest / "SFOGLIA_MEDIA_V7.html").write_text(render_html(items,args.provider,args.query),
                                                       encoding="utf-8")
        print(f"ARCHIVIO V7: {len(items)} candidati, zero immagini/video generati o scaricati.")
    else:
        item = lookup(args.provider,args.kind,args.id,key)
        result = download_approved(item,dest)
        (dest / "PROVENIENZA_V7.json").write_text(
            json.dumps({"media":item,"download":result,"reviewed":False,
                        "approval_required":True,"auto_publish":False},
                       ensure_ascii=False,indent=2) + "\n",encoding="utf-8")
        (dest / "CREDITI_DA_VERIFICARE.txt").write_text(attribution(item),
                                                         encoding="utf-8")
        print(f"IMPORTATO (NON APPROVATO): {result['file']}, {result['bytes']} byte.")
    print("Voce Google Gemini e render V5 NON MODIFICATI. Nessuna pubblicazione.")


if __name__ == "__main__":
    main()
