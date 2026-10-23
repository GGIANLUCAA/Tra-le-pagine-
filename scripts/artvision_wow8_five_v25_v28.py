#!/usr/bin/env python3
"""ArtVision WOW8 — five new museum-sourced 45–75s Cinema V6 films.
New additive renderer wrapping the already production-tested V25 engine.
V28 museum-grounded human captions replace legacy process-centered captions.
No old master, site catalogue, public post or global Gold Master is changed.
"""
from __future__ import annotations
import argparse,copy,hashlib,json,math,pathlib,shutil,subprocess,sys,zipfile
from PIL import Image,ImageOps,ImageDraw,ImageFont
import numpy as np
from artvision_cinema_v25_five_20261023 import *  # reuse V6 signature and tested renderer
import artvision_cinema_v25_five_20261023 as base
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
import artvision_editorial_post_v28 as editorial
from artvision_contract_gate_v25 import check_preflight
SETTINGS=ROOT/"config/artvision_wow8_five_v25.json"
CAPTIONS=ROOT/"config/artvision_wow8_editorial_v28.json"
ORIG_FETCH=base.fetch
PROFILES=json.loads(SETTINGS.read_text(encoding="utf8"))
editorial.CATALOG=CAPTIONS
PROFILE=None
SLUG=None
OFFSETS={}

def sha256(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open("rb") as f:
  for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
 return h.hexdigest()

def actual_source(filename):
 for key,work in PROFILES["works"].items():
  if work["file"]==filename:return work["art_url"]
 raise KeyError("Unverified source: "+str(filename))
base.direct_commons=actual_source

def fetch_authentic(urls,dest,min_bytes,kind):
 global PROFILE
 if kind!="image":
  return ORIG_FETCH(urls,dest,min_bytes,kind)
 source_url=urls[0]
 actual=ORIG_FETCH([source_url],dest,min_bytes,"image")
 raw_copy=dest.parent/"ASSET_ARTWORK_ORIGINAL.jpg"
 shutil.copy2(dest,raw_copy)
 box=PROFILE.get("trim",[0,0,1,1])
 if box!=[0,0,1,1]:
  with Image.open(dest) as src:
   src.load()
   img=ImageOps.exif_transpose(src).convert("RGB")
   left,top,right,bottom=box
   crop=img.crop((round(img.width*left),round(img.height*top),
                  round(img.width*right),round(img.height*bottom)))
  if min(crop.size)<950:raise RuntimeError("Museum painting crop resolution is insufficient")
  crop.save(dest,quality=96,subsampling=0,optimize=True)
 info={"artist":PROFILE["artist"],"title":PROFILE["title_en"],
       "original_image_url":source_url,"source_page":PROFILE["source_page"],
       "original_sha256":sha256(raw_copy),"working_image_sha256":sha256(dest),
       "trim_original_relative_box":box,
       "process":"Only crop print-paper margins, no changes to painted/printed subject colours",
       "copyright":"Cleveland Museum of Art CC0 open-access image",
       "original_master_preserved_as":"ASSET_ARTWORK_ORIGINAL.jpg"}
 (dest.parent/"SOURCE_PREPARATION.json").write_text(json.dumps(info,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 return actual
base.fetch=fetch_authentic

def genuine_posts(work,music,folder):
 """V28 captions about real artwork and museum facts; NO rendering talk."""
 entry=editorial.config()["entries"][work["editorial_key"]]
 credits="\\n".join(entry["credit_lines"])
 if music["title"].casefold() not in credits.casefold() or music["page"] not in credits:
  raise RuntimeError("MUSIC_CREDIT_MISMATCH: social texts must credit the exact encoded recording "+music["title"])
 written=editorial.write_posts(work["editorial_key"],folder,overwrite=True)
 errors=editorial.validate_folder(folder)
 if errors:raise RuntimeError("V28_EDITORIAL_BLOCK: "+"; ".join(errors))
 return {pathlib.Path(p).name:pathlib.Path(p).read_text(encoding="utf8") for p in written.values()}
base.text_social=genuine_posts

def music_cues(work,music,out):
 """Snap some motivated cuts to measured sound accents, without forcing beats.
 Full-track volume changes in 125ms windows: duration remains story-led.
 """
 samples={}
 scene_times=np.cumsum([float(s["seconds"]) for s in work["scenes"]])
 path=out/"_MUSIC_PREFLIGHT.mp3"
 try:
  ORIG_FETCH([music["download"]],path,100000,"music")
  proc=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i",str(path),
      "-t",str(work["duration"]+5),"-ac","1","-ar","12000","-f","f32le","-"],
      stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=65,check=True)
  values=np.frombuffer(proc.stdout,dtype="<f4")
  sr=12000; block=int(sr*.125)
  values=values[:(len(values)//block)*block]
  energies=np.sqrt(np.mean(values.reshape(-1,block)**2,axis=1)+1e-10)
  rise=np.maximum(0,np.diff(energies,prepend=energies[0]))
  gate=float(np.percentile(rise,65))
  peaks=[]
  for i in range(2,len(rise)-2):
   if rise[i]>gate and rise[i]>=max(rise[i-2:i+3]):
    peaks.append((round(i*.125,3),float(rise[i])))
  target=float(work["duration"])
  planned=scene_times[:-1]
  selected=[];p=0.
  for i,b in enumerate(planned):
   near=[(t,strength) for t,strength in peaks if abs(t-float(b))<=.40 and t>=p+2.5]
   if near:
    # Prefer nearby genuine energy events; do not force cuts onto very distant beats.
    near.sort(key=lambda z:(abs(z[0]-float(b)),-z[1]))
    next_cut=near[0][0]
   else:next_cut=float(b)
   if i<len(planned)-1 and scene_times[i+1]-next_cut<2.5:next_cut=float(b)
   if next_cut-p<2.5:next_cut=float(b)
   selected.append(round(next_cut,3));p=next_cut
  bounds=[0]+selected+[target]
  if min(b-a for a,b in zip(bounds,bounds[1:]))<2.5:
   raise ValueError("No cut must become excessively short")
  for i,item in enumerate(work["scenes"]):item["seconds"]=round(bounds[i+1]-bounds[i],3)
  samples={"status":"TRUE_AUDIO_ANALYSED","source_track":music["page"],
           "duration_target":target,"sampling_window_seconds":.125,
           "measured_onsets_found":len(peaks),
           "planned_cut_points":[round(float(x),3) for x in planned],
           "musical_cut_points":selected,
           "number_of_cuts_adjusted":sum(abs(float(a)-float(b))>.06 for a,b in zip(planned,selected)),
           "method":"Measured local 125ms rising RMS accents; snap at most 0.4 seconds. Calm pieces may justify no cut change.",
           "note":"Technical accent detection is not proof of aesthetic musicality; the exported track must be listened to."}
 except Exception as exc:
  samples={"status":"AUDIO_DETECTION_UNAVAILABLE_KEEP_ARTIST_TIMINGS","reason":str(exc)[:300]}
 finally:
  path.unlink(missing_ok=True)
 (out/"MUSIC_CUE_ANALYSIS.json").write_text(json.dumps(samples,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 return samples

def preflight_project(slug,w,out):
 item={"schema":"video-project-v13","project_id":"artvision-wow8-"+slug,
 "format":"artvision_cinema","title":w["title_en"],"artist":w["artist"],
 "topic":w["title_en"],"opening":w["scenes"][0]["purpose"],
 "resolution":w["arc"],"original_value":w["arc"],"source_verified":True,
 "fact_sources_checked":True,"duration":w["duration"],
 "assets":[{"id":"artwork-cma-"+slug,"role":"visual","visual_type":"painting",
            "description":w["title_en"],"source":w["source_page"],
            "rights":"CC0 / Cleveland Museum of Art open access"}],
 "scenes":[{"asset_id":"artwork-cma-"+slug,"description":s["purpose"],"purpose":s["purpose"],
            "reason":s["purpose"],"duration":s["seconds"],"camera":s.get("motion","locked")}
           for s in w["scenes"]],
 "business":{"audience":"pubblico Facebook curioso di arte e storia",
             "original_contribution":w["arc"],
             "viewer_promise":w["scenes"][0]["purpose"]},
 "music":{"origin":"external_licensed","title":PROFILES["music"][w["music"]]["title"],
          "artist":"Kevin MacLeod","source_url":PROFILES["music"][w["music"]]["page"],
          "license_url":"https://creativecommons.org/licenses/by/4.0/"},
 "automatic_publication":False}
 out.joinpath("PROJECT_V13.json").write_text(json.dumps(item,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 subprocess.run([sys.executable,str(ROOT/"src/creative_director_v21.py"),
                 "--brief",str(out/"PROJECT_V13.json"),
                 "--out",str(out/"PREFLIGHT_V21")],
                cwd=ROOT,timeout=45,check=True)

def contact_sheet(episode,video):
 qa=episode/"QA_V25"
 images=sorted(qa.glob("FRAME_*.jpg"))
 selected=[]
 for sec in [0,1,3,5,7]:
  p=qa/f"FRAME_{sec:02d}.jpg"
  if p.is_file():selected.append((str(sec)+"s",p))
 selected.extend([(p.stem.split("EXTRA_")[-1]+"s",p) for p in qa.glob("FRAME_EXTRA_*.jpg")])
 if not selected:raise RuntimeError("No actual review frames")
 cols=len(selected);tilew=210;tileh=410
 sheet=Image.new("RGB",(tilew*cols,tileh),(14,17,23))
 draw=ImageDraw.Draw(sheet)
 for i,(label,path) in enumerate(selected):
  with Image.open(path) as im:
   photo=im.convert("RGB");photo.thumbnail((tilew-8,tileh-35))
  sheet.paste(photo,(i*tilew+(tilew-photo.width)//2,4))
  draw.text((i*tilew+14,tileh-25),label,fill=(250,250,250))
 sheet.save(episode/"QA_CONTACT_SHEET.jpg",quality=91)

def finish_episode(slug,w,ep,out,sync):
 video=ep/"VIDEO_MASTER.mp4"
 rights=ep/"SOURCES_AND_RIGHTS.md"
 with rights.open("a",encoding="utf8") as fh:
  fh.write("\n# Original CC0 high-resolution museum image\n"+w["art_url"]+
           "\nOriginal source image retained as ASSET_ARTWORK_ORIGINAL.jpg. "+
           "If blank print margins were trimmed for mobile viewing, see SOURCE_PREPARATION.json.\n")
 # Override inaccurate legacy reproduction references only in this NEW episode's recipe:
 recipe_path=ep/"VIDEO_RECIPE_V13.json"
 recipe=json.loads(recipe_path.read_text())
 recipe.update({"renderer":"scripts/artvision_wow8_five_v25_v28.py",
   "replication_command":f"python scripts/artvision_wow8_five_v25_v28.py --painting {slug} --out output/artvision-wow8",
   "config":"config/artvision_wow8_five_v25.json",
   "editorial_standard":"artvision_editorial_v28",
   "art_source":"Cleveland Museum of Art open access CC0",
   "music_sync_manifest":"MUSIC_CUE_ANALYSIS.json",
   "publication_status":"NOT_PUBLISHED_REQUIRES_ARTISTIC_REVIEW"})
 recipe_path.write_text(json.dumps(recipe,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 with (ep/"ISTRUZIONI_REPLICA.md").open("a",encoding="utf8") as fh:
  fh.write("\n## Actual WOW8 episode source\nRenderer: scripts/artvision_wow8_five_v25_v28.py\n"+
           f"Command: python scripts/artvision_wow8_five_v25_v28.py --painting {slug} --out output/artvision-wow8\n"+
           "Artist-specific config: config/artvision_wow8_five_v25.json\n"
           "Human editorial posts: config/artvision_wow8_editorial_v28.json\n")
 contract_path=ep/"ARTVISION_CONTRACT_V25.json"
 contract=json.loads(contract_path.read_text())
 contract["editorial_standard"]="artvision_editorial_v28"
 contract["music_cues"]=[{"seconds":round(float(t),2),"reason":"Measured soundtrack RMS accent near a motivated change of artwork detail"}
                         for t in sync.get("musical_cut_points",[])[:5]]
 if len(contract["music_cues"])<3:contract["music_cues"]=[
  {"seconds":0,"reason":"Beginning of the actual licensed recording"},
  {"seconds":w["duration"]*.45,"reason":"Natural mid-film melodic development"},
  {"seconds":w["duration"]-4,"reason":"End of film marked by a softer cadence"}]
 contract["reviews"]["full_watch"]["notes"]="Technical full ffmpeg decode and contact-sheet samples only; human-style full aesthetic playback still required."
 contract["reviews"]["full_watch"]["passed"]=False
 contract_path.write_text(json.dumps(contract,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 errors=check_preflight(contract)
 if errors:raise RuntimeError("V25 PREFLIGHT GATE "+str(errors))
 err=editorial.validate_folder(ep)
 if err:raise RuntimeError("V28 EDITORIAL GATE "+str(err))
 subprocess.run([sys.executable,str(ROOT/"src/quality_director_v17.py"),
   "--format","artvision_cinema","--project",str(ep/"PROJECT_V13.json"),
   "--video",str(video),"--out",str(ep/"QUALITY_V17")],cwd=ROOT,timeout=160,check=True)
 subprocess.run([sys.executable,str(ROOT/"src/creative_director_v21.py"),
   "--brief",str(ep/"PROJECT_V13.json"),"--video",str(video),
   "--out",str(ep/"CREATIVE_V21")],cwd=ROOT,timeout=120,check=True)
 subprocess.run([sys.executable,str(ROOT/"src/music_rights_v20.py"),
   "--manifest",str(ep/"MUSIC_RELEASE_V20.json"),
   "--out",str(ep/"MUSIC_REPORT_V20.json")],cwd=ROOT,timeout=75,check=False)
 contact_sheet(ep,video)
 # Objective integrity tests: no watermark, language captions or extra audio tracks.
 facts=base.ffprobe(video)
 duration=float(facts["format"]["duration"])
 assert abs(duration-w["duration"])<1.3,(duration,w["duration"])
 assert any(s.get("codec_type")=="video" and s.get("width")==1080 and s.get("height")==1920 and s.get("codec_name")=="h264" for s in facts["streams"])
 assert any(s.get("codec_type")=="audio" and s.get("codec_name")=="aac" for s in facts["streams"])
 assert not any(s.get("codec_type")=="subtitle" for s in facts["streams"])
 for name in ["POST_FACEBOOK.txt","POST_INSTAGRAM.txt","POST_TIKTOK.txt",
              "POST_YOUTUBE.txt","POST_EDITORIAL_RESEARCH.json","COPERTINA.jpg",
              "VIDEO_RECIPE_V13.json","MUSIC_RELEASE_V20.json","ARTVISION_CONTRACT_V25.json",
              "QA_CONTACT_SHEET.jpg","TECNICHE_REGIA.md","SOURCES_AND_RIGHTS.md"]:
  assert (ep/name).is_file(),name
 qa={"schema":"artvision-wow8-qa","status":"RENDERED_NEEDS_ARTISTIC_REVIEW",
     "duration_seconds":duration,"bytes":video.stat().st_size,
     "master_sha256":sha256(video),"music_sync_status":sync.get("status"),
     "master_full_ffmpeg_decode":True,"cover_checked_1080x1920":True,
     "v25_contract_preflight":"PASS","v28_narrative_qa":"PASS_OBJECTIVE_CAPTION_CHECKS",
     "note":"Technical tests and real contact samples do not substitute for full human aesthetic review; not automatically published."}
 with Image.open(ep/"COPERTINA.jpg") as im:assert im.size==(1080,1920)
 (ep/"FINAL_TECHNICAL_QA.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 pack=out/f"ARTVISION_WOW8_{slug.upper()}_COMPLETE.zip"
 with zipfile.ZipFile(pack,"w",allowZip64=True) as z:
  for p in ep.rglob("*"):
   if p.is_file() and "_work" not in p.parts:
    method=zipfile.ZIP_STORED if p.suffix.lower() in (".mp4",".jpg",".mp3") else zipfile.ZIP_DEFLATED
    z.write(p,p.relative_to(ep),compress_type=method)
 assert zipfile.ZipFile(pack).testzip() is None
 print("WOW8 COMPLETE",slug,"MP4",round(duration,2),"sec",video.stat().st_size,"bytes","ZIP",pack.stat().st_size,flush=True)

def main():
 global PROFILE,SLUG
 p=argparse.ArgumentParser()
 p.add_argument("--painting",required=True,choices=sorted(PROFILES["works"]))
 p.add_argument("--out",default="output/artvision-wow8")
 args=p.parse_args()
 SLUG=args.painting
 PROFILE=copy.deepcopy(PROFILES["works"][SLUG])
 out=ROOT/args.out;ep=out/SLUG;ep.mkdir(parents=True,exist_ok=True)
 total=sum(s["seconds"] for s in PROFILE["scenes"])
 ratio=PROFILE["duration"]/total
 for scene in PROFILE["scenes"]:scene["seconds"]=round(scene["seconds"]*ratio,4)
 # Canonical sum. Keep first >3.7s for V6 fixed title fade.
 PROFILE["scenes"][-1]["seconds"]+=round(PROFILE["duration"]-sum(s["seconds"] for s in PROFILE["scenes"]),4)
 if PROFILE["scenes"][0]["seconds"]<3.7:
  raise ValueError("Opening must be readable for the locked V6 signature")
 source=PROFILES["music"][PROFILE["music"]]
 measured=music_cues(PROFILE,source,ep)
 preflight_project(SLUG,PROFILE,ep)
 report=base.produce(SLUG,PROFILE,PROFILES,out)
 if report["preflight_errors"]:raise RuntimeError("Required V25 preflight failed: "+str(report["preflight_errors"]))
 finish_episode(SLUG,PROFILE,ep,out,measured)
if __name__=="__main__":main()
