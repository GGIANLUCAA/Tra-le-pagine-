#!/usr/bin/env python3
"""Francisco Goya Witches' Flight 1798: new authentic Prado Cinema Standard private review with original locally composed atmospheric soundtrack.
No paid API, TTS, Vidu, fictional Museum, Gold or publication.
"""
import hashlib, json, math, subprocess, urllib.parse, urllib.request, wave, zipfile
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT=Path('output/artvision-owner-goya-witches-flight-cinema-v1')
OUT.mkdir(parents=True,exist_ok=True)
# Prado P07748, original 1798 canvas; faithful original Commons Prado reproduction.
SOURCE='Francisco_de_Goya_-_Vuelo_de_brujas_(1798).jpg'
PAGE='https://commons.wikimedia.org/wiki/File:Francisco_de_Goya_-_Vuelo_de_brujas_(1798).jpg'
SOURCE_SHA1='f2952f3d5cd6b6568c3106901713fa14fa7c9742'
SOURCE_SIZE=5822775
SOURCE_PIXELS=(2068,2952)
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
        if len(data)!=SOURCE_SIZE or hashlib.sha1(data).hexdigest()!=SOURCE_SHA1:
            raise ValueError('exact Prado Wikimedia photo bytes/SHA1 mismatch')
        original.write_bytes(data)
        with Image.open(original) as im:
            if im.format!='JPEG' or im.size!=SOURCE_PIXELS: raise ValueError('wrong original painting pixels')
            im.verify()
        actual_url=url
        break
    except Exception as e:
        print('SOURCE_ATTEMPT_FAILED',type(e).__name__,str(e)[:170],flush=True)
if not actual_url:raise RuntimeError('GOYA_PRADO_P07748_VERIFIED_SOURCE_UNAVAILABLE')
print('GOYA_AUTHENTIC_PRADO_ORIGINAL_MATCH',SOURCE_SHA1,SOURCE_SIZE,SOURCE_PIXELS,flush=True)

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
shots=[
 ('OPEN: THREE WITCHES CARRYING THE VICTIM',2.5,(.52,.32,.53),(.52,.35,.50)),
 ('WITCHES FLIGHT: WHOLE ORIGINAL CANVAS',4.7,None,None),
 ('THE THREE HOODED FACES',4.5,(.53,.24,.55),(.55,.27,.50)),
 ('THE VICTIM IN THEIR ARMS',4.6,(.50,.40,.54),(.50,.40,.49)),
 ('THE RED CAPE IN THE AIR',4.2,(.60,.46,.55),(.62,.45,.52)),
 ('THE MAN WHO HIDES HIS HEAD',4.4,(.39,.69,.60),(.38,.68,.55)),
 ('THE OTHER FIGURE CROUCHES BELOW',4.2,(.73,.69,.57),(.70,.68,.54)),
 ('THE DARK DONKEY AT THE BASE',4.2,(.75,.88,.62),(.72,.86,.56)),
 ('THE CLOUDS ABOVE THE LANDSCAPE',3.8,(.52,.55,.69),(.54,.54,.64)),
 ('FACES IN THE OCCULT SKY',4.4,(.53,.21,.63),(.52,.22,.57)),
 ('A MEASURED RETURN THROUGH THE GROUP',4.5,(.54,.42,.72),(.50,.45,.67)),
 ('LAST WIDE VIEW: GOYA 1798',6.4,None,None),
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
np.random.seed(1798)
def pad(freq, phase=0):
    return (np.sin(2*np.pi*freq*t+phase+0.16*np.sin(2*np.pi*.074*t))
        +.26*np.sin(2*np.pi*freq*2.01*t+phase*.7)
        +.09*np.sin(2*np.pi*freq*3.003*t+phase*.17))
chord=[(55.0,0.23), (65.406,1.25), (82.407,2.13)]
for i,(freq,phase) in enumerate(chord):
    flutter=0.64+0.36*np.sin(2*np.pi*(0.017+i*0.006)*t+phase)**2
    voice=(.012 if i>0 else .018)*flutter*pad(freq,phase)
    audio[:,0]+=voice
    audio[:,1]+=np.roll(voice,round((3+i*2)*SR/1000))*.94
# Gentle breath, not shrill wind: low-pass-smoothed deterministic noise.
noise=np.random.standard_normal(n_audio).astype(np.float64)
# Interpolate soft noise knots to avoid any scipy or network library dependency.
knots=np.random.standard_normal(round((DURATION+.1)*24)+2)
moving=np.interp(t,np.arange(len(knots))/24,knots)*.38
air=moving*(.011+.005*np.sin(2*np.pi*.029*t))
audio[:,0]+=air
audio[:,1]+=np.roll(air,round(.012*SR))*.85
# Transitions placed at narrative beats; less repetition, no artificial crashes.
for start in [2.0,21.8,40.7]:
    pos=round(start*SR)
    samples=min(round(2.5*SR),n_audio-pos)
    z=np.arange(samples)/SR
    accent=.023*np.exp(-2.0*z)*np.sin(2*np.pi*(46-9*z)*z)
    audio[pos:pos+samples,0]+=accent
    audio[pos:pos+samples,1]+=accent*.91
# A slight harmonic opening in final six seconds.
finish=np.clip((t-(DURATION-7.5))/2.5,0,1)
audio[:,0]+=.008*finish*np.sin(2*np.pi*98.0*t)
audio[:,1]+=.007*finish*np.sin(2*np.pi*98.1*t)
audio*=np.clip(t/1.6,0,1)[:,None]*np.clip((DURATION-t)/3.3,0,1)[:,None]
audio=np.tanh(audio*1.25)*.79

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
draw.text((W/2,300),"THE WITCHES' FLIGHT",font=title_font,fill=(236,231,216),anchor='mm')
draw.text((W/2,1660),'FRANCISCO GOYA  ·  1798',font=small_font,fill=(226,221,201),anchor='mm')
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
                cv2.putText(frame,"THE WITCHES' FLIGHT",(52,162),cv2.FONT_HERSHEY_SIMPLEX,1.04,(235,230,210),2,cv2.LINE_AA)
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

rights={'title':"The Witches' Flight",'artist':'Francisco Goya','year':1798,
 'museum':'Museo Nacional del Prado, Madrid','inventory':'P07748',
 'painting_cm':[43.5,30.5],
 'object_page':'https://www.museodelprado.es/en/the-collection/art-work/witches-flight/5e44d19d-7cda-472b-b6d8-8868c599d252',
 'original_file_page':PAGE,'url_used':actual_url,'source_sha1':SOURCE_SHA1,
 'source_sha256':sha(original),'source_bytes':SOURCE_SIZE,'source_pixels':SOURCE_PIXELS,
 'commons_license':'Public-domain painting and faithful PD-Art photo via Wikimedia Commons; territorial museum reuse and commercial clearance must be reviewed separately.',
 'license_url':'https://creativecommons.org/publicdomain/mark/1.0/',
 'credit':'Francisco Goya, Witches Flight (1798), Museo del Prado P07748. Original image: Museo Nacional del Prado via Wikimedia Commons, faithful PD-Art reproduction; cinematic moving detail crops.',
 'rights_review':'PENDING_TERRITORIAL_AND_MUSEUM', 'commercial_distribution_authorized':False,
 'gallery_or_frame':'NONE: Cinema Standard only, not Museum',
 'music':'100% original local synthesized soundtrack, quiet nonrepeating accents and organic wind'};

(OUT/'SOURCES_RIGHTS.json').write_text(json.dumps(rights,indent=2,ensure_ascii=False)+'\n')
(OUT/'STORYBOARD.json').write_text(json.dumps({'duration_s':DURATION,'scene_count':len(story),'shots':story,'human_artistic_QA':'PENDING','no_generated_painting_details':True},indent=2)+'\n')
posts={'facebook':'Three witches carry a human figure through the dark. Below them, two people try to shield themselves. Francisco Goya painted Witches\' Flight in 1798; the original belongs to the Museo del Prado.',
 'instagram':'Look up at the figures in the sky — then look at the people below. The Witches\' Flight, Goya (1798), Museo del Prado. #ArtHistory #Goya',
 'tiktok':'Three figures above. Two frightened people below. Goya made this little canvas feel enormous. Witches\' Flight, 1798.',
 'youtube':'The Witches\' Flight by Francisco Goya (1798), Prado P07748. Original painting with cinematic camera details and a new original instrumental score.',
 'publication':'DRAFT_NOT_PUBLISHED'}
(OUT/'SOCIAL_DRAFTS.json').write_text(json.dumps(posts,ensure_ascii=False,indent=2)+'\n')
(OUT/'README_FIRST.md').write_text('ONE NEW Witches Flight Cinema Standard private review, two video bitrates of the SAME slot. No critic or Museum versions. Do not count as Gold. Exact Prado P07748 source photo from Wikimedia Commons: original size, pixel dimensions and fixed SHA1 checked; SHA256 recorded. no paid APIs, no publication. Full-speed artistic and territory/license checks pending.\n')
qa={'work_id':'goya_witches_flight_1798_prado_p07748','variant':'cinema_standard','source_sha1':SOURCE_SHA1,'source_sha256':sha(original),
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
print('NEW_GOYA_WITCHES_PRIVATE_CINEMA',json.dumps({'mp4_sha256':sha(mp4),'android_sha256':sha(mobile),'zip_sha256':sha(zipf),'full_decode':'PASS','CRC':'PASS','gold':False},indent=2),flush=True)
