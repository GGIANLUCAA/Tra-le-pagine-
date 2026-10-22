#!/usr/bin/env python3
"""ArtVision Enigma V1: regia additiva per enigmi visivi in opere autentiche.
Riusa IDENTITA_VISIVA_FISSA_V6 (solo cover/intro), OpenCV, FFmpeg e fonti curate.
Non sostituisce GOLD MASTER Cinema V6, Critico V2 o voce Google e non pubblica.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
V6 = ROOT / "modules" / "artvision"
if str(V6) not in sys.path:
    sys.path.insert(0, str(V6))
from identita_visiva_v6 import cover as v6_cover, signature as v6_signature

KINDS = {"detail", "medium", "full_artwork", "iris_reveal", "portrait"}
MOVES = {"static", "push_in", "pull_out", "pan_left", "pan_right", "reveal"}
LICENSES = {"CC0", "PDM", "PUBLIC DOMAIN", "CC BY 4.0"}
def ease(x):
    x = float(np.clip(x, 0., 1.))
    return x*x*(3.0-2*x)

def validate(data):
    """Controlli basati su fonti e regia dichiarate; non certifica verita/licenze."""
    problems = []
    if data.get("schema") != "artvision-enigma-v1": problems.append("Schema non valido")
    if not data.get("id") or not data.get("artist") or not data.get("artwork"):
        problems.append("ID, artista e opera obbligatori")
    if not data.get("hook") or not data.get("resolution"):
        problems.append("Manca una domanda visiva o la rivelazione")
    if len(str(data.get("hook", ""))) > 170: problems.append("Hook troppo lungo")
    if not data.get("original_value"): problems.append("Manca contributo originale")
    if not data.get("fact_sources") or not all(str(s).startswith("https://") for s in data.get("fact_sources", [])):
        problems.append("Fonti dei fatti da verificare")
    art = data.get("source") or {}
    if not art.get("file_page", "").startswith("https://commons.wikimedia.org/wiki/File:"):
        problems.append("Pagina Wikimedia dell'opera obbligatoria")
    if str(art.get("license", "")).upper() not in LICENSES:
        problems.append("Licenza immagine non approvata: verificare")
    music = data.get("music") or {}
    if not all(music.get(k) for k in ("title", "artist", "source_url", "license_url", "license")):
        problems.append("Musica: provenienza/licenza incomplete")
    shots = data.get("shots") or []
    if not 6 <= len(shots) <= 16: problems.append("Richieste 6-16 inquadrature originali")
    if not any(s.get("kind") == "iris_reveal" for s in shots): problems.append("Manca la rivelazione")
    if shots and shots[0].get("kind") == "full_artwork": problems.append("Rivelazione mostrata nel primo shot")
    if shots and shots[-1].get("kind") != "full_artwork": problems.append("Finale senza quadro intero")
    runs = 0
    previous = None
    for i, s in enumerate(shots):
        if s.get("kind") not in KINDS or s.get("move") not in MOVES: problems.append(f"Shot {i+1}: tipo/movimento invalido")
        if not s.get("purpose"): problems.append(f"Shot {i+1}: manca ragione narrativa")
        f = s.get("focus")
        if not isinstance(f, list) or len(f) != 2 or not all(isinstance(x, (int, float)) and .07 <= x <= .93 for x in f):
            problems.append(f"Shot {i+1}: fuoco invalido")
        dur = s.get("seconds")
        if not isinstance(dur, (int,float)) or not 1.3 <= dur <= 9:
            problems.append(f"Shot {i+1}: durata invalida")
        if s.get("kind") == previous: runs += 1
        else: runs = 1
        previous = s.get("kind")
        if runs >= 4: problems.append("Quattro inquadrature consecutive identiche")
    duration = sum(float(s.get("seconds") or 0) for s in shots)
    if not 25 <= duration <= 65: problems.append("Durata consigliata 25-65 secondi")
    if not 1 <= sum(s.get("kind") == "iris_reveal" for s in shots) <= 2:
        problems.append("Usare solo 1-2 rivelazioni, non ripetere l'effetto")
    if problems: raise ValueError("; ".join(problems))
    return duration

def load_art(path: Path):
    with Image.open(path) as img:
        im = ImageOps.exif_transpose(img)
        if min(im.size) < 650: raise ValueError("Immagine museale troppo piccola (<650 px)")
        return cv2.cvtColor(np.asarray(im.convert("RGB")), cv2.COLOR_RGB2BGR)

def whole_art(src, width, height):
    h, w = src.shape[:2]
    bg = cv2.resize(src, (width, height), interpolation=cv2.INTER_AREA)
    bg = cv2.GaussianBlur(bg, (0,0), max(10, width/16))
    bg = cv2.addWeighted(bg, .31, np.zeros_like(bg), .69, 0)
    scale = min(width*.93/w, height*.91/h)
    nw, nh = int(w*scale), int(h*scale)
    artwork = cv2.resize(src, (nw,nh), interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_CUBIC)
    x,y = (width-nw)//2, (height-nh)//2
    cv2.rectangle(bg, (max(0,x-4), max(0,y-4)), (min(width-1,x+nw+4), min(height-1,y+nh+4)), (10,12,15), -1)
    bg[y:y+nh,x:x+nw] = artwork
    return bg

def crop(src, width, height, focus, zoom, shift=(0.,0.)):
    h,w = src.shape[:2]
    frame_ratio = width/height
    if w/h > frame_ratio: bw,bh = h*frame_ratio,h
    else: bw,bh = w,w/frame_ratio
    cw,ch = max(4,bw/zoom),max(4,bh/zoom)
    fx = max(cw/2, min(w-cw/2, (focus[0]+shift[0])*w))
    fy = max(ch/2, min(h-ch/2, (focus[1]+shift[1])*h))
    part = cv2.getRectSubPix(src, (max(4,int(cw)),max(4,int(ch))), (fx,fy))
    return cv2.resize(part,(width,height),interpolation=cv2.INTER_AREA if part.shape[1]>width else cv2.INTER_CUBIC)

def frame(src, shot, t, width, height, complete):
    p=ease(t)
    kind,move=shot["kind"],shot["move"]
    if kind=="full_artwork": return complete.copy()
    if kind=="portrait": base=1.04
    elif kind=="medium": base=1.16
    elif kind=="detail": base=1.62
    else: base=1.36
    offset=(0.,0.)
    if move=="push_in": base+=.20*p
    elif move=="pull_out": base+=.20*(1.-p)
    elif move=="pan_left": offset=(.055*(1-p)-.027,0.)
    elif move=="pan_right": offset=(.055*p-.027,0.)
    close = crop(src,width,height,shot["focus"],base,offset)
    if kind=="iris_reveal":
        # Un'unica rivelazione semicircolare elegante dal dettaglio alla tela.
        f = ease(max(0.,(t-.12)/.82))
        yy,xx=np.ogrid[:height,:width]
        radius=(.035+1.20*f)*math.hypot(width,height)
        mask=((xx-width*.5)**2+(yy-height*.48)**2<=radius**2).astype(np.uint8)*255
        mask=cv2.GaussianBlur(mask,(0,0),max(1,width/120))
        a=(mask.astype(np.float32)/255.)[:,:,None]
        return np.clip(a*complete+(1-a)*close,0,255).astype(np.uint8)
    return close

def beat_times(audio:Path, duration):
    """Il ritmo deriva dall'audio REALE, non da BPM inventati."""
    import librosa
    signal,sr=librosa.load(str(audio),sr=11025,mono=True,duration=duration)
    if signal.size==0 or np.max(np.abs(signal))<.001:
        raise ValueError("La traccia musicale e vuota o silenziosa")
    env=librosa.onset.onset_strength(y=signal,sr=sr,hop_length=256)
    cuts=librosa.onset.onset_detect(onset_envelope=env,sr=sr,hop_length=256,units="time")
    return [float(x) for x in cuts if .5 < float(x) < duration-.5]

def boundaries(shots, audio_onsets, duration):
    nominal=np.cumsum([s["seconds"] for s in shots]).tolist()[:-1]
    out=[0.]
    for index,n in enumerate(nominal):
        # Pochi aggiustamenti (max 180ms): il ritmo musicale segue la regia, non la domina.
        matches=[x for x in audio_onsets if abs(x-n)<.18 and x-out[-1]>1.15 and (duration-x)>1.2]
        chosen=min(matches,key=lambda x:abs(x-n)) if matches else n
        if chosen-out[-1]<1.15: chosen=n
        out.append(float(chosen))
    out.append(float(duration))
    return out

def ffprobe(file):
    return json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries",
        "format=duration,size:stream=codec_type,width,height","-of","json",str(file)],text=True))

def verify_scenes(path):
    """PySceneDetect usato davvero per confronto shot/cut, mai certificazione estetica."""
    from scenedetect import detect, ContentDetector
    found=detect(str(path), ContentDetector(threshold=32.0), show_progress=False)
    return [{"start_seconds":round(a.get_seconds(),2),"end_seconds":round(b.get_seconds(),2)} for a,b in found]

def reuse_editor_v19(data,out):
    """Applica VERAMENTE la skill V19 preesistente, senza modificarne le altre regie."""
    from src.artvision_editor_v19 import outputs
    m=data["music"]
    brief={"format":"artvision_enigma","artist":data["artist"],
      "music":{"title":m["title"],"composer":m["artist"],"source_url":m["source_url"],
               "license_url":m["license_url"],"edits":"Estratto, volume e dissolvenza"},
      "sources":[{"artwork":data["artwork"],"url":data["source"]["file_page"],
                  "reuse_terms":data["source"]["license"],
                  "attribution":data["source"].get("photo_credit","")}],
      "editorial":{"opening":data["hook"],"body":data["resolution"],
                   "fact_sources_checked":False,"hashtags":["#Arte","#ArtVision"]},
      "artistic_review_complete":False,
      "scenes":[{"artwork":data["artwork"],
                 "framing":"medium" if shot["kind"]=="iris_reveal" else shot["kind"],
                 "move":"detail_reveal" if shot["move"]=="reveal" else shot["move"],
                 "purpose":shot["purpose"],"visual_hook":bool(i==0)}
                for i,shot in enumerate(data["shots"])]}
    report,plan,caption,rights=outputs(brief)
    if report["blocking_issues"]:
        raise ValueError("Editor V19 blocca la produzione: "+"; ".join(report["blocking_issues"]))
    for name,value in [("EDITOR_REPORT_V19.json",json.dumps(report,ensure_ascii=False,indent=2)+"\n"),
                       ("DIRECTION_PLAN_V19.md",plan),
                       ("SOURCES_V19.md",rights)]:
        (out/name).write_text(value,encoding="utf8")
    return report

def make_contact_sheet(video, out, duration, *, count=10):
    """Dieci fotogrammi REALI in una JPG leggera da controllare da Android."""
    cap=cv2.VideoCapture(str(video))
    if not cap.isOpened(): raise RuntimeError("Impossibile aprire il master per la scheda scene")
    tiles=[]
    try:
        for t in np.linspace(.45,max(.55,duration-.45),count):
            cap.set(cv2.CAP_PROP_POS_MSEC,float(t)*1000)
            ok,img=cap.read()
            if not ok: raise RuntimeError("Frame di controllo mancante, timecode "+str(round(t,2)))
            small=cv2.resize(img,(192,342),interpolation=cv2.INTER_AREA)
            cv2.rectangle(small,(0,0),(80,27),(0,0,0),-1)
            cv2.putText(small,f"{t:.1f}s",(9,19),cv2.FONT_HERSHEY_SIMPLEX,.55,(255,255,255),1,cv2.LINE_AA)
            tiles.append(small)
    finally:cap.release()
    layout=np.vstack([np.hstack(tiles[:5]),np.hstack(tiles[5:])])
    if not cv2.imwrite(str(out),layout,[cv2.IMWRITE_JPEG_QUALITY,85]):
        raise RuntimeError("Salvataggio contact sheet fallito")
    return out

def render(data,image,music,out,width=1080,height=1920,fps=24,voice=None):
    seconds=validate(data)
    if width%2 or height%2 or width<240 or height<426 or fps not in (12,24,25,30):
        raise ValueError("Dimensioni pari >= 240x426, FPS 12/24/25/30")
    if not image.is_file() or not music.is_file(): raise FileNotFoundError("Mancano immagine o musica")
    out.mkdir(parents=True,exist_ok=True)
    reuse_editor_v19(data,out)
    src=load_art(image);whole=whole_art(src,width,height)
    onsets=beat_times(music,seconds)
    edges=boundaries(data["shots"],onsets,seconds)
    coverframe=crop(src,1080,1920,data["shots"][0]["focus"],1.15)
    cover=v6_cover(coverframe,data["artist"],data["music"]["artist"])
    cv2.imwrite(str(out/"COPERTINA.jpg"),cover,[cv2.IMWRITE_JPEG_QUALITY,92])
    dest=out/"ARTVISION_ENIGMA_V1.mp4"
    cmd=["ffmpeg","-hide_banner","-loglevel","error","-y",
        "-f","rawvideo","-pix_fmt","bgr24","-s",f"{width}x{height}","-r",str(fps),"-i","pipe:0",
        "-stream_loop","-1","-i",str(music)]
    if voice is not None:
        cmd+=["-i",str(voice)]
        filters="[1:a]volume=0.16[bg];[2:a]volume=1.0[narr];[bg][narr]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.90,afade=t=out:st="+str(max(0,seconds-1.5))+":d=1.5[mix]"
        cmd+=["-filter_complex",filters,"-map","0:v","-map","[mix]"]
    else: cmd+=["-map","0:v","-map","1:a","-af","afade=t=out:st="+str(max(0,seconds-1.5))+":d=1.5"]
    cmd+=["-t",str(seconds),"-c:v","libx264","-preset","veryfast","-crf","20",
          "-pix_fmt","yuv420p","-c:a","aac","-b:a","160k",
          "-movflags","+faststart","-shortest",str(dest)]
    # FFmpeg riceve frame da OpenCV; nessuna immagine generata o opera ridipinta.
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    count=round(seconds*fps)
    try:
        for n in range(count):
            t=n/fps
            k=min(len(data["shots"])-1,max(0,int(np.searchsorted(edges,t,side="right")-1)))
            shot=data["shots"][k]
            p=min(1.,max(0.,(t-edges[k])/max(.01,edges[k+1]-edges[k])))
            img=frame(src,shot,p,width,height,whole)
            if n<int(2.4*fps):
                # riuso preciso di copertina/intro V6, solo a risoluzione originale
                if (width,height)==(1080,1920):
                    img=v6_signature(img,t,data["artist"],data["music"]["artist"])
            proc.stdin.write(img.tobytes())
        proc.stdin.close();err=proc.stderr.read().decode("utf8",errors="replace")
        if proc.wait()!=0:raise RuntimeError("FFmpeg: "+err[-1000:])
    except Exception:
        if proc.stdin and not proc.stdin.closed: proc.stdin.close()
        proc.kill();proc.wait()
        dest.unlink(missing_ok=True)
        raise
    info=ffprobe(dest)
    types={x["codec_type"] for x in info["streams"]}
    if not {"video","audio"}.issubset(types): raise RuntimeError("MP4 senza audio/video")
    if abs(float(info["format"]["duration"])-seconds)>.6: raise RuntimeError("Durata video errata")
    cuts=verify_scenes(dest)
    sheet=make_contact_sheet(dest,out/"ANTEPRIMA_SCENE.jpg",seconds)
    report={"schema":"enigma-v1","id":data["id"],"seconds":seconds,
            "frame_count":count,"width":width,"height":height,"music_onsets":len(onsets),
            "cut_boundaries_seconds":[round(x,3) for x in edges],
            "detected_scenes":cuts,"review_contact_sheet":str(sheet.name),"original_editorial_value":data["original_value"],
            "visual_source":data["source"],"music_source":data["music"],
            "fact_sources":data["fact_sources"],
            "render_sha256":hashlib.sha256(dest.read_bytes()).hexdigest(),
            "technical_pass":True,"artistic_review_required":True,
            "rights_review_required":True,"published":False}
    (out/"REPORT_QA.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    (out/"STORYBOARD.json").write_text(json.dumps({"episode":data["id"],"hook":data["hook"],
        "resolution":data["resolution"],"timeline":data["shots"],
        "edges":edges},ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    (out/"DESCRIZIONE_SOCIAL.txt").write_text(data["social_caption"].strip()+"\n\n"+
        "Musica: "+data["music"]["title"]+" — "+data["music"]["artist"]+
        "\nFonte: "+data["music"]["source_url"]+"\nLicenza: "+data["music"]["license_url"]+
        "\nOpera: "+data["source"]["file_page"]+
        "\nMontaggio e taglio audio: ArtVision Enigma V1.\n",encoding="utf8")
    return dest

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--config",type=Path,required=True)
    p.add_argument("--image",type=Path)
    p.add_argument("--music",type=Path)
    p.add_argument("--out",type=Path,default=Path("output/enigma-v1"))
    p.add_argument("--width",type=int,default=1080)
    p.add_argument("--height",type=int,default=1920)
    p.add_argument("--fps",type=int,default=24)
    p.add_argument("--voice",type=Path)
    p.add_argument("--plan-only",action="store_true")
    a=p.parse_args()
    data=json.loads(a.config.read_text(encoding="utf8"))
    seconds=validate(data)
    if a.plan_only:
        print(json.dumps({"valid":True,"seconds":seconds,"id":data["id"],"scenes":len(data["shots"])},ensure_ascii=False))
        return
    if not a.image or not a.music: p.error("--image e --music necessari per render")
    path=render(data,a.image,a.music,a.out,a.width,a.height,a.fps,a.voice)
    print("MP4 REALMENTE RENDERIZZATO",path,flush=True)

if __name__=="__main__":main()
