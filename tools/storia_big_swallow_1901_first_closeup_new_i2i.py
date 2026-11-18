#!/usr/bin/env python3
"""La Storia Rivive ONLY. New source, real 1901 first camera-facing close-up:
The Big Swallow, James Williamson (d.1933). No reuse of rejected 1900 I2I.
Real original B/W motion -> exact source frame -> one free Finegrain I2I ->
genuinely moving original neural chroma, not I2V. Artistic PENDING.
Never spend Vidu, publish social/site, or modify another format.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import quote
import hashlib,importlib.util,json,sys,zipfile
import cv2,numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
module=importlib.util.spec_from_file_location("big_swallow_historical_renderer",ROOT/"src/storia_cinema_magicien_1898_visual_social_v1.py")
m=importlib.util.module_from_spec(module);sys.modules[module.name]=m;module.loader.exec_module(m)
OUT=ROOT/"output/storia_big_swallow_1901_v1"
OUT.mkdir(parents=True,exist_ok=True)
ITEM="silent-the-big-swallow-aka-a-photographic-contortion"
TITLE="THE BIG SWALLOW · 1901"
SOURCE_PAGE="https://archive.org/details/"+ITEM
m.OUT=OUT;m.PAGE=SOURCE_PAGE
m.SOURCE=OUT/"BIG_SWALLOW_1901_AUTHENTIC_SOURCE.mkv"
m.CLIP=OUT/"BIG_SWALLOW_1901_SOURCE_CFR_EXCERPT.mp4"
m.MOVIE=OUT/"BIG_SWALLOW_1901_TRUE_CLOSEUP_I2I_REVIEW.mp4"
m.ZIP=OUT/"BIG_SWALLOW_1901_MP4_COVER_SOCIAL_QA.zip"
m.START=10.0;m.DURATION=19.0;m.ANCHOR=round(7.2*m.FPS);m.HOLD=round(1.72*m.FPS)
original_canvas=m.frame_canvas
def canvas(scene,title="",small=""):
    title=title.replace("LE MAGICIEN", "THE BIG SWALLOW").replace("1898","1901")
    small=small.replace("LOUIS MÉLIÈS","JAMES WILLIAMSON").replace("1898","1901")
    return original_canvas(scene,title,small)
m.frame_canvas=canvas
def source():
    ua="LaStoriaRiviveHistoricalFilm/1.0 (+github.com/GGIANLUCAA/Tra-le-pagine-)"
    with urlopen(Request("https://archive.org/metadata/"+ITEM,headers={"User-Agent":ua}),timeout=60) as r:
        data=json.load(r)
    filename="The Big Swallow AKA A Photographic Contortion.mkv"
    info=next((x for x in data.get("files",[]) if x.get("name")==filename),None)
    if info is None or not 10_000_000<int(info["size"])<27_000_000 or not info.get("sha1"):
        raise RuntimeError("ARCHIVE_ORIGINAL_FILE_METADATA_UNVERIFIED")
    url="https://archive.org/download/"+ITEM+"/"+quote(filename)
    if not m.SOURCE.exists() or m.SOURCE.stat().st_size!=int(info["size"]):
        with urlopen(Request(url,headers={"User-Agent":ua}),timeout=180) as r,m.SOURCE.open("wb") as f:
            while True:
                b=r.read(1<<20)
                if not b:break
                f.write(b)
                if f.tell()>27_000_000:raise RuntimeError("DOWNLOADED_WRONG_FILM_SIZE")
    raw=m.SOURCE.read_bytes()
    if len(raw)!=int(info["size"]) or hashlib.sha1(raw).hexdigest()!=info["sha1"]:
        raise RuntimeError("ARCHIVE_SOURCE_SHA1_INVALID")
    data=json.loads(m.run(["ffprobe","-v","error","-select_streams","v:0",
        "-show_entries","stream=width,height,avg_frame_rate","-show_entries","format=duration",
        "-of","json",str(m.SOURCE)]))
    sw=int(data["streams"][0]["width"]);sh=int(data["streams"][0]["height"])
    duration=float(data["format"]["duration"])
    if sw<400 or sh<290 or duration<m.START+m.DURATION+1.0:
        raise RuntimeError("ORIGINAL_SOURCE_INSUFFICIENT_RESOLUTION_OR_DURATION_"+str((sw,sh,duration)))
    m.run(["ffmpeg","-nostdin","-y","-v","error","-ss",str(m.START),"-i",str(m.SOURCE),
        "-t",str(m.DURATION),"-vf",
        "fps=24,scale=960:720:force_original_aspect_ratio=decrease,pad=960:720:(ow-iw)/2:(oh-ih)/2",
        "-an","-c:v","libx264","-preset","veryfast","-crf","17","-pix_fmt","yuv420p",str(m.CLIP)],220)
    cap=cv2.VideoCapture(str(m.CLIP)); n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if n<round(m.DURATION*24)-4:raise RuntimeError("NOT_ACTUAL_ORIGINAL_FILM_MOTION")
    shots=[]
    for idx in (0,24,48,72,96,120,144,m.ANCHOR-7,m.ANCHOR,m.ANCHOR+7,216,288,360,420):
        cap.set(cv2.CAP_PROP_POS_FRAMES,idx); ok,frame=cap.read()
        if ok:
            name=f"ORIGINAL_FILM_FRAME_{idx:04d}.jpg"
            cv2.imwrite(str(OUT/name),frame,[cv2.IMWRITE_JPEG_QUALITY,95])
            shots.append({"idx":idx,"absolute_time_s":round(m.START+idx/24,4),"file":name})
    cap.release()
    m.write("RIGHTS.json",{
      "source":SOURCE_PAGE,"filmmaker":"James Williamson","filmmaker_death":1933,
      "film_year":1901,"source_url":url,"original_source_sha1":info["sha1"],
      "original_source_sha256":hashlib.sha256(raw).hexdigest(),
      "original_size_bytes":len(raw),"source_resolution_px":[sw,sh],
      "source_duration_s":duration,"excerpt_start_s":m.START,
      "excerpt_duration_s":m.DURATION,"source_anchor_frame_index":m.ANCHOR,
      "source_anchor_absolute_time_s":m.START+m.ANCHOR/m.FPS,
      "source_scout_frames":shots,
      "rights_note":"Original film 1901, director and cinematographer James Williamson d.1933, historical original PD by Italy life+70 and US pre-1931; check copy-specific scan and reuse before publication.",
      "synthetic_color_is_modern_interpretation":True,
      "upscale_is_not_original_native_4K":True,
      "no_automatic_site_social_publishing":True,"no_paid_requests":True
    })
    print("AUTHENTIC_ONE_HUMAN_CLOSEUP_SOURCE_SHA256",hashlib.sha256(raw).hexdigest(),sw,sh,flush=True)
    return m.CLIP
m.source=source
def photo(base,orig):
    cv2.imwrite(str(OUT/"ANCHOR_REAL_ORIGINAL_BW.png"),orig)
    cv2.imwrite(str(OUT/"ANCHOR_AI_NEURAL_COLOR_BASE.png"),base)
    state={"provider":"finegrain/finegrain-image-enhancer","real_free_I2I":False,
        "original_frame_absolute_s":m.START+m.ANCHOR/m.FPS,
        "original_frame_index_cfr":m.ANCHOR,"source":SOURCE_PAGE,"paid_calls":0,
        "vidu_posts":0,"artistic_review":"PENDING"}
    m.write("PHOTO_QA.json",state)
    try:
        prompt=("A contemporary ultra-realistic photographic image-to-image restoration of the EXACT original 1901 motion-picture frame from The Big Swallow. "
          "There is ONE solitary adult Edwardian male performer seen in a true original camera-facing close-up, visibly approaching and making an intense funny facial expression toward the camera. "
          "Photograph that SAME man in the identical pose with his REAL period clothes, hat, pince-nez glasses and facial hair ONLY IF THOSE FEATURES ARE VISIBLE IN THE SOURCE. "
          "Keep exactly the original person, facial expression, eye orientation, mouth opening, chin, nose, facial proportions, perspective and simple background. "
          "The image must look like a sharply focused photograph taken today of the unchanged actual Edwardian character: natural pores, real human skin, optical microcontrast, natural daylight and believable colour. "
          "Do not invent any second person, mouth, teeth, hand, objects or background figures. No Hollywood actors, contemporary clothes or cartoon edits.")
        neg=("second person, extra face, extra eye, double mouth, fused face, altered eye shape, "
          "fake teeth, fake eyebrows, extra head, plastic skin, oversmoothing, painted face, "
          "anime, CGI, illustration, weird nose, fake spectacles, invented hats, extra camera, "
          "beard hallucination, orange skin, neon color, modern clothing, changed scene")
        client=m.Client("finegrain/finegrain-image-enhancer",verbose=False)
        result=client.predict(m.handle_file(str(OUT/"ANCHOR_AI_NEURAL_COLOR_BASE.png")),prompt,neg,
          1901,2,1.10,.96,6,112,144,.4,18,"DDIM",api_name="/process")
        path=result[1] if isinstance(result,(tuple,list)) and len(result)>1 else result
        if isinstance(path,dict):path=path.get("path")
        image=cv2.imread(str(path)) if path else None
        if image is None:raise RuntimeError("NO_REAL_FREE_GENERATIVE_PHOTO_RETURNED")
        image=cv2.resize(image,(960,720))
        destination=OUT/"GENERATIVE_PHOTO_REAL_CANDIDATE.png"
        cv2.imwrite(str(destination),image)
        corr=m.corr(orig,image)
        sat=float(cv2.cvtColor(image,cv2.COLOR_BGR2HSV)[:,:,1].mean())
        delta=float(np.mean(cv2.absdiff(base,image)))
        state.update({"real_free_I2I":True,"photo_sha256":m.sha(destination),
          "original_luma_corr":round(corr,4),"saturation":round(sat,2),
          "non_ddcolor_delta":round(delta,2)})
        if corr<.78 or not 15<sat<140 or delta<2.5:
            state["status"]="REAL_PHOTO_FAIL_TECHNICAL_GATE"
            m.write("PHOTO_QA.json",state)
            raise RuntimeError("REAL_I2I_SOURCE_IDENTITY_OR_COLOR_NOT_PASS")
        state["status"]="REAL_FREE_I2I_TECHNICAL_PASS_ARTISTIC_REVIEW_NOT_GRANTED"
        m.write("PHOTO_QA.json",state)
        return image
    except Exception as error:
        state["error"]=type(error).__name__+": "+str(error)[:250]
        if "status" not in state:state["status"]="FREE_PHOTO_PROVIDER_UNAVAILABLE"
        m.write("PHOTO_QA.json",state)
        raise
m.photo=photo
try:
    m.main()
    posts={
     "FACEBOOK":"THE BIG SWALLOW · 1901. Un uomo si avvicina alla macchina da presa come nessuno aveva mai osato fare. La reazione è recitata nel film storico originale di James Williamson: movimento autentico, fotografia restaurata da IA dichiarata. Anteprima in revisione.",
     "INSTAGRAM":"1901. Una faccia che invade lo schermo: il cinema scopre il primissimo piano. The Big Swallow di James Williamson, frame originale e fotografia AI interpretativa. Non è colore storico. #CinemaMuto #LaStoriaRivive",
     "TIKTOK":"1901: quando un attore sembrò inghiottire la cinepresa. Film vero → fermo originale → fotografia AI → movimento del film vero. Anteprima non pubblicata. #TheBigSwallow #Cinema",
     "YOUTUBE":"THE BIG SWALLOW · 1901 | James Williamson\nOriginal archival file: "+SOURCE_PAGE+"\nReal archival performance, source-locked AI photographic interpretation. Original film color was black and white. No new AI-generated motion. OWNER REVIEW."
    }
    for site,copy in posts.items():
        (OUT/f"POST_{site}.txt").write_text(copy+"\n",encoding="utf8")
    (OUT/"README_OWNER_REVIEW.txt").write_text("ONLY OWNER ARTISTIC REVIEW. Original 1901 film by James Williamson; one free Finegrain photographic still. Authentic movement returns with DDColor chroma, NOT temporal AI photo. No Vidu or expense; no site/social publishing. All resolution upscaled 1080x1920, not genuine 4K.\n",encoding="utf8")
    source_frame=OUT/"ANCHOR_REAL_ORIGINAL_BW.png";picture=OUT/"GENERATIVE_PHOTO_REAL_CANDIDATE.png"
    before=Image.open(source_frame).convert("RGB")
    after=Image.open(picture).convert("RGB")
    comparison=Image.new("RGB",(1920,770),(14,15,18))
    comparison.paste(before,(0,50));comparison.paste(after,(960,50))
    draw=ImageDraw.Draw(comparison)
    draw.text((12,12),"SOURCE: EXACT BLACK-WHITE FRAME - THE BIG SWALLOW 1901",fill="white")
    draw.text((975,12),"REAL FREE I2I PHOTO - ARTISTIC GATE PENDING",fill="white")
    comparison.save(OUT/"BEFORE_AFTER_EXACT_ANCHOR.jpg",quality=96)
    report=json.loads((OUT/"VISUAL_REPORT.json").read_text())
    report.update({"title":TITLE,"source":SOURCE_PAGE,
        "source_sha256":m.sha(m.SOURCE),"anchor_time_s":m.START+m.ANCHOR/m.FPS,
        "anchor_frame_index":m.ANCHOR,"source_frame_sha256":m.sha(source_frame),
        "real_i2i_photo_sha256":m.sha(picture),
        "face_anatomy_human_approved":False,"artistic_approval":False,
        "source_rights_check":"PENDING_FINAL","vidu_generated":False,"paid_api_calls":0})
    m.write("VISUAL_REPORT.json",report)
    with zipfile.ZipFile(m.ZIP,"w",zipfile.ZIP_DEFLATED,compresslevel=4) as archive:
        for name in [m.MOVIE.name,"SOCIAL_COVER.jpg","ORIGINAL_VS_PHOTO_VISUAL_QA.jpg",
         "BEFORE_AFTER_EXACT_ANCHOR.jpg","PHOTO_QA.json","RIGHTS.json",
         "VISUAL_REPORT.json","README_OWNER_REVIEW.txt","ANCHOR_REAL_ORIGINAL_BW.png",
         "GENERATIVE_PHOTO_REAL_CANDIDATE.png",
         *[f"POST_{p}.txt" for p in posts]]:
            archive.write(OUT/name,arcname=name)
    with zipfile.ZipFile(m.ZIP) as archive:
        if archive.testzip():raise RuntimeError("ANDROID_KIT_ZIP_CRC_FAIL")
    for stream,required in [("v","h264"),("a","aac")]:
        detected=m.run(["ffprobe","-v","error","-select_streams",stream,
              "-show_entries","stream=codec_name","-of","default=nw=1:nk=1",str(m.MOVIE)]).strip()
        if detected!=required:raise RuntimeError("REAL_VIDEO_CODEC_FAILURE_"+stream)
    m.run(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(m.MOVIE),"-f","null","-"],220)
    m.write("FINAL_TECH_QA.json",{"movie_sha256":m.sha(m.MOVIE),"zip_sha256":m.sha(m.ZIP),
         "full_mp4_decode":True,"zip_crc_pass":True,"new_1901_source":True,
         "real_Finegrain_photo":True,"artistic_review":"PENDING",
         "zero_paid_calls":True,"no_site_or_social_publication":True})
    print("BIG_SWALLOW_REAL_NEW_VIDEO_REVIEW_CREATED",m.MOVIE.name,m.sha(m.MOVIE),flush=True)
except Exception as error:
    m.write("FAILURE.json",{"error":str(error)[:500],
       "real_new_video_delivered":False,"artistic_approval":False,"no_paid_calls":True})
    raise
