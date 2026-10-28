#!/usr/bin/env python3
"""V60 real archival colorization pilot. Downloads CC0 Wikimedia source & Apache DDColor model.
No Vidu, paid service, synthetic historical shots or automatic publication.
Requires: python3, numpy, opencv-python-headless, onnxruntime, pillow, huggingface_hub, ffmpeg.
"""
import hashlib
import io
import json
import math
import os
import subprocess
import sys
import wave
import zipfile
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import cv2
import numpy as np
import onnxruntime as ort
from PIL import Image, ImageDraw, ImageFont
from huggingface_hub import hf_hub_download

BASE=Path("output/storia_rivive_v60_beirut")
BASE.mkdir(parents=True, exist_ok=True)
SOURCE_NAME="File:Scènes de rue - AI13347.webm"
SOURCE_PAGE="https://commons.wikimedia.org/wiki/File:Sc%C3%A8nes_de_rue_-_AI13347.webm"
UA="TraLePagineStoriaRivive/0.6 (https://github.com/GGIANLUCAA/Tra-le-pagine-)"
SCENES=[("PORTO",80.0,4.4),("MERCATO",117.0,4.5),("STRADA",143.0,4.9)]
FPS=20
WIDTH,HEIGHT=720,1280

def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):
            h.update(block)
    return h.hexdigest()

def get_source():
    q=urlencode({"action":"query","format":"json","formatversion":"2","prop":"imageinfo",
                 "titles":SOURCE_NAME,"iiprop":"url|size|mime|extmetadata",
                 "iiextmetadatafilter":"LicenseShortName|LicenseUrl|Artist"})
    url="https://commons.wikimedia.org/w/api.php?"+q
    with urlopen(Request(url,headers={"User-Agent":UA}),timeout=45) as r:
        data=json.load(r)
    page=data["query"]["pages"][0]
    info=page["imageinfo"][0]
    metadata=info.get("extmetadata",{})
    license_name=metadata.get("LicenseShortName",{}).get("value","").strip()
    license_url=metadata.get("LicenseUrl",{}).get("value","")
    if "cc0" not in license_name.lower().replace(" ","") and "publicdomain/zero" not in license_url:
        raise ValueError("Fonte non CC0 secondo Wikimedia. Non procedere.")
    if not info["mime"].startswith("video/") or info["size"]>100000000:
        raise ValueError("Formato o dimensione fonte inaccettabili")
    dest=BASE/"FONTE_ORIGINALE.webm"
    if not dest.exists() or dest.stat().st_size!=info["size"]:
        with urlopen(Request(info["url"],headers={"User-Agent":UA}),timeout=120) as source, dest.open("wb") as out:
            while True:
                b=source.read(1048576)
                if not b:break
                out.write(b)
    if dest.stat().st_size!=info["size"]:
        raise ValueError("Fonte incompleta")
    return dest,{"page":SOURCE_PAGE,"filename":SOURCE_NAME,"source_sha256":sha(dest),
                 "archive":"Musée Albert-Kahn","artist":"Lucien Le Saint (attribution on archive page)",
                 "license_declared":license_name,"license_url":license_url,
                 "source_size_bytes":dest.stat().st_size,
                 "rights_status":"CC0 declared on exact Wikimedia page; residual rights require editorial verification"}

def download_model():
    repo="edgetools/ddcolor"
    filename="ddcolor-tiny-fp16.onnx"
    path=Path(hf_hub_download(repo_id=repo,filename=filename))
    if path.stat().st_size < 100_000_000:
        raise ValueError("ONNX checkpoint unexpectedly small")
    digest=sha(path)
    expected="2653da00dc15e54a45e5200b61dbf82ee9ceaf56b02bb9b9657569ac775e82e6"
    if digest!=expected:
        raise ValueError("ONNX fingerprint mismatch: "+digest)
    providers=["CPUExecutionProvider"]
    so=ort.SessionOptions()
    so.intra_op_num_threads=4
    so.inter_op_num_threads=1
    so.graph_optimization_level=ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    s=ort.InferenceSession(str(path),sess_options=so,providers=providers)
    return s,{"model_id":repo+"/"+filename,"sha256":digest,"license":"Apache-2.0 (model page)","provider":str(s.get_providers())}

def decoded_segment(original,sec,duration):
    cmd=["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-ss",str(sec),
         "-i",str(original),"-t",str(duration),"-vf",f"fps={FPS},scale=720:576",
         "-pix_fmt","bgr24","-f","rawvideo","-"]
    p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=90)
    if p.returncode:
        raise RuntimeError("Decodifica filmato: "+p.stderr.decode(errors="ignore")[:600])
    framebytes=720*576*3
    n=len(p.stdout)//framebytes
    if n<max(5,int(duration*FPS*.7)):
        raise RuntimeError("Troppi pochi fotogrammi reali nello spezzone")
    return np.frombuffer(p.stdout[:n*framebytes],dtype=np.uint8).reshape(n,576,720,3).copy()

def l_channel(frame):
    rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB).astype(np.float32)/255.0
    return cv2.cvtColor(rgb,cv2.COLOR_RGB2LAB)[:,:,0]

def infer_ab(session,frame):
    l=l_channel(frame)
    lr=cv2.resize(l,(512,512),interpolation=cv2.INTER_AREA)
    inp_lab=np.stack([lr,np.zeros_like(lr),np.zeros_like(lr)],axis=-1)
    gray_rgb=cv2.cvtColor(inp_lab.astype(np.float32),cv2.COLOR_LAB2RGB)
    model_input=np.transpose(gray_rgb,(2,0,1))[None].astype(np.float32)
    pred=session.run(None,{session.get_inputs()[0].name:model_input})[0]
    if tuple(pred.shape)!=(1,2,512,512):
        raise RuntimeError("Unexpected ONNX output: "+str(pred.shape))
    ab=np.transpose(pred[0],(1,2,0)).astype(np.float32)
    return cv2.resize(ab,(320,256),interpolation=cv2.INTER_LINEAR)

def warp_ab(current, anchor, ab):
    a=cv2.resize(cv2.cvtColor(anchor,cv2.COLOR_BGR2GRAY),(320,256))
    b=cv2.resize(cv2.cvtColor(current,cv2.COLOR_BGR2GRAY),(320,256))
    # Current -> anchor mapping for stable optical-flow chroma transfer
    flow=cv2.calcOpticalFlowFarneback(b,a,None,.5,3,13,3,5,1.1,0)
    yy,xx=np.mgrid[0:256,0:320].astype(np.float32)
    ab_new=cv2.remap(ab,xx+flow[:,:,0],yy+flow[:,:,1],cv2.INTER_LINEAR,
                     borderMode=cv2.BORDER_REFLECT_101)
    return ab_new

def image_at(frame,ab_small):
    L=l_channel(frame)
    ab=cv2.resize(ab_small,(720,576),interpolation=cv2.INTER_LINEAR)
    ab=np.clip(ab*1.13,-112,112)
    lab=np.dstack((L,ab)).astype(np.float32)
    rgb=cv2.cvtColor(lab,cv2.COLOR_LAB2RGB)
    bgr=cv2.cvtColor(np.clip(rgb*255,0,255).astype(np.uint8),cv2.COLOR_RGB2BGR)
    return bgr

def letter_frame(img, seconds, scene_name, scene_idx, colored):
    # Authentic frame; crop only center for 9:16; no AI synthesis of scene.
    h,w=img.shape[:2]
    cropw=int(h*9/16)
    x0=(w-cropw)//2
    if scene_idx==0:x0=min(x0+12,w-cropw)
    if scene_idx==1:x0=max(0,x0-28)
    img=img[:,x0:x0+cropw]
    img=cv2.resize(img,(WIDTH,HEIGHT),interpolation=cv2.INTER_CUBIC)
    pil=Image.fromarray(cv2.cvtColor(img,cv2.COLOR_BGR2RGB))
    d=ImageDraw.Draw(pil,"RGBA")
    # Soft shadow behind title, no large opaque graphic overlays.
    d.rectangle((0,0,WIDTH,155),fill=(0,0,0,92))
    try:
        title=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",44)
        small=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",25)
    except OSError:
        title=ImageFont.load_default();small=ImageFont.load_default()
    d.text((49,39),"BEIRUT  ·  1919",font=title,fill=(255,255,255,244),stroke_width=1,stroke_fill=(15,15,15,200))
    d.text((50,105),"UNA CITTÀ IN MOVIMENTO",font=small,fill=(230,221,202,230))
    if scene_idx>0 and .0<seconds<2.6:
        d.rounded_rectangle((44,HEIGHT-211,251,HEIGHT-155),radius=9,fill=(8,10,15,162))
        d.text((59,HEIGHT-197),scene_name,font=small,fill=(255,255,255,241))
    return cv2.cvtColor(np.asarray(pil.convert("RGB")),cv2.COLOR_RGB2BGR)

def audio(duration,path):
    sr=32000
    t=np.arange(int(duration*sr),dtype=np.float32)/sr
    # Original soft instrumental texture. No sampled copyrighted music.
    freqs=(110.0,164.81,220.0,261.63)
    sig=np.zeros_like(t)
    for i,f in enumerate(freqs):
        trem=.5+.5*np.sin(2*np.pi*(.08+i*.018)*t+i*.8)
        sig+=.10*np.sin(2*np.pi*f*t+i*.6)*trem
        sig+=.018*np.sin(2*np.pi*(f*2.0)*t+i*.2)
    for at in [0,4.4,8.9]:
        tt=t-at
        gate=(tt>=0)&(tt<.9)
        sig[gate]+=.13*np.sin(2*np.pi*(72*tt[gate]+80*tt[gate]**2))*np.exp(-7*tt[gate])
    sig*=np.minimum(1,t/1.1)*np.minimum(1,np.maximum(0,(duration-t)/1.3))
    sig=np.tanh(sig*1.8)
    samples=(np.clip(sig,-1,1)*22000).astype("<i2")
    with wave.open(str(path),"wb") as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(samples.tobytes())

def colorized_video(source,session):
    outfile=BASE/"VIDEO_COLOR_AI.mp4"
    wav=BASE/"AUDIO_ORIGINALE.wav"
    length=sum(x[2] for x in SCENES)
    audio(length,wav)
    tmp=BASE/"temp_video.mp4"
    cmd=["ffmpeg","-nostdin","-y","-loglevel","error","-f","rawvideo",
         "-pix_fmt","bgr24","-s",f"{WIDTH}x{HEIGHT}","-r",str(FPS),"-i","-",
         "-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p",
         "-movflags","+faststart",str(tmp)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    if not p.stdin:raise RuntimeError("ffmpeg stdin unavailable")
    global_frame=0
    cover_frame=None
    stats=[]
    for si,(label,start,dur) in enumerate(SCENES):
        frames=decoded_segment(source,start,dur)
        print("SCENE",si,label,"real frames",len(frames),flush=True)
        keyidx=sorted(set(list(range(0,len(frames),FPS)) + [len(frames)-1]))
        anchor_ab={}
        for idx in keyidx:
            anchor_ab[idx]=infer_ab(session,frames[idx])
        for fi,frame in enumerate(frames):
            prev=max(i for i in keyidx if i<=fi)
            nxt=min(i for i in keyidx if i>=fi)
            if fi==prev:
                ab=anchor_ab[prev]
            else:
                ab0=warp_ab(frame,frames[prev],anchor_ab[prev])
                if prev==nxt:ab=ab0
                else:
                    ab1=warp_ab(frame,frames[nxt],anchor_ab[nxt])
                    mix=(fi-prev)/(nxt-prev)
                    ab=ab0*(1-mix)+ab1*mix
            colored=image_at(frame,ab)
            if si==0:
                local=fi/FPS
                # first 1.2s original B/W, then reveal actual AI chroma within same source.
                reveal=np.clip((local-1.2)/1.55,0,1)
                # smoothstep
                reveal=reveal*reveal*(3-2*reveal)
                colored=cv2.addWeighted(frame,1-reveal,colored,reveal,0)
            tagged=letter_frame(colored,fi/FPS,label,si,si>0 or fi/FPS>=2.75)
            if (si==1 and fi==int(.65*FPS)):
                cover_frame=tagged.copy()
            if global_frame%27==0:
                sm=cv2.resize(tagged,(120,213))
                lab=cv2.cvtColor(sm,cv2.COLOR_BGR2LAB)
                stats.append({"sec":round(global_frame/FPS,2),"mean_lab_ab":list(np.mean(lab[:,:,1:],axis=(0,1)).round(2))})
            try:p.stdin.write(tagged.tobytes())
            except BrokenPipeError:raise RuntimeError("ffmpeg closed prematurely")
            global_frame+=1
    p.stdin.close()
    err=p.stderr.read()
    if p.wait()!=0:raise RuntimeError("Render ffmpeg failed "+err.decode(errors="ignore")[-1100:])
    if cover_frame is None:raise RuntimeError("No colorized cover")
    cv2.imwrite(str(BASE/"COVER.jpg"),cover_frame,[cv2.IMWRITE_JPEG_QUALITY,92])
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",str(tmp),"-i",str(wav),
                    "-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","120k",
                    "-shortest","-movflags","+faststart",str(outfile)],check=True,timeout=120)
    test=subprocess.run(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(outfile),
                         "-f","null","-"],capture_output=True,timeout=150)
    if test.returncode:raise RuntimeError("Final video corrupt: "+test.stderr.decode(errors="ignore")[-400:])
    return outfile,{"duration_seconds":round(global_frame/FPS,2),"scene_count":len(SCENES),
                   "model_inferences":sum(math.ceil(x[2]) + 1 for x in SCENES),
                   "video_sha256":sha(outfile),"color_observations":stats}

def package(video,source_info,model_info,render_info):
    claims={
     "title":"Beirut, 1919 — Una città in movimento",
     "video_status":"REAL_DDCOLOR_COLORIZED_PENDING_FINAL_ARTISTIC_ANDROID_AND_SITE_REVIEW",
     "format":"La Storia Rivive V59/V60", "original_is_real":"true",
     "historical_license":source_info, "ai_colorization":model_info,
     "disclosure":"Riprese d'archivio autentiche. Colori ricostruiti digitalmente tramite IA.",
     "shots":[{"topic":x[0],"start_in_original_seconds":x[1],"duration_seconds":x[2]} for x in SCENES],
     "music":"Composizione originale sintetizzata per questo video; non proviene dalla pellicola",
     "render":render_info,"vidu_credits_used":0,"social_auto_published":False,
     "archive_site_synced":False,"user_android_download_tested":False
    }
    (BASE/"FONTI_E_DIRITTI.json").write_text(json.dumps(claims,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    posts={
      "FACEBOOK":"Beirut, 1919. Una città pulsa fra il porto, il mercato e le strade: persone vere, gesti quotidiani, un tempo che sembrava lontanissimo. Queste riprese provengono dall'archivio del Musée Albert-Kahn e sono state colorizzate digitalmente con intelligenza artificiale: i colori sono ricostruiti, il movimento appartiene al film originale. Fonte: Musée Albert-Kahn / Wikimedia Commons (CC0). #Beirut #Storia #FilmatiDArchivio",
      "INSTAGRAM":"Non è una ricostruzione del movimento. È Beirut nel 1919, ripresa davvero. ⚓️ Dal porto al mercato, i colori sono stati immaginati dall'AI; le persone e i loro gesti arrivano dal film originale. 🎞️ Archivio Musée Albert-Kahn / Wikimedia Commons, CC0. #Beirut1919 #HistoryReels #Archivio #ColorizedHistory",
      "TIKTOK":"Beirut nel 1919, ma la guardi come se fosse ieri. Il porto, il mercato, le persone: sono riprese vere. I colori? Ricostruiti con AI, non originali del 1919. Fonte Musée Albert-Kahn, Wikimedia Commons CC0. #storia #beirut #archivio #colorizzazione",
      "YOUTUBE":"BEIRUT 1919 | Una città in movimento — Riprese autentiche restaurate e colorizzate\n\nUn breve viaggio attraverso tre scene realmente filmate a Beirut nel 1919: il porto, il mercato e la strada. La pellicola originale proviene dal Musée Albert-Kahn ed è disponibile su Wikimedia Commons con dichiarazione CC0. La colorizzazione è una ricostruzione digitale effettuata con DDColor: i colori non sono testimonianze cromatiche certe dell'epoca. La musica è stata composta per questa clip, non è un audio originale del filmato. Fonte: "+SOURCE_PAGE
    }
    for k,v in posts.items():
        (BASE/("POST_"+k+".txt")).write_text(v+"\n",encoding="utf8")
    (BASE/"README.txt").write_text("V60 VIDEO REALMENTE COLORIZZATO con modello AI DDColor-tiny (ONNX). La pellicola originale e' CC0 secondo Wikimedia Commons. Colori storici non documentati. MP4 H264/AAC; cover JPEG; quattro post; scheda di fonte. Il download Android e il sito privato non sono ancora verificati.\n",encoding="utf8")
    z=BASE/"BEIRUT_1919_COLORE_AI_COMPLETO.zip"
    with zipfile.ZipFile(z,"w",compression=zipfile.ZIP_DEFLATED) as arc:
        for name in ["VIDEO_COLOR_AI.mp4","COVER.jpg","FONTI_E_DIRITTI.json","README.txt",
                     "POST_FACEBOOK.txt","POST_INSTAGRAM.txt","POST_TIKTOK.txt","POST_YOUTUBE.txt"]:
            arc.write(BASE/name,arcname=name)
    with zipfile.ZipFile(z) as arc:
        if arc.testzip():raise RuntimeError("zip CRC test failed")
    print("DONE",json.dumps({"video":str(video),"zip":str(z),"bytes":video.stat().st_size,
                              "sha256":sha(video)},ensure_ascii=False),flush=True)

if __name__=="__main__":
    original,source_meta=get_source()
    print("SOURCE_READY",source_meta["source_size_bytes"],flush=True)
    session,model_meta=download_model()
    print("MODEL_READY",model_meta["model_id"],flush=True)
    movie,info=colorized_video(original,session)
    package(movie,source_meta,model_meta,info)
