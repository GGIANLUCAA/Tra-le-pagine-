#!/usr/bin/env python3
"""Tra le Pagine V12 — narrative/visual scene review, entirely offline.

An image's semantic accuracy cannot be certified by comparing filenames and text.
This generates a per-scene speech-to-visual review; fail closed on mismatched
sentence anchors and missing images, mark semantic approval as HUMAN REVIEW.
It never changes the prior renderer, text or original files.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

SPLIT=re.compile(r"(?<=[.!?])\s+(?=[A-ZÀ-ÙÈÉ«“])")
IMAGES=(".jpg",".jpeg",".png",".webp")

def phrases(text):
    return [v.strip() for v in SPLIT.split(re.sub(r"\s+"," ",text.strip())) if v.strip()]

def scene_review(episode):
    ep=Path(episode)
    narration=(ep/"testo.txt").read_text(encoding="utf-8")
    cues=json.loads((ep/"scene_cues.json").read_text(encoding="utf-8"))
    items=phrases(narration)
    if len(items)<8 or len(cues)<8:
        raise ValueError("Copione o scene troppo brevi")
    starts=[c["start_sentence"] for c in cues]
    if starts[0]!=0 or any(not isinstance(i,int) or i<0 or i>=len(items) for i in starts):
        raise ValueError("Gli inizi delle scene non coincidono con le frasi narrate")
    if any(a>=b for a,b in zip(starts,starts[1:])):
        raise ValueError("Scene non ordinate")
    provenance={}
    for name in ("PROVENIENZA_FOTO.json","PROVENIENZA_IMMAGINI.json"):
        p=ep/name
        if p.exists():
            obj=json.loads(p.read_text(encoding="utf-8"))
            source=obj if isinstance(obj,list) else (obj.get("images") or [])
            # Both original episode metadata and Autopilot's image/source schema.
            for row in source:
                if not isinstance(row, dict):
                    continue
                value = row.get("asset")
                if value is None:
                    match = re.fullmatch(r"scena_(\d+)\.(?:jpg|jpeg|png|webp)",
                                         Path(str(row.get("image", ""))).name, re.I)
                    value = match.group(1) if match else None
                try:
                    asset_id = int(value)
                except (TypeError, ValueError):
                    continue
                provenance[asset_id] = {**row, "source_url": row.get("source_url") or row.get("source", "")}
            break
    report=[]
    for i,cue in enumerate(cues):
        n=int(cue.get("asset",0))
        if not 1<=n<=35:
            raise ValueError("ID immagine fuori intervallo")
        start=starts[i]
        end=starts[i+1] if i+1<len(starts) else len(items)
        voice=" ".join(items[start:end])
        if not voice.strip():
            raise ValueError("Inquadratura senza narrazione")
        anchor=cue.get("narration_anchor")
        if anchor is not None and anchor !=items[start]:
            raise ValueError(f"Scena {i+1}: inizio immagine NON coincide con la frase narrata")
        picture=next((ep/"images"/f"scena_{n:02}{suffix}"
                      for suffix in IMAGES
                      if (ep/"images"/f"scena_{n:02}{suffix}").is_file()),None)
        source=provenance.get(n,{})
        report.append({
            "scene":i+1,"asset":n,"sentence_start":start,"sentence_end":end-1,
            "exact_voice_segment":voice,
            "first_spoken_sentence":items[start],
            "visual_description":str(cue.get("description","")),
            "visual_search":str(cue.get("visual_search","")),
            "image_file":str(picture) if picture else "",
            "original_source":str(source.get("source_url","")),
            # Cannot verify visual truth from filenames/metadata.
            "semantic_alignment":"NEEDS_VISUAL_REVIEW"
        })
    return {"episode":ep.name,"total_phrases":len(items),
            "scene_count":len(report),"subtitle_policy":"DISABLED",
            "visuals_certified":False,"scenes":report}

def write_review(episode):
    ep=Path(episode)
    data=scene_review(ep)
    target=ep/"REGIA_NARRATIVA_V12.json"
    target.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    lines=["TRA LE PAGINE — V12 — VERIFICA SCENE PRIMA DEL MONTAGGIO",
           "Ogni riga mette in relazione il parlato vero con l'immagine prevista.",
           "IMPORTANTE: allineamento semantico immagini NON certificato automaticamente.",
           "Sottotitoli vietati in tutti i nuovi MP4.", ""]
    for s in data["scenes"]:
        lines.extend([
            f"SCENA {s['scene']:02} | FOTO {s['asset']:02} | FRASI {s['sentence_start']}–{s['sentence_end']}",
            "VOCE: "+s["exact_voice_segment"],
            "IMMAGINE: "+s["visual_description"],
            "CERCA: "+s["visual_search"],
            "FILE: "+(s["image_file"] or "(da completare prima del render)"),
            "FONTE: "+(s["original_source"] or "(non disponibile)"),
            "VERIFICA ARTISTICA: verificare visivamente che la foto mostri ciò che si racconta.",
            "",
        ])
    (ep/"REGIA_NARRATIVA_V12.txt").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print("REGIA V12:",len(data["scenes"]),"scene narrate, nessun sottotitolo.")
    return data

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--episode",required=True)
    args=p.parse_args()
    write_review(args.episode)
