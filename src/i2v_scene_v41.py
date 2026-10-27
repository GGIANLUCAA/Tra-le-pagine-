#!/usr/bin/env python3
"""V41 safe selection of one episode still frame from images/ or premium ZIP.

Nothing is downloaded or published. Used by the Android GitHub Actions entry.
"""
from __future__ import annotations
import argparse
import os
import re
from pathlib import Path
import zipfile

EXTS=(".jpg",".jpeg",".png",".webp")


def select(episode_slug:str, scene_number:int, out:Path)->Path:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,70}", episode_slug):
        raise ValueError("Nome episodio non valido")
    if type(scene_number) is not int or not 1<=scene_number<=35:
        raise ValueError("Numero scena: da 1 a 35")
    root=Path("episodes")/episode_slug
    if not root.is_dir():
        raise ValueError("Episodio non presente nel repository")
    name=f"scena_{scene_number:02}"
    candidates=[root/"images"/(name+e) for e in EXTS]
    found=[p for p in candidates if p.is_file()]
    if len(found)>1:
        raise ValueError("Più copie della stessa scena: scegliere un unico originale")
    out=Path(out)
    out.mkdir(parents=True,exist_ok=True)
    if found:
        candidate=found[0]
        size=candidate.stat().st_size
        if not 1000<=size<=9_500_000:raise ValueError("Immagine fuori limite")
        return candidate
    archive=root/"scene_premium.zip"
    if not archive.is_file():
        raise ValueError("La scena manca sia dalle immagini sia dal pacchetto premium")
    with zipfile.ZipFile(archive) as z:
        matches=[x for x in z.infolist() if not x.is_dir() and
                 Path(x.filename).name.lower() in {name+e for e in EXTS}]
        if len(matches)!=1:raise ValueError("Scena ZIP assente o ambigua")
        entry=matches[0]
        if not 1000<=entry.file_size<=9_500_000:
            raise ValueError("Dimensioni ZIP sospette")
        dest=out/Path(entry.filename).name
        if dest.exists():raise ValueError("Non sovrascrivere un file già presente")
        with z.open(entry) as source,dest.open("xb") as target:
            import shutil
            shutil.copyfileobj(source,target,length=1024*1024)
        return dest


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--episode",required=True)
    p.add_argument("--scene",type=int,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args()
    result=select(a.episode,a.scene,a.output_dir)
    print("Immagine selezionata:",result)
    if os.getenv("GITHUB_ENV"):
        with open(os.environ["GITHUB_ENV"],"a",encoding="utf-8") as f:
            f.write("I2V_SOURCE_IMAGE="+str(result)+"\n")


if __name__=="__main__":main()
