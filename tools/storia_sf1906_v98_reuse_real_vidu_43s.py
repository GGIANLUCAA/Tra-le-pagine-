#!/usr/bin/env python3
"""La Storia Rivive V98: four ACTUAL V97 Finegrain I2I photo restorations +
one REAL already-paid V86 Vidu clip, using its exact original 43s Market Street film.
No Vidu POST, no additional credits, no inventing source photos, no stale 411s splice.
Reviewer-endorsed V97 first four scenes are retained frame-for-frame.
V91/V94/V96 artistic FINAL remains pending a genuine complete visual review.
"""
from __future__ import annotations
import hashlib, json, pathlib, subprocess, sys, wave, zipfile
import cv2
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=pathlib.Path("output/sf1906_v98_correct_4photo_1vidu")
P=R/"SF1906_V97_FOUR_RESTORATIONS_QA_PREVIEW_NOT_FINAL.mp4"
ARCHIVE=R/"ORIGINAL_ARCHIVE.webm"
FILM_QA=R/"V97_PREVIEW_STATUS.json"
PHOTO_QA=R/"PHOTO_QA.json"
VIDU=R/"VIDU_SF1906_05_COLOR_MOTION.mp4"
VIDU_QA=R/"QA_PUBLIC_V86.json"
RESULT=R/"LA_STORIA_RIVIVE_SF1906_V98_FOUR_REAL_I2I_ONE_REAL_VIDU.mp4"
COVER=R/"COPERTINA_V98.jpg"
CONTACT=R/"V98_FIVE_SCENES_REAL_ORIGINAL_RESTORED.jpg"
OUTPUT_ZIP=R/"SAN_FRANCISCO_1906_V98_ANDROID_KIT.zip"
FPS=30
WIDTH=720
HEIGHT=1280
VIDU_SOURCE_SECOND=43.0
VIDU_SOURCE_CROP_LEFT=600  # original source 1440×1072, real crop from prior V86 generator
KNOWN_V97_MASTER_SHA="84b60dcb974c405e6e3f0d99e15db8e1647940b9aa2dfeac8ae8a3a6eb472ef5"
KNOWN_V86_VIDU_SHA="3b383a5f75021b8dd872eff61cb1514cd625a2c373109fa866013c697dac28bd"
EXPECTED_V86_SOURCE_SHA="c8b30802c0fbeb5f9ec3dc9af3e4f71ef627a863d4abba5550b63998cb46725a"
# Original four frames and preserves exact V97 pacing, never edit or repeat them.
FOUR_SOURCE_TIMES=[18.0,74.0,161.0,312.0]
FOUR_ORIGINAL_MOTIONS=[1.35,1.3,1.4,1.35]

def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1048576),b""):
            h.update(b)
    return h.hexdigest()

def run(cmd,timeout=150):
    p=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout)
    if p.returncode:
        raise RuntimeError("FFMPEG_OPERATION_FAILED "+str(cmd[:5])+" "+p.stderr[-900:])
    return p.stdout

def photo_color_metrics(frames):
    x=[cv2.imread(str(z)) for z in frames]
    if not all(v is not None and v.shape[:2]==(HEIGHT,WIDTH) for v in x):
        raise RuntimeError("V97_RESTORED_PHOTOS_UNAVAILABLE_OR_WRONG_RESOLUTION")
    stats=[]
    for f in x:
        hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
        stats.append({"saturation_median":float(np.median(hsv[:,:,1])),"saturation_mean":float(np.mean(hsv[:,:,1])),
                      "brightness_median":float(np.median(hsv[:,:,2]))})
    return stats

def corr_gray(a,b):
    def small(frame):
        x=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        x=cv2.resize(x,(120,212))
        return cv2.GaussianBlur(x,(7,7),0).astype("float32").ravel()
    x,y=small(a),small(b)
    return float(np.corrcoef(x,y)[0,1]),float(np.mean(np.abs(x-y)))

def describe_clip(cap):
    width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps=float(cap.get(cv2.CAP_PROP_FPS))
    count=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    return width,height,fps,count

def prepare():
    mandatory=[P,ARCHIVE,FILM_QA,PHOTO_QA,VIDU,VIDU_QA,
               *[R/f"PHOTO_AI_{k:02}.png" for k in range(1,5)]]
    for path in mandatory:
        if not path.is_file() or path.stat().st_size<50:
            raise RuntimeError("MISSING_VERIFIED_INPUT_"+str(path))
    if sha(P)!=KNOWN_V97_MASTER_SHA:raise RuntimeError("USER_APPROVED_V97_MP4_SHA_MISMATCH")
    if sha(VIDU)!=KNOWN_V86_VIDU_SHA:raise RuntimeError("EXISTING_REAL_VIDU_MP4_SHA_MISMATCH")
    v97=json.loads(FILM_QA.read_text())
    v86=json.loads(VIDU_QA.read_text())
    pq=json.loads(PHOTO_QA.read_text())
    if sha(ARCHIVE)!=v97["source"]["original_sha256"]:
        raise RuntimeError("ARCHIVAL_FILM_SHA_MISMATCH")
    if len(pq)!=4 or len(v97["photos"])!=4:raise RuntimeError("NOT_FOUR_ACTUAL_FINEGRAIN_PHOTOS")
    for j,p in enumerate(pq):
        if p["source_time"]!=FOUR_SOURCE_TIMES[j] or p["model"]!="DDColor+free Finegrain image enhancer":
            raise RuntimeError("MISORDERED_OR_NOT_TRUE_I2I_PHOTOGRAPH_"+str(j))
        if p["photo_sha256"]!=sha(R/p["photo_file"]):
            raise RuntimeError("FAILED_PHOTOGRAPH_INTEGRITY_"+str(j))
    if v86.get("vidu_5th_scene_source_frame_time")!=VIDU_SOURCE_SECOND or v86.get("vidu_count")!=1:
        raise RuntimeError("EXISTING_PAID_CLIP_HAS_DIFFERENT_HISTORICAL_SOURCE")
    if v86.get("vidu_moving_color_sha256")!=sha(VIDU):
        raise RuntimeError("EXISTING_VIDU_PAID_TASK_DOES_NOT_MATCH_VIDEO")
    source=cv2.VideoCapture(str(ARCHIVE))
    w,h,sfps,n=describe_clip(source)
    if (w,h)!=(1440,1072) or sfps<20 or n/sfps<450:
        raise RuntimeError("ARCHIVE_RESOLUTION_OR_FPS_NOT_AUTHENTIC_SOURCE")
    source.set(cv2.CAP_PROP_POS_MSEC,VIDU_SOURCE_SECOND*1000)
    ok,frame43=source.read()
    if not ok:raise RuntimeError("EXACT_HISTORICAL_43S_SOURCE_FRAME_MISSING")
    expected43=cv2.resize(frame43[:,VIDU_SOURCE_CROP_LEFT:VIDU_SOURCE_CROP_LEFT+603],(WIDTH,HEIGHT),interpolation=cv2.INTER_CUBIC)
    original_gray=cv2.cvtColor(cv2.cvtColor(expected43,cv2.COLOR_BGR2GRAY),cv2.COLOR_GRAY2BGR)
    clip=cv2.VideoCapture(str(VIDU))
    cw,ch,cfps,cn=describe_clip(clip)
    if (cw,ch)!=(WIDTH,HEIGHT) or not 23<=cfps<=60 or not 4.7<=cn/cfps<=5.5:
        raise RuntimeError("REUSED_VIDU_MOVING_VIDEO_FORMAT_WRONG")
    ok,f0=clip.read()
    if not ok:raise RuntimeError("VIDU_FIRST_FRAME_NOT_DECODABLE")
    similarity,luma_delta=corr_gray(original_gray,f0)
    # This is a true source identity gate. Do not splice a different street shot.
    if similarity<.72 or luma_delta>57:
        raise RuntimeError("V98_HARD_STOP_DIFFERENT_SHOT_AT_MOVING_VIDEO_START corr="+str(round(similarity,3))+
                           " luma_delta="+str(round(luma_delta,1)))
    preview=cv2.VideoCapture(str(P))
    pw,ph,pfps,pn=describe_clip(preview)
    classic_frames=sum(round(t*FPS)+11+round(1.65*FPS) for t in FOUR_ORIGINAL_MOTIONS)
    if (pw,ph)!=(WIDTH,HEIGHT) or abs(pfps-FPS)>.01 or pn<classic_frames+24 or pn>classic_frames+100:
        raise RuntimeError("USER_APPROVED_FOUR_CLASSIC_CHAPTERS_DIFFERENT_THAN_EXPECTED")
    photo_stats=photo_color_metrics([R/f"PHOTO_AI_{i:02}.png" for i in range(1,5)])
    first4_ends=classic_frames/FPS
    print("V98_REAL_SAME_SOURCE_MOVING_VIDU_PRECHECK",
          "source_sha",sha(ARCHIVE),"same_as_v86_expected_source",sha(ARCHIVE)==EXPECTED_V86_SOURCE_SHA,
          "corr",round(similarity,3),"mean_luma_delta",round(luma_delta,2),
          "original_classic_duration",first4_ends,
          "reused_existing_task",v86.get("vidu_task_id"),flush=True)
    return source,clip,preview,original_gray,classic_frames,cfps,cn,photo_stats,v86,similarity,luma_delta

def prepare_audio(duration,scene_starts):
    # One original piece, continuous across all five chapters; never loop the short V97 audio at the seam.
    sr=32000
    t=np.arange(round(duration*sr),dtype=np.float32)/sr
    chords=[[130.81,164.81,196],[146.83,196,246.94],[164.81,207.65,261.63],
            [130.81,174.61,220],[146.83,220,293.66]]
    v=np.zeros_like(t)
    stops=scene_starts[1:]+[duration]
    for i,(start,end) in enumerate(zip(scene_starts,stops)):
        mask=(t>=start)&(t<end);u=t[mask]-start
        z=np.zeros_like(u)
        for k,f in enumerate(chords[i]):
            z+=.028*np.sin(2*np.pi*f*u+k*.23)*(.80+.20*np.cos(.27*u))
            z+=.003*np.sin(2*np.pi*2.02*f*u+k*.32)
        v[mask]=z
        if i>0:
            d=t-start;m=(d>=0)&(d<.5)
            v[m]+=.028*np.sin(2*np.pi*(96*d[m]+87*d[m]*d[m]))*np.exp(-9*d[m])
    env=np.minimum(1,t/.65)*np.minimum(1,np.maximum(0,(duration-t)/.75))
    v=np.tanh(v*2)*env
    path=R/"MUSICA_ORIGINALE_CONTINUA_V98.wav"
    stereo=np.column_stack((v,np.roll(v,int(sr*.012))*.94))
    with wave.open(str(path),"wb") as f:
        f.setnchannels(2);f.setsampwidth(2);f.setframerate(sr)
        f.writeframes((stereo*19000).astype("<i2").tobytes())
    return path

def make_contact():
    ims=[]
    for j in range(1,5):
        a=cv2.imread(str(R/f"FRAME_{j:02}_SOURCE.png"))
        b=cv2.imread(str(R/f"PHOTO_AI_{j:02}.png"))
        if a is None or b is None:raise RuntimeError("MISSING_SIDE_BY_SIDE_PHOTO")
        ims.append((a,b,"RESTORED "+str(j)))
    source=cv2.VideoCapture(str(ARCHIVE))
    source.set(cv2.CAP_PROP_POS_MSEC,VIDU_SOURCE_SECOND*1000)
    ok,src=source.read();source.release()
    vid=cv2.VideoCapture(str(VIDU))
    vid.set(cv2.CAP_PROP_POS_MSEC,2800);okv,moving=vid.read();vid.release()
    if not ok or not okv:raise RuntimeError("FIFTH_VISUAL_CONTACT_FRAME_MISSING")
    bw=cv2.resize(src[:,600:1203],(WIDTH,HEIGHT))
    ims.append((bw,moving,"REAL VIDU MOTION 5"))
    board=Image.new("RGB",(5*222,2*420+28),(13,16,21))
    d=ImageDraw.Draw(board)
    for j,(raw,color,name) in enumerate(ims):
        for row,f in enumerate((raw,color)):
            image=Image.fromarray(cv2.cvtColor(f,cv2.COLOR_BGR2RGB)).resize((213,387))
            board.paste(image,(222*j+4,26+420*row))
        d.text((222*j+6,6),name,fill=(240,229,206))
    board.save(CONTACT,quality=91)

def make_cover():
    im=Image.open(R/"PHOTO_AI_01.png").convert("RGB")
    draw=ImageDraw.Draw(im,"RGBA")
    try:
        serif=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",42)
        sans=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",24)
    except:serif=ImageFont.load_default();sans=serif
    # Thin unobtrusive top treatment (<7% opaque box height) with no gigantic Bombay title band.
    draw.rounded_rectangle((15,25,705,108),radius=10,fill=(5,8,13,90))
    draw.text((32,33),"SAN FRANCISCO  ·  1906",font=serif,fill=(246,235,215,255))
    draw.text((32,111),"THE CITY BEFORE THE EARTHQUAKE",font=sans,fill=(230,222,206,255))
    im.save(COVER,quality=94)

def create_posts():
    captions={
        "FACEBOOK":"SAN FRANCISCO · 1906. Quattro giorni prima del terremoto, Market Street era viva: carrozze, tram e persone attraversavano la città. Quattro momenti della pellicola diventano fotografie ricostruite a colori, mentre un quinto riprende vita in un breve video animato con AI. Film autentico dei Miles Brothers, ricostruzioni digitali dichiarate. Fonte: Library of Congress. #LaStoriaRivive",
        "INSTAGRAM":"SAN FRANCISCO · 1906. A few days before the earthquake. 🎞️ Four original moving shots freeze into carefully restored color photographs. One last shot begins on the real archival film and continues in AI-animated color. Colors and animation are interpretations, not authentic period color footage. #SanFrancisco1906 #HistoryReels",
        "TIKTOK":"San Francisco, 1906. Una città piena di vita poco prima del disastro. Quattro fotogrammi restaurati e un quinto che continua davvero a muoversi in colore ricostruito con AI. Film originale storico autentico, colori e animazione ricostruiti. #History",
        "YOUTUBE":"SAN FRANCISCO 1906 | THE CITY BEFORE THE EARTHQUAKE\n\nOriginal moving film of Market Street by the Miles Brothers, preserved in public collections: https://www.loc.gov/item/00694408/ . Four still images reconstructed from their exact original shots with image-to-image photo restoration; a fifth distinct real moving archival shot continues in one existing Vidu Q2 Pro Fast AI animation, matched to its original source frame at 43s. Colors, fine detail, and generated movement are interpretive AI reconstructions, not authentic period color film. Review rights before reuse."
    }
    for k,v in captions.items():
        (R/f"POST_{k}.txt").write_text(v+"\n",encoding="utf8")
    return list(captions)

def main():
    R.mkdir(parents=True,exist_ok=True)
    source,vidu,preview,anchor,classic_count,vidufps,vidunc,stats,viduqa,score,delta=prepare()
    bw_frames=round(1.08*FPS)
    vidu_frames=round(5.0*FPS)
    total_count=classic_count+bw_frames+vidu_frames
    length=total_count/FPS
    writer_path=R/"V98_VIDEO_ONLY.mp4"
    proc=subprocess.Popen(["ffmpeg","-nostdin","-y","-v","error",
        "-f","rawvideo","-pix_fmt","bgr24","-s","720x1280","-r","30",
        "-i","-","-an","-c:v","libx264","-preset","veryfast","-crf","18",
        "-pix_fmt","yuv420p","-movflags","+faststart",str(writer_path)],
        stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    motion_samples=[]
    prev=None
    try:
        # The V97 first 4 chapters are the user-approved, ACTUAL I2I historical scenes.
        for i in range(classic_count):
            ok,frame=preview.read()
            if not ok:raise RuntimeError("TRUNCATED_4_RESTAURATIONS_V97")
            proc.stdin.write(frame.tobytes())
        # Fifth historical chapter must use the *real* 41.92s-43s historical clip
        # that matches V86's paid source at 43s, NOT the unrelated 411s V97 shot.
        source.set(cv2.CAP_PROP_POS_MSEC,(VIDU_SOURCE_SECOND-bw_frames/FPS)*1000)
        raw=[]
        source_count=round(bw_frames*source.get(cv2.CAP_PROP_FPS))+3
        for k in range(source_count):
            ok,frame=source.read()
            if not ok:break
            cropped=cv2.resize(frame[:,VIDU_SOURCE_CROP_LEFT:VIDU_SOURCE_CROP_LEFT+603],
                (WIDTH,HEIGHT),interpolation=cv2.INTER_CUBIC)
            raw.append(cv2.cvtColor(cv2.cvtColor(cropped,cv2.COLOR_BGR2GRAY),cv2.COLOR_GRAY2BGR))
        if len(raw)<max(12,bw_frames*.75):raise RuntimeError("MISSING_FIFTH_GENUINE_ORIGINAL_MOVEMENT")
        for k in range(bw_frames):
            # Last two real original frames are exact verified anchor from t=43.0s.
            frame=anchor if k>=bw_frames-2 else raw[min(len(raw)-1,round(k*(len(raw)-1)/max(1,bw_frames-1)))]
            proc.stdin.write(frame.tobytes())
        # A single genuine, previously PAID Vidu video, without any new provider POST.
        # V86 clip has the carefully graded 1s B/W->color reveal on its OWN moving frames.
        for i in range(vidu_frames):
            vidu.set(cv2.CAP_PROP_POS_FRAMES,min(vidunc-1,round(i*vidufps/FPS)))
            ok,f=vidu.read()
            if not ok:raise RuntimeError("TRUNCATED_REAL_VIDU_MOTION")
            if prev is not None and i%15==0:
                gray=cv2.resize(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY),(180,320)).astype("float32")
                old=cv2.resize(cv2.cvtColor(prev,cv2.COLOR_BGR2GRAY),(180,320)).astype("float32")
                motion_samples.append({"vidu_s":round(i/FPS,2),"motion_delta":round(float(np.abs(gray-old).mean()),3),
                  "saturation_median":round(float(np.median(cv2.cvtColor(f,cv2.COLOR_BGR2HSV)[:,:,1])),1)})
            prev=f
            proc.stdin.write(f.tobytes())
    finally:
        source.release();vidu.release();preview.release()
        proc.stdin.close()
        err=proc.stderr.read().decode(errors="replace")
        if proc.wait():raise RuntimeError("VIDEO_ENCODE_FAILED "+err[-600:])
    # Do not call the static photograph a moving Vidu video: measure movement after reveal.
    moved=sum(x["motion_delta"]>1.2 for x in motion_samples if x["vidu_s"]>1.15)
    colorful=sum(x["saturation_median"]>12 for x in motion_samples if x["vidu_s"]>1.15)
    if moved<3 or colorful<3:
        raise RuntimeError("V98_VIDU_MOVEMENT_OR_COLOR_AFTER_1S_FAILED_"+str((moved,colorful)))
    starts=[0]
    at=0
    for t in FOUR_ORIGINAL_MOTIONS:
        at+=(round(t*FPS)+11+round(1.65*FPS))/FPS
        starts.append(at)
    music=prepare_audio(length,starts)
    run(["ffmpeg","-nostdin","-y","-v","error","-i",str(writer_path),"-i",str(music),
         "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","160k",
         "-shortest","-movflags","+faststart",str(RESULT)],180)
    run(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(RESULT),"-f","null","-"],180)
    probe=json.loads(run(["ffprobe","-v","error","-show_entries","format=duration,size:stream=codec_name,width,height",
         "-of","json",str(RESULT)],30))
    codecs={s.get("codec_name") for s in probe["streams"]}
    if not {"h264","aac"}.issubset(codecs):raise RuntimeError("V98_AUDIO_OR_VIDEO_MISSING")
    if not 19.2<float(probe["format"]["duration"])<20.1:raise RuntimeError("V98_DURATION_INCORRECT")
    make_contact();make_cover();posts=create_posts()
    qa={
        "version":"V98 2026-10-30","episode":"San Francisco 1906",
        "status":"COMPLETE_REVIEW_MP4_NOT_HUMAN_ARTISTIC_FINAL",
        "user_approved_base":"V97 four real image-to-image photo restorations",
        "original_archival_film_sha256":sha(ARCHIVE),
        "four_real_photographs_from_v97":[{"source_s":x,"actual_photo_sha256":sha(R/f"PHOTO_AI_{i:02}.png")}
            for i,x in enumerate(FOUR_SOURCE_TIMES,1)],
        "fifth_replaced_wrong_411s_source_with_authentic_source_s":VIDU_SOURCE_SECOND,
        "same_true_source_shot_gray_correlation_first_Vidu_frame":round(score,4),
        "same_true_source_luma_delta":round(delta,2),
        "original_BW_motion_before_fifth_Vidu_s":bw_frames/FPS,
        "existing_Vidu_motion_seconds":vidu_frames/FPS,
        "color_reveal_by_s":1.15,"full_Vidu_file_sha256":sha(VIDU),
        "existing_Vidu_original_paid_task_id":viduqa.get("vidu_task_id"),
        "additional_Vidu_credits_spent":0,"new_Vidu_paid_generations":0,
        "reuse_not_new_generation":True,
        "black_and_white_to_color_five_scene_structure":True,
        "photo_color_metrics":stats,"Vidu_motion_samples":motion_samples,
        "duration_s":float(probe["format"]["duration"]),
        "final_mp4_sha256":sha(RESULT),
        "final_mp4_bytes":RESULT.stat().st_size,
        "format":"720x1280 H264/AAC 30fps",
        "render_decode_pass":True,
        "artistic_QA":"PENDING_COMPLETE_VIEW",
        "source_rights_italy":"PENDING_REVIEW",
        "social_published":False,"site_published":False,
        "note":"Color restoration and AI motion are interpretive, not authentic archival color film; V96 artistic final requires human playback/review."
    }
    (R/"QA_V98.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n")
    with zipfile.ZipFile(OUTPUT_ZIP,"w",zipfile.ZIP_DEFLATED) as z:
        for f in [RESULT,COVER,CONTACT,R/"QA_V98.json",
                  *[R/f"POST_{v}.txt" for v in posts]]:
            z.write(f,f.name)
    with zipfile.ZipFile(OUTPUT_ZIP) as z:
        if z.testzip() is not None:raise RuntimeError("ANDROID_ZIP_BAD_CRC")
    print("SF1906_V98_REAL_FIVE_SCENE_MOVING_VIDU_MP4",str(RESULT),
          "duration",round(length,3),"bytes",RESULT.stat().st_size,
          "source_to_vidu_match",round(score,3),
          "moving_after_color",moved,
          "PAID_CALLS_THIS_RUN_ZERO",flush=True)
if __name__=="__main__":
    main()
