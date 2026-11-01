#!/usr/bin/env python3
"""Seventh ArtVision pilot: Jacek Malczewski Błędne koło, MNP FR 56.
One verified public-domain painting; four independently directed video slots.
Fail closed on source identity. No paid API calls. New Critico voice only in
owner-attested Free/no-billing Gacrux tier; never call if tier/key unavailable.
"""
import hashlib,json,os,sys,subprocess,urllib.request,zipfile,math,wave
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageEnhance,ImageFilter

SRC='https://upload.wikimedia.org/wikipedia/commons/9/9e/Bledne_kolo.jpg'
EXPECTED_SHA1='94a56db15afd68bad5d1322e8b13a7d8970335e3'
W,H,FPS=720,1280,20
ROOT=Path(__file__).resolve().parents[1]
OUT=Path(os.environ.get('ARTVISION_OUT','output/artvision_malczewski_v110'))
WORDS=[
 ('Un ragazzo, una scala', 'Un ragazzo siede in cima a una scala, con un pennello in mano. Intorno a lui, i corpi sembrano sfidare la gravità.'),
 ('L’invenzione del mondo', 'Non è una scena reale: è il mondo della sua immaginazione. Jacek Malczewski lo chiama Il circolo vizioso.'),
 ('La metà luminosa', 'A sinistra, figure giovani si avvolgono in una danza luminosa. I colori sono caldi, i gesti liberi, quasi festosi.'),
 ('L’altra metà', 'A destra la luce si spegne. Volti provati, braccia tese, ombre e fatica trasformano quel girotondo in un peso.'),
 ('Una scala', 'La scala attraversa tutto il dipinto. Il piccolo artista sta in alto, ma non domina davvero ciò che ha creato.'),
 ('Corpi sospesi', 'Guardiamo le figure più vicine: alcune si protendono verso il vuoto, altre sembrano trattenute da una forza invisibile.'),
 ('Due forze', 'Gioia e dolore non sono due quadri diversi. Sono le due metà di un unico movimento, intorno allo stesso ragazzo.'),
 ('Polonia e simboli', 'Malczewski dipinse quest’opera tra il milleottocentonovantacinque e il milleottocentonovantasette, dentro un mondo segnato dalla storia polacca e dal simbolismo.'),
 ('La domanda finale', 'Che cosa significa essere un artista? Inventare un mondo, o sopportare tutto ciò che quel mondo contiene? Il cerchio rimane aperto.')
]
# Source-canvas coordinates: fractions of original landscape painting.
FOCUS={'boy':(.515,.155,1.95),'left_festive':(.235,.285,1.42),
       'right_shadow':(.805,.365,1.42),'ladder':(.52,.68,1.35),
       'lower_left':(.19,.78,1.58),'central_body':(.51,.48,1.40),
       'right_faces':(.79,.22,1.58),'whole':(.5,.5,1.0)}
BEATS=['boy','whole','left_festive','right_shadow','ladder','central_body','left_festive','right_faces','whole']
CINEMA=[('boy',5),('whole',6),('left_festive',6),('central_body',5),('right_shadow',6),('ladder',6),('right_faces',6),('whole',7)]
CINEMA_M=[('room',8),('boy',5),('left_festive',6),('right_shadow',6),('ladder',6),('central_body',6),('whole',6),('room_out',9)]


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
 target=OUT/'Bledne_kolo_MNP_FR56_PD.jpg'
 if not target.exists():
  req=urllib.request.Request(SRC,headers={'User-Agent':'ArtVision-Malczewski/1.0 (copyright public domain research)'})
  with urllib.request.urlopen(req,timeout=90) as resp:
   if 'image' not in resp.headers.get('Content-Type',''):raise ValueError('Not source image')
   target.write_bytes(resp.read(12000000))
 if digest(target,'sha1')!=EXPECTED_SHA1:raise ValueError('Exact Wikimedia source SHA1 mismatch')
 with Image.open(target) as im:
  if im.size!=(5026,3557):raise ValueError('Source image dims mismatch')
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
 if key=='boy':
  d=ImageDraw.Draw(card,'RGBA');d.rectangle((0,1070,W,H),fill=(11,14,17,190))
  d.text((W//2,1133),'IL CIRCOLO VIZIOSO',font=font(36),anchor='mm',fill=(250,240,218))
  d.text((W//2,1194),'JACEK MALCZEWSKI',font=font(18,False),anchor='mm',fill=(207,202,181))
 return card

def room_card(im):
 # Clearly declared digital study space, not actual Poznan museum or historical frame.
 base=Image.new('RGB',(W,H),(53,54,56));dr=ImageDraw.Draw(base)
 for y in range(H):
  c=int(40+y*.010);dr.line([(0,y),(W,y)],fill=(c,c+2,c+4))
 pic=fit(im,(W-110,760));px=(W-pic.width)//2;py=430
 dr.rectangle([px-18,py-18,px+pic.width+18,py+pic.height+18],fill=(31,30,30),outline=(120,109,89),width=9)
 base.paste(pic,(px,py));dr.rectangle([px-12,py-12,px+pic.width+12,py+pic.height+12],outline=(160,144,112),width=4)
 dr.line([(0,1120),(W,1120)],fill=(89,84,76),width=6)
 dr.rectangle([30,1133,W-30,1272],fill=(38,39,41))
 dr.text((W//2,1200),'RICOSTRUZIONE DIGITALE',font=font(15,False),anchor='mm',fill=(160,163,164))
 return base

def title_card(im):
 x=backdrop(im);dr=ImageDraw.Draw(x,'RGBA');dr.rectangle((0,920,W,H),fill=(11,14,17,200))
 dr.text((W//2,986),'IL CIRCOLO VIZIOSO',font=font(38),anchor='mm',fill=(248,241,226))
 dr.text((W//2,1051),'JACEK MALCZEWSKI  ·  1895–1897',font=font(18,False),anchor='mm',fill=(215,201,169))
 dr.text((W//2,1105),'MUSEO NAZIONALE DI POZNAŃ',font=font(15,False),anchor='mm',fill=(218,213,201))
 return x

def make_cards(im):
 folder=OUT/'cards';folder.mkdir(exist_ok=True)
 for key in list(FOCUS)+['room','title']:
  card=room_card(im) if key=='room' else title_card(im) if key=='title' else art_card(im,key)
  card.save(folder/(key+'.jpg'),quality=94,optimize=True)
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
 """Avoid repetitive move: alternating 1–3% controlled push/pull, no fake movement of painted people."""
 count=round(duration*FPS)
 if count<12:raise ValueError('Shot too short')
 target=folder/f'{idx:02d}_{key}.mp4'
 if key=='room':
  z="min(1+on*0.70/(d-1),1.70)".replace('d-1',str(count-1))
 elif key=='room_out':
  z="max(1.70-on*0.70/(d-1),1)".replace('d-1',str(count-1))
 else:
  inc=.016 if idx%3==0 else .032 if idx%3==1 else .023
  z=(f'min(1+on*{inc:.4f}/{count-1},1+{inc:.4f})' if idx%2 else f'max(1+{inc:.4f}-on*{inc:.4f}/{count-1},1)')
 filt=f"zoompan=z='{z}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={count}:s={W}x{H}:fps={FPS},format=yuv420p"
 run([ffmpeg(),'-hide_banner','-v','error','-y','-loop','1','-i',image,'-vf',filt,'-frames:v',count,'-an','-c:v','libx264','-preset','ultrafast','-crf','20','-r',FPS,'-pix_fmt','yuv420p',target])
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
 output=OUT/f'MALCZEWSKI_{name.upper()}_V110_REVIEW.mp4'
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
 if os.environ.get('ARTVISION_EXACT_WORK_ID')!='malczewski_bledne_kolo_1897_mnp_fr56': raise RuntimeError('Seventh pilot scope not explicitly selected')
 source=get_art()
 with Image.open(source) as im:make_cards(im.convert('RGB'))
 manifest=OUT/'QA_V110.json';q=json.loads(manifest.read_text()) if manifest.exists() else {'work_id':'malczewski_bledne_kolo_1897_mnp_fr56','museum':'National Museum Poznań','inventory':'MNP FR 56','source':SRC,'source_sha1':EXPECTED_SHA1,'source_sha256':digest(source),'source_dimensions':[5026,3557],'museum_room':'digital reconstruction, frame NOT documented historic','social_published':False,'V25_Gold':0,'Android_R2_verified':False,'files':{}}
 if args.mode=='cinema':
  score=OUT/'CINEMA_MUSICA_ORIGINALE.wav';synth_score(score,60)
  q['files']['cinema_standard']=video_from_sequence('cinema_standard',CINEMA,score)
  q['files']['cinema_museum']=video_from_sequence('cinema_museum',CINEMA_M,score)
 else:
  dur,state=voice_once();q['voice']=state
  if dur:
   # Shared AAC exactly identical (bit-by-bit) in both Critico.
   # Voice begins 5 seconds into both films, room intro for Museum.
   shared=OUT/'CRITICO_AUDIO_IDENTICO.m4a'
   music=OUT/'CRITICO_MUSICA_ORIGINALE.wav';synth_score(music,dur+11)
   run([ffmpeg(),'-v','error','-y','-i',OUT/'VOCE.wav','-i',music,'-filter_complex','[0:a]adelay=5000|5000,volume=1.0[v];[1:a]volume=0.19[m];[v][m]amix=inputs=2:duration=longest:dropout_transition=0,alimiter=limit=0.92[a]','-map','[a]','-c:a','aac','-b:a','160k',shared])
   ends=state['chapter_ends'];durations=[ends[0]]+[b-a for a,b in zip(ends,ends[1:])]
   # Put intro 5s and exit 6s in both, precisely same total duration.
   std=[('boy',5.0)]+list(zip(BEATS,durations))+[('whole',6.0)]
   mus=[('room',5.0)]+list(zip(BEATS,durations))+[('room_out',6.0)]
   q['files']['critico_standard']=video_from_sequence('critico_standard',std,music,shared)
   q['files']['critico_museum']=video_from_sequence('critico_museum',mus,music,shared)
   q['voice']['aac_shared_sha256']=digest(shared)
 q['files_generated_count']=len(q['files']);manifest.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
 # Covers + 4 original social posts per actual produced variant, never published.
 social=OUT/'SOCIAL_BOZZE.txt'
 social.write_text('''ARTVISION — IL CIRCOLO VIZIOSO — POST IN BOZZA, NON PUBBLICATI\n\nCRITICO STANDARD\n1. Un bambino, una scala, un mondo che non sta fermo.\n2. La metà luminosa e la metà oscura della stessa vita.\n3. Jacek Malczewski: la pittura come domanda, non risposta.\n4. Poznań conserva una delle visioni più inquietanti del simbolismo.\n\nCRITICO MUSEUM\n1. Entriamo in un dipinto dove la gravità smette di valere.\n2. Una spirale di figure: chi comanda davvero?\n3. Non è una sala storica: l'ambiente di ingresso è ricostruito digitalmente.\n4. Il museo immaginato lascia spazio all'opera autentica.\n\nCINEMA STANDARD\n1. Un circolo di gioia e sofferenza.\n2. Il mondo inventato da un ragazzo con il pennello.\n3. La fantasia che diventa vertigine.\n4. La bellezza è anche inquietudine.\n\nCINEMA MUSEUM\n1. Un passo dentro l'immaginazione.\n2. La scala al centro di tutto.\n3. Dal museo ricostruito al quadro vero.\n4. Quando il dipinto diventa mondo.\n''',encoding='utf8')
 # Only declare selected real files, not imaginary four.
 if args.mode=='critico':
  expected={'cinema_standard','cinema_museum','critico_standard','critico_museum'}
  if expected.issubset(q['files']):
   with zipfile.ZipFile(OUT/'MALCZEWSKI_4_VIDEO_ANDROID_V110_REVIEW.zip','w',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
    for it in q['files'].values():z.write(OUT/it['name'],it['name'])
    z.write(manifest,manifest.name)
   with zipfile.ZipFile(OUT/'MALCZEWSKI_4X1_COMPLETO_V110_REVIEW.zip','w',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
    for it in q['files'].values():z.write(OUT/it['name'],it['name'])
    for pp in ['QA_V110.json','SOCIAL_BOZZE.txt','cards/title.jpg','VOICE_STATE.json']:
     if (OUT/pp).exists():z.write(OUT/pp,pp)
   q['zip_crc_verified']=all(not zipfile.ZipFile(p).testzip() for p in [OUT/'MALCZEWSKI_4_VIDEO_ANDROID_V110_REVIEW.zip',OUT/'MALCZEWSKI_4X1_COMPLETO_V110_REVIEW.zip'])
   manifest.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(q,ensure_ascii=False,indent=2))

if __name__=='__main__': main()