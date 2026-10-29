#!/usr/bin/env python3
"""V80 Ellis Island: more detailed modern-looking faces and repair concrete BAG->PERSON hallucination.
Improves only manual genuine human face masks with free GFPGAN ONNX on CPU; exact historical motion remains.
NOT an exact historical identity claim. Best-effort and separate artistic preview.
"""
from pathlib import Path
import subprocess,json,hashlib,zipfile,wave,importlib.util
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageEnhance

BASE=Path("output/storia_v80_ellis")
BASE.mkdir(parents=True,exist_ok=True)
MODEL_ID="opiumuseless/gfpgan-v1.4-w16"
MODEL_FILE="GFPGANv1.4-w16.onnx"
MASKS={
 1:[(230,310,495,580,.45)],
 2:[(239,462,425,695,.60),(425,170,641,421,.34)],
 3:[(365,355,571,614,.68)]
}
STILLS={1:(2.27,6.6),2:(9.0,13.0),3:(15.3,19.47)}
FPS,W,H=30,720,1280
EXTRA_S=0.64

def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for c in iter(lambda:f.read(1048576),b""):h.update(c)
 return h.hexdigest()
def check(cmd,limit=150):
 p=subprocess.run(cmd,capture_output=True,text=True,timeout=limit)
 if p.returncode:raise RuntimeError(str(cmd[:3])+": "+p.stderr[-700:])
 return p.stdout

def load_face_model():
 from huggingface_hub import hf_hub_download
 import onnxruntime as ort
 model=Path(hf_hub_download(repo_id=MODEL_ID,filename=MODEL_FILE))
 if model.stat().st_size<150_000_000:raise RuntimeError("GFPGAN ONNX corrupted")
 opts=ort.SessionOptions();opts.intra_op_num_threads=4;opts.graph_optimization_level=ort.GraphOptimizationLevel.ORT_ENABLE_ALL
 session=ort.InferenceSession(str(model),sess_options=opts,providers=["CPUExecutionProvider"])
 inputs=session.get_inputs();outputs=session.get_outputs()
 if len(inputs)!=1 or len(outputs)<1:raise RuntimeError("Wrong GFPGAN model signature")
 print("FACE_MODEL",str(model.stat().st_size),[(x.name,x.shape) for x in inputs],[(x.name,x.shape) for x in outputs],flush=True)
 return session

def selective_faces(photo,rois,session):
 out=photo.copy()
 for q,(x0,y0,x1,y1,strength) in enumerate(rois,1):
  x0,y0,x1,y1=map(int,(x0,y0,x1,y1))
  src=out[y0:y1,x0:x1]
  if src.size<5000:continue
  inp=cv2.resize(src,(512,512),interpolation=cv2.INTER_CUBIC)
  rgb=cv2.cvtColor(inp,cv2.COLOR_BGR2RGB).astype(np.float32)/127.5-1.0
  nchw=np.transpose(rgb,(2,0,1))[None].astype(np.float32)
  out0=session.run(None,{session.get_inputs()[0].name:nchw})[0]
  if len(out0.shape)!=4 or out0.shape[1]!=3:raise RuntimeError("Bad face output "+str(out0.shape))
  restored=np.transpose(np.clip(out0[0],-1,1),(1,2,0))
  face=cv2.cvtColor(np.clip((restored+1)*127.5,0,255).astype(np.uint8),cv2.COLOR_RGB2BGR)
  face=cv2.resize(face,(x1-x0,y1-y0),interpolation=cv2.INTER_AREA)
  # Source-locked spatial mask: protect the hat, side objects, clothes and backdrop.
  yy,xx=np.ogrid[:y1-y0,:x1-x0]
  cx=(x1-x0)*.50;cy=(y1-y0)*.51
  rx=(x1-x0)*.40;ry=(y1-y0)*.34
  radial=np.clip(1-np.sqrt(((xx-cx)/rx)**2+((yy-cy)/ry)**2),0,1)
  mask=cv2.GaussianBlur(radial.astype(np.float32),(0,0),12)*strength
  # Repair not replace with an unrestricted portrait: no change outside the true face.
  crop=out[y0:y1,x0:x1].astype(np.float32)
  out[y0:y1,x0:x1]=np.clip(crop*(1-mask[...,None])+face.astype(np.float32)*mask[...,None],0,255).astype(np.uint8)
  print("FACE_ROI_INFERENCE",q,[x0,y0,x1,y1],"strength",strength,flush=True)
 return out

def fix_fake_face_on_luggage(photo,base_color):
 # Only candidate #1 has invented human eyes/nose/mouth on an authentic patterned textile BAG.
 # Mask whole corner, recover material structure from already colorized original source.
 h,w=photo.shape[:2]
 yy,xx=np.mgrid[:h,:w].astype(np.float32)
 # Mask around lower-right basket, not an actual face
 mask=np.clip((xx-464)/35,0,1)*np.clip((yy-838)/43,0,1)
 mask*=np.clip((1275-yy)/28,0,1)
 mask=cv2.GaussianBlur(mask.astype(np.float32),(0,0),13)
 target=photo.astype(np.float32)*(1-mask[...,None])+base_color.astype(np.float32)*mask[...,None]
 result=np.clip(target,0,255).astype(np.uint8)
 return result,float((mask>.5).mean())

def reduce_sepia(image):
 # White-balance controlled chroma, no global blur. Retain natural warm period palette.
 f=image.astype(np.float32)
 # reduce broad yellow-orange tint by channel gains, while preserving real photo texture
 b,g,r=cv2.split(f)
 f=cv2.merge([np.clip(b*1.20+1,0,255),np.clip(g*1.04,0,255),np.clip(r*.92,0,255)])
 f=np.clip(.86*f+.14*image.astype(np.float32),0,255).astype(np.uint8)
 return f

def prepare():
 base=BASE/"V79_ASSETS"
 for i in (1,2,3):
  for pre,ext in (("FOTO_AI_","png"),("ORIGINAL_","png"),("COLORED_SOURCE_","jpg")):
   p=base/f"{pre}{i:02d}.{ext}"
   if not p.is_file():raise RuntimeError("V79 artifact missing "+str(p))
 session=load_face_model()
 results=[]
 for i in (1,2,3):
  img=cv2.imread(str(base/f"FOTO_AI_{i:02d}.png"))
  original=cv2.imread(str(base/f"ORIGINAL_{i:02d}.png"))
  color_src=cv2.imread(str(base/f"COLORED_SOURCE_{i:02d}.jpg"))
  if img is None or original is None or color_src is None:raise RuntimeError("Missing input")
  if img.shape!=(H,W,3):raise RuntimeError("Wrong image dimensions")
  repaired_area=0
  if i==1:img,repaired_area=fix_fake_face_on_luggage(img,color_src)
  enhanced=selective_faces(img,MASKS[i],session)
  enhanced=reduce_sepia(enhanced)
  # ensure only limited editing and no global loss of detail.
  def sharp(im):return float(cv2.Laplacian(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY),cv2.CV_32F).var())
  before=sharp(cv2.imread(str(base/f"FOTO_AI_{i:02d}.png")));after=sharp(enhanced)
  if after<before*.80:raise RuntimeError("Result got overly soft, not accepting "+str(i))
  dst=BASE/f"FOTO_AI_{i:02d}_FACE_HD.png";cv2.imwrite(str(dst),enhanced,[cv2.IMWRITE_PNG_COMPRESSION,2])
  results.append(dict(scene=i,input_sha=sha(base/f"FOTO_AI_{i:02d}.png"),output_sha=sha(dst),
                      face_rois=MASKS[i],source_bag_hallucination_repaired=bool(i==1),
                      mask_repaired_fraction=round(repaired_area,3),source_photo_blur_score=round(before,1),
                      hd_photo_sharp_score=round(after,1),human_identity_art_review="PENDING"))
  print("FACE_HD_READY",i,dst.name,before,after,flush=True)
 (BASE/"FACE_QA.json").write_text(json.dumps(results,ensure_ascii=False,indent=2))
 # Contact sheet
 canvas=Image.new("RGB",(3*240,3*465),(12,13,16));d=ImageDraw.Draw(canvas)
 for j,i in enumerate((1,2,3)):
  for k,p in enumerate((base/f"FOTO_AI_{i:02d}.png",BASE/f"FOTO_AI_{i:02d}_FACE_HD.png",base/f"ORIGINAL_{i:02d}.png")):
   a=Image.open(p).convert("RGB").resize((234,415))
   canvas.paste(a,(k*240+3,j*465+36));d.text((k*240+3,j*465+11),["V79 foto","V80 viso HD","1903 sorgente"][k],fill="white")
 canvas.save(BASE/"CONFRONTO_VOLTI_V79_V80.jpg",quality=91)
 return results

def synthesized_audio(seconds):
 sr=32000;t=np.arange(int(seconds*sr),dtype=np.float32)/sr;v=np.zeros_like(t)
 tone=[130.81,174.61,220,261.63]
 for k,f in enumerate(tone):
  v+=(0.03-.004*k)*np.sin(2*np.pi*f*t+.7*k)*(0.75+.18*np.sin(2*np.pi*.08*t+k))
 for at in (2.24,9.74,16.8):
  u=t-at;m=(u>=0)&(u<.65)
  v[m]+=.065*np.sin(2*np.pi*(190*u[m]+80*u[m]**2))*np.exp(-9*u[m])
 v*=np.minimum(1,t/.9)*np.minimum(1,(seconds-t)/.9)
 v=np.tanh(v*1.9)
 wav=BASE/"MUSIC_ORIGINAL_V80.wav"
 with wave.open(str(wav),"wb") as f:
  f.setnchannels(2);f.setsampwidth(2);f.setframerate(sr)
  f.writeframes((np.stack([v,np.roll(v,380)*.94],axis=1)*16500).astype("<i2").tobytes())
 return wav

def render():
 video=BASE/"V79_ASSETS/LA_STORIA_RIVIVE_ELLIS_ISLAND_1903_V79.mp4"
 cap=cv2.VideoCapture(str(video))
 if not cap.isOpened():raise RuntimeError("Cannot decode V79 source")
 fps=cap.get(cv2.CAP_PROP_FPS);count=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
 if abs(fps-FPS)>0.2 or count<500:raise RuntimeError("Wrong V79 original MP4")
 dst=BASE/"SILENT_V80.mp4"
 p=subprocess.Popen(["ffmpeg","-nostdin","-y","-v","error","-f","rawvideo","-pix_fmt","bgr24",
       "-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","18",
       "-pix_fmt","yuv420p",str(dst)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 photos={i:cv2.imread(str(BASE/f"FOTO_AI_{i:02d}_FACE_HD.png")) for i in (1,2,3)}
 out_frames=0
 try:
  for n in range(count):
   ok,frame=cap.read()
   if not ok:break
   t=n/FPS
   active=next((i for i,(a,b) in STILLS.items() if t>=a and t<b),None)
   if active:
    a,b=STILLS[active]
    strength=np.clip((t-a)/.36,0,1)
    strength=strength**2*(3-2*strength)
    frame=cv2.addWeighted(frame,1-strength,photos[active],strength,0)
   p.stdin.write(frame.tobytes());out_frames+=1
   # Extend only the existing held AI photos with no invented movement.
   if active and (n+1)>=round(STILLS[active][1]*FPS):
    for k in range(round(EXTRA_S*FPS)):
     p.stdin.write(photos[active].tobytes());out_frames+=1
 finally:
  cap.release();p.stdin.close();err=p.stderr.read().decode(errors="replace")
  if p.wait():raise RuntimeError("Video encode error "+err[-900:])
 dur=out_frames/FPS
 wav=synthesized_audio(dur)
 video_out=BASE/"LA_STORIA_RIVIVE_ELLIS_ISLAND_1903_V80_VOLTI_HD.mp4"
 check(["ffmpeg","-nostdin","-y","-v","error","-i",str(dst),"-i",str(wav),
    "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","160k",
    "-movflags","+faststart","-t",str(dur),str(video_out)])
 check(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(video_out),"-f","null","-"])
 gate_spec=importlib.util.spec_from_file_location("gate","src/storia_rivive_v74_effect_gate.py")
 gate=importlib.util.module_from_spec(gate_spec);gate_spec.loader.exec_module(gate)
 qa=gate.inspect_video(video_out,sat_threshold=32,bw_threshold=28)
 if qa["approved_pattern_cycles"]<3:raise RuntimeError("Reference pattern lost "+str(qa))
 Image.open(BASE/"FOTO_AI_03_FACE_HD.png").convert("RGB").save(BASE/"COPERTINA.jpg",quality=94)
 status=dict(episode="Ellis Island 1903",version="V80",seconds=round(dur,2),
  source_record="https://www.loc.gov/item/00694367/",artifact_sha=sha(video_out),
  face_model=MODEL_ID,bag_transmuted_to_false_human_corrected=True,faces="Modern plausible AI details, not historically proven identity",
  videos_true_motion=True,photo_stills=3,reference_cycles=qa["approved_pattern_cycles"],
  no_paid_api=True,no_vidu=True,site_uploaded=False,social_published=False,
  human_semantic_quality_review="PENDING")
 (BASE/"V80_STATUS.json").write_text(json.dumps(status,ensure_ascii=False,indent=2))
 z=BASE/"ELLIS_ISLAND_1903_V80_KIT.zip"
 with zipfile.ZipFile(z,"w",compression=zipfile.ZIP_DEFLATED) as arc:
  for f in [video_out,BASE/"COPERTINA.jpg",BASE/"FACE_QA.json",BASE/"V80_STATUS.json",BASE/"CONFRONTO_VOLTI_V79_V80.jpg"]:
   arc.write(f,f.name)
 with zipfile.ZipFile(z) as arc:
  if arc.testzip():raise RuntimeError("zip CRC failure")
 print("V80_REAL_NEW_MOVIE_HD_READY",str(video_out),video_out.stat().st_size,"DURATION",dur,"ZIP",z.stat().st_size,flush=True)

if __name__=="__main__":
 prepare()
 render()
