#!/usr/bin/env python3
"""Renderer separato Controluce, riutilizza il motore Tra le Pagine invariato.

Il vecchio render.py crea un nome provvisorio TRA_LE_PAGINE_EP01.mp4,
che qui viene rinominato SOLO nella cartella d'output di Controluce.
"""
from __future__ import annotations
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
from controluce import validate_episode

ROOT=Path(__file__).resolve().parents[1]

def cover(source, title, target):
    image=ImageOps.fit(Image.open(source).convert("RGB"),(1080,1920),centering=(.5,.45))
    layer=Image.new("RGBA", image.size, (0,0,0,0))
    d=ImageDraw.Draw(layer)
    for y in range(1920):
        a = int(215 * ((y-1120)/800)**1.5) if y>=1120 else 0
        if a: d.line((0,y,1080,y), fill=(7,15,22,min(a,230)))
    fontpath="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    header=ImageFont.truetype(fontpath,45)
    title_font=ImageFont.truetype(fontpath,64)
    d.text((62,135),"CONTROLUCE",fill=(243,233,211,255),font=header,stroke_width=1,stroke_fill=(0,0,0,180))
    words=title.upper().split(); lines=[]; current=""
    for word in words:
        candidate=(current+" "+word).strip()
        if current and d.textbbox((0,0),candidate,font=title_font)[2]>950:
            lines.append(current);current=word
        else:current=candidate
    if current:lines.append(current)
    if len(lines)>4: raise ValueError("Titolo troppo lungo per la copertina")
    y=1580 - (len(lines)-1)*79
    for line in lines:
        d.text((63,y),line,font=title_font,fill=(255,252,243,255),stroke_width=2,stroke_fill=(8,15,20,255))
        y+=79
    Image.alpha_composite(image.convert("RGBA"),layer).convert("RGB").save(target,quality=92)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--episode",required=True,help="Cartella completa formats/controluce/episodes/...")
    p.add_argument("--engine",choices=["gemini","edge","espeak","supertonic","kokoro"],default="gemini")
    p.add_argument("--effects",choices=["off","v4"],default="v4")
    p.add_argument("--out",default="output_controluce/video")
    a=p.parse_args()
    ep=Path(a.episode).resolve(); output=Path(a.out).resolve()
    safe_root=(ROOT/"formats/controluce/episodes").resolve()
    if safe_root not in ep.parents: raise ValueError("Episodio fuori dalla cartella Controluce")
    validated=validate_episode(ep,require_images=True)
    output.mkdir(parents=True,exist_ok=True)
    subprocess.run([sys.executable,str(ROOT/"src/render.py"),"--episode",str(ep),
                    "--engine",a.engine,"--effects",a.effects,"--out",str(output)],
                   cwd=ROOT,check=True)
    interim=output/"TRA_LE_PAGINE_EP01.mp4"
    if not interim.is_file(): raise RuntimeError("Il render non ha restituito MP4")
    name="CONTROLUCE_"+validated["event_date"]+".mp4"
    if (output/name).exists(): raise FileExistsError("Output esistente; scegliere una nuova cartella")
    data=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries",
        "format=duration:stream=codec_type,width,height","-of","json",str(interim)],text=True))
    duration=float(data["format"]["duration"])
    if not 115<=duration<=210: raise ValueError(f"Durata {duration:.1f}s fuori intervallo editoriale")
    streams=data.get("streams",[])
    if not any(s.get("codec_type")=="audio" for s in streams):raise ValueError("Audio mancante")
    if not any(s.get("codec_type")=="video" and s.get("width")==720 and s.get("height")==1280 for s in streams):
        raise ValueError("Video non verticale 720x1280")
    if "ANTEPRIMA TECNICA" in (output/"STATO_IMMAGINI.txt").read_text(encoding="utf-8"):
        raise ValueError("Presenti immagini segnaposto")
    interim.rename(output/name)
    cover_source=output/"COPERTINA.jpg"
    cover(cover_source,validated["title"],output/"COPERTINA_CONTROLUCE.jpg")
    shutil.copy2(ep/"research.json",output/"FONTI_E_VERIFICA.json")
    shutil.copy2(ep/"asset_manifest.json",output/"DIRITTI_IMMAGINI.json")
    report={"format":"Controluce","approved_for_publication":False,
        "event_date":validated["event_date"],"title":validated["title"],
        "duration_seconds":duration,"video":name,"assets_rights_review":True,
        "notes":"Revisionare il risultato umano prima della pubblicazione. Nessuna pubblicazione automatica."}
    (output/"CONTROLLO_CONTROLUCE.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"MP4 prodotto: {output/name} ({duration:.1f} secondi)")
if __name__=="__main__":main()
