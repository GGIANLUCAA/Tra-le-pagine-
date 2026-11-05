#!/usr/bin/env python3
"""Cinema Reale episode 004: real NOAA dragonfish, isolated CPU render, no generative video."""
import json,hashlib,math,random,struct,subprocess,urllib.request,wave,zipfile
from pathlib import Path
O=Path("output/cinema_reale/episode_004");O.mkdir(parents=True,exist_ok=True)
SRC="https://oceanexplorer.noaa.gov/wp-content/uploads/2019/11/dive04-dragonfish-1280x720-1.mp4"
PAGE="https://oceanexplorer.noaa.gov/multimedia/unknown-dragonfish/"
CREDIT="NOAA Ocean Exploration, 2019 Southeastern U.S. Deep-sea Exploration"
def cmd(a):
 p=subprocess.run(a,text=True,capture_output=True)
 if p.returncode:raise RuntimeError(str(a[:2])+": "+p.stderr[-1800:])
 return p.stdout
def probe(f):return json.loads(cmd(["ffprobe","-v","error","-show_format","-show_streams","-of","json",str(f)]))
def main():
 original=O/"source.mp4"
 req=urllib.request.Request(SRC,headers={"User-Agent":"CinemaReale/1.0 research source"})
 with urllib.request.urlopen(req,timeout=160) as r,original.open("wb") as f:
  while True:
   b=r.read(1048576)
   if not b:break
   f.write(b)
 if original.stat().st_size<200000:raise RuntimeError("Source download too short")
 p=probe(original);dur=float(p["format"]["duration"])
 v=next(x for x in p["streams"] if x["codec_type"]=="video")
 if dur<12:raise RuntimeError("Insufficient source duration")
 w,h=v["width"],v["height"]
 # Trim source beginning and ending to reduce pre-existing slates. Keep chronological order.
 margin=max(2.0,min(5.0,dur*.08))
 start=margin; end=dur-margin
 if end-start<10:raise RuntimeError("Insufficient clean source")
 # Short, variable-length cinematic passage: one continuous authentic event, no fake cuts.
 length=min(27.0,end-start)
 # End is near final genuine movement; no reverse or repeat.
 start=max(margin,end-length)
 # Keep whole frame in portrait via neutral blurred background rather than cut off the animal.
 vf="split=2[bg][fg];[bg]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,boxblur=24:8[blur];[fg]scale=720:1280:force_original_aspect_ratio=decrease[sharp];[blur][sharp]overlay=(W-w)/2:(H-h)/2,format=yuv420p,fps=30"
 silent=O/"visual.mp4"
 cmd(["ffmpeg","-hide_banner","-loglevel","error","-ss",str(start),"-i",str(original),"-t",str(length),"-an","-filter_complex",vf,"-c:v","libx264","-preset","veryfast","-crf","19","-movflags","+faststart","-y",str(silent)])
 d=float(probe(silent)["format"]["duration"])
 sr=24000;rng=random.Random(20261104);audio=O/"score.wav"
 with wave.open(str(audio),"wb") as f:
  f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr)
  for k in range(0,int(d*sr),4096):
   out=bytearray()
   for i in range(k,min(k+4096,int(d*sr))):
    t=i/sr; env=min(1,t/1.4,max(0,(d-t)/1.7))
    drone=.14*math.sin(2*math.pi*49*t)+.055*math.sin(2*math.pi*73.5*t)+.035*math.sin(2*math.pi*98*t)
    breath=.65+.35*math.sin(t*.42)**2
    v0=env*(drone*breath+(.015*(rng.random()-.5)))
    for hit in (d*.3,d*.62,d*.84):
     z=t-hit
     if 0<z<1.5:v0+=.09*math.exp(-3*z)*math.sin(2*math.pi*62*z)
    out+=struct.pack("<h",int(max(-1,min(1,v0))*22000))
   f.writeframesraw(out)
 final=O/"CINEMA_REALE_004_DRAGONFISH_REAL_FOOTAGE_REVIEW.mp4"
 cmd(["ffmpeg","-hide_banner","-loglevel","error","-i",str(silent),"-i",str(audio),"-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","160k","-shortest","-movflags","+faststart","-y",str(final)])
 outp=probe(final);streams=outp["streams"]
 assert any(x["codec_type"]=="video" and x["width"]==720 and x["height"]==1280 for x in streams)
 assert any(x["codec_type"]=="audio" for x in streams)
 cmd(["ffmpeg","-v","error","-i",str(final),"-f","null","-"])
 cover=O/"cover_no_text.jpg"
 cmd(["ffmpeg","-hide_banner","-loglevel","error","-ss",str(min(2,d*.2)),"-i",str(final),"-frames:v","1","-y",str(cover)])
 (O/"SOURCES_AND_RIGHTS.txt").write_text("Source: "+PAGE+"\nAsset: "+SRC+"\nCredit: "+CREDIT+"\nCheck NOAA media kit and third-party exceptions before social publication.\n")
 (O/"SOCIAL_DESCRIPTION_DRAFT.txt").write_text("A living shadow with its own light: the dragonfish. Real footage recorded by NOAA Ocean Exploration.\nFootage credit: "+CREDIT+"\n#DeepSea #OceanExploration\n")
 report={"project_id":"cinema_reale","status":"RENDERED_REVIEW_NOT_PUBLISHED","source":SRC,"source_sha256":hashlib.sha256(original.read_bytes()).hexdigest(),"output_sha256":hashlib.sha256(final.read_bytes()).hexdigest(),"source_duration":dur,"source_size":[w,h],"output_duration":d,"selected_range":[start,start+length],"video_ai":False,"added_voice":False,"added_text":False,"music":"original procedural score","qa":"Technical full decode PASS; visual/editorial review pending","rights":"NOAA source; confirm specific rights before publication"}
 (O/"qa_report.json").write_text(json.dumps(report,indent=2))
 with zipfile.ZipFile(O/"CINEMA_REALE_004_PACKAGE.zip","w",zipfile.ZIP_DEFLATED) as z:
  for f in [final,cover,O/"SOURCES_AND_RIGHTS.txt",O/"SOCIAL_DESCRIPTION_DRAFT.txt",O/"qa_report.json"]:z.write(f,f.name)
 original.unlink()
 print(json.dumps({"result":"REVIEW_READY","duration":d,"bytes":final.stat().st_size}))
if __name__=="__main__":main()
