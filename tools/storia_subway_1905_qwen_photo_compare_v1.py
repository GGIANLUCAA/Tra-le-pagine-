#!/usr/bin/env python3
"""Single source-locked Qwen photo edit comparative pilot. Zero paid Vidu, zero publishing."""
import pathlib,cv2,json,hashlib,numpy as np
from PIL import Image,ImageDraw,ImageFont
from gradio_client import Client,handle_file
R=pathlib.Path("output/storia_subway_1905_qwen_compare");R.mkdir(parents=True,exist_ok=True)
I=pathlib.Path("output/storia_subway_1905_prev_photo")
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def corr(a,b):
 def g(v):
  v=cv2.cvtColor(cv2.resize(v,(100,178)),cv2.COLOR_BGR2GRAY)
  return cv2.GaussianBlur(v,(7,7),0).astype(np.float32).ravel()
 a,b=g(a),g(b)
 return float(np.corrcoef(a,b)[0,1]) if a.std()>.5 and b.std()>.5 else -1
def main():
 bw=cv2.imread(str(I/"ORIGINAL_REAL_1905_EXACT_CROPPED.png"))
 base=cv2.imread(str(I/"DDCOLOR_BASE_ONLY_NOT_A_PHOTOREAL_PHOTO.png"))
 fine=cv2.imread(str(I/"FINEGRAIN_NEW_REAL_I2I_PHOTO.jpg"))
 assert bw is not None and base is not None and fine is not None
 prompt=("Source-locked modern high-detail color analog photographic restoration of the EXACT same frame from "
  "a staged 1905 Biograph silent comedy titled 2 A.M. in the Subway. Keep the same three main historical performers: "
  "the woman dressed in 1905 Edwardian clothing in the center waving her hand, a man to her right smiling, "
  "and a uniformed transit policeman to her left. Preserve the exact historic actor faces and facial expressions, "
  "hair, hats, poses, arms, all people count, location, stairs, perspective and era-appropriate realistic clothing. "
  "Look like a beautiful natural 2026 documentary photography capture, sharp real fabric and optical texture. "
  "No added person, no false props, no fake hands, no modern signs, no altered objects, no illustration, no painterly effects, "
  "natural real skin but not glamour plastic skin, plausible authentic cinematic image, portrait 9:16.")
 report={"source_original_sha256":sha(I/"ORIGINAL_REAL_1905_EXACT_CROPPED.png"),
         "finegrain_sha256":sha(I/"FINEGRAIN_NEW_REAL_I2I_PHOTO.jpg"),
         "paid_Vidu_posts":0,"qwen_attempts":1}
 try:
  client=Client("Qwen/Qwen-Image-Edit-2509",verbose=False)
  result=client.predict([[handle_file(str(I/"DDCOLOR_BASE_ONLY_NOT_A_PHOTOREAL_PHOTO.png")),None]],
    prompt,42,False,4.0,24,1024,576,False,api_name="/infer")
  gallery=result[0] if isinstance(result,(tuple,list)) else result
  if isinstance(gallery,list):gallery=gallery[0]
  if isinstance(gallery,(tuple,list)):gallery=gallery[0]
  if isinstance(gallery,dict):
   gallery=gallery.get("image",gallery)
   if isinstance(gallery,dict):gallery=gallery.get("path",gallery.get("name"))
  q=cv2.imread(str(gallery))
  if q is None:raise RuntimeError("QWEN_RETURNED_NO_IMAGE")
  q=cv2.resize(q,(720,1280))
  path=R/"QWEN_REAL_NEW_RESTORATION_TRIAL.jpg"
  cv2.imwrite(str(path),q,[cv2.IMWRITE_JPEG_QUALITY,96])
  co=corr(bw,q);sat=float(cv2.cvtColor(q,cv2.COLOR_BGR2HSV)[:,:,1].mean())
  delta=float(cv2.absdiff(q,base).mean())
  report.update({"state":"real_qwen_image_generated","sha256":sha(path),
    "geometry_corr":co,"mean_saturation":sat,"delta_vs_base":delta,
    "auto_gate":bool(co>=.80 and 20<=sat<=135 and delta>3.0),"human_artistic_pass":False})
  ims=[("ORIGINAL HISTORICAL B/W",bw),("FINEGRAIN CANDIDATE",fine),("QWEN CANDIDATE",q)]
  contact=Image.new("RGB",(1050,680),(14,14,19));d=ImageDraw.Draw(contact)
  f=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",17)
  for i,(label,z) in enumerate(ims):
   cv=cv2.resize(z,(350,622))
   contact.paste(Image.fromarray(cv2.cvtColor(cv,cv2.COLOR_BGR2RGB)),(i*350,48))
   d.text((i*350+5,10),label,fill="white",font=f)
  contact.save(R/"ACTUAL_FINEGRAIN_VS_QWEN_VISUAL_QA.jpg",quality=95)
 except Exception as e:
  report.update({"state":"qwen_failed_or_quota","error_type":type(e).__name__,"error":str(e)[:430]})
 (R/"QWEN_ONE_FRAME_PHOTO_TRIAL.json").write_text(json.dumps(report,indent=2))
 print("QWEN_SINGLE_TRIAL",json.dumps(report),flush=True)
if __name__=="__main__":main()
