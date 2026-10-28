#!/usr/bin/env python3
"""V67 Vienna 1920 real video decode, source fidelity, freeze hold and contact-board QA.
Technical pass is never an assertion of photographic reference-quality or restored true identities.
"""
import importlib.util, json, subprocess
from pathlib import Path
import cv2, numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
sp=importlib.util.spec_from_file_location("paris",ROOT/"src/storia_rivive_paris_1918_v65.py")
p=importlib.util.module_from_spec(sp);sp.loader.exec_module(p)
OUT=p.OUT
info=json.loads((OUT/"FONTI_E_QA.json").read_text())
source=OUT/"VIENNA_1920_ARCHIVIO_CC0.webm"
final=OUT/"AUSTRIA_1920_IL_TEMPO_SI_FERMA_V67.mp4"
assert source.is_file() and final.is_file()
assert info["mp4_ffmpeg_full_decode_passed"] and p.sha(final)==info["mp4_sha256"]
assert info["source_sha256_verified"]
assert info["output_resolution_px"]==[1080,1920] and not info["is_native_4k"]
duration=info["runtime_s"]
assert 24<duration<29,duration
cap=cv2.VideoCapture(str(source));dest=cv2.VideoCapture(str(final))
assert cap.isOpened() and dest.isOpened()
assert round(dest.get(cv2.CAP_PROP_FRAME_WIDTH))==1080
assert round(dest.get(cv2.CAP_PROP_FRAME_HEIGHT))==1920
assert abs(dest.get(cv2.CAP_PROP_FPS)-30)<.1
board=Image.new("RGB",(7*234,2*444),(18,19,22))
draw=ImageDraw.Draw(board)
try:font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",17)
except OSError:font=ImageFont.load_default()
elapsed=0
scores=[]
for i,s in enumerate(p.SHOTS):
 orig=p.raw_frame(cap,s["end"])
 orig=p.crop(orig,s["x"])
 cpath=OUT/f"FOTO_RESTAURATA_{i+1:02d}.jpg"
 restored=cv2.imread(str(cpath))
 assert restored is not None and restored.shape[:2]==(1920,1080)
 assert info["scenes"][i]["ai_photo_sha256"]==p.sha(cpath)
 original_grey=cv2.cvtColor(orig,cv2.COLOR_BGR2GRAY)
 restaur_grey=cv2.cvtColor(restored,cv2.COLOR_BGR2GRAY)
 sm0=cv2.resize(original_grey,(72,128),interpolation=cv2.INTER_AREA).astype(np.float32)
 sm1=cv2.resize(restaur_grey,(72,128),interpolation=cv2.INTER_AREA).astype(np.float32)
 sm0=cv2.GaussianBlur(sm0,(11,11),0);sm1=cv2.GaussianBlur(sm1,(11,11),0)
 corr=float(np.corrcoef(sm0.ravel(),sm1.ravel())[0,1])
 assert corr>.35,(i,corr,"Photo no longer matches original structure")
 # Distinguish AI-restored photo from monochrome original.
 saturation=float(cv2.cvtColor(restored,cv2.COLOR_BGR2HSV)[:,:,1].mean())
 assert saturation>12
 t_photo=elapsed+s["motion"]+s["reveal"]+.6
 def read(t):
  dest.set(cv2.CAP_PROP_POS_MSEC,t*1000)
  ok,b=dest.read()
  if not ok:raise RuntimeError("MP4 frame read failed: "+str(t))
  return cv2.resize(b,(108,192))
 a=read(t_photo);b=read(t_photo+.42)
 deviation=float(np.abs(a.astype(np.float32)-b.astype(np.float32)).mean())
 assert deviation<1.6,(i,deviation,"AI photo not frozen")
 for row,fr in enumerate([cv2.cvtColor(orig,cv2.COLOR_BGR2GRAY),restored]):
  if row==0:
   fr=cv2.cvtColor(fr,cv2.COLOR_GRAY2RGB)
  else:
   fr=cv2.cvtColor(fr,cv2.COLOR_BGR2RGB)
  fr=cv2.resize(fr,(218,388),interpolation=cv2.INTER_AREA)
  board.paste(Image.fromarray(fr),(i*234+8,row*444+37))
 draw.text((i*234+9,9),s["name"]+" · archivio",fill="#ebebec",font=font)
 draw.text((i*234+9,453),s["name"]+" · restauro AI",fill="#ebebec",font=font)
 elapsed+=s["motion"]+s["reveal"]+s["hold"]
 scores.append({"subject":s["theme"],"structural_correlation":round(corr,3),
                "photo_color_saturation":round(saturation,1),"hold_frame_difference":round(deviation,3)})
cap.release();dest.release()
board_path=OUT/"AUSTRIA_1920_CONFRONTO_PRIMA_DOPO.jpg"
board.save(board_path,quality=89)
report={"technical_pass":True,"creative_quality_approved":False,
        "source":p.v67.PAGE,"source_cc0_claim_verified":True,
        "native_4k":False,"duration_s":duration,"scenes":scores,
        "human_restoration_review":"Required: faces, non-fabricated history, colors, consistency with social reference examples",
        "site_uploaded":False,"vidu_credits_used":0}
(OUT/"QA_REPORT.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print("VIENNA_V67_REAL_VIDEO_QA_PASS",json.dumps({"seconds":duration,"pairs":7,"board":str(board_path)},ensure_ascii=False),flush=True)
