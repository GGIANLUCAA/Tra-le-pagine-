#!/usr/bin/env python3
"""La Storia Rivive ONLY: NEW archival film La petite fille et son chat (1900).
REAL historic B/W moving film -> exact frame -> FREE photogenerative I2I ->
same genuine historical motion with neural chroma. Strict owner review only.
No Vidu, no paid requests, no website/social publication, no other projects.
"""
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
import hashlib,importlib.util,json,sys,zipfile,subprocess
import cv2,numpy as np

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("storia_girl_cat_template",ROOT/"src/storia_cinema_magicien_1898_visual_social_v1.py")
m=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=m
spec.loader.exec_module(m)
OUT=ROOT/"output/storia_petite_fille_chat_1900_review"
OUT.mkdir(parents=True,exist_ok=True)
TITLE="LA PETITE FILLE ET SON CHAT · 1900"
FILENAME="La Petite fille et son chat - Film 1900.webm"
PAGE="https://commons.wikimedia.org/wiki/File:La_Petite_fille_et_son_chat_-_Film_1900.webm"
m.OUT=OUT
m.PAGE=PAGE
m.SOURCE=OUT/"LUMIERE_GIRL_CAT_1900_ORIGINAL.webm"
m.CLIP=OUT/"REAL_LUMIERE_EXCERPT_CFR.mp4"
m.MOVIE=OUT/"PETITE_FILLE_CHAT_1900_NEW_REAL_I2I_OWNER_REVIEW.mp4"
m.ZIP=OUT/"PETITE_FILLE_CHAT_1900_ANDROID_OWNER_REVIEW.zip"
m.START=2.0
m.DURATION=18.0
m.ANCHOR=round(5.0*m.FPS)
m.HOLD=round(1.75*m.FPS)
orig_canvas=m.frame_canvas
def canvas(scene,title="",small=""):
    title=title.replace("LE MAGICIEN", "GIRL & CAT").replace("1898","1900")
    small=small.replace("LOUIS MÉLIÈS","LOUIS LUMIÈRE").replace("1898","1900")
    return orig_canvas(scene,title,small)
m.frame_canvas=canvas
def source():
    """Use original standalone Internet Archive item when Commons upload gives HTTP429.
    Exact 2012 archive file byte-checked against IA sha1; never claim native 1080p.
    """
    from urllib.parse import quote
    ua="LaStoriaRiviveAuthenticSource/1.0 (+github.com/GGIANLUCAA/Tra-le-pagine-)"
    item="LaPetiteFilleEtSonChat"
    with urlopen(Request("https://archive.org/metadata/"+item,headers={"User-Agent":ua}),timeout=40) as response:
        meta=json.load(response)
    filename="1899Lumire-LaPetiteFilleEtSonChat.mp4"
    record=next((f for f in meta.get("files",[]) if f.get("name")==filename),None)
    if not record or int(record.get("size",0))<2_000_000 or int(record.get("size",0))>8_000_000 or not record.get("sha1"):
        raise RuntimeError("STANDALONE_ORIGINAL_IA_FILE_METADATA_NOT_VERIFIED")
    u="https://archive.org/download/"+item+"/"+quote(filename)
    m.SOURCE=OUT/"LUMIERE_GIRL_AND_CAT_IA_2012_SOURCE.mp4"
    if not m.SOURCE.exists() or m.SOURCE.stat().st_size!=int(record["size"]):
        with urlopen(Request(u,headers={"User-Agent":ua}),timeout=120) as response,m.SOURCE.open("wb") as target:
            while True:
                block=response.read(1024*1024)
                if not block:break
                target.write(block)
                if target.tell()>8_000_000:raise RuntimeError("SOURCE_EXCEEDS_METADATA_CAP")
    raw=m.SOURCE.read_bytes()
    if len(raw)!=int(record["size"]) or hashlib.sha1(raw).hexdigest()!=record["sha1"]:
        raise RuntimeError("AUTHENTIC_IA_ARCHIVE_SOURCE_HASH_MISMATCH")
    p=json.loads(m.run(["ffprobe","-v","error","-select_streams","v:0",
        "-show_entries","stream=width,height,r_frame_rate","-show_entries","format=duration",
        "-of","json",str(m.SOURCE)]))
    stream=p["streams"][0];width=int(stream["width"]);height=int(stream["height"])
    duration=float(p["format"]["duration"])
    if width<320 or height<200 or duration<m.START+m.DURATION+1:
        raise RuntimeError("IA_FILM_NOT_LONG_OR_SHARP_ENOUGH_FOR_ANY_REVIEW")
    m.run(["ffmpeg","-nostdin","-y","-v","error","-ss",str(m.START),"-i",str(m.SOURCE),
        "-t",str(m.DURATION),"-vf",
        "fps=24,scale=960:720:force_original_aspect_ratio=decrease,pad=960:720:(ow-iw)/2:(oh-ih)/2",
        "-an","-c:v","libx264","-preset","veryfast","-crf","18","-pix_fmt","yuv420p",
        str(m.CLIP)],180)
    cap=cv2.VideoCapture(str(m.CLIP))
    count=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); fps=float(cap.get(cv2.CAP_PROP_FPS))
    for i in [0,24,48,72,96,m.ANCHOR-7,m.ANCHOR,m.ANCHOR+7,192,288,360]:
        cap.set(cv2.CAP_PROP_POS_FRAMES,i);ok,frame=cap.read()
        if ok:cv2.imwrite(str(OUT/f"SOURCE_SCOUT_FRAME_{i:04d}.jpg"),frame)
    cap.release()
    if count<400 or fps<23.9:raise RuntimeError("STANDALONE_ARCHIVE_CLIP_NOT_18S_REAL_MOTION")
    m.write("RIGHTS.json",{
      "work":"La petite fille et son chat","year_catalogue_lumiere":1900,
      "internet_archive_listing_date":1899,
      "recorded_1900_according_to_catalogue":True,
      "film_director":"Louis Lumiere","director_death_year":1948,
      "reference_catalogue":"https://catalogue-lumiere.com/edition-bluray-2015/",
      "exact_source":"https://archive.org/details/"+item,
      "archive_file":u,"archive_file_sha1":record["sha1"],
      "archive_file_sha256":hashlib.sha256(raw).hexdigest(),
      "source_width_px":width,"source_height_px":height,
      "source_duration_s":duration,"source_codec":"check ffprobe",
      "excerpt_start_s":m.START,"excerpt_duration_s":m.DURATION,
      "exact_frame_at_source_time_s":m.START+m.ANCHOR/m.FPS,
      "anchor_frame_index_in_CFR_excerpt":m.ANCHOR,
      "copyright_note":"1900 original work PD France/Italy (Louis Lumiere d.1948); IA copy marked Public Domain Mark. Verify source rights if redistributing; not 2015 remaster.",
      "1080x1920_output_upscaled_NOT_native_high_resolution":True,
      "artistic_approval":False,"no_vidu_or_paid_requests":True,
      "publication":False})
    print("REAL_STANDALONE_SOURCE_SUCCESS",width,height,record["sha1"],m.sha(m.SOURCE),flush=True)
    return m.CLIP
m.source=source
def photo(base,original):
    original_path=OUT/"ANCHOR_REAL_ORIGINAL_BW.png"
    colorbase=OUT/"ANCHOR_AI_NEURAL_COLOR_BASE.png"
    cv2.imwrite(str(original_path),original)
    cv2.imwrite(str(colorbase),base)
    state={"provider":"finegrain/finegrain-image-enhancer","actual_free_I2I":False,
       "source":PAGE,"anchor_source_local_frame":m.ANCHOR,
       "anchor_absolute_s":m.START+m.ANCHOR/m.FPS,
       "source_original_SHA256":m.sha(m.SOURCE),
       "paid_calls":0,"new_vidu_posts":0,"artistic_review":"PENDING"}
    try:
        client=m.Client("finegrain/finegrain-image-enhancer",verbose=False)
        prompt=("A truly photorealistic contemporary documentary color photograph restoring the EXACT original year 1900 Lumiere film frame. "
          "A single young girl Madeleine Koehler dressed in the SAME authentic 1900 light period garment and period hat visible in the source, "
          "sitting beside the SAME ONE real large house cat interacting with food at a little table, ONLY if those objects appear in this exact frame. "
          "Maintain EXACT girl face angle, real eye gaze, real joyful or surprised expression only as seen, her two real hands, "
          "the cat's original paws, muzzle, ears, eyes, fur markings, furniture, branches, background, poses, "
          "subject spacing and the original unaltered fixed camera view. "
          "Natural real photographic skin with texture, child face proportions, truthful cat anatomy, historic fabric weave and subtle warm daylight. "
          "No invented smiles, people, cat tails, children, hands, extra limbs or props. No plastic skin, no painterly look.")
        neg=("extra child, extra cat, baby doll, face replacement, altered eye gaze, extra hand, fused fingers, "
          "extra animal paw, invented hat, changed clothes, changed age, distorted eyes, overly sharp uncanny face, "
          "cartoon, illustration, synthetic skin, pale wax, orange skin, pink purple sky, extra furniture, "
          "fabric melted into cat, artificial facial expression, modern accessories, text, watermark")
        raw=client.predict(m.handle_file(str(colorbase)),prompt,neg,1900,2,1.12,.97,6,112,144,.42,18,"DDIM",api_name="/process")
        obj=raw[1] if isinstance(raw,(tuple,list)) and len(raw)>1 else raw
        if isinstance(obj,dict):obj=obj.get("path")
        result=cv2.imread(str(obj)) if obj else None
        if result is None:raise RuntimeError("FREE_PROVIDER_RETURNED_NO_ACTUAL_IMAGE")
        result=cv2.resize(result,(960,720))
        sat=float(cv2.cvtColor(result,cv2.COLOR_BGR2HSV)[:,:,1].mean())
        base_delta=float(np.mean(cv2.absdiff(result,base)))
        c1=m.corr(original,result);c2=m.corr(base,result)
        target=OUT/"GENERATIVE_PHOTO_REAL_CANDIDATE.png"
        cv2.imwrite(str(target),result)
        state.update({"actual_free_I2I":True,"real_i2i_image_sha256":m.sha(target),
          "real_source_corr":round(c1,4),"color_base_corr":round(c2,4),
          "mean_saturation":round(sat,2),"pixel_delta_vs_DDColor":round(base_delta,2)})
        if c1<.78 or c2<.80 or not (14<sat<135) or base_delta<3.5:
            state["status"]="PHOTO_TECH_FAIL_NOT_PUBLISHED"
            m.write("PHOTO_QA.json",state)
            raise RuntimeError("SOURCE_LOCKED_REAL_I2I_PHOTO_NOT_USABLE")
        state["status"]="REAL_FREE_I2I_TECH_PASS_FACIAL_ART_REVIEW_PENDING"
        m.write("PHOTO_QA.json",state)
        return result
    except Exception as e:
        state["failure"]=str(e)[:300]
        if "status" not in state:state["status"]="FREE_I2I_PROVIDER_BLOCKED"
        m.write("PHOTO_QA.json",state)
        raise
m.photo=photo
try:
    m.main()
    captions={
      "FACEBOOK": "LA PETITE FILLE ET SON CHAT · 1900. Una bambina, un gatto e un momento vero di vita quotidiana ripreso dai Lumière. La ripresa in movimento è originale; il colore e la fotografia sono ricostruzioni contemporanee interpretative. Anteprima in revisione, non pubblicata.",
      "INSTAGRAM":"1900 · LA PETITE FILLE ET SON CHAT. Un gesto semplice, un secolo di distanza. La bambina e il gatto compaiono in un filmato autentico; il fermo a colori è una ricostruzione AI. #StoriaRivive #Lumiere #Cinema",
      "TIKTOK":"Una bambina e il suo gatto, filmati nel 1900. Guarda come la pellicola si ferma sullo stesso fotogramma e diventa una ricostruzione fotografica moderna. Originale storico + AI dichiarata. #LaStoriaRivive",
      "YOUTUBE":"LA PETITE FILLE ET SON CHAT · 1900 | Lumière original film + source-locked photographic AI.\nSource: "+PAGE+"\nOriginal historic film remains in motion before and after the freeze. New color portrait is AI interpretation, not a genuine color image from 1900. Review only."
    }
    for site,words in captions.items():
        (OUT/f"POST_{site}.txt").write_text(words+"\n",encoding="utf8")
    (OUT/"README_REVIEW_ONLY.txt").write_text(
      "NEW HISTORICAL EPISODE, TECHNICAL REVIEW ONLY. Not artistically approved. No site/social publication.\n"
      "True historical B/W moving film -> precise still -> FREE generated I2I image -> original historic motion with neural chroma (NOT generative moving I2V).\n"
      "One genuine girl's face and one cat only; use source vs photo files to reject any defects. No Vidu requests or credits.\n"
      "Film source: "+PAGE+"\nCommons Public Domain Mark; verify 2015 scan/restoration territorial reuse before commercial publication.\n"
      "1080x1920 output presentation is not 4K or original native resolution.\n",encoding="utf8")
    original_png=OUT/"ANCHOR_REAL_ORIGINAL_BW.png"
    pic_png=OUT/"GENERATIVE_PHOTO_REAL_CANDIDATE.png"
    comparison=OUT/"GIRL_CAT_1900_EXACT_FRAME_BEFORE_AFTER.png"
    from PIL import Image,ImageDraw
    before=Image.open(original_png).convert("RGB")
    after=Image.open(pic_png).convert("RGB")
    montage=Image.new("RGB",(before.width*2,before.height+50),(18,19,22))
    montage.paste(before,(0,50));montage.paste(after,(before.width,50))
    d=ImageDraw.Draw(montage);d.text((15,15),"SOURCE: ORIGINAL BLACK-WHITE EXACT FRAME",fill="white")
    d.text((before.width+15,15),"REAL FREE I2I: ART REVIEW PENDING",fill="white")
    montage.save(comparison)
    base_metadata=json.loads((OUT/"VISUAL_REPORT.json").read_text())
    base_metadata.update({"title":TITLE,"source_page":PAGE,
       "source_original_sha256":m.sha(m.SOURCE),"freeze_original_index":m.ANCHOR,
       "freeze_original_time_s":m.START+m.ANCHOR/m.FPS,
       "source_frame_sha256":m.sha(original_png),"i2i_photo_sha256":m.sha(pic_png),
       "new_historical_footage":True,"artistic_approval":False,
       "human_face_anatomy_verified":False,
       "year_and_director_italy_copyright":"RECHECK_BEFORE_COMMERCIAL_PUBLISH",
       "website_or_social_publication":False,"paid_api_posts":0,"vidu_generated":False})
    m.write("VISUAL_REPORT.json",base_metadata)
    include=[m.MOVIE.name,"SOCIAL_COVER.jpg","ORIGINAL_VS_PHOTO_VISUAL_QA.jpg",
       "GIRL_CAT_1900_EXACT_FRAME_BEFORE_AFTER.png","VISUAL_REPORT.json",
       "PHOTO_QA.json","RIGHTS.json","README_REVIEW_ONLY.txt",
       "POST_FACEBOOK.txt","POST_INSTAGRAM.txt","POST_TIKTOK.txt",
       "POST_YOUTUBE.txt","GENERATIVE_PHOTO_REAL_CANDIDATE.png",
       "ANCHOR_REAL_ORIGINAL_BW.png"]
    with zipfile.ZipFile(m.ZIP,"w",zipfile.ZIP_DEFLATED,compresslevel=4) as z:
        for file in include:z.write(OUT/file,arcname=file)
    with zipfile.ZipFile(m.ZIP) as z:
        if z.testzip():raise RuntimeError("ZIP_CRC_FAIL")
    for stream,expected in [("v","h264"),("a","aac")]:
        actual=m.run(["ffprobe","-v","error","-select_streams",stream,"-show_entries","stream=codec_name",
            "-of","default=nw=1:nk=1",str(m.MOVIE)]).strip()
        if actual!=expected:raise RuntimeError("CODEC_FAIL_"+stream+"_"+actual)
    m.run(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(m.MOVIE),"-f","null","-"],190)
    m.write("DELIVERY.json",{"video_sha256":m.sha(m.MOVIE),"zip_sha256":m.sha(m.ZIP),
        "zip_crc_pass":True,"full_video_decode_pass":True,"artistic_review":"PENDING",
        "real_new_I2I":True,"source_original_sha256":m.sha(m.SOURCE),"no_cost":True})
    print("NEW_GIRL_CAT_1900_REAL_I2I_MP4_REVIEW_CREATED",m.MOVIE.name,
       "VIDEO_SHA",m.sha(m.MOVIE),"ZIP_SHA",m.sha(m.ZIP),flush=True)
except Exception as ex:
    m.write("FAILURE.json",{"error":type(ex).__name__+": "+str(ex)[:800],
        "no_paid_api_calls":True,"artistic_approval":False,"no_publication":True})
    print("FAIL_CLOSED_NO_FAKE_FINAL",repr(ex),flush=True)
    raise
