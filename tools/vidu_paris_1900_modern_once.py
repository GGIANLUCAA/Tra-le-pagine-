#!/usr/bin/env python3
"""One user-authorized Vidu start/end test: authentic Paris 1900 film -> modern photo.
Never silently resubmit: durable GitHub receipt before first paid POST.
Public-source historical frames only; no user/private media published.
"""
import base64,hashlib,json,os,pathlib,subprocess,sys,time,urllib.request,urllib.error,wave,math,zipfile
from PIL import Image,ImageStat
ROOT=pathlib.Path("output/vidu_paris_1900_20261029")
ROOT.mkdir(parents=True,exist_ok=True)
REPO=os.environ.get("GITHUB_REPOSITORY","GGIANLUCAA/Tra-le-pagine-")
LEDGER="queue/vidu_api_attempts/PARIS_1900_MODERN_SINGLE_20261029.json"
SOURCE="LA_STORIA_RIVIVE_SOCIAL_MUSEUM_V76.mp4"
TAG="storia-rivive-parigi-1896-1900-social-museum-v76"
MAX_CREDITS=16
MODEL="viduq2-pro-fast"
PROMPT=("A precisely frame-matched historic-to-modern photographic transformation. The black-and-white "
"archival film frame of the Paris 1900 moving walkway slowly develops into the exact realistic natural-color "
"restored photograph supplied as the final keyframe. Camera remains locked at identical perspective and "
"framing. Preserve the EXACT people, faces, body positions, hats, clothes, walkway machinery, rails and "
"buildings throughout the entire transition. Gradually reveal lifelike skin and clothing textures and "
"natural warm colors, maintaining documentary authenticity. Gentle scene atmosphere, very restrained "
"physical motion, no invented people, no missing people, no face swaps, no objects becoming humans, "
"no character morphing, no new architecture, no dramatic zoom, no cuts, no text, no talking, no music.")
def sh(cmd,timeout=180):
 p=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout)
 if p.returncode:raise RuntimeError("Command failed: "+" ".join(cmd[:5])+" "+p.stderr[-1500:])
 return p.stdout
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
 return h.hexdigest()
def writej(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True)+"\n")
def ghput(data,sha_old=None):
 endpoint=f"repos/{REPO}/contents/{LEDGER}"
 args=["gh","api","-X","PUT",endpoint,"-f","message=Record single Vidu Paris 1900 approved generation","-f","content="+base64.b64encode((json.dumps(data,sort_keys=True)+"\n").encode()).decode(),"-f","branch=main"]
 if sha_old: args+=["-f","sha="+sha_old]
 return json.loads(sh(args,50))
def update_receipt(data):
 endpoint=f"repos/{REPO}/contents/{LEDGER}"
 old=json.loads(sh(["gh","api",endpoint+"?ref=main"],50))
 ghput(data,old["sha"])
def api(path,key,body=None,method="GET",timeout=35):
 u="https://api.vidu.com"+path
 headers={"Authorization":"Token "+key,"Accept":"application/json","Content-Type":"application/json"}
 req=urllib.request.Request(u,data=(json.dumps(body).encode() if body is not None else None),headers=headers,method=method)
 with urllib.request.urlopen(req,timeout=timeout) as r:
  return json.loads(r.read(1000000))
def rows(data):
 r=data.get("remains",data.get("remaining_credits"))
 if not isinstance(r,list) or not r:raise RuntimeError("Cannot verify credit balances")
 v=[{"type":str(x.get("type","credits")),"credits":x.get("credit_remain")} for x in r if isinstance(x,dict)]
 if not v or any(not isinstance(x["credits"],(int,float)) or x["credits"]<0 for x in v):
  raise RuntimeError("Invalid credit balances")
 return v
def preview():
 src=ROOT/SOURCE
 sh(["gh","release","download",TAG,"--repo",REPO,"-p",SOURCE,"-D",str(ROOT)],160)
 sh(["gh","release","download",TAG,"--repo",REPO,"-p","FONTI_E_QA.json","-D",str(ROOT)],100)
 report=json.loads((ROOT/"FONTI_E_QA.json").read_text())
 if sha(src)!=report.get("video_sha256"):raise RuntimeError("Source video does not match public provenance")
 for stamp,name in [("16.08","START_BW.jpg"),("16.78","END_MODERN.jpg")]:
  sh(["ffmpeg","-nostdin","-y","-v","error","-i",str(src),"-ss",stamp,"-frames:v","1","-q:v","2",str(ROOT/name)],60)
 first=Image.open(ROOT/"START_BW.jpg").convert("RGB");last=Image.open(ROOT/"END_MODERN.jpg").convert("RGB")
 if first.size!=(720,1280) or last.size!=(720,1280):raise RuntimeError("Keyframe geometry mismatch")
 from PIL import ImageEnhance
 bw=ImageStat.Stat(first.convert("HSV")).mean[1];col=ImageStat.Stat(last.convert("HSV")).mean[1]
 if not (bw<12 and col>14):raise RuntimeError(f"Not a genuine B/W-to-modern pair {bw:.1f},{col:.1f}")
 return {"source_release":TAG,"source_sha256":sha(src),"start_sha256":sha(ROOT/"START_BW.jpg"),"end_sha256":sha(ROOT/"END_MODERN.jpg"),"bw_sat":round(bw,1),"modern_sat":round(col,1),
  "archival_source":"https://commons.wikimedia.org/wiki/File:A_Trip_Through_Paris,_France,_Late_1890s.webm",
  "scene":"Paris Exposition moving walkway 1900","start_in_previous_master":16.08,"end_in_previous_master":16.78,
  "new_video_is_reconstruction_not_historical_record":True}
def make_audio(length):
 sr=32000;wav=ROOT/"MUSICA_ORIGINALE.wav"
 with wave.open(str(wav),"wb") as w:
  w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr)
  import array
  a=array.array("h")
  for i in range(int(length*sr)):
   t=i/sr
   env=min(1,t/.7,max(0,(length-t)/.75))
   chord=0.45*math.sin(2*math.pi*130.81*t)+0.27*math.sin(2*math.pi*164.81*t)+0.20*math.sin(2*math.pi*196*t)
   pulse=math.sin(2*math.pi*(200*t+11*t*t))*math.exp(-11*max(0,t-2.0)) if 2<=t<2.35 else 0
   v=int(1450*env*chord+1150*env*pulse)
   a.extend((v,int(v*.93)))
  w.writeframes(a.tobytes())
 return wav
def compose(data):
 source=ROOT/SOURCE;clip=ROOT/"VIDU_TRANSIZIONE_ORIGINALE.mp4"
 sh(["ffmpeg","-nostdin","-y","-v","error","-ss","14.10","-i",str(source),"-t","1.98","-vf","fps=24,scale=720:1280:flags=lanczos,format=yuv420p","-an","-c:v","libx264","-crf","19",str(ROOT/"intro.mp4")],100)
 sh(["ffmpeg","-nostdin","-y","-v","error","-i",str(clip),"-vf","fps=24,scale=720:1280:flags=lanczos,format=yuv420p","-an","-c:v","libx264","-crf","19",str(ROOT/"transition.mp4")],100)
 sh(["ffmpeg","-nostdin","-y","-v","error","-loop","1","-framerate","24","-i",str(ROOT/"END_MODERN.jpg"),"-t","1.2","-vf","scale=720:1280:flags=lanczos,format=yuv420p","-an","-c:v","libx264","-crf","19",str(ROOT/"hold.mp4")],100)
 cmd=["ffmpeg","-nostdin","-y","-v","error","-i",str(ROOT/"intro.mp4"),"-i",str(ROOT/"transition.mp4"),"-i",str(ROOT/"hold.mp4"),
 "-filter_complex","[0:v]setpts=PTS-STARTPTS[v0];[1:v]setpts=PTS-STARTPTS[v1];[2:v]setpts=PTS-STARTPTS[v2];[v0][v1][v2]concat=n=3:v=1:a=0,format=yuv420p[v]",
 "-map","[v]","-c:v","libx264","-preset","veryfast","-crf","18","-movflags","+faststart",str(ROOT/"silent.mp4")]
 sh(cmd,180)
 length=float(json.loads(sh(["ffprobe","-v","error","-show_format","-of","json",str(ROOT/"silent.mp4")],20))["format"]["duration"])
 wav=make_audio(length)
 out=ROOT/"PARIS_1900_PASSATO_DIVENTA_PRESENTE_VIDU.mp4"
 sh(["ffmpeg","-nostdin","-y","-v","error","-i",str(ROOT/"silent.mp4"),"-i",str(wav),"-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","128k","-shortest","-movflags","+faststart",str(out)],100)
 sh(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(out),"-f","null","-"],120)
 spec=json.loads(sh(["ffprobe","-v","error","-show_entries","format=duration,size:stream=codec_name,width,height","-of","json",str(out)],30))
 writej(ROOT/"QA_E_CREDITI.json",{**data,"final_sha256":sha(out),"media":spec,"visual_review":"PENDING_HUMAN","social_published":False,"private_archive_published":False})
 Image.open(ROOT/"END_MODERN.jpg").save(ROOT/"COPERTINA.jpg",quality=95)
 posts={"FACEBOOK":"PARIS, 1900. Un vero istante del passato si trasforma in un’immagine moderna. Ripresa originale d’epoca; colore e transizione ricostruiti con AI. Fonte: Lumière / Wikimedia Commons.",
 "INSTAGRAM":"PARIS · 1900. Un attimo sospeso tra due secoli. 🎞️ Riprese autentiche, ricostruzione AI. #HistoryReels #Paris1900",
 "TIKTOK":"Parigi, 1900: il passato prende colore davanti ai tuoi occhi. Film originale d’epoca e trasformazione AI. #Storia #Paris",
 "YOUTUBE":"PARIS 1900 | Dal film antico alla fotografia moderna\n\nClip d'epoca autenticata: A Trip Through Paris, 1896–1900 (Wikimedia Commons). Transizione video creata con Vidu AI a partire da fotogrammi originali e ricostruiti: la parte AI è un’interpretazione artistica, non un filmato storico autentico."}
 for site,post in posts.items():(ROOT/("POST_"+site+".txt")).write_text(post+"\n")
 kit=ROOT/"PARIS_1900_VIDU_ANDROID.zip"
 with zipfile.ZipFile(kit,"w",zipfile.ZIP_DEFLATED) as z:
  for fn in [out.name,"COPERTINA.jpg","QA_E_CREDITI.json",*[f"POST_{k}.txt" for k in posts]]:
   z.write(ROOT/fn,fn)
 with zipfile.ZipFile(kit) as z:
  if z.testzip():raise RuntimeError("zip invalid")
 print("FINAL_VIDEO_OK",out.as_posix(),out.stat().st_size,"DURATION",length,"ZIP",kit.stat().st_size,flush=True)
def main():
 key=os.environ.get("VIDU_API_KEY","")
 if not key:raise RuntimeError("Vidu secret missing; stop before any paid call")
 d=preview()
 before=rows(api("/ent/v2/credits",key))
 if not any(x["credits"]>=MAX_CREDITS for x in before):raise RuntimeError("Insufficient credits per pool")
 # Reserve permanently on GitHub BEFORE the one billable POST.
 receipt={"status":"reserved","model":MODEL,"max_credits":MAX_CREDITS,"duration":5,"resolution":"720p","off_peak":False,
          "start_image_sha256":d["start_sha256"],"end_image_sha256":d["end_sha256"],"prompt_sha256":hashlib.sha256(PROMPT.encode()).hexdigest(),
          "user_approved":True,"request":"antique film becomes modern","created_at":int(time.time()),"source":d["archival_source"]}
 try:ghput(receipt)
 except Exception as exc:
  raise RuntimeError("A single-use ledger exists or cannot be reserved. Do not submit again.") from exc
 images=["data:image/jpeg;base64,"+base64.b64encode((ROOT/s).read_bytes()).decode() for s in ("START_BW.jpg","END_MODERN.jpg")]
 request={"model":MODEL,"images":images,"duration":5,"resolution":"720p","off_peak":False,"audio":False,"is_rec":False,
          "prompt":PROMPT,"payload":"paris1900-modern-once-20261029"}
 # After this POST no retry under any condition, including network timeout.
 try:resp=api("/ent/v2/start-end2video",key,request,"POST",60)
 except Exception as exc:
  receipt.update(status="submission_unknown",error_type=type(exc).__name__)
  update_receipt(receipt)
  raise RuntimeError("Provider submission ambiguous; no automatic retry") from exc
 task=str(resp.get("task_id",""))
 if not task or not task.replace("_","").replace("-","").isalnum():raise RuntimeError("Missing task id; no resubmission")
 receipt.update(status="submitted",task_id=task,credits_reported=resp.get("credits"),created_utc=int(time.time()))
 update_receipt(receipt)
 print("VIDU_ACCEPTED_TASK_ID",task,"CREDIT_MAX",MAX_CREDITS,flush=True)
 writej(ROOT/"VIDU_TASK.json",{"task_id":task,"state":"submitted","max_credits":MAX_CREDITS,"model":MODEL})
 success=False
 for attempt in range(42):
  time.sleep(12)
  try: info=api("/ent/v2/tasks/"+task+"/creations",key,timeout=30)
  except Exception as exc:
   print("POLL_NETWORK_ERROR",type(exc).__name__,flush=True);continue
  state=info.get("state")
  print("VIDU_STATE",state,"POLL",attempt+1,flush=True)
  if state in ("failed","cancelled"):
   receipt.update(status=state,credits_reported=info.get("credits",receipt.get("credits_reported")))
   update_receipt(receipt);break
  if state!="success":continue
  creations=info.get("creations") or []
  url=creations[0].get("url") if creations else None
  if not isinstance(url,str) or not url.startswith("https://"):raise RuntimeError("Provider has no valid downloadable mp4")
  req=urllib.request.Request(url,headers={"User-Agent":"TraLePagine/1.0"})
  with urllib.request.urlopen(req,timeout=100) as response:
   blob=response.read(60000000+1)
  if not 5000<len(blob)<60000000 or blob[4:8]!=b"ftyp":raise RuntimeError("Provider MP4 invalid")
  (ROOT/"VIDU_TRANSIZIONE_ORIGINALE.mp4").write_bytes(blob)
  sh(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(ROOT/"VIDU_TRANSIZIONE_ORIGINALE.mp4"),"-f","null","-"],150)
  receipt.update(status="video_downloaded",credits_reported=info.get("credits",receipt.get("credits_reported")),mp4_sha256=sha(ROOT/"VIDU_TRANSIZIONE_ORIGINALE.mp4"))
  update_receipt(receipt)
  success=True;break
 after=rows(api("/ent/v2/credits",key))
 out={**d,"task_id":task,"provider_state":receipt["status"],"balance_before":before,"balance_after":after,
   "estimated_credits":MAX_CREDITS,"provider_reported_credits":receipt.get("credits_reported"),
   "credits_consumed_by_pool":[{"type":x["type"],"before":x["credits"],"after":next((y["credits"] for y in after if y["type"]==x["type"]),None)} for x in before],
   "paid_request_count":1}
 writej(ROOT/"CREDITI_PRIVATI_PER_PROPRIETARIO.json",out)
 if not success:
  print("NOT_READY_OR_FAILED_NO_RETRY",receipt["status"],"TASK_ID",task,flush=True)
  return
 compose(out)
 receipt["status"]="final_ready"
 update_receipt(receipt)
if __name__=="__main__":main()
