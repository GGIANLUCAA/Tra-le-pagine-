#!/usr/bin/env python3
"""ONLY La Storia Rivive / new silent-cinema social episodes, source-locked review candidates.
Reuses the successfully rendered Magicien V1 pipeline; distinct real films and real free I2I.
FAIL CLOSED: do not publish, no paid API, no Vidu POST. Review photo/frame personally first.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, pathlib, shutil, sys, zipfile, os
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import cv2
import numpy as np

ROOT=pathlib.Path(__file__).resolve().parents[1]
PROFILES={
 "martinetti_1894":{
  "filename":"Luis Martinetti, Contortionist (1894).webm",
  "label":"LUIS MARTINETTI","year":1894,"short":"LUIS MARTINETTI · 1894",
  "author":"Edison Kinetoscope film, W. K. L. Dickson","death":1935,
  "start":0.2,"length":13.5,
  "min_bytes":27000000,"max_bytes":33000000,"min_width":1420,"min_height":1020,
  "prompt":("Photorealistic faithful restoration of this EXACT real 1894 Edison film frame, filmed contortionist Luis Martinetti, one REAL historical adult man in the exact source pose, in his original period athletic clothing, with the very same rings and stage elements ONLY if present in the source. Keep his actual face, gaze, posture, body proportions, limb count, fabric and exact camera perspective. High-resolution contemporary documentary photographic appearance: believable skin pores, natural eyes, precise nose and lips, individual hair strands and original clothing weave, physical light and real photographic texture. Restrained natural colors and no invented person, props or altered identity. This is a source-locked interpretation, not a new scene."),
  "neg":"new person, duplicate man, extra arms, extra feet, floating hand, extra gymnastic ring, removed ring, replacement clothing, costume change, modern studio props, horns, invented face, crossed eyes, asymmetrical eyes, portrait painting, CGI, illustration, doll skin, wax face, oversaturated orange, purple",
  "description":"Luis Martinetti performs genuine contortion movements in an Edison Kinetoscope film from 1894. The moving film is authentic; the color photograph is an AI interpretation."
 }
}
def digest(path):
 h=hashlib.sha256()
 with open(path,"rb") as f:
  for chunk in iter(lambda:f.read(1<<20),b""):h.update(chunk)
 return h.hexdigest()
def save(out,name,obj):
 (out/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--reuse-artifact-dir",default="",help="Reuse exact earlier free I2I result after source lock SHA+frame match; never duplicate paid calls")
 ap.add_argument("--episode",required=True,choices=sorted(PROFILES))
 args=ap.parse_args()
 profile=PROFILES[args.episode]
 sys.path.insert(0,str(ROOT/"src"))
 spec=importlib.util.spec_from_file_location("storia_magicien_template",ROOT/"src/storia_cinema_magicien_1898_visual_social_v1.py")
 m=importlib.util.module_from_spec(spec)
 sys.modules[spec.name]=m
 spec.loader.exec_module(m)
 key=args.episode
 output=ROOT/"output"/("storia_serial_"+key)
 output.mkdir(parents=True,exist_ok=True)
 m.OUT=output
 m.PAGE="https://commons.wikimedia.org/wiki/File:"+profile["filename"].replace(" ","_")
 m.SOURCE=output/("SOURCE_"+key+".webm")
 m.CLIP=output/"REAL_FILM_EXCERPT.mp4"
 m.MOVIE=output/(key.upper()+"_SOCIAL_REVIEW.mp4")
 m.ZIP=output/(key.upper()+"_SOCIAL_REVIEW_WITH_SOCIAL.zip")
 m.START=profile["start"]
 m.DURATION=profile["length"]
 m.ANCHOR=round(1.15*m.FPS)
 m.HOLD=round(1.85*m.FPS)
 original_frame_canvas=m.frame_canvas
 def frame_canvas(scene,title="",small=""):
  if "LE MAGICIEN" in title:title=profile["short"]
  if "MÉLIÈS" in small:small="ARCHIVAL MOVING FILM · "+str(profile["year"])
  return original_frame_canvas(scene,title,small)
 m.frame_canvas=frame_canvas
 def source():
  ua="LaStoriaRiviveSeries/1.0 (+https://github.com/GGIANLUCAA/Tra-le-pagine-)"
  api="https://commons.wikimedia.org/w/api.php?"+urlencode({
     "action":"query","format":"json","formatversion":"2","prop":"imageinfo",
     "titles":"File:"+profile["filename"],"iiprop":"url|size|mime"})
  with urlopen(Request(api,headers={"User-Agent":ua}),timeout=35) as response:
   data=json.load(response)
  info=data["query"]["pages"][0]["imageinfo"][0]
  assert info["mime"].startswith("video/"),"SOURCE_IS_NOT_VIDEO"
  bytes_expected=int(info["size"])
  assert profile["min_bytes"]<=bytes_expected<=profile["max_bytes"],("SOURCE_SIZE_MISMATCH",bytes_expected)
  source_url=info["url"]
  if not m.SOURCE.exists() or m.SOURCE.stat().st_size!=bytes_expected:
   with urlopen(Request(source_url,headers={"User-Agent":ua}),timeout=120) as response, m.SOURCE.open("wb") as file:
    while True:
     chunk=response.read(1<<20)
     if not chunk:break
     file.write(chunk)
     if file.tell()>profile["max_bytes"]: raise RuntimeError("WRONG_SOURCE_SIZE")
  assert m.SOURCE.stat().st_size==bytes_expected,"INCOMPLETE_SOURCE_BYTES"
  cap=cv2.VideoCapture(str(m.SOURCE))
  w=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH));h=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
  fps=float(cap.get(cv2.CAP_PROP_FPS));n=cap.get(cv2.CAP_PROP_FRAME_COUNT)
  cap.release()
  assert w>=profile["min_width"] and h>=profile["min_height"] and fps>10 and n/fps>m.START+m.DURATION+1,("SOURCE_WRONG_METADATA",w,h,fps,n)
  m.run(["ffmpeg","-nostdin","-y","-v","error","-ss",str(m.START),"-i",str(m.SOURCE),
         "-t",str(m.DURATION),"-vf","fps=24,scale=960:720","-an",
         "-c:v","libx264","-preset","veryfast","-crf","18","-pix_fmt","yuv420p",str(m.CLIP)],320)
  c=cv2.VideoCapture(str(m.CLIP))
  count=int(c.get(cv2.CAP_PROP_FRAME_COUNT));rate=float(c.get(cv2.CAP_PROP_FPS))
  c.release()
  assert abs(rate-24)<.1 and count>=int(m.DURATION*24)-5,("EXCERPT_NOT_DECODED",count,rate)
  # Real archival files may deliver one fewer CFR frame than requested, do not request a nonexistent last frame.
  if count<int(m.DURATION*m.FPS):
   m.DURATION=(count-1)/m.FPS
   print("TRUE_FILM_TRUNCATE_TO_LAST_DECODED_FRAME",count,m.DURATION,flush=True)
  # Real motion must be visible, not a static intertitle or zoom-only still.
  cap=cv2.VideoCapture(str(m.CLIP))
  samples=[]
  for j in [12,24,48,72]:
   cap.set(cv2.CAP_PROP_POS_FRAMES,j);ok,a=cap.read()
   cap.set(cv2.CAP_PROP_POS_FRAMES,j+12);ok2,b=cap.read()
   if ok and ok2:
    samples.append(float(np.mean(cv2.absdiff(cv2.resize(a,(160,120)),cv2.resize(b,(160,120))))))
  cap.release()
  assert np.median(samples)>1.0,("NOT_ENOUGH_REAL_MOVEMENT",samples)
  save(output,"RIGHTS.json",{
   "film":profile["label"],"year":profile["year"],"author":profile["author"],
   "author_latest_death_year":profile["death"],"source_commons":m.PAGE,"source_download_url":source_url,
   "source_sha256":digest(m.SOURCE),"source_size":bytes_expected,"scan_resolution":[w,h],"source_fps":fps,
   "excerpt_start_s":m.START,"excerpt_length_s":m.DURATION,"real_motion_diffs":samples,
   "rights_note":"Work published before 1931, US PD; known creator(s) died before 1956, Italian life+70 term elapsed. Commons file rights must be honored separately.",
   "colors_are_interpretations_not_original":True,"no_social_publication":True,
   "no_paid_calls":True,"no_vidu_generated":True})
  return m.CLIP
 m.source=source
 def photo(base,original):
  m.cv2.imwrite(str(output/"ANCHOR_REAL_ORIGINAL_BW.png"),original)
  m.cv2.imwrite(str(output/"ANCHOR_AI_NEURAL_COLOR_BASE.png"),base)
  trial={"source":m.PAGE,"service":"finegrain/finegrain-image-enhancer","real_free_I2I_created":False,
         "status":"NOT_ATTEMPTED","paid_calls":0,"artistic_review":"PENDING","source_frame_idx":m.ANCHOR}
  try:
   if args.reuse_artifact_dir:
    folder=pathlib.Path(args.reuse_artifact_dir)
    oldrights=json.loads((folder/"RIGHTS.json").read_text())
    currentrights=json.loads((output/"RIGHTS.json").read_text())
    if oldrights["source_sha256"]!=currentrights["source_sha256"]:
     raise RuntimeError("REUSING_PHOTO_FROM_DIFFERENT_ARCHIVAL_FILE_FORBIDDEN")
    prior=cv2.imread(str(folder/"ANCHOR_REAL_ORIGINAL_BW.png"))
    if prior is None or prior.shape!=original.shape:
     raise RuntimeError("PHOTO_REUSE_SOURCE_ANCHOR_MISSING")
    delta=float(np.mean(np.abs(prior.astype(np.int16)-original.astype(np.int16))))
    if delta>1.0:raise RuntimeError("PHOTO_REUSE_FRAME_MISMATCH "+str(delta))
    previous=json.loads((folder/"PHOTO_QA.json").read_text())
    if previous.get("status")!="REAL_PHOTO_TECHNICAL_GATE_PASS_ARTISTIC_QA_PENDING":
     raise RuntimeError("PHOTO_REUSE_PRIOR_GATE_NOT_PASS")
    pic=cv2.imread(str(folder/"GENERATIVE_PHOTO_REAL_CANDIDATE.png"))
    if pic is None or pic.shape!=original.shape:raise RuntimeError("PHOTO_REUSE_PRIOR_PIXELS_MISSING")
    cv2.imwrite(str(output/"GENERATIVE_PHOTO_REAL_CANDIDATE.png"),pic)
    trial.update({"real_free_I2I_created":True,"status":"PHOTO_REUSED_FROM_PRIOR_REAL_FREE_I2I_NO_NEW_CALL",
       "old_photo_sha256":digest(folder/"GENERATIVE_PHOTO_REAL_CANDIDATE.png"),
       "source_frame_pixel_abs_delta":round(delta,5),"new_provider_calls":0,
       "source_corr":m.corr(original,pic)})
    save(output,"PHOTO_QA.json",trial)
    print("REUSED_EXACT_PREVIOUS_FINEGRAIN_PHOTO_NO_NEW_API_POST",flush=True)
    return pic
   token=os.environ.get("HF_TOKEN","").strip()
   if not token: raise RuntimeError("HF_TOKEN_NOT_AVAILABLE__DO_NOT_REPEAT_ANONYMOUS_ZERO_GPU")
   client=m.Client("finegrain/finegrain-image-enhancer",hf_token=token,verbose=False)
   raw=client.predict(m.handle_file(str(output/"ANCHOR_AI_NEURAL_COLOR_BASE.png")),
       profile["prompt"],profile["neg"],profile["year"],2,1.14,.97,6,112,144,.45,18,"DDIM",api_name="/process")
   obj=raw[1] if isinstance(raw,(list,tuple)) and len(raw)>1 else raw
   if isinstance(obj,dict):obj=obj.get("path")
   pic=m.cv2.imread(str(obj))
   if pic is None:raise RuntimeError("REAL_FREE_I2I_PHOTO_MISSING")
   pic=m.cv2.resize(pic,(960,720))
   corr_source=m.corr(original,pic);corr_base=m.corr(base,pic)
   hsv=m.cv2.cvtColor(pic,m.cv2.COLOR_BGR2HSV)
   sat=float(hsv[:,:,1].mean())
   diff=float(m.np.abs(pic.astype(m.np.float32)-base.astype(m.np.float32)).mean())
   m.cv2.imwrite(str(output/"GENERATIVE_PHOTO_REAL_CANDIDATE.png"),pic)
   trial.update({"real_free_I2I_created":True,"source_corr":round(corr_source,4),"color_corr":round(corr_base,4),
                 "mean_saturation":round(sat,2),"delta_from_base":round(diff,2)})
   if corr_source<.78 or corr_base<.80 or not (20<sat<150) or diff<2.0:
    trial["status"]="TECHNICAL_IDENTITY_COLOR_GATE_FAIL"
    raise RuntimeError("REJECTED_PHOTO_IDENTITY_COLOR")
   trial["status"]="REAL_PHOTO_TECHNICAL_GATE_PASS_ARTISTIC_QA_PENDING"
   save(output,"PHOTO_QA.json",trial)
   return pic
  except Exception as e:
   if trial["status"]=="NOT_ATTEMPTED":trial["status"]="PROVIDER_UNAVAILABLE"
   trial["error"]=type(e).__name__+": "+str(e)[:300]
   save(output,"PHOTO_QA.json",trial)
   raise
 m.photo=photo
 # Real prior successful renderer, with titles overridden to distinguish new films.
 m.main()
 # New original, restrained instrumental bed; no sampled copyrighted tune.
 import wave, math
 v=pathlib.Path(m.MOVIE)
 import subprocess
 pr=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","json",str(v)]))
 duration=float(pr["format"]["duration"])
 sr=22050
 t=np.arange(int(duration*sr),dtype=np.float64)/sr
 sound=np.zeros_like(t)
 for i,(freq,amplitude) in enumerate([(146.83,.11),(174.61,.045),(220.0,.032),(293.66,.017)]):
  sound+=amplitude*(np.sin(2*np.pi*freq*t)+.12*np.sin(2*np.pi*2*freq*t))
 sound*=np.minimum(1,np.maximum(0,t/.8))*np.minimum(1,np.maximum(0,(duration-t)/1.1))
 sound=np.tanh(sound*1.3)
 wav=output/"ORIGINAL_SUBTLE_MUSIC.wav"
 with wave.open(str(wav),"wb") as f:
  f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr)
  f.writeframes((sound*32767).astype(np.int16).tobytes())
 tmp=output/"MARTINETTI_WITH_AUDIO.tmp.mp4"
 m.run(["ffmpeg","-nostdin","-y","-v","error","-i",str(v),"-i",str(wav),
        "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","96k",
        "-t",str(duration),"-movflags","+faststart",str(tmp)],150)
 tmp.replace(v)
 m.run(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(v),"-f","null","-"],180)
 meta=json.loads((output/"VISUAL_REPORT.json").read_text())
 meta.update({"sha256":digest(v),"bytes":v.stat().st_size,
  "original_subtle_music":True,"audio_codec":"aac","new_source":"Luis Martinetti 1894",
  "artistic_review":"PENDING","no_vidu":True})
 save(output,"VISUAL_REPORT.json",meta)
 post={
 "FACEBOOK":f'{profile["label"]} · {profile["year"]}\n{profile["description"]}\nSource: {m.PAGE}\nReview copy only; not yet published.',
 "INSTAGRAM":f'{profile["label"]} · {profile["year"]} 🎞️\nAuthentic moving film and a source-matched AI photo. Visual restoration preview.\n#SilentCinema #History',
 "TIKTOK":f'{profile["year"]}: {profile["label"]}. Real archival film in motion, one modern AI photographic interpretation. #EarlyCinema',
 "YOUTUBE":f'{profile["label"]} · {profile["year"]} | REAL ORIGINAL FILM + AI PHOTO\n\n{profile["description"]}\nFilm source: {m.PAGE}\nRestored imagery is interpretative, not original recorded colors.'
 }
 for platform,body in post.items():
  (output/("POST_"+platform+".txt")).write_text(body+"\n",encoding="utf-8")
 (output/"README_REVIEW_ONLY.txt").write_text(
  "NOT ARTISTICALLY APPROVED. One real free image-to-image still; true B/W moving footage, historic-motion recoloring, NOT fully photorealistic image-to-video. No Vidu or paid calls. Do not publish. Film rights/source in RIGHTS.json.\n",encoding="utf-8")
 with zipfile.ZipFile(m.ZIP,"r") as prior:
  names=prior.namelist()
 temp=output/"REPACK_CHECKED.zip"
 with zipfile.ZipFile(temp,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=4) as arch:
  for name in names:
   if not (output/name).is_file():raise RuntimeError("PACKAGE_FILE_MISSING "+name)
   arch.write(output/name,arcname=name)
 temp.replace(m.ZIP)
 with zipfile.ZipFile(m.ZIP) as arch: assert arch.testzip() is None
 metadata=json.loads((output/"VISUAL_REPORT.json").read_text())
 metadata.update({"title":profile["label"],"year":profile["year"],"movie_sha256":digest(m.MOVIE),
                 "zip_sha256":digest(m.ZIP),"artistic_approval":False,
                 "generation_type":"new historical episode, source real; neural color motion + one real free I2I still",
                 "public_preview_uploaded":False,"site_social_published":False})
 save(output,"SERIAL_QA.json",metadata)
 print("NEW_SERIAL_FILM_TECHNICAL_REVIEW_READY",args.episode,metadata["movie_sha256"],flush=True)
if __name__=="__main__":main()
