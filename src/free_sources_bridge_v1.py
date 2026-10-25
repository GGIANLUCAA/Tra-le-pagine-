#!/usr/bin/env python3
"""Tra le Pagine: ponte fonti immagini/video con ricerca on-demand e costo zero.

Controllo chiavi SOLO sulla presenza; non stampa mai i segreti.
Pixabay: solo ricerca singola, non scraping/download massivo (API terms).
Openverse: riusa Archivio V7; nessuna nuova API key.
Risultati non autorizzati per il render finché non siano verificati i diritti.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request

AGENT = "TraLePagine-EditorialResearch/1.0 (github.com/GGIANLUCAA/Tra-le-pagine-)"
NAMES = (
    "AIHORDE_API_KEY", "AIHORDE_API_KEY_2", "GEMINI_API_KEY",
    "OPENROUTER2", "OPENROUTER_API_KEY",
    "PIXABAY", "PIXABAY_API_KEY", "PRIXIBAY2", "PEXELS_API_KEY",
)
MAX_QUERY = 100


class SourceError(ValueError):
    pass


def configuration(environ=None):
    env = os.environ if environ is None else environ
    available = {name: bool(env.get(name, "").strip()) for name in NAMES}
    return {
        "secrets_presence_only": available,
        "horde_primary_ready": available["AIHORDE_API_KEY"],
        "pixabay_ready": available["PIXABAY"] or available["PIXABAY_API_KEY"],
        "openrouter_readiness": available["OPENROUTER2"] or available["OPENROUTER_API_KEY"],
        "notes": [
            "Presente significa solo che il secret e' stato fornito, non che e' valido.",
            "Solo AIHORDE_API_KEY puo' essere usato dall'adapter immagini esistente.",
            "AIHORDE_API_KEY_2 non e' usato per aggirare code o quote.",
            "PRIXIBAY2 e' registrato come nome segnalato dall'utente ma non viene usato automaticamente.",
            "OPENROUTER2 e' inattivo finche' non e' configurato un modello gratuito esplicito.",
            "Nessun secret viene registrato o pubblicato."
        ],
    }


def validate_query(query, limit, kind):
    query = query.strip()
    if not 3 <= len(query) <= MAX_QUERY:
        raise SourceError("Query richiesta tra 3 e 100 caratteri")
    if not re.fullmatch(r"[\w\s,'-]+", query, flags=re.UNICODE):
        raise SourceError("La query contiene caratteri non supportati")
    if kind not in ("image", "video"):
        raise SourceError("Tipo non valido")
    if not 1 <= limit <= 5:
        raise SourceError("Max cinque candidati per una ricerca manuale")
    return query


def fetch_json(url):
    # Chiamata interna soltanto a Pixabay; non stampare URL che contiene la key.
    if not url.startswith("https://pixabay.com/api/"):
        raise SourceError("Host non consentito")
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": AGENT})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            if int(res.headers.get("Content-Length", "0")) > 2_000_000:
                raise SourceError("Risposta oltre limite")
            raw = res.read(2_000_001)
            if len(raw) > 2_000_000:
                raise SourceError("Risposta oltre limite")
            return json.loads(raw)
    except urllib.error.HTTPError as exc:
        if exc.code == 429:
            raise SourceError("Pixabay: limite 429, nessun nuovo tentativo automatico") from None
        raise SourceError("Pixabay: errore HTTP " + str(exc.code)) from None
    except urllib.error.URLError:
        raise SourceError("Pixabay: connessione non disponibile") from None


def pixabay_search(query, kind, limit, key):
    if not key:
        raise SourceError("Manca PIXABAY (o PIXABAY_API_KEY) nei GitHub Secrets")
    validate_query(query, limit, kind)
    params = {
        "key": key,
        "q": query,
        "per_page": max(3, limit),
        "page": 1,
        "safesearch": "true",
        "lang": "en",
    }
    if kind == "image":
        params.update({"image_type": "all", "orientation": "vertical"})
    endpoint = "https://pixabay.com/api/" + ("videos/" if kind == "video" else "")
    # urllib non riprende l'URL nei log: non stampare mai l'eccezione grezza.
    response = fetch_json(endpoint + "?" + urllib.parse.urlencode(params))
    if not isinstance(response, dict) or not isinstance(response.get("hits"), list):
        raise SourceError("Formato risposta Pixabay non riconosciuto")
    found = []
    for item in response["hits"]:
        if not isinstance(item, dict):
            continue
        source = item.get("pageURL")
        if not isinstance(source, str) or not source.startswith("https://pixabay.com/"):
            continue
        if kind == "image":
            if int(item.get("imageWidth") or 0) < 640 or int(item.get("imageHeight") or 0) < 640:
                continue
            preview = item.get("webformatURL", "")
            dimensions = [int(item.get("imageWidth") or 0), int(item.get("imageHeight") or 0)]
        else:
            renditions = item.get("videos") or {}
            renditions = [renditions.get(t) or {} for t in ("medium", "small", "large", "tiny")]
            chosen = next((x for x in renditions if x.get("url") and x.get("width")), {})
            if not chosen:
                continue
            preview = item.get("picture_id", "")
            dimensions = [int(chosen.get("width") or 0), int(chosen.get("height") or 0)]
        found.append({
            "provider": "pixabay", "kind": kind,
            "id": item.get("id"), "title": item.get("tags", "")[:150],
            "creator": item.get("user", ""),
            "source_url": source, "preview": preview,
            "dimensions": dimensions,
            "rights": "Pixabay Content License - verificare la pagina originale e i limiti",
            "review_required": True,
            "selected": False,
            "note": "Solo candidato: nessun download, nessun inserimento automatico nel video.",
        })
        if len(found) >= limit:
            break
    return found


def openverse_search(query, kind, limit):
    validate_query(query, limit, kind)
    if kind != "image":
        raise SourceError("Openverse V7 nel progetto supporta solo immagini")
    from archivio_media_v7 import discover
    items = discover("openverse", "image", query, limit)
    return [{
        "provider": "openverse", "kind": "image",
        "id": x.get("id"), "title": x.get("title"),
        "creator": x.get("author"), "source_url": x.get("source_url"),
        "preview": x.get("preview_url"),
        "rights": x.get("license"), "license_url": x.get("license_url"),
        "review_required": True, "selected": False,
        "note": "Candidato d'archivio: provenienza e diritti da verificare.",
    } for x in items]


def produce(provider, query, kind, limit, environ=None):
    env = os.environ if environ is None else environ
    output = {
        "version": "free-sources-v1",
        "provider": provider, "kind": kind, "query": query if provider not in ("status", "plan") else "",
        "automatic_download": False, "automatic_publish": False,
        "paid_api_requests": False,
        "commercial_licence_approval": False,
        "items": [],
    }
    if provider in ("plan", "status"):
        output["configuration"] = configuration(env)
        output["next_step"] = "Selezionare un candidato e controllare diritti e aderenza alla scena."
    elif provider == "pixabay":
        output["items"] = pixabay_search(query, kind, limit,
                                         env.get("PIXABAY") or env.get("PIXABAY_API_KEY") or "")
    elif provider == "openverse":
        output["items"] = openverse_search(query, kind, limit)
    else:
        raise SourceError("Provider non abilitato")
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=["plan", "status", "pixabay", "openverse"], default="plan")
    parser.add_argument("--query", default="")
    parser.add_argument("--kind", choices=["image", "video"], default="image")
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--out", default="output/fonti_gratuite/REPORT.json")
    args = parser.parse_args()
    try:
        result = produce(args.provider, args.query, args.kind, args.limit)
        target = Path(args.out)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": "ok", "provider": args.provider,
                          "candidates": len(result["items"]), "report": str(target)}))
    except (SourceError, KeyError, ValueError) as exc:
        # Nessun traceback con URL contenenti API key.
        raise SystemExit("Operazione interrotta: " + str(exc)) from None


if __name__ == "__main__":
    main()
