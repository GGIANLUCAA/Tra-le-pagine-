#!/usr/bin/env python3
"""Prompt pack per asset: suggerimenti senza richieste a servizi esterni."""
from __future__ import annotations
import json
from pathlib import Path

STYLES = {
    "libri": "cinema letterario pittorico, composizione di alta qualità, personaggi coerenti",
    "fiabe": "illustrazione d'autore raffinata, luce narrativa, mai stile clipart",
    "social": "immagine editoriale di grande impatto, composizione leggibile su telefono",
    "cronaca": "grafica editoriale illustrativa esplicitamente distinta dalle prove reali",
    "documentario": "illustrazione didattica sobria, mai falsa fotografia di prova",
}


def character_notes(ep: Path, text: str):
    source = ep / "personaggi.json"
    if not source.exists():
        return []
    data = json.loads(source.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("personaggi", [])
    if not isinstance(data, list):
        raise ValueError("personaggi.json deve contenere una lista o {personaggi: lista}.")
    notes = []
    for item in data:
        if not isinstance(item, dict):
            continue
        name = str(item.get("nome", "")).strip()
        if not name or name.casefold() not in text.casefold():
            continue
        description = str(item.get("caratteristiche", "")).strip()
        if description:
            notes.append({"nome": name, "caratteristiche": description})
    return notes


def build_prompts(report: dict, ep: Path) -> dict:
    mode = report["format"]
    if mode not in STYLES:
        raise ValueError("Formato sconosciuto.")
    seen = set()
    assets = []
    for scene in report["scenes"]:
        aid = scene["asset"]
        if aid in seen:
            continue
        seen.add(aid)
        desc = scene["description"]
        people = character_notes(ep, desc)
        character_string = "; ".join(
            p["nome"] + ": " + p["caratteristiche"] for p in people)
        if mode in ("cronaca", "documentario"):
            basis = (
                "RICOSTRUZIONE ILLUSTRATIVA, NON UN FILMATO AUTENTICO. "
                "Se la scena riguarda eventi o persone reali, non inventare documenti, "
                "date, testimoni, uniforme o loghi. Usare materiali di archivio autorizzati "
                "quando disponibili. Contesto richiesto: " + desc
            )
        else:
            basis = "Momento preciso della storia: " + desc
        assets.append({
            "asset": aid, "filename_suggerito": f"scena_{aid:02d}.png",
            "gia_presente": scene["asset_presente"],
            "generazione_necessaria": not scene["asset_presente"],
            "personaggi_rilevanti": people,
            "prompt": (
                basis + ". Stile: " + STYLES[mode] +
                (". Continuità personaggi: " + character_string if character_string else "") +
                ". Inquadratura verticale 9:16, 1080x1920 quando supportato; "
                "una scena unica, anatomia credibile, atmosfera coerente. "
                "Niente testo nell'immagine, niente collage, niente watermark. "
                "Titoli e indicazioni di ricostruzione in postproduzione."
            ),
            "controlli": [
                "Corrispondenza alla frase narrata", "Volti e mani corretti",
                "Ambientazione coerente", "Formato verticale",
                "Diritti e provenienza dell'immagine"
            ]
        })
    return {
        "version": "V6", "episodio": report["episodio"],
        "format": mode, "scene_distinte": len(report["scenes"]),
        "immagini_da_generare": sum(x["generazione_necessaria"] for x in assets),
        "asset": assets,
        "note": "Prompt predisposti. Nessuna immagine generata, nessun modello eseguito."
    }
