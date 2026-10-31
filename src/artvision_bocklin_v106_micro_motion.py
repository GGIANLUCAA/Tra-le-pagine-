#!/usr/bin/env python3
"""V106: non-destructive, offline camera micro-motion in PROVEN static holds of V105.
Does not synthesize anything, generate voice, call APIs, or overwrite source.
Preserves V105's first and last Museum transitions and copies AAC bit-for-bit.
The result is always review-only, never owner-approved V25 Gold.
"""
import argparse, hashlib, json, math, subprocess
from pathlib import Path
import cv2
import numpy as np

FPS_EXPECTED=20
WIDTH,HEIGHT=720,1280
THRESH=0.16  # MAD on 180x320 8-bit greyscale
MIN_SECONDS=2.75
KEEP_INTRO_END_SECONDS=5.05
KEEP_OUTRO_BEGIN_SECONDS=102.50


def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for x in iter(lambda:f.read(2**20),b""):
            h.update(x)
    return h.hexdigest()


def run(args):
    p=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
    if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace')[-1800:])
    return p.stdout


def frames_and_motion(path):
    cap=cv2.VideoCapture(str(path))
    if not cap.isOpened():raise RuntimeError("Could not open input MP4")
    fps=cap.get(cv2.CAP_PROP_FPS)
    if abs(fps-FPS_EXPECTED)>.01:raise RuntimeError(f"Unexpected FPS {fps}")
    ds=[]; prev=None;n=0
    while True:
        ok,frame=cap.read()
        if not ok:break
        if frame.shape[:2]!=(HEIGHT,WIDTH):raise RuntimeError("Unexpected resolution")
        small=cv2.resize(cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY),(180,320))
        ds.append(float(np.abs(small.astype(np.int16)-prev.astype(np.int16)).mean()) if prev is not None else 0.0)
        prev=small;n+=1
    cap.release()
    if n<200:raise RuntimeError("Insufficient decoded frames")
    return np.array(ds,dtype=np.float32),fps


def find_holds(delta,fps):
    still=(delta<THRESH)
    lo=int(round(KEEP_INTRO_END_SECONDS*fps));hi=int(round(KEEP_OUTRO_BEGIN_SECONDS*fps))
    still[:lo]=False;still[hi:]=False
    # Bridge <=0.10s isolated high differences from compression/tiny motion.
    ranges=[];start=None
    for i,flag in enumerate(list(still)+[False]):
        if flag and start is None:start=i
        elif not flag and start is not None:ranges.append([start,i]);start=None
    merged=[]
    for a,b in ranges:
        if merged and a-merged[-1][1]<=2:merged[-1][1]=b
        else:merged.append([a,b])
    return [(a,b) for a,b in merged if b-a>=round(MIN_SECONDS*fps)]


def transform(frame,index,a,b,slot):
    # Return pixel-identical endpoints; zero first derivative avoids boundary jerks.
    u=(index-a)/max(1,b-a-1)
    t=math.sin(math.pi*u)**2
    # Varied, mild camera paths; no continuous robotic zoom, no framing re-selection.
    base=[.026,.032,.022,.029,.037,.023][slot%6]
    z=1+base*t
    sx=[1,-1,0,1,-1,0][slot%6]
    sy=[0,1,-1,-1,0,1][slot%6]
    dx=sx*5*t;dy=sy*6*t
    if t<1e-9:return frame
    M=cv2.getRotationMatrix2D((WIDTH/2,HEIGHT/2),0,z)
    M[0,2]+=dx;M[1,2]+=dy
    return cv2.warpAffine(frame,M,(WIDTH,HEIGHT),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT_101)


def render(master,output,report_path):
    if output.resolve()==master.resolve():raise RuntimeError("Never overwrite master")
    delta,fps=frames_and_motion(master)
    runs=find_holds(delta,fps)
    if not runs:raise RuntimeError("No measured static holds; do not render")
    n=len(delta);silent=output.with_suffix('.silent.tmp.mp4')
    cap=cv2.VideoCapture(str(master))
    command=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','bgr24',
        '-s',f'{WIDTH}x{HEIGHT}','-r',str(FPS_EXPECTED),'-i','pipe:0','-an','-c:v','libx264',
        '-preset','veryfast','-crf','18','-pix_fmt','yuv420p',str(silent)]
    p=subprocess.Popen(command,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    r=0; written=0
    try:
        for i in range(n):
            ok,frame=cap.read()
            if not ok:raise RuntimeError(f"Premature EOF {i}/{n}")
            while r<len(runs) and i>=runs[r][1]:r+=1
            if r<len(runs) and runs[r][0]<=i<runs[r][1]:
                frame=transform(frame,i,*runs[r],r)
                written+=1
            p.stdin.write(frame.tobytes())
    finally:
        cap.release()
        p.stdin.close()
    err=p.stderr.read().decode(errors='replace')
    if p.wait()!=0:raise RuntimeError('FFmpeg encode: '+err[-1500:])
    run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(silent),'-i',str(master),
         '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','copy','-shortest',
         '-movflags','+faststart',str(output)])
    run(['ffmpeg','-v','error','-xerror','-i',str(output),'-f','null','-'])
    # ADTS copies MUST match: audio bitstream verification, not only decoded waveform.
    original_adts=run(['ffmpeg','-v','error','-i',str(master),'-map','0:a:0','-c:a','copy','-f','adts','pipe:1'])
    result_adts=run(['ffmpeg','-v','error','-i',str(output),'-map','0:a:0','-c:a','copy','-f','adts','pipe:1'])
    audio_identical=hashlib.sha256(original_adts).digest()==hashlib.sha256(result_adts).digest()
    if not audio_identical:raise RuntimeError("AAC not identical; reject new candidate")
    silent.unlink(missing_ok=True)
    after,_=frames_and_motion(output)
    if len(after)!=n:raise RuntimeError('Frame count changed')
    def medin(d,a,b):return float(np.median(d[a:b]))
    records=[]
    for i,(a,b) in enumerate(runs):
        records.append({'start_s':round(a/fps,2),'end_s':round(b/fps,2),
                        'length_s':round((b-a)/fps,2),
                        'median_MAD_before':round(medin(delta,a,b),4),
                        'median_MAD_after':round(medin(after,a,b),4)})
    report={'input_file':master.name,'input_size':master.stat().st_size,'input_sha256':sha(master),
        'output_file':output.name,'output_size':output.stat().st_size,'output_sha256':sha(output),
        'video_frames':n,'fps':fps,'duration_s':round(n/fps,2),
        'changed_intervals':records,'modified_frames':written,
        'aac_ADTS_sha256':hashlib.sha256(result_adts).hexdigest(),
        'aac_bit_identical_to_master':audio_identical,
        'FFmpeg_full_decode':'PASS',
        'museum_intro_outro':f'not transformed before {KEEP_INTRO_END_SECONDS}s or after {KEEP_OUTRO_BEGIN_SECONDS}s',
        'status':'review_only_not_V25_gold','R2_android_playback':'not_tested',
        'AI_TTS_API_calls':0,'social_posts':0}
    report_path.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--report',type=Path,required=True)
    args=p.parse_args();print(json.dumps(render(args.input,args.output,args.report),ensure_ascii=False,indent=2))