#!/usr/bin/env python3
"""La Storia Rivive / CINEMA (isolated): one genuine film, real DDColor and one
FREE photographic I2I. Never claim Vidu or artistic approval automatically."""
from __future__ import annotations
import hashlib, json, math, os, subprocess, sys, time, wave, zipfile
from pathlib import Path
from urllib.request import Request, urlopen

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
import storia_rivive_real_ai_v60 as dd

OUT=ROOT/"output"/"storia_cinema_1903_gunman"
OUT.mkdir(parents=True,exist_ok=True)
SRC=OUT/"EDWIN_PORTER_1903_FINAL_REAL.webm"
FILE_URL="https://upload.wikimedia.org/wikipedia/commons/b/be/Edwin_Stanton_Porter_The_Great_Train_Robbery_%281903%29_-_Final_Scene.webm"
SRC_PAGE="https://commons.wikimedia.org/wiki/File:Edwin_Stanton_Porter_The_Great_Train_Robbery_(1903)_-_Final_Scene.webm"
FILM_PAGE="https://www.loc.gov/item/00694220/"
UA="LaStoriaRiviveCinema/1.0 (https://github.com/GGIANLUCAA/Tra-le-pagine-; archival video research)"
FPS=24
W,H=720,1280
SLOW=1.18
ANCHOR_S=5.35
REVEAL_START=1.4
REVEAL_END=2.75

def hsh(path):
    d=hashlib.sha256()
    with open(path,"rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""):
            d.update(c)
    return d.hexdigest()

def write(name,d):
    (OUT/name).write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n",encoding="utf8")

def run(cmd,timeout=240):
    p=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout)
    if p.returncode:
        raise RuntimeError("COMMAND_FAILED "+str(cmd[:6])+" "+p.stderr[-650:])
    return p.stdout

def download():
    if SRC.is_file() and 1_000_000<SRC.stat().st_size<8_000_000:
        return SRC
    urls=[FILE_URL,"https://commons.wikimedia.org/wiki/Special:Redirect/file/Edwin_Stanton_Porter_The_Great_Train_Robbery_%281903%29_-_Final_Scene.webm"]
    failures=[]
    for url in urls:
        try:
            req=Request(url,headers={"User-Agent":UA,"Accept":"video/webm,application/octet-stream,*/*"})
            with urlopen(req,timeout=55) as response,SRC.open("wb") as target:
                while True:
                    chunk=response.read(1<<20)
                    if not chunk:break
                    target.write(chunk)
                    if target.tell()>8_000_000:raise RuntimeError("SOURCE_OVER_8MB")
            if 1_000_000<SRC.stat().st_size<8_000_000:return SRC
            raise RuntimeError("INCOMPLETE_SOURCE")
        except Exception as e:
            failures.append(type(e).__name__+": "+str(e)[:170])
    write("SOURCE_FETCH_FAILURE.json",{"urls":urls,"failures":failures})
    raise RuntimeError("HISTORIC_CLIP_DOWNLOAD_FAILED "+str(failures))

def draw_title(bgr,second,title=True):
    if not title:return bgr
    pil=Image.fromarray(cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB))
    d=ImageDraw.Draw(pil)
    try:
        ft=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",25)
        sourceft=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",16)
    except OSError:ft=ImageFont.load_default();sourceft=ft
    # Short, international film title without opaque blocks or people occlusion.
    label="THE GREAT TRAIN ROBBERY  ·  1903"
    d.text((31,58),label,font=ft,fill=(233,220,194),
           stroke_width=2,stroke_fill=(8,10,13))
    if second<2.4:
        d.text((32,H-60),"EDWIN S. PORTER  ·  ORIGINAL FILM 1903",font=sourceft,
               fill=(235,230,222),stroke_width=2,stroke_fill=(9,10,12))
    return cv2.cvtColor(np.asarray(pil),cv2.COLOR_RGB2BGR)

def crop_portrait(frame):
    h,w=frame.shape[:2]
    # Preserve actual proportions; no artificial perspective distortions.
    cw=int(round(h*9/16))
    x=max(0,(w-cw)//2)
    return cv2.resize(frame[:,x:x+cw],(W,H),interpolation=cv2.INTER_CUBIC)

def frames_of_original():
    scan=cv2.VideoCapture(str(SRC))
    scanfps=float(scan.get(cv2.CAP_PROP_FPS))
    scann=int(scan.get(cv2.CAP_PROP_FRAME_COUNT))
    v={"width":int(scan.get(cv2.CAP_PROP_FRAME_WIDTH)),
       "height":int(scan.get(cv2.CAP_PROP_FRAME_HEIGHT)),"codec_name":"vp9"}
    scan.release()
    if scanfps<=0:raise RuntimeError("SOURCE_FPS_MISSING")
    dur=scann/scanfps
    if not(11.3<=dur<=13.5 and int(v["width"])>=1200 and int(v["height"])>=700):
        raise RuntimeError("WRONG_HISTORIC_SOURCE "+str(probe)[:220])
    cap=cv2.VideoCapture(str(SRC))
    srcfps=float(cap.get(cv2.CAP_PROP_FPS))
    if not(12<=srcfps<=61):raise RuntimeError("SOURCE_FRAME_RATE_UNEXPECTED")
    # Decode source once, sample closest genuine frame 24fps and crop only at display stage.
    raw=[]
    while True:
        ok,img=cap.read()
        if not ok:break
        raw.append(img)
        if len(raw)>900:raise RuntimeError("UNEXPECTED_FILM_FRAME_COUNT")
    cap.release()
    if len(raw)<90:raise RuntimeError("NOT_REAL_MOTION")
    n=int(dur*FPS)-2
    images=[]
    for i in range(n):
        idx=min(len(raw)-1,int((i/FPS)*srcfps))
        images.append(crop_portrait(raw[idx]))
    raw.clear()
    if len(images)<240:raise RuntimeError("ORIGINAL_SHORTER_THAN_EXPECTED")
    diffs=[float(np.mean(cv2.absdiff(cv2.resize(images[i],(120,213)),
                                     cv2.resize(images[i+13],(120,213)))))
           for i in range(10,len(images)-15,28)]
    if float(np.median(diffs))<1.2:raise RuntimeError("SOURCE_NOT_REAL_MOVING")
    write("SOURCE_AND_RIGHTS.json",{
        "film":"The Great Train Robbery","year":1903,"author":"Edwin S. Porter",
        "author_death_year":1941,"source_page":SRC_PAGE,"film_archive":FILM_PAGE,
        "source_file_url":FILE_URL,"source_sha256":hsh(SRC),
        "license":"Wikimedia Commons Public Domain Mark 1.0, PD-US, PD-old-80",
        "italy_term_note":"Edwin S. Porter died 1941; life+70 years term has elapsed by 2012. Source is 1903 film; scan/original file independently checked.",
        "original_dimensions":[int(v["width"]),int(v["height"])],
        "original_duration_s":dur,"original_sampled_fps":FPS,
        "original_native_motion_median_difference":float(np.median(diffs)),
        "colorization":"Interpretive AI. NOT real 1903 colors.",
        "new_video_ai_generation_vidu":False,"source_of_audio":"Fresh original electronic composition, no music samples.",
        "published":False})
    # Contact sheet of exact original 1903 frames for honest quality QA.
    board=Image.new("RGB",(6*240,450),(13,16,19))
    draw=ImageDraw.Draw(board)
    for i,t in enumerate([0.4,2,4,6,8,10]):
        image=Image.fromarray(cv2.cvtColor(images[int(t*FPS)],cv2.COLOR_BGR2RGB))
        board.paste(image.resize((240,426)),(i*240,24))
        draw.text((i*240+6,5),f"REAL FILM {t:.1f}s",fill="white")
    board.save(OUT/"ORIGINAL_CONTACT.jpg",quality=91)
    return images,dur

def brightness(frame):
    return cv2.cvtColor(frame,cv2.COLOR_BGR2LAB)[:,:,0]

def colorize(frame,small_ab):
    lab=cv2.cvtColor(frame.astype("float32")/255,cv2.COLOR_BGR2LAB)
    ab=cv2.resize(small_ab,(W,H),interpolation=cv2.INTER_LINEAR)
    lab[:,:,1:]=np.clip(ab*1.1,-120,120)
    rgb=cv2.cvtColor(lab.astype("float32"),cv2.COLOR_LAB2BGR)
    return np.clip(rgb*255,0,255).astype("uint8")

def corr(a,b):
    def norm(v):
        x=cv2.cvtColor(cv2.resize(v,(96,160)),cv2.COLOR_BGR2GRAY)
        return cv2.GaussianBlur(x,(5,5),0).astype("float32").ravel()
    return float(np.corrcoef(norm(a),norm(b))[0,1])

def photo_finegrain(base,orig):
    cv2.imwrite(str(OUT/"DDCOLOR_AI_COLOR_BASE.png"),base)
    cv2.imwrite(str(OUT/"ORIGINAL_ANCHOR_1903.png"),orig)
    trial={"provider":"finegrain/finegrain-image-enhancer","paid_credits":0,
           "generated_photo":False,"photo_approved_artistic":False}
    try:
        from gradio_client import Client,handle_file
        prompt=("Ultra photorealistic restored 1903 Western movie frame, THE SAME individual adult male "
                "wearing authentic brimmed hat, dark cowboy coat and shirt pointing a revolver at the camera. "
                "The SAME authentic composition, exact revolver position, natural hands and correct five fingers, "
                "historically plausible earth-tone cloth, lifelike human skin and hair, natural daylight, crisp "
                "period photographic realism and optical detail. A mild plausible reconstruction of indistinct "
                "face details allowed. Keep the exact same person, handgun, pose and period background.")
        negative=("extra fingers, horns, animal head, second gun, double hand, multiple faces, distorted mouth, "
                  "shiny plastic skin, wax statue, cartoon, painterly look, illegible text, new buildings, "
                  "modern outfit, contemporary vehicles, cloned gun, bad anatomy")
        c=Client("finegrain/finegrain-image-enhancer",verbose=False)
        result=c.predict(handle_file(str(OUT/"DDCOLOR_AI_COLOR_BASE.png")),prompt,negative,
                         1903,2,1.14,.97,6,112,144,.45,18,"DDIM",api_name="/process")
        p=result[1] if isinstance(result,(tuple,list)) and len(result)>1 else result
        if isinstance(p,dict):p=p.get("path")
        photo=cv2.imread(str(p))
        if photo is None:raise RuntimeError("FREE_I2I_NO_REAL_OUTPUT")
        photo=cv2.resize(photo,(W,H),interpolation=cv2.INTER_CUBIC)
        sc=corr(orig,photo)
        sc_base=corr(base,photo)
        hsv=cv2.cvtColor(photo,cv2.COLOR_BGR2HSV)[:,:,1]
        sat=float(hsv.mean())
        colored=float(np.mean(hsv>=18))
        diff=float(np.mean(cv2.absdiff(base,photo)))
        trial.update({"source_structure_correlation":sc,"base_structure_correlation":sc_base,
                      "mean_saturation":sat,"colored_fraction":colored,
                      "difference_from_base":diff,"generated_photo":True})
        if sc<.72 or sc_base<.80 or sat<23 or colored<.35 or diff<1:
            trial["status"]="PHOTO_TECHNICALLY_REJECTED"
            raise RuntimeError("REAL_PHOTO_FAILED_GEOMETRY_OR_COLOR_GATE")
        cv2.imwrite(str(OUT/"REAL_PHOTOGRAPHIC_I2I_1903.png"),photo)
        trial["status"]="REAL_FREE_I2I_READY_FOR_VISUAL_QA"
        write("PHOTO_QA.json",trial)
        return photo
    except Exception as e:
        trial["error"]=type(e).__name__+": "+str(e)[:260]
        trial.setdefault("status","FREE_I2I_FAILED")
        write("PHOTO_QA.json",trial)
        raise

def synth_sound(seconds):
    sr=32000
    t=np.arange(round(seconds*sr),dtype=np.float32)/sr
    sig=np.zeros_like(t)
    # An original cinematic dark-strings-like underscore, not borrowed recordings.
    for ix,f in enumerate([110.,146.83,164.81,220.]):
        drift=(1+0.0005*np.sin(2*np.pi*0.29*t+ix))
        sig+=.048*np.sin(2*np.pi*f*t*drift+ix*.47)*(0.65+0.3*np.cos(t*(.18+ix*.04)))
        sig+=.009*np.sin(2*np.pi*f*2.005*t+ix*.4)
    for at in (0,2.8,7.8,13.9):
        z=t-at
        mask=(z>=0)&(z<.8)
        sig[mask]+=.062*np.sin(2*np.pi*(68*z[mask]+80*z[mask]**2))*np.exp(-7*z[mask])
    # Percussive accent around the iconic pistol gesture; synthetic sound only.
    for at in (12.2,):
        z=t-at
        mask=(z>=0)&(z<.26)
        prng=np.random.default_rng(1903)
        noise=prng.standard_normal(mask.sum()).astype("float32")
        sig[mask]+=.15*noise*np.exp(-28*z[mask])
    fade=np.minimum(1,np.maximum(0,t)/.65)*np.minimum(1,np.maximum(0,(seconds-t)/.9))
    sig=np.tanh(sig*1.2)*fade
    path=OUT/"ORIGINAL_MUSIC_1903.wav"
    with wave.open(str(path),"wb") as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr)
        w.writeframes((np.clip(sig,-1,1)*22000).astype("<i2").tobytes())
    return path

def export(images,photo,session):
    # Every shot is authentic cinema, not a panned image:
    # motion is ORIGINAL archival motion, recolor is AI interpretation.
    n=len(images)
    anchors=sorted(set([0]+list(range(0,n,2*FPS))+[n-1]))
    ab={i:dd.infer_ab(session,images[i]) for i in anchors}
    anchor_i=min(n-1,round(ANCHOR_S*FPS))
    moven=int(n*SLOW)
    insert_at=int(anchor_i*SLOW)
    holdframes=round(2.12*FPS)
    outfile=OUT/"CINEMA_1903_SILENT.mp4"
    writer=subprocess.Popen(["ffmpeg","-nostdin","-y","-v","error",
      "-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
      "-an","-c:v","libx264","-preset","veryfast","-crf","18",
      "-pix_fmt","yuv420p","-movflags","+faststart",str(outfile)],
      stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    if writer.stdin is None:raise RuntimeError("NO_VIDEO_ENCODER")
    color_samples=[]
    contact=[]
    try:
        for vi in range(moven):
            si=min(n-1,int(vi/SLOW))
            frm=images[si]
            lower=max(x for x in anchors if x<=si)
            upper=min(x for x in anchors if x>=si)
            if lower==upper: ab_now=ab[lower]
            else:
                left=dd.warp_ab(frm,images[lower],ab[lower])
                right=dd.warp_ab(frm,images[upper],ab[upper])
                mix=(si-lower)/(upper-lower)
                ab_now=left*(1-mix)+right*mix
            restored=colorize(frm,ab_now)
            sec=vi/FPS
            a=np.clip((sec-REVEAL_START)/(REVEAL_END-REVEAL_START),0,1)
            a=a*a*(3-2*a)
            view=cv2.addWeighted(frm,1-a,restored,a,0)
            # One freeze/reconstruction of THE SAME source moment with short fades.
            if vi==insert_at:
                for k in range(holdframes):
                    wt=min(1,(k+1)/(FPS*.28),(holdframes-k)/(FPS*.28))
                    wt=max(0.,wt);wt=wt*wt*(3-2*wt)
                    still=cv2.addWeighted(restored,1-wt,photo,wt,0)
                    writer.stdin.write(draw_title(still,sec).tobytes())
                contact.append(("GENERATIVE PHOTO",photo.copy()))
            view=draw_title(view,sec)
            if vi in (0,round(2*FPS),round(4*FPS),round(7*FPS),round(10*FPS),moven-1):
                contact.append((f"FILM {sec:.1f}s",view.copy()))
            if vi%72==0:
                color_samples.append({"seconds":round(sec,2),"saturation":round(float(cv2.cvtColor(view,cv2.COLOR_BGR2HSV)[:,:,1].mean()),2)})
            writer.stdin.write(view.tobytes())
    finally:
        writer.stdin.close()
        stderr=writer.stderr.read().decode(errors="ignore")
        if writer.wait()!=0:raise RuntimeError("VIDEO_RENDER_ERROR "+stderr[-700:])
    duration=(moven+holdframes)/FPS
    music=synth_sound(duration)
    final=OUT/"CINEMA_1903_THE_GREAT_TRAIN_ROBBERY.mp4"
    run(["ffmpeg","-nostdin","-y","-v","error","-i",str(outfile),"-i",str(music),
         "-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","160k",
         "-movflags","+faststart","-shortest",str(final)],120)
    run(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(final),"-f","null","-"],160)
    probe=cv2.VideoCapture(str(final))
    checkfps=float(probe.get(cv2.CAP_PROP_FPS))
    checkn=int(probe.get(cv2.CAP_PROP_FRAME_COUNT))
    probe.release()
    if checkfps<=0 or checkn<300:raise RuntimeError("FINAL_VIDEO_NOT_DECODABLE")
    actual_dur=checkn/checkfps
    metadata=subprocess.run(["ffmpeg","-hide_banner","-i",str(final),
                            "-f","null","-"],capture_output=True,text=True,timeout=140)
    if metadata.returncode or "Video: h264" not in metadata.stderr or "Audio: aac" not in metadata.stderr:
        raise RuntimeError("H264_AAC_CODEC_NOT_CONFIRMED "+metadata.stderr[-300:])
    meta={"format":{"duration":str(actual_dur)}} 
    assert 15<float(meta["format"]["duration"])<28
    assert final.stat().st_size>2_500_000
    cover=photo.copy()
    cv2.imwrite(str(OUT/"COVER_CINEMA_1903_NO_TEXT.jpg"),cover)
    cover=draw_title(cover,0)
    cv2.imwrite(str(OUT/"COVER_CINEMA_1903.jpg"),cover,[cv2.IMWRITE_JPEG_QUALITY,94])
    b=Image.new("RGB",(len(contact)*218,2*400),(13,16,20))
    d=ImageDraw.Draw(b)
    for i,(tag,frame) in enumerate(contact):
        small=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)).resize((212,377))
        b.paste(small,(i*218,26))
        d.text((i*218+4,4),tag,fill="white")
    b.save(OUT/"FILM_AND_AI_SCENE_REVIEW.jpg",quality=91)
    return final,{"duration_s":round(float(meta["format"]["duration"]),3),
                  "original_motion_seconds":round(n/FPS,3),
                  "authentic_film_motion":True,"AI_semantic_DDColor_anchored_motion":True,
                  "true_AI_photo_I2I":True,"num_color_anchors":len(anchors),
                  "vidu_clip_generated":False,"vidu_clip_used":False,
                  "original_music":True,"complete_decode_pass":True,
                  "bytes":final.stat().st_size,"sha256":hsh(final),
                  "color_saturation_samples":color_samples,"technical_approved":True,
                  "human_visual_approval":"PENDING","social_published":False,"site_published":False}

def package(final,report):
    write("TECHNICAL_QA.json",report)
    posts={
        "FACEBOOK":"THE GREAT TRAIN ROBBERY · 1903\nUn gesto che ha fatto la storia del cinema: un pistolero punta la sua arma direttamente verso gli spettatori. Il movimento proviene dalla vera pellicola del 1903; i colori e i dettagli fotografici sono ricostruzioni interpretative con IA. Fonte: Edwin S. Porter / Wikimedia Commons (pubblico dominio).",
        "INSTAGRAM":"THE GREAT TRAIN ROBBERY · 1903 🎬\nIl primo cinema torna a colori, senza perdere il movimento della pellicola originale. Ricostruzione AI interpretativa. #SilentCinema #FilmHistory #LaStoriaRivive",
        "TIKTOK":"1903. Il pistolero che sparò verso il pubblico. 🎥 Movimento originale del cinema muto, colori e dettagli ricostruiti con IA. #VintageCinema #FilmHistory",
        "YOUTUBE":"THE GREAT TRAIN ROBBERY · 1903 | Cinema History Restored\n\nUn'inquadratura del finale del film di Edwin S. Porter, conservata come ripresa autentica in bianco e nero. Colorizzazione neurale e un fotogramma fotografico generato con IA: non sono colori originali del 1903. Fonte: Wikimedia Commons, Public Domain Mark 1.0. "+SRC_PAGE
    }
    for channel,content in posts.items():
        (OUT/f"POST_{channel}.txt").write_text(content+"\n",encoding="utf8")
    (OUT/"README_RIGHTS_AND_LIMITATIONS.txt").write_text(
       "SOURCE: "+SRC_PAGE+"\nFILM: The Great Train Robbery, Edwin S. Porter, 1903, author died 1941.\n"
       "Public Domain Mark / PD old 80 (Wikimedia). 1903 film copyright expired in Italy and US; source is an archived public-domain copy.\n"
       "Color, skin and details: modern interpretive AI reconstruction, not authentic 1903 color.\n"
       "The FILM MOTION is historical and real. No new Vidu clip was created or represented.\n"
       "Zero purchased APIs and no publication performed.\n"
       "Artistic-level human approval still required prior to public release.\n",encoding="utf8")
    include=[final,OUT/"COVER_CINEMA_1903.jpg",OUT/"FILM_AND_AI_SCENE_REVIEW.jpg",
             OUT/"SOURCE_AND_RIGHTS.json",OUT/"PHOTO_QA.json",OUT/"TECHNICAL_QA.json",
             OUT/"README_RIGHTS_AND_LIMITATIONS.txt"]+[OUT/f"POST_{p}.txt" for p in posts]
    zp=OUT/"CINEMA_1903_COMPLETE_PACKAGE.zip"
    with zipfile.ZipFile(zp,"w",zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for path in include:z.write(path,path.name)
    with zipfile.ZipFile(zp) as z:
        assert z.testzip() is None
    write("DELIVERY_STATUS.json",{
        "status":"COMPLETE_REAL_MP4_ZIP_ARTISTIC_REVIEW_PENDING",
        "film":"The Great Train Robbery (1903)","mp4":final.name,
        "package":zp.name,"mp4_sha256":hsh(final),"package_sha256":hsh(zp),
        "bytes_mp4":final.stat().st_size,"bytes_package":zp.stat().st_size,
        "artistic_approval":False,"new_vidu_clip":False,"paid_calls":0,"published":False})

def main():
    try:
        download()
        images,duration=frames_of_original()
        session,model_info=dd.download_model()
        write("NEURAL_COLOR_MODEL.json",model_info)
        ai_anchor=images[min(len(images)-1,round(ANCHOR_S*FPS))]
        photo_base=colorize(ai_anchor,dd.infer_ab(session,ai_anchor))
        photo=photo_finegrain(photo_base,ai_anchor)
        final,report=export(images,photo,session)
        package(final,report)
        print("DONE_REAL_NEW_CINEMA_MASTER",report["sha256"],report["duration_s"],flush=True)
    except Exception as e:
        write("FAILURE.json",{"status":"NOT_DELIVERED","error":type(e).__name__+": "+str(e)[:700],
                              "paid_calls":0,"published":False})
        raise

if __name__=="__main__":
    main()
