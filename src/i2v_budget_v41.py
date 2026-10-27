#!/usr/bin/env python3
"""V41: optional Vidu Q2 Pro Fast I2V API, never spend without explicit submit.

plan: offline estimated cost + shot validation
submit: explicit --approve-charge YES, requires VIDU_API_KEY environment secret
collect: check previously submitted task, download video and ZIP immediately
Output is a trial, NOT a published/approved Tra le Pagine video.
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import urllib.request
import urllib.parse
import zipfile

API="https://api.vidu.com"
MODEL="viduq2-pro-fast"
ECONOMY_MODEL="viduq2-turbo"
PRESETS={"cinema720":(MODEL,"720p"),"economy540":(ECONOMY_MODEL,"540p")}
MIME={".png":"image/png",".jpg":"image/jpeg",".jpeg":"image/jpeg",".webp":"image/webp"}


def estimate(seconds=5, off_peak=True, preset="cinema720"):
    if preset not in PRESETS:
        raise ValueError("Profilo AI sconosciuto")
    if type(seconds) is not int or not 2<=seconds<=10:
        raise ValueError("Durata I2V: scegliere 2-10 secondi")
    if preset=="economy540" and seconds>8:
        raise ValueError("Durata economia 540p: massimo 8 secondi")
    # Official Vidu Q2 pricing: initial second + two credits per later sec.
    first=6 if preset=="economy540" else 8
    base=first+2*(seconds-1)
    n=math.ceil(base/2) if off_peak else base
    return {"credits":n,"usd":round(n*0.005,4)}


def plan(image:Path,prompt:str,seconds:int=5,off_peak=True,max_cost_usd=0.10,preset="cinema720"):
    image=Path(image)
    if not image.is_file() or image.suffix.lower() not in MIME:
        raise ValueError("Immagine PNG/JPG/WebP obbligatoria")
    if not 1000<=image.stat().st_size<=9_500_000:
        raise ValueError("Immagine vuota o oltre 9.5 MB")
    if not isinstance(prompt,str) or not 30<=len(prompt.strip())<=2000:
        raise ValueError("Descrivere un'azione verificabile in almeno 30 caratteri")
    # Fail BEFORE submitting a paid generation if the picture is corrupt,
    # extremely narrow, or too small for acceptable cinematic output.
    from PIL import Image, UnidentifiedImageError
    try:
        with Image.open(image) as picture:
            width,height=picture.size
            picture.verify()
    except (OSError,UnidentifiedImageError,ValueError) as exc:
        raise ValueError("Immagine danneggiata o non decodificabile") from exc
    if min(width,height)<256 or max(width/height,height/width)>=4:
        raise ValueError("Immagine con risoluzione o proporzioni non idonee a I2V")
    quote=estimate(seconds,off_peak,preset)
    if max_cost_usd<=0 or quote["usd"]>max_cost_usd+1e-8:
        raise ValueError("La richiesta supera il tetto di spesa consentito")
    sha=hashlib.sha256(image.read_bytes()).hexdigest()
    fingerprint=hashlib.sha256(json.dumps(
        [sha,prompt,seconds,off_peak,preset],ensure_ascii=False).encode()).hexdigest()
    model,resolution=PRESETS[preset]
    return {"version":"v42","model":model,"provider":"vidu","preset":preset,
            "image":str(image),"image_sha256":sha,"prompt":prompt,
            "duration":seconds,"resolution":resolution,"off_peak":off_peak,
            "audio":False,"is_rec":False,"usd_estimated":quote["usd"],
            "credits_estimated":quote["credits"],"fingerprint":fingerprint,
            "status":"planned_not_submitted","review_required":True}


def _json_save(path,content):
    path.write_text(json.dumps(content,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def _api(method,path,key,payload=None):
    if not key:
        raise ValueError("Manca VIDU_API_KEY nei Secrets di GitHub")
    data=None if payload is None else json.dumps(payload).encode()
    req=urllib.request.Request(API+path,data=data,method=method,headers={
        "Authorization":"Token "+key,"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=35) as response:
        return json.loads(response.read(1048576))


def _payload(info):
    image=Path(info["image"])
    encoded=base64.b64encode(image.read_bytes()).decode("ascii")
    uri="data:"+MIME[image.suffix.lower()]+";base64,"+encoded
    # Q2 Turbo official endpoint specifies a one-item images array.
    # Keep legacy Pro Fast single-image payload until that endpoint is verified live.
    images=[uri] if info["model"]==ECONOMY_MODEL else uri
    return {"model":info["model"],"images":images,"prompt":info["prompt"],
            "duration":info["duration"],"resolution":info["resolution"],
            "off_peak":info["off_peak"],"audio":False,"is_rec":False}


def submit(info,out:Path,key:str):
    state=out/"VIDU_TASK.json"
    if state.exists():
        raise RuntimeError("Richiesta già registrata. Non duplicare chiamate pagate")
    # Reserve the ID locally BEFORE network I/O; even a network timeout may
    # mean a task was accepted. Resolve via Vidu console rather than resubmit.
    attempt={"status":"possibly_submitted_check_console",
             "fingerprint":info["fingerprint"]}
    _json_save(state,attempt)
    response=_api("POST","/ent/v2/img2video",key,_payload(info))
    task_id=response.get("task_id")
    if not isinstance(task_id,str) or not task_id:
        raise RuntimeError("POST senza task_id, verificare console prima di ripetere")
    attempt.update({"status":response.get("state","created"),
                    "task_id":task_id,"credits_reported":response.get("credits")})
    _json_save(state,attempt)
    return attempt


def collect(out:Path,key:str):
    state=out/"VIDU_TASK.json"
    record=json.loads(state.read_text(encoding="utf-8"))
    task_id=record.get("task_id","")
    if not isinstance(task_id,str) or not task_id or not all(
            c.isascii() and (c.isalnum() or c in "-_") for c in task_id):
        raise ValueError("ID task mancante: recuperarlo dalla console Vidu")
    result=_api("GET","/ent/v2/tasks/"+task_id+"/creations",key)
    record["status"]=result.get("state")
    if record["status"]=="success":
        entries=result.get("creations") or []
        url=entries[0].get("url") if entries else None
        if not isinstance(url,str) or urllib.parse.urlparse(url).scheme!="https":
            raise ValueError("Vidu non ha fornito URL HTTPS per il video")
        target=out/"I2V_V41_DA_REVISIONARE.mp4"
        if not target.exists():
            temp=out/"I2V_V41.part"
            try:
                with urllib.request.urlopen(url,timeout=90) as resp, temp.open("xb") as w:
                    total=0
                    while True:
                        chunk=resp.read(1048576)
                        if not chunk: break
                        total+=len(chunk)
                        if total>300_000_000:raise ValueError("Video oltre 300MB")
                        w.write(chunk)
                if total<20000:raise ValueError("MP4 troppo piccolo")
                probed=subprocess.run(["ffprobe","-v","error","-show_entries",
                    "format=duration:stream=codec_type","-of","json",str(temp)],
                    capture_output=True,text=True,check=True)
                media=json.loads(probed.stdout)
                if not any(x.get("codec_type")=="video" for x in media.get("streams",[])):
                    raise ValueError("Il file non contiene un video")
                temp.rename(target)
                with zipfile.ZipFile(out/"I2V_V41_ANDROID.zip","w",allowZip64=True) as z:
                    z.write(target,arcname=target.name,compress_type=zipfile.ZIP_STORED)
                with zipfile.ZipFile(out/"I2V_V41_ANDROID.zip") as z:
                    if z.testzip() is not None:raise ValueError("ZIP non valido")
                record["download_sha256"]=hashlib.sha256(target.read_bytes()).hexdigest()
                record["download_bytes"]=total
                record["actual_duration"]=float(media["format"]["duration"])
            finally:
                temp.unlink(missing_ok=True)
    _json_save(state,record)
    return record


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("action",choices=["plan","submit","collect"])
    ap.add_argument("--image",type=Path)
    ap.add_argument("--prompt")
    ap.add_argument("--seconds",type=int,default=5)
    ap.add_argument("--preset",choices=sorted(PRESETS),default="cinema720")
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--off-peak",action=argparse.BooleanOptionalAction,default=True)
    ap.add_argument("--max-cost-usd",type=float,default=.10)
    ap.add_argument("--approve-charge",default="NO")
    a=ap.parse_args()
    a.out.mkdir(parents=True,exist_ok=True)
    if a.action=="collect":
        result=collect(a.out,os.environ.get("VIDU_API_KEY",""))
    else:
        if a.image is None or a.prompt is None:
            ap.error("Immagine e prompt obbligatori")
        result=plan(a.image,a.prompt,a.seconds,a.off_peak,a.max_cost_usd,a.preset)
        if a.action=="submit":
            if a.approve_charge!="YES":ap.error("Serve --approve-charge YES")
            if not os.getenv("VIDU_API_KEY"):ap.error("VIDU_API_KEY non impostata")
        _json_save(a.out/"I2V_PLAN.json",result)
        if a.action=="submit":
            result=submit(result,a.out,os.environ["VIDU_API_KEY"])
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=="__main__":main()
