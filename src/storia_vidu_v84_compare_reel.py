#!/usr/bin/env python3
"""V84 QA-only reel: join five different moving-color Vidu tests with one audio bed.
Does not modify the five original videos. No provider API calls.
Not an approved historical master; scenes may span years 1900/1918.
"""
import json,math,subprocess,wave,zipfile
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont

D=Path("output/storia_vidu_v84_five_tests")
def sh(cmd,timeout=180):
 p=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout)
 if p.returncode:raise RuntimeError("VIDEO_EDIT_FAILED "+" ".join(cmd[:6])+" "+p.stderr[-1100:])
 return p.stdout
def main():
 qa=json.loads((D/"TEST_REPORT_FOR_REVIEW.json").read_text())
 specs=qa["new_videos"]
 if len(specs)!=5:raise RuntimeError("FIVE_DISTINCT_VIDU_TESTS_REQUIRED")
 inputs=[D/s["mp4"] for s in specs]
 if any(not f.is_file() for f in inputs):raise RuntimeError("MISSING_REAL_TEST_CLIP")
 audio=D/"V84_ORIGINAL_MUSIC.wav"
 length=25.1;sr=32000
 t=np.arange(round(length*sr),dtype=np.float32)/sr
 signal=np.zeros_like(t)
 for j,f in enumerate([130.81,164.81,196,261.63]):
  signal+=(.023-.003*j)*np.sin(2*np.pi*f*t+j*.27)*(0.70+.30*np.sin(.18*t+j))
 for beat in [0,5,10,15,20]:
  d=t-beat;m=(d>=0)&(d<.6)
  signal[m]+=.035*np.sin(2*np.pi*(105*d[m]+56*d[m]*d[m]))*np.exp(-12*d[m])
 signal=np.tanh(signal*2)*np.minimum(1,t/.8)*np.minimum(1,np.maximum(0,(length-t)/.7))
 with wave.open(str(audio),"wb") as w:
  w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr)
  w.writeframes((np.column_stack((signal,np.roll(signal,int(.011*sr))*.91))*19000).astype("<i2").tobytes())
 silent=D/"V84_REEL_SILENT.mp4"
 cmd=["ffmpeg","-nostdin","-y","-v","error"]
 for p in inputs:cmd+=["-i",str(p)]
 filter_chains=[]
 for i in range(5):
  filter_chains.append(f"[{i}:v]fps=30,scale=720:1280:flags=lanczos,setsar=1,format=yuv420p,setpts=PTS-STARTPTS,trim=duration=5[v{i}]")
 filt=";".join(filter_chains)+";"+"".join(f"[v{i}]" for i in range(5))+"concat=n=5:v=1:a=0[v]"
 sh(cmd+["-filter_complex",filt,"-map","[v]","-c:v","libx264","-crf","18","-preset","veryfast","-pix_fmt","yuv420p",str(silent)],220)
 final=D/"V84_CINQUE_PROVE_VIDU_CONFRONTO.mp4"
 sh(["ffmpeg","-nostdin","-y","-v","error","-i",str(silent),"-i",str(audio),
  "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","160k","-shortest","-movflags","+faststart",str(final)],100)
 sh(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(final),"-f","null","-"],130)
 probe=json.loads(sh(["ffprobe","-v","error","-show_entries","format=duration,size:stream=codec_name,width,height","-of","json",str(final)]))
 dur=float(probe["format"]["duration"])
 if not 23.8<dur<26.0:raise RuntimeError("FIVE_TEST_REEL_DURATION_WRONG")
 qa["reel_video"]=final.name;qa["reel_duration"]=dur;qa["reel_contains"]="five authentic real generated AI video tests with 1s monochrome-to-color reveal, not an original historical continuous take"
 (D/"TEST_REPORT_FOR_REVIEW.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n")
 cover=Image.open(D/("INPUT_"+specs[0]["id"]+".jpg")).convert("RGB")
 draw=ImageDraw.Draw(cover,"RGBA")
 draw.rectangle((0,70,720,330),fill=(8,12,16,165))
 try:font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",52)
 except:font=ImageFont.load_default()
 draw.text((45,132),"THE PAST",font=font,fill="white")
 draw.text((45,218),"COMES ALIVE",font=font,fill=(235,210,166,255))
 cover.save(D/"COVER.jpg",quality=92)
 with zipfile.ZipFile(D/"FIVE_VIDU_TESTS_ANDROID.zip","a",zipfile.ZIP_DEFLATED) as z:
  z.write(final,final.name);z.write(D/"COVER.jpg","COVER.jpg")
 with zipfile.ZipFile(D/"FIVE_VIDU_TESTS_ANDROID.zip") as z:
  if z.testzip():raise RuntimeError("DELIVERY_ZIP_CRC_FAIL")
 print("V84_FIVE_TESTS_REEL_OK",final.name,"bytes",final.stat().st_size,"duration",dur,flush=True)
if __name__=="__main__":main()
