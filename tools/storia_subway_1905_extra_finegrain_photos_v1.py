#!/usr/bin/env python3
"""Fresh 1905 staged subway comedy: three EXTRA real Finegrain I2I historical photo trials.
No Vidu requests. Save every successful image even if free HF quota runs out."""
import os,sys,json,math,hashlib,pathlib,cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
from gradio_client import Client,handle_file
sys.path.insert(0,"src")
import storia_rivive_real_ai_v60 as dd
R=pathlib.Path("output/storia_subway_1905_more_photos")
R.mkdir(parents=True,exist_ok=True)
S=pathlib.Path("output/storia_subway_1905_source")
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for z in iter(lambda:f.read(1<<20),b""):h.update(z)
 return h.hexdigest()
def corr(a,b):
 def g(x):
  v=cv2.cvtColor(cv2.resize(x,(120,200)),cv2.COLOR_BGR2GRAY)
  return cv2.GaussianBlur(v,(7,7),0).astype("float32").ravel()
 a,b=g(a),g(b)
 return float(np.corrcoef(a,b)[0,1]) if a.std()>.3 and b.std()>.3 else -1
def center_on_faces(frame):
 h,w=frame.shape[:2]
 cw=round(h*9/16)
 cascade=cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_frontalface_default.xml")
 gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
 faces=cascade.detectMultiScale(cv2.equalizeHist(gray),1.09,4,minSize=(26,26))
 choices=[]
 for x in range(0,w-cw+1,16):
  good=[(fx,fy,a,b) for fx,fy,a,b in faces if fx>=x+8 and fx+a<x+cw-8]
  score=35*len(good)+.40*sum(math.sqrt(a*b) for fx,fy,a,b in good)-.05*abs(x+cw/2-w/2)
  choices.append((score,x,len(good)))
 _,x,n=max(choices)
 crop=cv2.resize(frame[:,x:x+cw],(720,1280),interpolation=cv2.INTER_CUBIC)
 return crop,{"x":x,"width":cw,"faces_in_crop":n}
def color_base(bw,model):
 lab=cv2.cvtColor(bw.astype(np.float32)/255,cv2.COLOR_BGR2LAB)
 ab=dd.infer_ab(model,bw)
 lab[:,:,1:]=np.clip(cv2.resize(ab,(720,1280))*.85,-95,95)
 return np.uint8(np.clip(cv2.cvtColor(lab,cv2.COLOR_LAB2BGR)*255,0,255))
def main():
 meta=json.loads((S/"SCOUT_REPORT.json").read_text())
 if meta["reality_status"]!="FICTIONAL_REENACTMENT_NOT_ACTUAL_SUBWAY_PASSENGERS":raise RuntimeError("WRONG_FILM")
 src=S/"SOURCE_1905_REAL_MOVING.webm"
 if sha(src)!=meta["source_metadata"]["sha256"]:raise RuntimeError("UNVERIFIED_SOURCE_SHA")
 model,_=dd.download_model()
 client=Client("finegrain/finegrain-image-enhancer",verbose=False)
 cap=cv2.VideoCapture(str(src))
 scenes=[
 (53.0,"Two Edwardian women gesture to each other beside a subway train, authentic actress faces, ornate hats and long dresses"),
 (29.0,"One woman bends as a man crouches on a staged 1905 subway platform; genuine historical movie action and real hands, feet, clothing"),
 (20.0,"The gentleman walks playfully with two Edwardian ladies, early Biograph 1905 subway comedy; exact original bodies and faces")
 ]
 report={"origin":"Biograph staged fiction, shot June 5 1905","new_paid_vidu_posts":0,
         "first_previous_photo_sha":"7a6e05fd8fc28197d1d9e8c3d132817831f6945b3f71123bc9f5876a32eac5f4",
         "attempts":[],"human_visual_QA":"PENDING","finished_video":False}
 for tm,story in scenes:
  tag="T"+str(int(tm))
  row={"timecode_s":tm,"anchor_id":tag,"method":"Finegrain real I2I after DDColor"}
  try:
   cap.set(cv2.CAP_PROP_POS_MSEC,tm*1000);ok,frame=cap.read()
   if not ok:raise RuntimeError("FRAME_UNAVAILABLE")
   bw,crop=center_on_faces(frame)
   row["crop"]=crop
   bw=cv2.cvtColor(cv2.cvtColor(bw,cv2.COLOR_BGR2GRAY),cv2.COLOR_GRAY2BGR)
   origfile=R/(tag+"_ORIGINAL_EXACT_BW.png")
   cv2.imwrite(str(origfile),bw)
   initial=color_base(bw,model)
   b=R/(tag+"_DDCOLOR_BASE_NOT_FINAL.png")
   cv2.imwrite(str(b),initial)
   prompt=("Source-locked high-quality photographic image-to-image RESTORATION of EXACT real frame from "
    "the staged Biograph 1905 comedy '2 A.M. in the Subway'. This is a FICTION film staged in a set. "
    +story+". Preserve EXACT actors' individual facial proportions, expressions, person count, "
    "head and body placement, Edwardian period costumes and hat styles, hands and real railroad details; "
    "no added people, no modern objects, absolutely no changed camera angle. "
    "Create a very photorealistic modern analog color photograph, real-looking skin pores, "
    "genuine 1905 clothing fabric textures and natural subtle colors, realistic optical depth. "
    "Do not hallucinate identifiable eye detail where original source cannot support it. "
    "Maintain all original silhouettes and the 9:16 vertical crop.")
   negative=("painting, poster, illustration, duplicated persons, changed face, plastic wax skin, "
    "fake hands, weird extra legs, modern makeup, false hats, fake teeth, neon orange, modern signs, "
    "bad anatomy, distorted proportions, blur, over-smooth skin, fictional architecture")
   result=client.predict(handle_file(str(b)),prompt,negative,1905,2,1.14,.97,6,112,144,.45,18,"DDIM",api_name="/process")
   pic=result[1] if isinstance(result,(list,tuple)) and len(result)>1 else result
   if isinstance(pic,dict):pic=pic.get("path")
   image=cv2.imread(str(pic))
   if image is None:raise RuntimeError("PROVIDER_RETURNED_NO_IMAGE")
   image=cv2.resize(image,(720,1280))
   cc=corr(bw,image)
   sat=float(cv2.cvtColor(image,cv2.COLOR_BGR2HSV)[:,:,1].mean())
   delta=float(cv2.absdiff(initial,image).mean())
   qc=(cc>=.81 and 18<=sat<=145 and delta>2.2)
   row.update({"state":"rendered_i2i","geometry_corr":round(cc,4),"mean_saturation":round(sat,2),
      "dissimilar_to_neural_recolor":round(delta,2),"automatic_source_gate":qc,
      "human_face_identity_approved":False})
   file=R/(tag+"_REAL_FINEGRAIN_RESTORATION.jpg")
   cv2.imwrite(str(file),image,[cv2.IMWRITE_JPEG_QUALITY,96])
   row.update({"filename":file.name,"sha256":sha(file),"source_photo_sha":sha(origfile)})
   print("NEW_FINEGRAIN_PHOTO",tag,"QC",row,flush=True)
  except Exception as e:
   row.update({"state":"failed","error_type":type(e).__name__,"error":str(e)[:250]})
   print("PHOTO_FAILED_NO_VIDU",tag,str(e)[:250],flush=True)
   report["attempts"].append(row)
   (R/"MORE_PHOTOS_REPORT.json").write_text(json.dumps(report,indent=2)+"\n")
   # Daily free GPU limit is an account-level resource; don't waste additional trial calls.
   if "ZeroGPU" in str(e) or "quota" in str(e).lower() or "limit" in str(e).lower():break
   continue
  report["attempts"].append(row)
  (R/"MORE_PHOTOS_REPORT.json").write_text(json.dumps(report,indent=2)+"\n")
 cap.release()
 successes=[a for a in report["attempts"] if a["state"]=="rendered_i2i"]
 sheet=Image.new("RGB",(len(successes)*680,600),(18,18,24))
 d=ImageDraw.Draw(sheet);ft=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",16)
 for i,a in enumerate(successes):
  for j,name in enumerate((a["anchor_id"]+"_ORIGINAL_EXACT_BW.png",a["filename"])):
   im=Image.open(R/name).convert("RGB").resize((335,550))
   sheet.paste(im,(i*680+j*335,36))
   d.text((i*680+j*335+6,8),str(a["timecode_s"])+"s "+("ORIGINAL" if j==0 else "I2I PHOTO"),font=ft,fill="white")
 sheet.save(R/"PHOTOS_SOURCE_VS_AI_QA.jpg",quality=93)
 report["genuine_new_i2i_photos"]=len(successes)
 report["source_photo_trust_gate_pass"]=sum(a.get("automatic_source_gate",False) for a in successes)
 report["ready_to_spend_on_Vidu"]=False
 (R/"MORE_PHOTOS_REPORT.json").write_text(json.dumps(report,indent=2)+"\n")
 print("PHOTO_BATCH_DONE",len(successes),"NO_VIDU_CHARGES",flush=True)
if __name__=="__main__":main()
