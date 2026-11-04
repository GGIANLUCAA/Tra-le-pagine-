#!/usr/bin/env python3
"""V285: Delhi moving historical film + five true color photos, with NO VIDU.

This is a new REVIEW MP4/ZIP correcting the missing-color ending in V282.
The real fifth Vidu clip is still missing; no fake animated photo, never FINAL.
"""
from __future__ import annotations
import argparse,hashlib,json,subprocess,zipfile
from pathlib import Path
from PIL import Image
import storia_rivive_v281_delhi_real_movement_stage as v281

FIFTH_SHA="556c432960bea3fd58663ac85ad77e792463fbcca1a92f3bb1b0616195a10264"
FIFTH_FRAME_SHA="28a71dff0d65a4529a946fbe1d531626c70dca389d344e4d17f7646022fc8ca2"
FIFTH_TIME=218.176
FIFTH_CROP=750
NAME="DELHI_1910_V285_FIVE_SOURCE_LOCKED_PHOTOS_NO_VIDU_PREVIEW_NOT_FINAL"

def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as file:
        for b in iter(lambda:file.read(1024*1024),b""):h.update(b)
    return h.hexdigest()

def assert_fifth(photos,manifest,original_frame):
    j=json.loads(Path(manifest).read_text(encoding="utf-8"))
    if(j.get("original_source_frame_sha256")!=FIFTH_FRAME_SHA
       or j.get("original_time_s")!=FIFTH_TIME
       or j.get("original_crop_bbox_px")!=[750,0,1358,1080]
       or j.get("generated_photo_sha256")!=FIFTH_SHA
       or j.get("scene5_photo_generated") is not True
       or j.get("auto_preflight_passed") is not True
       or j.get("five_second_vidu_clip_generated") is not False
       or j.get("scene5_photo_artistically_approved") is not False
       or j.get("italian_rights_approved") is not False
       or j.get("publication_allowed") is not False):
        raise ValueError("V285_FIFTH_I2I_PROVENANCE_OR_APPROVAL_CHANGED")
    pic=Path(photos)/j["generated_photo_filename"]
    if(not pic.is_file() or pic.is_symlink() or sha(pic)!=FIFTH_SHA
       or not Path(original_frame).is_file() or sha(original_frame)!=FIFTH_FRAME_SHA):
        raise ValueError("V285_FIFTH_REAL_IMAGE_HASH_MISMATCH")
    with Image.open(pic) as im:
        if im.size!=(720,1280) or im.format!="JPEG":raise ValueError("V285_FIFTH_PHOTO_DIMENSIONS")
    # V288: actual human review identified a human-cattle head fusion in this
    # exact source/restoration. Technical SHA and geometry PASS cannot waive it.
    # Original B/W movement can still be used; color reveal/VIDU needs new frame.
    from storia_rivive_visual_reject_v288 import require_safe_for_photo
    require_safe_for_photo("delhi_ruins_1910_v217",FIFTH_FRAME_SHA,sha(pic))
    return pic

def render_fifth_real_motion(film,out,original,photo):
    vf=f"crop=608:1080:{FIFTH_CROP}:0,scale=720:1280:flags=lanczos,fps=30,format=yuv420p"
    base=["-an","-vf",vf,"-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p","-r","30"]
    motion=out/"shot05_real_bw_motion.mp4"
    v281.command("ffmpeg","-hide_banner","-loglevel","error","-y",
                 "-ss",f"{FIFTH_TIME-1.3:.3f}","-i",str(film),"-t","1.3",*base,str(motion))
    freeze=out/"shot05_exact_original_freeze.mp4"
    v281.command("ffmpeg","-hide_banner","-loglevel","error","-y",
                 "-loop","1","-framerate","30","-i",str(original),"-t","0.13",*base,str(freeze))
    final=out/"shot05_true_photo_hold_NOT_VIDU.mp4"
    v281.render_segment(final,frame=photo,seconds=2.65)
    return [motion,freeze,final]

def render(film,frames,photos,qa,fifth_photos,fifth_report,out):
    original_report=v281.verify_inputs(film,frames,photos,qa)
    fifth=assert_fifth(fifth_photos,fifth_report,frames/v281.FRAMES[4])
    out.mkdir(parents=True,exist_ok=True)
    parts=[]
    for i,t in enumerate(v281.TIMES[:4]):
        bw=out/f"shot{i+1:02d}_real_bw.mp4"
        freeze=out/f"shot{i+1:02d}_freeze_real_frame.mp4"
        color=out/f"shot{i+1:02d}_real_i2i.jpg.mp4"
        v281.render_segment(bw,video=film,seconds=1.3,start=t-1.3)
        v281.render_segment(freeze,frame=frames/v281.FRAMES[i],seconds=.13)
        v281.render_segment(color,frame=photos/original_report["real_photo_files"][i]["actual_finegrain_photo_filename"],seconds=2.55)
        parts.extend((bw,freeze,color))
    parts.extend(render_fifth_real_motion(film,out,frames/v281.FRAMES[4],fifth))
    listing=out/"concat_paths.txt"
    # REAL line separators, not literal slash followed by n.
    listing.write_text("".join("file '"+str(p.resolve()).replace("'","'\\''")+"'\n" for p in parts))
    silent=out/"staged_no_audio.mp4"
    v281.command("ffmpeg","-hide_banner","-loglevel","error","-y",
                 "-f","concat","-safe","0","-i",str(listing),"-an",
                 "-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p",str(silent))
    meta=json.loads(v281.command("ffprobe","-v","error","-show_format","-of","json",str(silent)))
    length=float(meta["format"]["duration"])
    if not 14<=length<=35:raise ValueError("V285_BAD_DURATION")
    soundtrack=out/"synthesized_original_ambient.wav"
    v281.audio(soundtrack,length)
    movie=out/(NAME+".mp4")
    v281.command("ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(silent),"-i",str(soundtrack),
                 "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","128k","-shortest","-movflags","+faststart",str(movie))
    v281.command("ffmpeg","-hide_banner","-loglevel","error","-xerror","-i",str(movie),"-f","null","-")
    decoded=json.loads(v281.command("ffprobe","-v","error","-show_streams","-show_format","-of","json",str(movie)))
    if not any(s.get("codec_name")=="h264" for s in decoded["streams"]) or not any(s.get("codec_name")=="aac" for s in decoded["streams"]):
        raise ValueError("V285_H264_AAC_MISSING")
    cover=out/(NAME+"_COVER.jpg")
    v281.make_cover(photos/original_report["real_photo_files"][0]["actual_finegrain_photo_filename"],cover)
    social=out/"FOUR_SOCIAL_CAPTIONS_DRAFT_ONLY.txt"
    social.write_text("FACEBOOK: Delhi 1910 · restoration test, not an original color film. Not cleared for publication.\nINSTAGRAM: DELHI · 1910 | archival film & experimental AI reconstruction. Draft only.\nTIKTOK: Delhi 1910 | Original historical movement into AI-restored photography. Draft only.\nYOUTUBE: Delhi 1910 historical film restoration work in progress. Not publishable.\n",encoding="utf-8")
    status=out/"V285_MEDIA_QA_NOT_FINAL.json"
    info={"version":"V285_CORRECTED_FIFTH_COLOR_PHOTO_NOT_VIDU",
        "source_movie_sha256":v281.FILM_SHA,
        "photo5_sha256":FIFTH_SHA,
        "original_real_bw_moving_shots":5,
        "source_locked_frozen_original_frames":5,
        "real_photo_i2i_images":5,
        "vidu_animated_clips":0,
        "fifth_image_is_real_photo_not_animated":True,
        "duration_s":round(float(decoded["format"]["duration"]),3),
        "video_sha256":sha(movie),"video_bytes":movie.stat().st_size,
        "artistically_approved":False,"italian_rights_cleared":False,
        "real_vidu_required_to_finish":True,
        "publication_allowed":False,"approved_finished_episodes":0,
        "status":"RENDERED_NEEDS_REVIEW_NO_REAL_VIDU_NOT_FINAL"}
    status.write_text(json.dumps(info,indent=2)+"\n",encoding="utf-8")
    package=out/(NAME+"_ANDROID_REVIEW_ONLY.zip")
    with zipfile.ZipFile(package,"w",compression=zipfile.ZIP_DEFLATED) as z:
        for item in [movie,cover,social,status]:z.write(item,item.name)
    with zipfile.ZipFile(package) as z:
        if z.testzip() is not None:raise ValueError("V285_CORRUPT_REVIEW_ZIP")
    print("V285_REAL_LAST_SHOT_NOW_HAS_TRUE_COLOR_PHOTO",info["duration_s"],"VIDU_GENERATED_0","FINAL_0_OF_4")
    return info

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for key in ("film","frames","photos","qa","fifth-photos","fifth-report","out"):p.add_argument("--"+key,required=True,type=Path)
    a=p.parse_args()
    render(a.film,a.frames,a.photos,a.qa,a.fifth_photos,a.fifth_report,a.out)
