#!/usr/bin/env python3
"""La Storia Rivive ONLY. New source-locked I2I episode from actual 1895–1905
Lumiere anthology: women smiling into the original moving camera.
Historical origin is real; individual short film identification/Italy reuse PENDING.
NO Vidu, purchases, social/site publication, or modifications to other formats."""
import importlib.util,sys,hashlib,json,subprocess,urllib.request,cv2,numpy as np,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("smile_template",ROOT/"src/storia_cinema_magicien_1898_visual_social_v1.py")
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
OUT=ROOT/"output/storia_lumiere_smiling_women_new_review"
OUT.mkdir(parents=True,exist_ok=True)
m.OUT=OUT
m.SOURCE=OUT/"ARCHIVE_LUMIERE_1895_1905_ORIGINAL_COMPILATION.mp4"
m.CLIP=OUT/"ACTUAL_1900_ERA_CROWD_SHOT_CFR.mp4"
m.MOVIE=OUT/"LUMIERE_SMILING_WOMEN_NEW_REAL_I2I_REVIEW.mp4"
m.ZIP=OUT/"LUMIERE_SMILING_WOMEN_REAL_I2I_REVIEW_ANDROID.zip"
m.START=1919.0     # 31:59 ORIGINAL compilation, NOT elapsed local clip
m.DURATION=13.5
m.ANCHOR=round(6.0*m.FPS) # exact B/W original anchor 32:05
m.HOLD=round(1.5*m.FPS)
ARCHIVE="https://archive.org/details/lumiereaaventuracomeca18951905"
URL="https://archive.org/download/lumiereaaventuracomeca18951905/Lumi%C3%A8re%2C%20a%20aventura%20come%C3%A7a%20%281895-1905%29.mp4"
EXPECTED_SHA="1a1fe806dba52b5c845d59353cbf91a8d28ed2978eb161528477fd2a068a2dc8"
EXPECTED_BYTES=593660232
def source():
    if not m.SOURCE.exists() or m.SOURCE.stat().st_size!=EXPECTED_BYTES:
        # Two bounded archive downloads max, NEVER a new paid service.
        for attempt in range(2):
            tmp=m.SOURCE.with_suffix(".partial")
            try:
                if tmp.exists():tmp.unlink()
                req=urllib.request.Request(URL,headers={"User-Agent":"LaStoriaRiviveAuthenticArchiveResearch/1.0 github.com/GGIANLUCAA/Tra-le-pagine-"})
                with urllib.request.urlopen(req,timeout=150) as r,tmp.open("wb") as f:
                    while True:
                        chunk=r.read(1<<20)
                        if not chunk:break
                        f.write(chunk)
                        if f.tell()>EXPECTED_BYTES:raise RuntimeError("ARCHIVE_DOWNLOAD_TOO_LARGE")
                if tmp.stat().st_size!=EXPECTED_BYTES:raise RuntimeError("ARCHIVE_DOWNLOAD_INCOMPLETE")
                if m.sha(tmp)!=EXPECTED_SHA:raise RuntimeError("ARCHIVE_SHA256_DIFFERENT")
                tmp.replace(m.SOURCE);break
            except Exception:
                if tmp.exists():tmp.unlink()
                if attempt:raise
    if m.sha(m.SOURCE)!=EXPECTED_SHA:raise RuntimeError("SOURCE_SHA256_MISMATCH")
    meta=json.loads(m.run(["ffprobe","-v","error","-select_streams","v:0","-show_entries","stream=width,height,avg_frame_rate","-show_entries","format=duration","-of","json",str(m.SOURCE)]))
    st=meta["streams"][0]
    if st["width"]!=854 or st["height"]!=480 or abs(float(meta["format"]["duration"])-5704.083333)>2:raise RuntimeError("ARCHIVE_PROBE_INCONSISTENT")
    # Image has 4:3 historic film centered in 16:9 compilation. Cut black sidebars;
    # do NOT crop out any person or fake upscale/native 4K claims.
    m.run(["ffmpeg","-nostdin","-y","-v","error","-ss",str(m.START),"-i",str(m.SOURCE),"-t",str(m.DURATION),
        "-vf","crop=640:480:(iw-640)/2:0,fps=24,scale=960:720","-an",
        "-c:v","libx264","-preset","veryfast","-crf","18","-pix_fmt","yuv420p",str(m.CLIP)],260)
    cap=cv2.VideoCapture(str(m.CLIP))
    n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT));fps=cap.get(cv2.CAP_PROP_FPS)
    for idx in (0,24,60,m.ANCHOR-7,m.ANCHOR,m.ANCHOR+7,216,312):
        cap.set(cv2.CAP_PROP_POS_FRAMES,idx);ok,im=cap.read()
        if ok:cv2.imwrite(str(OUT/f"ORIGINAL_MOVING_FRAME_{idx:04d}.jpg"),im)
    cap.release()
    if n<315 or abs(fps-24)>.1:raise RuntimeError("MOTION_IS_NOT_AUTHENTIC_OR_TOO_SHORT")
    m.write("RIGHTS.json",{"production":"SOURIRES DEVANT LA CAMERA · 1895-1905",
       "historical_origin":"Cinématographe Lumière anthology, original shorts 1895–1905",
       "clip_identity":"Exact short's individual title and exact date PENDING specialist attribution; no single year claimed",
       "source":ARCHIVE,"asset_download":URL,"original_compilation_sha256":EXPECTED_SHA,
       "downloaded_source_sha256":m.sha(m.SOURCE),"source_resolution":[854,480],
       "film_cropped_frame_resolution":[640,480],"output_resolution_note":"1080x1920 upscaled display only",
       "original_extract_start_s":m.START,"duration_s":m.DURATION,
       "source_anchor_absolute_seconds":m.START+m.ANCHOR/m.FPS,
       "source_anchor_local_frame_index":m.ANCHOR,
       "territory_italy_reuse_rights":"PENDING: historic 1895–1905 footage, compilation restored 2015; confirm before any distribution",
       "paid_calls":0,"vidu_calls":0,"publication":False,"artistic_review":"PENDING"})
    return m.CLIP
m.source=source
def photo(base,original):
    cv2.imwrite(str(OUT/"ANCHOR_REAL_ORIGINAL_BW.png"),original)
    cv2.imwrite(str(OUT/"ANCHOR_AI_NEURAL_COLOR_BASE.png"),base)
    state={"provider":"finegrain/finegrain-image-enhancer","source":ARCHIVE,
       "exact_source_time_s":m.START+m.ANCHOR/m.FPS,
       "exact_original_frame_sha256":m.sha(OUT/"ANCHOR_REAL_ORIGINAL_BW.png"),
       "actual_free_I2I":False,"artistic_review":"PENDING","paid_requests":0}
    try:
        prompt=("An extraordinarily convincing modern color DOCUMENTARY PHOTOGRAPH reconstruction of this SAME EXACT original black-and-white movie frame. "
            "Three prominent historically dressed young women walking toward a fixed movie camera; preserve precisely all existing people, "
            "the women's real smiles, eye direction, age, gestures, hand positions, collars, fabric, hair and late Victorian hats. "
            "Maintain their exact positions and natural faces, all people behind, trees, road, the background exactly as in the input. "
            "Subtle realistically imperfect skin pores, real eyes, natural asymmetry, period-accurate neutral clothing and real daylight. "
            "Do not create anyone, do not turn background objects into faces. Photojournalistic and emotionally authentic, not illustration.")
        negative=("new person, duplicate woman, extra hand, extra arm, invented face, face formed in a hat, merged face, "
            "wrong era clothes, purple, excessive saturated color, unnatural teeth, overly smooth skin, wax skin, cartoon, "
            "painting, excessive sharpening, fabricated expression, altered background, new objects, blurry smudged faces")
        cli=m.Client("finegrain/finegrain-image-enhancer",verbose=False)
        result=cli.predict(m.handle_file(str(OUT/"ANCHOR_AI_NEURAL_COLOR_BASE.png")),prompt,negative,
                           1900,2,1.12,.97,6,112,144,.42,18,"DDIM",api_name="/process")
        obj=result[1] if isinstance(result,(list,tuple)) and len(result)>1 else result
        if isinstance(obj,dict):obj=obj.get("path")
        im=cv2.imread(str(obj)) if obj else None
        if im is None:raise RuntimeError("FREE_PHOTO_PROVIDER_RETURNED_NO_IMAGE")
        im=cv2.resize(im,(960,720));sat=float(cv2.cvtColor(im,cv2.COLOR_BGR2HSV)[:,:,1].mean())
        delta=float(np.mean(cv2.absdiff(im,base)))
        corr1=m.corr(original,im)
        photo_path=OUT/"GENERATIVE_PHOTO_REAL_CANDIDATE.png"
        cv2.imwrite(str(photo_path),im)
        state.update({"actual_free_I2I":True,"photo_sha256":m.sha(photo_path),
            "structure_corr_original":round(corr1,4),"sat":round(sat,2),"delta_vs_ddcolor":round(delta,2)})
        if not (corr1>.77 and 15<sat<135 and delta>4):
            state["status"]="PHOTO_TECHNICAL_GATE_FAIL";m.write("PHOTO_QA.json",state)
            raise RuntimeError("FREE_PHOTO_NOT_PLAUSIBLE_SOURCE_LOCKED")
        state["status"]="TECH_PASS_ANATOMY_AND_EMOTION_HUMAN_QA_PENDING"
        m.write("PHOTO_QA.json",state)
        return im
    except Exception as e:
        state["failure"]=str(e)[:300]
        state.setdefault("status","FREE_PHOTO_FAILED")
        m.write("PHOTO_QA.json",state)
        raise
m.photo=photo
old_canvas=m.frame_canvas
def canvas(scene,title="",small=""):
    return old_canvas(scene,title.replace("LE MAGICIEN","SOURIRES DAVANTI ALLA CAMERA").replace("1898","1895-1905"),
      small.replace("LOUIS MÉLIÈS","LUMIÈRE · ARCHIVIO").replace("1898","1895-1905"))
m.frame_canvas=canvas
try:
    m.main()
    social={
      "FACEBOOK":"SOURIRES DAVANTI ALLA CAMERA · 1895–1905. Tre donne si avvicinano sorridendo all'obiettivo in un filmato storico della raccolta Lumière. Ripresa originale in movimento e ricostruzione fotografica AI interpretativa. Anteprima tecnica non pubblicata.",
      "INSTAGRAM":"Un sorriso che attraversa oltre un secolo. Volti e movimento autentici da una pellicola Lumière (1895–1905); colore e fotografia moderna sono ricostruzioni AI dichiarate. Revisione artistica in corso.",
      "TIKTOK":"Un secolo prima dei selfie, tre sorrisi davanti a una cinepresa. Ripresa storica originale, ricostruzione fotografica AI source-locked. Non è un vero video a colori del 1900.",
      "YOUTUBE":"Smiles at the Camera · Lumière anthology 1895–1905. Genuine period movie source: "+ARCHIVE+". Exact short identification and 2015 digital restoration reuse rights pending. Modern AI image is an interpretation, not authentic 1900 color."
    }
    for k,v in social.items():(OUT/f"POST_{k}.txt").write_text(v+"\n",encoding="utf8")
    (OUT/"README_REVIEW_ONLY.txt").write_text("NEW SOURCE EPISODE. H264/AAC 1080x1920 display, NOT native 4K. Art review pending. "
      "Source-locked AI still generated free, moving footage truly historical with neural DDColor chroma (NOT generative I2V). "
      "Exact individual film year, 2015 restoration territorial rights pending. No social/site publication or Vidu use.\n",encoding="utf8")
    real=OUT/"ANCHOR_REAL_ORIGINAL_BW.png"
    ai=OUT/"GENERATIVE_PHOTO_REAL_CANDIDATE.png"
    from PIL import Image,ImageDraw
    a=Image.open(real).convert("RGB");b=Image.open(ai).convert("RGB")
    both=Image.new("RGB",(a.width*2,a.height+45),(20,20,20))
    both.paste(a,(0,45));both.paste(b,(a.width,45))
    draw=ImageDraw.Draw(both)
    draw.text((15,14),"TRUE BLACK-WHITE SOURCE FRAME",fill="white")
    draw.text((a.width+15,14),"GENERATIVE I2I PHOTO - PENDING HUMAN QA",fill="white")
    both.save(OUT/"SMILES_EXACT_ORIGINAL_VS_TRUE_I2I.jpg",quality=95)
    include=[m.MOVIE.name,"SOCIAL_COVER.jpg","ORIGINAL_VS_PHOTO_VISUAL_QA.jpg",
       "SMILES_EXACT_ORIGINAL_VS_TRUE_I2I.jpg","VISUAL_REPORT.json","PHOTO_QA.json","RIGHTS.json",
       "README_REVIEW_ONLY.txt","POST_FACEBOOK.txt","POST_INSTAGRAM.txt","POST_TIKTOK.txt","POST_YOUTUBE.txt",
       "GENERATIVE_PHOTO_REAL_CANDIDATE.png","ANCHOR_REAL_ORIGINAL_BW.png"]
    with zipfile.ZipFile(m.ZIP,"w",zipfile.ZIP_DEFLATED,compresslevel=4) as z:
        for name in include:z.write(OUT/name,arcname=name)
    with zipfile.ZipFile(m.ZIP) as z:
        if z.testzip():raise RuntimeError("ZIP_CRC_FAILED")
    for stream,codec in [("v","h264"),("a","aac")]:
        actual=m.run(["ffprobe","-v","error","-select_streams",stream,"-show_entries","stream=codec_name",
            "-of","default=nw=1:nk=1",str(m.MOVIE)]).strip()
        if actual!=codec:raise RuntimeError("WRONG_CODEC_"+stream)
    m.write("DELIVERY.json",{"new_episode":True,"source_sha256":EXPECTED_SHA,
       "video_sha256":m.sha(m.MOVIE),"zip_sha256":m.sha(m.ZIP),
       "full_video_decode_pass":True,"zip_crc_pass":True,
       "artistic_review":"PENDING","rights_italy":"PENDING",
       "source_locked_photo_created":True,"new_vidu_posts":0,"paid_calls":0,"published":False})
    print("NEW_HISTORICAL_SMILES_I2I_VIDEO_REVIEW",m.MOVIE.name,m.sha(m.MOVIE),flush=True)
except Exception as e:
    m.write("FAILURE.json",{"error":type(e).__name__+": "+str(e)[:600],
       "no_approved_video":True,"paid_requests":0,"published":False})
    print("NEW_VIDEO_FAIL_CLOSED",repr(e),flush=True)
    raise
