#!/usr/bin/env python3
"""V63 QA: authentic film frame vs reconstructed photo; numeric guardrails and visual review board."""
import importlib.util,json,os,subprocess,sys
from pathlib import Path
import cv2, numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("v63",ROOT/"src/storia_rivive_director_cut_v63.py")
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
out=Path("output/storia_rivive_v63_director_cut")
video=out/"LA_STORIA_RIVIVE_BEIRUT_1919_REGIA_V63.mp4"
source=Path("output/storia_rivive_v60_beirut/FONTE_ORIGINALE.webm")
meta=json.loads((out/"FONTI_RICETTA_QA.json").read_text())
assert source.is_file() and video.is_file()
assert meta["mp4_decode_test_passed"] and meta["mp4_sha256"]==v.sha(video)
assert meta["actual_delivery_resolution"]==[1080,1920]
assert meta["source_native_resolution"]==[720,576]
assert meta["true_4k"] is False
assert len(meta["shots"])==len(v.SHOTS)==6
duration=meta["timings"]["total_video_s"];assert 22<=duration<=27
rawcap=cv2.VideoCapture(str(source));outcap=cv2.VideoCapture(str(video))
assert outcap.isOpened()
assert outcap.get(cv2.CAP_PROP_FRAME_WIDTH)==1080
assert outcap.get(cv2.CAP_PROP_FRAME_HEIGHT)==1920
assert abs(outcap.get(cv2.CAP_PROP_FPS)-30)<.15
board=Image.new("RGB",(6*250,2*458),"#0c0d10");draw=ImageDraw.Draw(board)
stats=[]
cumulative=0
for i,s in enumerate(v.SHOTS):
 original=v.extract_frame(rawcap,s["end"])
 cropped=v.crop9(original,s["x"])
 png=out/(f"FOTO_AI_{i+1:02d}.jpg")
 restored=cv2.imread(str(png))
 assert restored is not None and restored.shape[:2]==(1920,1080)
 assert meta["shots"][i]["photo_sha256"]==v.sha(png)
 gray=cv2.cvtColor(cropped,cv2.COLOR_BGR2GRAY)
 restored_gray=cv2.cvtColor(restored,cv2.COLOR_BGR2GRAY)
 orig_view=cv2.resize(cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR),(230,410))
 new_view=cv2.resize(restored,(230,410))
 for row,img in enumerate((orig_view,new_view)):
  pos=(i*250+10,row*458+35)
  board.paste(Image.fromarray(cv2.cvtColor(img,cv2.COLOR_BGR2RGB)),pos)
 draw.text((i*250+10,12),s["name"]+" / B-N",fill="#e7e7eb")
 draw.text((i*250+10,458+12),s["name"]+" / foto IA",fill="#e7e7eb")
 saturation=cv2.cvtColor(restored,cv2.COLOR_BGR2HSV)[:,:,1].mean()
 # QA (not artwork certification): still has chromatic information and source geometry.
 assert saturation>12,("Color restoration too desaturated",i,float(saturation))
 motion=round(s["motion_s"]*30);transition=round(s["reveal_s"]*30);hold=round(s["hold_s"]*30)
 tphoto=(cumulative+motion+transition+.4*30)/30
 tphoto2=tphoto+.6
 outcap.set(cv2.CAP_PROP_POS_MSEC, tphoto*1000);ok,a=outcap.read()
 outcap.set(cv2.CAP_PROP_POS_MSEC, tphoto2*1000);ok2,b=outcap.read()
 assert ok and ok2
 diff=float(np.mean(abs(cv2.resize(a,(120,213)).astype(np.float32)-cv2.resize(b,(120,213)).astype(np.float32))))
 assert diff<1.4,(i,"color photo should remain still",diff)
 stats.append({"scene":i+1,"subject":s["subject"],"photo_saturation_mean":round(float(saturation),2),
               "photo_motion_mean_abs_diff":round(diff,3),
               "cropped_native_source":[cropped.shape[1],cropped.shape[0]],"delivered_photo":[1080,1920]})
 cumulative+=motion+transition+hold
rawcap.release();outcap.release()
boardpath=out/"V63_QA_SIX_BEFORE_AFTER.jpg";board.save(boardpath,quality=90)
report={"pass_technical":True,"photographic_source_faithfulness_human_review":"REQUIRED","artistic_reference_grade_approved":False,
        "native_4k":False,"accurate_label":"1080p photo restored from 324x576 crop",
        "delivered_duration_s":duration,"review_board":str(boardpath),"scenes":stats}
(out/"V63_QA_REPORT.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"status":"QA_TECHNICAL_PASS_REQUIRES_HUMAN_ARTISTIC_REVIEW",
"board":str(boardpath),"duration_s":duration,
"still_motion_max":max(x["photo_motion_mean_abs_diff"] for x in stats)},ensure_ascii=False))
