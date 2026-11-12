#!/usr/bin/env python3
"""Richard Dadd The Fairy Feller's Master-Stroke: a NEW Cinema Standard using a CC BY 3.0 credited true photograph of Tate Britain T00598.
No paid API, TTS, Vidu, fictional Museum, Gold or publication.
"""
import hashlib, json, math, subprocess, urllib.parse, urllib.request, wave, zipfile
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT=Path('output/artvision-owner-dadd-fairy-feller-cinema-v1')
OUT.mkdir(parents=True,exist_ok=True)
# Original Richard Dadd painting 1855–1864, Tate Britain T00598.
# Use Sailko's independent CC BY 3.0 photos of the EXACT canvas, not generated art.
SOURCE_PRIMARY='Richard_dadd,_il_colpo_da_maestro_del_cantastorie,_1855-64,_01.jpg'
SOURCE_SECONDARY='Richard_dadd,_il_colpo_da_maestro_del_cantastorie,_1855-64,_02.jpg'
PAGES=[
 'https://commons.wikimedia.org/wiki/File:Richard_dadd,_il_colpo_da_maestro_del_cantastorie,_1855-64,_01.jpg',
 'https://commons.wikimedia.org/wiki/File:Richard_dadd,_il_colpo_da_maestro_del_cantastorie,_1855-64,_02.jpg']
def direct_url(name):
    h=hashlib.md5(name.encode()).hexdigest()
    return 'https://upload.wikimedia.org/wikipedia/commons/'+h[0]+'/'+h[:2]+'/'+urllib.parse.quote(name,safe='._-')
sources=[
 ('SAILKO_2017_01_CC_BY_3_0',SOURCE_PRIMARY,(3024,3828),8608140,'0960e2d3a3d114c67c6455ce655f92f29f37413f',PAGES[0]),
 ('SAILKO_2017_02_CC_BY_3_0',SOURCE_SECONDARY,(3648,5472),12670838,'8d7007ae708fef9f0482f1971af40bf9e90e8309',PAGES[1])
]
original=OUT/'ORIGINAL_ARTWORK.jpg'
actual_url=None
for tag,name,pixels,size,expected_sha1,page in sources:
    try:
        url=direct_url(name)
        req=urllib.request.Request(url,headers={'User-Agent':'ArtVisionOwnerPrivateReview/1.0 (https://github.com/GGIANLUCAA/Tra-le-pagine-)'})
        with urllib.request.urlopen(req,timeout=105) as f:data=f.read(size+1)
        if len(data)!=size or hashlib.sha1(data).hexdigest()!=expected_sha1:raise ValueError('source physical byte envelope/SHA1 mismatch')
        original.write_bytes(data)
        with Image.open(original) as im:
            if im.format!='JPEG' or im.size!=pixels:raise ValueError('wrong JPEG image dimensions')
            im.verify()
        actual_url=url;selected_source=tag;PAGE=page
        SOURCE_PIXELS=pixels;SOURCE_SIZE=size;SOURCE_SHA1=expected_sha1
        break
    except Exception as e:
        print('SOURCE_ATTEMPT_FAILED',tag,type(e).__name__,str(e)[:180],flush=True)
if not actual_url:raise RuntimeError('FAIRY_FELLER_GENUINE_SAILKO_SOURCE_UNAVAILABLE_NO_VIDEO')
print('FAIRY_FELLER_CORRECT_ARTWORK_CC_BY_PHOTOGRAPH_VERIFIED',selected_source,SOURCE_SHA1,SOURCE_SIZE,SOURCE_PIXELS,flush=True)

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
shots=[
 ('OPEN: THE FAIRY FELLER AND HIS AXE',2.7,(.59,.77,.63),(.59,.74,.57)),
 ('REVEAL THE FANTASTICAL FOREST',3.3,None,None),
 ('THE FAIRY FELLER POISED TO STRIKE',4.2,(.59,.74,.54),(.59,.74,.49)),
 ('THE HAZELNUT AT HIS FEET',4.1,(.53,.87,.55),(.51,.85,.52)),
 ('THE TINY FAIRY COURT',4.4,(.43,.42,.67),(.45,.40,.59)),
 ('THE BIG HAT AND THE PATRIARCH',4.0,(.49,.37,.60),(.46,.39,.56)),
 ('DAISIES TOWER OVER FAIRIES',4.3,(.83,.31,.66),(.80,.35,.61)),
 ('FIGURES IN THE UPPER WOODLAND',4.3,(.46,.18,.70),(.51,.20,.63)),
 ('THE GATHERED WOMEN',4.2,(.27,.52,.65),(.31,.50,.60)),
 ('TINY ONLOOKERS BETWEEN THE FLOWERS',4.0,(.75,.61,.67),(.71,.65,.60)),
 ('RETURN TO THE AXE RAISED ABOVE THE NUT',4.2,(.58,.73,.66),(.56,.75,.60)),
 ('FINAL: THE WHOLE LITTLE WORLD',5.6,None,None),
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
tones=[65.406,73.416,82.407,98.0,73.416,82.407,65.406]
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
    for beat in (.8,4.7):
        p=round((start+beat)*SR)
        if p>=n_audio:continue
        n=min(round(1.2*SR),n_audio-p)
        z=np.arange(n)/SR
        drum=.013*np.exp(-5*z)*np.sin(2*np.pi*(76-14*z)*z)
        audio[p:p+n,:]+=drum[:,None]
audio[:,0]+=.006*np.sin(2*np.pi*42*t)
audio[:,1]+=.006*np.sin(2*np.pi*42.13*t+.18)
audio*=np.clip(t/1.7,0,1)[:,None]*np.clip((DURATION-t)/3.4,0,1)[:,None]
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
draw.text((W/2,275),'THE FAIRY FELLER',font=title_font,fill=(236,231,216),anchor='mm')
draw.text((W/2,348),'MASTER-STROKE',font=title_font,fill=(236,231,216),anchor='mm')
draw.text((W/2,1660),'RICHARD DADD  ·  1855–1864',font=small_font,fill=(226,221,201),anchor='mm')
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
                cv2.putText(frame,'THE FAIRY FELLER',(52,162),cv2.FONT_HERSHEY_SIMPLEX,1.04,(235,230,210),2,cv2.LINE_AA)
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

rights={'title':"The Fairy Feller's Master-Stroke",'artist':'Richard Dadd','year':'1855–1864',
 'museum':'Tate Britain, London','inventory':'T00598','painting_cm':[54.0,39.4],
 'object_page':'https://www.tate.org.uk/art/artworks/dadd-the-fairy-fellers-master-stroke-t00598',
 'original_file_page':PAGE,'url_used':actual_url,'source_variant':selected_source,
 'source_photo_author':'Sailko','source_photo_year':2017,'source_sha1':SOURCE_SHA1,
 'source_sha256':sha(original),'source_bytes':SOURCE_SIZE,'source_pixels':SOURCE_PIXELS,
 'commons_license':'Sailko own work CC BY 3.0 Unported; author + source + license + alterations attribution required; territorial museum rights review pending',
 'license_url':'https://creativecommons.org/licenses/by/3.0/',
 'credit':"Richard Dadd, The Fairy Feller's Master-Stroke (1855–64), Tate Britain T00598; photograph by Sailko (2017) via Wikimedia Commons, CC BY 3.0. Editorial moving crops, local score.",
 'historical_context':'Dadd imagines the instant a fairy feller raises his axe to split a chestnut before Queen Mab and gathered fairies.',
 'territorial_rights_review':'PENDING','commercial_distribution_authorized':False,
 'gallery_or_frame':'NONE: Cinema Standard only, not Museum','music':'Original locally generated restrained atmospheric soundtrack, no paid API'}
(OUT/'SOURCES_RIGHTS.json').write_text(json.dumps(rights,indent=2,ensure_ascii=False)+'\n')
(OUT/'STORYBOARD.json').write_text(json.dumps({'duration_s':DURATION,'scene_count':len(story),'shots':story,'human_artistic_QA':'PENDING','no_generated_painting_details':True},indent=2)+'\n')
posts={'facebook':"There is an entire fairy world waiting for one swing of an axe. Richard Dadd painted The Fairy Feller's Master-Stroke from 1855 to 1864. Tate Britain T00598, photographed by Sailko, CC BY 3.0.",
 'instagram':"Daisies become forests, chestnuts become monuments, and a tiny woodcutter is ready to strike. Richard Dadd, The Fairy Feller’s Master-Stroke. #ArtHistory",
 'tiktok':"Look closely: that tiny woodcutter is about to split a nut, with a whole fairy court watching. Richard Dadd, 1855–64.",
 'youtube':"The Fairy Feller's Master-Stroke (1855–64), Richard Dadd. A cinematic tour of the genuine Tate painting using credited Sailko CC BY 3.0 photograph.",
 'publication':'DRAFT_NOT_PUBLISHED'}
(OUT/'SOCIAL_DRAFTS.json').write_text(json.dumps(posts,ensure_ascii=False,indent=2)+'\n')
(OUT/'README_FIRST.md').write_text("ONE NEW Fairy Feller's Master-Stroke Cinema Standard private review, two video bitrates of the SAME slot. No critic or Museum versions. Do not count as Gold. Exact 2017 Sailko original Tate painting photographs CC BY 3.0; file SHA1/bytes/pixels hard-verified; source and alterations attributed. No paid APIs, no publication. Full-speed artistic and territory/license checks pending.\n")
qa={'work_id':'richard_dadd_fairy_fellers_master_stroke_tate_t00598','variant':'cinema_standard','source_sha1':SOURCE_SHA1,'source_sha256':sha(original),
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
print('NEW_DADD_FAIRY_FELLER_PRIVATE_CINEMA',json.dumps({'mp4_sha256':sha(mp4),'android_sha256':sha(mobile),'zip_sha256':sha(zipf),'full_decode':'PASS','CRC':'PASS','gold':False},indent=2),flush=True)
