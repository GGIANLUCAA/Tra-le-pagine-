#!/usr/bin/env python3
"""Render ONE storyboard scene silently, never alter approved footage or voice."""
from __future__ import annotations
import argparse, json, subprocess
from pathlib import Path
import cv2
import numpy as np
from illustration_reveals_lab_v2 import animation_maps, frame_at, load_image, sha256

def effect_frame(src,maps,effect,progress,roi):
    if effect=='none':return src.copy()
    if effect=='color_accent':
        gray=cv2.cvtColor(cv2.cvtColor(src,cv2.COLOR_RGB2GRAY),cv2.COLOR_GRAY2RGB)
        p=float(np.clip(progress,0,1))
        effect_image=np.uint8(gray.astype(np.float32)*(1-p)+src.astype(np.float32)*p)
    else:
        effect_image=frame_at(src,maps,effect,max(0.,min(1.,progress)))
    if roi is None:return effect_image
    h,w=src.shape[:2]
    x,y,bw,bh=roi
    x0,y0=int(round(x*w)),int(round(y*h))
    x1,y1=min(w,int(round((x+bw)*w))),min(h,int(round((y+bh)*h)))
    if x1<=x0 or y1<=y0:return src.copy()
    mask=np.zeros((h,w),dtype=np.float32)
    mask[y0:y1,x0:x1]=1.
    mask=cv2.GaussianBlur(mask,(0,0),max(1,round(min(w,h)*.005)))[:,:,None]
    return np.uint8(np.clip(src.astype(np.float32)*(1-mask)+effect_image.astype(np.float32)*mask,0,255))

def render_scene(plan_file,scene_id,image,output,*,width=360,height=640,fps=24,seed=17):
    plan_file,image,output=Path(plan_file),Path(image),Path(output)
    partial=output.with_name(output.stem+'.rendering.mp4')
    if output.suffix.lower()!='.mp4' or any(p.exists() for p in (output,output.with_suffix('.json'),partial)):
        raise FileExistsError('Anteprima nuova richiesta: nessuna sovrascrittura')
    if not image.is_file() or image.suffix.lower() not in ('.png','.jpg','.jpeg','.webp'):
        raise ValueError('Serve una immagine sorgente, mai MP4 master')
    if width%2 or height%2 or min(width,height)<64 or width*height>1920*1080 or not 10<=fps<=60:
        raise ValueError('Dimensioni o fps non validi')
    plan=json.loads(plan_file.read_text(encoding='utf-8'))
    if plan.get('schema')!='narrative-reveal-plan-v3':raise ValueError('Piano V3 non valido')
    found=[r for r in plan['scenes'] if r['id']==scene_id]
    if len(found)!=1:raise ValueError('Scena mancante o duplicata')
    row=found[0]
    if row['visual_mode']!='illustration':raise ValueError('Non alterare quadro/documento autentico')
    src=load_image(image,width,height)
    maps=animation_maps(src,seed)
    requested=row['effect'];chosen=requested if maps[4] else 'none'
    if requested=='color_accent' and row['effect_target']!='roi':chosen='none'
    roi=row['focus_roi'] if row['effect_target']=='roi' else None
    duration=float(row['duration_s']);count=round(duration*fps)
    if not 0<count<=fps*240:raise ValueError('Durata clip fuori limite')
    t_start=float(row['effect_start_s']);t_len=float(row['effect_duration_s'])
    if chosen!='none' and t_len<=0:chosen='none'
    output.parent.mkdir(parents=True,exist_ok=True)
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-nostdin','-y','-f','rawvideo',
         '-pix_fmt','rgb24','-s:v',f'{width}x{height}','-r',str(fps),'-i','pipe:0',
         '-an','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p',
         '-movflags','+faststart',str(partial)]
    proc=None
    try:
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        for i in range(count):
            clock=i/fps
            if chosen=='none' or (roi is None and clock<t_start):
                frame=src
            else:
                progress=float(np.clip((clock-t_start)/max(t_len,.0001),0,1))
                progress=progress*progress*(3-2*progress)
                frame=effect_frame(src,maps,chosen,progress,roi)
            proc.stdin.write(frame.tobytes())
        proc.stdin.close()
        err=proc.stderr.read().decode(errors='replace');code=proc.wait()
        proc.stderr.close()
        if code or not partial.is_file() or partial.stat().st_size<1000:
            raise RuntimeError('FFmpeg failed: '+err[-800:])
        partial.replace(output)
    except Exception:
        if proc is not None and proc.poll() is None:proc.kill()
        partial.unlink(missing_ok=True)
        raise
    result={'schema':'narrative-reveal-render-v3',
      'status':'technical_preview_needs_artist_review','scene':scene_id,
      'effect_requested':requested,'effect_applied':chosen,'safety_fallback':chosen!=requested,
      'duration_seconds':round(count/fps,3),'fps':fps,
      'effect_start_seconds':t_start,'effect_duration_seconds':t_len,
      'hold_after_seconds':row['visible_hold_s'],'source_image':str(image),
      'source_sha256':sha256(image),'preview':str(output),'preview_sha256':sha256(output),
      'voice_synced':False,'voice_preserved':True,'master_modified':False,
      'auto_publish':False,'ai_api_calls':0}
    output.with_suffix('.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan',type=Path,required=True)
    p.add_argument('--scene',required=True)
    p.add_argument('--image',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--width',type=int,default=360)
    p.add_argument('--height',type=int,default=640)
    p.add_argument('--fps',type=int,default=24)
    a=p.parse_args()
    print(json.dumps(render_scene(a.plan,a.scene,a.image,a.out,width=a.width,height=a.height,fps=a.fps),ensure_ascii=False,indent=2))

if __name__=='__main__':main()
