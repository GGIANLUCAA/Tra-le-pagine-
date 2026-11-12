#!/usr/bin/env python3
"""Edward Burne-Jones The Baleful Head (1885–87): original Staatsgalerie Stuttgart oil painting, authentic private Cinema Standard with a restrained original music cue.
No paid API, TTS, Vidu, fictional Museum, Gold or publication.
"""
import hashlib, json, math, subprocess, urllib.parse, urllib.request, wave, zipfile
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT=Path('output/artvision-owner-baleful-head-cinema-v1')
OUT.mkdir(parents=True,exist_ok=True)
# Original completed oil painting in Stuttgart, not the different Southampton preparatory gouache.
SOURCE='The_Baleful_Head_-_Edward_Burne-Jones.jpg'
PAGE='https://commons.wikimedia.org/wiki/File:The_Baleful_Head_-_Edward_Burne-Jones.jpg'
SOURCE_PIXELS=(1410,1800)
SOURCE_MIN=450000
SOURCE_MAX=1400000
md5=hashlib.md5(SOURCE.encode()).hexdigest()
uri=md5[0]+'/'+md5[:2]+'/'+urllib.parse.quote(SOURCE,safe='._-')
urls=['https://upload.wikimedia.org/wikipedia/commons/'+uri,
      'https://commons.wikimedia.org/wiki/Special:Redirect/file/'+urllib.parse.quote(SOURCE,safe='._-')]
original=OUT/'ORIGINAL_ARTWORK.jpg'
actual_url=None
for url in urls:
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'ArtVisionOwnerPrivateReview/1.0 (https://github.com/GGIANLUCAA/Tra-le-pagine-)'})
        with urllib.request.urlopen(req,timeout=105) as f:data=f.read(SOURCE_MAX+1)
        if not SOURCE_MIN<=len(data)<=SOURCE_MAX:raise ValueError('unexpected exact Stuttgart photo bytes')
        original.write_bytes(data)
        with Image.open(original) as im:
            if im.format!='JPEG' or im.size!=SOURCE_PIXELS:raise ValueError('not the full Stuttgart 1410x1800 painting')
            im.verify()
        actual_url=url
        SOURCE_SIZE=len(data);SOURCE_SHA1=hashlib.sha1(data).hexdigest()
        break
    except Exception as e:print('SOURCE_ATTEMPT_FAILED',type(e).__name__,str(e)[:175],flush=True)
if not actual_url:raise RuntimeError('BALEFUL_HEAD_STUTTGART_ORIGINAL_SOURCE_UNAVAILABLE')
print('BALEFUL_HEAD_COMPLETED_STUTTGART_OIL_VERIFIED',SOURCE_SHA1,SOURCE_SIZE,SOURCE_PIXELS,flush=True)

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
# Focus descriptions are subject hypotheses pending contact/full-speed human review.
# The global wide beats keep the original horizontal 651 cm canvas visible.
# The physical painting is portrait; restrained, semantic moves without invented detail.
# Candidate semantic framing awaits full-speed human artistic check.
# Different camera language for a social-realist city scene, semantic review pending.
# Actual Stuttgart painting: Perseus and Andromeda, Medusa's image in the reflecting pool,
# apples, garden foliage, carved fountain. No invented subjects or strong perspective tilts.
shots=[
 ('OPEN: THE UNSETTLING REFLECTION',2.7,(.51,.56,.45),(.52,.57,.43)),
 ('REVEAL THE WHOLE PAINTING',4.2,None,None),
 ('PERSEUS IN DARK ARMOUR',4.3,(.27,.33,.57),(.30,.35,.53)),
 ('ANDROMEDA BENDS TO THE WATER',4.3,(.72,.33,.56),(.69,.36,.52)),
 ('THEIR JOINED HANDS',4.1,(.52,.43,.47),(.50,.44,.44)),
 ('MEDUSA REFLECTED SAFELY IN WATER',4.6,(.54,.58,.43),(.54,.57,.40)),
 ('THE OCTAGONAL STONE WELL',4.1,(.49,.67,.64),(.49,.68,.59)),
 ('RIPE APPLES AND GREEN LEAVES',4.2,(.37,.14,.57),(.42,.18,.53)),
 ('THE GARDEN GROWS AROUND THEM',4.0,(.82,.65,.55),(.77,.65,.53)),
 ('THEIR FACES IN PROFILE',4.2,(.53,.29,.53),(.54,.31,.50)),
 ('A QUIET RETURN TO THE WELL',4.4,(.53,.55,.70),(.50,.54,.64)),
 ('WHOLE PAINTING: HOLD THE FINAL MOMENT',6.0,None,None),
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
# Subtle original cue: a slower unresolved string-like pad, quiet breath/noise
# and three irregular low accents (not the old 7-second repeating beat).
# Original instrumental music: softly articulated plucked notes, not repeated 7-second drums.
# New original evocative score: spare resonant tones, gentle strings, no rhythmic template.
np.random.seed(1887)
for i,(f,phase) in enumerate(((65.406,.2),(98.,.8),(130.813,1.5))):
    swell=.60+.40*np.sin(2*np.pi*(.017+.006*i)*t+phase)**2
    layer=(.008 if i else .014)*swell*(np.sin(2*np.pi*f*t+phase)+.22*np.sin(2*np.pi*2.003*f*t+.55*phase))
    audio[:,0]+=layer;audio[:,1]+=np.roll(layer,round((i*3+4)*SR/1000))*.94
notes=[196.,174.614,164.814,196.,220.,174.614,196.,146.832,164.814,196.]
starts=[1.4,5.9,10.6,15.4,20.7,25.2,30.0,35.2,40.9,46.1]
for idx,(start,f) in enumerate(zip(starts,notes)):
    a=round(start*SR);n=min(round(3.2*SR),n_audio-a)
    if n<=0:continue
    u=np.arange(n)/SR
    pluck=.011*(1-np.exp(-30*u))*np.exp(-1.58*u)*(np.sin(2*np.pi*f*u)+.24*np.sin(2*np.pi*2.01*f*u))
    audio[a:a+n,0]+=pluck*(.90 if idx%2 else .72)
    audio[a:a+n,1]+=pluck*(.72 if idx%2 else .90)
knots=np.random.standard_normal(round((DURATION+.3)*23)+2)
wind=np.interp(t,np.arange(len(knots))/23,knots)*.24
audio[:,0]+=.0028*wind;audio[:,1]+=.0025*np.roll(wind,round(.008*SR))
audio*=np.clip(t/1.6,0,1)[:,None]*np.clip((DURATION-t)/3.8,0,1)[:,None]
audio=np.tanh(audio*1.31)*.80

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
draw.text((W/2,300),'THE BALEFUL HEAD',font=title_font,fill=(236,231,216),anchor='mm')
draw.text((W/2,1660),'EDWARD BURNE-JONES  ·  1887',font=small_font,fill=(226,221,201),anchor='mm')
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
                cv2.putText(frame,'THE BALEFUL HEAD',(52,162),cv2.FONT_HERSHEY_SIMPLEX,1.04,(235,230,210),2,cv2.LINE_AA)
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

rights={'title':'The Baleful Head','artist':'Edward Burne-Jones','year':'1885–1887',
 'museum':'Staatsgalerie Stuttgart','inventory':'3110','painting_cm':[150,130],
 'object_page':'https://mediaguide.staatsgalerie.de/en/sammlung/baleful-head/people_with_hearing_impairments/',
 'original_file_page':PAGE,'url_used':actual_url,'source_sha1':SOURCE_SHA1,
 'source_sha256':sha(original),'source_bytes':SOURCE_SIZE,'source_pixels':SOURCE_PIXELS,
 'commons_license':'Public Domain Mark 1.0 / faithful PD-Art original oil painting reproduction; commercial territory-specific usage still pending',
 'license_url':'https://creativecommons.org/publicdomain/mark/1.0/',
 'credit':'Edward Burne-Jones, The Baleful Head (1885–87), Staatsgalerie Stuttgart inv.3110, oil on canvas. Source via Wikimedia Commons PD-Art. Adapted moving crops. THIS IS THE COMPLETED STUTTGART OIL, NOT THE SOUTHAMPTON STUDY.',
 'rights_review':'PENDING_TERRITORIAL_AND_MUSEUM','commercial_distribution_authorized':False,
 'gallery_or_frame':'NONE: Cinema Standard only, not Museum','music':'locally composed original gentle chamber-style cue, no paid services'};

(OUT/'SOURCES_RIGHTS.json').write_text(json.dumps(rights,indent=2,ensure_ascii=False)+'\n')
(OUT/'STORYBOARD.json').write_text(json.dumps({'duration_s':DURATION,'scene_count':len(story),'shots':story,'human_artistic_QA':'PENDING','no_generated_painting_details':True},indent=2)+'\n')
posts={'facebook':'Perseus cannot show Andromeda the head of Medusa directly. In this garden he lets her see it reflected in a fountain. Edward Burne-Jones, The Baleful Head (1885–87), Staatsgalerie Stuttgart.',
 'instagram':'A reflection saves them from Medusa’s gaze. Look down into the water. The Baleful Head, Edward Burne-Jones. #ArtHistory',
 'tiktok':'Do you see the third face? Perseus and Andromeda are looking into a well — at Medusa, not at each other. The Baleful Head (1885–87).',
 'youtube':'The Baleful Head (1885–87), Edward Burne-Jones, Stuttgart. A cinematic look at the original painting, the reflection and the garden, with a new original score.',
 'publication':'DRAFT_NOT_PUBLISHED'}
(OUT/'SOCIAL_DRAFTS.json').write_text(json.dumps(posts,ensure_ascii=False,indent=2)+'\n')
(OUT/'README_FIRST.md').write_text('ONE NEW Baleful Head Cinema Standard private review, two video bitrates of the SAME slot. No critic or Museum versions. Do not count as Gold. Authentic oil painting (Stuttgart 3110, not Southampton preparatory study), fixed pixel identity and SHA1/SHA256 computed, with original composition. no paid APIs, no publication. Full-speed artistic and territory/license checks pending.\n')
qa={'work_id':'burne_jones_baleful_head_1887_stuttgart_3110','variant':'cinema_standard','source_sha1':SOURCE_SHA1,'source_sha256':sha(original),
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
print('NEW_BALEFUL_HEAD_PRIVATE_CINEMA',json.dumps({'mp4_sha256':sha(mp4),'android_sha256':sha(mobile),'zip_sha256':sha(zipf),'full_decode':'PASS','CRC':'PASS','gold':False},indent=2),flush=True)
