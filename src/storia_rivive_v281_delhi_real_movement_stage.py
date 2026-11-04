#!/usr/bin/env python3
"""V281: real Delhi 1910 moving-film -> EXACT archival freeze -> 4 true Finegrain I2I.

PRODUCTION WORK-IN-PROGRESS. NOT FINAL: no Vidu shot5, artistic and Italian rights
still pending. Does not synthesize/pretend a Vidu scene. No provider POST.
"""
from __future__ import annotations
import argparse, hashlib, json, math, shutil, subprocess, wave, zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

FILM_SHA="0a0de7b032cdb19e34d4dac5a6efca02dfa4b00260411aa82290c54b2899f278"
FRAMES=("frame_01.png","frame_04.png","frame_06.png","frame_11.png","frame_12.png")
FRAME_HASHES=(
"1b6464e8566ba5c292b59f4d5aa1c3f01de767f0feb58f0ad5cd10de744157fc",
"8771b50f5a26b3e27eadf00ad085f998bfe2d552daa7f8492027a4c40c6c2a71",
"d6a6f21789093f971cff0adfa4259511a24875eb73753b8c7f177b882762f16e",
"05e8e7d2c0134ecb4c9f31dbc469c31fc68981379513aa3bdb85694bc4d0a0f6",
"28a71dff0d65a4529a946fbe1d531626c70dca389d344e4d17f7646022fc8ca2")
TIMES=(9.486,66.401,104.345,199.204,218.176)
RUNTIME=(1.3, .13, 2.55, 3.5)  # actual original motion, exact freeze, photo, shot5 BW
NAME="DELHI_1910_V281_REAL_MOVEMENT_FOUR_I2I_NO_VIDU_NOT_FINAL"
SOURCE_URL="https://commons.wikimedia.org/wiki/File:Ruins_of_Delhi_(1910).webm"

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):
            h.update(block)
    return h.hexdigest()

def command(*args):
    p=subprocess.run(args,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if p.returncode:
        raise RuntimeError(str(args[:5])+" : "+p.stderr[-1600:])
    return p.stdout

def verify_inputs(film,frames,photos,qa):
    if not film.is_file() or sha(film)!=FILM_SHA:
        raise ValueError("V281_ORIGINAL_1910_FILM_SHA_MISMATCH")
    data=json.loads(Path(qa).read_text())
    if(data.get("source_identity",{}).get("original_film_sha256")!=FILM_SHA
       or data.get("source_identity",{}).get("verified_unique_frames")!=5
       or data.get("artistic_approval") is not False
       or data.get("vidu_scene5_generated") is not False
       or data.get("italian_rights_verified") is not False
       or data.get("publish_allowed") is not False
       or len(data.get("real_photo_files",[]))!=4):
        raise ValueError("V281_UNTRUSTED_REAL_I2I_REPORT")
    for i,frame in enumerate(FRAMES):
        p=frames/frame
        if not p.is_file() or p.is_symlink() or sha(p)!=FRAME_HASHES[i]:
            raise ValueError("V281_ORIGINAL_FRAME_SHA_MISMATCH:"+frame)
        with Image.open(p) as im:
            if im.format!="PNG" or im.size!=(1920,1080):
                raise ValueError("V281_FRAME_DIMENSIONS_CHANGED")
    for i,row in enumerate(data["real_photo_files"]):
        if(row.get("shot")!=i+1 or row.get("original")!=FRAMES[i]
           or row.get("source_frame_sha256")!=FRAME_HASHES[i]
           or row.get("artistically_approved") is not False):
            raise ValueError("V281_PHOTO_SOURCE_IDENTITY_MISMATCH")
        p=photos/row["actual_finegrain_photo_filename"]
        if not p.is_file() or p.is_symlink() or sha(p)!=row["real_i2i_sha256"]:
            raise ValueError("V281_GENERATED_PHOTO_SHA_MISMATCH")
        with Image.open(p) as im:
            if im.format!="JPEG" or im.size!=(720,1280):
                raise ValueError("V281_PHOTO_BAD_RASTER")
    return data

def render_segment(out,video=None,frame=None,seconds=1.0,start=0.0):
    vf="crop=608:1080:656:0,scale=720:1280:flags=lanczos,fps=30,format=yuv420p" if video else "scale=720:1280,fps=30,format=yuv420p"
    if video:
        args=["ffmpeg","-hide_banner","-loglevel","error","-y","-ss",f"{start:.3f}","-i",str(video),"-t",f"{seconds:.3f}"]
    else:
        args=["ffmpeg","-hide_banner","-loglevel","error","-y","-loop","1","-framerate","30","-i",str(frame),"-t",f"{seconds:.3f}"]
        if frame.suffix.lower()==".png" and frame.name.startswith("frame_"):
            vf="crop=608:1080:656:0,scale=720:1280:flags=lanczos,fps=30,format=yuv420p"
    command(*args,"-an","-vf",vf,"-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p","-r","30","-video_track_timescale","30000",str(out))

def audio(out,seconds):
    # Original synthesized ambient soundtrack, no copyrighted recording/provider.
    rate=16000
    n=round(seconds*rate)
    with wave.open(str(out),"wb") as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate)
        import array
        b=array.array("h")
        for i in range(n):
            t=i/rate
            fade=min(1., t/1.1, max(0.,(seconds-t)/1.2))
            tone=(math.sin(2*math.pi*110*t)+.4*math.sin(2*math.pi*164.81*t)+.3*math.sin(2*math.pi*220*t))
            b.append(int(1250*fade*tone))
            if len(b)>=4096:
                w.writeframes(b.tobytes());b=array.array("h")
        if b:w.writeframes(b.tobytes())

def make_cover(photo,out):
    with Image.open(photo) as im: canvas=im.convert("RGB").copy()
    draw=ImageDraw.Draw(canvas)
    for y in range(0,160):
        a=int(150*(1-y/160))
        draw.line((0,y,719,y),fill=(max(0,32-int(a*.2)),max(0,32-int(a*.2)),max(0,32-int(a*.2))))
    f="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    try:font=ImageFont.truetype(f,34)
    except OSError:font=ImageFont.load_default()
    draw.text((34,38),"DELHI  ·  1910",font=font,fill=(255,255,255),stroke_width=1,stroke_fill=(25,25,25))
    canvas.save(out,quality=91)

def main():
    p=argparse.ArgumentParser()
    for option in ("film","frames","photos","qa","out"):p.add_argument("--"+option,required=True,type=Path)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    report=verify_inputs(a.film,a.frames,a.photos,a.qa)
    parts=[]; durations=[]
    for i,t in enumerate(TIMES):
        if i<4:
            motion=a.out/f"part{i+1}_bw_motion.mp4"
            still=a.out/f"part{i+1}_exact_freeze.mp4"
            photo=a.out/f"part{i+1}_real_i2i.mp4"
            render_segment(motion,video=a.film,seconds=RUNTIME[0],start=t-RUNTIME[0])
            render_segment(still,frame=a.frames/FRAMES[i],seconds=RUNTIME[1])
            image=a.photos/report["real_photo_files"][i]["actual_finegrain_photo_filename"]
            render_segment(photo,frame=image,seconds=RUNTIME[2])
            parts.extend([motion,still,photo]);durations.extend(RUNTIME[:3])
        else:
            motion=a.out/"part5_bw_source_only_NO_VIDU.mp4"
            render_segment(motion,video=a.film,seconds=RUNTIME[3],start=t-RUNTIME[3])
            parts.append(motion);durations.append(RUNTIME[3])
    listing=a.out/"inputs.txt"
    listing.write_text("".join("file '"+str(f.resolve()).replace("'","'\\''")+"'\\n" for f in parts))
    noaudio=a.out/"video_assembled_no_audio.mp4"
    command("ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0","-i",str(listing),
            "-an","-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p",str(noaudio))
    probe=json.loads(command("ffprobe","-v","error","-show_format","-of","json",str(noaudio)))
    length=float(probe["format"]["duration"])
    if not 14<=length<=35:raise ValueError("V281_BAD_DURATION")
    soundtrack=a.out/"original_ambient.wav";audio(soundtrack,length)
    movie=a.out/(NAME+".mp4")
    command("ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(noaudio),"-i",str(soundtrack),
            "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","128k","-shortest","-movflags","+faststart",str(movie))
    command("ffmpeg","-v","error","-xerror","-i",str(movie),"-f","null","-")
    meta=json.loads(command("ffprobe","-v","error","-show_streams","-show_format","-of","json",str(movie)))
    streams=meta["streams"]
    if not any(x["codec_name"]=="h264" for x in streams) or not any(x["codec_name"]=="aac" for x in streams):
        raise ValueError("V281_UNDECODABLE_MP4_OR_AUDIO")
    cover=a.out/(NAME+"_COVER.jpg")
    make_cover(a.photos/report["real_photo_files"][0]["actual_finegrain_photo_filename"],cover)
    posts=a.out/"SOCIAL_COPY_DRAFT_NOT_PUBLISHABLE.txt"
    posts.write_text(
        "FOUR SOCIAL DRAFTS — NOT APPROVED OR PUBLISHED; RIGHTS ITALY NOT CLEARED\\n\\n"
        "Facebook: Delhi, 1910. Archival movement meets experimental AI restoration. Research preview.\\n\\n"
        "Instagram: DELHI · 1910 | Historical film and experimental photo restoration. Not an original color film.\\n\\n"
        "TikTok: DELHI · 1910 — Real historical footage, experimental restoration. Preview only.\\n\\n"
        "YouTube Shorts: Delhi in 1910 — An archival film restoration work in progress.\\n",
        encoding="utf-8")
    status={"version":"V281_REAL_ARCHIVE_MOTION_FOUR_REAL_I2I_STAGE_NOT_FINAL",
            "original_film_sha256":FILM_SHA,"source_page":SOURCE_URL,
            "photos_source_locked":4,"actual_original_film_motion_segments":5,
            "original_freeze_exact_sha_frames":4,
            "vidu_clips":0,"fifth_sequence_is_unrestored_original_film":True,
            "artistic_approval":False,"italian_rights_verified":False,
            "publish_allowed":False,"final_video":False,
            "new_finished_episodes_delivered":0,
            "missing":["REAL_SOURCE_LOCKED_VIDU_SCENE5","ARTISTIC_QA","ITALY_RIGHTS","FINAL_V91_V94_V96_V99"],
            "video_sha256":sha(movie),"duration_s":float(meta["format"]["duration"]),
            "video_bytes":movie.stat().st_size,
            "source_frame_sha256s":list(FRAME_HASHES),
            "video_status":"WORK_IN_PROGRESS_REAL_MOTION_PREVIEW_NOT_A_FINAL"}
    qaout=a.out/"V281_REAL_MEDIA_STATUS_NOT_FINAL.json"
    qaout.write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    bundle=a.out/(NAME+"_ANDROID_REVIEW_ONLY.zip")
    with zipfile.ZipFile(bundle,"w",compression=zipfile.ZIP_DEFLATED) as z:
        for f in (movie,cover,posts,qaout):z.write(f,f.name)
    if zipfile.ZipFile(bundle).testzip() is not None:raise RuntimeError("CORRUPT_REVIEW_ZIP")
    print("V281_REAL_MOTION_MP4_CREATED_REVIEW_ONLY",movie,"SECONDS",status["duration_s"],"FINISHED",0,"OF",4)

if __name__=="__main__":main()
