#!/usr/bin/env python3
"""ArtVision CINEMA V6 add-on: second batch of five DISTINCT artists.
Curated iconic openings; Commons licensed images + provenance, then thematic V6 edits.
No alteration to existing V6 Gold Master or old workflows. No paid APIs.
"""
from __future__ import annotations
import argparse, hashlib, html, io, json, re, subprocess, sys, time, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image, ImageOps
import cv2
import numpy as np
from export_caravaggio_v6 import valid_license
from atelier_v4 import audio_download, TRACKS
import director_cinema_v6 as cinema
from identita_visiva_v6 import signature, cover
from batch3_cinema_v6 import detail_foci, check_movie
ROOT=Path("output/artvision-batch5-cinema")
UA="ArtVisionTraLePagine/3.0 (genuine artist research; public-domain/CC-BY; GitHub GGIANLUCAA/Tra-le-pagine-)"
LICENSE_URL="https://creativecommons.org/licenses/by/4.0/"
P={
 "klimt":{
  "name":"Gustav Klimt","duration":119,"hero":"Klimt - The Kiss.jpg",
  "key":["the kiss","judith","adele bloch","hope","tree of life","woman in gold","water serpents","danae","beethoven frieze","portrait","golden","the virgin"],
  "find":["Gustav Klimt painting","Klimt Google Art Project","Gustav Klimt portrait"],
  "act":["Gold and the kiss","Women and symbolic gestures","Ornament like living skin","Faces, hope and mystery","A golden return"],"track":"dreams_become_real"},
 "vermeer":{
  "name":"Johannes Vermeer","duration":110,"hero":"1665 Girl with a Pearl Earring.jpg",
  "key":["girl with a pearl earring","milkmaid","the art of painting","woman holding a balance","view of delft","astronomer","geographer","girl reading","music lesson","woman in blue","woman with a lute"],
  "find":["Johannes Vermeer painting","Johannes Vermeer Google Art Project","Vermeer Mauritshuis Rijksmuseum"],
  "act":["A glance in silence","Window light and domestic life","Hands that pour and write","The blue and yellow rooms","Return to the pearl"],"track":"evening_fall_piano"},
 "bosch":{
  "name":"Hieronymus Bosch","duration":132,"hero":"The Garden of Earthly Delights by Hieronymus Bosch.jpg",
  "key":["garden of earthly delights","temptation of st anthony","last judgement","haywain","ship of fools","christ carrying the cross","hell","conjurer","extraction of stone","adoration","hermit saint"],
  "find":["Hieronymus Bosch Temptation Saint Anthony","Hieronymus Bosch The Haywain","Hieronymus Bosch Last Judgment","Hieronymus Bosch Ship of Fools","Hieronymus Bosch Triptych painting","Hieronymus Bosch Garden Delights"],
  "act":["First sight of an impossible world","Earthly abundance and temptation","Animals, objects and enigmas","Hellfire and grotesque faces","The garden returns"],"track":"darkest_child"},
 "botticelli":{
  "name":"Sandro Botticelli","duration":125,"hero":"Nascita di Venere Botticelli.jpg","featured":["Primavera (Botticelli).jpg"],
  "key":["birth of venus","nascita di venere","primavera","venus and mars","portrait of a young woman","madonna of the magnificat","adoration of the magi","venus","annunciation","minerva and the centaur","portrait"],
  "find":["Sandro Botticelli Venus and Mars","Sandro Botticelli Madonna","Sandro Botticelli Adoration of the Magi","Sandro Botticelli Annunciation","Sandro Botticelli Portrait","Botticelli Primavera Birth of Venus"],
  "act":["Birth of an icon","The grace of a human face","Spring, flowers and myth","Movement in delicate lines","Venus comes back"],"track":"calmant"},
 "mucha":{
  "name":"Alphonse Mucha","duration":113,"hero":"Alphonse Mucha - Zodiac.jpg",
  "key":["zodiac","four seasons","spring","summer","autumn","winter","job","gismonda","chocolat","champagne","flowers","reverie","morning","evening"],
  "find":["Alphonse Mucha lithograph","Alphonse Mucha posters","Alphonse Mucha seasons"],
  "act":["An ornamental face fills the canvas","Hair, flowers and circular motifs","The female figure and typography","A gallery of the seasons","Zodiac returns"],"track":"night_on_the_docks_piano"},
}
# Verified in the project for four; fifth has two public official fallbacks.
SOUND={
 "dreams_become_real":{"title":"Dreams Become Real","author":"Kevin MacLeod","page":"https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1500027","urls":["https://incompetech.com/music/royalty-free/mp3-royaltyfree/Dreams%20Become%20Real.mp3"],"license":"CC BY 4.0","license_url":LICENSE_URL,"expected_seconds":410,"instrumental":True},
 "darkest_child":{"title":"Darkest Child","author":"Kevin MacLeod","page":"https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100783","urls":["https://incompetech.com/music/royalty-free/mp3-royaltyfree/Darkest%20Child.mp3"],"license":"CC BY 4.0","license_url":LICENSE_URL,"expected_seconds":239,"instrumental":True},
 "calmant":TRACKS["calmant"],
 "evening_fall_piano":TRACKS["evening_fall_piano"],
 "night_on_the_docks_piano":{"title":"Night on the Docks - Piano","author":"Kevin MacLeod","page":"https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100135","urls":["https://incompetech.com/music/royalty-free/mp3-royaltyfree/Night%20on%20the%20Docks%20-%20Piano.mp3"],"license":"CC BY 4.0","license_url":LICENSE_URL,"expected_seconds":174,"instrumental":True},
}
COMMONS="https://commons.wikimedia.org/w/api.php?"
def get(url,timeout=19,size=6_000_000):
 last=None
 for attempt in range(2):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"image/jpeg,image/png,application/json,*/*"})
   with urllib.request.urlopen(req,timeout=timeout) as r:
    data=r.read(size+1)
    if len(data)>size:raise RuntimeError("large file")
    return data
  except Exception as e:
   last=e;time.sleep(1.2*(attempt+1))
 raise RuntimeError(str(last)[:200])
def api(params):
 q=COMMONS+urllib.parse.urlencode({"action":"query","format":"json","formatversion":2,**params})
 return json.loads(get(q,timeout=26,size=7_000_000))
def rawclean(value):
 if isinstance(value,dict):value=value.get("value","")
 return re.sub(r"<[^>]+>"," ",html.unescape(str(value))).strip()
def info_file(name,width=2500):
 doc=api({"titles":"File:"+name,"prop":"imageinfo","iiprop":"url|size|extmetadata","iiurlwidth":width})
 arr=doc.get("query",{}).get("pages") or []
 if not arr or "imageinfo" not in arr[0]:raise RuntimeError("not found")
 return arr[0]["imageinfo"][0]
def discover(profile):
 found=[]
 for term in profile["find"]:
  try:
   doc=api({"generator":"search","gsrsearch":term+" filetype:bitmap","gsrnamespace":6,"gsrlimit":45,
      "prop":"imageinfo","iiprop":"url|size|extmetadata","iiurlwidth":2500})
   for page in doc.get("query",{}).get("pages",[]):
    if page.get("title","").startswith("File:") and page.get("imageinfo"):
     found.append((page["title"][5:],page["imageinfo"][0]))
  except Exception as e:print("SEARCH fallback",term,str(e)[:120],flush=True)
 return found
def priority(fn,cfg,hero=False):
 title=html.unescape(fn).lower()
 p=1000 if hero else 0
 for i,k in enumerate(cfg["key"]):
  if k.lower() in title:p+=max(12,90-6*i)
 if "google art project" in title:p+=18
 if "wga" in title:p+=5
 if any(k in title for k in ["after "," copy ","reproduction by ","portrait of "+cfg["name"].lower(),"statue","photograph","museum interior","restoration","detail of","frame","tracing","book cover"]):p-=95
 if "thumbnail" in title or "crop" in title:p-=35
 return p
def suitable_filename(fn,slug):
 lower=fn.lower()
 if not any(lower.endswith(x) for x in (".jpg",".jpeg",".png",".webp",".tif",".tiff")):return False
 excluded=[".svg","sculpture","wooden frame","statue","portrait of artist by","artwork on wall","cover.jpg","engraving after","sketchbook page"]
 if any(s in lower for s in excluded):return False
 person={"klimt":["klimt"],"vermeer":["vermeer","meer"],"bosch":["bosch"],"botticelli":["botticelli"],"mucha":["mucha"]}[slug]
 return any(s in lower for s in person)
def sources(slug,cfg,folder):
 dst=folder/"original_images";dst.mkdir(parents=True,exist_ok=True)
 found=[(cfg["hero"],None)]+[(p,None) for p in cfg.get("featured",[])]
 try:found+=discover(cfg)
 except Exception as e:print("DISCOVERY unavailable",str(e),flush=True)
 cache=set();candidates=[]
 for name,info in found:
  if name in cache:continue
  cache.add(name)
  if name==cfg["hero"] or name in cfg.get("featured",[]) or suitable_filename(name,slug):candidates.append((name,info))
 candidates.sort(key=lambda x:priority(x[0],cfg,hero=(x[0]==cfg["hero"] or x[0] in cfg.get("featured",[]))),reverse=True)
 if not candidates:raise RuntimeError("No verifiable Commons candidates")
 works=[];errors=[];seen_titles=set();motif_counts={}
 def motif_of(fn):
  title=fn.lower().replace("_"," ").replace("-"," ")
  # A museum image of the same painting may have many filenames / photographers.
  for k in cfg["key"]:
   if k.lower() in title:return k.lower()
  return re.sub(r"[^a-z0-9]","",title.replace(cfg["name"].lower(),"").replace("google art project",""))[:60]
 for fn,info in candidates[:115]:
  if len(works)>=16:break
  try:
   motif=motif_of(fn)
   limit=1 if slug=="vermeer" else (3 if slug=="bosch" else 2)
   if motif_counts.get(motif,0)>=limit:continue
   if info is None:info=info_file(fn)
   if not valid_license(info):raise RuntimeError("license unverified or commercial restriction")
   ext=info.get("extmetadata",{})
   attribution=rawclean(ext.get("Artist"))
   if attribution and slug not in ("bosch",) and cfg["name"].split()[-1].lower() not in attribution.lower() and "mucha" not in attribution.lower() and "botticelli" not in attribution.lower():
    raise RuntimeError("Artist attribution conflict: "+attribution[:50])
   image_url=info.get("thumburl") or info.get("url")
   try:raw=get(image_url,timeout=25,size=27_000_000)
   except Exception:
    inf=info_file(fn,width=1700);image_url=inf.get("thumburl") or inf.get("url")
    raw=get(image_url,timeout=18,size=22_000_000)
   with Image.open(io.BytesIO(raw)) as orig:
    orig.load();im=ImageOps.exif_transpose(orig).convert("RGB")
   if min(im.size)<640:raise RuntimeError("image too small")
   if max(im.size)>3700:im.thumbnail((3700,3700),Image.Resampling.LANCZOS)
   ident=hashlib.sha256(fn.encode()).hexdigest()[:17]
   path=dst/(ident+".jpg");im.save(path,quality=93,subsampling=0,optimize=True)
   title=re.sub(r"[-_]"," ",fn.rsplit(".",1)[0]).strip()
   title=re.sub(r"\bGoogle Art Project\b","",title,flags=re.I).strip(" -")
   title=title[:170]
   # Avoid exact duplicates when the gallery query gives the same Commons file.
   key=re.sub(r"[^a-z0-9]","",title.lower())
   if key in seen_titles:continue
   seen_titles.add(key)
   motif_counts[motif]=motif_counts.get(motif,0)+1
   rec={"id":ident,"title":title,"artist":cfg["name"],"source":"Wikimedia Commons - licensed image file",
       "url":"https://commons.wikimedia.org/wiki/File:"+urllib.parse.quote(fn.replace(" ","_")),
       "original_file":fn,"license":rawclean(ext.get("LicenseShortName")),
       "license_url":rawclean(ext.get("LicenseUrl")),"attribution":rawclean(ext.get("Attribution"))[:1200],
       "artist_metadata":attribution[:500],"image_url":image_url,
       "file":str(path),"width":im.width,"height":im.height,
       "sha256":hashlib.sha256(path.read_bytes()).hexdigest()}
   works.append(rec);print("ACCEPT",slug,len(works),title,im.size,flush=True)
  except Exception as e:
   errors.append({"file":fn,"error":str(e)[:140]})
  time.sleep(.35)
 if len(works)<9:
  raise RuntimeError(f"{slug} has only {len(works)} verifiable original images, 9 needed. Errors: {errors[:7]}")
 return works,errors
def artwork_sequence(works,cfg):
 # A visual story: the icon returns at the end, not a uniform alphabetical gallery.
 first=works[0]
 order=[first]+works[1:]
 if len(order)>14:order=order[:14]
 # 5 movements mix rather than group by source date/filename.
 return order+[order[2],first]
def directed_shots(works,cfg,slug):
 seq=artwork_sequence(works,cfg)
 shots=[]
 for i,w in enumerate(seq):
  a,b=detail_foci(w["file"])
  # Director's grammar: opening closeup, contextual whole and detail; alternating
  # combinations build shifts in texture and contrast with no identical three-beat pattern.
  patterns=[
   [("portrait",a),("texture",b),("whole",(.5,.5))],
   [("whole",(.5,.5)),("glide",a),("texture",b)],
   [("portrait",b),("whole",(.5,.5))],
   [("texture",a),("portrait",b),("whole",(.5,.5))],
   [("whole",(.5,.5)),("portrait",a)],
   [("glide",a),("texture",b),("portrait",a)],
  ]
  modes=patterns[i%len(patterns)]
  if i==0:modes=[("portrait",a),("texture",b),("whole",(.5,.5))]
  if i==len(seq)-1:modes=[("portrait",a),("whole",(.5,.5))]
  for k,(kind,f) in enumerate(modes):
   act=min(4,int(5*i/max(len(seq),1)))
   why=f"{cfg['act'][act]} — {w['title']}, {kind}, real photographic image."
   trans="dissolve" if kind=="whole" and k==0 else ("match" if k==1 and i%2==0 else "cut")
   weight=3.15 if kind=="whole" else (2.6 if kind=="portrait" else 2.15)
   if i==len(seq)-1 and k==len(modes)-1:weight=3.9
   shots.append(cinema.Shot(len(shots),w,kind,f,weight,why,trans))
 if len(shots)<27:raise RuntimeError("Insufficient cinematic decisions")
 factor=cfg["duration"]/sum(s.duration for s in shots)
 for sh in shots:sh.duration*=factor
 return shots

def make(slug):
 if slug not in P:raise ValueError(slug)
 cfg=P[slug];artist=cfg["name"];secs=cfg["duration"]
 folder=ROOT/slug/"sources";folder.mkdir(parents=True,exist_ok=True)
 out=ROOT/slug/"film";out.mkdir(parents=True,exist_ok=True)
 works,fail=sources(slug,cfg,folder)
 music=SOUND[cfg["track"]]
 try:mp3,proof=audio_download(music,folder,secs)
 except Exception as e:
  if slug=="mucha":
   print("TRACK UNAVAILABLE, fallback from licensed library",str(e),flush=True)
   music={"title":"Music for Manatees","author":"Kevin MacLeod","page":"https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1400009",
   "urls":["https://incompetech.com/music/royalty-free/mp3-royaltyfree/Music%20for%20Manatees.mp3"],
   "license":"CC BY 4.0","license_url":LICENSE_URL,"expected_seconds":1056,"instrumental":True}
   mp3,proof=audio_download(music,folder,secs)
  else:raise
 mp3.replace(folder/"licensed_piano_music.mp3")
 (folder/"music_rights.json").write_text(json.dumps(proof,indent=2,ensure_ascii=False),encoding="utf-8")
 (folder/"artworks.json").write_text(json.dumps({"artist":artist,"metadata":works,"failed":fail,"publish":False},indent=2,ensure_ascii=False),encoding="utf-8")
 shots=directed_shots(works,cfg,slug)
 cinema.label_title=lambda img,t:signature(img,t,artist,music["author"])
 original,timeline=cinema.render(shots,folder,out,duration=secs)
 finished=out/("ARTVISION_"+slug.upper()+"_CINEMA_V6.mp4")
 original.replace(finished)
 old=out/"COPERTINA_CINEMA_V6.jpg"
 old.unlink(missing_ok=True)
 # Lock the identical identity from approved Van Gogh / Caravaggio without modifying module.
 hero=cv2.imread(works[0]["file"])
 frame=cinema.compute(hero,shots[0].focus,1.12)
 cv2.imwrite(str(out/"COPERTINA.jpg"),cover(frame,artist,music["author"]),[int(cv2.IMWRITE_JPEG_QUALITY),95])
 spec=check_movie(finished,secs)
 (out/"silent_v6.mp4").unlink(missing_ok=True)
 credits=[artist+" — ArtVision Cinema V6",f"Music: {music['title']} — {music['author']}",
   f"Music page: {music['page']}","CC BY 4.0: "+LICENSE_URL,
   "Music edited (excerpt / fades / volume). Include full credits when posting.",
   "Before commercial publication verify all source and cultural heritage reuse restrictions.","",
   "WORKS — IMAGES — REUSE TERMS:"]
 credits += [f"{a['title']} — {a['url']} — {a['license']} — {a['attribution']}" for a in works]
 (out/"DESCRIZIONE_E_CREDITI.txt").write_text("\n".join(credits)+"\n",encoding="utf8")
 (out/"FONTI_E_DIRITTI.json").write_text(json.dumps({"artist":artist,"works":works,"music":proof,
   "publication_approved":False,"note":"Review artist attributions, Commons photographer credits and country-specific restrictions."},indent=2,ensure_ascii=False),encoding="utf8")
 (out/"REPORT.json").write_text(json.dumps({"artist":artist,"duration":secs,"original_works":len(works),"shots":len(shots),
    "music":music["title"],"regia":"Cinema V6 adapted by artwork","opening_brand":"IDENTITA_VISIVA_FISSA_V6",
    "technical":spec,"paid_api":False,"published":False},indent=2,ensure_ascii=False),encoding="utf8")
 print("BATCH5 COMPLETE",slug,secs,"seconds",len(works),"works",len(shots),"shots",flush=True)
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--artist",required=True,choices=sorted(P))
 a=p.parse_args();make(a.artist)
