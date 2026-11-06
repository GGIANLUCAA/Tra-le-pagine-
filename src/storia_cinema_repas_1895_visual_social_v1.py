#!/usr/bin/env python3
"""La Storia Rivive ONLY: Repas de bebe (1895), REAL motion + FREE image I2I, social review.
Fail closed: no final approval, no Vidu calls, no paid calls, no social/site posting."""
from __future__ import annotations
import cv2, numpy as np, subprocess, hashlib, json, zipfile, sys, os
from pathlib import Path
from urllib.request import urlopen, Request
from PIL import Image, ImageDraw, ImageFont
from gradio_client import Client,handle_file

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
import storia_rivive_real_ai_v60 as dd
OUT=ROOT/"output"/"storia_cinema_repas_1895_v1"
OUT.mkdir(parents=True,exist_ok=True)
PAGE="https://commons.wikimedia.org/wiki/File:Repas_de_b%C3%A9b%C3%A9_(1895).webm"
URL="https://upload.wikimedia.org/wikipedia/commons/8/86/Repas_de_b%C3%A9b%C3%A9_%281895%29.webm"
SOURCE=OUT/"LUMIERE_REPAS_1895_ORIGINAL.webm"
CLIP=OUT/"REAL_FILM_EXCERPT.mp4"
MOVIE=OUT/"REPAS_1895_SOCIAL_VISUAL_REVIEW.mp4"
ZIP=OUT/"REPAS_1895_VIDEO_COVER_SOCIAL.zip"
W,H,FPS=720,1280,24
AW,AH=720,540
START,DURATION=5,17
ANCHOR=round(4.2*FPS)
HOLD=round(1.85*FPS)
def run(command,timeout=320):
    p=subprocess.run(command,capture_output=True,text=True,timeout=timeout)
    if p.returncode: raise RuntimeError("CMD_ERROR "+str(command[:8])+" "+p.stderr[-420:])
    return p.stdout
def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()
def write(path,obj):
    (OUT/path).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
def source():
    if not SOURCE.exists() or SOURCE.stat().st_size<90_000_000:
        with urlopen(Request(URL,headers={"User-Agent":"LaStoriaRivive/1.0 (archival image research; https://github.com/GGIANLUCAA/Tra-le-pagine-)", "Accept":"video/webm,*/*"}),timeout=100) as response, SOURCE.open("wb") as target:
            while True:
                part=response.read(1024*1024)
                if not part: break
                target.write(part)
                if target.tell()>111_000_000: raise RuntimeError("WRONG_ORIGINAL_SIZE")
    if not 90_000_000<SOURCE.stat().st_size<111_000_000:raise RuntimeError("SOURCE_TRUNCATED")
    run(["ffmpeg","-nostdin","-y","-v","error","-ss",str(START),"-i",str(SOURCE),
         "-t",str(DURATION),"-vf",f"fps={FPS},scale=960:720", "-an",
         "-c:v","libx264","-preset","veryfast","-crf","17","-pix_fmt","yuv420p",str(CLIP)],200)
    cap=cv2.VideoCapture(str(CLIP))
    count=int(cap.get(cv2.CAP_PROP_FRAME_COUNT));fps=cap.get(cv2.CAP_PROP_FPS)
    sw=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH));sh=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    if not (340<=count<=440 and abs(fps-FPS)<.1 and sw==960 and sh==720): raise RuntimeError("NOT_GENUINE_FILM_SOURCE "+str((count,fps,sw,sh)))
    write("RIGHTS.json",{"film":"Repas de bebe","year":1895,"director":"Louis Lumiere","death_year":1948,
     "source":PAGE,"source_url":URL,"source_sha256":sha(SOURCE),"source_bytes":SOURCE.stat().st_size,
     "source_original_resolution":[1364,1022],"excerpt_start_s":START,"excerpt_duration_s":DURATION,
     "copyright":{"Italy":"Life+70; creator died 1948, term ended 2018","USA":"Pre-1931 published film, Public Domain Mark on Commons"},
     "colors":"Modern interpretation; not actual 1895 recorded colors",
     "release_policy":"Review-only PUBLIC GitHub prerelease for owner download; NEVER site/social publishing",
     "publication":False,"vidu_post_count":0,"paid_calls":0})
def readframe(idx):
    cap=cv2.VideoCapture(str(CLIP));cap.set(cv2.CAP_PROP_POS_FRAMES,int(idx))
    ok,f=cap.read();cap.release()
    if not ok:raise RuntimeError("SOURCE_FRAME_MISSING "+str(idx))
    return f
def colorize(frame,ab):
    lab=cv2.cvtColor(frame.astype(np.float32)/255.0,cv2.COLOR_BGR2LAB)
    chroma=cv2.resize(ab,(frame.shape[1],frame.shape[0]),interpolation=cv2.INTER_LINEAR)
    lab[:,:,1:]=np.clip(chroma*.83,-92,92)
    rgb=cv2.cvtColor(lab.astype(np.float32),cv2.COLOR_LAB2BGR)
    return np.clip(rgb*255,0,255).astype("uint8")
def corr(a,b):
    def feature(v):
        g=cv2.cvtColor(cv2.resize(v,(144,108)),cv2.COLOR_BGR2GRAY)
        return cv2.GaussianBlur(g,(5,5),0).astype(np.float32).ravel()
    return float(np.corrcoef(feature(a),feature(b))[0,1])
def photo(base,original):
    cv2.imwrite(str(OUT/"ANCHOR_REAL_ORIGINAL_BW.png"),original)
    cv2.imwrite(str(OUT/"ANCHOR_AI_NEURAL_COLOR_BASE.png"),base)
    report={"provider":"finegrain/finegrain-image-enhancer","real_free_I2I_created":False,"status":"NOT_TESTED","paid_calls":0,
            "artistic_review":"PENDING","source_frame_index":ANCHOR,"source_frame_local_seconds":ANCHOR/FPS}
    try:
        prompt=("A faithful modern documentary PHOTOGRAPHIC restoration of this EXACT 1895 French garden family-breakfast historical frame. "
                "Three and only three original people: an adult man to the left feeding the infant seated in the middle, "
                "an adult woman to the right wearing authentic 1895 dress, all seated at one table. "
                "Preserve source people, camera angle, exact pose, facial directions, arms, visible hands, baby's size and seating, "
                "period clothing, glassware, cups, metal utensils, table, chairs and exterior garden behind. "
                "Skin pores, natural fabric weave, real daylight, authentic natural colors, optical photographic sharpness. "
                "The baby's face may be plausibly refined but must have normal human anatomy. "
                "Do NOT add or omit any person, object, hand, limb, or tableware; no portrait substitutions.")
        neg=("extra fingers, missing fingers, merged hands, extra people, extra child, distorted infant face, "
             "second baby, animal head, horns, doubled spoon, melted face, fake objects, new cups, "
             "fantasy, cartoon, illustration, painting, wax, overprocessed skin, super saturated red, violet haze")
        client=Client("finegrain/finegrain-image-enhancer",verbose=False)
        raw=client.predict(handle_file(str(OUT/"ANCHOR_AI_NEURAL_COLOR_BASE.png")),prompt,neg,
                          1895,2,1.14,.97,6,112,144,.45,18,"DDIM",api_name="/process")
        obj=raw[1] if isinstance(raw,(list,tuple)) and len(raw)>1 else raw
        if isinstance(obj,dict):obj=obj.get("path")
        pic=cv2.imread(str(obj))
        if pic is None: raise RuntimeError("NO_REAL_IMAGE_RETURNED")
        pic=cv2.resize(pic,(960,720),interpolation=cv2.INTER_AREA)
        c1,c2=corr(original,pic),corr(base,pic)
        sat=float(cv2.cvtColor(pic,cv2.COLOR_BGR2HSV)[:,:,1].mean())
        delta=float(np.mean(cv2.absdiff(pic,base)))
        report.update({"real_free_I2I_created":True,"original_structure_corr":round(c1,4),
                       "color_base_corr":round(c2,4),"saturation":round(sat,2),"diff_from_ddcolor":round(delta,2)})
        cv2.imwrite(str(OUT/"GENERATIVE_PHOTO_REAL_CANDIDATE.png"),pic)
        if c1<.73 or c2<.80 or sat<18 or sat>135 or delta<2.0:
            report["status"]="TECHNICAL_IDENTITY_OR_COLOR_FAIL"
            raise RuntimeError("SOURCE_LOCKED_PHOTO_GATE_FAIL")
        report["status"]="REAL_PHOTO_TECHNICAL_GATE_PASS_ARTISTIC_REVIEW_PENDING"
        write("PHOTO_QA.json",report)
        return pic
    except Exception as e:
        if report["status"]=="NOT_TESTED":report["status"]="FREE_I2I_PROVIDER_FAILED"
        report["error"]=type(e).__name__+": "+str(e)[:360]
        write("PHOTO_QA.json",report)
        raise
def frame_canvas(scene,title="",small=""):
    # Preserve every original person in the complete 4:3 film frame. Vertical 9:16 is NOT a narrow crop.
    scene=cv2.resize(scene,(AW,AH),interpolation=cv2.INTER_AREA)
    tiny=cv2.resize(scene,(150,112),interpolation=cv2.INTER_AREA)
    bg=cv2.GaussianBlur(tiny,(0,0),13)
    out=cv2.resize(bg,(W,H),interpolation=cv2.INTER_LINEAR)
    out=cv2.convertScaleAbs(out,alpha=.37)
    top=(H-AH)//2
    out[top:top+AH,:]=scene
    cv2.line(out,(0,top-1),(W,top-1),(201,199,193),2)
    cv2.line(out,(0,top+AH+1),(W,top+AH+1),(201,199,193),2)
    if title or small:
        im=Image.fromarray(cv2.cvtColor(out,cv2.COLOR_BGR2RGB))
        d=ImageDraw.Draw(im)
        try:
            ft=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",27)
            fs=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",17)
        except:ft=fs=ImageFont.load_default()
        if title:d.text((33,140),title,font=ft,fill=(241,237,224),stroke_width=2,stroke_fill=(15,17,21))
        if small:d.text((34,1098),small,font=fs,fill=(229,224,210),stroke_width=2,stroke_fill=(13,16,20))
        out=cv2.cvtColor(np.asarray(im),cv2.COLOR_RGB2BGR)
    return out
def export(picture,session):
    # First REAL moving B/W 4s -> same-frame .35s freeze -> I2I photo reveal 1.85s -> colored ORIGINAL movement.
    count=round(DURATION*FPS)
    keyframes=sorted(set(list(range(0,count,FPS*2))+[ANCHOR,count-1]))
    baseframes={i:readframe(i) for i in keyframes}
    colors={i:dd.infer_ab(session,baseframes[i]) for i in keyframes}
    raw=OUT/"REVIEW_VIDEO_SILENT.mp4"
    writer=subprocess.Popen(["ffmpeg","-nostdin","-y","-v","error","-f","rawvideo","-pix_fmt","bgr24",
        "-s",f"{W}x{H}","-r",str(FPS),"-i","-","-an","-c:v","libx264","-preset","veryfast",
        "-crf","18","-pix_fmt","yuv420p","-movflags","+faststart",str(raw)],
        stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    if writer.stdin is None:raise RuntimeError("FFMPEG_NOT_STARTED")
    visual=[]
    cap=cv2.VideoCapture(str(CLIP))
    current=0
    try:
        while current<count:
            ok,frame=cap.read()
            if not ok:raise RuntimeError("HISTORICAL_MOVEMENT_FRAME_MISSING "+str(current))
            i=current
            if i<ANCHOR:result=frame
            else:
                near=min(keyframes,key=lambda k:abs(k-i))
                warped=dd.warp_ab(frame,baseframes[near],colors[near])
                col=colorize(frame,warped)
                # Chroma remains grounded in REAL footage; never present as full AI generative motion.
                hsv=cv2.cvtColor(col,cv2.COLOR_BGR2HSV)
                hsv[:,:,1]=(hsv[:,:,1].astype(np.float32)*.80).clip(0,255).astype(np.uint8)
                result=cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)
            if i==ANCHOR:
                # Explicitly pause the MOVING source. Keep SAME exact source frame for image morph.
                for j in range(9):
                    writer.stdin.write(frame_canvas(frame).tobytes())
                for j in range(HOLD):
                    ramp=np.clip((j+1)/round(FPS*.55),0,1)
                    ramp=ramp*ramp*(3-2*ramp)
                    freeze=cv2.addWeighted(frame,1-ramp,picture,ramp,0)
                    writer.stdin.write(frame_canvas(freeze).tobytes())
                for j in range(7):
                    writer.stdin.write(frame_canvas(picture).tobytes())
                visual.append(("REAL SAME-SHOT AI PHOTO",picture.copy()))
            title="REPAS DE BÉBÉ  ·  1895" if i<round(2*FPS) else ""
            small="LOUIS LUMIÈRE  ·  ORIGINAL MOVING FILM" if i<round(2*FPS) else ""
            writer.stdin.write(frame_canvas(result,title,small).tobytes())
            if i in [0,ANCHOR-15,ANCHOR+int(FPS*.6),ANCHOR+int(FPS*3),count-1]:
                visual.append((f"ORIGINAL MOTION t={i/FPS:.1f}s",result.copy()))
            current+=1
    finally:
        cap.release()
        writer.stdin.close()
        error=writer.stderr.read().decode(errors="ignore")
        if writer.wait()!=0:raise RuntimeError("ENCODER_FAILED "+error[-550:])
    # 1080x1920 output vertical 9:16; upscaled from faithfully composed 720x1280 image.
    run(["ffmpeg","-nostdin","-y","-v","error","-i",str(raw),"-f","lavfi","-i",
         "anullsrc=channel_layout=stereo:sample_rate=44100",
         "-vf","scale=1080:1920:flags=lanczos","-c:v","libx264","-preset","veryfast","-crf","19",
         "-pix_fmt","yuv420p","-c:a","aac","-b:a","96k","-shortest","-movflags","+faststart",str(MOVIE)],240)
    run(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(MOVIE),"-f","null","-"],180)
    n=(count+9+HOLD+7)/FPS
    cap=cv2.VideoCapture(str(MOVIE));real_n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT));f=cap.get(cv2.CAP_PROP_FPS)
    ww=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH));hh=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT));cap.release()
    if ww!=1080 or hh!=1920 or abs(real_n/f-n)>.25 or not 15<n<25:raise RuntimeError("VERTICAL_VIDEO_QA_FAILED")
    pic=cv2.resize(picture,(W,AH))
    cv2.imwrite(str(OUT/"SOCIAL_COVER.jpg"),frame_canvas(pic,"REPAS DE BÉBÉ  ·  1895","HISTORICAL CINEMA   ·   VISUAL REVIEW"),[cv2.IMWRITE_JPEG_QUALITY,95])
    tiles=Image.new("RGB",(5*238,2*184),(18,18,20));d=ImageDraw.Draw(tiles)
    pairs=[("HISTORIC FILM",readframe(ANCHOR)),("DDCOLOR BASE",colorize(readframe(ANCHOR),colors[ANCHOR])),
           ("TRUE FREE I2I",picture),("REAL MOVEMENT",readframe(ANCHOR+24)),("MOVEMENT LATER",readframe(ANCHOR+96))]
    for i,(name,f) in enumerate(pairs):
        item=Image.fromarray(cv2.cvtColor(cv2.resize(f,(232,174)),cv2.COLOR_BGR2RGB))
        tiles.paste(item,(i*238+3,30));d.text((i*238+4,5),name,fill="white")
    tiles.save(OUT/"ORIGINAL_VS_PHOTO_VISUAL_QA.jpg",quality=93)
    report={"status":"REAL_VERTICAL_MP4_RENDERED_REVIEW_PENDING","filename":MOVIE.name,
       "sha256":sha(MOVIE),"bytes":MOVIE.stat().st_size,"resolution":[ww,hh],"fps":round(f,3),
       "duration_s":round(n,3),"source_motion":"REAL archive video before and after freeze",
       "freeze_s":9/FPS,"photographic_i2i_hold_s":round((HOLD+7)/FPS,3),
       "moving_color":"Original footage with DDColor neural chroma; NOT fully generative I2V",
       "photo_status":"Generative single frame pending manual anatomical QC",
       "vidu_new_clip":False,"paid_calls":0,"artistic_approval":False,"published":False}
    write("VISUAL_REPORT.json",report)
    return report
def package(report):
    post={
      "FACEBOOK":"REPAS DE BÉBÉ · 1895\nUn momento familiare ripreso realmente dai Lumière. Movimento del film originale; un fotogramma reinterpretato fotograficamente con IA. Anteprima tecnica, non pubblicata.",
      "INSTAGRAM":"REPAS DE BÉBÉ · 1895 🎞️\nUna colazione di famiglia filmata dai Lumière. Ricostruzione fotografica interpretativa a partire dalla pellicola originale. Anteprima non pubblicata.",
      "TIKTOK":"Un pranzo in famiglia nel 1895. Il video è reale, la fotografia a colori è una ricostruzione IA. Episodio in revisione.",
      "YOUTUBE":"REPAS DE BÉBÉ · 1895 | Historical Motion & Photographic AI Test\n\nLouis Lumière. Fonte: "+PAGE+" · Pubblico dominio storico. Movimento reale. Colori e dettagli sono interpretazioni, non fotografie originali."}
    for key,val in post.items():(OUT/f"POST_{key}.txt").write_text(val+"\n",encoding="utf8")
    (OUT/"README_REVIEW_ONLY.txt").write_text("NOT APPROVED FOR PUBLICATION. Real historic movement + true AI still. Film by Louis Lumiere (d.1948). Public domain film, Commons source: "+PAGE+"\nNo Vidu. No new costs. 1080x1920 is upscaled presentation, not native 4K. Artist visual review still pending.\n",encoding="utf8")
    include=[MOVIE.name,"SOCIAL_COVER.jpg","ORIGINAL_VS_PHOTO_VISUAL_QA.jpg","VISUAL_REPORT.json","PHOTO_QA.json","RIGHTS.json",
             "README_REVIEW_ONLY.txt","POST_FACEBOOK.txt","POST_INSTAGRAM.txt","POST_TIKTOK.txt","POST_YOUTUBE.txt","GENERATIVE_PHOTO_REAL_CANDIDATE.png","ANCHOR_REAL_ORIGINAL_BW.png"]
    with zipfile.ZipFile(ZIP,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=4) as z:
        for name in include:z.write(OUT/name,arcname=name)
    with zipfile.ZipFile(ZIP) as z:assert z.testzip() is None
    write("DELIVERY.json",{"video_sha":sha(MOVIE),"zip_sha":sha(ZIP),"zip_crc_pass":True,
         "artistic_review":"PENDING","site_social_published":False,"new_paid_api_calls":0})
def main():
    try:
        source()
        original=readframe(ANCHOR)
        session,model=dd.download_model()
        write("COLOR_MODEL.json",model)
        base=colorize(original,dd.infer_ab(session,original))
        img=photo(base,original)
        report=export(img,session)
        package(report)
        print("SUCCESS_REAL_REVIEW_VIDEO",json.dumps(report),flush=True)
    except Exception as e:
        write("FAILURE.json",{"state":"NOT_DELIVERED","error":type(e).__name__+": "+str(e)[:700],
                              "paid_calls":0,"vidu_new_post":False,"published":False})
        print("REVIEW_PRODUCTION_FAIL",repr(e),flush=True)
        raise
if __name__=="__main__":main()
