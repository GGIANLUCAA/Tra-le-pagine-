#!/usr/bin/env python3
"""Evelyn De Morgan The Dryad (1884–85): authentic De Morgan painting, human-style quiet Cinema Standard, original gentle atmospheric soundtrack.
No paid API, TTS, Vidu, fictional Museum, Gold or publication.
"""
import hashlib, json, math, subprocess, urllib.parse, urllib.request, wave, zipfile
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT=Path('output/artvision-owner-demorgan-dryad-cinema-v1')
OUT.mkdir(parents=True,exist_ok=True)
# De Morgan Collection original; Wikimedia commons faithful PD-Art image.
# Full original: Dryad11.jpg, 8726x21359, 82826574 bytes, sha1 a46fbc28e7b9ab21bc384b7b4f684cc3a0a3871a.
# Use a Commons-generated faithful downsample so the GitHub runner/phone need not load 82.8 MB.
SOURCE='Dryad11.jpg'
PAGE='https://commons.wikimedia.org/wiki/File:Dryad11.jpg'
FULL_ORIGINAL_SOURCE_SHA1='a46fbc28e7b9ab21bc384b7b4f684cc3a0a3871a'
FULL_ORIGINAL_SOURCE_PIXELS=(8726,21359)
FULL_ORIGINAL_SOURCE_BYTES=82826574
key=SOURCE
md5=hashlib.md5(key.encode()).hexdigest()
base='https://upload.wikimedia.org/wikipedia/commons/thumb/'+md5[0]+'/'+md5[:2]+'/'+urllib.parse.quote(key,safe='._-')
urls=[
 ('FAITHFUL_COMMONS_2560PX_WIDE',base+'/2560px-'+key,2560),
 ('FAITHFUL_COMMONS_1920PX_WIDE',base+'/1920px-'+key,1920),
 ('FAITHFUL_COMMONS_1600PX_WIDE',base+'/1600px-'+key,1600),
]
original=OUT/'ORIGINAL_ARTWORK.jpg'
actual_url=None
selected_variant=None
for tag,url,width in urls:
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'ArtVisionOwnerPrivateReview/1.0 (https://github.com/GGIANLUCAA/Tra-le-pagine-)'})
        with urllib.request.urlopen(req,timeout=105) as f:data=f.read(22_000_001)
        if not (250_000<len(data)<=22_000_000):raise ValueError('bad derived JPEG byte count')
        original.write_bytes(data)
        with Image.open(original) as im:
            if im.format!='JPEG' or im.size[0]!=width or abs(im.size[1]/width-21359/8726)>.002:
                raise ValueError('bad file dimensions/aspect: expected original tall painting')
            im.verify()
        actual_url=url;selected_variant=tag
        SOURCE_SIZE=len(data)
        SOURCE_PIXELS=(width,round(width*21359/8726))
        SOURCE_SHA1=hashlib.sha1(data).hexdigest()
        break
    except Exception as e:print('SOURCE_ATTEMPT_FAILED',tag,type(e).__name__,str(e)[:165],flush=True)
if not actual_url:raise RuntimeError('DE_MORGAN_DRYAD_AUTHENTIC_COMMONS_DERIVATIVE_UNAVAILABLE')
print('DRYAD_AUTHENTIC_SOURCE_DERIVATIVE_VERIFIED',selected_variant,SOURCE_SHA1,SOURCE_SIZE,SOURCE_PIXELS,flush=True)

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
# A tall oil-on-panel work: guide the eye up/down the tree. No fictional figures.
# Avoid intrusive closeups on exposed torso; focus on face, textile, bark and flowers.
shots=[
 ('OPEN: THE DRYAD LOOKING OUT',2.6,(.50,.31,.44),(.49,.31,.42)),
 ('THE COMPLETE PAINTED TREE',4.4,None,None),
 ('HER AUBURN CURLS',4.0,(.47,.29,.41),(.45,.31,.39)),
 ('THE ANCIENT TRUNK ENVELOPS HER',4.2,(.59,.38,.59),(.57,.42,.56)),
 ('HER CROSSED ARMS AND THE BARK',4.3,(.48,.40,.51),(.50,.43,.48)),
 ('FABRIC FALLS BETWEEN TREE ROOTS',4.2,(.50,.65,.48),(.51,.68,.45)),
 ('FOOT PARTLY WITHIN THE TREE',4.1,(.47,.88,.47),(.47,.85,.45)),
 ('PURPLE IRISES AT THE BASE',4.5,(.80,.90,.43),(.77,.88,.42)),
 ('THE TWISTING WOOD',4.3,(.81,.44,.53),(.78,.46,.49)),
 ('TREE TOP AND BRANCHES',4.1,(.48,.12,.55),(.52,.15,.50)),
 ('SEA AND LIGHT BEYOND THE BARK',4.3,(.25,.68,.58),(.32,.66,.54)),
 ('RETURN TO THE WHOLE WORK',6.0,None,None),
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
# Original soft and organic local score. Slow chord bed plus irregular small bells,
# very light natural breath; no artificial repeated 7s percussion or strong beats.
np.random.seed(1885)
for i,(f,phase) in enumerate(((65.406,.17),(82.407,.83),(98.0,1.39))):
    drift=.65+.35*np.sin(2*np.pi*(.022+.007*i)*t+phase)**2
    pad=(.007 if i else .012)*drift*(np.sin(2*np.pi*f*t+phase+.09*np.sin(2*np.pi*.047*t))
         +.23*np.sin(2*np.pi*2.004*f*t+.7*phase))
    audio[:,0]+=pad
    audio[:,1]+=np.roll(pad,round((i*4+3)*SR/1000))*.91
# Bell tones intentionally sparse. Not mechanically triggered on each scene.
notes=[196.,174.614,220.,196.,164.814,174.614,220.,261.626,196.,174.614,146.832]
starts=[1.6,6.3,10.5,15.2,19.8,24.7,28.4,32.9,37.8,42.2,46.0]
for idx,(start,f) in enumerate(zip(starts,notes)):
    pos=round(start*SR);count=min(round(2.7*SR),n_audio-pos)
    if count<=0:continue
    u=np.arange(count,dtype=np.float64)/SR
    env=(1-np.exp(-38*u))*np.exp(-1.68*u)
    bell=.010*env*(np.sin(2*np.pi*f*u)+.19*np.sin(2*np.pi*2.003*f*u))
    audio[pos:pos+count,0]+=bell*(.93 if idx%2 else .67)
    audio[pos:pos+count,1]+=bell*(.67 if idx%2 else .93)
knots=np.random.standard_normal(round((DURATION+.2)*17)+2)
air=np.interp(t,np.arange(len(knots))/17,knots)*.3
audio[:,0]+=.0028*air;audio[:,1]+=.0025*np.roll(air,round(.012*SR))
audio*=np.clip(t/1.6,0,1)[:,None]*np.clip((DURATION-t)/4.3,0,1)[:,None]
audio=np.tanh(audio*1.32)*.80

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
draw.text((W/2,300),'THE DRYAD',font=title_font,fill=(236,231,216),anchor='mm')
draw.text((W/2,1660),'EVELYN DE MORGAN  ·  1885',font=small_font,fill=(226,221,201),anchor='mm')
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
                cv2.putText(frame,'THE DRYAD',(52,162),cv2.FONT_HERSHEY_SIMPLEX,1.04,(235,230,210),2,cv2.LINE_AA)
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

rights={'title':'The Dryad','artist':'Evelyn De Morgan','year':'1884–1885',
 'museum':'De Morgan Collection','inventory':'not specified',
 'painting_cm':[107.8,43.8],
 'object_page':'https://artsandculture.google.com/asset/the-dryad-0097/2wFzlXCcDrzUpA',
 'original_file_page':PAGE,'url_used':actual_url,
 'original_full_sha1_from_wikimedia_metadata':FULL_ORIGINAL_SOURCE_SHA1,
 'original_full_pixels_from_wikimedia_metadata':FULL_ORIGINAL_SOURCE_PIXELS,
 'source_variant':selected_variant,
 'source_sha1':SOURCE_SHA1,'source_sha256':sha(original),
 'source_bytes':SOURCE_SIZE,'source_pixels':SOURCE_PIXELS,
 'commons_license':'Public Domain Mark 1.0: faithful reproduction of public-domain 2D original via Wikimedia Commons; territory/photographic reuse terms still require final review',
 'license_url':'https://creativecommons.org/publicdomain/mark/1.0/',
 'credit':'Evelyn De Morgan, The Dryad (1884–85), De Morgan Collection. Original faithful digital reproduction: Wikimedia Commons Dryad11.jpg (PDM/PD-Art); used Commons-generated resized derivative. Cinematic moving crops.',
 'rights_review':'PENDING_TERRITORIAL_AND_MUSEUM',
 'commercial_distribution_authorized':False,
 'gallery_or_frame':'NONE: Cinema Standard only, not Museum',
 'music':'100% original local ambient score, gentle bells and irregular soft harmonic movement'};

(OUT/'SOURCES_RIGHTS.json').write_text(json.dumps(rights,indent=2,ensure_ascii=False)+'\n')
(OUT/'STORYBOARD.json').write_text(json.dumps({'duration_s':DURATION,'scene_count':len(story),'shots':story,'human_artistic_QA':'PENDING','no_generated_painting_details':True},indent=2)+'\n')
posts={'facebook':'At first glance she seems to be standing beside an old tree. Look at her foot: Evelyn De Morgan painted the dryad emerging from the trunk itself. The Dryad, 1884–85, De Morgan Collection.',
 'instagram':'A tree nymph who cannot leave her tree. Look at the foot, the roots and purple irises. Evelyn De Morgan, The Dryad (1884–85). #ArtHistory #EvelynDeMorgan',
 'tiktok':'Look where her foot meets the trunk: this isn’t just a woman near a tree. Evelyn De Morgan, The Dryad, 1884–85.',
 'youtube':'The Dryad (1884–85), Evelyn De Morgan. A cinematic look at an original panel painting, with faithful public-domain image and original instrumental soundtrack.',
 'publication':'DRAFT_NOT_PUBLISHED'}
(OUT/'SOCIAL_DRAFTS.json').write_text(json.dumps(posts,ensure_ascii=False,indent=2)+'\n')
(OUT/'README_FIRST.md').write_text('ONE NEW The Dryad Cinema Standard private review, two video bitrates of the SAME slot. No critic or Museum versions. Do not count as Gold. Wikimedia Commons faithful Dryad11.jpg downsample, full original dimensions and SHA1 documented, derivative exact proportions and SHA recorded. no paid APIs, no publication. Full-speed artistic and territory/license checks pending.\n')
qa={'work_id':'demorgan_dryad_1885_demorgan_collection','variant':'cinema_standard','source_sha1':SOURCE_SHA1,'source_sha256':sha(original),
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
print('NEW_DEMORGAN_DRYAD_PRIVATE_CINEMA',json.dumps({'mp4_sha256':sha(mp4),'android_sha256':sha(mobile),'zip_sha256':sha(zipf),'full_decode':'PASS','CRC':'PASS','gold':False},indent=2),flush=True)
