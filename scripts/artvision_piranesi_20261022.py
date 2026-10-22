#!/usr/bin/env python3
"""Artist-specific ArtVision Cinema V6 Piranesi director.
Retains approved 1080x1920 V6 renderer/typography; new 46-shot shotlist and original score.
Museum public-domain data from The Metropolitan Museum of Art Open Access API.
"""
import json, os, sys, time, math, subprocess, hashlib, shutil
from pathlib import Path
from collections import defaultdict

import requests
import mido
from mido import Message, MidiFile, MidiTrack, MetaMessage, bpm2tempo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'modules'/'artvision'))
import director_cinema_v6 as director
from identita_visiva_v6 import signature,cover
from PIL import Image

OUT = ROOT/'output'/'piranesi-cinema-v6'
ASSETS = OUT/'assets'
IMAGES = ASSETS/'original_images'
DURATION=148
ARTIST='GIOVANNI BATTISTA PIRANESI'
COMPOSER='ARTVISION STUDIO'
USER_AGENT='ArtVision Cinema Educational Open Access Film (project source attribution available)'
MET='https://collectionapi.metmuseum.org/public/collection/v1/objects/'
# Original 18th-century Carceri prints; exact institutional accession IDs
WORKS=[
 ('The Pier with Chains',362799),
 ('The Staircase with Trophies',362676),
 ('The Well',362670),
 ('Prisoners on a Projecting Platform',362671),
 ('The Giant Wheel',362675),
 ('The Round Tower',337725),
 ('Title Page',362797),
 ('The Drawbridge',362672),
 ('The Arch with a Shell Ornament',362673),
 ('The Smoking Fire',362674),
 ('The Arch of the Great Staircase',362677),
 ('The Sawhorse',362678),
]
# Narrative sequence: into the void → human scale → machines → lost stairs → release.
# Coordinates specific to architectural motifs: vault junctions, bridges, steps,
# hanging chains, tiny human figures, vanishing axes. No universal stock motion loop.
BEATS=[
 (0,'Pier','portrait',(.51,.30),2.5,'Chains loom: instant first-frame mystery','cut'),
 (1,'Staircase','texture',(.54,.49),2.0,'Shaft of stairs—no exit','match'),
 (2,'Well','portrait',(.52,.43),2.3,'Stones widen around the camera','cut'),
 (3,'Pier','texture',(.32,.22),2.4,'Chains, the central visual question','cut'),
 (4,'Prisoners','texture',(.55,.68),2.7,'The human body dwarfed by a platform','dissolve'),
 (5,'Pier','whole',(.50,.50),3.1,'Reveal the impossible mass and structure','cut'),
 (6,'Tower','portrait',(.57,.32),3.1,'First cylindrical vertigo','match'),
 (7,'Staircase','portrait',(.48,.31),2.8,'The stairs appear to climb forever','cut'),
 (8,'Staircase','texture',(.32,.53),2.3,'Watch a small figure between masonry','cut'),
 (9,'Well','texture',(.66,.29),2.3,'The vault seems to fold into itself','cut'),
 (10,'Giant Wheel','portrait',(.45,.41),3.2,'Inhuman machinery enters','dissolve'),
 (11,'Prisoners','portrait',(.55,.35),2.6,'Balconies like a floating city','cut'),
 (12,'Tower','whole',(.50,.50),3.5,'Breath: the scale fully revealed','dissolve'),
 (13,'Title','portrait',(.52,.30),2.7,'The first doorway of the dream','cut'),
 (14,'Pier','portrait',(.69,.53),2.6,'Return to the suspended bridges','match'),
 (15,'Well','portrait',(.30,.64),2.8,'Staircase recedes below us','cut'),
 (16,'Prisoners','texture',(.34,.44),2.4,'Architectural weight and empty ledges','cut'),
 (17,'Staircase','whole',(.50,.50),3.3,'Entire system of impossible stairs','dissolve'),
 (18,'Giant Wheel','texture',(.50,.63),2.5,'Giant spokes overpower human movement','cut'),
 (19,'Pier','texture',(.63,.25),2.3,'Vertical weight, chains as bars','match'),
 (20,'Well','texture',(.48,.43),2.25,'Stone crossbars and central darkness','cut'),
 (21,'Tower','texture',(.50,.55),2.4,'A spiral is also a trap','cut'),
 (22,'Prisoners','whole',(.50,.50),3.25,'Emotional distance: small human lives','dissolve'),
 (23,'Staircase','portrait',(.49,.60),2.9,'Human ascent, no visible destination','cut'),
 (24,'Pier','portrait',(.37,.72),2.55,'Architectural echoes in the depths','match'),
 (25,'Tower','portrait',(.38,.44),2.75,'Convergence against the circle','cut'),
 (26,'Giant Wheel','whole',(.50,.50),3.4,"Reveal the wheel's dreadful scale",'dissolve'),
 (27,'Well','portrait',(.63,.55),2.6,'Low vantage, high vault','cut'),
 (28,'Prisoners','portrait',(.38,.69),2.8,'The unreachable platform','cut'),
 (29,'Pier','portrait',(.59,.41),2.55,'Chained pillar and vanishing light','match'),
 (30,'Staircase','texture',(.65,.26),2.35,'Routes multiply overhead','cut'),
 (31,'Title','whole',(.50,.50),3.3,'The graphic threshold pauses the score','dissolve'),
 (32,'Tower','portrait',(.52,.66),2.65,'Human scale against gigantic stones','cut'),
 (33,'Well','portrait',(.50,.22),2.6,'A higher arch suggests escape','cut'),
 (34,'Staircase','portrait',(.64,.52),2.65,'Final futile diagonal ascent','match'),
 (35,'Pier','texture',(.50,.47),2.45,'Chains again: a recurring motif','cut'),
 (36,'Giant Wheel','portrait',(.57,.28),2.65,'Machinery becomes abstract geometry','cut'),
 (37,'Prisoners','texture',(.51,.70),2.65,'Return to the first human silhouettes','dissolve'),
 (38,'Well','whole',(.50,.50),3.35,'Composition opens up, first relief','dissolve'),
 (39,'Staircase','portrait',(.49,.42),3.1,'Long ascending line and unresolved fate','cut'),
 (40,'Pier','portrait',(.46,.35),2.8,'Soft, ominous return to the opening space','match'),
 (41,'Tower','whole',(.50,.50),3.45,'The impossible tower understood as a whole','dissolve'),
 (42,'Prisoners','portrait',(.55,.52),2.75,'Human scale is restored','cut'),
 (43,'Pier','portrait',(.48,.46),2.85,'The chain motif falls into shadow','cut'),
 (44,'Staircase','whole',(.50,.50),4.1,'One final contemplative image','dissolve'),
 (45,'Pier','whole',(.50,.50),4.5,'Close the loop in silence and shadow','dissolve'),
]
KEYS={
 'Pier':'The Pier with Chains',
 'Staircase':'The Staircase with Trophies',
 'Well':'The Well',
 'Prisoners':'Prisoners on a Projecting Platform',
 'Giant Wheel':'The Giant Wheel',
 'Tower':'The Round Tower',
 'Title':'Title Page',
}
def sh(cmd):
 print('COMMAND', ' '.join(map(str,cmd))[:400],flush=True)
 subprocess.run(list(map(str,cmd)),check=True)

def fetch_json(url,tries=3):
 for n in range(tries):
  try:
   r=requests.get(url,headers={'User-Agent':USER_AGENT},timeout=35)
   r.raise_for_status();return r.json()
  except Exception as e:
   print('API retry',n,str(e)[:180],flush=True);time.sleep(2*(n+1))
 return None

def download_images():
 IMAGES.mkdir(parents=True,exist_ok=True)
 entries=[]
 for alias,objid in WORKS:
  data=fetch_json(MET+str(objid))
  if not data:continue
  if data.get('artistDisplayName') and 'Piranesi' not in data.get('artistDisplayName',''):
   print('Reject incorrect artist',objid);continue
  if data.get('isPublicDomain') is not True:
   print('Reject not explicitly public domain',objid);continue
  urls=[u for u in [data.get('primaryImage'),data.get('primaryImageSmall')]+data.get('additionalImages',[]) if isinstance(u,str) and u.startswith('https://')]
  if not urls:continue
  p=IMAGES/(str(objid)+'.jpg')
  success=False
  for u in urls[:3]:
   try:
    r=requests.get(u,timeout=60,headers={'User-Agent':USER_AGENT});r.raise_for_status()
    if len(r.content)<100_000:continue
    p.write_bytes(r.content)
    with Image.open(p) as im:
     im.verify()
    with Image.open(p) as im:
     w,h=im.size
    if min(w,h)<1100:continue
    success=True;break
   except Exception as e:
    print('Image issue',str(objid),str(e)[:160],flush=True)
  if success:
   record={'id':str(objid),'source':'Met_Open_Access','file':p.name,'title':alias,
    'museum_title':data.get('title'),'artist':data.get('artistDisplayName'),
    'object_url':data.get('objectURL'),'image_url':u,'rights':'The Metropolitan Museum of Art — Open Access / CC0, public domain',
    'size':[w,h],'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
   entries.append(record);print('ASSET OK',alias,w,h,flush=True)
  if len(entries)>=10:break
 (ASSETS/'artworks.json').write_text(json.dumps({'metadata':entries},indent=2,ensure_ascii=False))
 if len(entries)<6:raise RuntimeError('Only '+str(len(entries))+' verified museum artworks. Never fill with invented images.')
 for k,v in KEYS.items():
  if v not in {x['title'] for x in entries}:
   raise RuntimeError('The core Piranesi picture is missing: '+v)
 return entries

def music_midi():
 ASSETS.mkdir(parents=True,exist_ok=True)
 mid=MidiFile(ticks_per_beat=480)
 tempo=bpm2tempo(77)
 def track(name,ch,program,volume):
  t=MidiTrack();mid.tracks.append(t);t.append(MetaMessage('track_name',name=name,time=0))
  if ch!=9:t.append(Message('program_change',program=program,channel=ch,time=0))
  t.append(Message('control_change',channel=ch,control=7,value=volume,time=0));return t
 lead=track('Viola - unanswered question',0,48,72)
 bass=track('Cello and low strings',1,42,90)
 harp=track('Harp - suspended staircases',2,46,65)
 choir=track('Human shadows',3,52,64)
 bell=track('Distant music box',4,10,58)
 drum=track('Subtle cinematic percussion',9,0,57)
 events=defaultdict(list)
 def note(tr,ch,pitch,vel,start,beats):
  a=max(0,round(start*480));b=max(a+1,round((start+beats)*480))
  events[id(tr)].append((a,1,Message('note_on',channel=ch,note=pitch,velocity=max(1,min(127,int(vel))),time=0)))
  events[id(tr)].append((b,0,Message('note_off',channel=ch,note=pitch,velocity=0,time=0)))
 chords=[
  [40,47,52,55,59], # Em
  [36,43,48,52,55], # Cm (foreign borrowed chord)
  [38,45,50,54,57], # D major
  [35,42,47,50,54], # Bm
  [40,47,52,55,59], # Em
  [36,43,48,52,55], # Cm
  [33,40,45,48,52], # Am
  [35,42,47,51,54], # B7
 ]
 for bar in range(49):
  start=bar*4;chord=chords[bar%len(chords)]
  section=(bar//12)
  intensity=[.68,.84,1.0,.72,.45][min(section,4)]
  v=int(50*intensity)
  for j in range(3):
   note(bass,1,chord[0]+(12 if j==2 and bar%2 else 0),50*intensity,start+j*1.35,1.45)
  notes=[chord[1]+12,chord[2]+12,chord[3]+12,chord[4]+12]
  path=[0,1,2,1,3,2,1,0]
  for k,n in enumerate(path):
   note(harp,2,notes[n],int((42 if k%4 else 51)*intensity),start+.5*k,.45)
  for q in [0,2]:
   note(choir,3,chord[2]+12,24*intensity,start+q*2,2.25)
  if bar>=4:
   notes2=[chord[3]+12,chord[4]+12,chord[2]+24]
   motif=[notes2[0],notes2[1],notes2[2],notes2[1]]
   for idx,p in enumerate(motif):
    note(lead,0,p,int(40*intensity),start+idx,.88)
  if bar%4==0 and bar>=8:note(bell,4,chord[4]+24,26*intensity,start+.3,2.8)
  if bar>=12 and bar<45 and bar%2==0:
   note(drum,9,36,42*intensity,start,.16)
  if bar in (12,20,28,36):note(drum,9,41,58*intensity,start,.27)
 for tr in mid.tracks:
  if id(tr) not in events:continue
  last=0
  for at,priority,msg in sorted(events[id(tr)],key=lambda x:(x[0],x[1])):
   msg.time=at-last;tr.append(msg);last=at
 mid.tracks[0].insert(1,MetaMessage('set_tempo',tempo=tempo,time=0))
 mid_path=ASSETS/'ORIGINAL_SCORE_PIRANESI.mid';mid.save(mid_path)
 sf2=next((p for p in ['/usr/share/sounds/sf2/FluidR3_GM.sf2','/usr/share/sounds/sf2/TimGM6mb.sf2'] if Path(p).is_file()),None)
 if not sf2:raise RuntimeError('No trusted local General MIDI soundfont')
 wav=ASSETS/'piranesi_original_score.wav'
 sh(['fluidsynth','-ni','-F',wav,'-r','48000',sf2,mid_path])
 mp3=ASSETS/'licensed_piano_music.mp3'
 sh(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',wav,
  '-af','highpass=f=35,lowpass=f=11000,aecho=0.7:0.45:70|140:0.15|0.1,alimiter=limit=0.84',
  '-t',str(DURATION),'-c:a','libmp3lame','-q:a','3',mp3])
 (ASSETS/'music_rights.json').write_text(json.dumps({
  'type':'original','composer':'ArtVision Studio — original MIDI score for Piranesi',
  'composition':'new original score generated from code in scripts/artvision_piranesi_20261022.py',
  'recording':'locally synthesized instrumental using FluidSynth with system-distributed SF2 soundfont',
  'license_note':'Before third-party commercialization verify the specific downloaded soundfont license; this music has not been published or cleared by platform',
  'midi':str(mid_path.relative_to(OUT)), 'duration':DURATION},indent=2))
 return mp3

def build_story(entries):
 found={x['title'] for x in entries}
 story=[]
 for _,key,mode,focus,seconds,why,join in BEATS:
  title=KEYS[key]
  if title not in found:continue
  story.append((title,mode,focus,seconds,why,join))
 if len(story)<40:raise RuntimeError('Not enough bespoke storyboard shots')
 return story

def run():
 OUT.mkdir(parents=True,exist_ok=True)
 print('PIRANESI NEW FILM starting',flush=True)
 entries=download_images()
 score=music_midi()
 director.STORY=build_story(entries)
 director.label_title=lambda frame,t:signature(frame,t,ARTIST,COMPOSER)
 director.MUSIC_BY='MUSIC BY '+COMPOSER
 loaded=director.load_artworks(ASSETS)
 shots=director.resolve_items(loaded,DURATION)
 mp4,log=director.render(shots,ASSETS,OUT,DURATION)
 # Soundfont tracks render at a deliberately quiet pre-master level.
 # Always master to a proper listening level before export; preserve video without re-encoding.
 normalized=OUT/'_normalized_mix.mp4'
 sh(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',mp4,
   '-map','0:v:0','-map','0:a:0','-c:v','copy',
   '-af','loudnorm=I=-16:LRA=9:TP=-2','-c:a','aac','-b:a','192k',
   '-movflags','+faststart',normalized])
 normalized.replace(mp4)
 named=OUT/'ARTVISION_PIRANESI_CARCERI_CINEMA_V6.mp4'
 mp4.rename(named)
 # cover extracted from actual frame, same immutable Cinema V6 title band
 import cv2
 cap=cv2.VideoCapture(str(named));cap.set(cv2.CAP_PROP_POS_MSEC,900)
 ret,frame=cap.read();cap.release()
 if not ret:raise RuntimeError('Cannot read rendered opening frame')
 cv2.imwrite(str(OUT/'COPERTINA_PIRANESI_CINEMA_V6.jpg'),cover(frame,ARTIST,COMPOSER),[int(cv2.IMWRITE_JPEG_QUALITY),93])
 probe=subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_name,codec_type,width,height,r_frame_rate','-of','json',str(named)])
 qa=json.loads(probe);streams=qa.get('streams',[])
 assert any(x.get('codec_type')=='video' and x.get('width')==1080 and x.get('height')==1920 for x in streams),qa
 assert any(x.get('codec_type')=='audio' for x in streams),qa
 assert abs(float(qa['format']['duration'])-DURATION)<2,qa
 checksum=hashlib.sha256(named.read_bytes()).hexdigest()
 (OUT/'DELIVERY_QA.json').write_text(json.dumps({'status':'rendered_needs_artistic_review','duration':DURATION,
  'sha256':checksum,'frame_count_expected':DURATION*24,'unique_artworks':len(entries),
  'directed_shots':len(log),'institutional_license': 'Met Museum Open Access / CC0',
  'fonts':'Immutable ArtVision Cinema V6 signature via identita_visiva_v6.py',
  'soundtrack':'Original MIDI composition synthesized by FluidSynth; final loudness normalized to -16 LUFS target; FluidR3 soundfont MIT license attribution for distribution',
  'ffprobe':qa},indent=2,ensure_ascii=False))
 caption=('PIRANESI, LE PRIGIONI CHE NON ESISTONO\n\n'
  'Scale che portano nel vuoto. Arcate gigantesche. Figure minuscole in architetture senza uscita. '
  'Nel Settecento Giovanni Battista Piranesi immaginò le Carceri d’invenzione: non luoghi reali, '
  'ma visioni incise nel metallo e nella memoria. Qui le attraversiamo attraverso dettagli e prospettive, '
  'lasciando che l’immagine racconti l’inquietudine.\n\n'
  'Opere originali: Giovanni Battista Piranesi, Carceri d’invenzione, ca. 1749–1761. '
  'Immagini: The Metropolitan Museum of Art, Open Access / Public Domain (fonti e accession ID nel file artworks.json). '
  'Musica: colonna sonora originale ArtVision Studio, sintetizzata da composizione MIDI originale.\n'
  '#Piranesi #StoriaDellArte #Arte')
 (OUT/'POST_FACEBOOK.txt').write_text(caption,encoding='utf-8')
 print('FINISHED',named,'sha256',checksum,'size',named.stat().st_size,flush=True)
if __name__=='__main__':run()
