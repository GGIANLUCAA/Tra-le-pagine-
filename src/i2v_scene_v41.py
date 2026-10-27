#!/usr/bin/env python3
"""V41 safe selection of one episode still frame from images/ or premium ZIP.

Nothing is downloaded or published. Used by the Android GitHub Actions entry.
"""
from __future__ import annotations
import argparse
import json
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



def narration_matches(episode_slug:str, scene_number:int)->dict:
    """Read the ACTUAL words at every cue using the requested picture.

    Does not claim semantic correctness: a repeated image can belong to
    several different story beats and must be reviewed by an editor.
    """
    root=Path("episodes")/episode_slug
    cuefile=root/"scene_cues.json"
    scriptfile=root/"testo.txt"
    if not cuefile.is_file() or not scriptfile.is_file():
        return {"status":"narration_or_cues_missing", "matches":[],
                "human_review_required":True}
    cues=json.loads(cuefile.read_text(encoding="utf-8"))
    if not isinstance(cues,list) or not cues:
        raise ValueError("Il file scene_cues.json non contiene scene")
    script=re.sub(r"\s+"," ",scriptfile.read_text(encoding="utf-8").strip())
    sentences=[v.strip() for v in re.split(r"(?<=[.!?])\s+(?=[A-ZÀ-ÙÈÉ«“])",script)
               if v.strip()]
    starts=[c["start_sentence"] for c in cues]
    if starts[0]!=0 or any(type(v) is not int or v<0 or v>=len(sentences) for v in starts):
        raise ValueError("Indici di narrazione non validi")
    if any(a>=b for a,b in zip(starts,starts[1:])):
        raise ValueError("Inizi scene fuori ordine")
    matching=[]
    for i,cue in enumerate(cues):
        if cue.get("asset")!=scene_number:
            continue
        begin=starts[i]
        stop=starts[i+1] if i+1<len(starts) else len(sentences)
        matching.append({
            "cue_index":i,
            "image_asset":scene_number,
            "visual_description":str(cue.get("description","")),
            "first_spoken_sentence":sentences[begin],
            "spoken_segment":" ".join(sentences[begin:stop]),
            "narration_alignment":"NEEDS_HUMAN_REVIEW",
        })
    return {"status":"review_required","matches":matching,
            "human_review_required":True,
            "note":"Confrontare il prompt con la frase, l'immagine e la continuità dei personaggi."}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--episode",required=True)
    p.add_argument("--scene",type=int,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args()
    result=select(a.episode,a.scene,a.output_dir)
    print("Immagine selezionata:",result)
    report=narration_matches(a.episode,a.scene)
    (a.output_dir/"SCENA_NARRAZIONE_V41.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Corrispondenze con la narrazione:",len(report["matches"]))
    if os.getenv("GITHUB_ENV"):
        with open(os.environ["GITHUB_ENV"],"a",encoding="utf-8") as f:
            f.write("I2V_SOURCE_IMAGE="+str(result)+"\n")


if __name__=="__main__":main()
