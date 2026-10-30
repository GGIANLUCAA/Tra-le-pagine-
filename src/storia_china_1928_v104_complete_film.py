#!/usr/bin/env python3
"""CHINA c.1928 V104: native-source B/W -> DDColor semantics -> learned RealESRGAN
photo freezes; fifth scene uses ACTUAL ORIGINAL FOOTAGE animated in semantic color,
NOT Vidu. Fail-closed quality and genuine downloadable MP4. No paid provider calls.

This is a technical video candidate until human identity, rights, Vidu V94 gates
have independently passed. Do not claim source 4K; export is upscaled 1080x1920.
"""
from __future__ import annotations
import hashlib,importlib.util,json,math,os,subprocess,time,wave,zipfile
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont

R=Path("output/storia_china_1928_v104")
SOURCE=Path("output/storia_china_1928_v103")
W,H,FPS=1080,1920,30
MASTER=R/"CHINA_1928_V104_FOTOGRAFIE_AI_COLOR_MOTION_NON_VIDU_REVIEW.mp4"
PREROLL=1.12;FADE=.32
HOLDS=[2.45,2.25,2.35,2.45]
FIFTH=5.4
def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()
def cmd(args,timeout=180):
    p=subprocess.run([str(a) for a in args],capture_output=True,text=True,timeout=timeout)
    if p.returncode:raise RuntimeError("CMD_FAILED "+str(args[:6])+" "+p.stderr[-900:])
    return p.stdout
def load_module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def correlations(a,b):
    def g(z):
        y=cv2.cvtColor(cv2.resize(z,(90,160)),cv2.COLOR_BGR2GRAY)
        return cv2.GaussianBlur(y,(7,7),0).astype(np.float32).ravel()
    x,y=g(a),g(b)
    return float(np.corrcoef(x,y)[0,1]) if x.std() and y.std() else 0.
def semantic_color(dd,model,img):
    # A source-preserving semantic chroma suggestion, NOT fake reconstruction.
    small=cv2.resize(img,(720,576),interpolation=cv2.INTER_AREA)
    ab=dd.infer_ab(model,small)
    l=dd.l_channel(img)
    chroma=cv2.resize(ab,(img.shape[1],img.shape[0]),interpolation=cv2.INTER_LINEAR)
    lab=np.dstack((l,np.clip(chroma*1.05,-110,110))).astype(np.float32)
    rgb=np.clip(cv2.cvtColor(lab,cv2.COLOR_LAB2RGB)*255,0,255).astype(np.uint8)
    return cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR)
def refine_esrgan(v62,session,color):
    base=cv2.resize(color,(240,427),interpolation=cv2.INTER_AREA)
    high=v62.esrgan_4x(session,base)
    # Real learned superresolution: 960x1708 -> 1080x1920, not native 4K.
    high=cv2.resize(high,(W,H),interpolation=cv2.INTER_LANCZOS4)
    # Restrained grain, no object or human synthesis.
    return high
def authentic_end_frame(clip):
    cap=cv2.VideoCapture(str(clip))
    if not cap.isOpened():raise RuntimeError("Real archive clip absent")
    n=round(cap.get(cv2.CAP_PROP_FRAME_COUNT));cap.set(cv2.CAP_PROP_POS_FRAMES,max(0,n-1))
    ok,last=cap.read();cap.release()
    if not ok or last.shape[:2]!=(1280,720):raise RuntimeError("Original archive last frame not decodable")
    return last
def music(total,marks):
    sr=44100
    t=np.arange(round(total*sr),dtype=np.float32)/sr
    sound=np.zeros_like(t)
    chords=[[110.0,164.81,220.0],[123.47,185.0,246.94],[130.81,174.61,261.63],
            [110.0,146.83,220.0],[123.47,196.0,246.94]]
    for k,start in enumerate(marks):
        stop=marks[k+1] if k+1<len(marks) else total
        mask=(t>=start)&(t<stop);z=t[mask]-start
        for j,f in enumerate(chords[k]):
            drift=np.sin(2*np.pi*(.13+j*.015)*z)
            sound[mask]+=(.018-.003*j)*np.sin(2*np.pi*f*z+.09*drift+j*.6)
            sound[mask]+=.003*np.sin(2*np.pi*(f*2.003)*z+j*.2)
        sound[mask]+=.0025*np.sin(2*np.pi*(37+3*k)*z)
    for mark in marks:
        d=t-mark;sel=(d>=0)&(d<.55)
        sound[sel]+=.03*np.sin(2*np.pi*(72*d[sel]+38*d[sel]**2))*np.exp(-9*d[sel])
    sound=np.tanh(sound*2)
    sound*=np.minimum(1.,t/.7)*np.minimum(1.,np.maximum(0.,(total-t)/.95))
    dst=R/"ORIGINAL_SOUNDTRACK.wav"
    with wave.open(str(dst),"wb") as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr)
        stereo=np.column_stack((sound,np.roll(sound,int(.018*sr))*.96))
        w.writeframes((stereo*19500).astype("<i2").tobytes())
    return dst
def title(frame,frame_ix):
    if frame_ix>round(FPS*.9):return frame
    out=frame.copy()
    # Small serif lettering and no opaque panel; avoids title bar from rejected V95.
    txt="CHINA  ·  c. 1928"
    font=cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(out,txt,(57,118),font,1.02,(15,19,25),4,cv2.LINE_AA)
    cv2.putText(out,txt,(57,118),font,1.02,(246,235,215),2,cv2.LINE_AA)
    return out
def candidate_photos():
    R.mkdir(parents=True,exist_ok=True)
    source=json.loads((SOURCE/"SOURCE_MANIFEST.json").read_text())
    if source.get("version")!="V103_CHINA_1920S_SOURCE_SELECT" or len(source.get("scenes",[]))!=5:
        raise RuntimeError("V103 original archival verification absent")
    movie=SOURCE/"ORIGINAL_ARCHIVE.webm"
    if not movie.is_file() or sha(movie)!=source["original_film_sha256"]:
        raise RuntimeError("Source actual movie missing or changed")
    dd=load_module(Path("src/storia_rivive_real_ai_v60.py"),"v104_ddcolor")
    v62=load_module(Path("src/storia_rivive_real_photo_ai_v62.py"),"v104_esrgan")
    color_model,color_meta=dd.download_model()
    esrgan_model,esrgan_meta=v62.setup_upscaler()
    records=[]
    contact=Image.new("RGB",(4*264,2*485),(13,17,20));brush=ImageDraw.Draw(contact)
    for i,rec in enumerate(source["scenes"][:4]):
        n=rec["scene"];clip=SOURCE/rec["moving_original_excerpt"]
        if sha(clip)!=rec["original_motion_sha256"]:
            raise RuntimeError("Historical moving source hash changed "+str(n))
        genuine=authentic_end_frame(clip)
        bw=R/f"SCENE_{n:02d}_EXACT_LAST_MOVING_FRAME.png"
        cv2.imwrite(str(bw),genuine,[cv2.IMWRITE_PNG_COMPRESSION,3])
        print("REAL_SOURCE_BW_FRAME",n,sha(bw),flush=True)
        chroma=semantic_color(dd,color_model,genuine)
        photo=refine_esrgan(v62,esrgan_model,chroma)
        corr=correlations(cv2.resize(genuine,(W,H)),photo)
        sat=float(np.median(cv2.cvtColor(photo,cv2.COLOR_BGR2HSV)[:,:,1]))
        if corr<.86 or not 10<sat<185:
            raise RuntimeError(f"SCENE_{n:02d}_REJECT_PHOTO_GEOMETRY_OR_COLOR corr={corr:.3f} sat={sat:.2f}")
        fname=R/f"SCENE_{n:02d}_LEARNED_COLOR_PHOTO.png"
        cv2.imwrite(str(fname),photo,[cv2.IMWRITE_PNG_COMPRESSION,3])
        for row,img in enumerate((genuine,photo)):
            preview=Image.fromarray(cv2.cvtColor(img,cv2.COLOR_BGR2RGB))
            preview=preview.resize((256,456))
            x=i*264+3;y=row*485+23
            contact.paste(preview,(x,y))
            brush.text((x,y-17),f"Scene {n}: "+("film original B/W" if row==0 else "DDColor + RealESRGAN"),fill=(232,232,226))
        recx={"scene":n,"real_video_SHA256":sha(clip),"original_exact_frame_SHA256":sha(bw),
              "real_AI_semantic_color_model":color_meta["model_id"],"real_AI_learned_detail_model":esrgan_meta["repo"],
              "restored_photo":fname.name,"restored_photo_SHA256":sha(fname),
              "grayscale_geometry_corr":round(corr,4),"median_saturation":round(sat,2),
              "face_identity_human_QA":False,"photographic_generation":False,
              "true_AI_photo_restoration_semantic_chroma_and_learned_upscale":True}
        records.append(recx)
        print("V104_REAL_RESTORATION",n,"corr",round(corr,3),"sat",round(sat,2),flush=True)
    contact.save(R/"REAL_SOURCE_VS_NEURAL_RESTORATION.jpg",quality=95)
    record={"version":"V104_SOURCED_RESTORATION","source_video_SHA256":source["original_film_sha256"],
            "photos_technically_ready":len(records),"photos_generatively_approved":0,
            "Vidu_clip_present":False,"source_native_resolution":source["source_raster_px"],
            "AI_photo_details_historical_fact":False,"records":records}
    (R/"PHOTO_QA.json").write_text(json.dumps(record,indent=2,ensure_ascii=False)+"\n")
    return source,record,dd,color_model
def fifth_color_motion(dd,model,source):
    # The moving color passage uses ONLY the real archival frames after freeze,
    # NOT a Vidu-generated video. Clearly labeled as such in report.
    fifth=source["scenes"][4]
    left=fifth["source_native_crop"]["left"];cropw=fifth["source_native_crop"]["width"]
    top=fifth["source_native_crop"].get("top",16);bottom=fifth["source_native_crop"].get("bottom_removed",58)
    original=SOURCE/"ORIGINAL_ARCHIVE.webm"
    start=float(fifth["source_time_s"])-PREROLL
    out=R/"SCENE_05_LONG_REAL_MOVING_BW.mp4"
    cmd(["ffmpeg","-nostdin","-y","-v","error","-ss",start,"-i",original,
         "-t",FIFTH,"-vf",f"crop={cropw}:ih-{top+bottom}:{left}:{top},scale=720:1280:flags=lanczos,fps=30",
         "-an","-c:v","libx264","-crf","19","-preset","veryfast","-pix_fmt","yuv420p",out],140)
    cap=cv2.VideoCapture(str(out))
    if not cap.isOpened():raise RuntimeError("Fifth real moving color source missing")
    return cap,out
def make_video(source,photo_qa,dd,model):
    no_audio=R/"V104_VIDEO_ONLY.mp4"
    cap5,long_path=fifth_color_motion(dd,model,source)
    # Actual scene timing varies slightly to favor the human face and movement.
    scene_lengths=[(round(PREROLL*FPS)+round(FADE*FPS)+round(x*FPS)) for x in HOLDS]
    scene_lengths.append(round(FIFTH*FPS))
    count_frames=sum(scene_lengths)
    seconds=count_frames/FPS
    if not 17<=seconds<=27:raise RuntimeError("Historical edit outside duration constraints")
    marks=[];at=0
    for n in scene_lengths:
        marks.append(at/FPS);at+=n
    enc=subprocess.Popen(["ffmpeg","-nostdin","-y","-v","error","-f","rawvideo",
           "-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
           "-an","-c:v","libx264","-preset","medium","-crf","17",
           "-pix_fmt","yuv420p","-movflags","+faststart",str(no_audio)],
           stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    n_written=0;reveal_marks=[]
    try:
        for j,rec in enumerate(photo_qa["records"]):
            original_clip=SOURCE/f"SCENE_{j+1:02d}_SOURCE_MOVING_BW.mp4"
            sourcecap=cv2.VideoCapture(str(original_clip))
            orig_last=cv2.imread(str(R/f"SCENE_{j+1:02d}_EXACT_LAST_MOVING_FRAME.png"))
            photo=cv2.imread(str(R/rec["restored_photo"]))
            if orig_last is None or photo is None:raise RuntimeError("Missing real exact image")
            frames=[]
            while True:
                ok,f=sourcecap.read()
                if not ok:break
                frames.append(f)
            sourcecap.release()
            if len(frames)<round(PREROLL*FPS):raise RuntimeError("Original moving scene too short")
            motion=frames[-round(PREROLL*FPS):]
            if correlations(motion[-1],orig_last)<.995:raise RuntimeError("Freeze source mismatch")
            for ix,f in enumerate(motion):
                frame=cv2.resize(f,(W,H),interpolation=cv2.INTER_LANCZOS4)
                if j==0:frame=title(frame,ix)
                enc.stdin.write(frame.tobytes());n_written+=1
            for n in range(round(FADE*FPS)):
                a=(n+1)/round(FADE*FPS);a=a*a*(3-2*a)
                start=cv2.resize(orig_last,(W,H),interpolation=cv2.INTER_CUBIC)
                combined=cv2.addWeighted(start,1-a,photo,a,0)
                enc.stdin.write(combined.tobytes());n_written+=1
            for n in range(round(HOLDS[j]*FPS)):
                enc.stdin.write(photo.tobytes());n_written+=1
            reveal_marks.append({"scene":j+1,"bw_motion_s":PREROLL,"color_reveal_s":FADE,
                                 "restored_hold_s":HOLDS[j],"exact_original_sha256":rec["original_exact_frame_SHA256"],
                                 "restored_photo_sha256":rec["restored_photo_SHA256"]})
            print("V104_EDIT_REAL_FILM_TO_LEARNED_PHOTO",j+1,flush=True)
        # Scene 5: original B/W motion, then color revealed on that very SAME moving movie.
        key_ab=None;anchor_gray=None;key_frame=0
        first_source=None;total_5=scene_lengths[4]
        for ix in range(total_5):
            ok,src=cap5.read()
            if not ok:raise RuntimeError("Fifth archival source clip truncated")
            if first_source is None:first_source=src.copy()
            if ix<round(PREROLL*FPS):
                frame=cv2.resize(src,(W,H),interpolation=cv2.INTER_LANCZOS4)
            else:
                gray=cv2.cvtColor(cv2.resize(src,(320,256)),cv2.COLOR_BGR2GRAY)
                if key_ab is None or ix-key_frame>=round(.8*FPS):
                    key_ab=dd.infer_ab(model,cv2.resize(src,(720,576)))
                    anchor_gray=gray;key_frame=ix
                    ab=key_ab
                else:
                    # Chroma motion follows actual original optical flow. No made-up video.
                    flow=cv2.calcOpticalFlowFarneback(gray,anchor_gray,None,.5,3,13,3,5,1.1,0)
                    yy,xx=np.mgrid[:256,:320].astype(np.float32)
                    ab=cv2.remap(key_ab,xx+flow[:,:,0],yy+flow[:,:,1],cv2.INTER_LINEAR,
                                 borderMode=cv2.BORDER_REFLECT_101)
                l=dd.l_channel(src)
                full_ab=cv2.resize(ab,(720,1280))
                lab=np.dstack((l,np.clip(full_ab*1.05,-110,110))).astype(np.float32)
                rgb=np.clip(cv2.cvtColor(lab,cv2.COLOR_LAB2RGB)*255,0,255).astype(np.uint8)
                colored=cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR)
                interval=(ix-round(PREROLL*FPS))/FPS
                a=np.clip(interval/.8,0,1);a=a*a*(3-2*a)
                mixed=cv2.addWeighted(src,1-a,colored,a,0)
                frame=cv2.resize(mixed,(W,H),interpolation=cv2.INTER_LANCZOS4)
            enc.stdin.write(frame.tobytes());n_written+=1
        cap5.release()
        reveal_marks.append({"scene":5,"effect":"REAL_MOVING_ARCHIVAL_FOOTAGE_COLORIZED_BY_DDCOLOR_NO_VIDU",
                             "film_source_video_sha256":sha(long_path),
                             "vidu_provider_task":None})
    finally:
        cap5.release()
        if enc.stdin:enc.stdin.close()
        err=enc.stderr.read().decode(errors="replace")
        rc=enc.wait()
        if rc:raise RuntimeError("Video encoder failed "+err[-850:])
    if n_written!=count_frames:raise RuntimeError("Final video frame count mismatch")
    track=music(seconds,marks)
    cmd(["ffmpeg","-nostdin","-y","-v","error","-i",no_audio,"-i",track,"-map","0:v:0","-map","1:a:0",
          "-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",MASTER],180)
    cmd(["ffmpeg","-nostdin","-v","error","-xerror","-i",MASTER,"-f","null","-"],200)
    info=json.loads(cmd(["ffprobe","-v","error","-show_entries","format=duration,size:stream=codec_name,width,height,avg_frame_rate","-of","json",MASTER]))
    codecs={s.get("codec_name") for s in info["streams"]}
    if not {"h264","aac"}.issubset(codecs):raise RuntimeError("Audio or video missing")
    video=next(s for s in info["streams"] if s.get("width"))
    if (video["width"],video["height"])!=(W,H):raise RuntimeError("Resolution wrong")
    total=float(info["format"]["duration"])
    if abs(total-seconds)>.3:raise RuntimeError("Audio/video timeline drift")
    return reveal_marks,total,info
def deliver(source,photo_qa,marks,seconds,meta):
    # Contact sheet from actual final MP4, not merely design intent.
    cap=cv2.VideoCapture(str(MASTER))
    canvas=Image.new("RGB",(5*260,2*475),(13,17,21))
    draw=ImageDraw.Draw(canvas)
    timeline=0.0
    for i in range(5):
        bw=timeline+.52
        color=timeline+(PREROLL+FADE+.70 if i<4 else PREROLL+2.2)
        for row,t in enumerate([bw,color]):
            cap.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,f=cap.read()
            if not ok:raise RuntimeError("Final MP4 contact extraction failed")
            img=Image.fromarray(cv2.cvtColor(f,cv2.COLOR_BGR2RGB)).resize((254,450))
            x=i*260+3;y=row*475+21
            canvas.paste(img,(x,y));draw.text((x,y-17),f"SCENE {i+1} "+("ORIGINAL B/W" if row==0 else
                  ("LEARNED PHOTO" if i<4 else "REAL CHROMA MOTION (NOT VIDU)")),fill=(245,239,222))
        timeline+=PREROLL+FADE+HOLDS[i] if i<4 else FIFTH
    cap.release()
    canvas.save(R/"ACTUAL_MP4_FIVE_BEFORE_AFTER_CONTACT.jpg",quality=92)
    cover=cv2.imread(str(R/"SCENE_01_LEARNED_COLOR_PHOTO.png"))
    cv2.putText(cover,"CHINA  ·  c. 1928",(52,105),cv2.FONT_HERSHEY_SIMPLEX,1.05,(14,17,22),4,cv2.LINE_AA)
    cv2.putText(cover,"CHINA  ·  c. 1928",(52,105),cv2.FONT_HERSHEY_SIMPLEX,1.05,(244,226,197),2,cv2.LINE_AA)
    cv2.imwrite(str(R/"COVER.jpg"),cover,[cv2.IMWRITE_JPEG_QUALITY,94])
    title="CHINA · c. 1928"
    text={
    "FACEBOOK":title+"\nUn frammento autentico di vita quotidiana negli anni Venti: la vecchia pellicola in bianco e nero si ferma e lascia spazio a quattro fotografie ricostruite a colori. Nell'ultima scena, il movimento è ancora quello della pellicola originale, restaurato digitalmente nel colore. I colori sono interpretazioni AI, non registrazioni storiche originali. Materiale da archivio Wikimedia Commons, diritti da verificare per l'Italia. Anteprima tecnica, non master editoriale pubblicato.",
    "INSTAGRAM":title+" 🎞️ Cinque momenti autentici. Quattro fotografie restaurate AI e una sequenza d'archivio realmente in movimento con colore ricostruito. Colori interpretativi, riprese originali B/N. Anteprima in revisione. #LaStoriaRivive #Storia #Archivio",
    "TIKTOK":"CHINA · c. 1928. Volti e strade del passato, dal vero bianco e nero a fotografie restaurate AI. Colori interpretativi. Non è ancora la versione finale Vidu."
    }
    for site,desc in text.items():(R/f"POST_{site}.txt").write_text(desc+"\n",encoding="utf-8")
    report={"version":"V104_TRUE_NEURAL_COLOR_FILM_DRAFT","original_source_sha256":source["original_film_sha256"],
       "source_date":"1920s circa 1928, not exact capture date",
       "source_link":source["source_page"],"source_raster":source["source_raster_px"],
       "AI_reconstructed_not_historical_color":True,
       "true_real_learned_photo_restorations":4,"generative_facial_reconstruction":False,
       "real_Vidu_clip_present":False,"fifth_scene_movement":"real archival source semantically colorized, NOT Vidu",
       "no_paid_API_calls":True,"human_visual_approval":False,
       "V94_V96_V99_final_release_gate_passed":False,"territorial_rights_Italy_reviewed":False,
       "has_no_source_invented_people_guarantee":False,
       "duration_s":seconds,"resolution":[W,H],"frame_rate":FPS,
       "h264_and_aac_verified":True,"master_sha256":sha(MASTER),
       "original_soundtrack":"Procedurally synthesized original audio", "scene_log":marks,
       "release_status":"FULL_PLAYABLE_EDITORIAL_CANDIDATE_NOT_V94_FINAL"}
    (R/"TECHNICAL_REVIEW.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    outzip=R/"CHINA_1928_V104_EDITORIAL_CANDIDATE_ANDROID.zip"
    with zipfile.ZipFile(outzip,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=4) as z:
        for file in [MASTER,R/"TECHNICAL_REVIEW.json",R/"COVER.jpg",
                     R/"REAL_SOURCE_VS_NEURAL_RESTORATION.jpg",
                     R/"ACTUAL_MP4_FIVE_BEFORE_AFTER_CONTACT.jpg",R/"PHOTO_QA.json",
                     *[R/f"POST_{x}.txt" for x in text]]:
            z.write(file,file.name)
    with zipfile.ZipFile(outzip) as z:
        if z.testzip():raise RuntimeError("Download ZIP corrupt")
    print("V104_PLAYABLE_ACTUAL_COLOR_FILM_CANDIDATE",MASTER,
          "DURATION",round(seconds,3),"BYTES",MASTER.stat().st_size,
          "VIDU_PRESENT",False,"V94_FINAL",False,flush=True)
def main():
    source,photos,dd,model=candidate_photos()
    marks,duration,meta=make_video(source,photos,dd,model)
    deliver(source,photos,marks,duration,meta)
if __name__=="__main__":main()
