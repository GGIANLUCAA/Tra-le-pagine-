#!/usr/bin/env python3
"""George Bellows Cliff Dwellers 1913: authentic LACMA artwork and original gently rhythmic soundtrack.
No paid API, TTS, Vidu, fictional Museum, Gold or publication.
"""
import hashlib, json, math, subprocess, urllib.parse, urllib.request, wave, zipfile
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT=Path('output/artvision-owner-bellows-cliff-dwellers-cinema-v1')
OUT.mkdir(parents=True,exist_ok=True)
# Source LACMA 16.4, public domain Bellows 1913 faithful photo via Wikimedia.
SOURCE='George_Bellows_-_Cliff_Dwellers_(1913).jpg'
PAGE='https://commons.wikimedia.org/wiki/File:George_Bellows_-_Cliff_Dwellers_(1913).jpg'
SOURCE_SHA1='10c589ab9539c0db891c9e3546d524464ea9d5fe'
SOURCE_SIZE=8298747
SOURCE_PIXELS=(5588,5316)
md5=hashlib.md5(SOURCE.encode()).hexdigest()
path=md5[0]+'/'+md5[:2]+'/'+urllib.parse.quote(SOURCE,safe='._-()')
urls=['https://upload.wikimedia.org/wikipedia/commons/'+path,
      'https://commons.wikimedia.org/wiki/Special:Redirect/file/'+urllib.parse.quote(SOURCE,safe='._-()')]
original=OUT/'ORIGINAL_ARTWORK.jpg'
actual_url=None
for url in urls:
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'ArtVisionOwnerPrivateReview/1.0 (https://github.com/GGIANLUCAA/Tra-le-pagine-)'})
        with urllib.request.urlopen(req,timeout=105) as f:data=f.read(SOURCE_SIZE+1)
        if len(data)!=SOURCE_SIZE or hashlib.sha1(data).hexdigest()!=SOURCE_SHA1: raise ValueError('LACMA photo exact source bytes/SHA1 mismatch')
        original.write_bytes(data)
        with Image.open(original) as im:
            if im.format!='JPEG' or im.size!=SOURCE_PIXELS:raise ValueError('wrong image pixels')
            im.verify()
        actual_url=url
        break
    except Exception as e:print('SOURCE_ATTEMPT_FAILED',type(e).__name__,str(e)[:160],flush=True)
if not actual_url:raise RuntimeError('BELLOWS_LACMA_16_4_SOURCE_UNAVAILABLE')
print('BELLOWS_AUTHENTIC_LACMA_ORIGINAL_MATCH',SOURCE_SHA1,SOURCE_SIZE,SOURCE_PIXELS,flush=True)

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
shots=[
 ('OPEN: CHILDREN AND CROWD IN THE LIGHT',2.5,(.44,.75,.67),(.47,.72,.61)),
 ('ENTIRE STREET SCENE',4.2,None,None),
 ('STREETCAR AMID THE PASSERS-BY',4.5,(.54,.53,.71),(.58,.53,.65)),
 ('CHILDREN IN WHITE',4.5,(.52,.79,.60),(.49,.76,.55)),
 ('WOMAN WITH FAN AT RIGHT',4.1,(.84,.76,.66),(.81,.78,.60)),
 ('BALCONY AND FIGURES ABOVE',4.4,(.71,.29,.67),(.73,.31,.62)),
 ('NEIGHBOURS IN THE CROWDED STREET',4.2,(.28,.56,.72),(.31,.59,.66)),
 ('STREET DEEP BETWEEN BUILDINGS',4.0,(.47,.43,.76),(.49,.46,.70)),
 ('LAUNDRY AND UPPER WINDOWS',4.2,(.33,.26,.71),(.38,.27,.65)),
 ('PEOPLE PASS THE TROLLEY',4.1,(.59,.67,.68),(.58,.66,.62)),
 ('A PANORAMA OF CITY LIFE',4.5,(.49,.56,.88),(.54,.54,.82)),
 ('RETURN TO FULL BELLOWS PAINTING',6.1,None,None),
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
np.random.seed(1913)
for i,(f,ph) in enumerate(((73.416,.2),(110.0,.6),(146.832,1.2))):
    slow=.5+.5*np.sin(2*np.pi*(.026+.009*i)*t+ph)**2
    layer=(.007 if i else .011)*slow*(np.sin(2*np.pi*f*t+ph)+.2*np.sin(2*np.pi*2*f*t+.3*ph))
    audio[:,0]+=layer
    audio[:,1]+=np.roll(layer,round((i*4+2)*SR/1000))*.94
keys=[146.832,174.614,164.814,196.0,174.614,146.832,130.813,164.814,196.0,220.0,174.614,146.832,164.814,146.832]
starts=[1.1,4.3,7.8,11.5,14.6,18.7,22.0,25.5,28.9,32.6,36.1,39.4,43.2,46.7]
for idx,(start,f) in enumerate(zip(starts,keys)):
    a=round(start*SR);n=min(round(2.2*SR),n_audio-a)
    if n<=0:continue
    u=np.arange(n,dtype=np.float64)/SR
    amp=(.017+(.003 if idx%4==0 else 0))*np.exp(-2.1*u)*(1-np.exp(-40*u))
    pluck=amp*(np.sin(2*np.pi*f*u)+.35*np.sin(2*np.pi*2.01*f*u)+.13*np.sin(2*np.pi*3*f*u))
    audio[a:a+n,0]+=pluck*(.97 if idx%2==0 else .69)
    audio[a:a+n,1]+=pluck*(.69 if idx%2==0 else .97)
knots=np.random.standard_normal(round((DURATION+.2)*27)+2)
air=np.interp(t,np.arange(len(knots))/27,knots)*.25
audio[:,0]+=.0034*air;audio[:,1]+=.0031*np.roll(air,round(.01*SR))
audio*=np.clip(t/1.2,0,1)[:,None]*np.clip((DURATION-t)/3.2,0,1)[:,None]
audio=np.tanh(audio*1.32)*.82

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
draw.text((W/2,300),'CLIFF DWELLERS',font=title_font,fill=(236,231,216),anchor='mm')
draw.text((W/2,1660),'GEORGE BELLOWS  ·  1913',font=small_font,fill=(226,221,201),anchor='mm')
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
                cv2.putText(frame,'CLIFF DWELLERS',(52,162),cv2.FONT_HERSHEY_SIMPLEX,1.04,(235,230,210),2,cv2.LINE_AA)
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

rights={'title':'Cliff Dwellers','artist':'George Bellows','year':1913,
 'museum':'Los Angeles County Museum of Art','inventory':'16.4','painting_cm':[102.08,106.84],
 'object_page':'https://collections.lacma.org/object/11398','original_file_page':PAGE,'url_used':actual_url,
 'source_sha1':SOURCE_SHA1,'source_sha256':sha(original),'source_bytes':SOURCE_SIZE,'source_pixels':SOURCE_PIXELS,
 'commons_license':'Faithful PD-Art/PDM photograph of public-domain painting via Wikimedia Commons; LACMA site photography rights and Italian commercial reuse pending.',
 'license_url':'https://creativecommons.org/publicdomain/mark/1.0/',
 'credit':'George Bellows, Cliff Dwellers (1913), LACMA 16.4; public-domain 2D painting reproduction via Wikimedia Commons, altered moving camera crops.',
 'rights_review':'PENDING_TERRITORIAL_AND_MUSEUM','commercial_distribution_authorized':False,
 'gallery_or_frame':'NONE: Cinema Standard only, not Museum','music':'original local synthesized gentle rhythmic instrumental'};

(OUT/'SOURCES_RIGHTS.json').write_text(json.dumps(rights,indent=2,ensure_ascii=False)+'\n')
(OUT/'STORYBOARD.json').write_text(json.dumps({'duration_s':DURATION,'scene_count':len(story),'shots':story,'human_artistic_QA':'PENDING','no_generated_painting_details':True},indent=2)+'\n')
posts={'facebook':'George Bellows painted an entire New York street in 1913: children, a streetcar, neighbours and balconies filled with life. Cliff Dwellers, LACMA.',
 'instagram':'A neighbourhood alive in one painting: the tram, children and people watching from windows. Cliff Dwellers (1913), George Bellows. #ArtHistory',
 'tiktok':'The streets of New York, 1913 — everyone seems to be moving. Bellows captured it all in Cliff Dwellers.',
 'youtube':'Cliff Dwellers — George Bellows, 1913. An original painting, viewed through cinematic detail cameras with original instrumental music.',
 'publication':'DRAFT_NOT_PUBLISHED'}
(OUT/'SOCIAL_DRAFTS.json').write_text(json.dumps(posts,ensure_ascii=False,indent=2)+'\n')
(OUT/'README_FIRST.md').write_text('ONE NEW Cliff Dwellers Cinema Standard private review, two video bitrates of the SAME slot. No critic or Museum versions. Do not count as Gold. Exact LACMA 16.4 source photo from Wikimedia Commons: original size, pixels and SHA1 checked; SHA256 recorded. no paid APIs, no publication. Full-speed artistic and territory/license checks pending.\n')
qa={'work_id':'bellows_cliff_dwellers_1913_lacma_16_4','variant':'cinema_standard','source_sha1':SOURCE_SHA1,'source_sha256':sha(original),
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
print('NEW_BELLOWS_CLIFF_DWELLERS_PRIVATE_CINEMA',json.dumps({'mp4_sha256':sha(mp4),'android_sha256':sha(mobile),'zip_sha256':sha(zipf),'full_decode':'PASS','CRC':'PASS','gold':False},indent=2),flush=True)
