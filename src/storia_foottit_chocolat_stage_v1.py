#!/usr/bin/env python3
"""La Storia Rivive ONLY | new source-locked historic stage acrobat film visual trial."""
from __future__ import annotations
import hashlib, json, pathlib, subprocess, sys, zipfile
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT=pathlib.Path("output/storia_foottit_chocolat_v1")
SOURCE=OUT/"ORIGINAL_FOOTTIT_CHOCOLAT.webm"
SHA1="f3c54778123a4a44a9fecab3ade09ed27e3350a8"
SRC_URL="https://commons.wikimedia.org/wiki/File:Chocolat_et_Foottit_-_Chaise_en_bascule.webm"
YEAR="1897–1900"
AN=30.0; START=27.75; END=42.0
FPS=24; W=540; H=960; CROP_X=265; CROP_W=405
def hashfile(p,alg="sha256"):
    h=hashlib.new(alg)
    with open(p,"rb") as f:
        for part in iter(lambda:f.read(1024*1024),b""):h.update(part)
    return h.hexdigest()
def save_json(p,data):
    pathlib.Path(p).write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n")
def frame_crop(frame):
    assert frame is not None and frame.shape[1]>=CROP_X+CROP_W
    z=frame[:,CROP_X:CROP_X+CROP_W]
    return cv2.resize(z,(W,H),interpolation=cv2.INTER_CUBIC)
def clean_motion(frame):
    g=cv2.cvtColor(frame_crop(frame),cv2.COLOR_BGR2GRAY)
    g=cv2.fastNlMeansDenoising(g,h=3,templateWindowSize=7,searchWindowSize=17)
    blur=cv2.GaussianBlur(g,(0,0),.8)
    g=cv2.addWeighted(g,1.15,blur,-.15,0)
    return cv2.cvtColor(g,cv2.COLOR_GRAY2BGR)
def natural_stage_coloration(frame):
    """No extra performers or synthetic movement. Source pixel geometry is preserved."""
    b=clean_motion(frame)
    g=cv2.cvtColor(b,cv2.COLOR_BGR2GRAY)
    lab=cv2.cvtColor(b,cv2.COLOR_BGR2LAB)
    y,x=np.mgrid[0:H,0:W]
    # Stage curtain neutral warm olive-brown; floor warm dust; one cream costume,
    # dark jacket and dark boots. All colors are historically interpreted, not facts.
    aa=np.full((H,W),133.0,np.float32)
    bb=np.full((H,W),143.0,np.float32)
    floor=np.clip((y/H-.78)/.06,0,1)
    aa=aa*(1-floor)+131*floor
    bb=bb*(1-floor)+137*floor
    costume_region=(x/W>.075)&(x/W<.90)&(y/H>.27)
    cream=costume_region&(g>164)
    aa[cream]=129;bb[cream]=137
    dark=costume_region&(g<92)
    aa[dark]=132;bb[dark]=137
    # Subtle skin warmth where source greyscale face is visible (not shape alteration).
    face=(x/W>.42)&(x/W<.87)&(y/H>.20)&(y/H<.44)&(g>105)
    aa[face]=np.maximum(aa[face],143)
    bb[face]=np.maximum(bb[face],145)
    lab[:,:,1]=np.clip(aa,0,255).astype("uint8")
    lab[:,:,2]=np.clip(bb,0,255).astype("uint8")
    return cv2.cvtColor(lab,cv2.COLOR_LAB2BGR)
def fetch(t):
    cap=cv2.VideoCapture(str(SOURCE))
    assert cap.isOpened()
    cap.set(cv2.CAP_PROP_POS_MSEC,t*1000)
    ok,b=cap.read()
    cap.release()
    assert ok and b is not None,("MISSING_SOURCE_FRAME",t)
    return b
def prepare():
    OUT.mkdir(parents=True,exist_ok=True)
    assert SOURCE.is_file(),"AUTHENTIC_SOURCE_FILE_MISSING"
    assert hashfile(SOURCE,"sha1")==SHA1,"SOURCE_SHA1_MISMATCH"
    cap=cv2.VideoCapture(str(SOURCE))
    assert cap.isOpened()
    fw=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    fh=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frames=cap.get(cv2.CAP_PROP_FRAME_COUNT)
    fps=cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    assert fw==1280 and fh==720 and 45<frames/fps<47, (fw,fh,frames/fps)
    original=frame_crop(fetch(AN))
    guided=natural_stage_coloration(fetch(AN))
    cv2.imwrite(str(OUT/"AUTHENTIC_FRAME_30S_BW.png"),original)
    cv2.imwrite(str(OUT/"NEUTRAL_COLOR_GUIDE_30S.png"),guided)
    report={"film":"Foottit et Chocolat, III. Chaise en bascule","date_range":YEAR,
      "stage":"Nouveau Cirque Paris","catalogue":"https://catalogue-lumiere.com/foottit-et-chocolat-iii-chaise-en-bascule/",
      "source_url":SRC_URL,"source_sha1":SHA1,"source_sha256":hashfile(SOURCE),
      "frame_t_seconds":AN,"frame_crop_original_pixels":[CROP_X,0,CROP_W,720],
      "true_source_motion":True,"full_original_resolution":[1280,720],
      "public_domain_source_commons":True,"italy_usa_rights_final":"PENDING",
      "free_api_calls_planned":1,"paid_calls":0,"website_social_publication":False}
    save_json(OUT/"SOURCE_REPORT.json",report)
    print("VERIFIED_NEW_AUTHENTIC_CLOWN_FILM_FRAME_30S",report["source_sha256"],flush=True)
def finalize():
    rep={"project":"LA_STORIA_RIVIVE_ONLY","episode":"FOOTTIT_CHOCOLAT_CHAIR",
      "stage":"REAL_MOVING_SOURCE_BW_FREEZE_GEN_PHOTO_POST_COLOR_MOVEMENT",
      "paid_calls":0,"vidu_generated":False,"site_published":False,"social_published":False,
      "artistic_approval":False,"full_video_artistic_review":"PENDING",
      "rights_final_italy":"PENDING"}
    p=OUT/"I2I_TRIAL.json"
    if p.exists():rep["provider_trial"]=json.loads(p.read_text())
    photo=OUT/"NEW_PHOTO_I2I.png"
    if not photo.is_file():
        rep["status"]="NO_FREE_PHOTO_NO_MP4";save_json(OUT/"VISUAL_REPORT.json",rep);return
    bw=cv2.imread(str(OUT/"AUTHENTIC_FRAME_30S_BW.png"))
    guided=cv2.imread(str(OUT/"NEUTRAL_COLOR_GUIDE_30S.png"))
    photo_im=cv2.imread(str(photo))
    assert photo_im is not None
    new=cv2.resize(photo_im,(W,H))
    def structure(x):
        gray=cv2.cvtColor(x,cv2.COLOR_BGR2GRAY)
        return cv2.GaussianBlur(cv2.resize(gray,(90,160)).astype("float32"),(5,5),0).ravel()
    sim=float(np.corrcoef(structure(bw),structure(new))[0,1])
    sat=float(cv2.cvtColor(new,cv2.COLOR_BGR2HSV)[:,:,1].mean())
    detail=float(cv2.Laplacian(cv2.cvtColor(new,cv2.COLOR_BGR2GRAY),cv2.CV_32F).var())
    base_detail=float(cv2.Laplacian(cv2.cvtColor(bw,cv2.COLOR_BGR2GRAY),cv2.CV_32F).var())
    rep.update({"photo_sha256":hashfile(photo),"corr":round(sim,4),"mean_saturation":round(sat,2),
       "photo_laplacian":round(detail,2),"original_laplacian":round(base_detail,2),
       "actual_new_free_I2I":True})
    if not(sim>.79 and sat>20 and detail>base_detail*.70):
        rep["status"]="PHOTO_TECH_GATE_FAIL_NO_MP4"
        save_json(OUT/"VISUAL_REPORT.json",rep)
        print("PHOTO_TECH_GATE_FAIL",rep,flush=True);return
    # True source I2I pair for human judgment, no simulated BEFORE.
    board=Image.new("RGB",(W*3,H+49),(18,18,20));d=ImageDraw.Draw(board)
    for i,(frm,lab) in enumerate([(bw,"AUTHENTIC FILM 30.0S"),(guided,"COLOR GUIDE ONLY"),(new,"NEW FREE PHOTOGRAPHIC I2I")]):
        board.paste(Image.fromarray(cv2.cvtColor(frm,cv2.COLOR_BGR2RGB)),(i*W,49))
        d.text((i*W+12,17),lab,fill="white")
    board.save(OUT/"REAL_SOURCE_I2I_COMPARISON.jpg",quality=94)
    cap=cv2.VideoCapture(str(SOURCE));assert cap.isOpened()
    cap.set(cv2.CAP_PROP_POS_MSEC,START*1000)
    input_fps=cap.get(cv2.CAP_PROP_FPS)
    raw=OUT/"TRUE_MOVEMENT_TEMP.mp4"
    writer=cv2.VideoWriter(str(raw),cv2.VideoWriter_fourcc(*"mp4v"),FPS,(W,H))
    assert writer.isOpened()
    def get_at(t):
        cap.set(cv2.CAP_PROP_POS_MSEC,t*1000)
        ok,frm=cap.read()
        assert ok,(t,"SOURCE_UNREADABLE")
        return frm
    n_bw=round((AN-START)*FPS)
    for i in range(n_bw):
        t=START+i/FPS
        writer.write(clean_motion(get_at(t)))
    for _ in range(5):
        writer.write(cv2.cvtColor(cv2.cvtColor(bw,cv2.COLOR_BGR2GRAY),cv2.COLOR_GRAY2BGR))
    for _ in range(32):
        writer.write(new)
    n_color=round((END-AN)*FPS)
    for i in range(n_color):
        t=AN+i/FPS
        writer.write(natural_stage_coloration(get_at(t)))
    writer.release();cap.release()
    mp4=OUT/"FOOTTIT_CHOCOLAT_1897_1900_REAL_MOTION_V1_REVIEW.mp4"
    subprocess.run(["ffmpeg","-nostdin","-y","-v","error","-i",str(raw),
       "-f","lavfi","-i","anullsrc=channel_layout=stereo:sample_rate=44100",
       "-shortest","-vf","scale=1080:1920:flags=lanczos","-c:v","libx264","-preset","medium",
       "-crf","20","-pix_fmt","yuv420p","-c:a","aac","-b:a","96k","-movflags","+faststart",str(mp4)],check=True,timeout=400)
    subprocess.run(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(mp4),"-f","null","-"],check=True,timeout=300)
    meta=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries","stream=codec_name,codec_type,width,height",
        "-show_entries","format=duration","-of","json",str(mp4)],text=True))
    v=next(s for s in meta["streams"] if s["codec_type"]=="video")
    a=next(s for s in meta["streams"] if s["codec_type"]=="audio")
    assert v["codec_name"]=="h264" and a["codec_name"]=="aac"
    assert (v["width"],v["height"])==(1080,1920)
    total=float(meta["format"]["duration"])
    assert 14<total<25,total
    # Authentic motion at the end, no still-frame pan.
    rep.update({"status":"TRUE_FILM_MOVING_VISUAL_REVIEW_ARTISTIC_PENDING",
      "mp4_sha256":hashfile(mp4),"mp4_duration_seconds":round(total,3),
      "mp4_1080x1920_display_not_native_4k":True,"post_reveal_real_source_moving":True,
      "post_reveal_color_method":"GUIDED_CONSISTENT_NEUTRAL_CHROMA_NOT_GENERATIVE_I2V",
      "after_photo_motion_seconds":round(END-AN,2)})
    # Document distinctly different real historical frames across source and output.
    vc=cv2.VideoCapture(str(mp4));checktimes=[0.5,2.4,3.4,5.5,8.0,10.0,12.0,14.5]
    card=Image.new("RGB",(4*270,2*520),(13,15,19));dr=ImageDraw.Draw(card)
    for i,t in enumerate(checktimes):
        vc.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,fr=vc.read()
        if not ok:continue
        im=Image.fromarray(cv2.cvtColor(fr,cv2.COLOR_BGR2RGB));im.thumbnail((264,469))
        x=(i%4)*270+3;y=(i//4)*520+29
        card.paste(im,(x,y));dr.text((x,y-22),f"TRUE VIDEO t={t:.1f}s",fill="white")
    vc.release()
    card.save(OUT/"REAL_MOTION_TIMELINE.jpg",quality=90)
    cover=Image.fromarray(cv2.cvtColor(new,cv2.COLOR_BGR2RGB)).resize((1080,1920))
    d=ImageDraw.Draw(cover)
    d.rectangle((0,1720,1080,1920),fill=(14,15,17))
    d.text((55,1765),"FOOTTIT & CHOCOLAT",fill="white")
    d.text((55,1830),"PARIS • 1897–1900",fill=(212,208,194))
    cover.save(OUT/"FOOTTIT_CHOCOLAT_COVER.jpg",quality=94)
    social={
      "facebook":"Paris, 1897–1900. Two stage clowns, one astonishing acrobatic routine. Authentic motion picture footage, with an experimental photographic restoration. Visual preview, not an approved release.",
      "instagram":"A circus performance filmed over 125 years ago. Foottit & Chocolat — Paris, 1897–1900. Original moving film meets a photographic restoration experiment. #SilentFilm #FilmHistory",
      "tiktok":"This acrobatic stunt was REALLY FILMED more than 125 years ago. Watch it move again in color. Foottit & Chocolat, Paris.",
      "youtube":"Foottit & Chocolat: The Chair Acrobatics | Paris, 1897–1900. Genuine Lumière-era moving footage, a source-locked photographic restoration attempt and original moving film after the color reveal. Preview pending artistic review."}
    save_json(OUT/"SOCIAL_DRAFTS.json",social)
    save_json(OUT/"VISUAL_REPORT.json",rep)
    z=OUT/"FOOTTIT_CHOCOLAT_V1_VIDEO_COVER_SOCIAL_REVIEW.zip"
    names=[mp4.name,"FOOTTIT_CHOCOLAT_COVER.jpg","SOCIAL_DRAFTS.json","REAL_SOURCE_I2I_COMPARISON.jpg",
        "REAL_MOTION_TIMELINE.jpg","VISUAL_REPORT.json","SOURCE_REPORT.json"]
    with zipfile.ZipFile(z,"w",zipfile.ZIP_DEFLATED,compresslevel=5) as dst:
        for n in names: dst.write(OUT/n,n)
    with zipfile.ZipFile(z) as src:assert src.testzip() is None
    print("REAL_VIDEO_PREVIEW_DONE_SHA",hashfile(mp4),"ZIP_CRC_PASS","ARTISTIC_PENDING",flush=True)
if __name__=="__main__":
    if len(sys.argv)!=2 or sys.argv[1] not in ("prepare","finalize"):
        raise SystemExit("usage: ... prepare|finalize")
    (prepare if sys.argv[1]=="prepare" else finalize)()
