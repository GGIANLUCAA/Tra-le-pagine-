#!/usr/bin/env python3
"""Pieter Bruegel Dulle Griet: one new Cinema Standard private review with genuine museum restoration source.
No paid API, TTS, Vidu, fictional Museum, Gold or publication.
"""
import hashlib, json, math, subprocess, urllib.parse, urllib.request, wave, zipfile
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT=Path('output/artvision-owner-dulle-griet-cinema-v1')
OUT.mkdir(parents=True,exist_ok=True)
PAGE='https://commons.wikimedia.org/wiki/File:Pieter_Brueghel_-_Dulle_Griet_-_Museum_Mayer_van_den_Bergh_-_MMB.0045.tif'
SOURCE_TIF='Pieter_Brueghel_-_Dulle_Griet_-_Museum_Mayer_van_den_Bergh_-_MMB.0045.tif'
SOURCE_2016='Dulle_Griet,_by_Pieter_Brueghel_(I).jpg'
PAGE_2016='https://commons.wikimedia.org/wiki/File:Dulle_Griet,_by_Pieter_Brueghel_(I).jpg'
thumbnail='https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/'+SOURCE_TIF+'/lossy-page1-3840px-'+SOURCE_TIF+'.jpg'
old_md5=hashlib.md5(SOURCE_2016.encode()).hexdigest()
older='https://upload.wikimedia.org/wikipedia/commons/'+old_md5[0]+'/'+old_md5[:2]+'/'+urllib.parse.quote(SOURCE_2016,safe='._-')
urls=[('RESTORED_2021_3840px_WUYTS_DERIVATIVE',thumbnail,(3840,2814),None),
      ('PRE_RESTORATION_2016_ARCHIVE',older,(6000,4334),'0ecddb27579d6fbb9ef6489d4b204aef5d034828')]
original=OUT/'ORIGINAL_ARTWORK.jpg'
actual_url=None
selected_source=None
for tag,url,pixels,expected_sha1 in [(a,b,c,d) for a,b,c,d in urls]:
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'ArtVisionOwnerPrivateReview/1.0 (https://github.com/GGIANLUCAA/Tra-le-pagine-)'})
        with urllib.request.urlopen(req,timeout=110) as f:
            data=f.read(45_000_001)
        if not (500_000<len(data)<=45_000_000):
            raise ValueError('source bytes out of expected JPEG envelope')
        if expected_sha1 and hashlib.sha1(data).hexdigest()!=expected_sha1:
            raise ValueError('archived exact SHA1 differs')
        original.write_bytes(data)
        with Image.open(original) as im:
            if im.format!='JPEG' or im.size!=pixels:raise ValueError('source image JPEG dimensions differ')
            im.verify()
        actual_url=url
        selected_source=tag
        SOURCE_PIXELS=pixels
        SOURCE_SIZE=len(data)
        SOURCE_SHA1=hashlib.sha1(data).hexdigest()
        break
    except Exception as e:
        print('SOURCE_ATTEMPT_FAILED',tag,type(e).__name__,str(e)[:180],flush=True)
if not actual_url:raise RuntimeError('EXACT_GENUINE_DULLE_GRIET_SOURCE_UNAVAILABLE; NO_VIDEO_PRODUCED')
print('EXACT_ARTWORK_PHOTOGRAPH_VERIFIED',selected_source,SOURCE_SHA1,SOURCE_SIZE,SOURCE_PIXELS,flush=True)

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1<<20),b''):h.update(chunk)
    return h.hexdigest()
def run(args):
    r=subprocess.run([str(x) for x in args],capture_output=True)
    if r.returncode:raise RuntimeError(r.stderr.decode(errors='replace')[-2000:])
    return r.stdout

# Deliberately varied camera subjects, not automatic repetitive zooming.
# Scene labels are editorial hypotheses until full-speed artistic review.
shots=[
 ('OPEN: THE MOUTH OF HELL',2.4,(.10,.58,.66),(.14,.55,.60)),
 ('PANORAMA: DULLE GRIET',4.1,None,None),
 ('THE ARMOURED WOMAN',4.8,(.34,.59,.66),(.40,.58,.60)),
 ('HOUSEHOLD OBJECTS AND ARMOUR',4.1,(.44,.71,.53),(.44,.68,.48)),
 ('FIGURES SURROUNDING THE GIANT MOUTH',4.3,(.18,.72,.70),(.22,.70,.63)),
 ('THE INFERNAL CREATURES',4.2,(.67,.64,.62),(.70,.62,.57)),
 ('FANTASTIC LANDSCAPE AND TOWER',4.3,(.74,.41,.76),(.75,.44,.69)),
 ('WOMEN IN THE CHAOS',4.4,(.64,.72,.62),(.59,.70,.57)),
 ('DISTANT FIRES AND HORIZON',4.1,(.68,.21,.76),(.62,.23,.70)),
 ('THE STRANGE FACES',4.1,(.86,.52,.68),(.82,.55,.63)),
 ('THE NIGHTMARE AS A WHOLE',4.4,(.48,.50,.89),(.53,.51,.83)),
 ('RETURN: THE FULL PAINTING',6.0,None,None),
]
FPS=24;W=1080;H=1920
frame_counts=[round(s[1]*FPS) for s in shots]
N=sum(frame_counts);DURATION=N/FPS
assert 48<DURATION<57 and len(shots)==12

# Original soundtrack: additive tones and self-synthesized low percussion.
SR=32000
n_audio=round((DURATION+.08)*SR)
t=np.arange(n_audio,dtype=np.float64)/SR
audio=np.zeros((n_audio,2),np.float64)
tones=[41.203,49.0,55.0,43.65,61.735,55.0,65.406]
for k,start in enumerate(np.arange(0,DURATION,7.0)):
    a=round(start*SR);b=min(n_audio,round((start+8)*SR))
    if b<=a:continue
    u=t[a:b]-start
    env=np.clip(u/.9,0,1)*np.clip((b-a)/SR-u,0,1)
    f=tones[k%len(tones)]
    sound=env*(.033*np.sin(2*np.pi*f*u+.18*np.sin(2*np.pi*.09*u))+
             .013*np.sin(2*np.pi*f*2.01*u+.45)+.019*np.sin(2*np.pi*(f/2)*u))
    audio[a:b,0]+=sound
    audio[a:b,1]+=sound*.94
    for beat in (0,3.5):
        p=round((start+beat)*SR)
        if p>=n_audio:continue
        n=min(round(1.2*SR),n_audio-p)
        z=np.arange(n)/SR
        drum=.045*np.exp(-6*z)*np.sin(2*np.pi*(62-24*z)*z)
        audio[p:p+n,:]+=drum[:,None]
audio[:,0]+=.006*np.sin(2*np.pi*42*t)
audio[:,1]+=.006*np.sin(2*np.pi*42.13*t+.18)
audio*=np.clip(t/1.2,0,1)[:,None]*np.clip((DURATION-t)/2.8,0,1)[:,None]
audio=np.tanh(audio*1.5)*.82
score=OUT/'ORIGINAL_MUSIC.wav'
with wave.open(str(score),'wb') as wav:
    wav.setnchannels(2);wav.setsampwidth(2);wav.setframerate(SR)
    wav.writeframes((audio*32767).astype('<i2').tobytes())

art=Image.open(original).convert('RGB')
art.thumbnail((16000,6000),Image.Resampling.LANCZOS)
src=np.asarray(art)[:,:,::-1].copy()
ah,aw=src.shape[:2]
background=cv2.GaussianBlur(cv2.resize(src,(W,H),interpolation=cv2.INTER_AREA),(0,0),51)
background=cv2.convertScaleAbs(background,alpha=.28)
wide=background.copy()
full_w=min(W-42,int((H-300)*aw/ah));full_h=round(full_w*ah/aw)
x0=(W-full_w)//2;y0=(H-full_h)//2
wide[y0:y0+full_h,x0:x0+full_w]=cv2.resize(src,(full_w,full_h),interpolation=cv2.INTER_AREA)
def detail(p):
    cx,cy,hfrac=p
    hh=min(ah,max(180,round(ah*hfrac)))
    ww=min(aw,max(100,round(hh*W/H)))
    x=max(0,min(aw-ww,round(cx*aw-ww/2)))
    y=max(0,min(ah-hh,round(cy*ah-hh/2)))
    return cv2.resize(src[y:y+hh,x:x+ww],(W,H),interpolation=cv2.INTER_AREA)

cover=Image.fromarray(cv2.cvtColor(wide,cv2.COLOR_BGR2RGB))
draw=ImageDraw.Draw(cover)
title_font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',53)
small_font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',29)
draw.text((W/2,300),'DULLE GRIET',font=title_font,fill=(236,231,216),anchor='mm')
draw.text((W/2,1660),'PIETER BRUEGEL  ·  1563',font=small_font,fill=(226,221,201),anchor='mm')
cover.save(OUT/'COVER.jpg',quality=92)

mp4=OUT/'VIDEO_REVIEW.mp4'
cmd=['ffmpeg','-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-i',str(score),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','veryfast','-crf','21','-pix_fmt','yuv420p','-c:a','aac','-b:a','144k','-shortest','-movflags','+faststart',str(mp4)]
proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
contact=[];story=[];cursor=0
try:
    for k,((label,duration,frm,to),count) in enumerate(zip(shots,frame_counts)):
        for i in range(count):
            q=i/max(1,count-1);s=q*q*(3-2*q)
            if frm is None:frame=wide.copy()
            else:frame=detail(tuple(frm[j]+(to[j]-frm[j])*s for j in range(3)))
            # Short movement continuity ramps at scene boundaries.
            # Keep visible content faithful to the real source painting.
            prev=shots[k-1][3] if k>0 else None
            ramp=min(count//3,round(.70*FPS))
            if k>0 and i<ramp:
                e=i/max(1,ramp-1);e=e*e*(3-2*e)
                if prev is not None and frm is not None:
                    p=tuple(prev[j]+(frm[j]-prev[j])*e for j in range(3))
                    frame=detail(p)
                elif prev is None and frm is not None:
                    frame=cv2.addWeighted(wide,1-e,detail(frm),e,0)
                elif prev is not None and frm is None:
                    frame=cv2.addWeighted(detail(prev),1-e,wide,e,0)
            if k==0 and i<round(1.4*FPS):
                panel=frame.copy()
                cv2.rectangle(panel,(0,94),(W,214),(20,23,25),-1)
                alpha=max(0,.55*min(1,i/10)*min(1,(1.4*FPS-i)/10))
                frame=cv2.addWeighted(panel,alpha,frame,1-alpha,0)
                cv2.putText(frame,'DULLE GRIET',(52,162),cv2.FONT_HERSHEY_SIMPLEX,1.04,(235,230,210),2,cv2.LINE_AA)
            proc.stdin.write(np.ascontiguousarray(frame).tobytes())
            if i==count//2:contact.append((cursor+i/FPS,cv2.resize(frame,(216,384))))
        story.append({'scene':k+1,'subject_candidate':label,'start_s':round(cursor,3),'duration_s':round(count/FPS,3),'semantic_qa':'PENDING'})
        cursor+=count/FPS
    proc.stdin.close();err=proc.stderr.read()
    if proc.wait()!=0:raise RuntimeError(err.decode(errors='replace')[-1200:])
except Exception:
    proc.kill()
    raise

sheet=np.full((3*410,4*228,3),18,np.uint8)
for k,(seconds,f) in enumerate(contact):
    x=k%4*228+6;y=k//4*410+6
    sheet[y:y+384,x:x+216]=f
    cv2.putText(sheet,f'{seconds:.1f}s',(x+8,y+401),cv2.FONT_HERSHEY_SIMPLEX,.45,(220,215,198),1,cv2.LINE_AA)
cv2.imwrite(str(OUT/'CONTACT_SHEET.jpg'),sheet)
mobile=OUT/'VIDEO_ANDROID_720_REVIEW.mp4'
run(['ffmpeg','-y','-v','error','-i',mp4,'-vf','scale=720:1280:flags=lanczos','-map','0:v:0','-map','0:a:0','-c:v','libx264','-preset','veryfast','-crf','23','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',mobile])
for f in (mp4,mobile):run(['ffmpeg','-v','error','-xerror','-i',f,'-map','0','-f','null','-'])
probe=json.loads(run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',mp4]))
v=[x for x in probe['streams'] if x.get('codec_type')=='video']
a=[x for x in probe['streams'] if x.get('codec_type')=='audio']
assert len(v)==1 and len(a)==1 and v[0]['codec_name']=='h264' and a[0]['codec_name']=='aac'
assert int(v[0]['nb_frames'])==N

rights={'title':'Dulle Griet / Mad Meg','artist':'Pieter Bruegel the Elder','year':1563,
 'museum':'Museum Mayer van den Bergh, Antwerp','inventory':'MMB.0045','painting_cm':[117.4,162.2],
 'object_page':'https://search.museummayervandenbergh.be/details/collect/33',
 'restoration_research':'https://museummayervandenbergh.be/en/page/restoration-dulle-griet-reveals-unseen-wealth-colour-and-fresh-discoveries',
 'original_file_page':PAGE if selected_source.startswith('RESTORED') else PAGE_2016,
 'url_used':actual_url,'source_variant':selected_source,'source_sha1':SOURCE_SHA1,
 'source_sha256':sha(original),'source_bytes':SOURCE_SIZE,'source_pixels':SOURCE_PIXELS,
 'commons_license':'Wikimedia Commons PD-Art/PDM faithful 2D reproduction, with original modern restoration photo credited to Michel Wuyts when restored source; photo archived 2016 credit Museum Mayer van den Bergh/Jan Arkesteijn. Territorial reuse still pending.',
 'license_url':'https://creativecommons.org/publicdomain/mark/1.0/',
 'credit':('Pieter Bruegel the Elder, Dulle Griet (1563), Museum Mayer van den Bergh MMB.0045; photographic reproduction Michel Wuyts (2021), Wikimedia Commons PDM, moving editorial detail crops.' if selected_source.startswith('RESTORED') else 'Pieter Bruegel the Elder, Dulle Griet (1563), Museum Mayer van den Bergh; archival pre-restoration photograph, Wikimedia Commons PDM, animated detail crops.'),
 'territorial_rights_review':'PENDING','commercial_distribution_authorized':False,
 'gallery_or_frame':'NONE: Cinema Standard only, not Museum','music':'original locally generated ambient cinematic soundtrack'}
(OUT/'SOURCES_RIGHTS.json').write_text(json.dumps(rights,indent=2,ensure_ascii=False)+'\n')
(OUT/'STORYBOARD.json').write_text(json.dumps({'duration_s':DURATION,'scene_count':len(story),'shots':story,'human_artistic_QA':'PENDING','no_generated_painting_details':True},indent=2)+'\n')
posts={'facebook':'A woman marches through a landscape crowded with monsters, fire and impossible machines. Pieter Bruegel the Elder painted Dulle Griet in 1563. Look at what she carries — and what follows her. Museum Mayer van den Bergh.',
 'instagram':'An armoured woman. A mouth of hell. Dozens of creatures in one painting. Dulle Griet (1563), Pieter Bruegel the Elder. #ArtHistory #Bruegel',
 'tiktok':'At first it looks like chaos. Then you notice the armoured woman walking through it. Dulle Griet, Pieter Bruegel, 1563. #ArtTok',
 'youtube':'Dulle Griet, Pieter Bruegel (1563): a cinematic journey through the authentic painting in the Museum Mayer van den Bergh. Original music, moving details, source credited.',
 'publication':'DRAFT_NOT_PUBLISHED'}
(OUT/'SOCIAL_DRAFTS.json').write_text(json.dumps(posts,ensure_ascii=False,indent=2)+'\n')
(OUT/'README_FIRST.md').write_text('ONE new Dulle Griet Cinema Standard review, two video bitrates of the SAME slot. No critic or Museum versions. Do not count as Gold. Exact original museum painting source in archival or post-restoration photographic variant; dimensions/JPEG verified, SHA1 and SHA256 recorded after download; no paid APIs, no publication. Full-speed artistic and territory/license checks pending.\n')
qa={'work_id':'bruegel_dulle_griet_1563_mmb_0045','variant':'cinema_standard','source_sha1':SOURCE_SHA1,'source_sha256':sha(original),
 'mp4_sha256':sha(mp4),'mp4_bytes':mp4.stat().st_size,'android_mp4_sha256':sha(mobile),'android_mp4_bytes':mobile.stat().st_size,
 'duration_seconds':DURATION,'fps':FPS,'frame_count':N,'resolution':[W,H],'scene_count':len(story),
 'all_streams_ffmpeg_full_decode':'PASS','artistic_qa':'PENDING','territorial_rights':'PENDING','gold':False,'published':False,'paid_api_calls':0,
 'main_ten_queue_new_slots':0,'second_30_queue_new_cinema_slot':1}
(OUT/'QA_TECHNICAL.json').write_text(json.dumps(qa,indent=2)+'\n')
zipf=OUT/'ANDROID_REVIEW_PACKAGE.zip'
with zipfile.ZipFile(zipf,'w',zipfile.ZIP_DEFLATED,compresslevel=2) as z:
    for f in [mobile,OUT/'COVER.jpg',OUT/'CONTACT_SHEET.jpg',OUT/'SOURCES_RIGHTS.json',OUT/'STORYBOARD.json',OUT/'SOCIAL_DRAFTS.json',OUT/'QA_TECHNICAL.json',OUT/'README_FIRST.md']:
        z.write(f,f.name)
with zipfile.ZipFile(zipf) as z:
    assert z.testzip() is None
    assert hashlib.sha256(z.read(mobile.name)).hexdigest()==qa['android_mp4_sha256']
print('NEW_DULLE_GRIET_PRIVATE_CINEMA',json.dumps({'mp4_sha256':sha(mp4),'android_sha256':sha(mobile),'zip_sha256':sha(zipf),'full_decode':'PASS','CRC':'PASS','gold':False},indent=2),flush=True)
