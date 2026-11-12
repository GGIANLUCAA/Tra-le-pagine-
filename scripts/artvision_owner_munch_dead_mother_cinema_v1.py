#!/usr/bin/env python3
"""Munch Death and the Child (MM.M.00420), original 1899 canvas, new private Cinema.
One genuine video, no TTS, paid APIs, fictional Museum or publication.
"""
from pathlib import Path
import hashlib,io,json,math,subprocess,sys,urllib.parse,urllib.request,wave,zipfile
import cv2
import numpy as np
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"output/artvision-owner-munch-dead-mother-cinema-v1"
WORK_ID="munch_death_and_child_1899_mm_m_00420"
OWNER_TITLE="The Dead Mother and Child"
OFFICIAL_TITLE="Death and the Child"
OFFICIAL_URL="https://www.munch.no/en/object/MM.M.00420"
COMMONS_PAGE="https://commons.wikimedia.org/wiki/File:Edvard_Munch_-_Death_and_the_Child_-_MM.M.00420_-_Munch_Museum.jpg"
FILE_NAME="Edvard Munch - Death and the Child - MM.M.00420 - Munch Museum.jpg"
SOURCE_SHA1="49ef76c0108bdf4df4382c1567f65ddb45748ac3"
SOURCE_BYTES=297684
SOURCE_PIXELS=(2000,1204)
W,H,FPS=720,1280,20

# Drama is in the ACTUAL photographed source, not animated AI characters.
# Three deliberate full-configuration views, one at start of the narrative and
# one at ending, plus details that motivate camera movement in the painting.
SHOTS=[
 ("HOOK / THE GIRL HEARS NOTHING",4.3,(.31,.38,.82),(.32,.39,.76),"child's face and hands to ears"),
 ("REVEAL THE WHOLE PAINTING",6.1,None,None,"child and prone woman in the same room"),
 ("THE HANDS AGAINST HER EARS",5.4,(.31,.38,.76),(.29,.35,.71),"both hands at sides of the child's head"),
 ("PALE FIGURE ON THE BED",5.1,(.77,.35,.84),(.75,.37,.78),"reclining figure with closed eyes on bed"),
 ("THE DISTANCE BETWEEN THE TWO",6.2,(.52,.50,.99),(.54,.49,.96),"child foreground, bed behind"),
 ("RED FLOOR BELOW HER FEET",4.9,(.28,.88,.77),(.31,.86,.72),"red floor and child's lower body"),
 ("GREEN WALL AND UNEASY ROOM",4.6,(.24,.30,.91),(.23,.28,.86),"green wall and upper body"),
 ("RETURN TO HER EXPRESSION",4.7,(.29,.35,.76),(.30,.36,.71),"child's face and cupped ears"),
 ("END: THE ROOM IN SILENCE",6.3,None,None,"complete painting, held long enough to read"),
]
FRAMES=[round(s[1]*FPS) for s in SHOTS]
FRAME_COUNT=sum(FRAMES)
DURATION=FRAME_COUNT/FPS
assert len(SHOTS)==9 and 45<DURATION<51

def sha_file(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for chunk in iter(lambda:f.read(1<<20),b""):h.update(chunk)
 return h.hexdigest()
def call(cmd):
 result=subprocess.run([str(x) for x in cmd],capture_output=True)
 if result.returncode:raise RuntimeError(result.stderr.decode(errors="replace")[-2500:])
 return result.stdout
def save_json(name,d):
 (OUT/name).write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf8")

def exact_source():
 """Fail closed if identifier, SHA1, byte count or decoded pixels mismatch."""
 canonical=FILE_NAME.replace(" ","_")
 md5=hashlib.md5(canonical.encode("utf8")).hexdigest()
 urls=[
   "https://upload.wikimedia.org/wikipedia/commons/"+md5[0]+"/"+md5[:2]+"/"+urllib.parse.quote(canonical,safe="._-"),
   "https://commons.wikimedia.org/wiki/Special:Redirect/file/"+urllib.parse.quote(canonical,safe="._-")
 ]
 for link in urls:
  try:
   req=urllib.request.Request(link,headers={"User-Agent":"ArtVisionOwnerCinemaPrivate/1.0 (https://github.com/GGIANLUCAA/Tra-le-pagine-)"})
   with urllib.request.urlopen(req,timeout=100) as resp:raw=resp.read(SOURCE_BYTES+1)
   if len(raw)!=SOURCE_BYTES:raise ValueError(f"Unexpected source byte size {len(raw)}")
   if hashlib.sha1(raw).hexdigest()!=SOURCE_SHA1:raise ValueError("Source file SHA1 mismatch: refusing wrong edition")
   with Image.open(io.BytesIO(raw)) as pic:
    if pic.format!="JPEG" or pic.size!=SOURCE_PIXELS:raise ValueError("Source image dimensions mismatch")
    pic.verify()
   p=OUT/"ORIGINAL_MUNCH_MM_M_00420.jpg"
   p.write_bytes(raw)
   print("REAL_MUNCH_00420_SOURCE_VERIFIED",len(raw),SOURCE_SHA1,sha_file(p),flush=True)
   return p,link
  except Exception as exc:
   print("SOURCE_VERIFICATION_ATTEMPT_REJECTED",type(exc).__name__,str(exc)[:150],flush=True)
 raise RuntimeError("SOURCE_GATE_FAILED: do not fabricate the original nor generate MP4")

def compose_music():
 """Original self-composed understated ambient bed; no copyrighted samples."""
 sr=24000
 t=np.arange(round((DURATION+.1)*sr),dtype=np.float64)/sr
 y=np.zeros((len(t),2),dtype=np.float64)
 progression=[(65.406,98.0,130.813),(73.416,110,146.832),(61.735,92.499,123.47),(55,82.407,110),(65.406,98,123.47)]
 for ix,start in enumerate(np.arange(0,DURATION,9.8)):
  begin=round(start*sr);end=min(len(t),round((start+11.8)*sr))
  if end<=begin:continue
  u=t[begin:end]-start
  env=np.clip(u/2.4,0,1)*np.clip(((end-begin)/sr-u)/2.7,0,1)
  for k,hz in enumerate(progression[ix%len(progression)]):
   signal=(np.sin(2*np.pi*hz*u+.05*np.sin(2*np.pi*.07*u))+.09*np.sin(2*np.pi*2.002*hz*u))
   y[begin:end,0]+=.012*env*signal/(1+.3*k)
   y[begin:end,1]+=.011*env*np.sin(2*np.pi*hz*u+.12)/(1+.3*k)
  # Soft low note on entry, not rhythmic thumping.
  y[begin:end,:]+=(.011*np.exp(-2.5*u)*np.sin(2*np.pi*42*u))[:,None]
 y[:,0]+=.0028*np.sin(2*np.pi*43.1*t)
 y[:,1]+=.0028*np.sin(2*np.pi*43.34*t)
 y*=np.clip(t/1.8,0,1)[:,None]*np.clip(np.maximum(0,DURATION-t)/2.8,0,1)[:,None]
 p=OUT/"ORIGINAL_SCORE.wav"
 with wave.open(str(p),"wb") as f:
  f.setnchannels(2);f.setsampwidth(2);f.setframerate(sr)
  f.writeframes((np.tanh(y*1.4)*32767).astype("<i2").tobytes())
 return p

def make_frames(source):
 im=cv2.imread(str(source),cv2.IMREAD_COLOR)
 if im is None:raise RuntimeError("The verified image is unreadable")
 ih,iw=im.shape[:2]
 assert (iw,ih)==SOURCE_PIXELS
 # Never stretch the 2000 x 1204 original: diffuse blurred background only
 # outside the centered full artwork, which remains in the real proportions.
 bg=cv2.GaussianBlur(cv2.resize(im,(W,H)),(0,0),42)
 bg=cv2.convertScaleAbs(bg,alpha=.35)
 wh=W-34;hh=round(wh*ih/iw)
 full=bg.copy();x0=(W-wh)//2;y0=(H-hh)//2
 full[y0:y0+hh,x0:x0+wh]=cv2.resize(im,(wh,hh),interpolation=cv2.INTER_AREA)

 def crop(params):
  cx,cy,f=params
  # Portrait camera crop is constrained by the original height and width.
  # No generative enlargement of features.
  ch=int(max(520,min(ih,ih*f)))
  cw=int(ch*W/H)
  if cw>iw:cw=iw;ch=int(cw*H/W)
  x=max(0,min(iw-cw,round(cx*iw-cw/2)))
  y=max(0,min(ih-ch,round(cy*ih-ch/2)))
  return cv2.resize(im[y:y+ch,x:x+cw],(W,H),interpolation=cv2.INTER_CUBIC)

 cover=full.copy()
 cv2.rectangle(cover,(0,70),(W,216),(19,20,22),-1)
 cv2.putText(cover,"DEATH AND THE CHILD",(23,135),cv2.FONT_HERSHEY_SIMPLEX,.81,(234,226,210),2,cv2.LINE_AA)
 cv2.putText(cover,"EDVARD MUNCH   1899",(24,187),cv2.FONT_HERSHEY_SIMPLEX,.48,(215,210,196),1,cv2.LINE_AA)
 cv2.imwrite(str(OUT/"COVER.jpg"),cover,[cv2.IMWRITE_JPEG_QUALITY,93])

 return full,crop

def render(source,music):
 full,crop=make_frames(source)
 mp4=OUT/"VIDEO_ANDROID_REVIEW.mp4"
 proc=subprocess.Popen([
  "ffmpeg","-y","-hide_banner","-loglevel","error",
  "-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(FPS),
  "-i","pipe:0","-i",str(music),"-map","0:v:0","-map","1:a:0",
  "-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p",
  "-c:a","aac","-b:a","144k","-shortest","-movflags","+faststart",str(mp4)
 ],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 contact=[];timeline=[];position=0
 try:
  for ix,((name,duration,frm,to,anchor),count) in enumerate(zip(SHOTS,FRAMES)):
   for i in range(count):
    t=i/max(1,count-1);s=t*t*(3-2*t)
    if frm is None:picture=full.copy()
    else:picture=crop(tuple(frm[j]*(1-s)+to[j]*s for j in range(3)))
    # Initial title is small and short, not a persistent watermark.
    if ix==0 and 6<i<round(1.6*FPS):
     text_layer=picture.copy()
     cv2.rectangle(text_layer,(0,78),(W,177),(17,22,24),-1)
     alpha=.45*min(1,(i-6)/8,(1.6*FPS-i)/10)
     picture=cv2.addWeighted(picture,1-max(0,alpha),text_layer,max(0,alpha),0)
     if alpha>.14:cv2.putText(picture,"DEATH AND THE CHILD",(18,134),cv2.FONT_HERSHEY_SIMPLEX,.77,(230,227,211),2,cv2.LINE_AA)
    proc.stdin.write(np.ascontiguousarray(picture).tobytes())
    if i==count//2:contact.append(cv2.resize(picture,(216,384),interpolation=cv2.INTER_AREA))
   timeline.append({"number":ix+1,"start_s":round(position/FPS,2),"duration_s":count/FPS,
    "artwork":WORK_ID,"framing":name,"move":"slow_push" if frm is not None else "static",
    "camera_reason":"semantic_detail" if frm is not None else "give viewer complete original",
    "visual_anchor":anchor,"complex_detail":ix in (2,3,4),
    "semantic_human_review":"PENDING"})
   position+=count
  proc.stdin.close()
  error=proc.stderr.read()
  if proc.wait()!=0:raise RuntimeError("FFmpeg encoding failed "+error.decode(errors="replace")[-1300:])
 except Exception:
  proc.kill()
  raise

 sheet=np.full((3*392,3*224,3),20,dtype=np.uint8)
 for i,p in enumerate(contact):
  x=(i%3)*224+4;y=(i//3)*392+4
  sheet[y:y+384,x:x+216]=p
 cv2.imwrite(str(OUT/"CONTACT_SHEET.jpg"),sheet)
 return mp4,timeline

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 q=json.loads((ROOT/"research/artvision_owner_selected_30_future_20261109.json").read_text())
 match=[w for w in q["works"] if w.get("title_as_chosen")==OWNER_TITLE and w.get("artist_as_chosen")=="Edvard Munch"]
 assert len(match)==1 and match[0]["selection_order"]==18
 assert not list((ROOT/"queue").glob("artvision_owner_30_render_checkpoint_*dead*mother*.json"))
 assert not list((ROOT/"queue").glob("artvision_owner_30_render_checkpoint_*death*child*.json"))
 source,src_url=exact_source()
 music=compose_music()
 video,story=render(source,music)
 call(["ffmpeg","-v","error","-xerror","-i",video,"-map","0","-f","null","-"])
 info=json.loads(call(["ffprobe","-v","error","-show_format","-show_streams","-of","json",video]))
 vids=[s for s in info["streams"] if s.get("codec_type")=="video"]
 sounds=[s for s in info["streams"] if s.get("codec_type")=="audio"]
 assert len(vids)==1 and vids[0]["codec_name"]=="h264" and (vids[0]["width"],vids[0]["height"])==(W,H)
 assert len(sounds)==1 and sounds[0]["codec_name"]=="aac"
 assert abs(float(info["format"]["duration"])-DURATION)<.4
 assert int(vids[0].get("nb_frames",FRAME_COUNT))==FRAME_COUNT
 save_json("FFPROBE.json",info)

 sys.path.insert(0,str(ROOT/"src"))
 from director_reference_v326 import analyze_scenes,inspect_black_tail
 blocks,warnings,facts=analyze_scenes([{
    "duration":x["duration_s"],"artwork":x["artwork"],"framing":x["framing"],"move":x["move"],
    "camera_reason":x["camera_reason"],"visual_anchor":x["visual_anchor"],
    "complex_detail":x["complex_detail"]
 } for x in story],short=True)
 tail_w,tail_facts=inspect_black_tail(video,DURATION)
 assert not blocks, "V326 director timeline blocking errors"
 save_json("DIRECTOR_V326.json",{"blocking":blocks,"warnings":warnings,"facts":facts,"black_tail_warnings":tail_w,"black_tail_scan":tail_facts,
 "full_speed_human_artistic_QA":"PENDING"})

 rights={
 "owner_selected_title":OWNER_TITLE,"museum_official_title":OFFICIAL_TITLE,"artist":"Edvard Munch","year":1899,
 "museum_object":OFFICIAL_URL,"accession":"MM.M.00420","canvas_cm":[104.5,179.0],
 "original_file_page":COMMONS_PAGE,"original_download_url":src_url,"source_bytes":SOURCE_BYTES,
 "source_pixels":SOURCE_PIXELS,"source_sha1":SOURCE_SHA1,"source_sha256":sha_file(source),
 "reproduction_status":"Faithful PD-Art digital reproduction from Munch Museum per Wikimedia Commons; territorial reuse/commercial distribution rights to recheck",
 "retail_social_rights":"PENDING","museum_photograph_license":"NOT CLAIMED",
 "gallery_or_frame_in_video":False,"score":"fully original generated harmonic ambient music",
 "artwork_was_not_ai_redrawn":True,"publication_authorized":False}
 save_json("SOURCE_RIGHTS.json",rights)
 save_json("STORYBOARD.json",{"work":WORK_ID,"duration_s":DURATION,"scenes":story,"visual_truth":"exact original image checked; semantic QA by human pending"})
 save_json("SOCIAL_DRAFTS.json",{
 "title":"Death and the Child — Edvard Munch (1899)",
 "facebook":"Una bambina si copre le orecchie. Dietro di lei, una figura immobile nel letto. Edvard Munch, Death and the Child (1899), MUNCH Oslo. Il quadro non racconta soltanto la morte: ci mostra la distanza tra ciò che è accaduto e ciò che un bambino riesce a comprendere.",
 "instagram":"Le mani sulle orecchie, il letto sullo sfondo, il rosso del pavimento. Death and the Child, 1899, Edvard Munch. #ArtHistory",
 "tiktok":"La bambina si copre le orecchie. Nel letto alle sue spalle, tutto è fermo. Death and the Child — Edvard Munch, 1899. #ArtTok",
 "youtube":"Death and the Child — Edvard Munch 1899. An original cinematic study of MM.M.00420 at MUNCH, Oslo.",
 "status":"DRAFT_NOT_PUBLISHED"})

 qa={"schema":"artvision-owner-30-cinema-private-v1","work":OFFICIAL_TITLE,"owner_title":OWNER_TITLE,
 "variant":"cinema_standard","source_sha1":SOURCE_SHA1,"source_sha256":sha_file(source),
 "mp4_filename":video.name,"mp4_bytes":video.stat().st_size,"mp4_sha256":sha_file(video),
 "resolution":[W,H],"fps":FPS,"frames":FRAME_COUNT,"duration_s":DURATION,"shots":len(story),
 "ffmpeg_all_streams_full_decode":"PASS","v326_blocking_errors":len(blocks),"v326_warnings":warnings+tail_w,
 "artistic_full_speed_QA":"PENDING","territorial_commercial_rights":"PENDING",
 "gold":False,"published":False,"paid_api_calls":0,"original_10_queue_slots_added":0,
 "new_secondary_30_cinema_candidates":1}
 save_json("QA_TECHNICAL.json",qa)
 members=["VIDEO_ANDROID_REVIEW.mp4","COVER.jpg","CONTACT_SHEET.jpg","SOURCE_RIGHTS.json","STORYBOARD.json","SOCIAL_DRAFTS.json","QA_TECHNICAL.json","FFPROBE.json","DIRECTOR_V326.json"]
 z=OUT/"ANDROID_REVIEW_PACKAGE.zip"
 with zipfile.ZipFile(z,"w",zipfile.ZIP_DEFLATED,compresslevel=3) as f:
  for name in members:f.write(OUT/name,arcname=name)
 with zipfile.ZipFile(z) as f:
  assert f.testzip() is None
  assert hashlib.sha256(f.read(video.name)).hexdigest()==qa["mp4_sha256"]
 print("NEW_MUNCH_DEATH_CHILD_CINEMA_REVIEW",json.dumps({"mp4_sha256":qa["mp4_sha256"],"mp4_bytes":qa["mp4_bytes"],
 "zip_sha256":sha_file(z),"duration":DURATION,"ffmpeg":"PASS","zip_crc":"PASS","gold":False}),flush=True)

if __name__=="__main__":main()
