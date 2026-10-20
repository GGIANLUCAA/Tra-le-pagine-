#!/usr/bin/env python3
"""ARTVISION CINEMA V6 — lotto sperimentale di 3 artisti.
Nuovo motore additivo: NON modifica ne' sostituisce i film Van Gogh/Caravaggio.
Le opere provengono soltanto da collezioni museali marcate Public Domain/CC0.
"""
from __future__ import annotations
import argparse, hashlib, json, re, shutil, subprocess, sys
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from artvision import collect, download_pictures, norm
from atelier_v4 import audio_download, TRACKS
import director_cinema_v6 as cinema
from identita_visiva_v6 import signature, cover

ROOT=Path("output/artvision-batch-v6")
PROFILES={
 "monet":{
   "artist":"Claude Monet","duration":145,"key":["water lilies","nymph","japanese bridge","bridge","garden","haystack","impression","sunset","poplars","river","seine","landscape","spring","flowers","morning"],
   "arc":["Still water and reflected sky","Gardens and flower geometry","The changing face of daylight","Color dissolves solid forms","Return to water and light"],
   "music":"dreams_become_real","label":"Luce e riflessi"},
 "hokusai":{
   "artist":"Katsushika Hokusai","duration":140,"key":["great wave","wave","kanagawa","fuji","mount fuji","thirty-six views","red fuji","waterfall","bridge","storm","suruga","fishing","river","mountain","flower","eagle"],
   "arc":["The great ocean confronts us","Mount Fuji in the distance","Human figures against landscapes","Lines, wind and moving water","Return to the wave"],
   "music":"calmant","label":"La grande onda"},
 "rembrandt":{
   "artist":"Rembrandt van Rijn","duration":150,"key":["self-portrait","self portrait","portrait","young man","old man","woman","christ","simeon","biblical","saint","scholar","philosopher","mother","reading","light"],
   "arc":["A face appears from the darkness","Portraits and hands in warm light","Intimate scenes and human fragility","Theatrical contrast and sacred gesture","Return to the human gaze"],
   "music":"darkest_child","label":"La luce nell'ombra"},
}
MORE_MUSIC={
 "dreams_become_real":{
   "title":"Dreams Become Real","author":"Kevin MacLeod","isrc":"USUAN1500027",
   "page":"https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1500027",
   "urls":["https://incompetech.com/music/royalty-free/mp3-royaltyfree/Dreams%20Become%20Real.mp3"],
   "license":"CC BY 4.0","license_url":"https://creativecommons.org/licenses/by/4.0/",
   "expected_seconds":410,"instrumental":True},
 "darkest_child":{
   "title":"Darkest Child","author":"Kevin MacLeod","isrc":"USUAN1100783",
   "page":"https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100783",
   "urls":["https://incompetech.com/music/royalty-free/mp3-royaltyfree/Darkest%20Child.mp3"],
   "license":"CC BY 4.0","license_url":"https://creativecommons.org/licenses/by/4.0/",
   "expected_seconds":239,"instrumental":True},
 "calmant":TRACKS["calmant"],
}
PATTERNS=[
 ("portrait","texture","whole"),
 ("whole","portrait","texture"),
 ("glide","texture","portrait"),
 ("portrait","whole","texture"),
 ("texture","glide","whole"),
 ("whole","texture","portrait"),
]
def score(entry,keys):
    t=norm(entry.get("title",""))
    pts=0
    for k,word in enumerate(keys):
        if norm(word) in t:pts+=max(3,40-k*3)
    if any(s in t for s in ("verso","recto","untitled","study of","studies","cover of","catalogue")):pts-=18
    if entry.get("source")=="The Metropolitan Museum of Art":pts+=4
    return pts

def select_images(slug, config, folder):
    if slug=="monet":
        from monet_commons_sources_v6 import export as monet_commons_export
        return monet_commons_export(folder)
    collected,errs=collect(config["artist"],limit=100)
    if len(collected)<12:raise RuntimeError("Solo "+str(len(collected))+" opere museali per "+slug+": "+str(errs))
    # Keep high-interest works first, but spread museums: collect already round-robins sources.
    collected.sort(key=lambda item:score(item,config["key"]),reverse=True)
    unique=[];known=set()
    for item in collected:
        key=norm(item["title"])
        if key in known:continue
        known.add(key);unique.append(item)
    pictures,failed=download_pictures(unique,folder/"original_images",max_works=23)
    if len(pictures)<12:
        raise RuntimeError("Video bloccato: solo "+str(len(pictures))+" fotografie autorizzate. "+json.dumps(failed,ensure_ascii=False)[:500])
    # Preserve high-res museum masters when technically accessible, with graceful fallback.
    try:
        from universal_atelier_v5 import promote_museum_sources
        upgrades=promote_museum_sources(pictures[:7])
    except Exception as e:
        upgrades=[{"error":str(e)[:150]}]
    sufficient=[]
    for p in pictures:
        if min(p.get("width",0),p.get("height",0))<500:
            failed.append({"title":p["title"],"error":"Sorgente sotto 500 px, esclusa automaticamente"})
            print("LOW RES SKIP",p["title"],flush=True)
        else:
            sufficient.append(p)
    if len(sufficient)<12:
        raise RuntimeError("Solo "+str(len(sufficient))+" sorgenti sufficienti dopo il filtro Full HD")
    return sufficient,errs,failed,upgrades

def detail_foci(path):
    """Find two compositional high-information regions on the ACTUAL work.
    Optical cue suggestions only; no visual content generation or invented motifs."""
    raw=cv2.imread(str(path))
    if raw is None: return [(.5,.43),(.5,.6)]
    h,w=raw.shape[:2]
    small=cv2.resize(raw,(320,320),interpolation=cv2.INTER_AREA)
    gray=cv2.cvtColor(small,cv2.COLOR_BGR2GRAY)
    gx=cv2.Sobel(gray,cv2.CV_32F,1,0,ksize=3)
    gy=cv2.Sobel(gray,cv2.CV_32F,0,1,ksize=3)
    edges=cv2.GaussianBlur(cv2.magnitude(gx,gy),(0,0),11)
    cand=[]
    for y in range(3,9):
        for x in range(2,10):
            fx=(x+.5)/12;fy=(y+.5)/12
            y0=max(0,int((fy-.11)*320));y1=min(320,int((fy+.11)*320))
            x0=max(0,int((fx-.11)*320));x1=min(320,int((fx+.11)*320))
            patch=edges[y0:y1,x0:x1]
            if patch.size:
                rank=float(np.mean(patch))
                # Avoid over-selecting signature corners and borders.
                rank*=1-0.30*abs(fx-.5)
                cand.append((rank,fx,fy))
    cand.sort(reverse=True)
    one=(.5,.45)
    if cand:one=(round(cand[0][1],3),round(cand[0][2],3))
    second=next(((round(x,3),round(y,3)) for _,x,y in cand if abs(x-one[0])+abs(y-one[1])>.29),(.6,.65))
    return [one,second]

def build_shots(works,config):
    # Five-act dynamic structure with per-work visual cues and non-repeating motifs.
    # Variation avoids the old always-detail-then-whole slideshow.
    n=len(works)
    sequence=works[:]
    if n>=16:
        # An explicitly planned circular final act revisits the iconic opening motif.
        sequence=works[:16]+[works[1],works[4],works[0]]
    shots=[]
    for i,rec in enumerate(sequence):
        a,b=detail_foci(rec["file"])
        modes=PATTERNS[i%len(PATTERNS)]
        for j,mode in enumerate(modes):
            # A few complete works have just one held shot, letting the audience breathe.
            if j==2 and i in (4,9,14):continue
            f=(.5,.5) if mode=="whole" else (a if j%2==0 else b)
            why=(
              ("Full original composition, undistorted: " if mode=="whole" else
               "Genuine image detail suggested by composition: " if mode=="texture" else
               "Immersive movement on real artwork: ")+rec["title"])
            join="dissolve" if mode=="whole" and j==0 else ("match" if j and j%2 else "cut")
            length=(3.6 if mode=="whole" else (2.35 if mode=="texture" else 2.8))
            if i==len(sequence)-1 and j==len(modes)-1:length=4.0
            shots.append(cinema.Shot(len(shots),rec,mode,f,length,why,join))
    if len(shots)<42 or len({s.art["id"] for s in shots})<12:
        raise RuntimeError("Il lotto non supera la soglia minima V6 di regia/immagini")
    tot=sum(s.duration for s in shots)
    for s in shots:s.duration*=config["duration"]/tot
    return shots

def check_movie(movie,seconds):
    obj=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries",
              "format=duration,size:stream=codec_name,codec_type,width,height","-of","json",str(movie)]))
    assert abs(float(obj["format"]["duration"])-seconds)<2.0,obj
    video=next(s for s in obj["streams"] if s["codec_type"]=="video")
    assert (video["width"],video["height"])==(1080,1920),video
    assert {"audio","video"}<={s["codec_type"] for s in obj["streams"]}
    return obj

def run(slug):
    if slug not in PROFILES:raise ValueError(slug)
    cfg=PROFILES[slug];artist=cfg["artist"];sec=cfg["duration"]
    folder=ROOT/slug/"sources";folder.mkdir(parents=True,exist_ok=True)
    out=ROOT/slug/"film";out.mkdir(parents=True,exist_ok=True)
    pictures,errs,failed,upgrades=select_images(slug,cfg,folder)
    track=MORE_MUSIC[cfg["music"]]
    audio,rights=audio_download(track,folder,sec)
    audio.replace(folder/"licensed_piano_music.mp3")
    rights["full_attribution_required_in_public_description"]=True
    (folder/"music_rights.json").write_text(json.dumps(rights,indent=2,ensure_ascii=False),encoding="utf-8")
    (folder/"artworks.json").write_text(json.dumps({"artist":artist,"metadata":pictures,
      "source_errors":errs,"failed":failed,"print_upgrades":upgrades,
      "publication_approved":False},indent=2,ensure_ascii=False),encoding="utf-8")
    shots=build_shots(pictures,cfg)
    # Reuse exact unmodified V6 cinema engine and the SHARED locked identity.
    cinema.label_title=lambda img,t:signature(img,t,artist,track["author"])
    original,timeline=cinema.render(shots,folder,out,duration=sec)
    movie=out/("ARTVISION_"+slug.upper()+"_CINEMA_V6.mp4")
    original.replace(movie)
    cover_path=out/"COPERTINA.jpg"
    old_cover=out/"COPERTINA_CINEMA_V6.jpg"
    if old_cover.is_file():old_cover.replace(cover_path)
    spec=check_movie(movie,sec)
    (out/"silent_v6.mp4").unlink(missing_ok=True)  # keep only user-ready MP4
    used={s.art["id"] for s in shots}
    selected=[x for x in pictures if x["id"] in used]
    credits=[
     artist.upper()+" — ARTVISION CINEMA V6",
     "MUSIC: "+track["title"]+" — "+track["author"]+" (incompetech.com)",
     "CC BY 4.0 — https://creativecommons.org/licenses/by/4.0/",
     "Music: excerpt, volume adjustment, fade-in/fade-out.",
     "Source and music links: "+track["page"],
     "",
     "Original artworks and photographer/museum rights (verify before commercial reuse):"]
    credits += [x["title"]+" — "+x["source"]+" — "+x["url"]+" — "+x["license"] for x in selected]
    (out/"DESCRIZIONE_E_CREDITI.txt").write_text("\n".join(credits)+"\n",encoding="utf-8")
    (out/"FONTI_E_DIRITTI.json").write_text(json.dumps({
        "artist":artist,"artworks":selected,"music":rights,"publication_approved":False,
        "notice":"Controllare requisiti museali e diritto dei beni culturali italiani prima della monetizzazione"},
        indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"REPORT.json").write_text(json.dumps({
      "artist":artist,"style":"cinema_v6_batch_extension","graphic_identity":"IDENTITA_VISIVA_FISSA_V6.json",
      "duration_seconds":sec,"works":len(selected),"shots":len(shots),
      "soundtrack":track["title"],"format":spec,"paid_api":False,"published":False},
      indent=2,ensure_ascii=False),encoding="utf-8")
    print("BATCH-V6 COMPLETE",slug,len(selected),"works",len(shots),"directed shots",sec,"seconds",flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--artist",required=True,choices=sorted(PROFILES))
    arg=p.parse_args();run(arg.artist)
