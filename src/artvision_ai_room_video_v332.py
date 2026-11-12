#!/usr/bin/env python3
"""V332 front-on AI-gallery shot adapter, REVIEW ONLY.

- Demo mode: silent 8-second visual front-on approach/return.
- Full mode: preserves the existing Standard's middle frames and copies exact
  original AAC from Standard while replacing only Museum intro/outro frames.
- A single generated room image is 2D: this preview does *not* claim real 3D
  camera parallax. A visible hard cut at room/art transition BLOCKS approval.
- Never modifies Standard; no TTS, Vidu, paid API, publishing or Gold.
"""
from __future__ import annotations
import argparse,hashlib,json,math,subprocess
from pathlib import Path
import numpy as np
import cv2
from PIL import Image,ImageOps


def _sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as fp:
        for block in iter(lambda:fp.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def ease(t):
    t=max(0.,min(1.,float(t)));return t*t*(3-2*t)


def front_image(base_rgb,zoom,out_size):
    """Digital zoom with center fixed: NEVER roll, shear, twist or trapezoid."""
    width,height=base_rgb.size
    zoom=max(1.,float(zoom))
    cw=round(width/zoom);ch=round(height/zoom)
    left=(width-cw)//2;top=(height-ch)//2
    rect=base_rgb.crop((left,top,left+cw,top+ch))
    return np.asarray(ImageOps.fit(rect,out_size,Image.Resampling.LANCZOS).convert('RGB'))[:,:,::-1].copy()


def audio_adts_sha(path):
    output=subprocess.run(['ffmpeg','-hide_banner','-v','error','-i',str(path),'-map','0:a:0',
       '-c:a','copy','-f','adts','pipe:1'],capture_output=True,check=True).stdout
    return hashlib.sha256(output).hexdigest()


def verify_mp4(mp4):
    subprocess.run(['ffmpeg','-hide_banner','-v','error','-xerror','-i',str(mp4),'-map','0','-f','null','-'],check=True)


def boundary_delta(path,frame_idx):
    cap=cv2.VideoCapture(str(path));ims=[]
    try:
        for k in (frame_idx-1,frame_idx):
            cap.set(cv2.CAP_PROP_POS_FRAMES,k)
            ok,im=cap.read()
            if not ok:raise ValueError('Missing frame for boundary QA')
            ims.append(cv2.resize(im,(180,320),interpolation=cv2.INTER_AREA).astype(np.float32))
    finally:cap.release()
    return round(float(np.mean(np.abs(ims[0]-ims[1]))),3)


def render_gallery_video(museum_png,output_mp4,variant,standard_mp4=None,
                          preview_seconds=8.,intro_seconds=4.,outro_seconds=4.,
                          zoom_end=2.7,preview_fps=18,preview_size=(540,960)):
    if variant not in ('cinema_museum','critico_museum'):
        raise ValueError('Only Cinema Museum and Critico Museum')
    museum_png=Path(museum_png);output_mp4=Path(output_mp4)
    if not museum_png.is_file():raise FileNotFoundError(museum_png)
    if output_mp4.exists():raise FileExistsError(output_mp4)
    output_mp4.parent.mkdir(parents=True,exist_ok=True)
    base=Image.open(museum_png).convert('RGB')
    # Apply FIT, not stretch. A 2:3 gallery photo is cropped to 9:16 if needed.
    if standard_mp4:
        standard_mp4=Path(standard_mp4)
        cap=cv2.VideoCapture(str(standard_mp4))
        if not cap.isOpened():raise ValueError('Standard MP4 cannot open')
        fps=cap.get(cv2.CAP_PROP_FPS);frames=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        W=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH));H=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if min(W,H)<300 or fps<=0 or frames<5*fps:
            cap.release();raise ValueError('Standard video too short or resolution invalid')
        if intro_seconds+outro_seconds>frames/fps*.42:
            cap.release();raise ValueError('Museum ends must not overwhelm original content')
    else:
        cap=None;fps=preview_fps;frames=round(preview_seconds*fps)
        W,H=preview_size
    base=ImageOps.fit(base,(W,H),Image.Resampling.LANCZOS)
    in_n=max(1,round(intro_seconds*fps));out_n=max(1,round(outro_seconds*fps))
    if not standard_mp4 and in_n+out_n!=frames:
        raise ValueError('No Standard: silent demo length must match intro+outro exactly')
    command=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','bgr24',
       '-s',f'{W}x{H}','-r',f'{fps:.8f}','-i','pipe:0']
    if standard_mp4:
        command+=['-i',str(standard_mp4),'-map','0:v:0','-map','1:a:0','-c:a','copy']
    else:command+=['-an']
    command+=['-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p',
             '-movflags','+faststart',str(output_mp4)]
    ff=subprocess.Popen(command,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        for i in range(frames):
            if standard_mp4:
                ok,frame=cap.read()
                if not ok:raise ValueError('Source standard prematurely ended')
            else:frame=None
            if i<in_n:
                z=1+(zoom_end-1)*ease(i/max(1,in_n-1))
                frame=front_image(base,z,(W,H))
            elif i>=frames-out_n:
                z=1+(zoom_end-1)*ease((frames-1-i)/max(1,out_n-1))
                frame=front_image(base,z,(W,H))
            ff.stdin.write(frame.tobytes())
        ff.stdin.close();log=ff.stderr.read();code=ff.wait()
        if code:raise RuntimeError('FFmpeg failed '+log.decode(errors='ignore')[-1500:])
    except BaseException:
        ff.kill();ff.wait()
        output_mp4.unlink(missing_ok=True)
        raise
    finally:
        if cap:cap.release()
    verify_mp4(output_mp4)
    qa={'schema':'artvision-ai-gallery-video-qa-v332','output_sha256':_sha(output_mp4),
        'source_photo_sha256':_sha(museum_png),'variant':variant,'fps':fps,'frames':frames,
        'duration_seconds':round(frames/fps,3),'resolution_px':[W,H],
        'room_is_ai_scenography':True,'camera':'digital_frontal_zoom_NOT_3D_PARALLAX',
        'full_ffmpeg_decode':'PASS','original_standard_preserved':True,'approved_Gold':False,
        'human_artistic_review':'PENDING','published':False}
    if standard_mp4:
        qa['original_standard_sha256']=_sha(standard_mp4)
        qa['standard_audio_adts_sha256']=audio_adts_sha(standard_mp4)
        qa['museum_audio_adts_sha256']=audio_adts_sha(output_mp4)
        qa['audio_bitidentical']=qa['standard_audio_adts_sha256']==qa['museum_audio_adts_sha256']
        if not qa['audio_bitidentical']:raise RuntimeError('Audio changed: QA reject')
        deltas=[boundary_delta(output_mp4,in_n),boundary_delta(output_mp4,frames-out_n)]
        qa['room_to_source_boundary_delta']=deltas
        qa['v203_like_boundary_limit']=18.
        qa['museum_transition_gate']='PASS' if max(deltas)<=18 else 'FAIL_ARTISTIC_HARD_CUT'
        qa['status']='REVIEW' if qa['museum_transition_gate']=='PASS' else 'REJECTED_NEEDS_CONTINUOUS_CAMERA_REPAIR'
    else:
        qa['status']='SILENT_8S_DEMO_ONLY_NOT_VARIANT_DELIVERY'
    j=output_mp4.with_suffix('.qa.json');j.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return qa


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--museum-png',required=True,type=Path)
    p.add_argument('--out',required=True,type=Path)
    p.add_argument('--variant',required=True,choices=('cinema_museum','critico_museum'))
    p.add_argument('--standard-mp4',type=Path)
    p.add_argument('--preview-seconds',type=float,default=8.)
    p.add_argument('--intro-seconds',type=float,default=4.)
    p.add_argument('--outro-seconds',type=float,default=4.)
    a=p.parse_args()
    print(json.dumps(render_gallery_video(a.museum_png,a.out,a.variant,a.standard_mp4,
        a.preview_seconds,a.intro_seconds,a.outro_seconds),ensure_ascii=False,indent=2))

if __name__=='__main__':main()