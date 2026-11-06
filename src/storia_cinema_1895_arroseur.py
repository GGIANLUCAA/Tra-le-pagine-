#!/usr/bin/env python3
"""La Storia Rivive / CINEMA: L'Arroseur arrosé (1895).
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
OUT=ROOT/"output"/"storia_cinema_1895_arroseur"
OUT.mkdir(parents=True,exist_ok=True)
SRC=OUT/"ARROSEUR_1895_LUMIERE_NATIVE.webm"
PAGE="https://commons.wikimedia.org/wiki/File:Le_Jardinier_(l%27Arroseur_arros%C3%A9)_(1895).webm"
LOC="https://catalogue-lumiere.com/arroseur-et-arrose-i/"
UA="LaStoriaRiviveCinema/2.0 (+https://github.com/GGIANLUCAA/Tra-le-pagine-)"
FPS=24;W=720;H=1280
p.OUT=OUT;p.SRC=SRC;p.FPS=FPS;p.W=W;p.H=H;p.SLOW=1.06
p.ANCHOR_S=2.0;p.REVEAL_START=0.95;p.REVEAL_END=2.15
def write(name,data):
    (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def digest(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1048576),b""):h.update(b)
    return h.hexdigest()
def retrieve():
    if SRC.exists() and SRC.stat().st_size>8_000_000:
        return SRC
    name="Le Jardinier (l'Arroseur arrosé) (1895).webm"
    api="https://commons.wikimedia.org/w/api.php?"+urlencode({
        "action":"query","format":"json","formatversion":"2","prop":"imageinfo",
        "titles":"File:"+name,"iiprop":"url|size|mime|extmetadata"})
    links=[]
    try:
        req=Request(api,headers={"User-Agent":UA})
        with urlopen(req,timeout=25) as r: info=json.load(r)["query"]["pages"][0]["imageinfo"][0]
        assert info["mime"].startswith("video/") and 8_000_000<int(info["size"])<30_000_000
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
                    if out.tell()>30_000_000:raise RuntimeError("SOURCE_TOO_LARGE")
            if 8_000_000<SRC.stat().st_size<30_000_000:
                print("REAL_ARCHIVAL_MOVING_SOURCE",SRC.stat().st_size,flush=True)
                return SRC
            raise RuntimeError("SOURCE_TRUNCATED_OR_INCORRECT")
        except Exception as e:failures.append(type(e).__name__+" "+str(e)[:180])
    write("FETCH_FAILURE.json",{"status":"HISTORICAL_SOURCE_NOT_DOWNLOADABLE","reasons":failures})
    raise RuntimeError("NO_AUTHENTIC_HIGH_RES_SOURCE "+str(failures))
def center_crop(frame):
    h,w=frame.shape[:2]
    cw=int(h*W/H)
    # Actual full-frame review proved BOTH subjects are on the LEFT of 1895
    # original for the selected comedic segment. A center crop made a fake
    # 'photograph of an empty garden' (REJECTED). Keep the true actors in frame.
    x=0
    return cv2.resize(frame[:,x:x+cw],(W,H),interpolation=cv2.INTER_CUBIC)
def film_frames():
    cap=cv2.VideoCapture(str(SRC))
    nativefps=float(cap.get(cv2.CAP_PROP_FPS));total=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH));height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration=total/nativefps if nativefps>0 else 0
    if not(38.0<=duration<=43.0 and width>=1400 and height>=1000 and 14<=nativefps<=61):
        raise RuntimeError(f"SOURCE_META_NOT_EXPECTED {duration=}, {width=}, {height=}, {nativefps=}")
    frames=[]
    # Decode original to real frames, never still image pan/zoom. Preserve true camera motion.
    # Choose the true 1895 comic payoff: water sprays the gardener, the actors
    # move together, and the prank ends. Real frame content, not AI animation.
    # Decode just this sequence once to reduce expensive repeated VP9 seeking.
    excerpt=OUT/"ORIGINAL_1895_17_TO_37.mp4"
    process=subprocess.run(["ffmpeg","-nostdin","-y","-v","error","-ss","17",
             "-i",str(SRC),"-t","20","-vf",f"fps={FPS}","-an",
             "-c:v","libx264","-crf","17","-preset","veryfast",
             "-pix_fmt","yuv420p",str(excerpt)],capture_output=True,text=True,timeout=140)
    cap.release()
    if process.returncode or not excerpt.is_file():
        raise RuntimeError("AUTHENTIC_EXCERPT_DECODE_FAILED "+process.stderr[-300:])
    cap=cv2.VideoCapture(str(excerpt))
    for i in range(int(20.0*FPS)-2):
        ok,frame=cap.read()
        if not ok:raise RuntimeError("SOURCE_FRAME_READ_FAILED "+str(i))
        frames.append(center_crop(frame))
    cap.release()
    if len(frames)<300:raise RuntimeError("SHORT_ACTUAL_CINEMA")
    motions=[]
    for i in range(8,len(frames)-11,25):
        aa=cv2.resize(frames[i],(120,213))
        bb=cv2.resize(frames[i+9],(120,213))
        motions.append(float(np.mean(cv2.absdiff(aa,bb))))
    if np.median(motions)<1.5:raise RuntimeError("AUTHENTIC_MOTION_NOT_PROVED")
    # Gentle real-film de-flicker; never replace the dancer with a hallucinated frame.
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
    for i,t in enumerate([0.8,3.4,6.4,10.0,14.0,18.0]):
        idx=min(len(frames)-1,round(t*FPS))
        im=Image.fromarray(cv2.cvtColor(frames[idx],cv2.COLOR_BGR2RGB))
        board.paste(im.resize((236,420)),(i*240+2,29))
        draw.text((i*240+4,5),f"ACTUAL 1895 FILM {t:.1f}s",fill="white")
    board.save(OUT/"TRUE_ORIGINAL_CONTACT.jpg",quality=92)
    write("RIGHTS_AND_PROVENANCE.json",{
      "title":"L'Arroseur arrosé","year":1895,"director":"Louis Lumière",
      "director_died":1948,"camera":"Louis Lumière","archive":"Wikimedia Commons / Lumière catalog","excerpt_start_s":17.0,"excerpt_duration_s":20.0,
      "archive_link":LOC,"film_source":PAGE,"source_sha256":digest(SRC),
      "source_resolution":[width,height],"source_fps":nativefps,"source_duration_s":duration,
      "original_median_real_motion_delta":round(float(np.median(motions)),3),
      "rights":"Wikimedia Commons PDM, PD-old-70 and PD-US; Louis Lumière died 1948 and term life+70 expired in Italy in 2019.",
      "note":"AI photos and colors are modern interpretations, NOT actual 1895 colors.",
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
        d.text((32,55),"ARROSEUR  ·  1895",fill=(238,232,216),font=f,
            stroke_width=2,stroke_fill=(9,12,15))
        d.text((33,H-67),"LUMIÈRE  ·  ORIGINAL FILM 1895",fill=(237,235,229),
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
    # One-person action anchor (source ~19s), not the prior bad two-person
    # anchor that invented pistol-shaped props and failed actual image review.
    prompt=("Hyperphotorealistic modern documentary COLOR photograph restoring THIS EXACT "
            "1895 Louis Lumiere original frame: ONE adult male GARDENER wearing 19th-century "
            "work clothes, apron and brimmed work hat, outdoors in a real 1895 vegetable garden, "
            "caught by water splashing from a flexible GARDEN HOSE and trying to look down "
            "at its nozzle. Keep the EXACT SOURCE PERSON, ONE complete human body, real hat, "
            "hands and boots, natural realistic wet shirt and apron fabric folds, "
            "subtle splashes/droplets, unchanged pose, trees, garden, background wall "
            "and original field of view. Modern 2026 optical photographic realism "
            "with accurate natural skin detail and neutral authentic greens; "
            "do not invent anything not present in the source.")
    negative=("pistol, gun, firearm, revolver, rifle, weapon, gun barrel, added tool, "
              "extra person, child, alien, horns, fused limbs, deformed face, extra fingers, "
              "missing hands, fake extra hoses, strange water, surreal, plastic toy, "
              "illustration, cartoon, painting, fantasy outfit, strange bright saturation")
    try:
        c=Client("finegrain/finegrain-image-enhancer",verbose=False)
        raw=c.predict(handle_file(str(OUT/"NEURAL_COLOR_BASE.png")),prompt,negative,
                      1895,2,1.14,.97,6,112,144,.45,18,"DDIM",api_name="/process")
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
    wav=OUT/"ARROSEUR_ORIGINAL_SCORE.wav"
    with wave.open(str(wav),"wb") as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr);f.writeframes(sound.tobytes())
    return wav
p.synth_sound=score
def package(final,info):
    final_path=OUT/"ARROSEUR_1895_CINEMA_RESTORED.mp4"
    final.rename(final_path)
    cv2.imwrite(str(OUT/"ARROSEUR_1895_COVER.jpg"),cv2.imread(str(OUT/"COVER_CINEMA_1903.jpg")))
    src_cover=OUT/"COVER_CINEMA_1903.jpg"
    if src_cover.exists():src_cover.unlink()
    posts={
      "FACEBOOK":"L'ARROSEUR ARROSÉ · 1895 | La celebre gag del giardiniere e del ragazzo dispettoso. Il movimento è la pellicola originale dei Lumière; colori e fotografia sono ricostruiti con intelligenza artificiale. Fonte: Wikimedia Commons (pubblico dominio), Louis Lumière.",
      "INSTAGRAM":"L'ARROSEUR ARROSÉ · 1895 🎬 Una delle prime commedie della storia prende nuovamente vita. Movimento originale, colori ricostruiti. #SilentComedy #CinemaHistory #LaStoriaRivive",
      "TIKTOK":"Un giardiniere, un tubo e uno scherzo: la comicità nasceva già nel 1895. Film originale dei Lumière, restauro fotografico IA. #SilentCinema",
      "YOUTUBE":"L'ARROSEUR ARROSÉ · 1895 | First Cinema Comedy, Modern AI Restoration. Vera ripresa storica di Louis Lumière, fonte Wikimedia Commons PDM. Il movimento è originale e la ricostruzione a colori è interpretativa. "+PAGE
    }
    for social,text in posts.items():
        (OUT/f"POST_{social}.txt").write_text(text+"\n",encoding="utf-8")
    info["title"]="ARROSEUR · 1895"
    info["new_distinct_film_from_prior_1903"]=True
    info["new_Vidu_generated"]=False
    info["native_4K"]=False
    info["rights_italy"]="Louis Lumière died 1948; public domain in Italy after 2018 under life+70"
    info["human_anatomy_review"]="PENDING"
    info["quality_claim"]="modern photographic look goal; the source scan is not true 4K"
    info["sha256"]=digest(final_path)
    write("FINAL_QA.json",info)
    inputs=[final_path,OUT/"ARROSEUR_1895_COVER.jpg",OUT/"FILM_AND_AI_SCENE_REVIEW.jpg",
            OUT/"TRUE_ORIGINAL_CONTACT.jpg",OUT/"RIGHTS_AND_PROVENANCE.json",
            OUT/"PHOTO_I2I_QA.json",OUT/"FINAL_QA.json"] + [OUT/f"POST_{s}.txt" for s in posts]
    zp=OUT/"ARROSEUR_1895_VIDEO_COVER_SOCIAL.zip"
    with zipfile.ZipFile(zp,"w",zipfile.ZIP_DEFLATED) as z:
        for f in inputs:z.write(f,f.name)
    with zipfile.ZipFile(zp) as z:assert z.testzip() is None
    status={"state":"REAL_MP4_ZIP_RENDERED_ARTISTIC_REVIEW_PENDING",
            "duration_s":info["duration_s"],"mp4_sha256":digest(final_path),
            "mp4_bytes":final_path.stat().st_size,"zip_bytes":zp.stat().st_size,
            "zip_crc_verified":True,"paid_calls":0,"vidu_generated":False,
            "user_approved":False,"published":False}
    write("DELIVERY.json",status)
    print("REAL_ARROSEUR_VIDEO_ZIP_GENERATED",json.dumps(status),flush=True)
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
