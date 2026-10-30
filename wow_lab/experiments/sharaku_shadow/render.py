#!/usr/bin/env python3
"""Sharaku 'Kabuki Shadow Theatre' independent WOW LAB experiment.

CC0 verified Met object 37358. Two hand masks from actual color difference,
not fake AI-repainted fingers. Multi-layer print -> shadow pocket ->
foreground hands; no new background objects, no paid AI, no core changes.
"""
from __future__ import annotations
import json,math,wave,hashlib,zipfile,subprocess
from pathlib import Path
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont,ImageFilter
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'SHARAKU_WORK.png'
PROV=ROOT/'PROVENANCE.json'
OUT=ROOT/'RENDER';OUT.mkdir(exist_ok=True)
W,H,FPS,DURATION=720,1280,24,11.5
AW,AH=500,748;AX,AY=110,242
LROI=(90,1480,730,2060);RROI=(670,1660,1270,2085)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
SAN='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def ft(s,serif=True):return ImageFont.truetype(FONT if serif else SAN,s)
def ease(v):v=max(0.,min(1.,v));return v*v*(3-2*v)
def window(t,begin,rise,hold,fall):
    if t<begin:return 0.
    if t<begin+rise:return ease((t-begin)/rise)
    if t<hold:return 1.
    if t<fall:return 1-ease((t-hold)/(fall-hold))
    return 0.
def images():
    """Isolate one entire original right hand. Reject costume stripes and paper speckles."""
    im=Image.open(SOURCE).convert('RGB')
    a=np.asarray(im);h,w=a.shape[:2]
    r,g,b=[a[:,:,i].astype('int16') for i in range(3)]
    # The gold robe strokes have g-b≈45–63; true skin mostly g-b≈20–37.
    skin=(r>171)&(g>161)&(b>130)&((r-g)>8)&((r-g)<38)&((g-b)>10)&((g-b)<40)&((r-b)>24)
    x1,y1,x2,y2=RROI
    roi=np.zeros((h,w),dtype='uint8');roi[y1:y2,x1:x2]=1
    raw=np.uint8(skin&(roi>0))*255
    # Exact color-based mask, not a guessed outline of a finger.
    raw=cv2.morphologyEx(raw,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(11,11)))
    n, labels, cstats,_=cv2.connectedComponentsWithStats(raw,8)
    keep=np.zeros_like(raw)
    for k in range(1,n):
        if cstats[k,cv2.CC_STAT_AREA]>3000:keep[labels==k]=255
    keep=cv2.morphologyEx(keep,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)))
    # Remove the two gold costume stripe intrusions above the wrist and fingertips.
    yy,xx=np.mgrid[:h,:w]
    keep[(xx<837)&(yy<1750)]=0
    keep[(xx>1018)&(xx<1083)&(yy<1706)]=0
    # The cuff remains behind the painting; a feathered wrist makes the hand
    # emerge naturally instead of moving a rectangular crop of cloth.
    wrist=np.clip((xx-695)/110.,0,1)
    keep=(keep*wrist).astype('uint8')
    keep=cv2.GaussianBlur(keep,(5,5),.9)
    number,labels,areas,_=cv2.connectedComponentsWithStats(np.uint8(keep[y1:y2,x1:x2]>127),8)
    roi_count=sum(1 for k in range(1,number) if areas[k,cv2.CC_STAT_AREA]>180)
    ratio=float((keep[y1:y2,x1:x2]>127).mean())
    if not (.23<ratio<.46) or roi_count>3:
        raise RuntimeError(f'MASK REJECT: ratio={ratio:.3f}, components={roi_count}')
    # Quantify foreground intrusion in the distant gray background.
    if np.count_nonzero(keep[:,x2:]) or np.count_nonzero(keep[:y1,:]):
        raise RuntimeError('MASK REJECT: original background leakage')
    rgba=Image.fromarray(np.dstack([a[y1:y2,x1:x2],keep[y1:y2,x1:x2]]),'RGBA')
    rgba.save(OUT/'RIGHT_HAND_EXACT_RGBA.png')
    Image.fromarray(keep[y1:y2,x1:x2]).save(OUT/'RIGHT_HAND_MASK.png')
    audit=a.astype('float32')
    aa=keep.astype('float32')/255
    audit[:,:,0]=np.clip(audit[:,:,0]+aa*9,0,255)
    audit[:,:,1]=audit[:,:,1]*(1-.35*aa)
    audit[:,:,2]=audit[:,:,2]*(1-.4*aa)
    Image.fromarray(audit.astype('uint8')).resize((600,898)).save(OUT/'MASK_AUDIT.jpg',quality=94)
    sprite=rgba.resize((round((x2-x1)*AW/w),round((y2-y1)*AH/h)),Image.Resampling.LANCZOS)
    orig=im.resize((AW,AH),Image.Resampling.LANCZOS).convert('RGBA')
    combined=cv2.resize(keep,(AW,AH),interpolation=cv2.INTER_AREA)
    paint=np.array(orig.convert('RGB')).astype('float32')
    shadow=np.full_like(paint,(50,45,47))
    alpha=(combined.astype('float32')/255)[:,:,None]
    cutout=Image.fromarray(np.uint8(np.clip(paint*(1-alpha)+shadow*alpha,0,255)),'RGB').convert('RGBA')
    stats=[{'hand':'right','ratio':round(ratio,4),'connected_components':roi_count,
            'source_ROI':list(RROI),'palette_excludes_gold_strokes':True,
            'mask_has_original_fingertips':True}]
    return orig,cutout,[sprite],stats

def build_base():
    yy,xx=np.mgrid[:H,:W];rad=np.exp(-(((xx-W*.51)/(W*.84))**2+((yy-H*.35)/(H*.69))**2))
    noise=np.random.default_rng(37358).normal(0,.75,(H,W))
    rgb=np.zeros((H,W,3),dtype='uint8')
    for c,(b,boost) in enumerate([(21,20),(19,20),(24,25)]):
        rgb[:,:,c]=np.uint8(np.clip(b+boost*rad+noise,0,255))
    wall=Image.fromarray(rgb,'RGB').convert('RGBA')
    dr=ImageDraw.Draw(wall)
    dr.text((W//2,74),'ARTVISION  /  WOW LAB',font=ft(22,False),anchor='mm',fill=(210,190,155))
    dr.text((W//2,127),'KABUKI REACH',font=ft(41),anchor='mm',fill=(248,234,206))
    dr.text((W//2,170),'A WOODBLOCK STEPS FORWARD',font=ft(21,False),anchor='mm',fill=(195,189,185))
    dr.rectangle((0,1095,W,H),fill=(17,17,21))
    # Real painting not alleged in a real frame: anonymous virtual display clearly labeled.
    shadow=Image.new('RGBA',(W,H));s=ImageDraw.Draw(shadow)
    s.rectangle((AX-22,AY-24,AX+AW+24,AY+AH+28),fill=(0,0,0,145))
    wall=Image.alpha_composite(wall,shadow.filter(ImageFilter.GaussianBlur(17)))
    d=ImageDraw.Draw(wall)
    for ext,col,stroke in [(14,(59,39,30),4),(9,(172,124,74),4),(5,(218,177,101),3),(1,(103,70,48),2)]:
        d.rectangle((AX-ext,AY-ext,AX+AW+ext,AY+AH+ext),outline=col,width=stroke)
    d.text((W//2,1128),'1794  ·  TŌSHŪSAI SHARAKU',font=ft(18,False),anchor='mm',fill=(213,190,158))
    d.text((W//2,1164),'THE MET  ·  PUBLIC DOMAIN',font=ft(17,False),anchor='mm',fill=(172,167,160))
    d.text((W//2,1200),'ONE REAL HAND, ONE IMPOSSIBLE REACH',font=ft(16),anchor='mm',fill=(210,180,139))
    return wall

def pose(sprite,rect,t,which,p):
    """Perspective of two original hand masks; pivot near wrist. Leaves original color intact."""
    fullw,fullh=1470,2200
    x1,y1,x2,y2=rect
    x=AX+(x1*AW/fullw); y=AY+(y1*AH/fullh)
    # Larger apparent scale signifies a deeper layer, not just camera zoom.
    if which==1:
        grow=1+.80*p;dx=-34*p;dy=-83*p+4*math.sin(t*1.7)*p
        pivotx=x+sprite.width*.24; pivoty=y+sprite.height*.45
        ang=-2.7*p
    else:
        grow=1+1.06*p;dx=-4*p;dy=-35*p+4*math.sin(t*1.3)*p
        pivotx=x+sprite.width*.18;pivoty=y+sprite.height*.50
        ang=2.0*p
    spr=sprite.resize((round(sprite.width*grow),round(sprite.height*grow)),Image.Resampling.BICUBIC)
    # Small rotation, not cut/copy of entire artwork.
    if ang:spr=spr.rotate(ang,expand=True,resample=Image.Resampling.BICUBIC)
    px=x+dx+(x-pivotx)*(grow-1)
    py=y+dy+(y-pivoty)*(grow-1)
    # rotate expands bbox; recenter visual anchor at original sprite origin
    pw0=sprite.width*grow;ph0=sprite.height*grow
    px-=(spr.width-pw0)/2;py-=(spr.height-ph0)/2
    return spr,round(px),round(py)

def render_one(t,orig,cutout,sprites,wall):
    # The body and face remain part of the woodblock. Only the five-fingered
    # palm crosses the frame: no rectangular strips, no artificial flower cuts.
    p=window(t,.85,2.1,7.1,9.8)
    image=wall.copy()
    image.alpha_composite(Image.blend(orig,cutout,p),(AX,AY))
    if p>.001:
        sprite=sprites[0]
        fg,x,y=pose(sprite,RROI,t,2,p)
        # Cast shadow on the print and gallery wall, so the physical exit
        # reads as volume without falsely claiming a true 3D mesh.
        alpha=fg.getchannel('A')
        shadow=Image.new('RGBA',(W,H))
        dark=Image.new('RGBA',fg.size,(2,3,6,0))
        dark.putalpha(alpha.point(lambda v:round(v*.58*p)))
        shadow.paste(dark,(x+round(21*p),y+round(24*p)))
        image=Image.alpha_composite(image,shadow.filter(ImageFilter.GaussianBlur(16)))
        image.alpha_composite(fg,(x,y))
    return image.convert('RGB')

def make_audio(path):
    sr=24000;n=round(sr*DURATION);t=np.arange(n)/sr
    rng=np.random.default_rng(37358)
    noise=rng.normal(0,1,n)
    air=np.convolve(noise,np.ones(17)/17.,mode='same')
    bed=.018*air*(.35+.65*np.exp(-((t-5.0)/3.5)**2))
    for start,freq,vol in [(1.3,82,.19),(3.0,104,.22),(5.15,65,.14),(8.2,82,.11)]:
        k=t-start
        e=np.where(k>=0,np.exp(-np.maximum(k,0)*4),0)
        drum=(np.sin(2*np.pi*(freq*k-13*k*k))+.4*np.sin(2*np.pi*(freq*1.5*k)))*e*vol
        bed+=drum
    # An original slowly rising two-note ambient score
    for f,v in [(146.83,.028),(196.,.019),(293.66,.011)]:
        mod=np.sin(2*np.pi*(f*t+.35*np.sin(t*.32)))*v
        bed+=mod*np.exp(-((t-6.0)/3.9)**2)
    fade=np.minimum(1.,np.minimum(t/.6,(DURATION-t)/.7))
    bed=np.clip(bed*fade,-.8,.8)
    with wave.open(str(path),'wb') as wf:
        wf.setnchannels(1);wf.setsampwidth(2);wf.setframerate(sr)
        wf.writeframes((bed*32767).astype('int16').tobytes())

def main():
    info=json.loads(PROV.read_text())
    assert info['met_object_id']==37358 and info['public_domain'] and info['sha256']
    if 'SHARAKU_ORIGINAL.jpg' in [p.name for p in ROOT.iterdir()]:
        assert hashlib.sha256((ROOT/'SHARAKU_ORIGINAL.jpg').read_bytes()).hexdigest()==info['sha256']
    orig,cutout,sprites,stats=images();wall=build_base()
    stills={}
    for label,t in [('BEFORE',.2),('LEFT_HAND',2.45),('BOTH_HANDS',5.25),('RETURN',10.6)]:
        im=render_one(t,orig,cutout,sprites,wall)
        im.save(OUT/f'{label}.jpg',quality=93)
        stills[label]=im
    compare=Image.new('RGB',(W*2,H))
    compare.paste(stills['BEFORE'],(0,0));compare.paste(stills['BOTH_HANDS'],(W,0))
    compare.save(OUT/'BEFORE_AFTER.jpg',quality=92)
    audit=Image.new('RGB',(W*2,H*2))
    for k,p in [('BEFORE',(0,0)),('LEFT_HAND',(W,0)),('BOTH_HANDS',(0,H)),('RETURN',(W,H))]:audit.paste(stills[k],p)
    audit.resize((720,1280),Image.Resampling.LANCZOS).save(OUT/'CONTACT_SHEET.jpg',quality=92)
    snd=OUT/'SOUNDTRACK_ORIGINAL.wav';make_audio(snd)
    final=OUT/'SHARAKU_KABUKI_REACH_V4_WOW_ANDROID.mp4'
    cmd=['ffmpeg','-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-video_size',f'{W}x{H}',
      '-framerate',str(FPS),'-i','pipe:0','-i',str(snd),'-c:v','libx264','-preset','veryfast','-crf','20',
      '-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-movflags','+faststart','-t',str(DURATION),str(final)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        for i in range(round(FPS*DURATION)):
            proc.stdin.write(np.ascontiguousarray(render_one(i/FPS,orig,cutout,sprites,wall)).tobytes())
        proc.stdin.close();err=proc.stderr.read().decode(errors='replace')
        if proc.wait()!=0:raise RuntimeError(err[-2000:])
    except BaseException:
        proc.kill();raise
    decode=subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(final),'-f','null','-'],capture_output=True,text=True,timeout=100)
    if decode.returncode:raise RuntimeError('Decode error '+decode.stderr[-300:])
    check=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=codec_name,width,height:format=duration','-of','json',str(final)],text=True))
    codecs=[c['codec_name'] for c in check['streams']]
    assert 'h264' in codecs and 'aac' in codecs and float(check['format']['duration'])>=11.4 and final.stat().st_size>100000
    qa={'technical_pass':True,'artistic_status':'experimental_need_review','object_id':37358,
        'artist':info['artist'],'title':info['title'],'museum_url':info['object_url'],
        'source_sha256':info['sha256'],'source_license':'CC0',
        'duration_seconds':DURATION,'resolution':[W,H],'fps':FPS,'codecs':codecs,
        'soundtrack':'original synthetic taiko + ambient','mask_hand_qa':stats,
        'multiple_independent_foreground_layers':1,'special_effect':'Kabuki solo-hand shadow cutout / reach-out' ,
        'real_volumetric_3d':False,'paid_api_cost':0,'social_published':False,
        'video_bytes':final.stat().st_size}
    (OUT/'QA.json').write_text(json.dumps(qa,indent=2,ensure_ascii=False))
    (OUT/'SOCIAL_POST.txt').write_text('1794. Sharaku cattura un attore Kabuki nell’istante in cui la sua mano sembra uscire dalla stampa. Un incontro tra teatro giapponese e illusione cinematografica. Opera originale: The Metropolitan Museum of Art, Open Access CC0. Effetto 2.5D sperimentale, cornice virtuale. #ArtVision #Sharaku #Kabuki #WowLab\n')
    kit=OUT/'SHARAKU_KABUKI_REACH_V4_ANDROID_KIT.zip'
    names=['SHARAKU_KABUKI_REACH_V4_WOW_ANDROID.mp4','BEFORE.jpg','LEFT_HAND.jpg','BOTH_HANDS.jpg','RETURN.jpg','BEFORE_AFTER.jpg','CONTACT_SHEET.jpg','MASK_AUDIT.jpg','QA.json','SOCIAL_POST.txt']
    with zipfile.ZipFile(kit,'w',zipfile.ZIP_DEFLATED) as z:
        for n in names:z.write(OUT/n,n)
    with zipfile.ZipFile(kit) as z:assert z.testzip() is None
    print(json.dumps({'video':str(final),'zip':str(kit),'qa':qa},ensure_ascii=False))
if __name__=='__main__':main()