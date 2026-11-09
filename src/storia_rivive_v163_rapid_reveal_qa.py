#!/usr/bin/env python3
"""V163 -- reference-inspired B/W-motion to photographic-color reveal audit.

Pure FFmpeg/OpenCV byte inspection: does NOT restore, invent I2I proof, grant
rights, or publish. User-supplied benchmark reference video bytes stay LOCAL.
Use --mode reference to calibrate cadence; --mode delivery additionally checks
no long black promotional end cards and ensures proper audio and 9:16 format.
"""
import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path

import cv2
import numpy as np

SAMPLE_FPS = 4
SAMPLE_SHAPE = (72, 128)


def probe(media):
    cmd=['ffprobe','-v','error','-show_entries','format=duration:stream=codec_type,codec_name,width,height','-of','json',str(media)]
    out=subprocess.run(cmd,capture_output=True,text=True,timeout=30,check=True)
    metadata=json.loads(out.stdout)
    videos=[s for s in metadata.get('streams',[]) if s.get('codec_type')=='video']
    audios=[s for s in metadata.get('streams',[]) if s.get('codec_type')=='audio']
    if len(videos)!=1 or videos[0].get('codec_name')!='h264':
        raise ValueError('V163_SOURCE_NOT_SINGLE_H264_VIDEO')
    duration=float(metadata['format']['duration'])
    return duration,videos[0],audios


def decode(media):
    w,h=SAMPLE_SHAPE
    cmd=['ffmpeg','-nostdin','-v','error','-i',str(media),'-vf',f'fps={SAMPLE_FPS},scale={w}:{h}:flags=bilinear,format=rgb24','-f','rawvideo','-pix_fmt','rgb24','pipe:1']
    proc=subprocess.run(cmd,capture_output=True,timeout=90,check=True)
    size=w*h*3
    if len(proc.stdout)<size*16 or len(proc.stdout)%size:
        raise ValueError('V163_NOT_ENOUGH_FULLY_DECODED_RGB_FRAMES')
    return np.frombuffer(proc.stdout,dtype=np.uint8).reshape((-1,h,w,3))


def inspect(frames, *, duration, video=None, audios=(), mode='delivery'):
    """Classify actual saturated frames and multiple real B/W-to-color reveals.

    Technical proof of motion is not proof of historical authenticity or true
    AI I2I identity. Review of the restored photo and rights stays mandatory.
    """
    if mode not in ('reference','delivery'):
        raise ValueError('V163_INVALID_MODE')
    if len(frames)<56:
        raise ValueError('V163_TOO_SHORT_TO_MEASURE')
    s=[];grey=[];light=[]
    for f in frames:
        if f.shape[:2]!=(128,72):raise ValueError('V163_WRONG_SAMPLE_RASTER')
        hsv=cv2.cvtColor(f,cv2.COLOR_RGB2HSV)
        # Bypass top/bottom 6% where captions/letterbox can falsely raise color
        center=hsv[12:116,:,:]
        s.append(float(center[:,:,1].mean()))
        g=cv2.cvtColor(f,cv2.COLOR_RGB2GRAY)
        grey.append(g)
        light.append(float(np.mean(g)))
    # B/W threshold accommodates near-monochrome film; >20 is real saturation.
    state=['C' if a>=20 else 'B' if a<=12 else '?' for a in s]
    # In ambiguous frames, use the previous stable state (brief transitions).
    for k,v in enumerate(state):
        if v=='?':state[k]=state[k-1] if k else 'B'
    runs=[]
    for k,v in enumerate(state):
        if not runs or runs[-1][0]!=v:runs.append([v,k,k+1])
        else:runs[-1][2]=k+1
    reveals=[]
    unique=[]
    for i in range(1,len(runs)):
        previous, current = runs[i-1],runs[i]
        if previous[0]!='B' or current[0]!='C':continue
        bstart,bend=previous[1:];cstart,cend=current[1:]
        # Need at least ~0.5s genuine monochrome then ~0.5s color
        if (bend-bstart)<2 or (cend-cstart)<2:continue
        motion=[float(np.abs(grey[q].astype(np.int16)-grey[q-1].astype(np.int16)).mean())
                for q in range(bstart+1,bend)]
        moving=sum(n>=2 for n in motion)>=1
        # Reject entire black endcards: no picture and zero motion.
        if np.mean(light[bstart:bend])<20:continue
        frame=grey[min(bstart+1,bend-1)][16:112,6:66]
        frame=cv2.GaussianBlur(cv2.resize(frame,(32,48)),(5,5),0).astype(np.float32)
        low=frame-frame.mean()
        sig=low / (float(np.linalg.norm(low)) + 1e-5)
        # Each genuinely new shot must not be the same image reframed and repeated.
        same_as_previous=any(float(np.sum(sig*prev))>.975 for prev in unique)
        if not same_as_previous:unique.append(sig)
        reveals.append({
            'start_s':round(bstart/SAMPLE_FPS,2),
            'color_at_s':round(cstart/SAMPLE_FPS,2),
            'bw_s':round((bend-bstart)/SAMPLE_FPS,2),
            'color_s':round((cend-cstart)/SAMPLE_FPS,2),
            'bw_real_motion_observed':moving,
            'bw_motion_mad_max':round(max(motion) if motion else 0,2),
            'visually_distinct_source_fingerprint':not same_as_previous,
        })
    long_black=0
    for val in reversed(light):
        if val<16:long_black+=1
        else:break
    black_tail=round(long_black/SAMPLE_FPS,2)
    first=reveals[0]['color_at_s'] if reveals else None
    gate={
        'duration_in_range_14_35s':14<=duration<=35,
        'at_least_5_reveal_cycles':len(reveals)>=5,
        'at_least_5_distinct_monochrome_sources':len(unique)>=5,
        'every_counted_reveal_preceded_by_observed_bw_motion':len(reveals)>=5 and all(r['bw_real_motion_observed'] for r in reveals),
        'early_color_reveal_by_1_5s':first is not None and first<=1.5,
        'each_reveal_color_visible_at_least_0_5s':len(reveals)>=5 and all(r['color_s']>=.5 for r in reveals),
        'no_long_black_end_card':black_tail<=1.0,
    }
    if mode=='delivery':
        gate['h264_vertical_720x1280']=video is not None and (video.get('width'),video.get('height'))==(720,1280)
        gate['aac_audio_present']=any(a.get('codec_name')=='aac' for a in audios)
    checked=['duration_in_range_14_35s','at_least_5_reveal_cycles','at_least_5_distinct_monochrome_sources',
             'every_counted_reveal_preceded_by_observed_bw_motion','early_color_reveal_by_1_5s','each_reveal_color_visible_at_least_0_5s']
    if mode=='delivery':checked+=['no_long_black_end_card','h264_vertical_720x1280','aac_audio_present']
    result={
        'version':'V163','format':'B_W_MOTION_TO_COLORED_SOURCE_SAME_SHOT_MICRO_REVEALS',
        'mode':mode,'duration_s':round(duration,3),
        'reveal_count':len(reveals),'different_b_w_appearances':len(unique),
        'first_color_at_s':first,'black_endcard_s':black_tail,
        'cycles':reveals,'checks':gate,
        'status':'V163_CADENCE_TECHNICAL_PASS_NOT_ARTISTIC_APPROVAL' if all(gate[k] for k in checked)
                 else 'V163_NOT_LIKE_USER_REFERENCE_BLOCK_FINAL_DELIVERY',
        'claims_genuine_ai_i2i':False,'vidu_clip_verified':False,
        'historical_source_rights_verified':False,'restoration_identity_verified':False,
        'user_artistic_approval':False,'publishing_permitted':False,
        'note':'Matching grayscale/saturation rhythm never certifies restoration or identity. References are analyzed only, not ingested as publishable source.'
    }
    return result


def analyze(path, mode='delivery'):
    duration,video,audios=probe(path)
    frames=decode(path)
    result=inspect(frames,duration=duration,video=video,audios=audios,mode=mode)
    digest=hashlib.sha256(Path(path).read_bytes()).hexdigest()
    result['analyzed_video_sha256']=digest
    return result


if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('video');ap.add_argument('--mode',choices=['reference','delivery'],default='delivery')
    ap.add_argument('--report',required=True)
    args=ap.parse_args();r=analyze(args.video,args.mode)
    Path(args.report).parent.mkdir(parents=True,exist_ok=True)
    Path(args.report).write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
    print(r['status'], 'reveals',r['reveal_count'],'distinct',r['different_b_w_appearances'],'hash',r['analyzed_video_sha256'][:15])