#!/usr/bin/env python3
"""La Storia Rivive / Venice 1896 visual trial. Source locked; no publication."""
import argparse, hashlib, json, pathlib, subprocess, sys, zipfile
import cv2, numpy as np
from PIL import Image, ImageDraw

ROOT=pathlib.Path("output/storia_venice_1896_v2")
SOURCE=ROOT/"SOURCE_1896.webm"
EXPECTED_SHA="002b6bb6120cdd53f8a943e9ccb9af0195de883658b22de9a4628cec5cee70f2"
FPS=24; W=540; H=960; ANCHOR=22.0
def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1<<20),b""):h.update(block)
    return h.hexdigest()
def dump(path,data):path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n")
def crop(im):
    h,w=im.shape[:2];cw=round(h*9/16)
    x=min(max(0,round(w*.50-cw*.50)),w-cw)
    return cv2.resize(im[:,x:x+cw],(W,H),interpolation=cv2.INTER_AREA)
def tint(frame):
    """Natural muted chroma from original BW; guidance only, NOT AI regeneration."""
    g=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    lab=cv2.cvtColor(cv2.cvtColor(g,cv2.COLOR_GRAY2BGR),cv2.COLOR_BGR2LAB)
    y,x=np.mgrid[0:H,0:W].astype("float32")
    def ab(rgb):
        p=np.array([[[rgb[2],rgb[1],rgb[0]]]],dtype=np.uint8)
        return cv2.cvtColor(p,cv2.COLOR_BGR2LAB)[0,0,1:].astype("float32")
    stone=ab((175,161,148));water=ab((96,116,112));foliage=ab((72,89,62));pale=ab((196,188,174))
    w=np.clip((y-H*.795)/(H*.06),0,1);w=w*w*(3-2*w)
    fence=np.clip((y-H*.645)/(H*.075),0,1)*np.clip((H*.838-y)/(H*.075),0,1)
    dark=np.clip((138-g.astype("float32"))/110,0,1)
    middle=np.exp(-.5*((x-W*.24)/(W*.17))**4)*np.exp(-.5*((y-H*.48)/(H*.235))**4)
    green=np.clip(dark*middle*.8,0,.7)
    color=np.ones((H,W,2),np.float32)*stone
    for mask,tone in [(fence*.30,pale),(green,foliage),(w*.86,water)]:
        color=color*(1-mask[:,:,None])+tone*mask[:,:,None]
    lab[:,:,1:]=np.clip(color,0,255).astype("uint8")
    return cv2.cvtColor(lab,cv2.COLOR_LAB2BGR)
def prepare():
    ROOT.mkdir(parents=True,exist_ok=True)
    assert SOURCE.is_file(),"NO_AUTHENTIC_SOURCE"
    assert sha(SOURCE)==EXPECTED_SHA,"WRONG_SOURCE_SHA"
    cap=cv2.VideoCapture(str(SOURCE));assert cap.isOpened()
    sw,sh=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps=cap.get(cv2.CAP_PROP_FPS);duration=cap.get(cv2.CAP_PROP_FRAME_COUNT)/fps
    assert (sw,sh)==(1364,1022) and duration>49,(sw,sh,duration)
    cap.set(cv2.CAP_PROP_POS_MSEC,ANCHOR*1000);ok,original=cap.read();cap.release()
    assert ok
    original=crop(original)
    cv2.imwrite(str(ROOT/"ORIGINAL_BW_22S.png"),original)
    cv2.imwrite(str(ROOT/"COLORMAPPED_GUIDANCE_SAME_FRAME.png"),tint(original))
    dump(ROOT/"SOURCE_REPORT.json",{"source":"https://commons.wikimedia.org/wiki/File:Venise_Panorama_du_Grand_Canal_1896.webm","author":"Alexandre Promio (d. 1926)","year":1896,"source_sha256":sha(SOURCE),"size":(sw,sh),"duration_s":duration,"source_frame_time_s":ANCHOR,"color_guidance_is_not_AI":True,"italy_rights":"PRELIMINARY_PUBLIC_DOMAIN_NEEDS_FINAL_REVIEW","usa_rights":"PRE_1931_PRELIMINARY_PD","no_paid_calls":True,"no_publication":True})
    print("SOURCE_LOCKED_AND_GUIDANCE_READY",flush=True)
def finalize():
    rep={"project":"LA_STORIA_RIVIVE_ONLY","episode":"VENICE_1896","stage":"COLOR_GUIDED_FREE_I2I_NEW_TRIAL","paid_calls":0,"new_vidu_clips":0,"published_site":False,"published_social":False,"human_anatomy_visual_review":"PENDING","rights_final":"PENDING","editorial_approval":False}
    trial=ROOT/"I2I_TRIAL.json"
    if trial.exists():rep["free_provider_trial"]=json.loads(trial.read_text())
    photo=ROOT/"PHOTO_I2I_NEW.png"
    if not photo.is_file():
        rep["status"]="FREE_PROVIDER_UNAVAILABLE_NO_EPISODE"
        dump(ROOT/"VISUAL_REPORT.json",rep);return
    b=cv2.imread(str(ROOT/"ORIGINAL_BW_22S.png"))
    a=cv2.imread(str(ROOT/"COLORMAPPED_GUIDANCE_SAME_FRAME.png"))
    im=cv2.imread(str(photo));assert im is not None
    pic=cv2.resize(im,(W,H))
    def small_gray(arr):return cv2.GaussianBlur(cv2.resize(cv2.cvtColor(arr,cv2.COLOR_BGR2GRAY),(120,213)).astype("float32"),(7,7),0)
    corr=float(np.corrcoef(small_gray(b).ravel(),small_gray(pic).ravel())[0,1])
    sat=float(cv2.cvtColor(pic,cv2.COLOR_BGR2HSV)[:,:,1].mean())
    olddetail=float(cv2.Laplacian(cv2.cvtColor(b,cv2.COLOR_BGR2GRAY),cv2.CV_32F).var())
    detail=float(cv2.Laplacian(cv2.cvtColor(pic,cv2.COLOR_BGR2GRAY),cv2.CV_32F).var())
    rep.update({"actual_new_i2i":True,"candidate_sha256":sha(photo),"structure_correlation":round(corr,4),"saturation":round(sat,2),"source_detail":round(olddetail,2),"restoration_detail":round(detail,2)})
    if not(corr>=.89 and 17<sat<115 and detail>.75*olddetail):
        rep["status"]="PHOTO_TECH_GATE_FAIL_NOT_RENDERED";dump(ROOT/"VISUAL_REPORT.json",rep)
        print("PHOTO_TECH_GATE_FAIL",rep,flush=True);return
    board=Image.new("RGB",(3*W,H+55),(12,14,18));dr=ImageDraw.Draw(board)
    for i,(arr,label) in enumerate([(b,"AUTHENTIC 1896 BW FRAME"),(a,"COLOR GUIDE, NOT AI"),(pic,"NEW FREE I2I, HUMAN REVIEW")]):
        board.paste(Image.fromarray(cv2.cvtColor(arr,cv2.COLOR_BGR2RGB)),(i*W,55))
        dr.text((i*W+9,18),label,fill="white")
    board.save(ROOT/"VISUAL_CLOSE_QA.jpg",quality=91)
    # True archival film movement on BOTH sides of reveal, no slideshow/pan of still.
    cap=cv2.VideoCapture(str(SOURCE));assert cap.isOpened()
    raw=ROOT/"REVIEW_RAW.mp4";vw=cv2.VideoWriter(str(raw),cv2.VideoWriter_fourcc(*"mp4v"),FPS,(W,H))
    assert vw.isOpened()
    cap.set(cv2.CAP_PROP_POS_MSEC,17000)
    for _ in range(5*FPS):
        ok,f=cap.read();assert ok
        m=crop(f);vw.write(cv2.cvtColor(cv2.cvtColor(m,cv2.COLOR_BGR2GRAY),cv2.COLOR_GRAY2BGR))
    for _ in range(10):vw.write(b)
    for _ in range(34):vw.write(pic)
    cap.set(cv2.CAP_PROP_POS_MSEC,22000)
    for _ in range(15*FPS):
        ok,f=cap.read();assert ok
        vw.write(tint(crop(f)))
    cap.release();vw.release()
    out=ROOT/"VENICE_1896_V2_REAL_MOVEMENT_REVIEW.mp4"
    subprocess.run(["ffmpeg","-nostdin","-y","-v","error","-i",str(raw),"-f","lavfi","-i","anullsrc=channel_layout=stereo:sample_rate=44100","-shortest","-vf","scale=1080:1920:flags=lanczos","-c:v","libx264","-preset","fast","-crf","20","-pix_fmt","yuv420p","-c:a","aac","-b:a","96k","-movflags","+faststart",str(out)],check=True)
    subprocess.run(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(out),"-f","null","-"],check=True,timeout=250)
    j=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries","stream=codec_name,codec_type,width,height","-show_entries","format=duration","-of","json",str(out)],text=True))
    v=next(x for x in j["streams"] if x["codec_type"]=="video");audio=next(x for x in j["streams"] if x["codec_type"]=="audio")
    assert v["codec_name"]=="h264" and v["width"]==1080 and v["height"]==1920 and audio["codec_name"]=="aac"
    cover=Image.fromarray(cv2.cvtColor(pic,cv2.COLOR_BGR2RGB)).resize((1080,1920))
    d=ImageDraw.Draw(cover);d.rectangle((0,1770,1080,1920),fill=(7,10,13))
    d.text((55,1800),"VENICE  /  1896",fill="white")
    d.text((55,1850),"Authentic motion + experimental AI restoration",fill=(190,190,190))
    cover.save(ROOT/"VENICE_1896_V2_COVER.jpg",quality=92)
    drafts={"facebook":"VENICE · 1896. Authentic moving historical footage and a new source-locked photographic color restoration. Review preview only.","instagram":"Venice, 1896: a moving glimpse of the Grand Canal comes alive in an experimental restoration. Preview only.","tiktok":"VENICE 1896. Real historical motion, a restored frame, then moving color. Visual test.","youtube":"Venice 1896 — archival film and AI photographic restoration trial. Source: Alexandre Promio. Unapproved visual review."}
    dump(ROOT/"SOCIAL_DRAFTS.json",drafts)
    rep.update({"status":"REAL_PREVIEW_REQUIRES_HUMAN_ART_REVIEW","preview_sha256":sha(out),"duration":float(j["format"]["duration"]),"resolution":"1080x1920_upscaled_not_native_4K","post_photo_motion":"AUTHENTIC_HISTORICAL_FILM_WITH_GUIDED_CHROMA_NOT_NEW_I2V","delivery":"review_only_not_final"})
    dump(ROOT/"VISUAL_REPORT.json",rep)
    z=ROOT/"VENICE_1896_V2_REVIEW_VIDEO_COVER_SOCIAL.zip"
    with zipfile.ZipFile(z,"w",zipfile.ZIP_DEFLATED,compresslevel=6) as f:
        for name in ["VENICE_1896_V2_REAL_MOVEMENT_REVIEW.mp4","VENICE_1896_V2_COVER.jpg","VISUAL_CLOSE_QA.jpg","VISUAL_REPORT.json","SOURCE_REPORT.json","SOCIAL_DRAFTS.json"]:
            f.write(ROOT/name,name)
    with zipfile.ZipFile(z) as f:assert f.testzip() is None
    print("VIDEO_PREVIEW_TECH_PASS_ARTISTIC_PENDING",sha(out),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("stage",choices=["prepare","finalize"])
    args=p.parse_args()
    (prepare() if args.stage=="prepare" else finalize())
