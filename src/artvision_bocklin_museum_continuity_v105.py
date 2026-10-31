#!/usr/bin/env python3
"""Offline, non-destructive Böcklin Critico Museum V105 continuity correction.
Uses only verified original V102 MP4 frames; no TTS, source generation, or API calls.
Original AAC is copied bit-for-bit. Museum room remains a digital reconstruction.
"""
import argparse, hashlib, json, subprocess
from pathlib import Path
import cv2
import numpy as np

EXPECTED_SOURCE_SHA='03eb6c8a77c4572b7ca83c81088c4b3d499b06802dd996a97a505b6fe768a6ed'
FPS=20
W,H=720,1280

def sha(path):
    d=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(1<<20),b''):d.update(block)
    return d.hexdigest()

def check(cmd):
    p=subprocess.run([str(x) for x in cmd],capture_output=True,text=True)
    if p.returncode:raise RuntimeError('command failed '+str(cmd)+'\n'+p.stderr[-2500:])
    return p.stdout

def read_at(c,n):
    c.set(cv2.CAP_PROP_POS_FRAMES,n)
    ok,f=c.read()
    if not ok:raise ValueError('cannot decode source frame '+str(n))
    return f

def align(a,b):
    sift=cv2.SIFT_create(nfeatures=3500,contrastThreshold=.012)
    ka,da=sift.detectAndCompute(cv2.cvtColor(a,cv2.COLOR_BGR2GRAY),None)
    kb,db=sift.detectAndCompute(cv2.cvtColor(b,cv2.COLOR_BGR2GRAY),None)
    matches=cv2.BFMatcher().knnMatch(da,db,k=2)
    good=[m for m,n in matches if m.distance<.75*n.distance]
    x=np.float32([ka[m.queryIdx].pt for m in good]);y=np.float32([kb[m.trainIdx].pt for m in good])
    affine,inliers=cv2.estimateAffinePartial2D(x,y,method=cv2.RANSAC,ransacReprojThreshold=4)
    if affine is None or inliers.sum()<50:raise RuntimeError('painting registration failed')
    return np.vstack([affine,[0,0,1]]),int(inliers.sum())

def smooth(x):
    x=np.clip(x,0,1);return x*x*(3-2*x)

def warp(im,m):
    return cv2.warpPerspective(im,m,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)

def blend(a,b,u):
    return np.uint8(np.clip(a.astype(np.float32)*(1-u)+b.astype(np.float32)*u,0,255))

def prepare(c):
    # Entrance 4.00-5.00s: continuous photo push-in, then registered texture handoff.
    photo=read_at(c,80);painting=read_at(c,100)
    H_enter,entry_inliers=align(photo,painting)
    photo_close=warp(photo,H_enter)
    patches={}
    for n in range(80,100):
        if n<95:
            u=smooth((n-80)/15)
            patches[n]=warp(photo,(1-u)*np.eye(3)+u*H_enter)
        else:
            patches[n]=blend(photo_close,painting,smooth((n-95)/5))
    # Exit 102.65-103.65s: use an EARLIER genuine photo frame with full sky coverage.
    # This prevents the top-edge holes caused by zooming the late frame beyond its bounds.
    painting=read_at(c,2053);photo_wide=read_at(c,80);photo_final=read_at(c,2073)
    H_wide,wide_inliers=align(painting,photo_wide)
    H_final,final_inliers=align(painting,photo_final)
    H_start=np.linalg.inv(H_wide)
    H_end=H_final@H_start
    wide_close=warp(photo_wide,H_start)
    wide_final=warp(photo_wide,H_end)
    for n in range(2053,2073):
        if n<2057:
            patches[n]=blend(painting,wide_close,smooth((n-2053)/4))
        elif n<2070:
            u=smooth((n-2057)/13)
            patches[n]=warp(photo_wide,(1-u)*H_start+u*H_end)
        else:
            patches[n]=blend(wide_final,photo_final,smooth((n-2070)/3))
    return patches,dict(entry_inliers=entry_inliers,exit_wide_inliers=wide_inliers,exit_final_inliers=final_inliers,
                        corrected_frame_ranges=[[80,99],[2053,2072]],source_frame_indices=[80,100,2053,2073])

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();args.output.parent.mkdir(parents=True,exist_ok=True)
    if sha(args.source)!=EXPECTED_SOURCE_SHA:raise ValueError('Wrong original master SHA')
    cap=cv2.VideoCapture(str(args.source));fps=cap.get(cv2.CAP_PROP_FPS);count=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if abs(fps-FPS)>.01 or count!=2213:raise ValueError(f'Unexpected source fps/framecount {fps}/{count}')
    patches,alignment=prepare(cap);cap.set(cv2.CAP_PROP_POS_FRAMES,0)
    silent=args.output.with_name(args.output.stem+'_SILENT_TMP.mp4')
    ff=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}',
        '-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p',str(silent)]
    pipe=subprocess.Popen(ff,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        for n in range(count):
            ret,frame=cap.read()
            if not ret:raise RuntimeError(f'Source ended at frame {n}')
            pipe.stdin.write(patches.get(n,frame).tobytes())
    finally:
        cap.release();pipe.stdin.close()
    err=pipe.stderr.read().decode('utf8','replace')
    if pipe.wait()!=0:raise RuntimeError('FFmpeg encode failed '+err[-2500:])
    check(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',silent,'-i',args.source,
           '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','copy','-movflags','+faststart','-shortest',args.output])
    silent.unlink()
    check(['ffmpeg','-hide_banner','-loglevel','error','-xerror','-i',args.output,'-f','null','-'])
    qa={'source_sha256':EXPECTED_SOURCE_SHA,'output_sha256':sha(args.output),'output_bytes':args.output.stat().st_size,
        'fps':FPS,'frames':count,'duration_seconds':count/FPS,'video_codec':'H264','audio_codec':'AAC copied from V102',
        'ffmpeg_full_decode':'PASS','alignment':alignment,'V25_Gold':False,'R2_Android_verified':False,
        'editorial_status':'candidate_review_only','no_tts_no_api_no_paid_calls':True,
        'source_image':'Original V102 frames only, same Böcklin 1883 NG 2/80',
        'frame_photo_credit':'Sailko CC BY 3.0; museum room digitally reconstructed, not authentic gallery'}
    args.output.with_suffix('.qa.json').write_text(json.dumps(qa,indent=2,ensure_ascii=False))
    print(json.dumps(qa,indent=2,ensure_ascii=False))
if __name__=='__main__':main()