#!/usr/bin/env python3
"""V103 China — REAL archival B/W -> actual I2I still video REVIEW ONLY.
No Vidu exists for China yet; do not mislabel this as a V98-compliant final.
"""
from __future__ import annotations
import hashlib,json,math,subprocess,wave,zipfile
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path("output/storia_china_1928_v103")
OUT=ROOT/"CHINA_1920S_V103_ACTUAL_I2I_REVIEW_NOT_FINAL.mp4"
SIZE=(720,1280);FPS=30
def sha(p):
    d=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):d.update(b)
    return d.hexdigest()
def corr(a,b):
    def small(im):
        g=cv2.cvtColor(cv2.resize(im,(90,160)),cv2.COLOR_BGR2GRAY)
        return cv2.GaussianBlur(g,(9,9),0).astype(np.float32).ravel()
    aa=small(a);bb=small(b)
    if aa.std()<1 or bb.std()<1:return 0.
    return float(np.corrcoef(aa,bb)[0,1])
def synth_audio(total,marks):
    sr=32000;n=int(total*sr)
    t=np.arange(n,dtype=np.float32)/sr
    audio=np.zeros(n,dtype=np.float32)
    notes=[(130.81,164.81,196.00),(146.83,185.00,220.0),(123.47,164.81,246.94),
           (110.0,164.81,220.0),(130.81,196.0,261.63)]
    for i,start in enumerate(marks):
        end=marks[i+1] if i+1<len(marks) else total
        mask=(t>=start)&(t<end);z=t[mask]-start
        for j,f in enumerate(notes[i]):
            audio[mask]+=(0.019-.003*j)*np.sin(2*np.pi*f*z+j*.8)
            audio[mask]+=0.0015*np.sin(2*np.pi*(f*2.012)*z+j*.4)
    # Slight original analog warmth, not any non-public-domain song.
    for mark in marks:
        d=t-mark;mask=(d>=0)&(d<.45)
        audio[mask]+=0.022*np.sin(2*np.pi*(93*d[mask]+30*d[mask]**2))*np.exp(-12*d[mask])
    audio=np.tanh(audio*2.0)
    audio*=np.minimum(1.,t/.45)*np.minimum(1.,np.maximum(0,(total-t)/1.05))
    wavefile=ROOT/"ORIGINAL_MUSIC_V103.wav"
    with wave.open(str(wavefile),"wb") as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr)
        stereo=np.column_stack((audio,np.roll(audio,round(sr*.017))*.94))
        w.writeframes((np.clip(stereo,-1,1)*24000).astype("<i2").tobytes())
    return wavefile
def label_first_frame(img):
    # Modern country symbol intentionally omitted until period-political attribution checked.
    text="CHINA  ·  c. 1928"
    cv2.putText(img,text,(36,84),cv2.FONT_HERSHEY_SIMPLEX,.66,(13,17,22),4,cv2.LINE_AA)
    cv2.putText(img,text,(36,84),cv2.FONT_HERSHEY_SIMPLEX,.66,(240,224,193),2,cv2.LINE_AA)
    return img
def montage():
    s=json.loads((ROOT/"SOURCE_MANIFEST.json").read_text())
    v=json.loads((ROOT/"I2I_STATUS.json").read_text())
    ready={x["scene"]:x for x in v.get("items",[]) if x.get("auto_geometry_color_gate_pass") is True}
    if len(ready)<4:
        print("V103_NO_RENDER_ONLY",len(ready),"of five genuine photographs available",flush=True)
        (ROOT/"RENDER_STATUS.json").write_text(json.dumps({
           "status":"BLOCKED_FEWER_THAN_FOUR_ACTUAL_REAL_I2I_IMAGES","ready":len(ready),
           "final_video":False,"vidu_missing":True,"published":False},indent=2)+"\n")
        return
    if len(s.get("scenes",[]))!=5:raise RuntimeError("Untrusted source scene layout")
    time_marks=[];sections=[];timeline=0.
    for row in s["scenes"]:
        n=row["scene"];duration=1.25+(.33 if n in ready else 0)+(2.1 if n in ready else .9)
        sections.append((n,row,duration))
        time_marks.append(timeline);timeline+=duration
    silent=ROOT/"SILENT_V103_PREVIEW.mp4"
    args=["ffmpeg","-nostdin","-y","-v","error","-f","rawvideo","-pix_fmt","bgr24",
          "-s","720x1280","-r",str(FPS),"-i","-","-an","-c:v","libx264",
          "-preset","veryfast","-crf","18","-pix_fmt","yuv420p","-movflags","+faststart",str(silent)]
    encoder=subprocess.Popen(args,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    rows=[]
    try:
        for n,row,duration in sections:
            source=ROOT/row["moving_original_excerpt"]
            cap=cv2.VideoCapture(str(source))
            count=round(1.25*FPS);last=None
            for k in range(count):
                ok,frame=cap.read()
                if not ok:raise RuntimeError("Original moving film unreadable")
                if frame.shape[:2]!=(1280,720):raise RuntimeError("Wrong scene geometry")
                if n==1 and k<round(.9*FPS):
                    frame=label_first_frame(frame)
                encoder.stdin.write(frame.tobytes());last=frame
            cap.release()
            reference=cv2.imread(str(ROOT/row["source_exact_frame_file"]))
            matched=corr(last,reference)
            if matched<.86:raise RuntimeError(f"SCENE_{n:02d}_NOT_SOURCE_LOCKED corr={matched:.3f}")
            entry={"scene":n,"archival_source_time_s":row["source_time_s"],
                   "source_exact_frame_sha256":sha(ROOT/row["source_exact_frame_file"]),
                   "original_motion_match_corr":round(matched,4),"real_color_i2i":False}
            if n in ready:
                photo=ROOT/ready[n]["generated_image"]
                if sha(photo)!=ready[n]["generated_sha256"]:raise RuntimeError("AI image changed")
                im=cv2.imread(str(photo))
                for fade in range(round(.33*FPS)):
                    ratio=(fade+1)/round(.33*FPS);ratio=ratio*ratio*(3-2*ratio)
                    encoder.stdin.write(cv2.addWeighted(last,1-ratio,im,ratio,0).tobytes())
                for k in range(round(2.1*FPS)):encoder.stdin.write(im.tobytes())
                entry["real_color_i2i"]=True;entry["photo_sha256"]=sha(photo)
            else:
                for k in range(round(.9*FPS)):encoder.stdin.write(last.tobytes())
            rows.append(entry)
    finally:
        encoder.stdin.close()
        err=encoder.stderr.read().decode(errors="replace")
        rc=encoder.wait()
        if rc:raise RuntimeError("Encoder failed: "+err[-600:])
    actual_frames=sum(round((1.25+(.33 if n in ready else 0)+(2.1 if n in ready else .9))*FPS) for n,_,_ in sections)
    total=actual_frames/FPS
    audio=synth_audio(total,time_marks)
    subprocess.run(["ffmpeg","-nostdin","-y","-v","error","-i",str(silent),"-i",str(audio),
                    "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","160k",
                    "-shortest","-movflags","+faststart",str(OUT)],check=True,timeout=120)
    subprocess.run(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(OUT),"-f","null","-"],
                   check=True,timeout=150)
    meta=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries",
      "format=duration:stream=codec_name,width,height","-of","json",str(OUT)]))
    codecs={stream.get("codec_name") for stream in meta["streams"]}
    if not {"h264","aac"}<=codecs:raise RuntimeError("Missing H.264 or AAC")
    cover=ROOT/"COVER_CHINA_1920S_V103.jpg"
    first=ready.get(1,ready[sorted(ready)[0]])
    image=Image.open(ROOT/first["generated_image"]).convert("RGB")
    brush=ImageDraw.Draw(image)
    try:font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",35)
    except OSError:font=ImageFont.load_default()
    brush.text((35,85),"CHINA · c. 1928",fill=(242,225,197),font=font,stroke_width=2,stroke_fill=(14,17,22))
    image.save(cover,quality=94)
    social={"FACEBOOK":"CHINA, c. 1928 — fotografie ricostruite da fotogrammi di una pellicola storica autentica. I colori sono una ricostruzione con IA, non una ripresa originale a colori. Anteprima tecnica: non è il filmato finale con Vidu.",
      "INSTAGRAM":"CHINA · c. 1928 🎞️ La storia rivive. Filmati autentici in B/N, fotogrammi ricostruiti a colori con AI. Anteprima in revisione. #LaStoriaRivive #RestauroStorico",
      "TIKTOK":"Cina negli anni Venti: il passato si ferma e torna a colori. Ricostruzione interpretativa AI da pellicola storica originale. Provino.",
      "YOUTUBE":"CHINA · c. 1928 — Restauro storico, anteprima tecnica (non finale). Filmato originale da Wikimedia Commons; colori e dettagli creati tramite ricostruzione AI interpretativa. Non è inclusa una scena Vidu in questo provino."}
    for platform,copy in social.items():(ROOT/f"POST_{platform}.txt").write_text(copy+"\n")
    report={"version":"V103_CHINA_REAL_I2I_PREVIEW",
            "status":"RENDERED_TECHNICAL_REVIEW_NO_VIDU_NOT_FINAL",
            "source":s["source_page"],"source_original_sha256":s["original_film_sha256"],
            "photos_actual_generations":len(ready),"photos_human_approved":0,
            "vidu_shots":0,"human_artistic_approval":False,
            "territorial_rights_italy_verified":False,"published_to_site":False,
            "published_to_social":False,"duration_s":round(float(meta["format"]["duration"]),3),
            "resolution":[720,1280],"fps":30,"video_sha256":sha(OUT),
            "color_reference_only_not_original":True,"scenes":rows}
    (ROOT/"RENDER_STATUS.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    zipfile_path=ROOT/"CHINA_1920S_V103_TECHNICAL_REVIEW_ANDROID.zip"
    with zipfile.ZipFile(zipfile_path,"w",zipfile.ZIP_DEFLATED) as z:
        for p in [OUT,cover,ROOT/"RENDER_STATUS.json",ROOT/"I2I_STATUS.json",
                  ROOT/"CHINA_V103_REAL_SOURCE_VS_REAL_I2I.jpg",
                  *[ROOT/f"POST_{x}.txt" for x in social]]:
            if p.is_file():z.write(p,p.name)
    with zipfile.ZipFile(zipfile_path) as z:
        if z.testzip():raise RuntimeError("Corrupt ZIP")
    print("V103_REAL_PREVIEW_RENDERED_MP4",OUT,"DURATION",report["duration_s"],
          "PHOTO",len(ready),"VIDU",0,"STILL_NEEDS_ARTISTIC_QA",flush=True)

if __name__=="__main__":montage()
