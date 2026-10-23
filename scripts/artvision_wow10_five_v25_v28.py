#!/usr/bin/env python3
"""ArtVision WOW10: two *new* short cinematic art films from multiple authenticated
Cleveland Museum of Art CC0 artworks (Dürer + Kyōsai + Church + Rousseau + Rackham).
Extends the tested Cinema V6 Gold Master / V25 / V28 process without modifying it.

Both works are based on a cohesive original artwork or cohesive image series rather than unrelated
filler art. Every shot has its own actual artwork ID and editorial purpose.
No automatically published social content. No synthetic painting details.
"""
from __future__ import annotations
import argparse,copy,hashlib,json,os,pathlib,shutil,subprocess,sys,time,zipfile
from PIL import Image,ImageOps,ImageDraw
import artvision_wow8_five_v25_v28 as engine
import artvision_cinema_v25_five_20261023 as base
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
import artvision_editorial_post_v28 as editorial
from artvision_contract_gate_v25 import check_preflight
CFG=ROOT/"config/artvision_wow10_five_v25.json"
CAP=ROOT/"config/artvision_wow10_editorial_v28.json"
P=json.loads(CFG.read_text(encoding="utf8"))
engine.PROFILES=P
engine.CAPTIONS=CAP
editorial.CATALOG=CAP
engine.editorial.CATALOG=CAP
# base's approved V6 intro/cover/FFmpeg routines stay untouched.
base.text_social=engine.genuine_posts
base.CONF=CFG

def digest(path):
 h=hashlib.sha256()
 with pathlib.Path(path).open("rb") as f:
  for piece in iter(lambda:f.read(2**19),b""):h.update(piece)
 return h.hexdigest()

def load_real_museum_artworks(slug,w,ep):
 all_works={}
 srcroot=ep/"ARTWORKS_AUTHENTIC";srcroot.mkdir(exist_ok=True)
 for label,source in w["assets"].items():
  accession=source["accession"]
  url=f"https://openaccess-cdn.clevelandart.org/{accession}/{accession}_print.jpg"
  obj={"label":label,"accession":accession,"title":source["title"],
       "museum":"The Cleveland Museum of Art","source_page":f"https://www.clevelandart.org/art/{accession}",
       "source_image":url,"license":"CC0 open access",
       "license_url":"https://creativecommons.org/publicdomain/zero/1.0/",
       "artist":w["artist"]}
  original=srcroot/f"{label}_ORIGINAL.jpg"
  engine.ORIG_FETCH([url],original,60000,"image")
  with Image.open(original) as im:
   im.load()
   asset=ImageOps.exif_transpose(im).convert("RGB")
  rect=source.get("trim",[0,0,1,1])
  if rect!=[0,0,1,1]:
   x1,y1,x2,y2=rect
   asset=asset.crop((round(asset.width*x1),round(asset.height*y1),
                     round(asset.width*x2),round(asset.height*y2)))
  if min(asset.size)<950:raise RuntimeError("Low real source resolution for "+label)
  processed=srcroot/f"{label}_EDIT_CROP.jpg"
  asset.save(processed,quality=95,subsampling=0,optimize=True)
  obj.update(original_file=original.name,crop_file=processed.name,
             sha256_original=digest(original),sha256_working=digest(processed),
             trimmed_box=rect,working_width=asset.width,working_height=asset.height)
  all_works[label]=(asset,obj)
  print("WOW10 VERIFIED CC0",slug,label,accession,asset.size,flush=True)
 manifest={"status":"source_images_verified",
   "note":"Only museum CC0 sources; original reference photos preserved without color manipulation",
   "items":[x[1] for x in all_works.values()]}
 (ep/"COLLECTION_SOURCES_CC0.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 return all_works

def ensure_v28_music_match(w,music):
 key=w["editorial_key"]
 entry=editorial.config()["entries"][key]
 errors=editorial.validate_entry(key,entry)
 if errors:raise RuntimeError("V28 EDITORIAL FAILED "+str(errors))
 credits="\n".join(entry["credit_lines"])
 if music["title"].casefold() not in credits.casefold() or music["page"] not in credits:
  raise RuntimeError(f"Licensed music and social credits mismatch on {key}")
 return key

def compose_project(slug,w,ep,all_works):
 engine.preflight_project(slug,w,ep)
 path=ep/"PROJECT_V13.json"
 project=json.loads(path.read_text(encoding="utf8"))
 project["assets"]=[{"id":"museum-"+k,"role":"visual","visual_type":"original artwork",
      "description":item["title"],"source":item["source_page"],
      "rights":item["license"]+" "+item["license_url"],
      "file":str(pathlib.Path("ARTWORKS_AUTHENTIC")/item["crop_file"])}
      for k,(_,item) in all_works.items()]
 project["scenes"]=[{"asset_id":"museum-"+s["source_id"],"description":s["purpose"],
    "purpose":s["purpose"],"reason":s["purpose"],"camera":s["kind"],
    "motion":s["motion"],"focus":[s["x"],s["y"]],"duration":s["seconds"]}
    for s in w["scenes"]]
 project["source_verified"]=True
 path.write_text(json.dumps(project,ensure_ascii=False,indent=2)+"\n",encoding="utf8")

def genuine_sources_pack(slug,w,ep,all_works,scenes,music):
 manifest=[obj for (_,obj) in all_works.values()]
 source_lines=["# Originali di "+w["artist"]+" — "+w["title_en"],"",
  "Tutte le riproduzioni qui usate provengono dal Cleveland Museum of Art, con designazione CC0 per ogni originale.",
  "Le immagini sono state ritagliate solo ai margini secondo le coordinate documentate; il tratto, i colori e le figure restano fedeli.",""]
 for x in manifest:
  source_lines.extend(["## "+x["title"],"Accession: "+x["accession"],
   "Opera: "+x["source_page"],"Riproduzione: "+x["source_image"],
   "Licenza: "+x["license"]+" — "+x["license_url"],
   "SHA256 originale: "+x["sha256_original"],"SHA256 versione montata: "+x["sha256_working"],""])
 source_lines.extend(["## Registrazione sonora",music["title"]+" — "+music["composer"],
   "Pagina originale: "+music["page"],"Licenza registrazione: "+music["license_url"],
   "Modifiche: estratto, volume, dissolvenze; attribuzioni in tutti i post social.",
   "Stato: diritti e condizioni da ricontrollare prima di pubblicare e monetizzare."])
 (ep/"SOURCES_AND_RIGHTS.md").write_text("\n".join(source_lines)+"\n",encoding="utf8")
 contract=ep/"ARTVISION_CONTRACT_V25.json"
 data=json.loads(contract.read_text(encoding="utf8"))
 data["sources"]=[{"id":"museum-"+x["label"],"url":x["source_page"],
   "license":"CC0 Cleveland Museum of Art (open access)",
   "credit":x["title"]+" — "+w["artist"],"status":"verified"}for x in manifest]
 for original,seq in zip(data["scenes"],scenes):
  original["source_id"]="museum-"+seq["source_id"]
 data["editorial_standard"]="artvision_editorial_v28"
 contract.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 err=check_preflight(data)
 if err:raise RuntimeError("V25 REJECTED: "+str(err))
 rec=ep/"VIDEO_RECIPE_V13.json"
 recipe=json.loads(rec.read_text(encoding="utf8"))
 recipe["renderer"]="scripts/artvision_wow10_five_v25_v28.py"
 recipe["replication_command"]=f"python scripts/artvision_wow10_five_v25_v28.py --painting {slug} --out output/artvision-wow10"
 recipe["source_assets"]=manifest
 recipe["source_collection"]="Cleveland Museum of Art, CC0, multiple authentic plates"
 recipe["sequences"]=[dict(x,source_id=x["source_id"]) for x in scenes]
 recipe["authentic_scenes_count"]=len(scenes)
 recipe["music_license_verified_page"]=music["page"]
 recipe["description_style"]="V28 museum-grounded natural captions"
 recipe["published"]=False
 recipe["source_manifest"]="COLLECTION_SOURCES_CC0.json"
 rec.write_text(json.dumps(recipe,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 instr=ep/"ISTRUZIONI_REPLICA.md"
 instr.write_text(
  "# Replica completa e verificabile — "+w["title_en"]+"\n\n"+
  "Motore Gold Master: Cinema V6 preservato, con estensione additiva multi-opera.\n"+
  "Regole: Contratto V25, regia V23, V21 e social V28.\n"+
  "Renderer: scripts/artvision_wow10_five_v25_v28.py\n"+
  "Configurazione: config/artvision_wow10_five_v25.json\n"+
  "Didascalie verificate: config/artvision_wow10_editorial_v28.json\n"+
  f"Comando: python scripts/artvision_wow10_five_v25_v28.py --painting {slug} --out output/artvision-wow10\n"+
  "Dipendenze: Python 3.11, ffmpeg, ffprobe, Pillow, numpy, requests.\n"+
  "L'archivio conserva tutti gli originali, i loro hash e le singole focali, più la registrazione audio originale.\n"+
  "Non usare un'immagine di un altro artista quando un originale non è disponibile.\n"+
  "Durata misurata, mappa delle scene e cue musicali: VIDEO_RECIPE_V13.json / MUSIC_CUE_ANALYSIS.json.\n"+
  "Pubblicazione social NON eseguita automaticamente. Revisione artistica manuale ancora necessaria.\n",
 encoding="utf8")

def render_five(slug,out):
 w=copy.deepcopy(P["works"][slug])
 ep=out/slug;ep.mkdir(parents=True,exist_ok=True)
 workdir=ep/"_work";workdir.mkdir(exist_ok=True)
 music=P["music"][w["music"]]
 ensure_v28_music_match(w,music)
 total=sum(float(x["seconds"]) for x in w["scenes"])
 assert abs(total-w["duration"])<.3,(total,w["duration"])
 assert w["scenes"][0]["seconds"]>=3.7
 all_works=load_real_museum_artworks(slug,w,ep)
 assert all(s["source_id"] in all_works for s in w["scenes"])
 hero_key=w["scenes"][0]["source_id"]
 hero,hero_meta=all_works[hero_key]
 cover_art=ep/"ASSET_ARTWORK.jpg"
 hero.save(cover_art,quality=95,subsampling=0,optimize=True)
 shutil.copy2(ep/"ARTWORKS_AUTHENTIC"/hero_meta["original_file"],ep/"ASSET_ARTWORK_ORIGINAL.jpg")
 prep={"artist":w["artist"],"original_image_url":hero_meta["source_image"],
       "source_page":hero_meta["source_page"],"original_sha256":hero_meta["sha256_original"],
       "working_image_sha256":hero_meta["sha256_working"],
       "original_master_preserved_as":"ASSET_ARTWORK_ORIGINAL.jpg",
       "process":"Museo CC0; solo ritaglio della carta, senza generazione o alterazioni dell'opera."}
 (ep/"SOURCE_PREPARATION.json").write_text(json.dumps(prep,ensure_ascii=False,indent=2)+"\n")
 track=ep/"TRACK_LICENSED.mp3"
 origin_music=engine.ORIG_FETCH([music["download"]],track,100000,"music")
 # Measured musical cut timing remains subordinate to meaningful art direction.
 sync=engine.music_cues(w,music,ep)
 compose_project(slug,w,ep,all_works)
 clips=[]
 for i,s in enumerate(w["scenes"]):
  art,_=all_works[s["source_id"]]
  still=base.shot_image(art,s)
  clip=workdir/f"scene_{i:02d}.mp4"
  base.render_shot(still,s,i,clip,workdir,w["artist"],music["composer"])
  clips.append(clip)
  print("WOW10 DIRECTED",slug,i+1,len(w["scenes"]),s["source_id"],s["purpose"],flush=True)
 concat=workdir/"concat.txt"
 concat.write_text("".join("file '"+str(c.resolve())+"'\n" for c in clips))
 silent=workdir/"silent.mp4"
 base.run("ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0",
          "-i",concat,"-c:v","copy","-movflags","+faststart",silent)
 duration=float(base.ffprobe(silent)["format"]["duration"])
 video=ep/"VIDEO_MASTER.mp4"
 base.run("ffmpeg","-hide_banner","-loglevel","error","-y","-i",silent,"-i",track,
     "-map","0:v:0","-map","1:a:0","-c:v","copy",
     "-af",f"aresample=48000,volume=.85,afade=t=in:st=0:d=0.45,afade=t=out:st={max(0,duration-2.8):.3f}:d=2.8",
     "-c:a","aac","-b:a","192k","-t",f"{duration:.3f}","-movflags","+faststart",video)
 cover=ep/"COPERTINA.jpg"
 base.create_cover(base.shot_image(hero,w["scenes"][0]),w,music,cover)
 qa=ep/"QA_V25";qa.mkdir(exist_ok=True)
 for sec in [0,1,3,5,7]+[duration*p for p in (.24,.49,.76,.96)]:
  sec=round(float(sec),2)
  fname=(f"FRAME_{int(sec):02d}.jpg" if sec in [0,1,3,5,7]
         else f"FRAME_EXTRA_{sec:.2f}.jpg")
  base.run("ffmpeg","-hide_banner","-loglevel","error","-y","-ss",str(sec),
    "-i",video,"-frames:v","1","-q:v","3",qa/fname)
 # Produce V25/V28 package, extended below with *all* true source credits.
 err=base.write_release_package(slug,w,music,hero_meta["source_image"],origin_music,
     cover_art,track,video,cover,ep,w["scenes"],{"at_seconds":[0,1,3,5,7],"qa_folder":"QA_V25"})
 if err:raise RuntimeError("V25 first preflight failed: "+str(err))
 genuine_sources_pack(slug,w,ep,all_works,w["scenes"],music)
 base.run("ffmpeg","-hide_banner","-loglevel","error","-xerror","-i",video,"-f","null","-",timeout=210)
 verify=base.ffprobe(video)
 assert abs(float(verify["format"]["duration"])-w["duration"])<1.5
 assert any(x.get("codec_type")=="video" and x.get("width")==1080 and x.get("height")==1920 and x.get("codec_name")=="h264" for x in verify["streams"])
 assert any(x.get("codec_type")=="audio" and x.get("codec_name")=="aac" for x in verify["streams"])
 assert not any(x.get("codec_type")=="subtitle" for x in verify["streams"])
 # V17, V21, V20 and V28 checks + clean package, inherited from vetted batch.
 engine.finish_episode(slug,w,ep,out,sync)
 genuine_sources_pack(slug,w,ep,all_works,w["scenes"],music)
 # engine.finish_episode recreates one ZIP before our multi-source documentation
 # is final; regenerate the archive from the episode with no old master changes.
 zip_path=out/f"ARTVISION_WOW10_{slug.upper()}_COMPLETE.zip"
 with zipfile.ZipFile(zip_path,"w",allowZip64=True) as z:
  for file in ep.rglob("*"):
   if file.is_file() and "_work" not in file.parts:
    method=zipfile.ZIP_STORED if file.suffix.lower() in (".mp4",".mp3",".jpg") else zipfile.ZIP_DEFLATED
    z.write(file,file.relative_to(ep),compress_type=method)
 assert zipfile.ZipFile(zip_path).testzip() is None
 report={"title":w["title_en"],"artist":w["artist"],"status":"RENDERED_NEEDS_ARTISTIC_REVIEW",
         "duration_seconds":float(verify["format"]["duration"]),
         "mp4_size_bytes":video.stat().st_size,
         "master_sha256":digest(video),"visual_originals":len(all_works),
         "shots":len(w["scenes"]),"qa":"FFprobe + full ffmpeg decode + V25 V28 + V17 V21",
         "publication":"NOT_PUBLISHED","release_status":"MANUAL_ARTISTIC_REVIEW_REQUIRED",
         "preserve_approved_gold_masters":True}
 (ep/"WOW10_DELIVERY_REPORT.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
 # Include the final report as the last file in ZIP.
 with zipfile.ZipFile(zip_path,"a") as z:z.write(ep/"WOW10_DELIVERY_REPORT.json","WOW10_DELIVERY_REPORT.json")
 shutil.rmtree(workdir)
 print("WOW10 FINAL",slug,report["duration_seconds"],report["mp4_size_bytes"],
       "artworks",len(all_works),"zip",zip_path.stat().st_size,flush=True)

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--painting",choices=sorted(P["works"]),required=True)
 parser.add_argument("--out",default="output/artvision-wow10")
 args=parser.parse_args()
 out=ROOT/args.out;out.mkdir(parents=True,exist_ok=True)
 render_five(args.painting,out)
if __name__=="__main__":main()
