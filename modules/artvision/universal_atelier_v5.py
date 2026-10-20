#!/usr/bin/env python3
"""ArtVision Universal Atelier V5.
One 150s international art film. Real artworks, quiet camera, invariant signature opening.
No narration, lyrics, subtitles, generic credit roll, split screens or AI-generated paintings.
Full legally required music attribution is saved in the public post description, not in video.
"""
from __future__ import annotations
import argparse, json, math, shutil, time
from pathlib import Path
from datetime import datetime, timezone
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
from artvision import collect, download_pictures
from atelier_v4 import (EDITS, TRACKS, PHASE_WEIGHT, audio_download, storyboard, load_sources, cmd, smooth)

W,H,FPS=1080,1920,24
INTRO_SEC=4.6
TRACKS=dict(TRACKS)
TRACKS["dreams_become_real"]={
    "title":"Dreams Become Real","author":"Kevin MacLeod",
    "isrc":"USUAN1500027",
    "page":"https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1500027",
    "urls":["https://incompetech.com/music/royalty-free/mp3-royaltyfree/Dreams%20Become%20Real.mp3"],
    "license":"CC BY 4.0",
    "license_url":"https://creativecommons.org/licenses/by/4.0/",
    "expected_seconds":410,
    "instrumental":True,
}
def font(path,size):
    choices=[path,"/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf","/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    for x in choices:
        if Path(x).exists():return ImageFont.truetype(x,size)
    return ImageFont.load_default()

def opening_type(frame,artist,music,seconds):
    """Identical typography layout on every episode. ONLY artist and tiny MUSIC BY."""
    if seconds >= INTRO_SEC:return frame
    # Film opens with artist text already readable; fade out slowly toward first detail.
    opacity=min(1.0,max(0.0,(INTRO_SEC-seconds)/.85))
    if opacity<=0:return frame
    im=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)).convert("RGBA")
    layer=Image.new("RGBA",(W,H),(0,0,0,0));draw=ImageDraw.Draw(layer)
    a=round(255*opacity)
    draw.rectangle((0,0,W,320),fill=(10,12,18,round(210*opacity)))
    draw.line((99,296,W-99,296),fill=(210,183,143,round(162*opacity)),width=2)
    face=font("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",67)
    caption=font("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",22)
    name=artist.upper()
    bbox=draw.textbbox((0,0),name,font=face)
    if bbox[2]>W-130:
        face=font("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",round(67*(W-150)/bbox[2]))
    rect=draw.textbbox((0,0),name,font=face)
    tx=(W-(rect[2]-rect[0]))/2
    draw.text((tx,141),name,font=face,fill=(252,248,240,a),stroke_width=0)
    tiny=f"MUSIC BY {music['author'].upper()}"
    box=draw.textbbox((0,0),tiny,font=caption)
    draw.text(((W-box[2])/2,236),tiny,font=caption,fill=(209,204,196,round(a*.9)))
    return cv2.cvtColor(np.array(Image.alpha_composite(im,layer).convert("RGB")),cv2.COLOR_RGB2BGR)

def gallery_background():
    """A smooth, color-neutral gallery, no fake extension of the original artwork."""
    y,x=np.mgrid[0:H,0:W]
    radius=((x-W*.5)/(W*.74))**2+((y-H*.51)/(H*.74))**2
    value=(24-13*np.clip(radius,0,1)).astype(np.uint8)
    return np.stack([value,value,value],axis=2)

MATTE=None
def render_art(im,focus,z):
    """Original aspect ratio maintained, pixel-density-aware zoom cap, no AI fill."""
    global MATTE
    if MATTE is None: MATTE=gallery_background()
    ih,iw=im.shape[:2]
    base=min((W-78)/iw,(H-280)/ih)
    # Preserve pixel density. Image must not be enlarged beyond ~1.35x native sample density.
    cap=max(1.0,min(2.2,1.35/base))
    z=min(z,cap)
    scale=base*z
    nw,nh=max(1,int(round(iw*scale))),max(1,int(round(ih*scale)))
    interp=cv2.INTER_AREA if scale<1 else cv2.INTER_CUBIC
    displayed=cv2.resize(im,(nw,nh),interpolation=interp)
    # Full image centered; detail focus follows the real photograph.
    mix=smooth(min(1,(z-1)/.52))
    x=int(round((W-nw)/2*(1-mix)+(W*.5-focus[0]*nw)*mix))
    y=int(round((H-nh)/2*(1-mix)+(H*.5-focus[1]*nh)*mix))
    result=MATTE.copy()
    ax=max(x,0);ay=max(y,0);bx=min(W,x+nw);by=min(H,y+nh)
    if bx>ax and by>ay:result[ay:by,ax:bx]=displayed[ay-y:by-y,ax-x:bx-x]
    return result

def zoom_cap(im):
    ih,iw=im.shape[:2]
    base=min((W-78)/iw,(H-280)/ih)
    native=min(iw*1.35/(W/base),ih*1.35/(H/base))
    desired=1.88 if iw/ih>1.28 else (1.62 if iw/ih>.9 else 1.47)
    return float(min(desired,max(1.0,native)))

def shot_zoom(kind,progress,max_z):
    if kind=="detail":return max_z*(1-.004*smooth(progress))
    if kind=="whole":return 1.
    if kind=="push":return 1+(max_z-1)*smooth(progress)
    if kind=="reveal":return 1+(max_z-1)*(1-smooth(progress))
    raise ValueError(kind)

def render(works,scenes,duration,artist,track,musicfile,out):
    out=Path(out); working=out/"_atelier_v5_tmp";working.mkdir(parents=True,exist_ok=True)
    raw=working/"silent.mp4"
    writer=cv2.VideoWriter(str(raw),cv2.VideoWriter_fourcc(*"mp4v"),FPS,(W,H))
    if not writer.isOpened():raise RuntimeError("V5 cannot open video writer")
    src=load_sources(works,scenes)
    parts=[(scene,item) for scene in scenes for item in scene["parts"]]
    target=duration*FPS
    previous=None; previous_scene=None;done=0
    try:
        for idx,(scene,part) in enumerate(parts):
            frames=max(2,round(part["duration"]*FPS))
            if idx==len(parts)-1:frames=target-done
            if frames<1:raise RuntimeError("Invalid V5 frame allocation")
            im=src[scene["art_index"]]
            maximum=zoom_cap(im)
            kind=part["kind"];focus=part.get("focus")
            if focus is None:
                prior=scene["parts"][:scene["parts"].index(part)]
                focus=next((p["focus"] for p in reversed(prior) if p.get("focus") is not None),(.5,.5))
            # Do not jump rapidly from one hand-selected detail to the next:
            # crossfade very briefly within the same work, never side-by-side.
            new_scene=previous_scene != scene["art_index"]
            dissolve=(8 if new_scene else 6) if idx>0 else 0
            for k in range(frames):
                phase=k/max(frames-1,1)
                z=shot_zoom(kind,phase,maximum)
                frame=render_art(im,focus,z)
                elapsed=done/FPS
                if elapsed<INTRO_SEC:
                    frame=opening_type(frame,artist,track,elapsed)
                if dissolve and k<dissolve and previous is not None:
                    blend=smooth((k+1)/(dissolve+1))
                    frame=cv2.addWeighted(previous,1-blend,frame,blend,0.)
                if elapsed>duration-2.2:
                    frame=cv2.convertScaleAbs(frame,alpha=max(0.,min(1.,(duration-elapsed)/2.2)))
                writer.write(frame)
                done+=1
                previous=frame
            previous_scene=scene["art_index"]
            print(f"V5 {idx+1}/{len(parts)}: {scene['title']} / {kind}; native detail zoom cap {maximum:.2f}x",flush=True)
    finally:
        writer.release()
    if abs(done-target)>3:raise RuntimeError(f"V5 frame mismatch: {done}/{target}")
    movie=out/"ARTVISION_VIDEO.mp4"
    cmd(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(raw),"-i",str(musicfile),
        "-map","0:v:0","-map","1:a:0","-t",str(duration),
        "-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p",
        "-c:a","aac","-b:a","192k","-af",f"volume=0.88,afade=t=in:st=0:d=1.2,afade=t=out:st={duration-3}:d=3",
        "-movflags","+faststart",str(movie)])
    cmd(["ffmpeg","-hide_banner","-loglevel","error","-y","-ss","1.7","-i",str(movie),"-frames:v","1",str(out/"COPERTINA.jpg")])
    probe=json.loads(cmd(["ffprobe","-v","error","-show_entries",
                         "format=duration,size:stream=codec_type,codec_name,width,height","-of","json",str(movie)]))
    streams=probe["streams"]
    if abs(float(probe["format"]["duration"])-duration)>1.2 or {x["codec_type"] for x in streams}!={"audio","video"}:
        raise RuntimeError("V5 media QA failed")
    vid=next(x for x in streams if x["codec_type"]=="video")
    if (vid["width"],vid["height"])!=(W,H):raise RuntimeError("V5 resolution QA failed")
    shutil.rmtree(working,ignore_errors=True)
    return probe

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--artist",default="Vincent van Gogh")
    p.add_argument("--duration",type=int,default=150)
    p.add_argument("--max-works",type=int,default=16)
    p.add_argument("--music",default="dreams_become_real",choices=sorted(TRACKS))
    p.add_argument("--out",default="output/artvision")
    args=p.parse_args()
    if not 120<=args.duration<=180:p.error("Single-film duration must be between 120 and 180s")
    if not 12<=args.max_works<=24:p.error("At least 12 museum records needed for curated film")
    if "van gogh" not in args.artist.lower():
        raise RuntimeError("No artist-specific hand-curated map for this artist yet. Create one before rendering (never reuse Van Gogh details).")
    started=time.monotonic();out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    music=TRACKS[args.music]
    if args.duration>music["expected_seconds"]-6:raise RuntimeError("Music shorter than requested film")
    # Fetch licensed recording FIRST: no expensive artwork download if the source fails.
    musicfile, proof=audio_download(music,out,args.duration)
    catalog,errs=collect(args.artist)
    works,download_errors=download_pictures(catalog,out/"source_images",args.max_works)
    scenes=storyboard(works,args.duration)
    chosen={s["art_index"] for s in scenes}
    proof.update({"onscreen_credit":"Music by "+music["author"],
                  "full_license_attribution_in_social_caption":True})
    (out/"MUSICA_LICENZA_E_CREDITI.json").write_text(json.dumps(proof,indent=2,ensure_ascii=False),encoding="utf8")
    (out/"STORYBOARD_REGIA.json").write_text(json.dumps(scenes,indent=2,ensure_ascii=False),encoding="utf8")
    (out/"OPERE_FONTI_E_DIRITTI.json").write_text(json.dumps({
        "artist":args.artist,"style":"universal_atelier_v5",
        "works":[works[i] for i in sorted(chosen)],"source_errors":errs,"download_errors":download_errors,
        "publication_approved":False,"attributions_visible_only_in_caption":True,
        "museum_reuse_conditions_manual_check_required":True},indent=2,ensure_ascii=False),encoding="utf8")
    credits=[f'{works[i]["title"]} — {works[i]["artist"]} — {works[i]["source"]} — {works[i]["url"]} — {works[i]["license"]}' for i in sorted(chosen)]
    credit=f'"{music["title"]}" Kevin MacLeod (incompetech.com) | CC BY 4.0 | https://creativecommons.org/licenses/by/4.0/ | edited: excerpt, level, fade.'
    (out/"CREDITI_E_FONTI.txt").write_text("\n".join(credits)+"\n\nMusic: "+credit+"\n",encoding="utf8")
    (out/"DESCRIZIONE_SOCIAL.txt").write_text(
        f"{args.artist} | ArtVision\n\nMusic: {credit}\n\n"
        "Artworks: see CREDITI_E_FONTI.txt for title, museum, source and licensing details.\n"
        "#ArtVision #Art #Painting\n",encoding="utf8")
    media=render(works,scenes,args.duration,args.artist,music,musicfile,out)
    report={"artist":args.artist,"style":"universal_atelier_v5","one_video_only":True,
        "runtime_seconds":float(media["format"]["duration"]),"resolution":"1080x1920",
        "works":len(chosen),"shots":sum(len(x["parts"]) for x in scenes),
        "file_size_bytes":int(media["format"]["size"]),"processing_seconds":round(time.monotonic()-started,2),
        "music_track":music["title"],"music_author":music["author"],
        "text_in_video":["artist_name","music_by"],"other_credits_in_video":False,
        "real_recording":True,"paid_apis":0,"published":False}
    (out/"REPORT_PRODUZIONE.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf8")
    musicfile.unlink(missing_ok=True);shutil.rmtree(out/"source_images",ignore_errors=True)
    print("ARTVISION V5 FINISHED",json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__": main()
