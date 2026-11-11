#!/usr/bin/env python3
"""Controluce: raccolta editoriale RSS/Atom e validazione episodi.

Nessun LLM decide cosa e' vero. Le notizie sono SOLO candidate da verificare.
La raccolta non scrive mai su episodes/ e non pubblica nulla.
Usa esclusivamente la libreria standard Python.
"""
from __future__ import annotations
import argparse
from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from html.parser import HTMLParser
import hashlib
import json
import re
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlparse
from zoneinfo import ZoneInfo
import xml.etree.ElementTree as ET
import zipfile

ROME = ZoneInfo("Europe/Rome")
ROOT = Path(__file__).resolve().parents[1]
FORMAT = ROOT / "formats" / "controluce"
LIMIT_BYTES = 1_800_000
USER_AGENT = "ControluceResearch/0.1 (+public editorial research; no personal data)"

class PlainText(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts = []
    def handle_data(self, data):
        self.parts.append(data)

def clean_html(value):
    parser = PlainText(); parser.feed(value or "")
    return re.sub(r"\s+", " ", unescape(" ".join(parser.parts))).strip()

def node_text(elem, tags):
    for tag in tags:
        node = elem.find(tag)
        if node is not None and node.text:
            return node.text.strip()
    return ""

def parse_date(value):
    if not value: return None
    try:
        dt = parsedate_to_datetime(value)
    except (TypeError, ValueError, IndexError):
        try: dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError: return None
    if dt.tzinfo is None: dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(ROME)

def parse_feed(data, source):
    """Estrae candidate RSS/Atom, senza attribuire certezza a titolo o abstract."""
    root = ET.fromstring(data)
    entries = root.findall("./channel/item")
    atom = False
    if not entries:
        entries = root.findall("{http://www.w3.org/2005/Atom}entry")
        atom = True
    rows = []
    for entry in entries:
        if atom:
            ns = "{http://www.w3.org/2005/Atom}"
            title = node_text(entry, [ns + "title"])
            link = ""
            for l in entry.findall(ns + "link"):
                if l.get("rel", "alternate") == "alternate" and l.get("href"):
                    link = l.get("href"); break
            description = node_text(entry, [ns + "summary", ns + "content"])
            published = node_text(entry, [ns + "published", ns + "updated"])
        else:
            title = node_text(entry, ["title"])
            link = node_text(entry, ["link"])
            description = node_text(entry, ["description", "{http://purl.org/rss/1.0/modules/content/}encoded"])
            published = node_text(entry, ["pubDate", "{http://purl.org/dc/elements/1.1/}date"])
        if not title or not link or urlparse(link).scheme not in ("https", "http"):
            continue
        dt = parse_date(published)
        rows.append({
            "id": hashlib.sha256(link.encode("utf-8")).hexdigest()[:16],
            "title": clean_html(title), "url": link,
            "summary": clean_html(description)[:450],
            "published_at_rome": dt.isoformat() if dt else None,
            "published_date_rome": dt.date().isoformat() if dt else None,
            "event_date": None,  # La data dell'articolo NON e' quella dell'evento!
            "source_id": source["id"], "source_name": source["name"],
            "source_kind": source["kind"], "status": "da_verificare",
        })
    return rows

def fetch_feed(url, timeout=12):
    if urlparse(url).scheme != "https":
        raise ValueError("Sono consentiti soltanto feed HTTPS")
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml"})
    with urlopen(req, timeout=timeout) as response:
        data = response.read(LIMIT_BYTES + 1)
    if len(data) > LIMIT_BYTES: raise ValueError("Feed oltre il limite")
    return data

def collect(sources_file, target, output, fetcher=fetch_feed):
    sources = json.loads(Path(sources_file).read_text(encoding="utf-8"))["sources"]
    # Includiamo anche pubblicazioni di oggi che possono riferirsi a ieri;
    # la data dell'evento va comunque controllata a mano.
    upper = target + timedelta(days=2)
    lower = target - timedelta(days=1)
    items = []; errors = []
    for source in sources:
        feed = source.get("rss")
        if not feed: continue
        try:
            rows = parse_feed(fetcher(feed), source)
            for row in rows:
                when = row["published_date_rome"]
                if when and not lower <= date.fromisoformat(when) < upper: continue
                items.append(row)
        except (Exception,) as exc:
            errors.append({"source_id":source["id"], "feed":feed, "error":str(exc)[:240]})
    seen = set(); unique = []
    for row in items:
        if row["id"] in seen: continue
        seen.add(row["id"]);unique.append(row)
    unique.sort(key=lambda x:(x["published_at_rome"] or "", x["source_name"]), reverse=True)
    report = {
        "format":"controluce.research_candidates.v1",
        "target_event_date":target.isoformat(),
        "timezone":"Europe/Rome", "status":"raccolta_non_verificata",
        "note":"Solo spunti. Pubblicazione articolo != data evento; titoli e riassunti NON sono fatti accertati. Necessarie fonti primarie e controllo umano.",
        "sources_consulted":len([s for s in sources if s.get("rss")]),
        "source_errors":errors, "candidates":unique,
        "selected_story":None, "approved_for_render":False,
    }
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return report

def sentence_count(script):
    return len([x for x in re.split(r'(?<=[.!?])\s+(?=[A-ZÀ-ÙÈÉ«“])', re.sub(r'\s+', ' ', script.strip())) if x.strip()])

def validate_episode(episode, *, require_images=True):
    ep = Path(episode)
    def require(ok,msg):
        if not ok: raise ValueError(msg)
    required = ["metadata.json", "research.json", "testo.txt", "scene_cues.json", "DESCRIZIONE_SOCIAL.txt", "asset_manifest.json"]
    for name in required: require((ep/name).is_file(), "File mancante: " + name)
    meta = json.loads((ep/"metadata.json").read_text(encoding="utf-8"))
    research = json.loads((ep/"research.json").read_text(encoding="utf-8"))
    assets = json.loads((ep/"asset_manifest.json").read_text(encoding="utf-8"))
    text = (ep/"testo.txt").read_text(encoding="utf-8").strip()
    cues = json.loads((ep/"scene_cues.json").read_text(encoding="utf-8"))
    require(meta.get("series")=="Controluce", "Questa cartella non e' un episodio Controluce")
    require(re.fullmatch(r"\d{4}-\d\d-\d\d", str(meta.get("event_date",""))), "event_date non valida")
    require(str(meta.get("title","")).strip(), "Titolo mancante")
    require(meta.get("approved_for_render") is True and research.get("approved_by_editor") is True,
            "Approvazione editoriale esplicita mancante")
    require(research.get("event_date")==meta["event_date"], "Date evento discordanti")
    sources = research.get("sources",[])
    domains = {urlparse(s.get("url","")).netloc.lower().removeprefix("www.") for s in sources
               if s.get("used_for_verification") is True and urlparse(s.get("url","")).scheme=="https"}
    require(len(domains)>=2, "Servono almeno due domini di fonti verificati e distinti")
    claims=research.get("claims",[])
    require(bool(claims) and all(c.get("status") in ("confirmed","attributed","uncertain","analysis") for c in claims),
            "Scheda dei fatti incompleta")
    source_ids={s.get("id") for s in sources}
    for claim in claims:
        refs=claim.get("source_ids",[])
        if claim["status"] in ("confirmed","attributed"):
            require(bool(refs) and set(refs).issubset(source_ids), "Fatto senza fonte verificabile")
    words=len(text.split())
    require(245<=words<=410, f"Copione di {words} parole fuori dal limite 245–410")
    n=sentence_count(text)
    require(isinstance(cues,list) and 8<=len(cues)<=20, "Previsti 8–20 cambi di scena")
    indices=[c.get("start_sentence") for c in cues]
    require(indices[0]==0 and all(type(i) is int and 0<=i<n for i in indices)
            and all(a<b for a,b in zip(indices,indices[1:])), "Scene non allineate alle frasi")
    ids={c.get("asset") for c in cues}
    require(all(type(i) is int and 1<=i<=35 for i in ids),"Identificativi asset non validi")
    manifest={a.get("asset"):a for a in assets.get("assets",[])}
    for aid in ids:
        require(aid in manifest, f"Asset {aid} non dichiarato nel manifest")
        asset=manifest[aid]
        require(asset.get("type") in ("symbolic_ai","documentary","licensed_stock","original"), "Tipo asset non riconosciuto")
        if asset["type"] != "symbolic_ai":
            require(str(asset.get("rights","")).strip() and asset["rights"]!="da_verificare", f"Diritti asset {aid} non documentati")
        if asset["type"]=="documentary":
            require(str(asset.get("source_url","")).startswith("https://"), "Fonte immagine documentale mancante")
    if require_images:
        archive=ep/"scene_premium.zip"
        if archive.exists():
            with zipfile.ZipFile(archive) as z:
                names={Path(item.filename).stem.lower() for item in z.infolist() if not item.is_dir() and item.file_size>=35_000}
            missing=[i for i in ids if f"scena_{i:02d}" not in names]
        else:
            missing=[i for i in ids if not (ep/"images"/f"scena_{i:02d}.jpg").is_file()
                     or (ep/"images"/f"scena_{i:02d}.jpg").stat().st_size<35_000]
        require(not missing, "Immagini premium mancanti: "+", ".join(map(str,missing)))
    return {"episode":str(ep), "title":meta["title"], "event_date":meta["event_date"],
            "words":words, "sentences":n, "scenes":len(cues),"verified_source_domains":len(domains),
            "images_ready":require_images}

def main():
    p=argparse.ArgumentParser(description="Controluce - ricerca quotidiana e controllo editoriale")
    sub=p.add_subparsers(dest="command",required=True)
    collect_cmd=sub.add_parser("collect",help="Raccoglie candidati RSS senza considerarli verificati")
    collect_cmd.add_argument("--date",help="Data evento YYYY-MM-DD, default ieri (Europe/Rome)")
    collect_cmd.add_argument("--sources",default=str(FORMAT/"sources.json"))
    collect_cmd.add_argument("--output",default="output_controluce/candidates.json")
    validate_cmd=sub.add_parser("validate",help="Blocca render se fatti, diritti o immagini non approvati")
    validate_cmd.add_argument("--episode",required=True)
    validate_cmd.add_argument("--without-images",action="store_true",help="Solo revisione editoriale iniziale")
    a=p.parse_args()
    if a.command=="collect":
        target=date.fromisoformat(a.date) if a.date else datetime.now(ROME).date()-timedelta(days=1)
        report=collect(a.sources,target,a.output)
        print(f"Data {target}: {len(report['candidates'])} candidate, {len(report['source_errors'])} errori feed. Report: {a.output}")
    else:
        print(json.dumps(validate_episode(a.episode,require_images=not a.without_images),ensure_ascii=False,indent=2))
if __name__=="__main__": main()
