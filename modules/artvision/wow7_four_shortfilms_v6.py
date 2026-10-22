#!/usr/bin/env python3
"""ArtVision WOW7: four standalone 9:16 museum short films, full fidelity originals.
New editable source: keeps Cinema V6 Gold Master and earlier artist films untouched.
Images must have documented CC0/Public Domain reuse; no generated substitutes.
Creative direction: V21 + V22 fixed camera/slow one-way micro push, not oscillation.
"""
from pathlib import Path
from PIL import Image, ImageOps
import argparse,hashlib,io,json,sys,time,urllib.parse,unicodedata
import batch5_cinema_v6 as studio
import director_cinema_v6 as camera

ROOT=Path("output/artvision-wow7")
studio.ROOT=ROOT
studio.P.clear()
MOVIES={
 "aivazovsky":{
  "name":"Ivan Aivazovsky","title":"La forza dell'oceano","duration":50,
  "track":"the_descent","hero":"ninth",
  "opening":"Una gigantesca onda sta per inghiottire i superstiti.",
  "resolution":"I mari di Ivan Aivazovsky alternano tempesta, naufragio e chiarore lunare.",
  "original":"Una storia visiva sul mare: minaccia, lotta, sopravvivenza e infine silenzio.",
  "works":{
   "ninth":"Aivazovsky, Ivan - The Ninth Wave.jpg",
   "breaking":"Breaking Wave (by Ivan Aivazovsky).jpg",
   "abandoning":"Ivan Konstantinovich Aivazovsky - Abandoning Ship.jpg",
   "storm":"Storm over the Black Sea by Aivazovsky, 1893.png",
   "naval":"Aivazovsky, Brig Mercury Attacked by Two Turkish Ships 1892.jpg",
   "moon":"Ivan Konstantinovich Aivazovsky - Passing Ship on a Moonlit Night.jpg",
   "calm":"Ivan Aivazovsky - Sailing Ships on a Calm Day - 1887.png",
   "shipwreck":"Ivan Konstantinovich Aivazovsky - Shipwreck off the Black Sea Coast.jpg"
  },
  "acts":[
   ("ninth","texture",(.56,.53),3.1,"La nona onda: spuma e luce sul punto di rottura"),
   ("ninth","portrait",(.43,.72),3.0,"I sopravvissuti sulla scena del naufragio"),
   ("ninth","whole",(.5,.5),2.6,"Rivelazione della Nona onda"),
   ("breaking","portrait",(.55,.52),3.1,"Una seconda onda travolge il quadro"),
   ("breaking","whole",(.5,.5),2.3,"Le proporzioni del mare"),
   ("abandoning","texture",(.51,.68),2.6,"Una barca precaria al centro della tempesta"),
   ("abandoning","whole",(.5,.5),2.5,"Gli uomini contro l'oceano"),
   ("storm","portrait",(.5,.42),3.1,"Il cielo preannuncia il temporale"),
   ("storm","whole",(.5,.5),2.4,"La tempesta domina tutto"),
   ("naval","portrait",(.42,.53),2.9,"Navi contro il mare"),
   ("naval","whole",(.5,.5),2.4,"Battaglia e movimento"),
   ("shipwreck","portrait",(.67,.55),2.7,"La costa del naufragio"),
   ("shipwreck","whole",(.5,.5),2.4,"La scala del pericolo"),
   ("moon","texture",(.55,.38),3.0,"Il chiarore lunare interrompe la tensione"),
   ("moon","whole",(.5,.5),3.2,"Respirare dopo la tempesta"),
   ("calm","portrait",(.46,.54),3.2,"Il mare torna immobile"),
   ("calm","whole",(.5,.5),4.8,"Finale di quiete, nessun colpo di scena artificiale")
  ]},
 "blake":{
  "name":"William Blake","title":"Visioni oltre il velo","duration":59,
  "track":"dreams_become_real","hero":"whirlwind",
  "opening":"Una figura appare dal vortice, nel buio di un universo inciso.",
  "resolution":"William Blake trasformò il Libro di Giobbe e altri temi spirituali in immagini potenti e visionarie.",
  "original":"Dall'apparizione cosmica alla fragilità umana: incisioni autentiche senza invenzioni digitali.",
  "museum":"William Blake",
  "search":[
   ("whirlwind","The Book of Job:  Pl. 13, Then the Lord answered Job out of the Whirlwind"),
   ("dreams","The Book of Job:  Pl. 11, With Dreams upon my bed"),
   ("judgment","The Book of Job:  Pl. 16, Thou hast fulfilled the Judgment of the Wicked"),
   ("fear","Sketch for \"The Thought of Death alone, the Fear Destroys\""),
   ("justice","The Book of Job:  Pl. 10, The Just Upright Man is laughed to scorn"),
   ("family","The Holy Family (Christ in the Lap of Truth)"),
   ("saint","St. Matthew"),
   ("tree","The Pastorals of Virgil, Eclogue I:  The Blasted Tree"),
   ("wolf","The Pastorals of Virgil, Eclogue I:  The Shepherd Chases away a Wolf")
  ],
  "acts":[
   ("whirlwind","texture",(.52,.35),3.2,"Una figura nel vortice celeste"),
   ("whirlwind","portrait",(.50,.56),3.0,"Il corpo piccolo sotto la visione"),
   ("whirlwind","whole",(.5,.5),2.8,"Il vortice rivelato"),
   ("dreams","texture",(.55,.30),3.0,"I simboli dell'incubo"),
   ("dreams","whole",(.5,.5),2.6,"Un sogno inciso a pieno quadro"),
   ("fear","portrait",(.45,.45),3.1,"Il pensiero della morte"),
   ("fear","whole",(.5,.5),2.6,"La figura e lo spazio"),
   ("judgment","texture",(.52,.40),3.0,"Il giudizio e i simboli"),
   ("judgment","portrait",(.57,.72),2.8,"L'uomo dentro la visione"),
   ("judgment","whole",(.5,.5),2.8,"La forza della tavola"),
   ("justice","portrait",(.52,.40),3.2,"Un innocente di fronte agli altri"),
   ("justice","whole",(.5,.5),2.5,"La scena del giudizio umano"),
   ("tree","portrait",(.5,.47),3.0,"Un albero spezzato"),
   ("tree","whole",(.5,.5),2.7,"Il paesaggio simbolico"),
   ("saint","portrait",(.53,.30),3.1,"Uno sguardo rivolto oltre il quadro"),
   ("saint","whole",(.5,.5),2.6,"La composizione del santo"),
   ("family","portrait",(.48,.40),3.4,"Il gesto umano come conclusione"),
   ("family","whole",(.5,.5),4.1,"Ritorno dalla visione alla quiete")
  ]},
 "dore":{
  "name":"Gustave Doré","title":"Il mondo delle ombre","duration":65,
  "track":"evening_fall_piano","hero":"ice",
  "opening":"Il ghiaccio si spezza in una scena dalle proporzioni immense.",
  "resolution":"Le immagini di Gustave Doré passano dai paesaggi drammatici alle storie letterarie e ai personaggi.",
  "original":"Un viaggio nel chiaroscuro di Doré: natura, personaggi e immaginazione senza collage estranei.",
  "museum":"Gustave Doré",
  "search":[
   ("ice","The Breaking Ice, Souvenir of Norway"),
   ("liberty","Liberty"),
   ("sancho","Sancho Panza"),
   ("wolf","Sketch for \"The Wolf Turned Shepherd\" (recto)"),
   ("valence","Young Woman from Valence"),
   ("street","Street Scene (recto)"),
   ("officer","Sardinian Officer"),
   ("hunt","Sketch of Hunting Scene (verso)")
  ],
  "acts":[
   ("ice","texture",(.55,.48),3.4,"Acqua, ghiaccio e un dettaglio inaspettato"),
   ("ice","portrait",(.35,.42),3.0,"La scala della natura"),
   ("ice","whole",(.5,.5),2.8,"Rivelazione della distesa ghiacciata"),
   ("liberty","texture",(.46,.33),3.0,"Le linee nervose della stampa"),
   ("liberty","whole",(.5,.5),2.8,"La figura e il gesto"),
   ("officer","portrait",(.49,.42),3.0,"Un ritratto di soldato tra ombra e luce"),
   ("officer","whole",(.5,.5),2.8,"Il disegno della figura nella sua interezza"),
   ("sancho","portrait",(.49,.35),3.0,"Un personaggio osservato da vicino"),
   ("sancho","whole",(.5,.5),2.8,"Dai particolari al carattere"),
   ("quixote2","texture",(.62,.55),3.1,"L'incisione racconta un altro capitolo"),
   ("hunt","whole",(.5,.5),2.8,"Lo studio preparatorio per intero"),
   ("wolf","portrait",(.51,.46),3.0,"La favola e i suoi simboli"),
   ("wolf","whole",(.5,.5),2.9,"Il soggetto rivelato"),
   ("street","portrait",(.48,.55),3.0,"La vita di strada"),
   ("street","whole",(.5,.5),2.7,"Stacco tra universo fantastico e realtà"),
   ("valence","portrait",(.50,.38),3.2,"Uno sguardo umano"),
   ("valence","whole",(.5,.5),2.8,"Rallentamento della regia"),
   ("ice","whole",(.5,.5),4.8,"Ritorno al paesaggio, conclusione circolare")
  ]},
 "piranesi":{
  "name":"Giovanni Battista Piranesi","title":"Le prigioni impossibili","duration":73,
  "track":"darkest_child","hero":"drawbridge",
  "opening":"Una scala si perde nell'ombra di una prigione senza uscita.",
  "resolution":"Piranesi immaginò prigioni dalle dimensioni impossibili e descrisse i monumenti dell'antica Roma attraverso le incisioni.",
  "original":"Partire da passaggi e ponti impossibili, attraversare la Roma antica e tornare all'oscurità.",
  "museum":"Giovanni Battista Piranesi",
  "search":[
   ("drawbridge","The Prisons:  An Immense Interior with a Drawbridge"),
   ("platform","Prisoners on a Projecting Platform, Plate 10"),
   ("prisons","The Prisons"),
   ("nero","The Tomb of Nero"),
   ("sacrifice","Sacrificial Offering in a Temple"),
   ("colosseum","Views of Rome:  The Colosseum"),
   ("pantheon","Views of Rome:  The Pantheon"),
   ("aqueduct","Views of Rome:  The Aquaduct of Nero"),
   ("forum","Views of Rome:  Forum of Nerva"),
   ("temple","Views of Rome:  Temple of the Sibyl at Tivoli")
  ],
  "acts":[
   ("drawbridge","texture",(.55,.32),3.6,"L'occhio inciampa su una scala"),
   ("drawbridge","portrait",(.42,.63),3.3,"Passaggi e catene"),
   ("drawbridge","whole",(.5,.5),3.2,"La prigione impossibile"),
   ("platform","texture",(.62,.41),3.3,"Il prigioniero è minuscolo"),
   ("platform","portrait",(.42,.66),3.2,"La piattaforma senza sbocco"),
   ("platform","whole",(.5,.5),3.3,"Una struttura che sfida la logica"),
   ("prisons","portrait",(.52,.50),3.3,"La serie delle carceri immaginarie"),
   ("prisons","whole",(.5,.5),3.1,"Segni e profondità"),
   ("aqueduct","portrait",(.54,.51),3.3,"La Roma reale risponde alla fantasia"),
   ("aqueduct","whole",(.5,.5),3.2,"Un acquedotto in prospettiva"),
   ("colosseum","texture",(.59,.56),3.3,"L'arena diventa un labirinto"),
   ("colosseum","whole",(.5,.5),3.2,"Il monumento storico"),
   ("pantheon","portrait",(.42,.46),3.3,"Le masse del Pantheon"),
   ("pantheon","whole",(.5,.5),3.1,"La dimensione di Roma"),
   ("nero","portrait",(.52,.47),3.2,"Memoria e rovina"),
   ("nero","whole",(.5,.5),3.0,"Il monumento sopravvissuto"),
   ("temple","portrait",(.46,.44),3.3,"Luce tra le colonne"),
   ("temple","whole",(.5,.5),3.1,"Un respiro prima della chiusura"),
   ("drawbridge","portrait",(.49,.55),3.2,"Ritorno dentro le carceri"),
   ("drawbridge","whole",(.5,.5),5.1,"Ultima inquadratura ferma: l'enigma resta")
  ]}
}
# Reliably downloadable public-domain ocean art (Cleveland Museum).
# Used instead of the earlier Aivazovsky attempt blocked by Commons HTTP 429.
MOVIES["homer"]={
 "name":"Winslow Homer","title":"Il mare non perdona","duration":50,
 "track":"the_descent","hero":"morning",
 "opening":"Dopo la tempesta, un oceano immenso e una fragile traccia umana.",
 "resolution":"Winslow Homer raccontò le forze del mare, i naufragi e la vita dei marinai.",
 "original":"Un percorso autentico tra tempesta, naufragio, navigazione e ritorno della luce.",
 "museum":"Winslow Homer",
 "search":[
  ("morning","Early Morning After a Storm at Sea"),
  ("perils","Perils of the Sea"),
  ("wreck","The Wreck of the \"Atlantic\" - Cast Up by the Sea"),
  ("winter","Winter at Sea - Taking in Sail Off the Coast"),
  ("bells","Eight Bells"),
  ("signal","At Sea, Signalling a Passing Steamer"),
  ("shipbuild","Ship-Building, Gloucester Harbor"),
  ("buccaneers","The Buccaneers"),
  ("dad","\"Dad's Coming!\"")
 ],
 "acts":[
  ("morning","texture",(.52,.48),3.0,"Il mare domina lo schermo sin dal primo secondo"),
  ("morning","portrait",(.42,.58),2.6,"Sfumature della tempesta appena passata"),
  ("morning","whole",(.5,.5),2.7,"La vastità del paesaggio"),
  ("perils","portrait",(.53,.41),3.0,"La costa sembra pericolosa"),
  ("perils","whole",(.5,.5),2.6,"L'intera scena del pericolo"),
  ("wreck","texture",(.48,.65),3.0,"Il relitto sulla costa"),
  ("wreck","whole",(.5,.5),2.6,"Una tragedia resa attraverso l'incisione"),
  ("winter","portrait",(.52,.42),3.0,"Navigare contro il vento"),
  ("winter","whole",(.5,.5),2.6,"I marinai in una luce invernale"),
  ("bells","portrait",(.46,.48),3.1,"L'esperienza umana del mare"),
  ("bells","whole",(.5,.5),2.7,"Il quadro si rivela"),
  ("signal","portrait",(.53,.53),2.8,"Una nave all'orizzonte"),
  ("signal","whole",(.5,.5),2.7,"Navigare è cercare un segnale"),
  ("buccaneers","portrait",(.47,.46),2.9,"Il viaggio diventa storia umana"),
  ("buccaneers","whole",(.5,.5),2.4,"Il mare come luogo di racconti"),
  ("morning","whole",(.5,.5),4.5,"Ritorno al silenzio dopo la tempesta")
 ]
}
# Four ACTUALLY different durations: 50/59/65/73 seconds.
for slug,m in MOVIES.items():
 studio.P[slug]={"name":m["name"],"duration":m["duration"],
  "hero":m["hero"],"key":[m["hero"]],"find":[],
  "act":[m["opening"],m["original"],m["resolution"],m["title"],"Restare nell'immagine"],
  "track":m["track"]}
studio.SOUND["the_descent"]={
 "title":"The Descent","author":"Kevin MacLeod",
 "page":"https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1200094",
 "urls":["https://incompetech.com/music/royalty-free/mp3-royaltyfree/The%20Descent.mp3"],
 "license":"CC BY 4.0","license_url":studio.LICENSE_URL,
 "expected_seconds":192,"instrumental":True}

def normal(text):
 return " ".join(unicodedata.normalize("NFKD",str(text)).casefold().split())

def museum_sources(slug,cfg,folder):
 entry=MOVIES[slug]
 dst=folder/"original_images";dst.mkdir(parents=True,exist_ok=True)
 works=[];errors=[]
 def record(label,title,raw,url,origin,license_short,license_page,credit):
  with Image.open(io.BytesIO(raw)) as source:
   source.load()
   im=ImageOps.exif_transpose(source).convert("RGB")
  if min(im.size)<720:raise ValueError("Insufficient real artwork resolution")
  if max(im.size)>3900:im.thumbnail((3900,3900),Image.Resampling.LANCZOS)
  dig=hashlib.sha256((slug+":"+label+":"+url).encode()).hexdigest()[:17]
  path=dst/(dig+".jpg");im.save(path,quality=94,subsampling=0,optimize=True)
  obj={"id":dig,"label":label,"title":title,"artist":entry["name"],
      "source":origin,"url":url,"original_file":title,
      "license":license_short,"license_url":license_page,
      "attribution":credit,"artist_metadata":entry["name"],
      "file":str(path),"width":im.width,"height":im.height,
      "sha256":hashlib.sha256(path.read_bytes()).hexdigest()}
  works.append(obj)
  print("ACCEPT TRUE ART",slug,label,title,im.size,flush=True)
 if slug=="aivazovsky":
  names=list(entry["works"].values())
  url=studio.COMMONS+urllib.parse.urlencode({"action":"query","format":"json",
      "formatversion":2,"titles":"|".join("File:"+name for name in names),
      "prop":"imageinfo","iiprop":"url|size|extmetadata","iiurlwidth":2900})
  data=json.loads(studio.get(url,timeout=28,size=8_000_000))
  found={p.get("title","").removeprefix("File:"):(p.get("imageinfo") or [None])[0]
        for p in data.get("query",{}).get("pages",[])}
  for label,name in entry["works"].items():
   info=found.get(name)
   if not info:
    errors.append({"title":name,"error":"Commons image not found"});continue
   if not studio.valid_license(info):
    errors.append({"title":name,"error":"Image license not accepted"});continue
   meta=info.get("extmetadata") or {}
   attributed=studio.rawclean(meta.get("Artist"))
   if attributed and not any(x in attributed.casefold() for x in ("aivazov","ayvazov","айвазов","hovhannes")):
    errors.append({"title":name,"error":"Author attribution differs: "+attributed[:100]});continue
   try:
    url=info.get("thumburl") or info.get("url")
    raw=studio.get(url,timeout=30,size=27_000_000)
    link="https://commons.wikimedia.org/wiki/File:"+urllib.parse.quote(name.replace(" ","_"))
    record(label,name,raw,link,"Wikimedia Commons - licensed master image",
       studio.rawclean(meta.get("LicenseShortName")) or "Public domain",
       studio.rawclean(meta.get("LicenseUrl")),
       studio.rawclean(meta.get("Attribution")) or "Ivan Aivazovsky, public domain artwork reproduction")
   except Exception as e:errors.append({"title":name,"error":str(e)[:190]})
   time.sleep(.18)
 else:
  endpoint="https://openaccess-api.clevelandart.org/api/artworks/?"+urllib.parse.urlencode({
      "artists":entry["museum"],"limit":100})
  data=json.loads(studio.get(endpoint,timeout=28,size=11_000_000))
  museum=data.get("data",[])
  print("MUSEUM OPEN ACCESS",slug,len(museum),"records",flush=True)
  for label,phrase in entry["search"]:
   wanted=normal(phrase)
   matches=[a for a in museum if normal(a.get("title"))==wanted]
   if not matches:
    matches=[a for a in museum if wanted in normal(a.get("title"))]
   matches=[a for a in matches if a.get("share_license_status")=="CC0" and (a.get("images") or {}).get("print")]
   if not matches:
    errors.append({"title":phrase,"error":"Matching CC0 artwork missing"});continue
   item=matches[0]
   options=(item.get("images") or {})
   image=options.get("print") or options.get("web")
   url=image["url"]
   try:
    raw=studio.get(url,timeout=28,size=25_000_000)
    page="https://www.clevelandart.org/art/"+str(item.get("accession_number") or item["id"])
    record(label,item["title"],raw,page,"Cleveland Museum of Art Open Access",
      "CC0","https://creativecommons.org/publicdomain/zero/1.0/",
      entry["name"]+"; Open Access image courtesy of The Cleveland Museum of Art (CC0)")
   except Exception as e:errors.append({"title":phrase,"error":str(e)[:190]})
   time.sleep(.12)
  # Use only genuine creator catalog entries. Never substitute public book covers
  # or images from another creator as visual filler.
 ordered={label:i for i,label in enumerate([entry["hero"]]+[
   label for label,_ in (entry.get("search",[])) if label!=entry["hero"]])}
 works.sort(key=lambda w:ordered.get(w["label"],99))
 if not any(w["label"]==entry["hero"] for w in works):
  raise RuntimeError("Hero artwork missing, cannot make honest WOW intro: "+json.dumps(errors[:8]))
 if len(works)<5:
  raise RuntimeError("Five verified distinct original artworks required: "+json.dumps(errors[:10]))
 return works,errors
studio.sources=museum_sources

# Continuous motion caused nausea in previous episodes: fixed frames and
# only rare 0.5-0.8% monotonic push. No horizontal motion at all.
def stable_frame(img,shot,t,bg=None,full=None):
 if shot.kind=="whole":return full.copy() if full is not None else camera.whole(img,bg)
 base={"texture":1.38,"portrait":1.10,"glide":1.07,"breath":1.024}.get(shot.kind,1.08)
 if shot.kind=="glide":base*=1+.008*camera.ease(t)
 elif shot.kind=="portrait":base*=1+.004*camera.ease(t)
 ih,iw=img.shape[:2]
 native_w=min(iw,ih*camera.W/camera.H)
 return camera.compute(img,shot.focus,min(base,max(1.015,native_w/camera.W*.92)),motion=(0,0))
camera.frame_shot=stable_frame

def original_edit(works,cfg,slug):
 m=MOVIES[slug];by_label={x["label"]:x for x in works}
 from collections import Counter
 shots=[]
 for n,(label,mode,focus,weight,reason) in enumerate(m["acts"]):
  if label not in by_label:continue
  if mode=="whole" and shots and shots[-1].kind=="whole":continue
  transition="dissolve" if mode=="whole" and n%3==0 else ("match" if n%4==0 else "cut")
  # Spectacular first image is a REAL detail. Repetition only when editorially justified.
  shots.append(camera.Shot(len(shots),by_label[label],mode,focus,weight,reason,transition))
 if len(shots)<13 or len({s.art["id"] for s in shots})<5:
  raise RuntimeError(f"Insufficient directorial decisions: {len(shots)} shots")
 factor=cfg["duration"]/sum(x.duration for x in shots)
 for s in shots:s.duration*=factor
 assert len(shots)<30
 root=ROOT/slug
 assets=[{"id":w["id"],"role":"visual","visual_type":"painting",
          "description":w["title"],"file":"sources/original_images/"+Path(w["file"]).name,
          "rights":w["license"]+" "+w["url"]}for w in works]
 scenes=[{"asset_id":s.art["id"],"description":s.why,"reason":s.why,
          "purpose":s.why,"focus":list(s.focus),"camera":s.kind,
          "duration":round(s.duration,4),"transition":s.join} for s in shots]
 music=studio.SOUND[cfg["track"]]
 project={
  "schema":"video-project-v13","project_id":"wow7-"+slug,
  "format":"artvision_cinema","title":m["name"]+" — "+m["title"],
  "artist":m["name"],"topic":m["title"],
  "opening":m["opening"],"resolution":m["resolution"],
  "original_value":m["original"],
  "source_verified":True,"fact_sources_checked":True,
  "duration":cfg["duration"],"assets":assets,"scenes":scenes,
  "shots":scenes,"question_supported":False,
  "business":{"audience":"pubblico internazionale arte e curiosità",
      "original_contribution":m["original"],
      "viewer_promise":m["opening"]},
  "music":{"origin":"external_licensed","title":music["title"],
      "artist":music["author"],"source_url":music["page"],
      "license_url":studio.LICENSE_URL,
      "credit_text":"Musica: "+music["title"]+" — "+music["author"]+
        ". CC BY 4.0 https://creativecommons.org/licenses/by/4.0/; estratto, volume e dissolvenze modificati."},
  "automatic_publication":False,
  "director":"ArtVision Cinema V6 Gold Master + V21/V22 stable short editing"
 }
 root.mkdir(parents=True,exist_ok=True)
 (root/"PROJECT_V13.json").write_text(json.dumps(project,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 # Preflight V21 is a separate story+rights audit BEFORE rendering images.
 try:
  sys.path.insert(0,str(Path("src").resolve()))
  from creative_director_v21 import write_package
  write_package(project,root/"PREFLIGHT_V21")
  print("V21 PREFLIGHT READY",slug,flush=True)
 except Exception as e:print("V21 PREFLIGHT ERROR",str(e)[:250],flush=True)
 print("DIRECTOR",slug,len(shots),"shots",len({s.art["id"] for s in shots}),"genuine art sources",flush=True)
 return shots
studio.directed_shots=original_edit
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--artist",required=True,choices=sorted(MOVIES))
 a=p.parse_args();studio.make(a.artist)
