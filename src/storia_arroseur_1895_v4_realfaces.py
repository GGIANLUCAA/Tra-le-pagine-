#!/usr/bin/env python3
"""V4 L'Arroseur arrose (1895) — source-pixel-safe restoration.
No generative still, no freeze frame, no geometric face changes, no paid API.
DDColor is used ONLY for a subdued chroma estimate; all luminance, faces,
hands, historical actors and original camera perspective stay original.
This is a RE-MASTER of a previously rejected episode, NOT a new episode.
"""
from __future__ import annotations
import os,sys,math,time,json,wave,hashlib,zipfile,subprocess,importlib.util
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
import storia_rivive_real_ai_v60 as dd
OUT=ROOT/"output"/"storia_cinema_1895_arroseur_v4"
OUT.mkdir(parents=True,exist_ok=True)
SRC=OUT/"LUMIERE_NATIVE_1895.webm"
TITLE="L'ARROSEUR ARROSÉ · 1895"
SOURCE_URL="https://commons.wikimedia.org/wiki/File:Le_Jardinier_(l%27Arroseur_arros%C3%A9)_(1895).webm"
SOURCE_SHA="aba9f6dd27cf1bd614989a6d0684f46f3a71f9bcaac6d4836022e2d4f2756b46"
START=8.0;SECS=26.0;FPS=24
W=960;H=720
def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for c in iter(lambda:f.read(1024*1024),b''):h.update(c)
    return h.hexdigest()
def write(name,payload):
    (OUT/name).write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
def cmd(args,timeout=260):
    p=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
    if p.returncode:
        raise RuntimeError("FAILED "+str(args[:8])+" "+p.stderr[-900:])
    return p.stdout
def fetch_source():
    from urllib.request import urlopen,Request
    from urllib.parse import urlencode,quote
    if SRC.is_file() and sha(SRC)==SOURCE_SHA:return
    if SRC.is_file():SRC.unlink()
    title="File:Le Jardinier (l'Arroseur arrosé) (1895).webm"
    q="https://commons.wikimedia.org/w/api.php?"+urlencode({"action":"query","prop":"imageinfo","titles":title,"format":"json","formatversion":"2","iiprop":"url"})
    ua="LaStoriaRiviveCinema/4.0 (https://github.com/GGIANLUCAA/Tra-le-pagine-)"
    errors=[]
    urls=[]
    try:
        with urlopen(Request(q,headers={"User-Agent":ua}),timeout=35) as f:
            data=json.load(f)
        urls.append(data["query"]["pages"][0]["imageinfo"][0]["url"])
    except Exception as e:errors.append(str(e)[:180])
    urls.append("https://commons.wikimedia.org/wiki/Special:Redirect/file/"+quote(title[5:],safe=""))
    for url in urls:
        try:
            with urlopen(Request(url,headers={"User-Agent":ua}),timeout=100) as r, SRC.open("wb") as o:
                while True:
                    b=r.read(1<<20)
                    if not b:break
                    o.write(b)
                    if o.tell()>25_000_000:raise RuntimeError("EXCESSIVE_SOURCE_BYTES")
            if sha(SRC)==SOURCE_SHA:
                print("ORIGINAL_FILM_SOURCE_SHA256_VERIFIED",SRC.stat().st_size,flush=True)
                return
            errors.append("SHA_MISMATCH_"+sha(SRC))
        except Exception as e:errors.append(type(e).__name__+":"+str(e)[:180])
    raise RuntimeError("VERIFIED_NATIVE_SOURCE_NOT_AVAILABLE "+str(errors))
def preprocess():
    raw=OUT/"ORIGINAL_REAL_MOVEMENT_CLEAN.mp4"
    # Use the ENTIRE 4:3 frame to include BOTH actors. No synthetic pan or crop.
    # Denoising and soft deflicker only; no face hallucination, no warped geometry.
    cmd(["ffmpeg","-nostdin","-y","-v","error","-ss",str(START),"-i",str(SRC),
         "-t",str(SECS),"-vf",f"fps={FPS},scale={W}:{H}:flags=lanczos,hqdn3d=2.5:2.0:3.5:3.0,deflicker=s=5:mode=am,eq=contrast=1.065:brightness=0.003",
         "-an","-c:v","libx264","-crf","16","-preset","veryfast",
         "-pix_fmt","yuv420p",str(raw)],180)
    cap=cv2.VideoCapture(str(raw))
    n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    imgs=[]
    for i in range(n):
        ok,frame=cap.read()
        if not ok:break
        if frame.shape[:2]!=(H,W):raise RuntimeError("WRONG_NATIVE_ASPECT")
        imgs.append(frame)
    cap.release()
    if not 550<=len(imgs)<=660:raise RuntimeError("NOT_FULL_AUTHENTIC_MOTION")
    # Motion evidence: no fake still and semantic changes across at least 24 segments
    diffs=[float(np.mean(cv2.absdiff(cv2.resize(imgs[i],(160,120)),
                                     cv2.resize(imgs[i+12],(160,120)))))
           for i in range(0,len(imgs)-12,24)]
    if np.median(diffs)<2.0:raise RuntimeError("NOT_AUTHENTIC_MOVING_FILM")
    print("SOURCE_CLEAN_REAL_FRAMES",len(imgs),"MEDIAN_MOTION",round(float(np.median(diffs)),2),flush=True)
    return imgs
def estimate_chroma(session,images):
    n=len(images)
    anchors=sorted(set(list(range(0,n,48))+[n-1]))
    ab={}
    for idx in anchors:
        ab[idx]=dd.infer_ab(session,images[idx])
    print("NEURAL_CHROMA_ANCHORS",len(anchors),flush=True)
    return anchors,ab
def neutral_color(img,chromas):
    # CIE L is computed ONLY from the actual 1895 frame: cannot deform anatomy.
    rgb=cv2.cvtColor(img,cv2.COLOR_BGR2RGB).astype(np.float32)/255
    lab=cv2.cvtColor(rgb,cv2.COLOR_RGB2LAB)
    h,w=img.shape[:2]
    ab=cv2.resize(chromas,(w,h),interpolation=cv2.INTER_LINEAR)
    # Deliberately restrained chroma; no uncanny orange/magenta/violet skin.
    # DDColor's free semantic inference does NOT invent geometric pixels.
    ab=np.clip(ab*.56,[-15,-13],[14,19])
    # Low-strength environmental color prior (olive greens, natural warm earth)
    # to prevent implausible purple/pink foliage.
    yy=np.arange(h,dtype=np.float32)[:,None]
    a_prior=np.where(yy<h*.24,-6.0,np.where(yy<h*.76,-4.0,3.2))
    b_prior=np.where(yy<h*.24,9.5,np.where(yy<h*.76,8.0,8.7))
    lab[:,:,1]=np.clip(.82*ab[:,:,0]+.18*a_prior,-14,13)
    lab[:,:,2]=np.clip(.82*ab[:,:,1]+.18*b_prior,-11,18)
    # Chromatic shift only; luminance untouched, no still frames or altered faces.
    out=cv2.cvtColor(lab.astype(np.float32),cv2.COLOR_LAB2BGR)
    return np.clip(out*255,0,255).astype(np.uint8)
def sound(duration):
    sr=32000;n=round(sr*duration);t=np.arange(n,dtype=np.float32)/sr
    v=np.zeros(n,np.float32)
    # Fresh original acoustic-piano-like accompaniment, NOT a copied score.
    notes=(196.,246.94,293.66,392.)
    for j,f in enumerate(notes):
        ph=.19*j
        tone=np.sin(2*np.pi*f*t+ph)
        trem=(.48+.35*np.cos(2*np.pi*(.60+j*.11)*t))
        v+=.033*tone*trem
        v+=.004*np.sin(2*np.pi*f*2.00*t+ph*.8)
    for at in np.arange(.25,duration,1.0):
        z=t-at;sel=(z>=0)&(z<.33)
        v[sel]+=.012*np.sin(2*np.pi*180*z[sel])*np.exp(-15*z[sel])
    env=np.minimum(1,t/.8)*np.minimum(1,np.maximum(0,(duration-t)/.9))
    wav=OUT/"NEW_ORIGINAL_SILENT_FILM_SCORE.wav"
    with wave.open(str(wav),"wb") as wf:
        wf.setnchannels(1);wf.setsampwidth(2);wf.setframerate(sr)
        wf.writeframes(np.clip(v*env*18500,-32768,32767).astype("<i2").tobytes())
    return wav
def frameboard(images,samples):
    board=Image.new("RGB",(6*340,2*285),(16,18,22))
    d=ImageDraw.Draw(board)
    for row in range(2):
        for i,idx in enumerate(samples):
            frame=images[idx] if row==0 else images[len(images)+idx] if False else None
            # this helper is unused; actual before/after generated by render()
    return board
def render(images,session):
    n=len(images);anchors,chromas=estimate_chroma(session,images)
    encoded=OUT/"V4_REAL_MOVING_COLOR_ONLY.mp4"
    proc=subprocess.Popen(["ffmpeg","-nostdin","-y","-v","error",
        "-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(FPS),
        "-i","-","-an","-c:v","libx264","-preset","veryfast","-crf","17",
        "-pix_fmt","yuv420p","-movflags","+faststart",str(encoded)],
        stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    assert proc.stdin is not None
    board=Image.new("RGB",(6*320,2*274),(15,19,22))
    draw=ImageDraw.Draw(board)
    positions=[12,75,160,273,409,min(n-1,576)]
    motion=[];sats=[];structures=[]
    try:
        for i,frm in enumerate(images):
            upper=min((x for x in anchors if x>=i),default=anchors[-1])
            lower=max(x for x in anchors if x<=i)
            if upper==lower:labab=chromas[lower]
            else:
                aa=dd.warp_ab(frm,images[lower],chromas[lower])
                bb=dd.warp_ab(frm,images[upper],chromas[upper])
                t=(i-lower)/(upper-lower)
                labab=aa*(1-t)+bb*t
            col=neutral_color(frm,labab)
            tsec=i/FPS
            reveal=float(np.clip((tsec-.92)/1.35,0,1))
            reveal=reveal*reveal*(3-2*reveal)
            frame=cv2.addWeighted(frm,1-reveal,col,reveal,0)
            if i in positions:
                k=positions.index(i)
                for row,snapshot in ((0,frm),(1,frame)):
                    im=Image.fromarray(cv2.cvtColor(snapshot,cv2.COLOR_BGR2RGB)).resize((314,236))
                    board.paste(im,(k*320+3,row*274+25))
                    draw.text((k*320+6,row*274+5),
                        ("ORIGINAL CLEAN " if row==0 else "MOVING REMASTER ")+f"{tsec:.1f}s",fill="white")
            if i%48==0:
                sats.append(float(cv2.cvtColor(col,cv2.COLOR_BGR2HSV)[:,:,1].mean()))
                a=cv2.cvtColor(cv2.resize(frm,(240,180)),cv2.COLOR_BGR2GRAY).astype(np.float32)
                b=cv2.cvtColor(cv2.resize(col,(240,180)),cv2.COLOR_BGR2GRAY).astype(np.float32)
                structures.append(float(np.corrcoef(a.ravel(),b.ravel())[0,1]))
            if i%12==0 and i>=12:
                diff=np.mean(cv2.absdiff(cv2.resize(images[i-12],(160,120)),
                                          cv2.resize(frm,(160,120))))
                motion.append(float(diff))
            proc.stdin.write(frame.tobytes())
    finally:
        proc.stdin.close()
        err=proc.stderr.read().decode(errors="ignore")
        if proc.wait()!=0:raise RuntimeError("COLOR_REMASTER_RENDER_FAILED "+err[-700:])
    board.save(OUT/"FRAME_BY_FRAME_SOURCE_MATCH.jpg",quality=95)
    if np.median(structures)<.988:raise RuntimeError("COLOR_WARP_CHANGED_FACES_OR_SHAPES")
    if np.median(motion)<2.0:raise RuntimeError("TOO_MANY_FROZEN_FRAMES")
    if np.median(sats)>52:raise RuntimeError("UNNATURAL_COLOR_SATURATION")
    print("VISUAL_AUTOMATED_GATES_PASS","SOURCE_SIMILARITY",round(float(np.median(structures)),4),
          "COLOR_SATURATION",round(float(np.median(sats)),2),flush=True)
    return encoded,{"duration_s":n/FPS,"median_motion":float(np.median(motion)),
         "median_grayscale_structure_correlation":float(np.median(structures)),
         "color_saturation_median":float(np.median(sats)),
         "genuine_film_motion":True,"freeze_frame_inserted":False,
         "generative_photo_inserted":False,"face_geometry_changed":False,
         "camera_crop":"NO: entire historic 4:3 composition",
         "DDColor_only_estimates_chroma":True,
         "on_source_luminance_and_people_pixels":True,
         "visual_user_approval":"PENDING",
         "cost_credits":0,"vidu_generated":False,"social_published":False,"website_published":False}
def finish(encoded,metadata):
    d=metadata["duration_s"]
    audio=sound(d)
    full=OUT/"ARROSEUR_1895_V4_VOLTI_AUTENTICI.mp4"
    # Original geometric framing, 1440x1080 photo-real source structure.
    cmd(["ffmpeg","-nostdin","-y","-v","error","-i",str(encoded),"-i",str(audio),
         "-map","0:v","-map","1:a","-vf","scale=1440:1080:flags=lanczos,unsharp=5:5:0.28",
         "-c:v","libx264","-preset","veryfast","-crf","18","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","160k","-movflags","+faststart","-shortest",str(full)],220)
    # Vertical social file: entire original film in a photographic matte,
    # no misleading face crops or duplicated bodies.
    portrait=OUT/"ARROSEUR_1895_V4_VERTICALE_SOCIAL.mp4"
    filt="[0:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,boxblur=26:4[bg];[0:v]scale=720:540:flags=lanczos[fg];[bg][fg]overlay=0:(H-h)/2:shortest=1,format=yuv420p[out]"
    cmd(["ffmpeg","-nostdin","-y","-v","error","-i",str(full),"-filter_complex",filt,
         "-map","[out]","-map","0:a:0","-c:v","libx264","-preset","veryfast",
         "-crf","18","-c:a","copy","-movflags","+faststart",str(portrait)],200)
    for v in [full,portrait]:
        cmd(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(v),"-f","null","-"],240)
        if v.stat().st_size<3_000_000:raise RuntimeError("INCOMPLETE_MP4_"+v.name)
    cap=cv2.VideoCapture(str(full))
    cap.set(cv2.CAP_PROP_POS_MSEC,14000)
    ok,cover=cap.read();cap.release()
    if not ok:raise RuntimeError("NO_GENUINE_COVER")
    pil=Image.fromarray(cv2.cvtColor(cover,cv2.COLOR_BGR2RGB))
    d=ImageDraw.Draw(pil)
    try:f=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",54)
    except OSError:f=ImageFont.load_default()
    d.text((38,44),TITLE,fill=(244,236,217),font=f,
           stroke_width=3,stroke_fill=(12,13,16))
    pil.save(OUT/"ARROSEUR_1895_V4_COVER.jpg",quality=95)
    posts={
    "FACEBOOK":"L’ARROSEUR ARROSÉ · 1895 — Il primo scherzo del cinema torna a muoversi. Ripresa AUTENTICA dei Lumière, restaurata con riduzione della grana e colore interpretativo moderato. Zero facce sintetiche e zero fermo immagine. Wikimedia Commons, pubblico dominio.",
    "INSTAGRAM":"L’ARROSEUR ARROSÉ · 1895 🎬 Il giardiniere e il ragazzo dispettoso. Vera pellicola 1895, colori ricostruiti con moderazione. Nessun volto generato. #LaStoriaRivive #CinemaMuto",
    "TIKTOK":"1895. Uno scherzo con un tubo da giardino! Movimento originale e restauro senza facce finte. #StoriaDelCinema",
    "YOUTUBE":"L’ARROSEUR ARROSÉ · 1895 | Lumière · No-Freeze Authentic Film Restoration. Pellicola 1895 a 4:3 preservata, no AI generativa anatomica, solo de-flicker/de-noise e colore interpretativo. Fonte: "+SOURCE_URL}
    for platform,post in posts.items():
        (OUT/f"POST_{platform}.txt").write_text(post+"\n",encoding="utf8")
    metadata.update({"source_page":SOURCE_URL,"native_source_sha256":SOURCE_SHA,
                     "source_author":"Louis Lumière (died 1948)",
                     "public_domain_italy":True,"restoration_method":"source pixel preserving, restrained AI chroma, denoise, deflicker",
                     "landscape_master":full.name,"social_portrait":portrait.name,
                     "landscape_sha256":sha(full),"social_sha256":sha(portrait),
                     "technical_full_decode_pass":True})
    write("RESTAURO_V4_QA.json",metadata)
    files=[full,portrait,OUT/"ARROSEUR_1895_V4_COVER.jpg",
           OUT/"FRAME_BY_FRAME_SOURCE_MATCH.jpg",OUT/"RESTAURO_V4_QA.json"]+\
           [OUT/f"POST_{k}.txt" for k in posts]
    zp=OUT/"ARROSEUR_1895_V4_VIDEO_COMPLETO.zip"
    with zipfile.ZipFile(zp,"w",zipfile.ZIP_DEFLATED,compresslevel=5) as z:
        for path in files:z.write(path,path.name)
    with zipfile.ZipFile(zp) as z:assert z.testzip() is None
    delivery={"status":"V4_REAL_REMASTER_COMPLETE_ARTISTIC_REVIEW_PENDING",
              "full_mp4":full.name,"vertical_mp4":portrait.name,
              "zip":zp.name,"full_sha256":sha(full),
              "vertical_sha256":sha(portrait),"zip_sha256":sha(zp),
              "zip_crc":True,"MP4_decoded_full":True,
              "no_freeze_no_synthetic_face":True,"paid_credits":0,"published":False}
    write("DELIVERY_V4.json",delivery)
    print("V4_NEW_REMASTER_COMPLETED_VERIFIED",json.dumps(delivery),flush=True)
def main():
    try:
        fetch_source()
        images=preprocess()
        session,model=dd.download_model()
        write("ONNX_COLOR_MODEL.json",model)
        movie,metadata=render(images,session)
        finish(movie,metadata)
    except Exception as e:
        write("BLOCKER_V4.json",{"status":"NOT_APPROVED_NOT_DELIVERED","error":type(e).__name__+": "+str(e)[:550]})
        raise
if __name__=="__main__":main()
