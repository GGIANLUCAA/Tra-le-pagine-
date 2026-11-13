#!/usr/bin/env python3
"""New 1910 emotional archival-film pilot: real source + one TRUE free I2I.
Never claim full 4+1, photoreal facial approval, verified Italian rights, or publication.
Never submit Vidu or charge a payment method. All generated media are OWNER REVIEW.
"""
from __future__ import annotations
import hashlib, importlib.util, json, math, os, pathlib, shutil, subprocess, sys, time, wave, zipfile
from urllib.parse import quote, urlencode, urlsplit
from urllib.request import Request, urlopen
import cv2
import numpy as np
from PIL import Image, ImageDraw
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/"output"/"storia_milk_1910_new_owner_review"
OUT.mkdir(parents=True,exist_ok=True)
FILENAME="All on account of the milk (1910).webm"
PAGE="https://commons.wikimedia.org/wiki/File:All_on_account_of_the_milk_(1910).webm"
USER_AGENT="LaStoriaRiviveOwnerReview/1.0 (+https://github.com/GGIANLUCAA/Tra-le-pagine-)"
def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1048576),b""):h.update(b)
    return h.hexdigest()
def log(name,d):
    (OUT/name).write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
def get_json(url):
    with urlopen(Request(url,headers={"User-Agent":USER_AGENT}),timeout=35) as r:
        return json.load(r)
def download_verified_source():
    # Wikimedia file is 598MB. Use existing 720p transcode; NEVER label it native 1080p.
    api="https://commons.wikimedia.org/w/api.php?"+urlencode({
      "action":"query","format":"json","formatversion":"2","titles":"File:"+FILENAME,
      "prop":"imageinfo","iiprop":"url|size|sha1|mime|extmetadata"})
    data=get_json(api)
    info=data["query"]["pages"][0]["imageinfo"][0]
    assert info["mime"].startswith("video/") and int(info["size"])>400_000_000
    original=info["url"]
    p=urlsplit(original)
    assert p.scheme=="https" and p.hostname=="upload.wikimedia.org"
    rel=p.path.split("/wikipedia/commons/",1)[1]
    basename=rel.rsplit("/",1)[-1]
    transcode="https://upload.wikimedia.org/wikipedia/commons/transcoded/"+rel+"/"+basename+".720p.vp9.webm"
    assert "upload.wikimedia.org"==urlsplit(transcode).hostname
    dest=OUT/"SOURCE_COMMONS_720P.webm"
    if not dest.is_file() or dest.stat().st_size<20_000_000:
        dest.unlink(missing_ok=True)
        with urlopen(Request(transcode,headers={"User-Agent":USER_AGENT}),timeout=110) as r, dest.open("wb") as f:
            while True:
                b=r.read(1<<20)
                if not b:break
                f.write(b)
                if f.tell()>250_000_000:raise ValueError("SOURCE_720P_TOO_LARGE")
    assert 20_000_000<dest.stat().st_size<250_000_000
    cap=cv2.VideoCapture(str(dest))
    w=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH));h=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps=float(cap.get(cv2.CAP_PROP_FPS));duration=float(cap.get(cv2.CAP_PROP_FRAME_COUNT))/fps if fps else 0
    cap.release()
    assert w>=900 and h>=680 and 900<duration<1050,(w,h,fps,duration)
    meta={"source":PAGE,"file":FILENAME,"original_commons_sha1":info["sha1"],
      "original_size_bytes":info["size"],"transcode_720p":transcode,"transcode_sha256":sha(dest),
      "actual_native_download_width":w,"actual_native_download_height":h,"duration_s":duration,
      "year":1910,"director":"Frank Powell (died 1946)",
      "rights":"Commons labels the film US public domain; Italian reuse and scan rights NOT independently certified",
      "owner_review_only":True,"actual_photo_approved":False,"vidu_clip_generated":False,
      "credits_spent":0,"published_to_social_or_site":False}
    log("SOURCE_QA.json",meta)
    return dest,meta
def choose_real_human_moment(video,meta):
    cap=cv2.VideoCapture(str(video))
    face=cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_frontalface_default.xml")
    profile=cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_profileface.xml")
    found=[]
    # Bounded scout of NEW film; choose recognizable close faces, not intertitles or 1px people.
    for sec in np.arange(22,min(750,meta["duration_s"]-22),9):
        cap.set(cv2.CAP_PROP_POS_MSEC,float(sec*1000))
        ok,f=cap.read()
        if not ok:continue
        tiny=cv2.resize(f,(400,300))
        g=cv2.cvtColor(tiny,cv2.COLOR_BGR2GRAY)
        g=cv2.equalizeHist(g)
        sharp=cv2.Laplacian(g,cv2.CV_64F).var()
        if sharp<14 or np.mean(g)<35 or np.mean(g)>225:continue
        faces=face.detectMultiScale(g,scaleFactor=1.08,minNeighbors=3,minSize=(33,33))
        sides=profile.detectMultiScale(g,scaleFactor=1.09,minNeighbors=3,minSize=(39,39))
        areas=sorted([int(w*h) for x,y,w,h in list(faces)+list(sides)],reverse=True)
        if not areas:continue
        score= min(sum(areas[:3])/900,100) + min(sharp,280)/30 + 2*len(areas)
        found.append({"time_s":float(sec),"face_sizes":areas[:4],"sharpness":round(sharp,1),"score":round(score,2)})
    cap.release()
    found.sort(key=lambda d:d["score"],reverse=True)
    log("HUMAN_FACE_SOURCE_SCOUT.json",{"candidate_count":len(found),"top":found[:14],"auto_review_only":True})
    if not found:raise RuntimeError("NO_ORIGINAL_CLOSE_FACES_VERIFIED__SOURCE_REJECTED")
    t=found[0]["time_s"]
    if max(found[0]["face_sizes"])<1700:raise RuntimeError("FACES_TOO_SMALL_FOR_MODERN_PHOTO")
    start=max(4,t-4.2)
    return start,t
def make_new_photo(base,original):
    import storia_cinema_magicien_1898_visual_social_v1 as m
    cv2.imwrite(str(OUT/"ANCHOR_REAL_ORIGINAL_BW.png"),original)
    cv2.imwrite(str(OUT/"ANCHOR_AI_NEURAL_COLOR_BASE.png"),base)
    report={"provider":"finegrain/finegrain-image-enhancer","real_free_I2I_created":False,
            "credit_or_payment_calls":0,"historical_identity_proven":False,"artistic_review":"PENDING",
            "source_frame_index":m.ANCHOR,"source_lock_same_frame":True}
    try:
        from gradio_client import Client,handle_file
        prompt=("Create an extraordinarily photorealistic, lifelike modern color documentary PHOTOGRAPH "
         "from this EXACT 1910 black-and-white film frame. Preserve every REAL person actually visible, "
         "each face shape, age appearance, gaze, smile, posture, wardrobe, hands, count of people and "
         "background geometry. Realistic skin pores and individual hairs, believable natural eyes, "
         "fine cotton clothing, physically consistent natural light and optics, precise 1910 setting. "
         "Some lost microdetail can be plausibly reconstructed but NEVER change identity or invent "
         "new people, clothes, facial expressions, body parts, background objects or inscriptions. "
         "Looks like a contemporary high-end documentary photograph, NOT colored vintage film.")
        negative=("extra people, different person, invented eyes, changed smile, double pupils, crossed eyes, "
         "porcelain skin, fake teeth, deformed faces, cartoon, oil painting, exaggerated lips, "
         "makeup, additional arms, mutated fingers, added children, new objects, modern clothing, "
         "plastic skin, anime, oversaturated orange, violet highlights, text artifacts")
        c=Client("finegrain/finegrain-image-enhancer",verbose=False)
        raw=c.predict(handle_file(str(OUT/"ANCHOR_AI_NEURAL_COLOR_BASE.png")),
          prompt,negative,1910,2,1.14,.97,6,112,144,.45,18,"DDIM",api_name="/process")
        obj=raw[1] if isinstance(raw,(list,tuple)) and len(raw)>1 else raw
        if isinstance(obj,dict):obj=obj.get("path")
        pic=cv2.imread(str(obj))
        if pic is None:raise RuntimeError("FREE_PROVIDER_DID_NOT_RETURN_IMAGE")
        pic=cv2.resize(pic,(960,720))
        c1,c2=m.corr(original,pic),m.corr(base,pic)
        sat=float(cv2.cvtColor(pic,cv2.COLOR_BGR2HSV)[:,:,1].mean())
        delta=float(np.mean(cv2.absdiff(pic,base)))
        report.update({"real_free_I2I_created":True,"corr_original":round(c1,4),
          "corr_base":round(c2,4),"saturation":round(sat,2),"changed_pixels_mean":round(delta,2)})
        cv2.imwrite(str(OUT/"GENERATIVE_PHOTO_REAL_CANDIDATE.png"),pic)
        if c1<.73 or c2<.8 or not(16<sat<135) or delta<1.8:
            raise ValueError("SOURCE_GEOMETRY_OR_COLOR_GATE_REJECTED")
        report["status"]="TRUE_PHOTOGRAPHIC_I2I_CANDIDATE_HUMAN_REVIEW_PENDING"
        log("PHOTO_QA.json",report)
        return pic
    except Exception as e:
        report["status"]="NOT_PRODUCED_OR_QA_FAIL"
        report["error"]=type(e).__name__+": "+str(e)[:260]
        log("PHOTO_QA.json",report)
        raise
def add_original_music_and_package(m,report,meta):
    v=m.MOVIE
    length=float(report["duration_s"])
    sr=22050
    t=np.arange(math.ceil(length*sr))/sr
    # Original unobtrusive sound design; no borrowed recording or tune.
    sound=np.zeros_like(t,dtype=np.float64)
    chords=[(196.,246.94,293.66),(174.61,220.,261.63),(164.81,196.,246.94)]
    for i in range(3):
        a=i*length/3;b=(i+1)*length/3
        mask=(t>=a)&(t<b)
        loc=t[mask]-a
        env=(1-np.exp(-np.maximum(loc,0)*2.4))*(1-np.exp(-(b-a-loc).clip(min=0)*3.0))
        for j,f in enumerate(chords[i]):
            sound[mask] += (.13/(j+1))*env*(np.sin(2*np.pi*f*loc)+.16*np.sin(2*np.pi*2*f*loc))
    sound=np.tanh(sound*1.5)
    fade=np.minimum(np.minimum(t/.6,(length-t)/1.2),1).clip(0,1)
    audio=(np.clip(sound*fade,-1,1)*32767).astype(np.int16)
    wav=OUT/"ORIGINAL_MUSIC.wav"
    with wave.open(str(wav),"wb") as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(audio.tobytes())
    dest=OUT/"VIDEO_WITH_ORIGINAL_MUSIC.mp4"
    m.run(["ffmpeg","-nostdin","-y","-v","error","-i",str(v),"-i",str(wav),
        "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","96k",
        "-t",str(length),"-movflags","+faststart",str(dest)],150)
    shutil.move(str(dest),str(v))
    m.run(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(v),"-f","null","-"],150)
    report.update({"sha256":sha(v),"bytes":v.stat().st_size,"original_music":True,
        "photo_count_generated":1,"vidu_clips_generated":0,
        "NOT_4_PLUS_1":True,"artistic_approval":False,"rights_italy_verified":False,
        "new_1910_film_subject":True})
    log("VISUAL_REPORT.json",report)
    text={
      "FACEBOOK":"ALL ON ACCOUNT OF THE MILK · 1910\nUn momento umano da un autentico film del 1910. La pellicola in movimento è originale; il colore e il fotogramma fotografico sono una ricostruzione AI interpretativa. Prova artistica non approvata.",
      "INSTAGRAM":"ALL ON ACCOUNT OF THE MILK · 1910\nUn gesto, uno sguardo, un volto ritrovato. Riprese storiche autentiche e ricostruzione moderna AI, non colore originale. Revisione artistica in corso.",
      "TIKTOK":"1910. Una persona vera davanti alla macchina da presa. Movimento autentico, ricostruzione fotografica AI interpretativa. Provino.",
      "YOUTUBE":"ALL ON ACCOUNT OF THE MILK · 1910 | A Face From Early Cinema\nFonte archivistica: "+PAGE+"\nFilm autentico; colori, dettagli, audio moderni ricostruiti, non documenti storici originali. Solo anteprima da revisionare."
    }
    for k,vv in text.items(): (OUT/("POST_"+k+".txt")).write_text(vv+"\n",encoding="utf8")
    (OUT/"README_REVIEW_ONLY.txt").write_text(
      "NEW 1910 source, 720p Commons transcode, one TRUE generative I2I photo, real moving original B/W before/after freeze, generated original audio. "
      "NOT full 4+1, no Vidu. Visual/artistic/Italy-rights review pending. Not approved to publish.\n"+PAGE+"\n")
    include=[m.MOVIE.name,"SOCIAL_COVER.jpg","ORIGINAL_VS_PHOTO_VISUAL_QA.jpg",
      "VISUAL_REPORT.json","SOURCE_QA.json","HUMAN_FACE_SOURCE_SCOUT.json","PHOTO_QA.json",
      "README_REVIEW_ONLY.txt","GENERATIVE_PHOTO_REAL_CANDIDATE.png","ANCHOR_REAL_ORIGINAL_BW.png"]+["POST_"+x+".txt" for x in text]
    with zipfile.ZipFile(m.ZIP,"w",zipfile.ZIP_DEFLATED,compresslevel=4) as z:
        for x in include:
            assert (OUT/x).is_file(),x
            z.write(OUT/x,arcname=x)
    with zipfile.ZipFile(m.ZIP) as z:assert z.testzip() is None
    log("DELIVERY.json",{"video_sha256":sha(m.MOVIE),"zip_sha256":sha(m.ZIP),
      "video_bytes":m.MOVIE.stat().st_size,"zip_crc_pass":True,
      "new_subject":"1910 All on Account of the Milk","new_video":True,"photo_count":1,
      "full_4plus1":False,"artistic_review":"PENDING","rights_italy":"PENDING",
      "vidu_posts":0,"paid_calls":0,"published":False})
def main():
    try:
        import storia_cinema_magicien_1898_visual_social_v1 as m
        src,meta=download_verified_source()
        start,selected_t=choose_real_human_moment(src,meta)
        m.OUT=OUT;m.SOURCE=src;m.CLIP=OUT/"REAL_SOURCE_EXCERPT_1910.mp4"
        m.MOVIE=OUT/"MILK_1910_NEW_PHOTO_REVIEW.mp4"
        m.ZIP=OUT/"MILK_1910_NEW_VIDEO_COVER_SOCIAL.zip"
        m.START=start;m.DURATION=17;m.ANCHOR=round(4.2*m.FPS)
        m.PAGE=PAGE
        m.run(["ffmpeg","-nostdin","-y","-v","error","-ss",str(start),"-i",str(src),
          "-t",str(m.DURATION),"-vf",f"fps={m.FPS},scale=960:720","-an",
          "-c:v","libx264","-preset","veryfast","-crf","18","-pix_fmt","yuv420p",str(m.CLIP)],260)
        old_canvas=m.frame_canvas
        def canvas(frame,title="",small=""):
            if "LE MAGICIEN" in title:title="ALL ON ACCOUNT OF THE MILK · 1910"
            if "MÉLIÈS" in small:small="AUTHENTIC 1910 MOVING FILM"
            return old_canvas(frame,title,small)
        m.frame_canvas=canvas
        original=m.readframe(m.ANCHOR)
        model,model_details=m.dd.download_model()
        log("COLOR_MODEL_QA.json",model_details)
        base=m.colorize(original,m.dd.infer_ab(model,original))
        picture=make_new_photo(base,original)
        report=m.export(picture,model)
        add_original_music_and_package(m,report,meta)
        print("REAL_NEW_1910_OWNER_REVIEW_VIDEO_CREATED",sha(m.MOVIE),flush=True)
    except Exception as e:
        log("FAILURE.json",{"status":"NO_NEW_VIDEO_DELIVERED",
          "reason":type(e).__name__+": "+str(e)[:400],
          "provider_cost":0,"vidu_posts":0,"video_not_approved":True})
        raise
if __name__=="__main__":main()
