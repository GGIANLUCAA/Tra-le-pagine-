#!/usr/bin/env python3
"""ArtVision V114: exactly four newly authorized, individual 4x1 artworks.
Original museum sources, 4 real MP4 per artwork, owner-attested FREE Gacrux
only for one WAV per work. Reviewer approval is separate and never automated.
This script does not alter or rerender past paintings or make paid video calls.
"""
import hashlib,json,os,sys,subprocess,urllib.request,zipfile,math,wave
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageEnhance,ImageFilter
W,H,FPS=720,1280,20
ROOT=Path(__file__).resolve().parents[1]
SPEC_DIR=ROOT/'modules/artvision_critico/production_series/2026_11_01_four_original'
AUTH={
 'rosa_bonheur_horse_fair_met_87_25',
 'millais_blind_girl_birmingham_1892p3',
 'burne_jones_arthur_avalon_ponce_63_0369',
 'vedder_sphinx_seashore_deyoung_1979_7_102'
}
WORK_ID=os.environ.get('ARTVISION_EXACT_WORK_ID','')
if WORK_ID not in AUTH:raise RuntimeError('BLOCKED: V114 exactly four owner-authorized paintings; others forbidden')
CFG=json.loads((SPEC_DIR/(WORK_ID+'.json')).read_text(encoding='utf8'))
assert CFG['work_id']==WORK_ID and CFG['owner_authorized'] and len(CFG['story'])==9
SRC=CFG['source_url'];EXPECTED_SHA1=CFG.get('expected_sha1')
WORK_CODE={'rosa_bonheur_horse_fair_met_87_25':'BONHEUR_HORSE_FAIR',
'millais_blind_girl_birmingham_1892p3':'MILLAIS_BLIND_GIRL',
'burne_jones_arthur_avalon_ponce_63_0369':'BURNE_JONES_ARTHUR',
'vedder_sphinx_seashore_deyoung_1979_7_102':'VEDDER_SPHINX'}[WORK_ID]
OUT=Path(os.environ.get('ARTVISION_OUT','output/artvision_four_new_v114'))/WORK_ID
WORDS=[(row[0],row[1]) for row in CFG['story']]
FOCUS={k:tuple(v) for k,v in CFG['focus'].items()}
BEATS=[row[2] for row in CFG['story']]
CINEMA=[(row[0],float(row[1])) for row in CFG['cinema']]
CINEMA_M=[(row[0],float(row[1])) for row in CFG['cinema_museum']]

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
 target=OUT/'ART_PD_ORIGINAL.jpg'
 if not target.exists():
  req=urllib.request.Request(SRC,headers={'User-Agent':'ArtVision-Four-PD-2026/1.0 (public-domain artwork, GitHub Actions)'})
  with urllib.request.urlopen(req,timeout=150) as resp:
   assert 'image' in resp.headers.get('Content-Type',''), 'No image Content-Type'
   raw=resp.read(34_000_001)
   assert 150_000<len(raw)<34_000_001,'Source unexpectedly small or too large'
   target.write_bytes(raw)
 if EXPECTED_SHA1 and digest(target,'sha1')!=EXPECTED_SHA1:raise ValueError('EXACT original Wikimedia SHA1 mismatch')
 with Image.open(target) as im:
  if list(im.size)!=CFG['source_dimensions']:raise ValueError('Incorrect source image dimensions: '+repr(im.size))
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
  # Thin, tasteful titling for only the first shot. Avoid giant overlay on faces.
  dr=ImageDraw.Draw(card,'RGBA')
  dr.rectangle((0,1160,W,1280),fill=(9,12,16,155))
  dr.text((W//2,1196),CFG['title'].upper(),font=font(24),anchor='mm',fill=(248,238,217))
  dr.text((W//2,1243),CFG['artist'].upper(),font=font(16,False),anchor='mm',fill=(222,213,194))
 return card

def room_card(im):
 # Digital gallery study, never a claim of the real museum or authentic old frame.
 # 2x resolution so the camera can push inside the frame without bitmap blocks.
 S=2;w=W*S;h=H*S
 seed=int(hashlib.sha256(WORK_ID.encode()).hexdigest()[:8],16)
 rng=np.random.default_rng(seed)
 yy,xx=np.mgrid[0:h,0:w]
 # Natural stone/plaster texture, imperfect illumination and soft off-center spotlight.
 noise=rng.normal(0,3.0,size=(h,w)).astype('float32')
 dist=((xx-w*.52)/(w*.57))**2+((yy-h*.39)/(h*.53))**2
 lum=np.exp(-dist*2.0)*29
 wall=np.zeros((h,w,3),dtype='uint8')
 for k,b in enumerate((51,50,48)):
  wall[:,:,k]=np.clip(b+lum+noise+yy*.002-k*1.8,0,255).astype('uint8')
 base=Image.fromarray(wall,'RGB')
 del wall,noise,yy,xx,lum
 d=ImageDraw.Draw(base)
 # Wall/floor meet with natural distance and parquet perspective.
 horizon=int(h*.78)
 d.rectangle((0,horizon,w,h),fill=(59,47,36))
 for i in range(45):
  y=horizon+i*i*0.20
  if y>=h:break
  val=int(58+18*i/45)
  d.line([(0,int(y)),(w,int(y))],fill=(val,val-13,val-25),width=max(1,round(i/12)))
 van=w//2
 for x in range(-w*2,w*3,135):
  d.line((van,horizon,x,h),fill=(77,62,46),width=2)
 # Dado and understated ceiling trim.
 d.rectangle((0,horizon-12,w,horizon-2),fill=(31,30,29))
 d.line((0,100,w,100),fill=(102,93,81),width=8)
 d.line((0,115,w,115),fill=(37,34,31),width=4)
 # Gallery scale intentionally adjusted to an appropriate camera distance for each painting.
 phw=CFG['width_cm']/CFG['height_cm']
 maxw=int(w*.82);maxh=int(h*.53)
 if phw>.95:
  picw=maxw; pich=min(maxh,round(picw/phw))
 else:
  pich=maxh;picw=min(maxw,round(pich*phw))
 if CFG['height_cm']>170 and phw>1.5:
  # Large panoramas are hung across almost the complete wall.
  picw=int(w*.86);pich=round(picw/phw)
 if CFG['height_cm']<90 and phw>1.45:
  # Small original painting: step back enough to keep credible framing.
  picw=int(w*.60);pich=round(picw/phw)
 cx=w//2;cy=int(h*.405)
 x0=cx-picw//2;y0=cy-pich//2;x1=x0+picw;y1=y0+pich
 # Soft physical shadow under frame.
 shade=Image.new('RGBA',(w,h),(0,0,0,0));sd=ImageDraw.Draw(shade)
 sd.rounded_rectangle((x0-30+9,y0-30+18,x1+30+9,y1+30+18),radius=10,fill=(0,0,0,185))
 shade=shade.filter(ImageFilter.GaussianBlur(32))
 base=Image.alpha_composite(base.convert('RGBA'),shade)
 d=ImageDraw.Draw(base)
 # Realistic restrained wood/bronze moulding with bevel and slight patina.
 for k,color in [(35,(23,21,19,255)),(27,(60,48,35,255)),(23,(98,82,61,255)),(18,(25,24,23,255)),(13,(147,118,75,255)),(9,(55,43,30,255)),(5,(183,149,97,255))]:
  d.rectangle((x0-k,y0-k,x1+k,y1+k),outline=color,width=max(2,S+1))
 art=im.copy();art.thumbnail((picw,pich),Image.Resampling.LANCZOS)
 art=art.resize((picw,pich),Image.Resampling.LANCZOS)
 base.alpha_composite(art.convert('RGBA'),(x0,y0))
 d=ImageDraw.Draw(base)
 # Highlights on top and right imply a bevel, physically plausible shadow underneath.
 d.line((x0-25,y0-25,x1+25,y0-25),fill=(205,166,115,160),width=2)
 d.line((x1+25,y0-25,x1+25,y1+25),fill=(12,13,13,180),width=3)
 # Discreet anonymous wall caption: do not pretend to show an actual plaque.
 plaque_x=min(w-145,x1+70);plaque_y=min(horizon-130,y1-75)
 d.rectangle((plaque_x,plaque_y,plaque_x+70,plaque_y+50),fill=(155,148,134,255))
 for a in range(4):
  d.line((plaque_x+11,plaque_y+11+a*9,plaque_x+59-(a%2)*12,plaque_y+11+a*9),fill=(83,77,71,255),width=2)
 # Visible depth clues: subtle floor reflections, not invented gallery visitors.
 d.line((0,horizon+30,w,horizon+30),fill=(124,105,80,115),width=3)
 return base.convert('RGB')

def title_card(im):
 card=backdrop(im);d=ImageDraw.Draw(card,'RGBA')
 d.rectangle((0,980,W,H),fill=(10,14,18,194))
 d.text((W//2,1040),CFG['title'].upper(),font=font(27),anchor='mm',fill=(251,245,229))
 d.text((W//2,1110),CFG['artist'],font=font(23),anchor='mm',fill=(227,216,196))
 d.text((W//2,1170),CFG['museum'],font=font(14,False),anchor='mm',fill=(190,191,188))
 return card

def make_cards(im):
 folder=OUT/'cards';folder.mkdir(exist_ok=True)
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
  # Deliberately advance through the frame into the painting, not a static fake wall.
  z=(f'min(1+on*3.30/{count-1},4.30)' if key=='room' else
     f'max(4.30-on*3.30/{count-1},1)')
  # Room image at 1440x2560; artwork center at normalized y=.405.
  y="max(0,min(ih-ih/zoom,(ih*.5+(ih*.405-ih*.5)*(zoom-1)/3.3)-ih/zoom/2))"
 else:
  inc=.022 if idx%3==0 else .033 if idx%3==1 else .017
  z=(f'min(1+on*{inc:.4f}/{count-1},1+{inc:.4f})' if idx%2 else
     f'max(1+{inc:.4f}-on*{inc:.4f}/{count-1},1)')
  y='ih/2-ih/zoom/2'
 filt=(f"zoompan=z='{z}':x='iw/2-iw/zoom/2':y='{y}':"
       f"d={count}:s={W}x{H}:fps={FPS},format=yuv420p")
 run([ffmpeg(),'-hide_banner','-v','error','-y','-loop','1','-i',image,'-vf',filt,'-frames:v',count,
      '-an','-c:v','libx264','-preset','veryfast','-crf','23',
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
 output=OUT/f'{WORK_CODE}_{name.upper()}_V114_REVIEW.mp4'
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
 p=argparse.ArgumentParser();p.add_argument('--mode',choices=['cinema','critico'],required=True);args=p.parse_args()
 if os.environ.get('ARTVISION_EXACT_WORK_ID')!=WORK_ID:raise RuntimeError('Wrong work scope')
 source=get_art()
 with Image.open(source) as im:
  work=im.convert('RGB');work.thumbnail((5400,6500),Image.Resampling.LANCZOS)
  make_cards(work)
 manifest=OUT/'QA_V114.json'
 q=json.loads(manifest.read_text()) if manifest.exists() else {
  'work_id':WORK_ID,'artist':CFG['artist'],'title':CFG['title'],
  'museum':CFG['museum'],'inventory':CFG['inventory'],
  'physical_size_cm':[CFG['height_cm'],CFG['width_cm']],
  'source':SRC,'source_page':CFG['source_page'],
  'source_sha1':digest(source,'sha1'),'source_sha256':digest(source),
  'source_dimensions':CFG['source_dimensions'],
  'museum_room':'digital reconstruction, not authentic room or documented frame',
  'social_published':False,'V25_Gold':0,'Android_R2_verified':False,'files':{}}
 if args.mode=='cinema':
  score=OUT/'CINEMA_MUSICA_ORIGINALE.wav';synth_score(score,60)
  q['files']['cinema_standard']=video_from_sequence('cinema_standard',CINEMA,score)
  q['files']['cinema_museum']=video_from_sequence('cinema_museum',CINEMA_M,score)
 else:
  dur,state=voice_once();q['voice']=state
  if dur:
   shared=OUT/'CRITICO_AUDIO_IDENTICO.m4a'
   music=OUT/'CRITICO_MUSICA_ORIGINALE.wav';synth_score(music,dur+11)
   run([ffmpeg(),'-v','error','-y','-i',OUT/'VOCE.wav','-i',music,'-filter_complex',
     '[0:a]adelay=5000|5000,volume=1.0[v];[1:a]volume=0.16[m];[v][m]amix=inputs=2:duration=longest:dropout_transition=0,alimiter=limit=0.92[a]',
     '-map','[a]','-c:a','aac','-b:a','160k',shared])
   ends=state['chapter_ends'];durations=[ends[0]]+[b-a for a,b in zip(ends,ends[1:])]
   std=[(BEATS[0],5.0)]+list(zip(BEATS,durations))+[('whole',6.0)]
   mus=[('room',5.0)]+list(zip(BEATS,durations))+[('room_out',6.0)]
   q['files']['critico_standard']=video_from_sequence('critico_standard',std,music,shared)
   q['files']['critico_museum']=video_from_sequence('critico_museum',mus,music,shared)
   q['voice']['aac_shared_sha256']=digest(shared)
 q['files_generated_count']=len(q['files'])
 q['human_full_speed_review']='pending'
 manifest.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 posts=[]
 for variant in ['critico_standard','critico_museum','cinema_standard','cinema_museum']:
  posts.append('ARTVISION '+CFG['title']+' — '+variant.upper()+' (BOZZA NON PUBBLICATA)')
  for i,(heading,txt) in enumerate(WORDS[:4]):
   posts.append(str(i+1)+'. '+heading+': '+txt)
  posts.append('')
 (OUT/'SOCIAL_BOZZE_16.txt').write_text('\n'.join(posts),encoding='utf8')
 if args.mode=='critico':
  expected={'cinema_standard','cinema_museum','critico_standard','critico_museum'}
  if expected.issubset(q['files']):
   for label,complete in [('4_VIDEO_ANDROID',False),('4X1_COMPLETO',True)]:
    with zipfile.ZipFile(OUT/(WORK_CODE+'_'+label+'_V114_REVIEW.zip'),'w',zipfile.ZIP_STORED) as z:
     for it in q['files'].values():z.write(OUT/it['name'],it['name'])
     if complete:
      for nm in ['QA_V114.json','SOCIAL_BOZZE_16.txt','cards/title.jpg','VOICE_STATE.json','ALLINEAMENTO_VOCE.json']:
       p=OUT/nm
       if p.exists():z.write(p,nm)
   q['zip_crc_verified']=all(
    zipfile.ZipFile(OUT/(WORK_CODE+'_'+label+'_V114_REVIEW.zip')).testzip() is None
    for label in ['4_VIDEO_ANDROID','4X1_COMPLETO'])
   manifest.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps(q,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
