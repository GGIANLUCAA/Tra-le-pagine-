#!/usr/bin/env python3
"""Tra le Pagine V4: cinematic, story-driven visual effects without paid APIs.

Uses only FFmpeg, Pillow and NumPy; OpenCV adds better pencil linework when
available. No cloud calls, no GPU, no remote model download.

Design rules:
- Preserve the original illustration and its subject; no generative alteration.
- Strong brush/sketch reveals only for narrative turning points.
- Soft camera movement/atmosphere elsewhere; no hyperactive transitions.
- Every scene clip is encoded to matching fps/pixel format before concatenation.
"""
from __future__ import annotations

import json
import math
import re
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

FPS = 24
W, H = 720, 1280
EFFECTS = {"cinematic_pan", "sketch_paint", "brush_reveal", "parallax_soft", "light_atmosphere"}
STRONG = {"sketch_paint", "brush_reveal"}


def run(*args):
    subprocess.run([str(x) for x in args], check=True)


def pick_settings(config_path, scene_index, description, scene_count):
    """Human-authored per-scene directions take priority over heuristics."""
    config = {}
    if config_path and Path(config_path).exists():
        config = json.loads(Path(config_path).read_text(encoding="utf-8"))
    item = next((x for x in config.get("scenes", [])
                 if x.get("cue") == scene_index), None)
    if item is None:
        # Deliberate, conservative defaults for episodes with no art direction.
        if scene_index == 0:
            # Never impose a flashy intro on every book: explicit director approval.
            item = {"effect": "cinematic_pan"}
        elif scene_index == scene_count - 1:
            item = {"effect": "light_atmosphere"}
        else:
            item = {"effect": "cinematic_pan"}
    effect = item.get("effect", "cinematic_pan")
    if effect not in EFFECTS:
        raise ValueError(f"Effetto sconosciuto nella scena {scene_index}: {effect}")
    seconds = float(item.get("seconds", 2.8))
    if not 0.4 <= seconds <= 5.0:
        raise ValueError(f"Durata effetto non valida scena {scene_index}: {seconds}")
    mood = item.get("mood", "neutral")
    if mood not in {"neutral", "warm", "cool", "dusk"}:
        raise ValueError(f"Atmosfera non valida: {mood}")
    return effect, seconds, mood


def pick_postfx(config_path, scene_index):
    """Optional frei0r treatment, per storyboard cue; never used without explicit choice."""
    if not config_path or not Path(config_path).exists():
        return None
    config = json.loads(Path(config_path).read_text(encoding="utf-8"))
    item = next((x for x in config.get("scenes", [])
                 if x.get("cue") == scene_index), None)
    if not item:
        return None
    name = item.get("postfx")
    if name is None or name == "off":
        return None
    from frei0r_extra import PRESETS
    if name not in PRESETS:
        raise ValueError(f"Filtro esterno non autorizzato scena {scene_index}: {name!r}")
    return name


def color_grade(im, mood):
    if mood == "neutral":
        return im
    color = {"warm": (241, 180, 105), "cool": (103, 154, 208),
             "dusk": (112, 112, 175)}[mood]
    tinted = Image.new("RGB", im.size, color)
    return Image.blend(im, tinted, {"warm": 0.055, "cool": 0.06, "dusk": 0.075}[mood])


def sketch_image(img):
    """Generate pencil art from exactly the same pixels, so objects don't morph."""
    try:
        import cv2
        rgb = np.asarray(img)
        gray, _ = cv2.pencilSketch(
            cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR),
            sigma_s=70, sigma_r=0.08, shade_factor=0.055)
        sketch = Image.fromarray(gray, "L").convert("RGB")
    except (ImportError, AttributeError, cv2_error_type()):
        mono = ImageOps.grayscale(img)
        edges = ImageOps.invert(mono.filter(ImageFilter.FIND_EDGES))
        sketch = Image.blend(mono.convert("RGB"), edges.convert("RGB"), 0.68)
    return Image.blend(sketch, Image.new("RGB", img.size, (248, 243, 232)), 0.18)


def cv2_error_type():
    try:
        import cv2
        return cv2.error
    except ImportError:
        return ValueError


def muted_image(img):
    mono = ImageEnhance.Color(img).enhance(0.22)
    return Image.blend(mono, Image.new("RGB", img.size, (231, 214, 189)), 0.14)


def make_reveal_clip(img, dest, frames, kind, fps=FPS, w=W, h=H, seed=0):
    """Sweep irregular watercolor/pencil strokes using one existing illustration."""
    img = ImageOps.fit(img, (w, h), method=Image.Resampling.LANCZOS)
    rgb = np.asarray(img, dtype=np.float32)
    faded = sketch_image(img) if kind == "sketch_paint" else muted_image(img)
    original = np.asarray(faded, dtype=np.float32)
    rng = np.random.default_rng(197+seed*13)
    # Broad, organic deviations produce a soft, irregular brush edge.
    grain = Image.fromarray(rng.integers(0, 256,
                           (max(10,h//26), max(8,w//26)),dtype=np.uint8), "L")
    grain = grain.resize((w,h),Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(5))
    noise = (np.asarray(grain,dtype=np.float32)/255.0-.5)*.28
    yy,xx = np.mgrid[0:h,0:w]
    ridge = (xx.astype(np.float32)/w)*0.80 \
            + 0.13*np.sin(yy*math.tau/h*2.4+seed*.7) \
            + 0.055*np.cos(xx*math.tau/w*3.3+yy*0.008)
    wave = np.clip(ridge + noise, 0, 1)
    cmd = ["ffmpeg","-hide_banner","-loglevel","error","-y",
           "-f","rawvideo","-pixel_format","rgb24","-video_size",f"{w}x{h}",
           "-framerate",str(fps),"-i","pipe:0","-an","-c:v","libx264",
           "-preset","veryfast","-crf","23","-pix_fmt","yuv420p",
           "-r",str(fps),str(dest)]
    p = subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        for n in range(frames):
            progress=(n+1)/frames
            reveal=np.clip((progress*1.35-wave)*6.0,0,1).astype(np.float32)
            # Expensive effects limited to 1–3 key scenes, never the full video.
            frame=np.clip(original+(rgb-original)*reveal[:,:,None],0,255)
            p.stdin.write(frame.astype(np.uint8).tobytes())
        p.stdin.close()
        err=p.stderr.read().decode("utf-8","replace")
        if p.wait()!=0:
            raise RuntimeError("FFmpeg reveal non riuscito: "+err[-800:])
    finally:
        if p.poll() is None:p.kill()


def make_camera_clip(img,dest,frames, effect,mood,fps=FPS,w=W,h=H,seed=0):
    """CPU-efficient virtual camera; visual content remains the original drawing."""
    img = color_grade(img,mood)
    stage = ImageOps.fit(img,(int(w*1.14),int(h*1.14)),
                         method=Image.Resampling.LANCZOS)
    source=dest.with_suffix(".jpg")
    stage.save(source,quality=91)
    if effect=="parallax_soft":
        # Subtle 2.5D camera illusion; does NOT claim AI subject segmentation.
        zoom="min(zoom+0.00023,1.115)"
        x="iw/2-(iw/zoom/2)+14*sin(on/29)"
        y="ih/2-(ih/zoom/2)+9*cos(on/41)"
    elif effect=="light_atmosphere":
        zoom="min(zoom+0.00012,1.055)"
        x="iw/2-(iw/zoom/2)+7*sin(on/45)"
        y="ih/2-(ih/zoom/2)+5*cos(on/57)"
    else:
        zoom="min(zoom+0.00016,1.08)"
        sign=1 if seed%2 else -1
        x=f"iw/2-(iw/zoom/2)+{sign*9}*sin(on/37)"
        y="ih/2-(ih/zoom/2)+6*cos(on/46)"
    vf=(f"zoompan=z='{zoom}':x='{x}':y='{y}':"
        f"d=1:s={w}x{h}:fps={fps},format=yuv420p")
    if effect=="light_atmosphere":
        vf += ",eq=brightness='0.009*sin(2*PI*n/165)':eval=frame"
    run("ffmpeg","-hide_banner","-loglevel","error","-y","-loop","1",
        "-framerate",fps,"-i",source,"-vf",vf,"-frames:v",frames,
        "-an","-c:v","libx264","-preset","veryfast","-crf","23",
        "-pix_fmt","yuv420p","-r",fps,dest)


def render_montage(images,duration,tmp,starts=None,config_path=None,
                   output_manifest=None,fps=FPS,w=W,h=H):
    """Returns scene montage compatible with render.py; no TTS or network."""
    temp=Path(tmp)
    temp.mkdir(parents=True,exist_ok=True)
    total=math.ceil(duration*fps)
    if starts is not None:
        if len(starts)!=len(images): raise ValueError("Numero punti scena diverso")
        edges=[int(round(float(t)*fps)) for t in starts]+[total]
        edges[0]=0
        if any(a>=b for a,b in zip(edges,edges[1:])):
            raise ValueError("Tempi scena non crescenti")
        counts=[b-a for a,b in zip(edges,edges[1:])]
    else:
        counts=[total//len(images)+int(i<total%len(images))
                for i in range(len(images))]
    # V5 regia: validate the creative budget before rendering and match only
    # genuine color outliers in scenes with the SAME emotional palette.
    from regia_armonica_v5 import prepare
    quality_dir=Path(output_manifest).parent if output_manifest else temp
    images, editorial_report=prepare(
        images, temp/"v5_colori", config_path=config_path,
        report_path=quality_dir/"REGIA_ARMONICA_V5.json",
        contact_path=quality_dir/"CONTATTO_SCENE_V5.jpg")
    segments=[]
    manifest=[]
    for i,(picture,num) in enumerate(zip(images,counts)):
        effect,seconds,mood=pick_settings(config_path,i,"",len(images))
        im=Image.open(picture).convert("RGB")
        im=ImageOps.fit(im,(w,h),method=Image.Resampling.LANCZOS)
        introductory=0
        if effect in STRONG and num>=int(fps*1.2):
            introductory=min(int(round(seconds*fps)),max(1,num//2))
            intro=temp/f"v4_{i:02d}_reveal.mp4"
            make_reveal_clip(im,intro,introductory,effect,fps,w,h,i)
            segments.append(intro)
        remaining=num-introductory
        if remaining:
            camera=temp/f"v4_{i:02d}_camera.mp4"
            make_camera_clip(im,camera,remaining,
                             "cinematic_pan" if effect in STRONG else effect,
                             mood,fps,w,h,i)
            postfx=pick_postfx(config_path,i)
            if postfx:
                from frei0r_extra import apply_postfx
                filtered=temp/f"v4_{i:02d}_frei0r.mp4"
                apply_postfx(camera,filtered,postfx,remaining,fps)
                segments.append(filtered)
            else:
                segments.append(camera)
        else:
            postfx=None
        manifest.append({"cue":i,"asset":str(picture),"effect":effect,
                         "postfx":postfx,"mood":mood,"duration_sec":round(num/fps,3),
                         "reveal_sec":round(introductory/fps,3)})
        print(f"V4 scena {i+1}/{len(images)}: {effect} ({num/fps:.1f}s)",flush=True)
    listing=temp/"v4_segments.txt"
    listing.write_text("".join(f"file '{Path(x).resolve()}'\n" for x in segments),
                       encoding="utf-8")
    out=temp/"v4_montage.mp4"
    run("ffmpeg","-hide_banner","-loglevel","error","-y",
        "-f","concat","-safe","0","-i",listing,"-c","copy",out)
    if output_manifest is not None:
        Path(output_manifest).write_text(json.dumps(manifest,indent=2,
                     ensure_ascii=False),encoding="utf-8")
    return out
