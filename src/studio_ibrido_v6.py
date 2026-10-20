#!/usr/bin/env python3
"""Studio Ibrido V6: preproduzione separata dal renderer V5.
Nessuna rete, API, credenziale, download o modifica di episodi esistenti.
Il catalogo contiene candidati, NON prova di installazione/integrazione.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import zipfile
from pathlib import Path
from urllib.parse import urlparse
from prompt_asset_v6 import build_prompts

FORMATS = ("libri", "cronaca", "documentario", "fiabe", "social")
BUDGETS = ("zero", "basso")
MOTION = {
    "libri": "camera_lenta",
    "cronaca": "documenti_e_timeline",
    "documentario": "movimento_documentale",
    "fiabe": "parallasse_delicata",
    "social": "taglio_ritmico",
}
PORTRAIT_WORDS = ("volto", "ritratto", "primo piano", "guarda", "sorrid", "anziano")
LANDSCAPE_WORDS = ("fiume", "foresta", "paesaggio", "mare", "montagna", "città", "citta")
NO_AI_FACT_MODES = {"cronaca", "documentario"}


def read_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def asset_index(ep: Path):
    names = set()
    archive = ep / "scene_premium.zip"
    if archive.is_file():
        with zipfile.ZipFile(archive) as z:
            names.update(Path(x.filename).stem.lower()
                         for x in z.infolist() if not x.is_dir())
    folder = ep / "images"
    if folder.is_dir():
        names.update(p.stem.lower() for p in folder.iterdir() if p.is_file())
    return names


def source_report(ep: Path, mode: str):
    source_file = ep / "fonti.json"
    if not source_file.is_file():
        return {
            "status": "NON_RICHIESTE" if mode not in NO_AI_FACT_MODES else "FONTI_DA_AGGIUNGERE",
            "sources": 0, "independent_domains": 0,
            "note": "Nessuna verifica automatica della veridicità dei fatti."
        }
    data = read_json(source_file)
    if not isinstance(data, list):
        raise ValueError("fonti.json deve contenere una lista JSON.")
    domains = set()
    valid = 0
    for item in data:
        if not isinstance(item, dict):
            continue
        parsed = urlparse(str(item.get("url", "")))
        if parsed.scheme in ("http", "https") and parsed.netloc and str(item.get("titolo", "")).strip():
            valid += 1
            domains.add(parsed.netloc.lower().removeprefix("www."))
    status = "DA_VERIFICARE_A_MANO"
    if mode in NO_AI_FACT_MODES and len(domains) < 2:
        status = "FONTI_INSUFFICIENTI"
    return {
        "status": status, "sources": valid, "independent_domains": len(domains),
        "note": "Sono controllati URL e domini, non accuratezza, indipendenza editoriale o conferme."
    }


def scene_method(description: str, mode: str):
    d = description.casefold()
    if mode in NO_AI_FACT_MODES:
        return ("archivio_verificato_o_grafica_neutra",
                "Niente immagini AI presentate come documentazione di fatti reali.")
    if any(word in d for word in PORTRAIT_WORDS):
        return ("primo_piano_statico", "Proteggere anatomia, espressione e identità del volto.")
    if any(word in d for word in LANDSCAPE_WORDS):
        return ("panoramica_lenta", "Privilegiare ambiente e continuità visiva.")
    return (MOTION[mode], "Movimento minimo, solo se aiuta la comprensione.")


def build_plan(ep: Path, mode: str, budget: str, registry: dict):
    if mode not in FORMATS or budget not in BUDGETS:
        raise ValueError("Formato o budget non valido.")
    if not ep.is_dir():
        raise ValueError("Cartella episodio assente.")
    cues_path = ep / "scene_cues.json"
    if not cues_path.is_file():
        raise ValueError("Manca scene_cues.json: richiesto dal renderer attuale.")
    cues = read_json(cues_path)
    if not isinstance(cues, list) or not cues:
        raise ValueError("scene_cues.json vuoto o non valido.")
    ids = [t["id"] for t in registry["tools"]]
    if len(set(ids)) != len(ids):
        raise ValueError("Catalogo con ID duplicati.")
    by_id = {t["id"]: t for t in registry["tools"]}
    if not all(by_id[x]["enabled"] for x in ("ffmpeg", "gemini-tts")):
        raise ValueError("Impossibile conservare i motori base V5.")
    seen_assets = set()
    available = asset_index(ep)
    scenes = []
    previous_start = -1
    for i, cue in enumerate(cues):
        if not isinstance(cue, dict):
            raise ValueError("Cue non valido.")
        start, asset = cue.get("start_sentence"), cue.get("asset")
        if type(start) is not int or start <= previous_start:
            raise ValueError("start_sentence deve essere crescente e intero.")
        if type(asset) is not int or not 1 <= asset <= 999:
            raise ValueError("Asset numerico non valido.")
        previous_start = start
        desc = str(cue.get("description", "")).strip()
        if not desc:
            raise ValueError("Descrizione vuota per la scena.")
        method, caution = scene_method(desc, mode)
        assetname = f"scena_{asset:02d}"
        existing = assetname in available
        reused = asset in seen_assets
        seen_assets.add(asset)
        extras = []
        if mode not in NO_AI_FACT_MODES and budget == "basso":
            if any(w in desc.casefold() for w in PORTRAIT_WORDS):
                extras = ["liveportrait"]
            elif any(w in desc.casefold() for w in LANDSCAPE_WORDS):
                extras = ["wan2.2", "hunyuanvideo-1.5"]
            else:
                extras = ["z-image-turbo", "qwen-image"]
        scenes.append({
            "cue": i, "start_sentence": start, "asset": asset,
            "description": desc, "asset_name": assetname,
            "asset_presente": existing, "riutilizza_asset": reused,
            "regia_gratuita": method, "motivo": caution,
            "alternative_da_testare_non_attive": extras
        })
    sources = source_report(ep, mode)
    meta = read_json(ep / "metadata.json") if (ep / "metadata.json").is_file() else {}
    needs_sources = mode in NO_AI_FACT_MODES and sources["status"] in (
        "FONTI_DA_AGGIUNGERE", "FONTI_INSUFFICIENTI")
    return {
        "version": "V6", "episodio": ep.name,
        "title": str(meta.get("title", ep.name)),
        "format": mode, "budget": budget,
        "config_originale_intatta": True, "render_v5_modificato": False,
        "eseguiti_modelli_esterni": [], "consumo_crediti_api": 0,
        "costo_pianificazione_api_eur": 0, "costo_produzione_non_calcolato": True,
        "pubblicazione_automatica": False, "approvazione_umana_richiesta": True,
        "puo_passare_a_revisione_editoriale": not needs_sources,
        "stato_fonti": sources,
        "voce_attuale": "gemini-tts", "render_attuale": "ffmpeg",
        "scenes": scenes,
        "conteggi": {"inquadrature": len(scenes),
                    "immagini_distinte": len(seen_assets),
                    "asset_gia_presenti": sum(1 for a in seen_assets if f"scena_{a:02d}" in available),
                    "scene_con_asset_mancanti": sum(not x["asset_presente"] for x in scenes)},
        "regole": [
            "Non attivare strumenti GPU senza approvazione e verifica costo/licenze.",
            "Conservare la voce Gemini e il render V5 come impostazioni predefinite.",
            "Scene cronaca/documentario: distinguere immagini d'archivio, ricostruzioni, grafiche.",
            "Non pubblicare senza revisione umana dell'intero MP4."
        ]
    }


def storyboard_html(report):
    blocks = []
    for scene in report["scenes"]:
        status = "Disponibile" if scene["asset_presente"] else "Da produrre"
        reuse = " · Riutilizzato" if scene["riutilizza_asset"] else ""
        blocks.append(
            '<article><div class="eyebrow">INQUADRATURA %02d · FRASE %d</div>'
            '<h2>%s</h2><p><b>Asset:</b> %s (%s%s)</p>'
            '<p><b>Regia zero crediti:</b> %s</p><p>%s</p></article>' % (
                scene["cue"] + 1, scene["start_sentence"],
                html.escape(scene["description"]), html.escape(scene["asset_name"]),
                status, reuse, html.escape(scene["regia_gratuita"]), html.escape(scene["motivo"])
            )
        )
    title = html.escape(report["title"])
    source_warning = ""
    if not report["puo_passare_a_revisione_editoriale"]:
        source_warning = '<p class="warn">FONTI INSUFFICIENTI: non trasformare il progetto in cronaca pubblicabile.</p>'
    return ('''<!doctype html><html lang="it"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Studio Ibrido V6 - ''' + title + '''</title>
<style>
body{font-family:system-ui;background:#0c2330;color:#f6f1e6;margin:0;padding:24px;line-height:1.5}
main{max-width:1050px;margin:auto}h1{font-size:clamp(25px,6vw,42px)}
small,.eyebrow{color:#d1a96e}section{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:14px}
article{background:#173643;border:1px solid #41616a;border-radius:12px;padding:18px}
article h2{font-size:19px}p{font-size:14px}.warn{padding:13px;border-left:4px solid #f3b54a;background:#46351f}
</style><main><small>TRA LE PAGINE · STUDIO IBRIDO V6 · ANTEPRIMA</small>
<h1>''' + title + '''</h1>
<p>''' + html.escape(report["format"]) + ''' · budget ''' + html.escape(report["budget"]) +
''' · nessuna API invocata · nessun nuovo video generato</p>''' + source_warning +
'''<section>''' + "".join(blocks) + '''</section>
<p>Storyboard tecnico: serve ancora approvazione, verifica immagini, voce e fatti. Il video non è stato pubblicato.</p>
</main></html>''')


def run():
    ap = argparse.ArgumentParser(description="Pre-produzione V6: solo pianificazione, zero API.")
    ap.add_argument("--episode", required=True, help="Slug della cartella in episodes/")
    ap.add_argument("--format", choices=FORMATS, default="libri")
    ap.add_argument("--budget", choices=BUDGETS, default="zero")
    ap.add_argument("--out", default="output/studio_ibrido")
    args = ap.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,70}", args.episode):
        ap.error("Nome episodio non valido.")
    ep = Path("episodes") / args.episode
    registry = read_json(Path("config/studio_ibrido_tools.json"))
    report = build_plan(ep, args.format, args.budget, registry)
    dest = Path(args.out)
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "PIANO_SCENE_V6.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (dest / "STORYBOARD_V6.html").write_text(storyboard_html(report), encoding="utf-8")
    (dest / "PROMPT_IMMAGINI_V6.json").write_text(
        json.dumps(build_prompts(report, ep), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (dest / "CATALOGO_TOOLS_V6.json").write_text(
        json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"STUDIO IBRIDO V6: {report['conteggi']['inquadrature']} inquadrature.")
    print("Preproduzione soltanto. API: 0. Pubblicazioni: 0.")
    print(f"Output: {dest.resolve()}")
    if not report["puo_passare_a_revisione_editoriale"]:
        print("ATTENZIONE: fonti insufficienti, contenuto fattuale NON approvabile.")


if __name__ == "__main__":
    run()
