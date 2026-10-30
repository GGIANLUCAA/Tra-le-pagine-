#!/usr/bin/env python3
"""V98: restore FIVE DISTINCT actual Bombay 1929 source frames with a real,
FREE image-to-image photographic model (Finegrain). Four use stills, fifth is
the Vidu image anchor. No DDColor-only final photos and NO Vidu API calls.
"""
from pathlib import Path
import json,hashlib,cv2,numpy as np,time
from PIL import Image,ImageDraw
R=Path("output/storia_bombay_v98");R.mkdir(parents=True,exist_ok=True)
SCENES={
2:("The 1929 Bombay street crowd beside the recognisable two-storey historic building with pyramidal tiled roof. Preserve every visible human, the facade, windows, clothing, proportions and the street. Photographic modern 35mm DSLR documentary realism, period-authentic muted terracotta tile and natural Indian skin tones, fine optical detail. No new people, no invented eyes, no face swap, no new writing."),
4:("The same original 1929 Bombay working men arranging heavy textile sacks and baskets at the waterfront/market. Keep the adult worker with white short-sleeved shirt facing away exactly the same age, pose, clothing, body count, hands, load shapes and stone foreground. Lifelike subtle photographic cloth texture and natural rich colors; no additional humans, no objects morphing into people, no new letters."),
5:("1929 Bombay market street, shops, balconies and sunshades above real people walking far below. Faithful source-matched photographic restoration; natural weathered cream plaster, brown wooden balconies and original period clothing, human faces only as much as the source resolves. Avoid plastic-looking people and fabricated signs; rigid architecture; original vertical camera perspective."),
7:("Bombay India 1929 street market in daylight with real historical men walking along carts under trees and awnings. Crisp natural modern documentary photograph but EXACT same people and background buildings, hats, expressions, clothing, number and position of people, object identities and framing as the original image. Realistic cotton fabrics, skin and tree foliage with subdued vibrant historic materials. No new passers-by, face swaps or fake objects."),
8:("Photorealistic faithful restoration of the EXACT original 1929 Bombay film frame showing a close-knit group of adult Indian men in traditional shirts, jackets and caps looking toward the camera, one moustached man in light shirt near frame center and another moustached man to the right. Preserve every EXISTING face, exact moustache positions, eyes, age, caps, hand and arm postures, realistic natural medium-brown skin with pores, fine hair strands, gentle smiles, individual clothing texture. NO beautification, no invented extra people, no face/hat swaps, no added hands or changed background; photographic color consistent with an original frame.")
}
NEG=("fake identity, face swap, a new face, a new person, more people, fingers deform, extra limbs, "
 "plastic smooth face, anime, cartoon, digital painting, modern accessories, sunglasses, traffic from 2026, "
 "made up architecture, altered signage, extra hats, changing anatomy, overexposure, too much red or orange")
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()
def corr(a,b):
 def f(z):
  x=cv2.cvtColor(cv2.resize(z,(72,128)),cv2.COLOR_BGR2GRAY)
  return cv2.GaussianBlur(x,(7,7),0).astype("float32").ravel()
 x,y=f(a),f(b);return float(np.corrcoef(x,y)[0,1])
def sat(a):
 return float(cv2.cvtColor(a,cv2.COLOR_BGR2HSV)[:,:,1].mean())
def sharp(a):
 b=cv2.cvtColor(cv2.resize(a,(240,427)),cv2.COLOR_BGR2GRAY)
 return float(cv2.Laplacian(b,cv2.CV_32F).var())
def make():
 from gradio_client import Client,handle_file
 records=json.loads((R/"V95_FREE_SOURCE_QA.json").read_text())["selected_scenes"]
 client=Client("finegrain/finegrain-image-enhancer",verbose=False)
 manifest={"version":"V98_REAL_1929_FIVE_SCENES_I2I","operation":"5 free real image-to-image photorealistic restorations",
           "no_paid_vidu":True,"source_historical_film":"Street Scenes in Bombay (Jan. 1929)",
           "AI_reconstruction_interpretive":True,"scene_photos":[]}
 images=[]
 for k in [2,4,5,7,8]:
  row=next(x for x in records if x["scene"]==k)
  src=R/f"SOURCE_BW_{k:02d}.png";base=R/f"RESTORED_PHOTO_{k:02d}.jpg"
  if sha(src)!=row["original_BW_frame_sha256"] or sha(base)!=row["existing_AI_color_photo_sha256"]:
   raise RuntimeError("WRONG_SOURCE_PHOTO_MAPPING_"+str(k))
  orig=cv2.imread(str(src));old=cv2.imread(str(base))
  if orig is None or old is None or orig.shape[:2]!=(1280,720):raise RuntimeError("SOURCE_RASTER_WRONG")
  best=None; attempts=[]
  for trial in range(2 if k==8 else 1):
   try:
    raw=client.predict(handle_file(str(base)),SCENES[k],NEG,
        1929+k+trial*91,2,1.14,0.97,6,112,144,0.45,18,"DDIM",api_name="/process")
    item=raw[1] if isinstance(raw,(tuple,list)) and len(raw)>1 else raw
    if isinstance(item,dict):item=item.get("path")
    if not item or not Path(str(item)).is_file():raise RuntimeError("I2I_NO_OUTPUT_FILE")
    candidate=cv2.imread(str(item))
    if candidate is None:raise RuntimeError("I2I_UNDECODABLE")
    candidate=cv2.resize(candidate,(720,1280))
    c=corr(orig,candidate);s=sat(candidate);s0=sharp(old);s1=sharp(candidate)
    # Resemblance is conservative: enough change to be true image-to-image, but
    # no gross source geometry/identity displacement. Automated pass != human QA.
    if c<(.92 if k!=8 else .93):raise RuntimeError(f"I2I_SOURCE_GEOMETRY_FAIL corr={c:.3f}")
    if not 18<s<175:raise RuntimeError(f"I2I_COLOR_GATE_FAIL sat={s:.1f}")
    target=R/f"I2I_PHOTO_{k:02d}_VARIANT_{trial+1}.jpg"
    cv2.imwrite(str(target),candidate,[cv2.IMWRITE_JPEG_QUALITY,96])
    stats={"variant":trial+1,"image":target.name,"sha256":sha(target),"gray_correlation":round(c,4),
           "saturation_mean":round(s,1),"sharp_original":round(s0,1),"sharp_i2i":round(s1,1)}
    attempts.append(stats)
    if best is None or s1>best[1]:
     best=(candidate,s1,target,stats)
    print("V98_REAL_I2I",k,trial+1,"similarity",c,"sharp",s1,flush=True)
   except Exception as e:
    attempts.append({"variant":trial+1,"error_type":type(e).__name__,"explanation":str(e)[:250]})
    print("V98_I2I_ATTEMPT_FAILED",k,trial+1,str(e)[:200],flush=True)
  if best is None:
   manifest["scene_photos"].append({"scene":k,"status":"I2I_FAILED_REJECT_CLASSIC_PHOTO","attempts":attempts})
   (R/"V98_FREE_I2I_QA.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
   raise RuntimeError("NO_TRULY_SOURCE_LOCKED_REAL_IMAGE2IMAGE_SCENE_"+str(k))
  selected=R/f"RESTORATION_FINAL_{k:02d}.jpg"
  cv2.imwrite(str(selected),best[0],[cv2.IMWRITE_JPEG_QUALITY,96])
  images.append((k,orig,old,best[0]))
  manifest["scene_photos"].append({"scene":k,"status":"I2I_GENERATED_TECHNICALLY_SOURCE_LOCKED_REQUIRES_ARTISTIC_QA",
     "original_sha256":sha(src),"base_DDColor_not_final_sha256":sha(base),
     "new_i2i_photo_sha256":sha(selected),"method":"real_image_to_image_photographic_restoration",
     "auto_frame_correlation_pass":True,"source_to_output_corr":best[3]["gray_correlation"],
     "human_facial_fidelity":"PENDING","human_scene_identity":"PENDING","attempts":attempts})
 board=Image.new("RGB",(len(images)*244,3*452),(12,16,20));d=ImageDraw.Draw(board)
 for i,(k,original,old,new) in enumerate(images):
  for j,image in enumerate([original,old,new]):
   x=i*244+2;y=j*452+24
   im=Image.fromarray(cv2.cvtColor(image,cv2.COLOR_BGR2RGB)).resize((240,427))
   board.paste(im,(x,y))
   d.text((x+5,j*452+3),f"{k} "+["REAL B/W","OLD DDCOLOR","REAL I2I NEW"][j],fill="white")
 board.save(R/"V98_SOURCE_VS_DDCOLOR_VS_I2I.jpg",quality=92)
 (R/"V98_FREE_I2I_QA.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
 print("V98_FIVE_REAL_I2I_PHOTOGRAPHS_READY_NO_VIDU_SPEND",len(images),flush=True)
if __name__=="__main__":make()
