#!/usr/bin/env python3
"""ArtVision V4 Atelier: hand-directed 1/2/3 detail journeys, restrained film pacing, real licensed music."""
from __future__ import annotations
import argparse, hashlib, json, math, re, shutil, subprocess, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
from artvision import collect, download_pictures
from harmonic_reveal_v3 import render_frame, smooth, cmd

# Only tracks independently verified on the rightsholder's site.
TRACKS = {
    "evening_fall_piano": {
        "title": "Evening Fall (Piano)", "author": "Kevin MacLeod", "isrc": "USUAN1100235",
        "page": "https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100235",
        "urls": ["https://incompetech.com/music/royalty-free/mp3-royaltyfree/Evening%20Fall%20-%20Piano.mp3",
                 "https://commons.wikimedia.org/wiki/Special:Redirect/file/Evening%20Fall%20%28Piano%29%20%28ISRC%20USUAN1100235%29.mp3",
                 "https://upload.wikimedia.org/wikipedia/commons/f/fd/Evening_Fall_%28Piano%29_%28ISRC_USUAN1100235%29.mp3"],
        "license": "CC BY 4.0", "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "expected_seconds": 165},
    "calmant": {
        "title": "Calmant", "author": "Kevin MacLeod", "isrc": "USUAN1100859",
        "page": "https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100859",
        "url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Calmant.mp3",
        "license": "CC BY 4.0", "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "expected_seconds": 200},
}
# These locations and editing choices refer to distinctive, REAL features of Van Gogh's listed works.
# Coordinates within artwork: fractions x,y. A named motive accompanies every editorial decision.
EDITS = [
 {"key":"Irises","mood":"immersion","beats":[("detail",(.33,.36),"violet irises upper blooms"),
                                               ("detail",(.62,.56),"dense ultramarine petals"),
                                               ("detail",(.51,.81),"vase and turquoise tabletop"),
                                               ("reveal",None,"release into full floral composition"),
                                               ("whole",None,"rest on full painting")]},
 {"key":"Sunflowers","mood":"pulse","beats":[("whole",None,"open with complete sunflower painting"),
                                            ("push",(.34,.46),"blue background against flowers"),
                                            ("detail",(.66,.59),"thick golden flower brushwork"),
                                            ("reveal",None,"return to painting as a whole"),
                                            ("whole",None,"savor the full painting")]},
 {"key":"Two Poplars","mood":"rise","beats":[("detail",(.52,.27),"winding sky around cypress-like poplars"),
                                             ("detail",(.53,.70),"tree trunks and pale road"),
                                             ("reveal",None,"reveal diagonal perspective of landscape"),
                                             ("whole",None,"hold overall picture")]},
 {"key":"The Flowering Orchard","mood":"breath","beats":[("whole",None,"start with entire blooming orchard"),
                                                     ("push",(.50,.33),"forking branches with new buds"),
                                                     ("detail",(.44,.77),"spring greens and textured ground"),
                                                     ("whole",None,"restore wide orchard view")]},
 {"key":"Bouquet of Flowers","mood":"spark","beats":[("detail",(.35,.37),"flowers with orange petals"),
                                                ("detail",(.65,.50),"pale blossoms in the bouquet"),
                                                ("detail",(.50,.81),"vase with pink and red flowers"),
                                                ("reveal",None,"reveal entire still life"),
                                                ("whole",None,"stay with the full flower arrangement")]},
 {"key":"The Large Plane Trees","mood":"ground","beats":[("whole",None,"establish the tree-lined road"),
                                                 ("push",(.41,.34),"rhythm of intertwined trunks"),
                                                 ("detail",(.75,.69),"stones and pathway perspective"),
                                                 ("whole",None,"pause on tree-lined landscape")]},
 {"key":"First Steps","mood":"human","beats":[("detail",(.72,.51),"adult reaching toward child"),
                                        ("detail",(.43,.59),"child taking first steps"),
                                        ("reveal",None,"reveal family relationship"),
                                        ("whole",None,"linger on complete human scene")]},
 {"key":"The Zouave","mood":"portrait","beats":[("whole",None,"portrait as a complete human presence"),
                                          ("push",(.51,.27),"expression and direct gaze"),
                                          ("detail",(.52,.30),"eyes and character in the face")]},
 {"key":"Adeline Ravoux","mood":"portrait","beats":[("detail",(.52,.27),"eyes and quiet face of Adeline"),
                                              ("reveal",None,"reveal sitter and setting"),
                                              ("whole",None,"remain with full portrait")]},
 {"key":"L'Arlésienne","mood":"stillness","beats":[("whole",None,"whole seated figure first"),
                                             ("push",(.51,.29),"thoughtful expression"),
                                             ("detail",(.53,.72),"hands placed in the lap"),
                                             ("whole",None,"finish with complete seated figure")]},
 {"key":"Dr. Gachet","mood":"introspection","beats":[("detail",(.50,.29),"downturned face and intense eyes"),
                                              ("detail",(.41,.58),"hands and bowed body language"),
                                              ("reveal",None,"pull back to reveal portrait"),
                                              ("whole",None,"hold still and breathe")]},
 {"key":"Corridor in the Asylum","mood":"resolution","beats":[("whole",None,"architectural corridor seen in full"),
                                                         ("push",(.49,.52),"vanishing point of corridor"),
                                                         ("reveal",None,"withdraw to entire corridor"),
                                                         ("whole",None,"quiet final contemplation")]}
]
PHASE_WEIGHT={"detail":3.35,"whole":3.45,"push":3.0,"reveal":2.90}
WIDTH=1080;HEIGHT=1920;FPS=24

def pick_music(key, duration):
    if key not in TRACKS:raise ValueError("Requested music track unknown or unverified.")
    data=dict(TRACKS[key])
    if duration>data["expected_seconds"]-7:raise ValueError("Selected track insufficient for film")
    return data

def audio_download(music,out,minimum):
    path=out/"official_licensed_recording.mp3"
    candidates=music.get("urls") or [music.get("url")]
    errors=[]
    for url in candidates:
        try:
            with urlopen(Request(url,headers={"User-Agent":"ArtVisionVideoEditor/1.0 (artwork educational compilation; attribution follows CC BY 4.0)"}),timeout=55) as f:
                data=f.read(18000000)
            if len(data)<100000:raise ValueError("Unexpectedly small music file")
            path.write_bytes(data)
            fmt=json.loads(cmd(["ffprobe","-v","error","-show_entries","format=duration","-of","json",str(path)]))
            actual=float(fmt["format"]["duration"])
            if actual<minimum+.5:raise ValueError("Music shorter than video")
            proof={k:v for k,v in music.items() if k not in ("url","urls")}
            proof.update({"downloaded_from":url,"sha256":hashlib.sha256(data).hexdigest(),
                          "duration_seconds":actual,"editing":"excerpt, music volume and fades; soundtrack for art video",
                          "publication_attribution_required":True})
            return path,proof
        except Exception as exc:
            errors.append(str(exc)[:230]);path.unlink(missing_ok=True)
    raise RuntimeError("No verified recording available for chosen track: "+"; ".join(errors))

def storyboard(works, duration):
    selection=[]
    for item in EDITS:
        index=next((j for j,w in enumerate(works) if item["key"].lower() in w["title"].lower()),None)
        if index is not None:selection.append((index,item))
    if len(selection)<9:raise RuntimeError(f"Only {len(selection)} meaningfully curated artworks found. Refusing random framing.")
    # First 4.5 seconds for titling, final seconds for resolution; variable block durations depend on content.
    lengths=[sum(PHASE_WEIGHT[k] for k,*_ in item["beats"]) for _,item in selection]
    scale=duration/sum(lengths)
    scenes=[];t=0.
    for idx,(art_index,item) in enumerate(selection):
        parts=[]
        beats=item["beats"]
        for pi,(kind,focus,why) in enumerate(beats):
            seconds=PHASE_WEIGHT[kind]*scale
            if kind=="detail" and (item["mood"] in ("human","portrait","introspection")): seconds*=1.06
            parts.append({"kind":kind,"focus":focus,"why":why,"duration":seconds})
        block=sum(p["duration"] for p in parts)
        scenes.append({"art_index":art_index,"title":works[art_index]["title"],"mood":item["mood"],
                       "start":t,"end":t+block,"parts":parts,
                       "editorial_decision":"manually mapped significant motifs; no arbitrary crop"})
        t+=block
    # Normalize durations after emotional accent adjustment to precise output length.
    ratio=duration/t;at=0.
    for scene in scenes:
        scene["start"]=round(at,3)
        for part in scene["parts"]:part["duration"]*=ratio
        at+=sum(p["duration"] for p in scene["parts"])
        scene["end"]=round(at,3)
    return scenes

def load_sources(works,scenes):
    result={}
    for index in set(int(s["art_index"]) for s in scenes):
        with Image.open(works[index]["file"]) as orig:
            image=ImageOps.exif_transpose(orig).convert("RGB")
            # Avoid enormous memory use but retain > HD pixels in key art.
            image.thumbnail((3600,3600),Image.Resampling.LANCZOS)
        result[index]=cv2.cvtColor(np.array(image),cv2.COLOR_RGB2BGR)
    return result

def zoom_for(im,kind):
    h,w=im.shape[:2]
    # landscape works need deeper crop to let authentic painting fill portrait screen.
    return 2.0 if w/h>1.23 else (1.65 if w/h>0.9 else 1.48)

def moving_frame(im,kind,focus,progress,previous_zoom=None):
    focus=focus or (.5,.5)
    zmax=zoom_for(im,kind)
    if kind=="detail":
        z=zmax*(1.0015-0.003*smooth(progress))
    elif kind=="whole":
        z=1.0
    elif kind=="push":
        z=1+(zmax-1)*smooth(progress)
    elif kind=="reveal":
        z=1+(zmax-1)*(1-smooth(progress))
    else:raise RuntimeError("Bad shot kind")
    return render_frame(im,WIDTH,HEIGHT,focus,z)

def add_text(frame,title,track,stage):
    """Intermittent lower-left end credits, inside social-safe typography bounds."""
    if stage<=0:return frame
    pil=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)).convert("RGBA")
    layer=Image.new("RGBA",pil.size,(0,0,0,0))
    draw=ImageDraw.Draw(layer)
    ftitle="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
    fmeta="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    mainfont=ImageFont.truetype(ftitle,50)
    smallfont=ImageFont.truetype(fmeta,22)
    alpha=int(255*max(0,min(1,stage)))
    # Space reserved outside bottom platform overlay zone.
    bottom=HEIGHT-350
    draw.rounded_rectangle((64,bottom-44,WIDTH-64,bottom+115),radius=14,fill=(7,9,13,int(145*stage)))
    draw.text((96,bottom-20),title.upper(),font=mainfont,fill=(249,244,232,alpha))
    draw.text((97,bottom+62),f"Musica: {track['title']} · {track['author']}",
              font=smallfont,fill=(231,223,211,alpha))
    return cv2.cvtColor(np.asarray(Image.alpha_composite(pil,layer).convert("RGB")),cv2.COLOR_RGB2BGR)

def produce(works,scenes,duration,artist,track,audio,out,preview=False):
    working=out/"_temp_atelier";working.mkdir(parents=True,exist_ok=True)
    path=working/"uncompressed.mp4"
    writer=cv2.VideoWriter(str(path),cv2.VideoWriter_fourcc(*"mp4v"),FPS,(WIDTH,HEIGHT))
    if not writer.isOpened():raise RuntimeError("Cannot start V4 writer")
    sources=load_sources(works,scenes)
    allparts=[]
    for sc in scenes:
        for part in sc["parts"]:allparts.append((sc,part))
    target=int(duration*FPS);made=0
    try:
        for j,(scene,part) in enumerate(allparts):
            frames=max(2,round(part["duration"]*FPS))
            if j==len(allparts)-1:frames=max(1,target-made)
            img=sources[scene["art_index"]]
            focus=part["focus"]
            if focus is None:
                focus=next((pp["focus"] for pp in reversed(scene["parts"][:scene["parts"].index(part)]) if pp["focus"] is not None),(.5,.5))
            for k in range(frames):
                t=made/FPS
                progress=k/max(1,frames-1)
                frame=moving_frame(img,part["kind"],focus,progress)
                if t<5.4:
                    opacity=min(1,t/.9,max(0,(5.4-t)/.9))
                    frame=add_text(frame,artist,track,opacity)
                elif t>duration-5.4:
                    opacity=min(1,(t-(duration-5.4))/.9,max(0,(duration-t)/.7))
                    frame=add_text(frame,artist,track,opacity)
                # Readable understated shot transition: cut, no split, no flashes.
                if t>duration-2.1:
                    frame=cv2.convertScaleAbs(frame,alpha=max(0,(duration-t)/2.1))
                writer.write(frame);made+=1
            if j%4==0:print(f"Atelier shot {j+1}/{len(allparts)}: {scene['title']} - {part['kind']}",flush=True)
    finally:writer.release()
    if abs(made-target)>3:raise RuntimeError(f"Unexpected frames {made}, desired {target}")
    final=out/"ARTVISION_VIDEO.mp4"
    cmd(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(path),"-i",str(audio),
         "-map","0:v:0","-map","1:a:0","-t",str(duration),
         "-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","160k",
         "-af",f"volume=0.88,afade=t=in:st=0:d=1.8,afade=t=out:st={duration-4}:d=4",
         "-movflags","+faststart",str(final)])
    cmd(["ffmpeg","-hide_banner","-loglevel","error","-y","-ss","1.8","-i",str(final),"-frames:v","1",str(out/"COPERTINA.jpg")])
    probe=json.loads(cmd(["ffprobe","-v","error","-show_entries",
       "format=duration,size:stream=codec_type,width,height","-of","json",str(final)]))
    if abs(float(probe["format"]["duration"])-duration)>2 or {s["codec_type"] for s in probe["streams"]}!={"audio","video"}:raise RuntimeError("Final media validation failure")
    shutil.rmtree(working,ignore_errors=True)
    return probe

def main():
    parser=argparse.ArgumentParser(description="ArtVision Atelier V4 directorial render")
    parser.add_argument("--artist",default="Vincent van Gogh")
    parser.add_argument("--duration",type=int,default=150)
    parser.add_argument("--max-works",type=int,default=16)
    parser.add_argument("--music",default="evening_fall_piano",choices=list(TRACKS))
    parser.add_argument("--out",default="output/artvision")
    args=parser.parse_args()
    if not 120<=args.duration<=180:parser.error("Duration 120..180 seconds")
    if not 8<=args.max_works<=24:parser.error("Max works 8..24")
    if "van gogh" not in args.artist.lower():raise RuntimeError("Only Van Gogh has an approved V4 detail map; other artists require a NEW curated plan.")
    start=time.perf_counter();out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    records,errors=collect(args.artist)
    works,failures=download_pictures(records,out/"source_images",args.max_works)
    plan=storyboard(works,args.duration)
    music=pick_music(args.music,args.duration)
    audio,proof=audio_download(music,out,args.duration)
    (out/"MUSICA_LICENZA_E_CREDITI.json").write_text(json.dumps(proof,indent=2,ensure_ascii=False),encoding="utf8")
    credits=f'"{music["title"]}" Kevin MacLeod (incompetech.com) — CC BY 4.0 — {music["license_url"]} — excerpt and fades used.'
    selected={s["art_index"] for s in plan}
    (out/"OPERE_FONTI_E_DIRITTI.json").write_text(json.dumps({
       "artist":args.artist,"style":"atelier_v4","works":[works[i] for i in sorted(selected)],
       "download_errors":failures,"source_errors":errors,"publication_approved":False,
       "museum_reuse_conditions_need_manual_review":True},indent=2,ensure_ascii=False),encoding="utf8")
    (out/"STORYBOARD_REGIA.json").write_text(json.dumps(plan,indent=2,ensure_ascii=False),encoding="utf8")
    (out/"CREDITI_E_FONTI.txt").write_text("\n".join(
       f'{works[i]["title"]} — {works[i]["artist"]} — {works[i]["source"]} — {works[i]["url"]} — {works[i]["license"]}' for i in sorted(selected))
       +"\n\nMusica: "+credits+"\n",encoding="utf8")
    (out/"DESCRIZIONE_SOCIAL.txt").write_text(f"{args.artist}: un viaggio fra dettagli autentici e opere intere.\nMusica: {credits}\nFonti delle opere: CREDITI_E_FONTI.txt\n#artvision #arte #vangogh\n",encoding="utf8")
    probe=produce(works,plan,args.duration,args.artist,music,audio,out)
    report={"artist":args.artist,"style":"atelier_v4","scenes":len(plan),
        "shots":sum(len(s["parts"]) for s in plan),"works":len(selected),
        "duration":float(probe["format"]["duration"]),"resolution":"1080x1920",
        "bytes":int(probe["format"]["size"]),"music":music["title"],
        "music_rights":"CC BY 4.0, author credit required",
        "real_recording":True,"external_paid_apis_used":0,"voice":"off",
        "split_screen":False,"render_seconds":round(time.perf_counter()-start,2),
        "publishing_approved":False}
    (out/"REPORT_PRODUZIONE.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf8")
    audio.unlink(missing_ok=True);shutil.rmtree(out/"source_images",ignore_errors=True)
    print("ARTVISION ATELIER V4 COMPLETE",json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
