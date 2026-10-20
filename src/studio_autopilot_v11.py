#!/usr/bin/env python3
"""Tra le Pagine — V11 autopilot PILOT for non-news narrative only.

Combines existing Gemini account key, licensed photo discovery from V7, original V5 render.
Never publishes: complete MP4 appears as private-ish (repository-access-controlled)
GitHub Actions artifact for manual Gate 2. Public repo run inputs are publicly visible.
Does not substitute drawings/placeholders for absent real imagery.
"""
from __future__ import annotations
import argparse
import io
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps
from archivio_media_v7 import discover, download_approved
from episode_v3 import validate

SENTENCE = re.compile(r"(?<=[.!?])\s+(?=[A-ZÀ-ÙÈÉ«“])")
ALLOWED_FORMATS = {"libri", "fiabe", "social"}
MIN_WORDS=230
MAX_WORDS=700


def split_phrases(text):
    return [s.strip() for s in SENTENCE.split(re.sub(r"\s+"," ",text)) if s.strip()]


def content_prompt(title,idea,kind,minutes):
    words={2:"270–340",3:"380–470",4:"500–600"}[minutes]
    return f"""Sei autore e regista per una breve narrazione originale italiana.
Formato {kind}. Titolo: {title}. Idea: {idea}.
Scrivi il parlato fluido, umano, naturale, senza formule robotiche, {words} parole.
Per ogni scena seleziona UNA frase d'inizio e descrivi un'immagine fotografica esistente,
realisticamente ricercabile in Wikimedia/Openverse. Deve raccontare davvero quel momento:
no clipart o immagini di luoghi inesistenti indicate come autentiche.
Le ricerche visuali in inglese devono usare termini generici concretamente fotografabili.
Non dichiarare immagini storiche documentate se non lo sono.
Consegna SOLO oggetto JSON:
{{
 "title":"Titolo italiano",
 "author":"Tra le Pagine",
 "narration":"Il racconto completo di 2-4 minuti, con almeno 18 frasi chiare.",
 "scenes":[
   {{"start_sentence":0,"description":"Descrizione italiana scena precisa","search":"english visual keyword 2-5 words"}},
   {{"start_sentence":3,"description":"...","search":"..."}}
 ]
}}
Vincoli: 8-12 scene con indici start_sentence interi crescenti e primo zero.
Niente discorsi sui tuoi limiti o titoli nel campo narration.
Non includere persone pubbliche immaginarie come testimonianze vere.
La storia deve usare una struttura chiara, un finale convincente, tono coinvolgente.
"""


def validate_story(data):
    if not isinstance(data,dict):
        raise ValueError("Gemini non ha restituito una storia JSON.")
    script=data.get("narration","")
    if not isinstance(script,str):
        raise ValueError("Copione non testuale.")
    words=len(script.split())
    if not MIN_WORDS<=words<=MAX_WORDS:
        raise ValueError(f"Copione {words} parole: necessario {MIN_WORDS}-{MAX_WORDS}.")
    phrases=split_phrases(script)
    scenes=data.get("scenes")
    if not isinstance(scenes,list) or not 8<=len(scenes)<=12:
        raise ValueError("Servono tra 8 e 12 scene, non un video senza storyboard.")
    starts=[x.get("start_sentence") if isinstance(x,dict) else None for x in scenes]
    if starts[0]!=0 or not all(isinstance(x,int) and 0<=x<len(phrases) for x in starts):
        raise ValueError("Indici frase fuori dal copione.")
    if any(a>=b for a,b in zip(starts,starts[1:])):
        raise ValueError("Scene non ordinate.")
    for i,s in enumerate(scenes):
        for key in ("description","search"):
            if not isinstance(s.get(key),str) or not 3<=len(s[key])<=150:
                raise ValueError(f"Scena {i+1}: mancano immagini ricercabili.")
    return {"words":words,"sentences":len(phrases),"scenes":len(scenes)}


def get_story(key,title,idea,kind,minutes,model="gemini-2.5-flash"):
    from google import genai
    client=genai.Client(api_key=key)
    r=client.models.generate_content(
        model=model,contents=content_prompt(title,idea,kind,minutes),
        config={"response_mime_type":"application/json","temperature":0.75}
    )
    if not getattr(r,"text",None):
        raise RuntimeError("Gemini non ha prodotto il copione.")
    data=json.loads(r.text)
    validate_story(data)
    return data


def crop_to_poster(im):
    im=ImageOps.exif_transpose(im).convert("RGB")
    if im.width<350 or im.height<350:
        raise ValueError("Immagine troppo piccola per video premium.")
    # Preserve subject by foreground fitting, with a blurred supporting background.
    target=(1080,1920)
    background=ImageOps.fit(im,target,method=Image.Resampling.LANCZOS)
    background=background.filter(ImageFilter.GaussianBlur(24))
    foreground=ImageOps.contain(im,(1080,1920),method=Image.Resampling.LANCZOS)
    x=(target[0]-foreground.width)//2
    y=(target[1]-foreground.height)//2
    background.paste(foreground,(x,y))
    return background


def find_photo(query,from_dir,scene_number,existing_hashes):
    """Fetch actual Wikimedia-based Openverse results; fail on missing matches."""
    queries=[query, " ".join(query.split()[:2])]
    for search in dict.fromkeys(queries):
        if len(search.strip())<2:continue
        entries=discover("openverse","image",search[:140],10)
        for item in entries:
            if item["license"] not in {"CC0","BY"}:
                continue
            try:
                with tempfile.TemporaryDirectory() as temp:
                    meta=download_approved(item,Path(temp))
                    sha=meta["sha256"]
                    if sha in existing_hashes:
                        continue
                    content=(Path(temp)/meta["file"]).read_bytes()
                    with Image.open(io.BytesIO(content)) as im:
                        result=crop_to_poster(im)
                        target=from_dir/f"scena_{scene_number:02d}.jpg"
                        result.save(target,quality=94,subsampling=0)
                        if target.stat().st_size<35_000:
                            target.unlink()
                            continue
                    existing_hashes.add(sha)
                    return {
                        "image":target.name, "title":item["title"],
                        "author":item["author"], "source":item["source_url"],
                        "license":item["license"],"license_url":item["license_url"],
                        "sha256":sha,"query":search
                    }
            except (ValueError,OSError,RuntimeError,TimeoutError):
                continue
    raise ValueError(
        f"Scena {scene_number}: nessuna foto Wikimedia verificabile per '{query}'. "
        "Mi fermo PRIMA della sintesi della voce, senza usare illustrazioni finte."
    )


def create_episode(repo,slug,title,idea,kind,minutes,model,key):
    if not re.fullmatch(r"auto_[0-9]{6,20}",slug):
        raise ValueError("Slug automatico deve provenire dall'ID di run GitHub.")
    if kind not in ALLOWED_FORMATS:
        raise ValueError("Autopilot V11 solo libri, fiabe o fiction social: cronaca e documentari richiedono fonti e approvazione.")
    if minutes not in (2,3,4):
        raise ValueError("Durata non valida.")
    if not 5<=len(title)<=110 or not 15<=len(idea)<=1600:
        raise ValueError("Titolo e descrizione fuori limite.")
    ep=repo/"episodes"/slug
    if ep.exists():raise ValueError("Cartella episodio già presente.")
    ep.mkdir(parents=True)
    img=ep/"images"
    img.mkdir()
    story=get_story(key,title,idea,kind,minutes,model)
    (ep/"testo.txt").write_text(story["narration"].strip()+"\n",encoding="utf-8")
    meta={"series":"Tra le Pagine", "episode":slug.replace("auto_",""),
          "title":title,"author":"Tra le Pagine (copione assistito da Gemini)",
          "voice":"gemini","format":kind,"approved_for_render":True}
    (ep/"metadata.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (ep/"DESCRIZIONE_SOCIAL.txt").write_text(
        title+"\nVideo narrato sperimentale. Materiale visivo illustrativo da Wikimedia Commons.\n",
        encoding="utf-8")
    cues=[]
    for n,scene in enumerate(story["scenes"],1):
        cues.append({"asset":n,"start_sentence":scene["start_sentence"],
                    "description":scene["description"]})
    (ep/"scene_cues.json").write_text(json.dumps(cues,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    provenance=[]
    seen=set()
    try:
        for n,scene in enumerate(story["scenes"],1):
            item=find_photo(scene["search"],img,n,seen)
            provenance.append(item)
    finally:
        (ep/"PROVENIENZA_FOTO.json").write_text(
            json.dumps(provenance,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        (ep/"COPIONE_E_STORYBOARD.json").write_text(
            json.dumps(story,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    # Original validator ensures no credits consumed for voice if images unavailable.
    import episode_v3
    episode_v3.ROOT=repo/"episodes"
    validate(slug)
    return ep


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--title",required=True)
    ap.add_argument("--idea",required=True)
    ap.add_argument("--format",choices=sorted(ALLOWED_FORMATS),default="libri")
    ap.add_argument("--minutes",type=int,choices=[2,3,4],default=3)
    ap.add_argument("--slug",required=True)
    ap.add_argument("--model",default="gemini-2.5-flash")
    ap.add_argument("--repo",default=".")
    args=ap.parse_args()
    key=os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("Chiave GEMINI_API_KEY assente. Configurala fra i GitHub Secrets.")
    ep=create_episode(Path(args.repo),args.slug,args.title,args.idea,
                      args.format,args.minutes,args.model,key)
    print("STORY + GENUINE PHOTO ASSETS READY:",ep)


if __name__=="__main__":
    main()
