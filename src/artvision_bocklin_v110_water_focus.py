#!/usr/bin/env python3
"""ArtVision V110: corregge SOLO il focus sull'acqua nel Critico Museum Böcklin V109.
Sorgente: MP4 V109 verificato; nessun TTS, AI, download o modifica dei master.
La correzione è una camera geometrica sulla pittura già presente nel video.
"""
import argparse, hashlib, json, math, subprocess
from pathlib import Path
import cv2
import numpy as np

SOURCE_SHA = "07944553bf1f1547acc34f54185690f1f0c28c20f12cdc888eb24c8b6854a189"
AUDIO_SHA = "3f46d52d8e0a09974bd144c62a77f5357c1ec5cc63e9c3cee956c8853edd505e"
W,H,FPS,N = 720,1280,20,2213
START,FULL,HOLD,END = 28.25,30.30,39.50,41.15

def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1048576),b""):h.update(b)
    return h.hexdigest()

def ease(u):
    u=max(0.,min(1.,u))
    return u*u*(3-2*u)

def camera(t):
    if t<START or t>END:return 1.,360.,640.
    if t<FULL:
        a=ease((t-START)/(FULL-START))
        return 1+.95*a,360.,640+285*a
    if t<HOLD:
        u=(t-FULL)/(HOLD-FULL)
        return 1.95+.012*math.sin(math.pi*u)**2,360.+1.5*math.sin(2*math.pi*u),925.+2*math.sin(2*math.pi*u)
    a=ease((t-HOLD)/(END-HOLD))
    return 1.95-.95*a,360.,925.-285*a

def focus(frame,t):
    z,cx,cy=camera(t)
    if z==1 and cx==360 and cy==640:return frame
    if not 640/z-1<=cy<=H-640/z+1:raise ValueError("Camera outside source")
    M=np.float32([[z,0,360-z*cx],[0,z,640-z*cy]])
    return cv2.warpAffine(frame,M,(W,H),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)

def run(args):
    p=subprocess.run(list(map(str,args)),capture_output=True)
    if p.returncode:raise RuntimeError(p.stderr.decode(errors="replace")[-1500:])
    return p.stdout

def aac(p):
    return run(["ffmpeg","-v","error","-i",p,"-map","0:a:0","-c:a","copy","-f","adts","pipe:1"])

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--qa",type=Path,required=True)
    a=ap.parse_args()
    if sha(a.input)!=SOURCE_SHA:raise ValueError("Wrong verified V109 source")
    if a.input.resolve()==a.output.resolve():raise ValueError("Do not overwrite master")
    a.output.parent.mkdir(parents=True,exist_ok=True)
    cap=cv2.VideoCapture(str(a.input))
    if int(cap.get(cv2.CAP_PROP_FRAME_COUNT))!=N or abs(cap.get(cv2.CAP_PROP_FPS)-FPS)>.01:
        raise ValueError("Unexpected source video")
    tmp=a.output.with_name(a.output.stem+".silent.tmp.mp4")
    cmd=["ffmpeg","-hide_banner","-loglevel","error","-y","-f","rawvideo","-pix_fmt","bgr24",
         "-s",f"{W}x{H}","-r",str(FPS),"-i","pipe:0","-an","-c:v","libx264",
         "-preset","veryfast","-crf","19","-pix_fmt","yuv420p","-threads","2",str(tmp)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    count=0;prev=None;peak=0.;over=0
    try:
        for i in range(N):
            ok,f=cap.read()
            if not ok:raise ValueError("Truncated video")
            t=i/FPS;f=focus(f,t)
            if START<=t<=END:count+=1
            sm=cv2.resize(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY),(180,320))
            if prev is not None:
                mad=float(np.abs(sm.astype("int16")-prev.astype("int16")).mean())
                peak=max(peak,mad)
                over+=mad>35
            prev=sm
            proc.stdin.write(f.tobytes())
    finally:
        cap.release();proc.stdin.close()
    err=proc.stderr.read().decode(errors="replace")
    if proc.wait():raise RuntimeError("Encoder: "+err[-1000:])
    run(["ffmpeg","-v","error","-y","-i",tmp,"-i",a.input,
         "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","copy",
         "-shortest","-movflags","+faststart",a.output])
    tmp.unlink()
    run(["ffmpeg","-v","error","-xerror","-i",a.output,"-f","null","-"])
    aa,bb=aac(a.input),aac(a.output)
    if aa!=bb or hashlib.sha256(bb).hexdigest()!=AUDIO_SHA:raise ValueError("AAC changed")
    cap=cv2.VideoCapture(str(a.output));frames=int(cap.get(cv2.CAP_PROP_FRAME_COUNT));cap.release()
    if frames!=N:raise ValueError("Wrong output frame count")
    qa={"version":"V110","slot":"Boecklin critico_museum","input_sha256":SOURCE_SHA,
        "output_sha256":sha(a.output),"bytes":a.output.stat().st_size,
        "duration_seconds":N/FPS,"frames":N,"full_ffmpeg_decode":"PASS",
        "audio_sha256":AUDIO_SHA,"audio_bit_identical":True,
        "corrected_interval_seconds":[START,END],"changed_frames":count,
        "source":"Only verified V109 painting pixels, no AI/TTS",
        "voice_delay_seconds":5.0,
        "water_voice_video_seconds":[29.72,39.7],
        "V57_peak_MAD":round(peak,3),"V57_frames_above_35":over,
        "Gold_V25":False,"site_android_playback_verified":False,
        "library_readback_verified":False,"human_full_review":"pending"}
    a.qa.write_text(json.dumps(qa,indent=2,ensure_ascii=False),encoding="utf8")
    print(json.dumps(qa,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
