#!/usr/bin/env python3
"""La Storia Rivive / CINEMA: Sandow (1894).
One NEW authentic moving film -> clean source -> DDColor -> single genuinely
FREE Finegrain photographic I2I -> 18s short, score, cover, 4 posts, CRC ZIP.
Fail closed: no paid API/Vidu, no auto-publication, no false approval."""
from __future__ import annotations
import cv2, numpy as np, json, hashlib, wave, os, sys, time, zipfile, importlib.util, subprocess
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.parse import urlencode, quote
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("cinema_1903_tools",ROOT/"src/storia_cinema_1903_gunman.py")
p=importlib.util.module_from_spec(spec);sys.modules["cinema_1903_tools"]=p;spec.loader.exec_module(p)
OUT=ROOT/"output"/"storia_cinema_1894_sandow"
OUT.mkdir(parents=True,exist_ok=True)
SRC=OUT/"SANDOW_1894_LOC_NATIVE.webm"
PAGE="https://commons.wikimedia.org/wiki/File:Sandow_(1894).webm"
LOC="https://www.loc.gov/"
UA="LaStoriaRiviveCinema/2.0 (+https://github.com/GGIANLUCAA/Tra-le-pagine-)"
FPS=24;W=720;H=1280
p.OUT=OUT;p.SRC=SRC;p.FPS=FPS;p.W=W;p.H=H;p.SLOW=1.08
p.ANCHOR_S=5.95;p.REVEAL_START=0.90;p.REVEAL_END=2.02
def write(name,data):
    (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def digest(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1048576),b""):h.update(b)
    return h.hexdigest()
def retrieve():
    if SRC.exists() and SRC.stat().st_size>60_000_000:
        return SRC
    name="Sandow (1894).webm"
    api="https://commons.wikimedia.org/w/api.php?"+urlencode({
        "action":"query","format":"json","formatversion":"2","prop":"imageinfo",
        "titles":"File:"+name,"iiprop":"url|size|mime|extmetadata"})
    links=[]
    try:
        req=Request(api,headers={"User-Agent":UA})
        with urlopen(req,timeout=25) as r: info=json.load(r)["query"]["pages"][0]["imageinfo"][0]
        assert info["mime"].startswith("video/") and 60_000_000<int(info["size"])<88_000_000
        links.append(info["url"])
    except Exception as e:print("COMMONS_API_METADATA_UNAVAILABLE",type(e).__name__,str(e)[:120],flush=True)
    links.append("https://commons.wikimedia.org/wiki/Special:Redirect/file/"+quote(name,safe=""))
    failures=[]
    for url in links:
        try:
            with urlopen(Request(url,headers={"User-Agent":UA}),timeout=90) as r,SRC.open("wb") as out:
                while True:
                    b=r.read(1048576)
                    if not b:break
                    out.write(b)
                    if out.tell()>88_000_000:raise RuntimeError("SOURCE_TOO_LARGE")
            if 60_000_000<SRC.stat().st_size<88_000_000:
                print("REAL_ARCHIVAL_MOVING_SOURCE",SRC.stat().st_size,flush=True)
                return SRC
            raise RuntimeError("SOURCE_TRUNCATED_OR_INCORRECT")
        except Exception as e:failures.append(type(e).__name__+" "+str(e)[:180])
    write("FETCH_FAILURE.json",{"status":"HISTORICAL_SOURCE_NOT_DOWNLOADABLE","reasons":failures})
    raise RuntimeError("NO_AUTHENTIC_HIGH_RES_SOURCE "+str(failures))
def center_crop(frame):
    h,w=frame.shape[:2]
    cw=int(h*W/H)
    # Frame is theatre-studio, with one central strongman. Do not use synthetic camera motion.
    x=max(0,min(w-cw,(w-cw)//2))
    return cv2.resize(frame[:,x:x+cw],(W,H),interpolation=cv2.INTER_CUBIC)
def film_frames():
    cap=cv2.VideoCapture(str(SRC))
    nativefps=float(cap.get(cv2.CAP_PROP_FPS));total=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH));height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration=total/nativefps if nativefps>0 else 0
    if not(39.0<=duration<=42.0 and width>=1400 and height>=1000 and 14<=nativefps<=61):
        raise RuntimeError(f"SOURCE_META_NOT_EXPECTED {duration=}, {width=}, {height=}, {nativefps=}")
    frames=[]
    # Decode original to real frames, never still image pan/zoom. Preserve true camera motion.
    for i in range(int(20.0*FPS)-2):
        cap.set(cv2.CAP_PROP_POS_MSEC,(6.0+i/FPS)*1000)
        ok,frame=cap.read()
        if not ok:raise RuntimeError("SOURCE_FRAME_READ_FAILED "+str(i))
        frames.append(center_crop(frame))
    cap.release()
    if len(frames)<290:raise RuntimeError("SHORT_ACTUAL_CINEMA")
    motions=[]
    for i in range(8,len(frames)-11,25):
        aa=cv2.resize(frames[i],(120,213))
        bb=cv2.resize(frames[i+9],(120,213))
        motions.append(float(np.mean(cv2.absdiff(aa,bb))))
    if np.median(motions)<1.5:raise RuntimeError("AUTHENTIC_MOTION_NOT_PROVED")
    # Gentle real-film de-flicker; never replace the strongman with a hallucinated frame.
    means=np.array([np.mean(cv2.cvtColor(cv2.resize(x,(120,213)),cv2.COLOR_BGR2GRAY)) for x in frames])
    smoother=np.convolve(np.pad(means,(6,6),mode="edge"),np.ones(13)/13,mode="valid")
    cleaned=[]
    for i,img in enumerate(frames):
        # Spatial bilateral denoising of film speckles and controlled exposure leveling.
        small=cv2.resize(img,(540,960),interpolation=cv2.INTER_AREA)
        sm=cv2.bilateralFilter(small,5,19,19)
        sm=cv2.resize(sm,(W,H),interpolation=cv2.INTER_CUBIC)
        gain=float(np.clip(smoother[i]/max(1,means[i]),.92,1.08))
        sm=cv2.convertScaleAbs(sm,alpha=gain,beta=0)
        cleaned.append(sm)
    # Contact sheet: multiple REAL different frames.
    board=Image.new("RGB",(6*240,456),(13,16,20));draw=ImageDraw.Draw(board)
    for i,t in enumerate([1.0,3.5,6.0,9.0,14.0,19.0]):
        idx=min(len(frames)-1,round(t*FPS))
        im=Image.fromarray(cv2.cvtColor(frames[idx],cv2.COLOR_BGR2RGB))
        board.paste(im.resize((236,420)),(i*240+2,29))
        draw.text((i*240+4,5),f"ACTUAL 1894 FILM {t:.1f}s",fill="white")
    board.save(OUT/"TRUE_ORIGINAL_CONTACT.jpg",quality=92)
    write("RIGHTS_AND_PROVENANCE.json",{
      "title":"Sandow","year":1894,"director":"William Kennedy Laurie Dickson",
      "director_died":1935,"camera":"William Heise","archive":"Library of Congress","film_excerpt_start_s":6.0,"film_excerpt_duration_s":20.0,
      "archive_link":LOC,"film_source":PAGE,"source_sha256":digest(SRC),
      "source_resolution":[width,height],"source_fps":nativefps,"source_duration_s":duration,
      "original_median_real_motion_delta":round(float(np.median(motions)),3),
      "rights":"Wikimedia Commons PD-US-expired; director died 1935, life+70 Italy expired; no copyright registration stated by Library of Congress.",
      "note":"AI photos and colors are modern interpretations, NOT actual 1894 colors.",
      "video_motion":"Genuine film footage only, no synthetic pan.",
      "paid_credit_calls":0,"publication":False})
    return cleaned,duration
def title(frame,second,show=True):
    if not show:return frame
    img=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
    d=ImageDraw.Draw(img)
    try:
        f=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",29)
        small=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",16)
    except OSError:
        f=ImageFont.load_default();small=f
    if second<=2.2:
        d.text((32,55),"SANDOW  ·  1894",fill=(238,232,216),font=f,
            stroke_width=2,stroke_fill=(9,12,15))
        d.text((33,H-67),"EDISON STUDIO  ·  ARCHIVE FILM",fill=(237,235,229),
             font=small,stroke_width=2,stroke_fill=(7,10,13))
    return cv2.cvtColor(np.array(img),cv2.COLOR_RGB2BGR)
p.draw_title=title
def modern_color(frame,ab):
    # Restore the film's actual luminance, use semantically inferred colors,
    # then limit hue exaggeration and gently restore natural contrast.
    out=p.colorize_original(frame,ab)
    lab=cv2.cvtColor(out,cv2.COLOR_BGR2LAB).astype("float32")
    lab[:,:,1:]=128+(lab[:,:,1:]-128)*.76
    result=cv2.cvtColor(np.clip(lab,0,255).astype("uint8"),cv2.COLOR_LAB2BGR)
    g=cv2.GaussianBlur(result,(0,0),.82)
    return cv2.addWeighted(result,1.22,g,-.22,0)
p.colorize_original=p.colorize
p.colorize=modern_color
def photograph(base,mono):
    cv2.imwrite(str(OUT/"NEURAL_COLOR_BASE.png"),base)
    cv2.imwrite(str(OUT/"EXACT_BW_ANCHOR.png"),mono)
    manifest={"service":"Finegrain image enhancer, Gradio free tier","paid_api_calls":0,
              "authentic_source_frame":True,"attempt_count":1,"editorial_approval":False}
    from gradio_client import Client,handle_file
    prompt=("Extremely photorealistic modern COLOR photograph of this exact 1894 film frame of "
            "EUGEN SANDOW, ONE adult strongman with authentic muscular shoulders and arms, nineteenth-century "
            "posing attire, a neutral studio background, SAME face, exact flexing pose, hand positions, "
            "correct five fingers and normal human anatomy. Sharpen natural skin pores, hair and fabric, "
            "restrained real-world colours and studio lighting, like a clear contemporary photograph. "
            "Not an illustration and not a newly invented person.")
    negative=("three arms, extra fingers, missing hands, extra biceps or legs, body duplication, horns, "
              "deformed joints, wax statue, strange face, cartoon, painting, extra people, "
              "oversaturated orange skin, implausible muscle shape, fake text")
    try:
        c=Client("finegrain/finegrain-image-enhancer",verbose=False)
        raw=c.predict(handle_file(str(OUT/"NEURAL_COLOR_BASE.png")),prompt,negative,
                      1894,2,1.14,.97,6,112,144,.45,18,"DDIM",api_name="/process")
        ref=raw[1] if isinstance(raw,(list,tuple)) and len(raw)>1 else raw
        if isinstance(ref,dict):ref=ref.get("path")
        pic=cv2.imread(str(ref))
        if pic is None:raise RuntimeError("I2I_MISSING_PIXELS")
        pic=cv2.resize(pic,(W,H))
        structure=p.corr(mono,pic); base_sim=p.corr(base,pic)
        sat=float(cv2.cvtColor(pic,cv2.COLOR_BGR2HSV)[:,:,1].mean())
        diff=float(np.mean(cv2.absdiff(pic,base)))
        manifest.update({"created_real_ai_photo":True,
                         "structure_vs_bw":round(structure,4),
                         "same_shot_vs_color_base":round(base_sim,4),
                         "saturation":round(sat,3),
                         "difference_from_prior_color":round(diff,3)})
        # Image gate is not a human anatomy check, just a stop for gross divergence.
        if structure<.77 or base_sim<.82 or sat<25 or diff<1:
            manifest["status"]="REJECTED_PHOTO_STRUCTURE_COLOR"
            raise RuntimeError("FREE_I2I_VISUAL_GATE_FAILED")
        cv2.imwrite(str(OUT/"NEW_PHOTOGRAPHIC_RESTORATION.png"),pic)
        manifest["status"]="REAL_I2I_GENERATED_REVIEW_PENDING"
        write("PHOTO_I2I_QA.json",manifest)
        return pic
    except Exception as e:
        manifest.setdefault("status","PROVIDER_NOT_AVAILABLE_OR_QUALITY_FAIL")
        manifest["error"]=str(e)[:350]
        write("PHOTO_I2I_QA.json",manifest)
        raise
def score(seconds):
    sr=32000;t=np.arange(round(seconds*sr),dtype=np.float32)/sr
    s=np.zeros_like(t)
    # Completely original plucked/waltz-like silent-cinema underscore.
    for k,(f,phase) in enumerate([(196,.2),(293.66,.6),(392,1.5),(587.33,2.1)]):
        s+=.028*np.sin(2*np.pi*f*t+phase)*(0.57+0.35*np.cos(2*np.pi*(.87+.05*k)*t))
        s+=.004*np.sin(2*np.pi*f*2.01*t+phase)
    for j in np.arange(0,seconds,0.66):
        z=t-j;m=(z>=0)&(z<.27)
        s[m]+=.022*np.sin(2*np.pi*(195*z[m]+27*z[m]**2))*np.exp(-17*z[m])
    s=np.tanh(s*2.2)
    env=np.minimum(1,t/.75)*np.minimum(1,np.maximum(0,(seconds-t)/.85))
    sound=(np.clip(s*env,-1,1)*18500).astype("<i2")
    wav=OUT/"SANDOW_ORIGINAL_SCORE.wav"
    with wave.open(str(wav),"wb") as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr);f.writeframes(sound.tobytes())
    return wav
p.synth_sound=score
def package(final,info):
    final_path=OUT/"SANDOW_1894_CINEMA_RESTORED.mp4"
    final.rename(final_path)
    cv2.imwrite(str(OUT/"SANDOW_1894_COVER.jpg"),cv2.imread(str(OUT/"COVER_CINEMA_1903.jpg")))
    src_cover=OUT/"COVER_CINEMA_1903.jpg"
    if src_cover.exists():src_cover.unlink()
    posts={
      "FACEBOOK":"SANDOW · 1894 | Il pioniere della cultura fisica Eugen Sandow posa davanti alla cinepresa di Edison. Il movimento è quello del film originale; colori e dettagli sono ricostruzioni interpretative AI. Fonte: Library of Congress / Wikimedia Commons, pubblico dominio.",
      "INSTAGRAM":"SANDOW · 1894 🎬 I gesti del primo culturismo davanti a una cinepresa. Pellicola autentica, colore AI interpretativo. #SilentCinema #FilmHistory #LaStoriaRivive",
      "TIKTOK":"1894: Eugen Sandow, il culturista che Edison ha filmato. Movimento originale, colori e dettagli AI ricostruiti. #HistoryTok",
      "YOUTUBE":"SANDOW · 1894 | A Strongman on Film. Ripresa storica autentica del 1894 di Eugen Sandow, William K. L. Dickson, Library of Congress. Movimento reale, fotografia e colori AI interpretativi. Fonte: "+PAGE
    }
    for social,text in posts.items():
        (OUT/f"POST_{social}.txt").write_text(text+"\n",encoding="utf-8")
    info["title"]="SANDOW · 1894"
    info["new_distinct_film_from_prior_1903"]=True
    info["new_Vidu_generated"]=False
    info["native_4K"]=False
    info["rights_italy"]="Director died 1935; public-domain based on life+70 and 1894 production"
    info["human_anatomy_review"]="PENDING"
    info["quality_claim"]="4K perceived goal, source not true 4K"
    info["sha256"]=digest(final_path)
    write("FINAL_QA.json",info)
    inputs=[final_path,OUT/"SANDOW_1894_COVER.jpg",OUT/"FILM_AND_AI_SCENE_REVIEW.jpg",
            OUT/"TRUE_ORIGINAL_CONTACT.jpg",OUT/"RIGHTS_AND_PROVENANCE.json",
            OUT/"PHOTO_I2I_QA.json",OUT/"FINAL_QA.json"] + [OUT/f"POST_{s}.txt" for s in posts]
    zp=OUT/"SANDOW_1894_VIDEO_COVER_SOCIAL.zip"
    with zipfile.ZipFile(zp,"w",zipfile.ZIP_DEFLATED) as z:
        for f in inputs:z.write(f,f.name)
    with zipfile.ZipFile(zp) as z:assert z.testzip() is None
    status={"state":"REAL_MP4_ZIP_RENDERED_ARTISTIC_REVIEW_PENDING",
            "duration_s":info["duration_s"],"mp4_sha256":digest(final_path),
            "mp4_bytes":final_path.stat().st_size,"zip_bytes":zp.stat().st_size,
            "zip_crc_verified":True,"paid_calls":0,"vidu_generated":False,
            "user_approved":False,"published":False}
    write("DELIVERY.json",status)
    print("REAL_SANDOW_VIDEO_ZIP_GENERATED",json.dumps(status),flush=True)
def main():
    try:
        retrieve()
        images,duration=film_frames()
        dd_session,model=p.dd.download_model()
        write("COLOR_MODEL.json",model)
        anchor=min(len(images)-1,int(p.ANCHOR_S*FPS))
        bw=images[anchor]
        base=modern_color(bw,p.dd.infer_ab(dd_session,bw))
        photo=photograph(base,bw)
        movie,info=p.export(images,photo,dd_session)
        package(movie,info)
    except Exception as e:
        write("FAILURE.json",{"status":"NOT_DELIVERED","error":type(e).__name__+": "+str(e)[:520],
                              "paid_requests":0,"published":False})
        raise
if __name__=="__main__":main()
