#!/usr/bin/env python3
"""Peter Paul Rubens The Battle of the Amazons circa 1618: original Alte Pinakothek painting, authentic cinematic action detail and locally generated instrumental.
No paid API, TTS, Vidu, fictional Museum, Gold or publication.
"""
import hashlib, json, math, subprocess, urllib.parse, urllib.request, wave, zipfile
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT=Path('output/artvision-owner-rubens-amazons-cinema-v1')
OUT.mkdir(parents=True,exist_ok=True)
# Alte Pinakothek 324: canonical painting by Rubens ca.1618, not the earlier Rubens-Brueghel version or studio copies.
SOURCE='Peter_Paul_Rubens_-_The_Battle_of_the_Amazons.JPG'
PAGE='https://commons.wikimedia.org/wiki/File:Peter_Paul_Rubens_-_The_Battle_of_the_Amazons.JPG'
SOURCE_PIXELS=(3000,2195)
EXPECTED_BYTES_MIN=550000
EXPECTED_BYTES_MAX=2000000
md5=hashlib.md5(SOURCE.encode()).hexdigest()
uri=md5[0]+'/'+md5[:2]+'/'+urllib.parse.quote(SOURCE,safe='._-')
urls=['https://upload.wikimedia.org/wikipedia/commons/'+uri,
      'https://commons.wikimedia.org/wiki/Special:Redirect/file/'+urllib.parse.quote(SOURCE,safe='._-')]
original=OUT/'ORIGINAL_ARTWORK.jpg'
actual_url=None
for url in urls:
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'ArtVisionOwnerPrivateReview/1.0 (https://github.com/GGIANLUCAA/Tra-le-pagine-)'})
        with urllib.request.urlopen(req,timeout=100) as f:data=f.read(EXPECTED_BYTES_MAX+1)
        if not EXPECTED_BYTES_MIN<=len(data)<=EXPECTED_BYTES_MAX:raise ValueError('unexpected original source bytes')
        original.write_bytes(data)
        with Image.open(original) as im:
            if im.format!='JPEG' or im.size!=SOURCE_PIXELS:raise ValueError('expected original Alte Pinakothek painting at 3000x2195')
            im.verify()
        actual_url=url
        SOURCE_SIZE=len(data)
        SOURCE_SHA1=hashlib.sha1(data).hexdigest()
        break
    except Exception as e:print('SOURCE_ATTEMPT_FAILED',type(e).__name__,str(e)[:180],flush=True)
if not actual_url:raise RuntimeError('RUBENS_AMAZONS_ALTE_PINAKOTHEK_ORIGINAL_SOURCE_UNAVAILABLE')
print('RUBENS_AMAZONS_SOURCE_ID_AND_PIXELS_VERIFIED',SOURCE_SHA1,SOURCE_SIZE,SOURCE_PIXELS,flush=True)

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
# Rubens depicts two planes: horsemen over the bridge, vanquished Amazon warriors below.
# Cinematic camera chosen from real spatial detail, not fabricated action.
shots=[
 ('OPEN: THE HORSE REARING ABOVE THE BRIDGE',2.7,(.83,.32,.58),(.79,.34,.55)),
 ('FULL PAINTING: THE TWO LEVELS OF BATTLE',4.3,None,None),
 ('GREEK RIDERS SWEEP FROM THE LEFT',4.2,(.22,.30,.59),(.27,.31,.53)),
 ('HORSES COLLIDE AT THE BRIDGE CREST',4.1,(.51,.29,.58),(.53,.31,.54)),
 ('THE BRIDGE UNDER THE WEIGHT OF BATTLE',4.2,(.36,.50,.61),(.40,.52,.57)),
 ('AMAZON RIDERS FALL ON THE RIGHT',4.2,(.85,.58,.62),(.80,.59,.56)),
 ('A WHITE HORSE PLUNGES BELOW',4.2,(.51,.77,.59),(.55,.75,.55)),
 ('WATER AND HORSES IN THE LOWER RIGHT',4.0,(.73,.82,.57),(.70,.78,.53)),
 ('THE FIGHT STILL RAGES ON TOP',4.1,(.57,.24,.63),(.56,.28,.59)),
 ('THE FAR LEFT ARCH AND FIGHTERS',4.1,(.15,.58,.62),(.20,.58,.57)),
 ('RETURN THROUGH THE SWIRLING HORSES',4.7,(.51,.53,.84),(.55,.53,.76)),
 ('FULL PAINTING HOLDS ITS FINAL MOMENT',6.0,None,None),
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
# Original subtle dramatic instrumental: irregular harmonic swells,
# no repeated 7-second beat, with quieter softer impacts matched to composition.
np.random.seed(1618)
for i,(f,phase) in enumerate(((55.,.25),(65.406,1.19),(82.407,2.21))):
    swell=.5+.5*np.sin(2*np.pi*(.018+.004*i)*t+phase)**2
    voice=(.012 if not i else .008)*swell*(np.sin(2*np.pi*f*t+phase+.08*np.sin(2*np.pi*.043*t))
          +.21*np.sin(2*np.pi*2.002*f*t+phase*.7))
    audio[:,0]+=voice; audio[:,1]+=np.roll(voice,round((i*4+2)*SR/1000))*.93
# Hand-placed accents, not every scene.
for idx,start in enumerate([2.2,11.8,25.5,39.5]):
    p=round(start*SR);n=min(round(2.2*SR),n_audio-p)
    u=np.arange(n,dtype=np.float64)/SR
    beat=(.018 if idx<2 else .023)*np.exp(-2.45*u)*np.sin(2*np.pi*(54-8*u)*u)
    audio[p:p+n,0]+=beat;audio[p:p+n,1]+=beat*.94
# Soft chimes towards the end only.
for idx,(start,f) in enumerate([(34.1,146.832),(42.2,130.813),(46.5,164.814)]):
    p=round(start*SR);n=min(round(2*SR),n_audio-p);u=np.arange(n)/SR
    pluck=.008*np.exp(-2.2*u)*(np.sin(2*np.pi*f*u)+.18*np.sin(2*np.pi*2*f*u))
    audio[p:p+n,idx%2]+=pluck
knots=np.random.standard_normal(round((DURATION+.2)*24)+2)
air=np.interp(t,np.arange(len(knots))/24,knots)*.3
audio[:,0]+=.0025*air;audio[:,1]+=.0022*np.roll(air,round(.012*SR))
audio*=np.clip(t/1.3,0,1)[:,None]*np.clip((DURATION-t)/4.1,0,1)[:,None]
audio=np.tanh(audio*1.34)*.80

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
draw.text((W/2,300),'BATTLE OF THE AMAZONS',font=title_font,fill=(236,231,216),anchor='mm')
draw.text((W/2,1660),'PETER PAUL RUBENS  ·  1618',font=small_font,fill=(226,221,201),anchor='mm')
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
                cv2.putText(frame,'BATTLE OF THE AMAZONS',(52,162),cv2.FONT_HERSHEY_SIMPLEX,1.04,(235,230,210),2,cv2.LINE_AA)
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

rights={'title':'The Battle of the Amazons','artist':'Peter Paul Rubens','year':'c. 1618',
 'museum':'Alte Pinakothek, Munich','inventory':'324','painting_cm':[120.3,165.3],
 'object_page':'https://www.sammlung.pinakothek.de/en/artwork/2mxqZgML8b/peter-paul-rubens/die-amazonenschlacht',
 'original_file_page':PAGE,'url_used':actual_url,'source_sha1':SOURCE_SHA1,'source_sha256':sha(original),
 'source_bytes':SOURCE_SIZE,'source_pixels':SOURCE_PIXELS,
 'commons_license':'Faithful PD-Art PDM reproduction of public-domain oil on panel via Wikimedia Commons; territory-specific commercial re-use pending.',
 'license_url':'https://creativecommons.org/publicdomain/mark/1.0/',
 'credit':'Peter Paul Rubens, The Battle of the Amazons (c.1618), Bayerische Staatsgemäldesammlungen – Alte Pinakothek, inv.324; image via Wikimedia Commons PD-Art. Altered as moving detail crops.',
 'rights_review':'PENDING_TERRITORIAL_AND_MUSEUM','commercial_distribution_authorized':False,
 'gallery_or_frame':'NONE: Cinema Standard only, not Museum',
 'music':'100% original local instrumental soundtrack, restrained irregular swells and soft accent cues'};

(OUT/'SOURCES_RIGHTS.json').write_text(json.dumps(rights,indent=2,ensure_ascii=False)+'\n')
(OUT/'STORYBOARD.json').write_text(json.dumps({'duration_s':DURATION,'scene_count':len(story),'shots':story,'human_artistic_QA':'PENDING','no_generated_painting_details':True},indent=2)+'\n')
posts={'facebook':'Rubens turned a bridge into a two-level battle. Above, mounted warriors clash; below, horses and people tumble into the river. The Battle of the Amazons (c.1618), Alte Pinakothek.',
 'instagram':'Look at the bridge: a whole battle surges across it, while another unfolds below. Rubens, The Battle of the Amazons, c.1618. #ArtHistory',
 'tiktok':'Two battles in one painting: on the bridge and under it. Look at the horse falling into the river. Rubens, 1618.',
 'youtube':'The Battle of the Amazons — Peter Paul Rubens (c.1618), Alte Pinakothek. An original painting explored through camera movement and music, with source credit.',
 'publication':'DRAFT_NOT_PUBLISHED'}
(OUT/'SOCIAL_DRAFTS.json').write_text(json.dumps(posts,ensure_ascii=False,indent=2)+'\n')
(OUT/'README_FIRST.md').write_text('ONE NEW Rubens Battle of the Amazons Cinema Standard private review, two video bitrates of the SAME slot. No critic or Museum versions. Do not count as Gold. Exact Alte Pinakothek original 1618 Rubens painting from Commons, exact image dimensions/size envelope checked, SHA1/SHA256 recorded. no paid APIs, no publication. Full-speed artistic and territory/license checks pending.\n')
qa={'work_id':'rubens_battle_amazons_1618_alte_pinakothek_324','variant':'cinema_standard','source_sha1':SOURCE_SHA1,'source_sha256':sha(original),
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
print('NEW_RUBENS_AMAZONS_PRIVATE_CINEMA',json.dumps({'mp4_sha256':sha(mp4),'android_sha256':sha(mobile),'zip_sha256':sha(zipf),'full_decode':'PASS','CRC':'PASS','gold':False},indent=2),flush=True)
