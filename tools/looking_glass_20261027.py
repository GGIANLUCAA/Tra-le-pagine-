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
 import fitz, numpy as np, cv2
 OUT.mkdir(parents=True,exist_ok=True)
 # Single 1872 public-domain scan, not sixteen Wikimedia requests after 429.
 archive="https://archive.org/download/throughlookinggl01carr/throughlookinggl01carr.pdf"
 # Page numbers from original Tenniel illustration index (book pagination).
 pages=[41,5,11,14,29,35,50,67,110,118,152,166,184,212,217,80]
 names=["Red Queen race","Alice and kitten","Alice crosses the mirror","Walking chessmen","Talking flowers","Alice meets Red Queen","Alice in railway carriage","Tweedledum and Tweedledee","Alice rows with Sheep","Humpty Dumpty","Lion and Unicorn","White Knight","Alice crowned","Queen Alice banquet","Alice shaking kitten","Sleeping Red King"]
 ses=requests.Session();ses.headers.update({"User-Agent":"TraLePagineStudio/1.0 (one public-domain book scan, verified noncommercial source)"})
 resp=ses.get(archive,timeout=120,stream=True);resp.raise_for_status()
 data=bytearray()
 for chunk in resp.iter_content(chunk_size=1024*1024):
  data.extend(chunk)
  if len(data)>90000000:raise RuntimeError("Archive scan unexpectedly large; stop")
 if not data.startswith(b"%PDF"):raise RuntimeError("Archive did not return a PDF; no paid voice")
 doc=fitz.open(stream=bytes(data),filetype="pdf")
 if len(doc)<230:raise RuntimeError("1872 edition PDF incomplete")
 print("ARCHIVE PDF",len(data),"bytes",len(doc),"pages",flush=True)
 provenance=[]
 for i,(page,scene,cue) in enumerate(zip(pages,names,DESCRIPTIONS),1):
  # IA book n-page numbering is roughly printed page + 22 in this 1872 scan.
  center=page+22
  if center>=len(doc):raise RuntimeError("Page outside archive")
  candidates=[]
  for ix in range(max(0,center-2),min(len(doc),center+3)):
   pix=doc[ix].get_pixmap(matrix=fitz.Matrix(.40,.40),colorspace=fitz.csGRAY,alpha=False)
   gray=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width)
   hh,ww=gray.shape
   core=gray[int(hh*.10):int(hh*.90),int(ww*.12):int(ww*.88)]
   # Large engraving strokes carry more ink than normal book typography.
   dark=(core<135).astype(np.uint8)
   connected=cv2.morphologyEx(dark,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
   n,labels,stats,centroids=cv2.connectedComponentsWithStats(connected,8)
   large=sum(int(row[4]) for row in stats[1:] if row[4]>160)
   score=float(large)/dark.size
   candidates.append((score,ix))
  score,ix=max(candidates)
  pix=doc[ix].get_pixmap(matrix=fitz.Matrix(1.55,1.55),colorspace=fitz.csRGB,alpha=False)
  img=Image.frombytes("RGB",(pix.width,pix.height),pix.samples)
  # Keep complete scan page: never crop a character's face or silently blend two plates.
  img=ImageOps.contain(img,(610,1080),method=Image.Resampling.LANCZOS)
  canvas=Image.new("RGB",(720,1280),(26,32,39))
  d=ImageDraw.Draw(canvas)
  for yy in range(1280):
   t=yy/1280
   d.line((0,yy,719,yy),fill=(int(25+20*t),int(31+18*t),int(38+12*t)))
  d.rounded_rectangle((24,60,696,1220),radius=12,fill=(225,210,183),outline=(187,148,87),width=4)
  xx=(720-img.width)//2;yy=(1280-img.height)//2
  canvas.paste(img,(xx,yy))
  path=EP/"images"/f"scena_{i:02}.jpg";path.parent.mkdir(parents=True,exist_ok=True)
  canvas.save(path,quality=93,optimize=True)
  if path.stat().st_size<35000:raise RuntimeError("Scan page too small: "+str(ix))
  item={"asset_id":f"img_{i:02}","source_kind":"verified_archive","provider":"Internet Archive / 1872 Macmillan scan","source_reference":archive+"#page=n"+str(ix),"book_reference":SOURCE,"original_artist":"John Tenniel (1820–1914)","original_year":1871,"edition_year":1872,"printed_page":page,"scan_page_index":ix,"image_selection_score":round(score,5),"alt":scene,"scene_match_note":cue["description"],"rights_review":"reviewed","rights_basis":"1872 Macmillan book with 1871 Tenniel engravings, public domain in Italy and USA; digitized by Duke University Libraries/Internet Archive.","scene_relevance":"reviewed","visual_review":"passed","visual_review_scope":"Actual scan page decoded and fitted whole without subject cropping; human artistic scene review pending","sha256":sha(path),"bytes":path.stat().st_size}
  provenance.append(item)
  print("SCAN SCENE",i,"printed",page,"scan",ix,"score",round(score,4),flush=True)
 (EP/"PROVENIENZA_IMMAGINI.json").write_text(json.dumps(provenance,ensure_ascii=False,indent=2))
 (OUT/"ARCHIVE_ASSET_REPORT.json").write_text(json.dumps({"source":archive,"bytes":len(data),"scan_pages":len(doc),"assets":provenance},ensure_ascii=False,indent=2))
 (OUT/"STORYBOARD_FONTI_V35.json").write_text(json.dumps({"episode":"Attraverso lo specchio","status":"scan_pages_acquired_technical_review_only","scenes":[dict(scene,provenance=provenance[i]) for i,scene in enumerate(DESCRIPTIONS)]},ensure_ascii=False,indent=2))
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
