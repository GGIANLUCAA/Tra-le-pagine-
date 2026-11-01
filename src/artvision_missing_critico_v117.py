#!/usr/bin/env python3
"""ArtVision V117: 8 formerly blocked Critico videos (4 museum-documented paintings).
Four already-existing pairs of Cinema untouched. Per work: exactly one free-tier
Gacrux WAV and two different genuine MP4 with bit-identical Critico AAC.
No social auto-publish, no paid video AI, no new subjects or Cinema rerenders.
"""
import hashlib,json,os,sys,subprocess,urllib.request,urllib.parse,zipfile,math,wave
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageEnhance,ImageFilter
W,H,FPS=720,1280,20
ROOT=Path(__file__).resolve().parents[1]
SPEC_DIR=ROOT/'modules/artvision_critico/production_series/2026_11_01_missing_critico_v117'
AUTH={
 'fabritius_goldfinch_1654',
 'seurat_grande_jatte_1884',
 'turner_fighting_temeraire_1839',
 'homer_gulf_stream_met11122_1899'
}
WORK_ID=os.environ.get('ARTVISION_EXACT_WORK_ID','')
if WORK_ID not in AUTH:raise RuntimeError('V117 disallows new or already finished artwork')
CFG=json.loads((SPEC_DIR/(WORK_ID+'.json')).read_text(encoding='utf8'))
assert CFG['work_id']==WORK_ID and CFG['owner_authorized_now'] and len(CFG['story'])==9
FILE=CFG.get('commons_filename','')
name=FILE.replace(' ','_')
if name:
 md5=hashlib.md5(name.encode('utf8')).hexdigest()
 from urllib.parse import quote
 base='https://upload.wikimedia.org/wikipedia/commons/'
 if CFG.get('source_thumb_width'):
  SRC=base+'thumb/'+md5[0]+'/'+md5[:2]+'/'+quote(name)+'/'+str(CFG['source_thumb_width'])+'px-'+quote(name)
 else:
  SRC=base+md5[0]+'/'+md5[:2]+'/'+quote(name)
else:
 SRC='https://collectionapi.metmuseum.org/public/collection/v1/objects/'+str(CFG['met_object_id'])
EXPECTED_SHA1=CFG.get('source_sha1')
WORK_CODE={
 'fabritius_goldfinch_1654':'FABRITIUS_GOLDFINCH',
 'seurat_grande_jatte_1884':'SEURAT_GRANDE_JATTE',
 'turner_fighting_temeraire_1839':'TURNER_TEMERAIRE',
 'homer_gulf_stream_met11122_1899':'HOMER_GULF_STREAM'
}[WORK_ID]
OUT=Path(os.environ.get('ARTVISION_OUT','output/artvision_missing_critico_v117'))/WORK_ID
WORDS=[(r[0],r[1]) for r in CFG['story']]
FOCUS={k:tuple(v) for k,v in CFG['focus'].items()}
BEATS=[r[2] for r in CFG['story']]

def digest(path,kind='sha256'):
 h=hashlib.new(kind)
 with open(path,'rb') as f:
  for part in iter(lambda:f.read(1048576),b''):h.update(part)
 return h.hexdigest()

def run(args):
 p=subprocess.run([str(x) for x in args],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 if p.returncode: raise RuntimeError(str(args[0])+' failed: '+p.stderr[-1300:])
 return p.stdout

def ffmpeg():
 import shutil
 x=shutil.which('ffmpeg')
 if not x:raise RuntimeError('FFmpeg unavailable')
 return x

def get_art():
 OUT.mkdir(parents=True,exist_ok=True)
 target=OUT/'ARTWORK_ORIGINAL_PUBLIC_DOMAIN.jpg'
 if not target.exists():
  address=SRC
  if CFG.get('met_object_id'):
   req=urllib.request.Request(SRC,headers={'User-Agent':'ArtVision-V117-Met-OpenAccess/1.0'})
   with urllib.request.urlopen(req,timeout=80) as resp:meta=json.load(resp)
   if int(meta.get('objectID',-1))!=int(CFG['met_object_id']) or meta.get('isPublicDomain') is not True:
    raise RuntimeError('STOP Met Open Access identity/PD mismatch')
   address=meta.get('primaryImage')
   if not isinstance(address,str) or not address.startswith('https://'):
    raise RuntimeError('STOP Met no approved original image')
   (OUT/'MET_OPEN_ACCESS_OBJECT.json').write_text(json.dumps({
    'objectID':meta['objectID'],'title':meta['title'],'isPublicDomain':True,'original_image':address,
    'objectURL':meta.get('objectURL')},indent=2))
  data=None
  # No need to retry a billable resource: image is freely downloadable, only HTTP.
  req=urllib.request.Request(address,headers={'User-Agent':'ArtVision-Museum-Source-Research/1.0 (Open Access PD)'})
  with urllib.request.urlopen(req,timeout=150) as resp:
   if 'image' not in resp.headers.get('Content-Type',''):
    raise RuntimeError('STOP source is not an image')
   data=resp.read(32_000_001)
  if not 140_000<len(data)<32_000_001:raise RuntimeError('STOP public-domain image invalid or too large')
  target.write_bytes(data)
 if EXPECTED_SHA1 and digest(target,'sha1')!=EXPECTED_SHA1:raise RuntimeError('STOP exact Commons source SHA1 mismatch')
 with Image.open(target) as im:
  if im.format!='JPEG':raise RuntimeError('STOP image not JPEG')
  if CFG.get('source_dimensions') and list(im.size)!=CFG['source_dimensions']:
   raise RuntimeError('STOP source dimensions unexpected '+repr(im.size))
  if min(im.size)<1000:raise RuntimeError('STOP Met image low resolution '+repr(im.size))
  dims=list(im.size)
 (OUT/'ARTWORK_PROVENANCE_V117.json').write_text(json.dumps({
   'artist':CFG['artist'],'work':CFG['original_title'],'museum':CFG['museum'],
   'inventory':CFG['inventory'],'source_url':SRC,
   'physical_size_cm':[CFG['height_cm'],CFG['width_cm']],
   'image_dimensions':dims,'sha1':digest(target,'sha1'),
   'sha256':digest(target),'public_domain_verification':'official museum + Commons or Met Open Access',
   'museum_frame':'digital interpretation, historic physical frame not replicated'},ensure_ascii=False,indent=2)+'\n')
 return target

def font(size,serif=True):
 family='DejaVuSerif' if serif else 'DejaVuSans'
 for p in [f'/usr/share/fonts/truetype/dejavu/{family}.ttf',f'/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf']:
  try:return ImageFont.truetype(p,size)
  except OSError:pass
 return ImageFont.load_default()

def fit(im,dim):
 out=im.copy();out.thumbnail(dim,Image.Resampling.LANCZOS);return out

def backdrop(im):
 bg=im.resize((W,H),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(55))
 bg=ImageEnhance.Brightness(bg).enhance(.31)
 fg=fit(im,(W-32,H-230));bg.paste(fg,((W-fg.width)//2,(H-fg.height)//2));return bg

def zoom_crop(im,x,y,zoom):
 # Keep moderate focal length: zoom=1 means full height, portrait crop horizontally.
 ow,oh=im.size
 ch=max(500,int(oh/zoom));cw=round(ch*W/H)
 l=max(0,min(ow-cw,round(ow*x-cw/2)));t=max(0,min(oh-ch,round(oh*y-ch/2)))
 return im.crop((l,t,l+cw,t+ch)).resize((W,H),Image.Resampling.LANCZOS)

def art_card(im,key):
 if key=='whole':return backdrop(im)
 x,y,z=FOCUS[key]
 card=zoom_crop(im,x,y,z)
 if key==BEATS[0]:
  d=ImageDraw.Draw(card,'RGBA');d.rectangle((0,1160,W,1280),fill=(10,13,16,172))
  title=CFG['title'].upper()
  d.text((W//2,1199),title,font=font(22),anchor='mm',fill=(252,243,223))
  d.text((W//2,1244),CFG['artist'].upper(),font=font(17,False),anchor='mm',fill=(223,211,190))
 return card

def room_card(im):
 """Gallery with high resolution physical depth: restrained, NOT a historic museum.
 A physical-ratio artwork, neutral aged oak frame, spatial lights, wall textures,
 parquet perspective, realistic cast shadow. No historical-frame claims.
 """
 S=2;w=W*S;h=H*S
 seed=int(hashlib.sha256(WORK_ID.encode()).hexdigest()[:8],16)
 rng=np.random.default_rng(seed)
 yy,xx=np.ogrid[:h,:w]
 # Neutral warm limestone gallery walls. Correct directional falloff.
 light1=np.exp(-((xx-w*.51)/(w*.54))**2-((yy-h*.30)/(h*.35))**2)*51
 light2=np.exp(-((xx-w*.30)/(w*.42))**2-((yy-h*.22)/(h*.45))**2)*15
 clouds=rng.normal(0,2.1,size=(h,w)).astype('float32')
 basearr=np.empty((h,w,3),dtype=np.uint8)
 for k,color in enumerate((91,86,78)):
  basearr[:,:,k]=np.uint8(np.clip(color+light1+light2+clouds-yy*.006-k*2.6,0,255))
 b=Image.fromarray(basearr,'RGB').convert('RGBA')
 del basearr,clouds,light1,light2
 d=ImageDraw.Draw(b)
 # Gallery architecture: cornice ceiling, dado rail, herringbone-floor perspective.
 hzn=2010
 d.rectangle((0,hzn,w,h),fill=(85,69,51,255))
 for t in range(40):
  y=hzn+t*t*0.32
  if y>h:break
  q=min(1,t/40);c=(int(86+18*q),int(69+14*q),int(50+11*q),255)
  d.line((0,int(y),w,int(y)),fill=c,width=max(2,t//10))
 for xpos in range(-w,w*2,100):
  d.line((w//2,hzn,xpos,h),fill=(57,46,37,170),width=1)
 for y,c,sz in [(75,(60,53,45,255),7),(100,(158,144,122,255),4),
                (hzn-35,(53,48,43,255),13),(hzn-18,(141,128,109,255),4)]:
  d.line((0,y,w,y),fill=c,width=sz)
 # Different work shapes each given a real-world ratio (never force square).
 ratio=CFG['width_cm']/CFG['height_cm']
 targetw=int(w*.79) if ratio>1.35 else int(w*.64)
 p_w=targetw; p_h=round(p_w/ratio)
 if p_h>int(h*.51):
  p_h=int(h*.51);p_w=round(p_h*ratio)
 px=(w-p_w)//2; py=int(h*.412-p_h/2)
 # Rounded shadow above wall, dimensions correct for the exact painting.
 shadow=Image.new('RGBA',(w,h));sd=ImageDraw.Draw(shadow)
 sd.rounded_rectangle((px-31+15,py-31+18,px+p_w+31+15,py+p_h+31+18),radius=7,fill=(0,0,0,175))
 shadow=shadow.filter(ImageFilter.GaussianBlur(28))
 b=Image.alpha_composite(b,shadow)
 d=ImageDraw.Draw(b)
 # Constructed thin dark wood frame: plausible museum neutral replacement,
 # never a mistaken ornate historical gold frame. Light/shadow give 3D bevel.
 for m,col in [(26,(17,17,16,255)),(21,(55,42,33,255)),(16,(105,77,47,255)),
               (12,(36,30,25,255)),(8,(168,133,78,255)),(5,(31,28,24,255))]:
  d.rectangle((px-m,py-m,px+p_w+m,py+p_h+m),outline=col,width=4)
 art=im.resize((p_w,p_h),Image.Resampling.LANCZOS).convert('RGBA')
 b.alpha_composite(art,(px,py))
 d=ImageDraw.Draw(b)
 d.line((px-25,py-25,px+p_w+25,py-25),fill=(183,142,91,190),width=2)
 d.line((px+p_w+25,py-23,px+p_w+25,py+p_h+25),fill=(18,14,13,190),width=3)
 # No invented readable labels or false captions resembling the actual collection.
 lx=min(w-110,px+p_w+55); ly=min(hzn-90,py+p_h-40)
 d.rectangle((lx,ly,lx+70,ly+47),fill=(167,163,156,255))
 for i in range(3):d.line((lx+10,ly+10+11*i,lx+55-(i%2)*10,ly+10+11*i),fill=(82,80,75,255),width=2)
 # Natural contact shadow for a very low, restrained viewing bench.
 bx0=int(w*.29);bx1=int(w*.71);by=int(h*.902)
 d.ellipse((bx0,by+80,bx1,by+115),fill=(22,18,14,80))
 d.rounded_rectangle((bx0,by,bx1,by+58),radius=11,fill=(40,37,33,255))
 d.rectangle((bx0+27,by+58,bx0+37,by+103),fill=(32,27,23,255))
 d.rectangle((bx1-37,by+58,bx1-27,by+103),fill=(32,27,23,255))
 return b.convert('RGB')

def title_card(im):
 a=backdrop(im);d=ImageDraw.Draw(a,'RGBA')
 d.rectangle((0,950,W,1280),fill=(9,12,15,198))
 d.text((W//2,1005),CFG['title'].upper(),font=font(22),anchor='mm',fill=(252,241,220))
 d.text((W//2,1062),CFG['artist'],font=font(23),anchor='mm',fill=(235,221,203))
 d.text((W//2,1125),CFG['year'],font=font(19,False),anchor='mm',fill=(206,207,202))
 return a

def make_cards(im):
 folder=OUT/'cards';folder.mkdir(exist_ok=True,parents=True)
 for key in list(FOCUS)+['room','title']:
  card=room_card(im) if key=='room' else title_card(im) if key=='title' else art_card(im,key)
  card.save(folder/(key+'.jpg'),quality=92,optimize=True)
 return folder

def synth_score(path,seconds):
 # Original instrumental score: evolving pads, bass swells, bell notes; no licensed recording.
 sr=32000;n=round(seconds*sr);t=np.arange(n,dtype=np.float32)/sr
 chords=[(146.83,174.61,220.0),(130.81,164.81,196.0),(110.0,146.83,174.61),(130.81,164.81,220.0)]
 s=np.zeros(n,dtype=np.float32)
 for j,c in enumerate(chords):
  a=j*seconds/4;b=(j+1)*seconds/4;mask=(t>=a)&(t<b);tt=t[mask]-a
  # Gentle detuning, original composition rather than borrowed melody.
  for k,f in enumerate(c):s[mask]+=np.float32(.063/(k+1))*np.sin(2*np.pi*f*tt+.18*np.sin(2*np.pi*.12*tt))
  s[mask]+=np.float32(.067)*np.sin(2*np.pi*(c[0]/2)*tt)
 for at in np.arange(1.4,seconds-1,2.75):
  ind=np.arange(max(0,int(at*sr)),min(n,int((at+1.5)*sr)))
  tau=(ind/sr-at).astype('float32')
  f=[440,523.25,392,587.33][int(at/2.75)%4]
  s[ind]+=(.075*np.exp(-tau*2.7)*np.sin(2*np.pi*f*tau)).astype('float32')
 env=np.minimum(np.minimum(t/2.5,(seconds-t)/3.0),1.0)
 s*=np.clip(env,0,1).astype('float32')
 s=np.tanh(s*2.3)*.85
 pcm=(np.clip(s,-1,1)*32760).astype('<i2')
 with wave.open(str(path),'wb') as f:
  f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr);f.writeframes(pcm.tobytes())

def scene(folder,image,key,duration,idx,museum=False):
 count=round(duration*FPS)
 if count<12:raise ValueError('Shot too short')
 target=folder/f'{idx:02d}_{key}.mp4'
 if key in ('room','room_out'):
  # Continuous geometric museum camera, no crossfades or double exposed art.
  z=(f'min(1+on*4.8/{count-1},5.8)' if key=='room' else
     f'max(5.8-on*4.8/{count-1},1)')
  # Work in the exact center: y points toward physical canvas at ~0.41H.
  y="max(0,min(ih-ih/zoom,iw*0+ih*0.41-ih/zoom/2))"
 else:
  inc=.018 if idx%3==0 else .033 if idx%3==1 else .022
  z=(f'min(1+on*{inc:.4f}/{count-1},1+{inc:.4f})' if idx%2 else
     f'max(1+{inc:.4f}-on*{inc:.4f}/{count-1},1)')
  y='ih/2-ih/zoom/2'
 filt=f"zoompan=z='{z}':x='iw/2-iw/zoom/2':y='{y}':d={count}:s={W}x{H}:fps={FPS},format=yuv420p"
 run([ffmpeg(),'-hide_banner','-v','error','-y','-loop','1','-i',image,'-vf',filt,
      '-frames:v',count,'-an','-c:v','libx264','-preset','veryfast','-crf','21',
      '-r',FPS,'-pix_fmt','yuv420p',target])
 return target

def video_from_sequence(name,shotlist,score,shared_audio=None):
 folder=OUT/name;folder.mkdir(exist_ok=True)
 cards=OUT/'cards';clips=[]
 for i,(key,duration) in enumerate(shotlist):
  image=cards/(('room' if key=='room_out' else key)+'.jpg')
  clips.append(scene(folder,image,key,duration,i))
 concat=folder/'concat.txt';concat.write_text(''.join("file '"+str(p.resolve())+"'\n" for p in clips))
 silent=folder/'silent.mp4'
 run([ffmpeg(),'-v','error','-y','-f','concat','-safe','0','-i',concat,'-c','copy',silent])
 output=OUT/f'{WORK_CODE}_{name.upper()}_V117_REVIEW.mp4'
 audio=shared_audio or score
 run([ffmpeg(),'-v','error','-y','-i',silent,'-i',audio,'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac' if shared_audio is None else 'copy','-b:a','160k','-shortest','-movflags','+faststart',output])
 run([ffmpeg(),'-v','error','-xerror','-i',output,'-f','null','-'])
 return dict(name=output.name,bytes=output.stat().st_size,sha256=digest(output),seconds=round(sum(d for _,d in shotlist),2),full_decode='PASS',V25_Gold=False)

def chapters_from_timing(timed,duration):
 # gemini_voice sends individual sentences; group by original chapter sentence count.
 from gemini_voice import sentences
 out=[];i=0
 for _,text in WORDS:
  i+=len(sentences(text));out.append(float(timed[i-1][2]))
 if out[-1]<duration-3:out[-1]=duration
 if any(out[i+1]<=out[i] for i in range(len(out)-1)):raise ValueError('Nonmonotonic narration timestamps')
 return out

def voice_once():
 state=OUT/'VOICE_STATE.json'
 if os.environ.get('ARTVISION_GEMINI_PROJECT_BILLING_TIER')!='Free' or not os.environ.get('GEMINI_API_KEY'):
  data={'status':'BLOCKED_MISSING_OWNER_ATTESTED_FREE_TIER_OR_SECOND_KEY_NO_TTS_CALL'};state.write_text(json.dumps(data,indent=2));return None,data
 sys.path.insert(0,str(ROOT/'src'))
 import gemini_voice
 text='\n\n'.join(t for _,t in WORDS)
 try:
  pcm,timed=gemini_voice.synthesize(text,OUT)
  dur=len(pcm)/24000
  if not 50<dur<180: raise ValueError('Narration duration invalid')
  times=chapters_from_timing(timed,dur)
  data={'status':'ONE_SHARED_GACRUX_WAV_READY','wav_sha256':digest(OUT/'VOCE.wav'),'duration':dur,'chapter_ends':times,'source_account':'GEMINI_API_KEY2 owner-attested Free, invoicing not independently verifiable','call_repeat_forbidden':True}
  state.write_text(json.dumps(data,ensure_ascii=False,indent=2));return dur,data
 except Exception as e:
  data={'status':'VOICE_ATTEMPT_FAILED_NO_AUTOMATIC_RETRY','error':type(e).__name__+':'+str(e)[:240],'wav_exists':(OUT/'VOCE.wav').exists()}
  state.write_text(json.dumps(data,ensure_ascii=False,indent=2));return None,data

def main():
 import argparse
 p=argparse.ArgumentParser()
 p.add_argument('--mode',choices=['preflight','critico'],required=True)
 args=p.parse_args()
 if os.environ.get('ARTVISION_EXACT_WORK_ID')!=WORK_ID:raise RuntimeError('Scope mismatch')
 source=get_art()
 with Image.open(source) as im:
  a=im.convert('RGB');a.thumbnail((5400,6500),Image.Resampling.LANCZOS)
  make_cards(a)
 manifest=OUT/'QA_V117.json'
 q=json.loads(manifest.read_text()) if manifest.exists() else {
  'work_id':WORK_ID,'artist':CFG['artist'],'title':CFG['title'],
  'museum':CFG['museum'],'inventory':CFG['inventory'],
  'source_actual_url':SRC,'source_sha256':digest(source),
  'source_image_size':list(Image.open(source).size),
  'scene':'DIGITAL museum reproduction; frame NOT authenticated historic',
  'preserved_prior_cinema_standard':True,'preserved_prior_cinema_museum':True,
  'Social_published':False,'Gold_V25':0,'Android_site_verified':False,
  'files':{}}
 if args.mode=='preflight':
  q['source_preflight_pass']=True
  q['source_image_cards_created']=len(list((OUT/'cards').glob('*.jpg')))
  manifest.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
  print(json.dumps({'work':WORK_ID,'source_sha256':q['source_sha256'],
      'source_cards':q['source_image_cards_created'],'state':'SRC_QUALITY_OK_NO_TTS_CALLED'},indent=2))
  return
 # No retry: if audio state already attempted, this work cannot call TTS again.
 if (OUT/'VOICE_STATE.json').exists():raise RuntimeError('STOP: Gacrux attempt already recorded - never make second call')
 dur,state=voice_once();q['voice']=state
 if not dur:
  q['blocked_no_voice_no_fake_mp4']=True
  manifest.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
  print(json.dumps(q,ensure_ascii=False,indent=2));return
 shared=OUT/'CRITICO_AUDIO_IDENTICO.m4a'
 music=OUT/'CRITICO_MUSICA_ORIGINALE.wav'
 synth_score(music,dur+11)
 run([ffmpeg(),'-v','error','-y','-i',OUT/'VOCE.wav','-i',music,'-filter_complex',
   '[0:a]adelay=5000|5000,volume=1.0[v];[1:a]volume=0.16[m];[v][m]amix=inputs=2:duration=longest:dropout_transition=0,alimiter=limit=0.92[a]',
   '-map','[a]','-c:a','aac','-b:a','160k',shared])
 ends=state['chapter_ends'];duration=[ends[0]]+[b-a for a,b in zip(ends,ends[1:])]
 std=[(BEATS[0],5.0)]+list(zip(BEATS,duration))+[('whole',6.0)]
 mus=[('room',5.0)]+list(zip(BEATS,duration))+[('room_out',6.0)]
 q['files']['critico_standard']=video_from_sequence('critico_standard',std,music,shared)
 q['files']['critico_museum']=video_from_sequence('critico_museum',mus,music,shared)
 q['voice']['shared_AAC_sha256']=digest(shared)
 q['files_generated_count']=len(q['files'])
 q['standard_and_museum_both_use_same_narration']=True
 q['human_artistic_qa']='pending'
 manifest.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
 with zipfile.ZipFile(OUT/(WORK_CODE+'_2_CRITICO_ANDROID_V117.zip'),'w',zipfile.ZIP_STORED) as z:
  for item in q['files'].values():z.write(OUT/item['name'],item['name'])
  z.write(manifest,manifest.name)
 with zipfile.ZipFile(OUT/(WORK_CODE+'_2_CRITICO_COMPLETO_V117.zip'),'w',zipfile.ZIP_STORED) as z:
  for item in q['files'].values():z.write(OUT/item['name'],item['name'])
  for nm in ['QA_V117.json','ARTWORK_PROVENANCE_V117.json','VOICE_STATE.json','cards/title.jpg']:
   if (OUT/nm).exists():z.write(OUT/nm,nm)
 q['zip_crc_verified']=all(
  zipfile.ZipFile(OUT/(WORK_CODE+'_'+x+'_V117.zip')).testzip() is None
  for x in ['2_CRITICO_ANDROID','2_CRITICO_COMPLETO'])
 manifest.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(q,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
