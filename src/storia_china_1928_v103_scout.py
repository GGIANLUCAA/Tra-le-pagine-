#!/usr/bin/env python3
"""CHINA c.1928 V103: original-footage scouting and SHA-locked true-frame clips.
Does not generate AI, spend credits, claim territorial rights, or publish.
"""
from __future__ import annotations
import argparse, hashlib, json, math, subprocess, urllib.parse, urllib.request
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw

PAGE="https://commons.wikimedia.org/wiki/File:China_and_the_Chinese%2C_1920s_-_Travelfilmarchive.webm"
OUT=Path("output/storia_china_1928_v103")
UA="TraLePagine-StoriaResearch/1.0 (GitHub GGIANLUCAA/Tra-le-pagine-)"
def sha(path):
    d=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):d.update(b)
    return d.hexdigest()
def run(args,timeout=180):
    p=subprocess.run(args,text=True,capture_output=True,timeout=timeout)
    if p.returncode:raise RuntimeError(" ".join(args[:4])+": "+p.stderr[-500:])
    return p.stdout
def download():
    OUT.mkdir(parents=True,exist_ok=True)
    name="File:China and the Chinese, 1920s - Travelfilmarchive.webm"
    endpoint="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({
      "action":"query","format":"json","formatversion":"2","titles":name,
      "prop":"imageinfo","iiprop":"url|size|extmetadata"})
    with urllib.request.urlopen(urllib.request.Request(endpoint,headers={"User-Agent":UA}),timeout=30) as f:
        response=json.load(f)
    info=response["query"]["pages"][0]["imageinfo"][0]
    url=info["url"]; u=urllib.parse.urlsplit(url)
    if u.scheme!="https" or u.netloc!="upload.wikimedia.org" or not u.path.endswith(".webm"):
        raise ValueError("Source media not a Wikimedia-hosted original WEBM")
    if not 0<int(info["size"])<60_000_000:raise ValueError("Source size not expected")
    dest=OUT/"ORIGINAL_ARCHIVE.webm"
    if dest.is_file() and dest.stat().st_size==info["size"]:
        pass
    else:
        with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":UA}),timeout=100) as f, dest.open("wb") as o:
            n=0
            while True:
                b=f.read(1<<20)
                if not b:break
                n+=len(b)
                if n>60_000_000:raise ValueError("Excessive archive media bytes")
                o.write(b)
        if n!=info["size"]:raise RuntimeError("Download truncated")
    probes=json.loads(run(["ffprobe","-v","error","-show_entries","format=duration:stream=codec_name,width,height,r_frame_rate","-of","json",str(dest)]))
    video=next(x for x in probes["streams"] if x.get("width"))
    if video["width"]<600 or video["height"]<400:raise ValueError("Source below archival raster threshold")
    return dest,info,video,float(probes["format"]["duration"])

def boxfocus(frame):
    h,w=frame.shape[:2]
    # A vertical crop of the native film is unavoidable. Keep subject-centering consistent.
    detector=cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_frontalface_default.xml")
    gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    faces=detector.detectMultiScale(gray,scaleFactor=1.2,minNeighbors=5,minSize=(28,28)) if not detector.empty() else []
    center=float(w/2)
    if len(faces):
        faces=sorted(faces,key=lambda z:z[2]*z[3],reverse=True)
        x,y,fw,fh=faces[0];center=float(x+fw/2)
    cropw=min(w,round(h*9/16));left=int(max(0,min(w-cropw,center-cropw/2)))
    return left,cropw,len(faces)

def vertical(frame,left,width):
    # Pixel-preserving geometry, no new faces/objects. Native crop 270x480 -> 720x1280.
    h,w=frame.shape[:2]
    piece=frame[:,left:left+width]
    return cv2.resize(piece,(720,1280),interpolation=cv2.INTER_CUBIC)

def scout():
    source,info,video,duration=download()
    cap=cv2.VideoCapture(str(source))
    if not cap.isOpened():raise RuntimeError("Could not decode real source")
    samples=[]
    cascade=cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_frontalface_default.xml")
    for t in np.arange(12,min(duration-4,470),5):
        cap.set(cv2.CAP_PROP_POS_MSEC,float(t)*1000);ok,raw=cap.read()
        if not ok:continue
        gr=cv2.cvtColor(raw,cv2.COLOR_BGR2GRAY)
        low=cv2.resize(gr,(150,100))
        brightness=float(np.mean(low));std=float(np.std(low))
        if brightness<36 or brightness>224 or std<25:continue
        detail=float(cv2.Laplacian(low,cv2.CV_32F).var())
        people=cascade.detectMultiScale(gr,1.2,5,minSize=(28,28)) if not cascade.empty() else []
        cap.set(cv2.CAP_PROP_POS_MSEC,float(t+.7)*1000);ok2,next_frame=cap.read()
        if not ok2:continue
        movement=float(np.mean(cv2.absdiff(cv2.resize(gr,(150,100)),cv2.resize(cv2.cvtColor(next_frame,cv2.COLOR_BGR2GRAY),(150,100)))))
        if movement<2 or movement>90:continue
        score=(min(detail/200,2)*.26+min(std/60,2)*.23+
               min(movement/19,2)*.30+min(len(people),3)*.32)
        # Keep all candidates for provenance; these scores are not artistic approvals.
        samples.append((float(score),float(t),raw,detail,movement,len(people)))
    if len(samples)<5:raise RuntimeError("Not enough usable genuine moving film scenes")
    overview=Image.new("RGB",(1400,math.ceil(min(60,len(samples))/6)*166),(16,19,23))
    draw=ImageDraw.Draw(overview)
    ranked_by_time=sorted(samples,key=lambda x:x[1])
    choose_every=max(1,math.ceil(len(ranked_by_time)/60))
    for j,a in enumerate(ranked_by_time[::choose_every][:60]):
        score,t,raw,_,_,faces=a
        image=Image.fromarray(cv2.cvtColor(raw,cv2.COLOR_BGR2RGB))
        image.thumbnail((222,126))
        x=(j%6)*233+4;y=(j//6)*166+22
        overview.paste(image,(x,y))
        draw.text((x,y-17),f"t={t:.0f}s faces~{faces}",fill=(232,232,226))
    overview.save(OUT/"CHINA_1920S_SOURCE_OVERVIEW.jpg",quality=90)
    # Diverse source periods, distinct original frames and actual movement.
    picked=[]
    for item in sorted(samples,key=lambda x:x[0],reverse=True):
        if all(abs(item[1]-p[1])>=28 for p in picked):
            picked.append(item)
        if len(picked)==5:break
    if len(picked)<5:raise RuntimeError("Five temporally distinct original shots unavailable")
    picked.sort(key=lambda x:x[1])
    data=[]
    for idx,(score,t,frame,detail,movement,people) in enumerate(picked,1):
        left,width,faces=boxfocus(frame)
        source_frame=OUT/f"SCENE_{idx:02d}_EXACT_BW.png"
        cv2.imwrite(str(source_frame),vertical(frame,left,width))
        bw_clip=OUT/f"SCENE_{idx:02d}_SOURCE_MOVING_BW.mp4"
        # The selected frame is the end of the original moving excerpt.
        run(["ffmpeg","-nostdin","-y","-v","error","-ss",str(max(0,t-1.25)),"-i",str(source),
            "-t","1.25","-vf",f"crop={width}:ih:{left}:0,scale=720:1280:flags=lanczos,fps=30",
            "-an","-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p",str(bw_clip)],120)
        data.append({"scene":idx,"source_time_s":t,"source_native_crop":{"left":left,"width":width},
            "source_exact_frame_file":source_frame.name,"source_exact_frame_sha256":sha(source_frame),
            "moving_original_excerpt":bw_clip.name,"original_motion_sha256":sha(bw_clip),
            "detected_faces_advisory":faces,"motion_score":round(movement,2),
            "source_detail_advisory":round(detail,2),
            "historically_distinct_shot_verified":False,"human_scene_approved":False})
    cap.release()
    manifest={"version":"V103_CHINA_1920S_SOURCE_SELECT","status":"REAL_ORIGINAL_BW_PREPARED_NEEDS_HUMAN_REVIEW",
      "subject":"China in the 1920s (source catalog dates 1928)",
      "display_date":"c. 1928","country_flag":"OMITTED_UNTIL_HISTORICALLY_VERIFIED",
      "source_page":PAGE,"original_film_file":source.name,
      "original_film_sha256":sha(source),"source_raster_px":[video["width"],video["height"]],
      "full_film_duration_s":duration,"source_license_us_and_china":"WIKIMEDIA_PD_CLAIM_NEEDS_ITALIAN_REVIEW",
      "copyright_italy_checked":False,"right_to_publish_on_social":False,
      "scenes":data,"candidate_count":len(samples),
      "no_paid_calls":True,"restored_photos_created":0,"vidu_clip_created":False,
      "editorial_approval":False}
    (OUT/"SOURCE_MANIFEST.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n")
    print("CHINA_V103_SOURCE_PREPARED",len(data),"original_frames",len(samples),"sha",sha(source),flush=True)
    return manifest

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--run",action="store_true")
    args=p.parse_args();scout()
