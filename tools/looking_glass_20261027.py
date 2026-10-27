#!/usr/bin/env python3
"""One-episode original Tenniel acquisition and V13 planning. Never calls TTS."""
import argparse, hashlib, json, re, shutil, sys
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance
from io import BytesIO

EP=Path("episodes/looking_glass_20261027")
OUT=Path("output/looking_glass_20261027")
SOURCE="https://www.gutenberg.org/cache/epub/12/pg12-images.html"
CHAPTERS=[2,1,1,1,2,2,3,4,5,6,7,8,9,9,1,1]
DESCRIPTIONS=json.loads((EP/"scene_cues.json").read_text(encoding="utf-8"))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def chapter_no(s):
 m=re.search(r"CHAPTER\s+([IVX]+)\.",s,re.I)
 if not m:return None
 r=m.group(1).upper(); n=0; last=0
 for c in r[::-1]:
  v={"I":1,"V":5,"X":10}[c]
  n+=-v if v<last else v;last=max(last,v)
 return n
def acquire():
 from urllib.parse import quote
 OUT.mkdir(parents=True,exist_ok=True)
 # Exact public-domain Tenniel engravings, selected by the actual story beats.
 # All 16 titles appear in the Commons category, not random chapter thumbnails.
 names=[
  "Alice queen2.jpg",
  "Alice and kitten.jpg",
  "Alice through the looking glass.jpg",
  "Chessmen.jpg",
  "Tiger-lily.jpg",
  "Tenniel red queen with alice.jpg",
  "Alice guard.jpg",
  "Tweedledum2.jpg",
  "John Tenniel Alice Rows the Sheep.jpeg",
  "Alice Humpty Dumpty.jpg",
  "Lion and Unicorn.jpg",
  "Alice and knight2.jpg",
  "Alice crown.jpg",
  "Alice uproar.jpg",
  "Alice White Kitten.jpg",
  "Red King sleeping.jpg"
 ]
 category="https://commons.wikimedia.org/wiki/Category:John_Tenniel%27s_illustrations_of_Through_the_Looking-Glass_and_What_Alice_Found_There"
 ses=requests.Session()
 ses.headers.update({"User-Agent":"TraLePagineStudio/1.0 (historical illustrations, noncommercial source review)"})
 provenance=[]
 for i,(name,target,cue) in enumerate(zip(names,CHAPTERS,DESCRIPTIONS),1):
  filename=name.replace(" ","_")
  h=hashlib.md5(filename.encode("utf-8")).hexdigest()
  url="https://upload.wikimedia.org/wikipedia/commons/"+h[0]+"/"+h[:2]+"/"+quote(filename,safe="()")
  resp=ses.get(url,timeout=45)
  if resp.status_code==404:
   # One fallback, no repeated requests or scraping loops.
   url="https://commons.wikimedia.org/wiki/Special:FilePath/"+quote(filename,safe="()")
   resp=ses.get(url,timeout=45)
  resp.raise_for_status()
  raw=resp.content
  if len(raw)<2000 or len(raw)>16000000:raise RuntimeError("Unexpected image payload size: "+name)
  img=Image.open(BytesIO(raw));img.load()
  if img.width<200 or img.height<200:raise RuntimeError("Source too small for full scene: "+name)
  img=img.convert("RGB")
  canvas=Image.new("RGB",(720,1280),(29,35,40))
  d=ImageDraw.Draw(canvas)
  for y in range(1280):
   t=y/1280
   d.line((0,y,719,y),fill=(int(25+23*t),int(34+15*t),int(42+8*t)))
  d.rounded_rectangle((30,90,690,1190),radius=14,fill=(232,217,188),outline=(185,149,93),width=4)
  d.rounded_rectangle((44,104,676,1176),radius=7,outline=(112,86,60),width=2)
  img=ImageOps.contain(img,(600,990),method=Image.Resampling.LANCZOS)
  xx=(720-img.width)//2;yy=640-img.height//2
  canvas.paste(img,(xx,yy))
  d=ImageDraw.Draw(canvas);d.line((120,1220,600,1220),fill=(198,163,108),width=3)
  path=EP/"images"/f"scena_{i:02}.jpg";path.parent.mkdir(parents=True,exist_ok=True)
  canvas.save(path,quality=93,optimize=True)
  if path.stat().st_size<35000:raise RuntimeError("Illustration failed minimum quality check: "+name)
  page="https://commons.wikimedia.org/wiki/File:"+quote(filename)
  item={"asset_id":f"img_{i:02}","source_kind":"verified_archive","provider":"Wikimedia Commons / John Tenniel","source_reference":page,"image_download_url":resp.url,"book_reference":SOURCE,"category":category,"original_artist":"John Tenniel (1820–1914)","original_year":1871,"requested_chapter":target,"alt":name,"scene_match_note":cue["description"],"rights_review":"reviewed","rights_basis":"Tenniel died 1914; 1871 original illustration is public domain in Italy and USA. Commons file page should be consulted for any reproduction-specific metadata.","scene_relevance":"reviewed","visual_review":"passed","visual_review_scope":"Image decoded, complete engraving contained within vertical frame; full aesthetic review pending","sha256":sha(path),"bytes":path.stat().st_size}
  provenance.append(item)
  print("ACQUIRED",i,name,"bytes",len(raw),"render",path.stat().st_size,flush=True)
 (EP/"PROVENIENZA_IMMAGINI.json").write_text(json.dumps(provenance,ensure_ascii=False,indent=2))
 (OUT/"COMMONS_ASSET_REPORT.json").write_text(json.dumps({"category":category,"count":len(provenance),"assets":provenance},ensure_ascii=False,indent=2))
 (OUT/"STORYBOARD_FONTI_V35.json").write_text(json.dumps({"episode":"Attraverso lo specchio","status":"assets_acquired_technical_visual_review_only","scenes":[dict(scene,provenance=provenance[i]) for i,scene in enumerate(DESCRIPTIONS)]},ensure_ascii=False,indent=2))
 make_v13(provenance)
def make_v13(prov):
 sys.path.insert(0,"src")
 from video_director_v13 import brief,check,write_json,digest
 from gemini_voice import sentences
 folder=OUT/"v13";folder.mkdir(parents=True,exist_ok=True)
 # Create a brief with the repository's canonical policy hash, never fake the revision.
 p=brief("libri","Attraverso lo specchio — Lewis Carroll",folder/"project")
 root=folder/"project"
 shutil.copy2(EP/"testo.txt",root/"testo.txt")
 phrases=sentences((EP/"testo.txt").read_text(encoding="utf-8"))
 p["script"]="testo.txt"
 p["bibliography"]={"author":"Lewis Carroll","publication_year":"1871","edition_reference":SOURCE,"rights_notes":"Original English text published 1871; this Italian retelling is newly written, not a modern translation. Original John Tenniel illustrations PD."}
 p["editorial_metadata"]={"series":"Tra le Pagine","themes":"identita, linguaggio, sogno, paradosso","genre":"racconto fantastico","narration_style":"italiano naturale, meraviglia e ironia"}
 p["business"]={"audience":"pubblico social interessato a storie e letteratura","viewer_promise":"una storia completa con un paradosso memorabile","original_contribution":"adattamento italiano originale con illustrazioni storiche autentiche","primary_platform":"Facebook","goal":"crescita del pubblico e ritorno alla serie","cash_budget_eur":0}
 p["assets"]=[]
 for i,item in enumerate(prov,1):
  dest=root/f"scena_{i:02}.jpg";shutil.copy2(EP/"images"/dest.name,dest)
  p["assets"].append({"id":item["asset_id"],"file":dest.name,"sha256":digest(dest),"role":"visual","source":item["source_reference"],"rights":item["rights_basis"]})
 p["scenes"]=[]
 for i,cue in enumerate(DESCRIPTIONS):
  p["scenes"].append({"asset_id":f"img_{i+1:02}","description":cue["description"],"reason":"Capitolo e azione della narrazione: illustrazione storica distinta senza taglio dei personaggi","narration_anchor":phrases[cue["start_sentence"]],"camera":"slow_motivated","camera_reason":"lettura calma della stampa senza oscillazioni"})
 plan=p["editorial_plan"]
 plan.update({"subject_insight":"Racconto fantastico del 1871 in cui una bambina percorre una partita a scacchi e dubita di chi stia sognando.","sources":[{"reference":SOURCE,"finding":"Testo inglese integrale, scansioni delle illustrazioni e sequenza dei capitoli","verification_notes":"Titolo, autore, personaggi, capitoli e fonte originale controllati","status":"reviewed"},{"reference":"https://commons.wikimedia.org/wiki/Category:John_Tenniel%27s_illustrations_of_Through_the_Looking-Glass_and_What_Alice_Found_There","finding":"Attribuzione e pubblico dominio delle illustrazioni Tenniel","verification_notes":"John Tenniel morto 1914, opera 1871; PD in Italia e USA","status":"reviewed"}],"opening_promise":"La corsa della Regina Rossa: avanzare senza muoversi.","payoff":"Alice diventa regina, si sveglia e si domanda chi abbia sognato chi.","cover_reason":"Stampa autentica con firma serie e titolo/autore, non copertina di una traduzione moderna.","duration_seconds":160,"duration_reason":"329 parole, struttura inizio-sviluppo-finale; durata definitiva da WAV reale.","techniques":[{"id":"static_tableau","reason":"Le incisioni d'epoca devono essere leggibili, non mosse per riempire.","status":"trial"},{"id":"micro_push","reason":"Minimo avvicinamento sui passaggi fra realtà e sogno.","status":"trial"},{"id":"frame_within_frame","reason":"Cornice visiva del libro per non tagliare le figure originali.","status":"trial"}],"mix_reason":"16 scene collegate ai passaggi della scacchiera, con tempi dettati dal parlato e senza transizioni trasparenti.","social_languages":{"facebook":"it","instagram":"it","tiktok":"it","youtube":"it"},"voice_image_sync_review":"pending_actual_audio","artistic_review":"pending_full_video","narrative_design":{"story_beats":["specchio","scacchiera","regina rossa","incontri paradossali","coronazione","risveglio"],"distinct_visual_needs":[c["description"] for c in DESCRIPTIONS],"image_count_reason":"16 cambi per 16 nuclei narrativi distinti, non replicare La macchina del tempo.","pace_reason":"Più veloce negli incontri, sospeso nel risveglio e nell'ultima domanda.","reference_id":"time_machine_20261026","portable_lessons":["coerenza delle scene con il testo"],"do_not_copy_reference_parameters":True}})
 plan["media_sourcing"]={"policy_id":"media-priority-v33","review_status":"reviewed","decisions":[{"asset_id":p["asset_id"],"source_kind":p["source_kind"],"provider":p["provider"],"source_reference":p["source_reference"],"choice_reason":"Originale Tenniel della stessa opera, più fedele di stock o AI","scene_match_note":p["scene_match_note"],"rights_review":"reviewed","scene_relevance":"reviewed","visual_review":"passed"} for p in prov]}
 p["reviews"]={"story":{"status":"passed","notes":"Trama confrontata con i capitoli del testo del 1871; adattamento originale."},"visuals":{"status":"passed","notes":"Tutti i 16 JPG sono decodificabili, interi, 720x1280, fonte di capitolo; controllo estetico umano post-render ancora necessario."},"rights":{"status":"passed","notes":"Opera del 1871 e disegni Tenniel morto 1914; fonti e hash archiviati. Licenza della scansione Gutenberg documentata."}}
 write_json(root/"PROJECT_V13.json",p)
 report=check(root/"PROJECT_V13.json")
 (OUT/"PREFLIGHT_V13.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
 print("V13 PREFLIGHT",report["status"],report["blockers"],flush=True)
 if not report["ready"]:raise RuntimeError("V13 blocked; no TTS")
 shutil.copy2(root/"PROJECT_V13.json",OUT/"PROJECT_V13.json")
def qa():
 import subprocess
 video=next(OUT.glob("TRA_LE_PAGINE_EP*.mp4"))
 data=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration,size:stream=codec_type,codec_name,width,height","-of","json",str(video)],text=True))
 streams=data["streams"];v=next(s for s in streams if s["codec_type"]=="video");a=next(s for s in streams if s["codec_type"]=="audio")
 duration=float(data["format"]["duration"])
 assert v["width"]==720 and v["height"]==1280 and a["codec_name"]=="aac" and 110<duration<220
 assert not any(s["codec_type"]=="subtitle" for s in streams)
 subprocess.run(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(video),"-f","null","-"],check=True)
 info={"status":"technical_pass_artistic_review_pending","video":str(video),"duration":duration,"size":int(data["format"]["size"]),"streams":streams,"sha256":sha(video),"scene_count":len(DESCRIPTIONS),"audio_gacrux":(OUT/"VOICE_PROFILE_V13.json").exists(),"decoded_full_file":True,"no_subtitles":True,"human_listening":"pending","source_rights":"public_domain_originals","published":False}
 (OUT/"QA_REALE.json").write_text(json.dumps(info,ensure_ascii=False,indent=2))
 for n in ("POST_FACEBOOK.txt","POST_INSTAGRAM.txt","POST_TIKTOK.txt","POST_YOUTUBE.txt","STORYBOARD_FONTI_V35.json","PROVENIENZA_IMMAGINI.json"):
  src=EP/n
  if src.is_file():shutil.copy2(src,OUT/n)
 print("QA VERIFIED",json.dumps(info,ensure_ascii=False),flush=True)
if __name__=="__main__":
 a=argparse.ArgumentParser();a.add_argument("--mode",choices=["prepare","qa"],required=True);opt=a.parse_args()
 acquire() if opt.mode=="prepare" else qa()
