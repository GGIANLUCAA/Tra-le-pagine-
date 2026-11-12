#!/usr/bin/env python3
"""GIULIANO 03 Antikythera: two-stage narrated documentary renderer.
VOICE mode: one permitted Gemini synthesis, writes persistent WAV/timing.
RENDER mode: source-locked images + model footage, FFmpeg concat, QA, ZIP.
No social publication. No image generation or additional paid API calls.
"""
from __future__ import annotations
import argparse, hashlib, json, math, os, subprocess, sys, zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
import numpy as np
import soundfile as sf

ROOT=Path(__file__).resolve().parents[1]
PLAN=ROOT/"giuliano/antikythera/EP03_SCRIPT_SHOTMAP_V1.json"
W,H,FPS=720,1280,24
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SRC=ROOT/"input-media/output/GIULIANO_03_SOURCE_PREFLIGHT"
VOICE=ROOT/"output/GIULIANO_03_VOICE"
OUT=ROOT/"output/GIULIANO_03_MASTER"

def call(args,timeout=480,quiet=True):
    r=subprocess.run([str(x) for x in args],capture_output=quiet,text=quiet,timeout=timeout)
    if r.returncode:
        raise RuntimeError("FFmpeg command failed: "+str(args[:6])+" "+str(r.stderr or "")[-1500:])
    return r.stdout or ""

def digest(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()

def writej(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def plan():
    m=json.loads(PLAN.read_text(encoding="utf-8"))
    assert m["publication_allowed"] is False
    assert m["external_paid_calls_allowed"] is False
    assert m["schema"]=="giuliano-antikythera-episode-v1"
    assert len(m["scenes"])==20
    return m

def do_voice():
    m=plan()
    if os.getenv("GIULIANO_TTS_ONE_SHOT")!="1":
        raise RuntimeError("ONE_SHOT_AUTHORIZATION_MISSING")
    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError("GEMINI_API_KEY_UNAVAILABLE: no synthetic fallback permitted")
    VOICE.mkdir(parents=True,exist_ok=True)
    from gemini_voice import synthesize,sentences
    story=" ".join(s["narration"].strip() for s in m["scenes"])
    # One single human-paced Italian narration. Cached audio is reused if valid.
    wav,timed=synthesize(story,VOICE)
    actual_duration=len(wav)/24000.0
    source_sents=sentences(story)
    counts=[len(sentences(s["narration"])) for s in m["scenes"]]
    assert sum(counts)==len(source_sents)==len(timed), "Voice segmentation mismatch"
    boundaries=[0.0]
    off=0
    for count in counts[:-1]:
        off+=count
        a=timed[off-1][2]
        b=timed[off][1]
        boundaries.append(round((a+b)/2,4))
    boundaries.append(actual_duration)
    spans=[]
    for i,scene in enumerate(m["scenes"]):
        start,end=boundaries[i:i+2]
        spans.append({"scene":scene["scene"],"asset_id":scene["asset_id"],
                      "narration":scene["narration"],"start":round(start,4),
                      "end":round(end,4),"duration":round(end-start,4)})
    alignment_path=VOICE/"ALLINEAMENTO_VOCE.json"
    alignment=json.loads(alignment_path.read_text()) if alignment_path.exists() else {"method":"missing"}
    report={"schema":"giuliano-ep03-real-voice-v1","narration_provider":"Google Gemini via existing project integration",
            "tts_request_policy":"one-shot; no API retries from this script",
            "audio_seconds":round(actual_duration,3),"sentences":len(source_sents),
            "voice_sha256":digest(VOICE/"VOCE.wav"),"alignment":alignment,
            "scene_spans":spans,"human_artistic_approved":False}
    writej(VOICE/"GIULIANO_03_VOICE_TIMING.json",report)
    if alignment.get("method")!="asr_with_interpolation":
        raise RuntimeError("Voice synthesized but ASR word timing not available; keep WAV artifact and do not issue finished-film claim.")
    if float(alignment.get("matched_fraction",0))<0.48:
        raise RuntimeError("Voice ASR quality too weak, inspect reusable WAV and do not repeat provider call.")
    if any(s["duration"]<2.35 for s in spans):
        raise RuntimeError("Narration produces too-short scene; revise beat segmentation without repeating TTS.")
    print("VOICE_OK",round(actual_duration,2),"s",len(spans),"beats",flush=True)

def font(size,bold=False):return ImageFont.truetype(BOLD if bold else FONT,int(size))

def composite(photo,title="",subtitle="",focus=0):
    src=Image.open(photo).convert("RGB")
    bg=ImageOps.fit(src,(W,H),Image.Resampling.LANCZOS)
    bg=bg.filter(ImageFilter.GaussianBlur(42))
    bg=ImageEnhance.Brightness(bg).enhance(.20)
    foreground=ImageOps.contain(src,(W-36,H-188),Image.Resampling.LANCZOS)
    # Human-style restrained framing: visible object, no exaggerated fake camera push.
    x=(W-foreground.width)//2;y=(H-foreground.height)//2-30
    if focus>0 and foreground.width>W*.8:
        x=max(0,min(W-foreground.width,x))
    bg.paste(foreground,(x,y))
    dim=Image.new("RGBA",(W,180),(8,12,15,200))
    bg.paste(dim,(0,H-180),dim)
    d=ImageDraw.Draw(bg)
    if title:d.text((26,H-154),title,fill="#e8e4dc",font=font(25,True))
    if subtitle:d.text((26,H-112),subtitle[:65],fill="#b8c1c5",font=font(16))
    return bg

def map_plate():
    im=Image.new("RGB",(W,H),(10,24,37));d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,H),fill=(10,26,42))
    # Stylized original chart: explicitly NOT a surveyed map or period photograph.
    for ring in range(10):
        pad=ring*53
        d.arc((50+pad,240+pad//2,930-pad,1180-pad//2),0,355,fill=(22,46,59),width=2)
    coords=[(140,490),(260,425),(345,605),(423,788),(466,698),(535,915),
            (260,990),(585,406),(610,660),(145,740)]
    for i,(x,y) in enumerate(coords):
        r=[20,8,11,6,7][i%5]
        d.ellipse((x-r,y-r,x+r,y+r),fill=(38,65,72),outline=(61,89,91),width=2)
    d.line((205,400,410,784),fill=(76,122,126),width=3)
    d.ellipse((402,776,418,792),fill=(220,174,97))
    d.ellipse((392,766,428,802),outline=(220,174,97),width=2)
    d.text((31,75),"THE ANCIENT COMPUTER",fill=(234,229,218),font=font(35,True))
    d.text((31,136),"GIULIANO · EPISODIO 03",fill=(172,188,192),font=font(21))
    d.text((50,832),"ANTICITERA",fill=(255,225,163),font=font(35,True))
    d.text((50,888),"MARE EGEO · 1900",fill=(192,206,202),font=font(22))
    d.text((28,1212),"MAPPA SCHEMATICA · NON DOCUMENTO DEL 1900",fill=(164,178,184),font=font(16))
    return im

def cycle_plate(cycle,caption):
    im=Image.new("RGB",(W,H),(12,19,26));d=ImageDraw.Draw(im)
    d.text((25,100),"IL CALENDARIO NEL BRONZO",font=font(29,True),fill=(230,228,216))
    center=(360,600)
    turns=4.0;points=[]
    for k in range(800):
        t=k/799;angle=t*turns*2*math.pi-math.pi/2; radius=50+310*t
        points.append((int(center[0]+radius*math.cos(angle)),int(center[1]+radius*math.sin(angle))))
    d.line(points,fill=(192,148,82),width=5)
    for k in range(15):
        theta=(k/15)*turns*2*math.pi-math.pi/2;r=50+310*(k/15)
        x=int(center[0]+r*math.cos(theta));y=int(center[1]+r*math.sin(theta))
        d.ellipse((x-5,y-5,x+5,y+5),fill=(226,215,187))
    d.text((35,1068),str(cycle),font=font(63,True),fill=(230,199,141))
    d.text((35,1148),caption,font=font(24),fill=(206,217,219))
    d.text((35,1230),"SCHEMA DIDATTICO · NON IL QUADRANTE ORIGINALE",font=font(15),fill=(137,153,157))
    return im

def plate_for(scene,assetdir,idx,outdir,variant=0):
    kind=scene["asset_id"]
    if idx==0:
        im=map_plate()
    elif idx==13:
        im=cycle_plate("19 ANNI","Ciclo metonico · 235 mesi lunari")
    elif idx==14:
        im=cycle_plate("223 MESI","Ciclo di Saros · previsione eclissi")
    else:
        # No museum placard or unsourced fake CT screenshots.
        replacements={"wreck1900":"front","wreckmuseum":"fragb","scientific-gears":"front","scientific-dials":"back"}
        kind=replacements.get(kind,kind)
        src=assetdir/(kind+".jpg")
        if not src.exists():src=assetdir/"front.jpg"
        label=("FRAMMENTO "+kind.replace("frag","").upper() if kind.startswith("frag") else
               "FRAMMENTO A · REPERTO ORIGINALE" if kind in ("front","back") else "REPERTO AUTENTICO")
        if idx in (8,9):label="INTERNO DEL BRONZO · SCHEMA ESPLICATIVO"
        im=composite(src,label,"Museo Archeologico Nazionale di Atene · fotografia documentale",variant)
    dst=outdir/f"plate_{idx:02}_{variant}.jpg"
    im.save(dst,quality=92)
    return dst

def clip_still(src,frames,out):
    seconds=frames/FPS
    call(["ffmpeg","-hide_banner","-y","-v","error","-loop","1","-framerate",FPS,"-i",src,
          "-frames:v",frames,"-vf","format=yuv420p","-an","-c:v","libx264",
          "-preset","veryfast","-crf","22","-pix_fmt","yuv420p",out],timeout=120)

def clip_video(src,frames,out,offset=1):
    # Source is authentic CC-BY licensed research animation, not original ancient filming.
    vf=(f"[0:v]fps={FPS},split=2[foreground][background];"
        f"[background]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
        f"boxblur=24:1,eq=brightness=-0.29[base];"
        f"[foreground]scale={W}:-2[sharp];"
        f"[base][sharp]overlay=(W-w)/2:(H-h)/2:shortest=1,format=yuv420p,"
        "drawtext=fontfile="+FONT+":text='RICOSTRUZIONE SCIENTIFICA':"
        "fontcolor=white@0.9:fontsize=22:x=22:y=h-70:box=1:boxcolor=black@0.6:boxborderw=9")
    call(["ffmpeg","-hide_banner","-y","-v","error","-ss",str(offset),"-i",src,
          "-frames:v",frames,"-filter_complex",vf,"-an","-r",FPS,
          "-c:v","libx264","-preset","veryfast","-crf","22",
          "-pix_fmt","yuv420p",out],timeout=180)

def music(duration,path):
    sr=24000;n=int((duration+0.5)*sr)
    t=np.arange(n,dtype=np.float32)/sr
    a=np.zeros(n,dtype=np.float32)
    # Original slowly evolving minor/major-neutral cinematic drone, not sampled music.
    notes=[110.,164.814,220.,246.942]
    for i,hz in enumerate(notes):
        wobble=(0.92+0.08*np.sin(2*np.pi*(0.012+i*.007)*t))
        a+=(0.011/(1+i*.3))*wobble*np.sin(2*np.pi*hz*t+0.17*i)
    for k in range(int(duration)//4+2):
        start=int(k*4*sr)
        if start>=n:break
        dur=min(int(3.7*sr),n-start)
        tt=np.arange(dur,dtype=np.float32)/sr
        root=[146.83,130.81,164.81,110.0][k%4]
        env=(1-np.exp(-8*tt))*np.exp(-tt*1.3)
        a[start:start+dur]+=.022*env*np.sin(2*np.pi*root*tt)
    fade=np.minimum(1,t/2)*np.minimum(1,np.maximum(0,(duration-t))/3)
    a*=fade
    sf.write(path,a,sr,subtype="PCM_16")

def render():
    m=plan();OUT.mkdir(parents=True,exist_ok=True)
    status=json.loads((SRC/"SOURCE_QA_REPORT.json").read_text())
    usable={a["id"] for a in status["assets"] if a["state"]=="verified"}
    require={"front","back","fragb","fragc","fragd","verified-2026-gears","verified-2026-exploded"}
    if not require.issubset(usable):raise RuntimeError("Licensed material missing from authenticated source artifact")
    timings=json.loads((VOICE/"GIULIANO_03_VOICE_TIMING.json").read_text())
    if timings["alignment"].get("method")!="asr_with_interpolation":
        raise RuntimeError("Voice timing not ASR; do not issue finished film.")
    voice_wav=VOICE/"VOCE.wav"
    if not voice_wav.exists() or digest(voice_wav)!=timings["voice_sha256"]:
        raise RuntimeError("Original voice changed or absent")
    timeline=timings["scene_spans"]
    assert len(timeline)==20
    duration=float(timings["audio_seconds"])
    clips=[];frames_total=0
    for i,(scene,span) in enumerate(zip(m["scenes"],timeline)):
        segment_frames=max(1,round(span["duration"]*FPS))
        name=scene["asset_id"]
        actual_video=name.startswith("scientific")
        if actual_video:
            original=SRC/("verified-2026-gears.mp4" if name=="scientific-gears" else "verified-2026-exploded.mp4")
            # Avoid apparent static loops: alternate offsets and show different animation detail.
            offset=(i*3)%7
            if offset+(segment_frames/FPS)>14:offset=max(0,14-segment_frames/FPS)
            out=OUT/f"scene_{i:02}.mp4"
            clip_video(original,segment_frames,out,offset)
        else:
            plate=plate_for(scene,SRC,i,OUT)
            out=OUT/f"scene_{i:02}.mp4"
            clip_still(plate,segment_frames,out)
        clips.append(out);frames_total+=segment_frames
        print("SCENE",i+1,"/",len(timeline),"frames",segment_frames,"visual",name,flush=True)
    listfile=OUT/"shots.txt"
    listfile.write_text("".join("file '"+p.name+"'\n" for p in clips),encoding="utf-8")
    silent=OUT/"GIULIANO_03_PICTURE_LOCK.mp4"
    call(["ffmpeg","-hide_banner","-y","-v","error","-f","concat","-safe","0",
          "-i",listfile,"-c","copy","-movflags","+faststart",silent],timeout=180)
    pad=OUT/"ORIGINAL_AMBIENCE.wav";music(duration,pad)
    audio=OUT/"GIULIANO_03_MIX.wav"
    call(["ffmpeg","-hide_banner","-y","-v","error","-i",voice_wav,"-i",pad,
          "-filter_complex","[0:a]volume=1.0[sp];[1:a]volume=0.21[bg];"
          "[sp][bg]amix=inputs=2:duration=first:dropout_transition=0[out]",
          "-map","[out]","-c:a","pcm_s16le",audio],timeout=150)
    master=OUT/"GIULIANO_03_THE_ANCIENT_COMPUTER_MASTER.mp4"
    call(["ffmpeg","-hide_banner","-y","-v","error","-i",silent,"-i",audio,
          "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","192k",
          "-movflags","+faststart","-shortest",master],timeout=180)
    android=OUT/"GIULIANO_03_THE_ANCIENT_COMPUTER_ANDROID.mp4"
    call(["ffmpeg","-hide_banner","-y","-v","error","-i",master,
          "-vf","scale=540:960:flags=lanczos","-c:v","libx264","-preset","veryfast",
          "-crf","26","-c:a","aac","-b:a","112k","-movflags","+faststart",android],timeout=240)
    # Independently decode all video/audio, not just metadata.
    for p in (master,android):
        call(["ffmpeg","-v","error","-xerror","-i",p,"-f","null","-"],timeout=300)
    cap=OUT/"GIULIANO_03_COVER.jpg"
    front=Image.open(SRC/"front.jpg").convert("RGB")
    cover=composite(SRC/"front.jpg","THE ANCIENT COMPUTER","GIULIANO · Un reperto di 2.000 anni",0)
    cover.save(cap,quality=93)
    credits=OUT/"FONTI_LICENZE_E_NOTE.txt"
    credits.write_text("\n".join([
        "GIULIANO 03 - THE ANCIENT COMPUTER",
        "Video non pubblicato; visione privata di revisione artistica.",
        "Fotos originali dei frammenti A, B, C, D: Wikimedia Commons, licenze registrate nei metadati SOURCE_QA_REPORT.json.",
        "CC BY 4.0 / CC BY-SA 4.0: attribuzione e collegamenti esatti disponibili nel report fonti incluso.",
        "RICOSTRUZIONE 3D: taciclei, https://github.com/taciclei/antikythera-mechanism, CC BY 4.0. I modelli seguono ipotesi scientifiche, non originali antichi.",
        "Base accademica: Freeth et al., Scientific Reports 11, 5821 (2021), https://doi.org/10.1038/s41598-021-84310-w.",
        "Voce: Google Gemini TTS, voce Gacrux del progetto, una sola sintesi.",
        "Musica: sintetizzata come composizione originale appositamente per questo episodio.",
        "Durate scene guidate da allineamento ASR: vedere TIMING_REAL_VOICE.json.",
        "Non dichiarare pubblicazione e approvazione artistica per solo controllo tecnico."
    ])+"\n",encoding="utf-8")
    report={"schema":"giuliano-03-master-technical-v1","length_seconds":duration,
            "scene_count":len(clips),"video_frames_expected":frames_total,
            "source_footage_real":["fragments A,B,C,D"],"scientific_reconstruction_labeled":True,
            "voice_sha256":digest(voice_wav),"human_artistic_approved":False,
            "technical_full_decode_pass":True,
            "files":{p.name:{"bytes":p.stat().st_size,"sha256":digest(p)} for p in (master,android,cap)}}
    writej(OUT/"QA_TECHNICAL.json",report)
    (OUT/"TIMING_REAL_VOICE.json").write_text((VOICE/"GIULIANO_03_VOICE_TIMING.json").read_text())
    (OUT/"SOURCE_QA_REPORT.json").write_text((SRC/"SOURCE_QA_REPORT.json").read_text())
    archive=OUT/"GIULIANO_03_COMPLETO.zip"
    members=(master,android,cap,credits,OUT/"QA_TECHNICAL.json",
             OUT/"TIMING_REAL_VOICE.json",OUT/"SOURCE_QA_REPORT.json")
    with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=2) as z:
        for p in members:z.write(p,p.name)
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:raise RuntimeError("ZIP CRC failure")
    print("GIULIANO_03_RENDERED_TECHNICAL_PASS",round(duration,2),str(archive),flush=True)

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--mode",choices=("voice","render"),required=True)
    a=parser.parse_args()
    if a.mode=="voice":do_voice()
    else:render()
