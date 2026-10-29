#!/usr/bin/env python3
"""V90 new authentic 1900 Cléo de Mérode dance film, 4 source->AI photo scenes + ONE Vidu moving shot.
Source is Wikimedia Commons PDM file; AI details hypothetical. No repeated paid POST.
"""
import base64, hashlib, json, os, pathlib, subprocess, time, urllib.request, wave, math, zipfile, shutil
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageStat
ROOT=pathlib.Path("output/storia_cleo_1900_v90")
ROOT.mkdir(parents=True,exist_ok=True)
REPO=os.environ.get("GITHUB_REPOSITORY","GGIANLUCAA/Tra-le-pagine-")
SRC_URL="https://commons.wikimedia.org/wiki/Special:Redirect/file/Danse_javanaise_%281900%29.webm"
SRC=ROOT/"DANSE_JAVANAISE_1900_SOURCE.webm"
LEDGER="queue/vidu_api_attempts/CLEO_DANSE_1900_V90_ONCE_20261029.json"
FPS,W,H=30,720,1280
CLIP_TIMES=[20.0,56.0,92.0,128.0,163.0]
MODEL="viduq2-pro-fast"; MAX_CREDITS=16
KEY=os.environ.get("VIDU_API_KEY","")
TAG="la-storia-rivive-cleo-1900-v90-ai-photo-vidu-test"
PROMPT=("ONE uninterrupted live-action documentary movement, color photograph of Cléo de Mérode "
"performing a graceful Javanese dance in the historic theatrical setting of Paris Expo 1900. "
"Use the supplied exact original-frame-anchored restored image as the camera framing. "
"Keep the SAME performer and exact face, outfit, arms, fingers, palms, hairstyle, stage, painted palm backdrop and objects. "
"Her hands and arms move slowly and organically in a refined authentic dance. "
"Camera stationary, no theatrical pans, natural period costume fabric and skin color, consistent physical anatomy, "
"no extra limbs, no new spectators, no object morphing, no cut, no caption, no logos, no music. "
"Rich natural colors, refined photographic sharpness without plastic CGI appearance.")
def cmd(args,timeout=180):
    p=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=timeout)
    if p.returncode:raise RuntimeError("Command failed "+str(args[:6])+" "+p.stderr[-1400:])
    return p.stdout
def digest(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for c in iter(lambda:f.read(1048576),b""):h.update(c)
    return h.hexdigest()
def writej(p,obj):
    pathlib.Path(p).write_text(json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
def api(path,body=None,method="GET",timeout=60):
    req=urllib.request.Request("https://api.vidu.com"+path,
        data=(json.dumps(body).encode() if body is not None else None),
        headers={"Authorization":"Token "+KEY,"Content-Type":"application/json","Accept":"application/json"},method=method)
    with urllib.request.urlopen(req,timeout=timeout) as r:return json.loads(r.read(2500000))
def balance():
    d=api("/ent/v2/credits")
    xs=d.get("remains",d.get("remaining_credits"))
    if not isinstance(xs,list) or not xs:raise RuntimeError("Vidu credits unavailable: stop")
    nums=[r.get("credit_remain") for r in xs if isinstance(r,dict)]
    if not nums or any(type(n) not in (int,float) or n<0 for n in nums):raise RuntimeError("Invalid Vidu credits")
    return sum(nums)
def frame_at(t):
    cap=cv2.VideoCapture(str(SRC));cap.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,fr=cap.read();cap.release()
    if not ok:raise RuntimeError("Archival frame missing "+str(t))
    h,w=fr.shape[:2];cw=int(h*9/16)
    # Allow entire dancer's gesture, prioritize performer center.
    left=(w-cw)//2
    im=fr[:,left:left+cw]
    return cv2.resize(im,(W,H),interpolation=cv2.INTER_LANCZOS4)
def download_and_scout():
    cmd(["curl","-fsSL","--retry","2","--max-time","180","-A","TraLePagine-History/1.0",SRC_URL,"-o",str(SRC)],210)
    if SRC.stat().st_size<6000000:raise RuntimeError("Missing original historical archival film")
    info=json.loads(cmd(["ffprobe","-v","error","-show_entries","format=duration:stream=width,height,r_frame_rate","-of","json",str(SRC)]))
    if float(info["format"]["duration"])<170:raise RuntimeError("Source duration unexpected")
    if not any(x.get("width",0)>=1200 and x.get("height",0)>=700 for x in info["streams"]):
        raise RuntimeError("Historical video resolution insufficient")
    stills=[]
    for i,t in enumerate(CLIP_TIMES):
        fr=frame_at(t)
        cv2.imwrite(str(ROOT/f"ARCHIVE_FRAME_{i+1:02}.png"),fr)
        stills.append(fr)
    # The frames must represent genuinely changing historic motion; no repeated zoom crops.
    for a,b in zip(stills,stills[1:]):
        g1=cv2.resize(cv2.cvtColor(a,cv2.COLOR_BGR2GRAY),(80,144)).astype(np.float32)
        g2=cv2.resize(cv2.cvtColor(b,cv2.COLOR_BGR2GRAY),(80,144)).astype(np.float32)
        diff=float(np.mean(np.abs(g1-g2)))
        if diff<1.1:raise RuntimeError("Near duplicate dance pose, do not pad video")
    print("SOURCE_AUTHENTIC_AND_DISTINCT",SRC.stat().st_size,flush=True)
    return stills
def restoration(stills):
    from gradio_client import Client, handle_file
    client=Client("finegrain/finegrain-image-enhancer",verbose=False)
    out=[]
    for i,src in enumerate(stills):
        fn=ROOT/f"ARCHIVE_FRAME_{i+1:02}.png"
        prompt=("Source-faithful documentary restoration of a precisely 1900 historical dancer. "
            "Original person Cléo de Mérode in Javanese costume against painted theatrical palms. "
            "Natural believable full-color documentary photograph, fine textile, accurate human anatomy, "
            "natural skin and hair, preserve EVERY original contour, gesture, number of people, outfit details, and backdrop.")
        negative=("extra people, extra fingers, different face, invented scenery, face swap, deformed hands, "
                  "plastic skin, fake theatrical lighting, cartoon, painted illustration, modern costume, altered pose")
        result=client.predict(handle_file(str(fn)),prompt,negative,214+i*17,2,1.20,.96,6,112,144,.49,20,"DDIM",api_name="/process")
        p=result[1] if isinstance(result,(tuple,list)) else result
        if isinstance(p,dict):p=p.get("path")
        if not p or not pathlib.Path(p).is_file():raise RuntimeError("No genuine generative photo from restoration")
        dst=ROOT/f"COLOR_AI_{i+1:02}.jpg"
        Image.open(p).convert("RGB").resize((W,H),Image.Resampling.LANCZOS).save(dst,quality=95,subsampling=0)
        im=cv2.imread(str(dst))
        gr1=cv2.resize(cv2.GaussianBlur(cv2.cvtColor(src,cv2.COLOR_BGR2GRAY),(9,9),2),(80,144))
        gr2=cv2.resize(cv2.GaussianBlur(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY),(9,9),2),(80,144))
        corr=float(np.corrcoef(gr1.ravel(),gr2.ravel())[0,1])
        sat=float(ImageStat.Stat(Image.open(dst).convert("HSV")).mean[1])
        print("RESTORATION_QA",i+1,round(corr,3),round(sat,1),flush=True)
        if not np.isfinite(corr) or corr<.82 or sat<16:
            raise RuntimeError("AI still is not source-faithful or not really colorful")
        out.append({"path":str(dst),"source_frame_timecode_s":CLIP_TIMES[i],"correlation":round(corr,3),
                    "saturation":round(sat,1),"sha256":digest(dst)})
    return out
def ghwrite(body,old=None):
    endpoint=f"repos/{REPO}/contents/{LEDGER}"
    x=base64.b64encode((json.dumps(body,sort_keys=True)+"\n").encode()).decode()
    params=["gh","api","-X","PUT",endpoint,"-f","branch=main","-f","message=V90 one-time paid task record","-f","content="+x]
    if old:params+=["-f","sha="+old]
    cmd(params,75)
def update(body):
    x=json.loads(cmd(["gh","api",f"repos/{REPO}/contents/{LEDGER}?ref=main"],40))
    ghwrite(body,x["sha"])
def vidu(stills):
    if not KEY:raise RuntimeError("Vidu API key unavailable; no paid task")
    credit=balance()
    if credit<MAX_CREDITS:raise RuntimeError("No sufficient Vidu credits to authorize one 5s clip")
    anchor=ROOT/"COLOR_AI_05.jpg"
    receipt={"status":"reserved_before_one_paid_post","authorized_by_user":"2026-10-29 use credits on a new higher-quality historical video",
      "source":SRC_URL,"model":MODEL,"duration":5,"resolution":"720p","maximum_credits":MAX_CREDITS,
      "image_sha256":digest(anchor),"prompt_sha256":hashlib.sha256(PROMPT.encode()).hexdigest(),
      "created_epoch":int(time.time()),"paid_post_count":0}
    # A pre-existing ledger prevents any accidental repeated generation.
    try:ghwrite(receipt)
    except Exception as exc:raise RuntimeError("Ledger exists/cannot reserve; abort Vidu request") from exc
    data={"model":MODEL,"images":["data:image/jpeg;base64,"+base64.b64encode(anchor.read_bytes()).decode()],
      "prompt":PROMPT,"duration":5,"resolution":"720p","off_peak":False,"audio":False,"is_rec":False,
      "payload":"CLEO_1900_V90_HISTORICAL_DANCE_ONE_CREDITED_CLIP"}
    try:res=api("/ent/v2/img2video",data,"POST",70)
    except Exception as exc:
        receipt.update(status="unknown_post_result_NO_RETRY",paid_post_count=1)
        update(receipt)
        raise RuntimeError("Provider POST ambiguous, NEVER auto retry") from exc
    task=str(res.get("task_id",""))
    receipt.update(paid_post_count=1,task_id=task,status="submitted",reported_credits=res.get("credits"))
    update(receipt)
    if not task:raise RuntimeError("Accepted generation missing task ID; no resubmit")
    if type(res.get("credits")) in (float,int) and res["credits"]>MAX_CREDITS:
        raise RuntimeError("Provider exceeded capped credits; stop")
    completed=None
    for k in range(65):
        time.sleep(10)
        try:x=api("/ent/v2/tasks/"+task+"/creations",timeout=30)
        except Exception as e:
            print("VIDU_POLL_ERROR",type(e).__name__,flush=True);continue
        if k%6==0:print("VIDU_STATUS",x.get("state"),flush=True)
        if x.get("state") in ("failed","cancelled"):
            receipt.update(status=x["state"]);update(receipt)
            raise RuntimeError("Vidu failed, no second request")
        if x.get("state")=="success":completed=x;break
    if completed is None:
        receipt.update(status="still_pending_NO_RETRY");update(receipt)
        raise RuntimeError("Vidu not ready within workflow, no duplicate call")
    links=completed.get("creations") or []
    url=links[0].get("url") if links else None
    if not isinstance(url,str) or not url.startswith("https://"):raise RuntimeError("No Vidu video URL")
    target=ROOT/"VIDU_REAL_MOVEMENT_05.mp4"
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"ArtVision/1.0"}),timeout=120) as r,open(target,"wb") as f:
        while part:=r.read(1024*1024):
            f.write(part)
            if f.tell()>90000000:raise RuntimeError("Provider MP4 too large")
    cmd(["ffmpeg","-v","error","-xerror","-i",str(target),"-f","null","-"],160)
    receipt.update(status="clip_downloaded",mp4_sha256=digest(target),
       provider_credits=completed.get("credits"))
    update(receipt)
    return {"mp4":str(target),"task_id":task,"reported_credits":completed.get("credits"),
            "sha256":digest(target)}
def music(seconds):
    rate=32000
    path=ROOT/"MUSIC_ORIGINAL.wav"
    import array
    notes=[174.61,207.65,261.63,311.13,293.66,261.63,207.65,196.]
    samples=array.array("h")
    for i in range(int(seconds*rate)):
        t=i/rate
        note=notes[int(t*1.30)%len(notes)]
        frac=(t*1.30)%1.0
        pluck=math.exp(-4.3*frac)
        a=.40*math.sin(2*math.pi*note*t)+.22*math.sin(2*math.pi*2*note*t)+.10*math.sin(2*math.pi*3*note*t)
        bass=.31*math.sin(2*math.pi*87.31*t)
        pad=.20*math.sin(2*math.pi*130.81*t)+.13*math.sin(2*math.pi*164.81*t)
        env=min(1,t/.55,(seconds-t)/.75)
        v=int(max(-30000,min(30000,2600*max(0,env)*(pluck*a+bass+pad))))
        samples.extend((v,int(v*.94)))
    with wave.open(str(path),"wb") as f:
        f.setnchannels(2);f.setsampwidth(2);f.setframerate(rate);f.writeframes(samples.tobytes())
    return path
def extract_motion(end,length):
    cap=cv2.VideoCapture(str(SRC))
    n=round(length*FPS)
    ret=[]
    for i in range(n):
        t=end-length+i/FPS
        cap.set(cv2.CAP_PROP_POS_MSEC,t*1000)
        ok,fr=cap.read()
        if not ok:raise RuntimeError("Historical motion unavailable at "+str(t))
        h,w=fr.shape[:2];cw=int(h*9/16);fr=fr[:,(w-cw)//2:(w+cw)//2]
        fr=cv2.resize(fr,(W,H),interpolation=cv2.INTER_CUBIC)
        mono=cv2.cvtColor(cv2.cvtColor(fr,cv2.COLOR_BGR2GRAY),cv2.COLOR_GRAY2BGR)
        ret.append(mono)
    cap.release()
    return ret
def text_frame(fr,t):
    if t>1.60:return fr
    im=Image.fromarray(cv2.cvtColor(fr,cv2.COLOR_BGR2RGB)).convert("RGBA")
    overlay=Image.new("RGBA",im.size,(0,0,0,0));d=ImageDraw.Draw(overlay)
    opacity=int(185*min(1,t/.3,(1.6-t)/.34))
    if opacity<0:return fr
    d.rounded_rectangle((W*.075,H*.78,W*.925,H*.89),radius=22,fill=(6,13,19,max(0,opacity)))
    fontpath="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    font=ImageFont.truetype(fontpath,37);small=ImageFont.truetype(fontpath,23)
    d.text((W*.12,H*.80),"PARIS  ·  1900",font=font,fill=(245,237,220,max(0,opacity)))
    d.text((W*.12,H*.845),"A DANCE BROUGHT BACK TO LIFE",font=small,fill=(222,201,171,max(0,opacity)))
    return cv2.cvtColor(np.asarray(Image.alpha_composite(im,overlay).convert("RGB")),cv2.COLOR_RGB2BGR)
def render(stills,vidu_info):
    # 4 variable archival scenes + 5s entirely moving Vidu coda.
    timings=[(0.82,.30,2.14),(1.05,.32,2.33),(.89,.35,2.65),(1.10,.30,2.01)]
    out=ROOT/"PARIS_1900_CLEO_DANCE_V90.mp4"
    silent=ROOT/"silent.mp4"
    p=subprocess.Popen(["ffmpeg","-y","-nostdin","-v","error","-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}",
      "-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","19",
      "-pix_fmt","yuv420p",str(silent)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    processed=0
    duration=0.0
    try:
        for i,(bw,reveal,hold) in enumerate(timings):
            actual=extract_motion(CLIP_TIMES[i],bw)
            im=cv2.imread(str(ROOT/f"COLOR_AI_{i+1:02}.jpg"))
            for fr in actual:
                if i==0:fr=text_frame(fr,processed/FPS)
                p.stdin.write(fr.tobytes());processed+=1
            original=actual[-1]
            for k in range(round(reveal*FPS)):
                q=(k+1)/max(1,round(reveal*FPS));q=q*q*(3-2*q)
                p.stdin.write(cv2.addWeighted(original,1-q,im,q,0).tobytes());processed+=1
            for k in range(round(hold*FPS)):
                p.stdin.write(im.tobytes());processed+=1
        cap=cv2.VideoCapture(vidu_info["mp4"])
        fps=cap.get(cv2.CAP_PROP_FPS)
        count=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if fps<20 or not 4.5<count/fps<5.6:raise RuntimeError("Vidu moving clip not ~5s")
        first=None;last=None
        for k in range(round(5.0*FPS)):
            cap.set(cv2.CAP_PROP_POS_MSEC,(k/FPS)*1000)
            ok,fr=cap.read()
            if not ok:raise RuntimeError("Vidu clip truncated")
            fr=cv2.resize(fr,(W,H))
            if k==0:
                first=fr.copy()
                source=cv2.imread(str(ROOT/"COLOR_AI_05.jpg"))
                def gray(x):return cv2.GaussianBlur(cv2.resize(cv2.cvtColor(x,cv2.COLOR_BGR2GRAY),(80,144)),(9,9),0)
                corr=float(np.corrcoef(gray(source).ravel(),gray(first).ravel())[0,1])
                if corr<.62:raise RuntimeError("Vidu lost dance performer or framing")
            if k==round(2.0*FPS):last=fr.copy()
            # Actual Vidu remains moving; first second only is desaturated.
            t=k/FPS;a=max(0,min(1,(t-.08)/.92));a=a*a*(3-2*a)
            g=cv2.cvtColor(cv2.cvtColor(fr,cv2.COLOR_BGR2GRAY),cv2.COLOR_GRAY2BGR)
            p.stdin.write(cv2.addWeighted(g,1-a,fr,a,0).tobytes());processed+=1
        cap.release()
        if last is not None:
            delta=float(np.mean(np.abs(cv2.resize(first,(90,160)).astype(np.float32)-
                                            cv2.resize(last,(90,160)).astype(np.float32))))
            if delta<2.0:raise RuntimeError("Vidu scene has insufficient real moving content")
    finally:
        p.stdin.close()
    err=p.stderr.read().decode(errors="replace")
    if p.wait()!=0:raise RuntimeError("Render failed "+err[-1000:])
    duration=processed/FPS
    if not 14<=duration<=35:raise RuntimeError("V70 duration out of bounds "+str(duration))
    wav=music(duration)
    cmd(["ffmpeg","-y","-nostdin","-v","error","-i",str(silent),"-i",str(wav),
         "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","128k",
         "-shortest","-movflags","+faststart",str(out)],180)
    cmd(["ffmpeg","-v","error","-xerror","-i",str(out),"-f","null","-"],150)
    return out,duration
def pack(out,seconds,stills,vidu_info):
    cover=ROOT/"COVER.jpg";shutil.copyfile(ROOT/"COLOR_AI_01.jpg",cover)
    posts={
      "FACEBOOK":"Paris, 1900. La danza di Cléo de Mérode durante l'Esposizione Universale torna a prendere vita: pellicola autentica, fotografie restaurate con IA e un breve inserto di movimento AI. I colori e i dettagli ricostruiti sono interpretazioni, non testimonianze storiche certe. Fonte: Wikimedia Commons, Danse javanaise (1900), pubblico dominio.",
      "INSTAGRAM":"PARIS · 1900. Una danzatrice, un palcoscenico e un istante sospeso nel tempo. 🎞️ Film d'epoca autentico, fotografie e movimento ricostruiti con IA. #Paris1900 #HistoryReels #Restauro",
      "TIKTOK":"Nel 1900 una danza finì su pellicola. Oggi quel momento rivive a colori. 🎞️ Originale storico di pubblico dominio, colori e parte del movimento ricostruiti con IA. #Storia #BelleEpoque",
      "YOUTUBE":"PARIS 1900 | A DANCE BROUGHT BACK TO LIFE\nFilmato d'archivio autentico: Danse javanaise (1900), Wikimedia Commons. Ricostruzione digitale a colori tramite IA e un inserto Vidu generato dal fotogramma restaurato; colori e movimento AI non sono una prova storica."
    }
    for site,s in posts.items():(ROOT/f"POST_{site}.txt").write_text(s+"\n",encoding="utf-8")
    qa={"status":"RENDERED_NEEDS_REAL_ARTISTIC_REVIEW","video":out.name,"sha256":digest(out),
        "duration_s":round(seconds,3),"size":out.stat().st_size,"source":SRC_URL,"source_sha256":digest(SRC),
        "source_license":"Wikimedia Commons public domain mark; page inspected 2026-10-29",
        "actual_scene_types":"4 original B/W motion->4 frame-anchored AI color photos; 1 Vidu 5s color-motion",
        "photo_evidence":stills,"vidu":vidu_info,"paid_vidu_posts":1,
        "vidu_credit_limit":MAX_CREDITS,"new_historical_footage":True,
        "disclosure":"Original historical moving images; AI-created color stills and one AI motion interpretation.",
        "social_autopublished":False,"archive_verified":False,"human_visual_quality_review":False}
    writej(ROOT/"QA_SOURCES_RIGHTS.json",qa)
    z=ROOT/"PARIS_1900_CLEO_V90_ANDROID.zip"
    with zipfile.ZipFile(z,"w",compression=zipfile.ZIP_DEFLATED) as f:
        for n in [out,cover,ROOT/"QA_SOURCES_RIGHTS.json",*[ROOT/f"POST_{x}.txt" for x in posts]]:
            f.write(n,n.name)
    with zipfile.ZipFile(z) as f:
        if f.testzip():raise RuntimeError("Invalid delivery ZIP")
    print("NEW_HISTORY_FILM_READY",out.name,"DURATION",seconds,"ZIP",z.name,flush=True)
def main():
    original=download_and_scout()
    photos=restoration(original)
    # No Vidu billable task until all AI stills and source gates pass.
    movie=vidu(photos)
    out,duration=render(photos,movie)
    pack(out,duration,photos,movie)
if __name__=="__main__":
    main()
