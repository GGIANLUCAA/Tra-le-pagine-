#!/usr/bin/env python3
"""ArtVision Cole V6/V21: one original silent 9:16 film on The Course of Empire.
Five exact genuine 1836 Cole paintings; optional 1838 open-access nature prologue.
Manual visual storytelling; stationary camera or <= 0.8% one-way push, no oscillation.
No mutation of approved Gold Master / prior outputs; no external paid API.
"""
from pathlib import Path
import argparse,hashlib,io,json,re,urllib.parse
from PIL import Image,ImageOps
import cv2
import batch5_cinema_v6 as studio
import director_cinema_v6 as camera

SLUG="thomas_cole"
studio.ROOT=Path("output/artvision-thomas-cole-course-v6")
studio.P.clear()
studio.P[SLUG]={
 "name":"Thomas Cole","duration":122,
 "hero":"Cole Thomas The Course of Empire Destruction 1836.jpg",
 "key":["the course of empire","savage state","arcadian","consummation","destruction","desolation"],
 "find":["Cole Thomas The Course of Empire"],
 "act":["Il crollo, senza preamboli","Natura e primi insediamenti",
        "La nascita della città","La grandezza conduce alla guerra",
        "Dopo la rovina resta il silenzio"],
 "track":"dreams_become_real"}
COMMONS={
 "savage":"Cole Thomas The Course of Empire The Savage State 1836.jpg",
 "arcadian":"Cole Thomas The Course of Empire The Arcadian or Pastoral State 1836.jpg",
 "consummation":"Cole Thomas The Consummation The Course of the Empire 1836.jpg",
 "destruction":"Cole Thomas The Course of Empire Destruction 1836.jpg",
 "desolation":"Cole Thomas The Course of Empire Desolation 1836.jpg"}
def real_images(slug,cfg,root):
 dst=root/"original_images";dst.mkdir(parents=True,exist_ok=True)
 url=studio.COMMONS+urllib.parse.urlencode({
  "action":"query","format":"json","formatversion":2,
  "titles":"|".join("File:"+p for p in COMMONS.values()),
  "prop":"imageinfo","iiprop":"url|size|extmetadata","iiurlwidth":3000})
 doc=json.loads(studio.get(url,timeout=28,size=7_000_000))
 found={p.get("title","").removeprefix("File:"):p.get("imageinfo",[None])[0]
        for p in doc.get("query",{}).get("pages",[])}
 works=[];errors=[]
 def store(label,title,raw,origin,source,license_short,license_url,credit):
  with Image.open(io.BytesIO(raw)) as image:
   image.load()
   im=ImageOps.exif_transpose(image).convert("RGB")
  if min(im.size)<700:raise ValueError("Painting photo below minimum resolution")
  if max(im.size)>3800:im.thumbnail((3800,3800),Image.Resampling.LANCZOS)
  digest=hashlib.sha256((label+title).encode()).hexdigest()[:17]
  path=dst/(digest+".jpg")
  im.save(path,quality=93,subsampling=0,optimize=True)
  record={"id":digest,"title":title,"label":label,"artist":"Thomas Cole",
   "source":origin,"url":source,"original_file":title,"license":license_short,
   "license_url":license_url,"attribution":credit,"artist_metadata":"Thomas Cole",
   "image_url":source,"file":str(path),"width":im.width,"height":im.height,
   "sha256":hashlib.sha256(path.read_bytes()).hexdigest()}
  works.append(record)
  print("ORIGINAL ART",label,title,im.size,flush=True)
 # Exact five iconic compositions; never substitute similar paintings.
 for label,name in COMMONS.items():
  info=found.get(name)
  if not info:
   errors.append({"title":name,"error":"Wikimedia Commons entry missing"});continue
  if not studio.valid_license(info):
   errors.append({"title":name,"error":"No verified Commons license"});continue
  try:
   thumbnail=info.get("thumburl") or info.get("url")
   raw=studio.get(thumbnail,timeout=30,size=20_000_000)
   ext=info.get("extmetadata") or {}
   store(label,name,raw,"Wikimedia Commons",
    "https://commons.wikimedia.org/wiki/File:"+urllib.parse.quote(name.replace(" ","_")),
    studio.rawclean(ext.get("LicenseShortName")) or "Public domain",
    studio.rawclean(ext.get("LicenseUrl")),
    studio.rawclean(ext.get("Attribution")) or "Thomas Cole; faithful public-domain artwork reproduction")
  except Exception as exc:errors.append({"title":name,"error":str(exc)[:180]})
 if not all(any(w["label"]==k for w in works) for k in COMMONS):
  raise RuntimeError("Do not fabricate missing Course of Empire paintings: "+json.dumps(errors))
 # Open-access Cleveland artworks: contextual prologue only, never labelled part
 # of the five-painting cycle.
 try:
  lookup="https://openaccess-api.clevelandart.org/api/artworks/?artists=Thomas%20Cole&limit=30"
  museum=json.loads(studio.get(lookup,timeout=25,size=5_000_000))
  preferred={"View of Schroon Mountain, Essex County, New York, After a Storm":"schroon"}
  for item in museum.get("data",[]):
   title=item.get("title") or "";label=preferred.get(title)
   if not label or item.get("share_license_status")!="CC0":continue
   artwork=(item.get("images") or {}).get("print") or {}
   if not artwork.get("url"):continue
   try:
    data=studio.get(artwork["url"],timeout=28,size=20_000_000)
    store(label,title,data,"Cleveland Museum of Art Open Access",
      "https://www.clevelandart.org/art/"+str(item.get("accession_number") or item["id"]),
      "CC0","https://creativecommons.org/publicdomain/zero/1.0/",
      "Open Access image courtesy of Cleveland Museum of Art (CC0)")
   except Exception as exc:errors.append({"title":title,"error":str(exc)[:180]})
 except Exception as exc:
  errors.append({"source":"Cleveland optional prologue","error":str(exc)[:160]})
 priority={"destruction":0,"consummation":1,"desolation":2,"savage":3,"arcadian":4,"schroon":5}
 works.sort(key=lambda w:priority.get(w["label"],99))
 return works,errors
studio.sources=real_images

# Adopts the fixed/near-fixed V22 discipline on the existing V6 camera module:
# locked focus, absolutely no back-and-forth translation or sinusoidal motion.
def quiet_shot(img,shot,t,bg=None,full=None):
 if shot.kind=="whole":
  return full.copy() if full is not None else camera.whole(img,bg)
 modes={"texture":1.42,"portrait":1.115,"glide":1.08,"breath":1.025}
 zoom=modes.get(shot.kind,1.08)
 # Only 'glide' and 'portrait' get a tiny (0.8%) one-way push; no camera pan.
 if shot.kind=="glide":zoom*=1+.008*camera.ease(t)
 elif shot.kind=="portrait":zoom*=1+.004*camera.ease(t)
 # UHD museum files generally allow these zoom values without loss.
 ih,iw=img.shape[:2]
 base_width=min(iw,ih*camera.W/camera.H)
 limit=max(1.015,base_width/camera.W*.92)
 return camera.compute(img,shot.focus,min(zoom,limit),motion=(0,0))
camera.frame_shot=quiet_shot

# Music selects a real CC BY instrumental recording already used by this studio;
# a different creative cut from John Martin, not its soundtrack or pacing.
BEATS=[
 ("destruction","texture",(.55,.48),3.0,"Un lampo: la città si sta spezzando","cut"),
 ("destruction","portrait",(.68,.50),2.5,"Le rovine raccontano il conflitto","cut"),
 ("destruction","whole",(.5,.5),2.5,"Rivelazione: la catastrofe riguarda tutto l'impero","dissolve"),
 ("schroon","portrait",(.58,.39),3.3,"Prima delle città c'è il paesaggio","cut"),
 ("schroon","glide",(.28,.50),3.2,"Luce e natura, nessun moto artificioso","cut"),
 ("savage","portrait",(.49,.33),3.4,"Le prime forme dell'insediamento umano","cut"),
 ("savage","texture",(.74,.60),2.8,"Un piccolo gesto umano nella valle","cut"),
 ("savage","breath",(.35,.49),3.5,"Le forze della natura dominano ancora","cut"),
 ("savage","whole",(.5,.5),3.5,"Prima tappa: The Savage State","dissolve"),
 ("arcadian","portrait",(.45,.48),3.4,"La valle si fa domestica","cut"),
 ("arcadian","texture",(.72,.62),2.9,"Figure, campi e vita pastorale","cut"),
 ("arcadian","glide",(.27,.49),3.3,"Architetture semplici emergono nel paesaggio","cut"),
 ("arcadian","whole",(.5,.5),3.5,"Seconda tappa: la società pastorale","dissolve"),
 ("consummation","portrait",(.54,.38),3.5,"La città occupa l'intera valle","cut"),
 ("consummation","texture",(.78,.56),3.1,"Decorazioni e architetture monumentali","cut"),
 ("consummation","portrait",(.24,.57),3.4,"La folla ora è minuscola davanti alle colonne","cut"),
 ("consummation","glide",(.59,.78),3.0,"Lo splendore e il suo peso","cut"),
 ("consummation","whole",(.5,.5),3.6,"Terza tappa: Consummation","dissolve"),
 ("destruction","portrait",(.43,.54),3.3,"Lo stesso luogo viene travolto","cut"),
 ("destruction","texture",(.29,.66),3.1,"Battaglia, tempesta e caos","cut"),
 ("destruction","breath",(.68,.37),3.3,"La città non è più invincibile","cut"),
 ("destruction","portrait",(.58,.70),3.1,"Tensione: gli ultimi monumenti","cut"),
 ("destruction","whole",(.5,.5),3.5,"Quarta tappa: Destruction, immagine intera","dissolve"),
 ("desolation","portrait",(.52,.45),3.3,"L'assenza umana è la vera svolta","cut"),
 ("desolation","texture",(.71,.33),3.2,"Le colonne sopravvivono senza l'impero","cut"),
 ("desolation","breath",(.31,.61),3.4,"Acqua e natura si riprendono il luogo","cut"),
 ("desolation","glide",(.60,.52),3.4,"Una quiete senza celebrazione","cut"),
 ("desolation","whole",(.5,.5),5.2,"Quinta tappa: Desolation, ultimo sguardo immobile","dissolve")]
def editorial_shots(works,cfg,slug):
 by_label={a["label"]:a for a in works}
 shots=[]
 for i,(label,mode,focus,seconds,why,join) in enumerate(BEATS):
  if label not in by_label:
   if label=="schroon":continue
   raise RuntimeError("Essential Cole composition unavailable: "+label)
  shots.append(camera.Shot(len(shots),by_label[label],mode,focus,seconds,why,join))
 if len(shots)<25:raise RuntimeError("Too few independently planned shots")
 duration=cfg["duration"];sumw=sum(x.duration for x in shots)
 for shot in shots:shot.duration*=duration/sumw
 root=studio.ROOT/slug
 assets=[{"id":w["id"],"role":"visual",
  "file":"sources/original_images/"+Path(w["file"]).name,
  "visual_type":"painting","description":w["title"],"rights":w["license"]+" "+w["url"]}
  for w in works]
 scenes=[{"asset_id":sh.art["id"],"description":sh.why,"reason":sh.why,
          "purpose":sh.why,"duration":round(sh.duration,3),"focus_xy":list(sh.focus),
          "camera":sh.kind,"transition":sh.join} for sh in shots]
 original="Un racconto senza voce: dal crollo iniziale si torna alla nascita di un impero e si attraversano cinque dipinti autentici sino alla desolazione."
 project={"schema":"video-project-v13","project_id":"cole-course-empire-cinema-v6-v21",
 "format":"artvision_cinema","title":"Thomas Cole — Il destino di un impero",
 "artist":"Thomas Cole","topic":"Il corso dell'impero: cinque dipinti, una parabola sulla civiltà",
 "duration":duration,
 "opening":"Una città grandiosa sta crollando. Ma come è arrivata fin qui?",
 "resolution":"Thomas Cole dipinse la serie The Course of Empire nel 1836: natura, vita pastorale, splendore, distruzione, desolazione.",
 "original_value":original,"source_verified":True,"fact_sources_checked":True,
 "assets":assets,"scenes":scenes,"shots":scenes,"question_supported":False,
 "music":{"origin":"external_licensed","title":"Dreams Become Real",
     "artist":"Kevin MacLeod","license_url":studio.LICENSE_URL,
     "source_url":studio.SOUND["dreams_become_real"]["page"],
     "credit_text":"Musica: Dreams Become Real — Kevin MacLeod. Licenza CC BY 4.0: https://creativecommons.org/licenses/by/4.0/ . Brano montato in estratto, con dissolvenze e volume regolato."},
 "business":{"original_contribution":original,"viewer_promise":"Cinque quadri autentici raccontano la nascita e la caduta di un impero",
 "audience":"Pubblico curioso di arte, storia e mistero"},
 "director":"ArtVision Cinema V6 + V21, V22 stable shots",
 "automatic_publication":False}
 (root/"PROJECT_V13.json").write_text(json.dumps(project,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 return shots
studio.directed_shots=editorial_shots
if __name__=="__main__":
 ap=argparse.ArgumentParser()
 ap.add_argument("--artist",choices=[SLUG],default=SLUG)
 studio.make(ap.parse_args().artist)
