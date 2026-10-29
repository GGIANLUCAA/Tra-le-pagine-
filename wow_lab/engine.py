#!/usr/bin/env python3
"""WOW LAB V1, standalone, zero-paid CPU content lab.

All reads/writes are constrained to wow_lab/ and an explicit --out directory.
No imports from parent ArtVision modules, no social publication, no Vidu.
This renderer produces CINEMATIC 2.5D PREVIEW candidates, not true 3D meshes.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import io
import json
import math
import os
import random
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import wave
import zipfile
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent
API = "https://collectionapi.metmuseum.org/public/collection"
PREFIX = "wow-lab-v1-"
SCHEMA = "wow-lab-v1"
SAFE_MODES = ("gallery_orbit", "luminous_reveal", "depth_portal")


def read_config(path: Path) -> dict:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if obj.get("schema") != "artvision-wow-lab-v1":
        raise ValueError("Unexpected WOW LAB config version")
    if not obj.get("no_paid_services") or not obj.get("no_vidu"):
        raise ValueError("Fail closed: paid service or Vidu flag altered")
    if not obj.get("no_core_config_edits") or not obj.get("no_core_automation_edits"):
        raise ValueError("Fail closed: core project boundaries relaxed")
    if obj.get("output_scope") != "wow-lab-* releases and artifacts only":
        raise ValueError("Output scope mismatch")
    if tuple(obj.get("techniques", [])) != SAFE_MODES:
        raise ValueError("Unreviewed technique configured")
    return obj


def slot_id(value: str | None) -> str:
    if value:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}", value):
            raise ValueError("Use UTC slot YYYY-MM-DDTHH")
        stamp = dt.datetime.strptime(value, "%Y-%m-%dT%H").replace(tzinfo=dt.timezone.utc)
    else:
        stamp = dt.datetime.now(dt.timezone.utc)
    stamp = stamp.replace(hour=stamp.hour // 2 * 2, minute=0, second=0, microsecond=0)
    return stamp.strftime("%Y%m%dT%H")


def get_bytes(url: str, limit: int = 18_000_000, attempts: int = 2) -> bytes:
    if not url.startswith("https://"):
        raise ValueError("HTTPS only")
    last_error = None
    for index in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ArtVision-WowLab-V1 (CC0 educational video experiment)", "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=35) as stream:
                payload = stream.read(limit + 1)
            if not payload or len(payload) > limit:
                raise ValueError("Empty or oversized response")
            return payload
        except Exception as err:
            last_error = err
            if index + 1 < attempts:
                time.sleep(2 + index * 3)
    raise RuntimeError("Could not fetch source: " + str(last_error))


def get_json(url: str) -> dict:
    return json.loads(get_bytes(url, limit=3_000_000).decode("utf-8"))


def recent_history() -> list[dict]:
    """Read only prerelease descriptions with our prefix; no modifications."""
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    token = os.environ.get("GITHUB_TOKEN", "")
    if repository != "GGIANLUCAA/Tra-le-pagine-" or not token:
        return []
    url = f"https://api.github.com/repos/{repository}/releases?per_page=50"
    request = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
        "User-Agent": "ArtVision-WowLab-Isolated",
    })
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            releases = json.load(response)
    except Exception as err:
        print(f"WOW_LAB history unavailable, using deterministic fallback: {err}", file=sys.stderr)
        return []
    history = []
    for release in releases:
        if not str(release.get("tag_name", "")).startswith(PREFIX):
            continue
        body = release.get("body") or ""
        found = re.search(r"<!-- WOWLAB_META (.*?) -->", body)
        if not found:
            continue
        try:
            meta = json.loads(found.group(1))
        except (ValueError, TypeError):
            continue
        if meta.get("schema") == SCHEMA:
            history.append(meta)
    return history[:25]


def object_url(object_id: int) -> str:
    return f"{API}/v1/objects/{object_id}"


def valid_object(record: dict) -> bool:
    image = record.get("primaryImage") or record.get("primaryImageSmall") or ""
    if not record.get("isPublicDomain", False) or not image.startswith("https://"):
        return False
    if int(record.get("objectID") or 0) <= 0:
        return False
    # Prevent sculptures and unrelated inventory records from being called paintings.
    label = " ".join([str(record.get("objectName") or ""),
                      str(record.get("medium") or ""),
                      str(record.get("classification") or "")]).lower()
    return any(token in label for token in ("paint", "oil on", "tempera", "watercolor", "drawing", "print"))


def discovery_ids(query: str, limit: int = 12) -> list[int]:
    args = urllib.parse.urlencode({"hasImages": "true", "q": query})
    for prefix in [f"{API}/v1.1/search", f"{API}/v1/search"]:
        try:
            obj = get_json(prefix + "?" + args)
            ids = obj.get("objectIDs") or []
            return [int(x) for x in ids[:limit] if isinstance(x, int)]
        except Exception as exc:
            print(f"WOW_LAB discovery fallback {query[:20]}: {str(exc)[:100]}", file=sys.stderr)
    return []


def select_artwork(conf: dict, stamp: str, history: list[dict], fixed_id: int | None = None):
    recently = [int(h.get("object_id", 0)) for h in history[:6]]
    rng = random.Random(stamp)
    candidates = [int(v) for v in conf["allowed_artwork_ids"]]
    if fixed_id is not None:
        # fixed ID used only for explicit test; still require official source rights.
        candidates = [int(fixed_id)]
    elif conf.get("allow_museum_api_search"):
        queries = conf.get("search_queries", [])
        if queries:
            index = (int(stamp[-2:]) // 2 + int(stamp[-4:-2])) % len(queries)
            queries = queries[index:] + queries[:index]
        for q in queries[:3]:
            candidates.extend(discovery_ids(q, limit=9))
    # Keep stable deterministic list, then prioritize novelty.
    candidates = list(dict.fromkeys(candidates))
    if fixed_id is None:
        rng.shuffle(candidates)
        candidates.sort(key=lambda n: (n in recently[:3], n in recently, n in conf["allowed_artwork_ids"]))
    problems = []
    for ident in candidates[:20]:
        if fixed_id is None and ident == (recently[0] if recently else None):
            continue
        try:
            rec = get_json(object_url(ident))
            if not valid_object(rec):
                continue
            if not str(rec.get("title") or "").strip():
                continue
            return rec
        except Exception as err:
            problems.append(f"{ident}:{str(err)[:45]}")
    raise RuntimeError("No suitable verified CC0 artwork available; skipping this slot. " + " / ".join(problems[:4]))


def save_original(rec: dict, out: Path, conf: dict):
    url = rec.get("primaryImage") or rec.get("primaryImageSmall")
    if not url or not url.startswith("https://"):
        raise RuntimeError("No original official Met image URL")
    failures = []
    for candidate in list(dict.fromkeys([url, rec.get("primaryImageSmall")])):
        if not candidate:
            continue
        try:
            payload = get_bytes(candidate, limit=20_000_000)
            with Image.open(io.BytesIO(payload)) as opened:
                image = ImageOps.exif_transpose(opened).convert("RGB")
            w, h = image.size
            if min(w, h) < min(conf["min_image_width"], conf["min_image_height"]):
                failures.append("Low source pixel count")
                continue
            # Save exact source bytes for provenance. Not generate fake details.
            (out / "SOURCE_MET_ORIGINAL.jpg").write_bytes(payload)
            return image, candidate, hashlib.sha256(payload).hexdigest()
        except Exception as err:
            failures.append(str(err)[:150])
    raise RuntimeError("CC0 source acquisition unavailable: " + "; ".join(failures))


def font(size: int):
    for location in ["/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
                     "/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf",
                     "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        if Path(location).is_file():
            return ImageFont.truetype(location, size)
    return ImageFont.load_default()


def fit_text(label: str, width: int, size: int = 26):
    label = " ".join((label or "UNTITLED").upper().split())
    if len(label) > 70:
        label = label[:67].rstrip() + "..."
    f = font(size)
    while size > 13 and ImageDraw.Draw(Image.new("RGB", (4, 4))).textbbox((0, 0), label, font=f)[2] > width:
        size -= 1
        f = font(size)
    return label, f


def prepare_panel(source: Image.Image, target_w: int, target_h: int, trim_mode: str):
    original = source.copy()
    original.thumbnail((target_w-30, target_h-30), Image.Resampling.LANCZOS)
    if original.width < 260 or original.height < 180:
        raise RuntimeError("Artwork too narrow after fitting")
    pw, ph = original.size
    border = 22
    cv = Image.new("RGBA", (pw + border * 2, ph + border * 2), (0, 0, 0, 0))
    artist = ImageDraw.Draw(cv)
    layers = [(0, (63, 40, 26, 255)), (4, (120, 76, 43, 255)),
              (9, (221, 171, 84, 255)), (14, (106, 71, 37, 255)),
              (18, (219, 177, 111, 255))]
    for offset, color in layers:
        artist.rectangle((offset, offset, cv.width-offset-1, cv.height-offset-1), outline=color, width=5)
    cv.alpha_composite(original.convert("RGBA"), (border, border))
    return cv


def mood_colors(source: Image.Image):
    small = np.asarray(source.resize((48, 48), Image.Resampling.BILINEAR)).astype(np.float32)
    avg = np.clip(np.mean(small, axis=(0,1)), 0, 255)
    return tuple(int(x) for x in avg)


def stage_base(W: int, H: int, accent: tuple[int,int,int], timep: float):
    yy, xx = np.mgrid[:H, :W]
    focus = np.exp(-(((xx-W*.56)/(W*.86))**2 + ((yy-H*.39)/(H*.82))**2)*1.4)
    # True gallery-like lighting and non-geometric soft illumination.
    noise = np.random.default_rng(91).normal(0, 0.6, (H, W))
    background = np.zeros((H,W,3), np.uint8)
    for channel, base in enumerate((18, 20, 27)):
        ref = np.clip(accent[channel], 30, 175) / 175
        data = base + (13 + 21*ref)*focus + noise
        background[:,:,channel] = np.uint8(np.clip(data,0,255))
    yy2 = H * .79
    background[int(yy2):] = np.clip(background[int(yy2):].astype(np.float32)*0.72+9, 0,255).astype(np.uint8)
    return background


def eased(x):
    x = max(0.0, min(1.0, x))
    return x*x*(3-2*x)


def shot_params(mode: str, p: float, W: int, H: int, sz: tuple[int,int]):
    sw, sh = sz
    # All techniques have camera movement plus different meaningful optical reveals.
    if mode == "gallery_orbit":
        a = math.sin((p*.95+.1)*math.pi)*0.105
        magnitude = 1.12 - 0.10*eased(p)
        yoff = -22*math.sin(p*math.pi)
    elif mode == "luminous_reveal":
        a = (p-.25)*0.12
        magnitude = 1.10 + 0.07*math.sin(p*math.pi)
        yoff = 28-60*eased(p)
    else:
        a = math.sin((p*.82+.12)*math.pi)*0.15
        magnitude = 1.02 + 0.16*eased(p)
        yoff = 24-36*eased(p)
    xoff = (p-.5)*(36 if mode != "gallery_orbit" else -48)
    center_x = W/2 + xoff
    center_y = H*.49+yoff
    halfw = sw/2*magnitude
    halfh = sh/2*magnitude
    perspective = a * halfw
    quad=np.float32([
        [center_x-halfw+perspective, center_y-halfh-0.8*a*sh],
        [center_x+halfw+perspective, center_y-halfh+0.8*a*sh],
        [center_x+halfw-perspective, center_y+halfh-0.6*a*sh],
        [center_x-halfw-perspective, center_y+halfh+0.6*a*sh],
    ])
    if not cv2.isContourConvex(quad.astype(np.int32)):
        raise RuntimeError('Invalid camera quadrilateral: self-crossing or concave')
    if not (quad[:,0].min() >= -W*.12 and quad[:,0].max() <= W*1.12 and
            quad[:,1].min() > H*.10 and quad[:,1].max() < H*.82):
        raise RuntimeError('Camera projected the artwork beyond the safe museum view')
    return quad


def draw_video_frame(panel_bgra, W: int, H: int, p: float, mode: str, accent,
                     title: str, artist: str, year: str):
    scene = stage_base(W,H,accent,p)
    src_h, src_w = panel_bgra.shape[:2]
    quad=shot_params(mode,p,W,H,(src_w,src_h))
    matrix=cv2.getPerspectiveTransform(np.float32([[0,0],[src_w-1,0],[src_w-1,src_h-1],[0,src_h-1]]),quad)
    layer=cv2.warpPerspective(panel_bgra,matrix,(W,H),flags=cv2.INTER_LINEAR,
                              borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0))
    opacity=layer[:,:,3].astype(np.float32)/255.0
    shadow=cv2.GaussianBlur(opacity,(0,0),sigmaX=20)
    shadow=np.roll(shadow,(12,18),(0,1))*.47
    scene=(scene.astype(np.float32)*(1-shadow[:,:,None])).astype(np.uint8)
    # The frame is physically separated from the wall by a coherent shadow.
    core=layer[:,:,:3][:,:,::-1].astype(np.float32)
    scene=np.uint8(np.clip(scene.astype(np.float32)*(1-opacity[:,:,None])+
                          core*opacity[:,:,None],0,255))
    # Original painting texture remains physically unchanged except for optics.
    # Light swipe is a gallery spotlight, not an alleged historical color restoration.
    if mode == "luminous_reveal":
        x = int(W*(.05 + .9*eased(p)))
        strip = np.exp(-((np.arange(W)-x)/(W*.095))**2).astype(np.float32)
        scene = np.uint8(np.clip(scene.astype(np.float32)+strip[None,:,None]*9,0,255))
    if mode == "depth_portal":
        # Luminous rim is clearly an invented cinematic effect.
        edge=(cv2.Canny(layer[:,:,3],100,240)>0).astype(np.float32)
        halo=cv2.GaussianBlur(edge,(0,0),sigmaX=5)[:, :, None]
        gold=np.array((209,171,98),np.float32)
        scene=np.uint8(np.clip(scene.astype(np.float32)+halo*gold*.25,0,255))
    card=Image.fromarray(scene,"RGB")
    d=ImageDraw.Draw(card)
    d.text((W//2,58),"A R T V I S I O N   ·   W O W   L A B",
           font=font(16),fill=(228,192,129),anchor="mm")
    tl,tf=fit_text(title,W-56,24)
    d.text((W//2, H-143),tl,font=tf,fill=(243,233,209),anchor="mm")
    author,af=fit_text(artist,W-50,18)
    d.text((W//2,H-111),author,font=af,fill=(183,185,184),anchor="mm")
    d.text((W//2,H-83),year[:34],font=font(14),fill=(174,153,130),anchor="mm")
    d.text((W//2,H-42),"VISUAL EXPERIMENT  ·  2.5D",font=font(12),
           fill=(155,153,149),anchor="mm")
    return np.asarray(card, np.uint8)


def original_sound(path: Path, seconds: float, seed: int):
    """Original, procedural ambient soundtrack. No external samples/music."""
    rate=24000
    t=np.arange(int(seconds*rate),dtype=np.float64)/rate
    freqs=(110,164.81,220,329.63,440)
    rng=random.Random(seed)
    score=np.zeros_like(t)
    length=2.2
    for index in range(math.ceil(seconds/length)+1):
        start=index*length
        note=freqs[(index + rng.randrange(3)) % len(freqs)]
        seg=np.maximum(0,t-start)
        window=(seg<length).astype(float)
        env=(1-np.exp(-seg*4))*np.exp(-seg/2.0)*window
        score+=env*(np.sin(2*math.pi*note*seg)*.20+
                   np.sin(2*math.pi*(note*1.5)*seg)*.035)
    score+=.024*np.sin(2*math.pi*55*t)
    fade=np.minimum(1,np.maximum(0,(seconds-t)/1.0))
    score=np.tanh(score*.6)*fade
    pcm=np.int16(np.clip(score,-1,1)*32767)
    with wave.open(str(path),"wb") as wav:
        wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(rate)
        wav.writeframes(pcm.tobytes())


def qa(video: Path, conf: dict, frames: list[np.ndarray]) -> dict:
    details=json.loads(subprocess.check_output(
        ["ffprobe","-v","error","-show_entries",
         "stream=codec_name,codec_type,width,height:format=duration",
         "-of","json",str(video)],text=True))
    streams=details["streams"]
    v=next((x for x in streams if x.get("codec_type")=="video"),None)
    a=next((x for x in streams if x.get("codec_type")=="audio"),None)
    delta0=float(np.mean(cv2.absdiff(frames[0],frames[1])))
    delta1=float(np.mean(cv2.absdiff(frames[1],frames[2])))
    brightness=float(np.mean(frames[1]))
    try:
        subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i",str(video),
                        "-f","null","-"],check=True,capture_output=True,timeout=120)
        decode_ok=True
    except (subprocess.CalledProcessError,subprocess.TimeoutExpired):
        decode_ok=False
    expected=conf["size"]
    passed=bool(v and v.get("codec_name")=="h264" and
                v.get("width")==expected[0] and v.get("height")==expected[1] and
                a and a.get("codec_name")=="aac" and
                video.stat().st_size>conf["quality"]["min_video_bytes"] and
                delta0>1.0 and delta1>1.0 and 12<brightness<230 and decode_ok)
    return {"technical_pass":passed,"codec_video":v.get("codec_name") if v else None,
            "codec_audio":a.get("codec_name") if a else None,
            "length_seconds":float(details["format"]["duration"]),
            "bytes":video.stat().st_size,"frame_differences":[round(delta0,2),round(delta1,2)],
            "mean_brightness":round(brightness,1),"decoded_without_errors":decode_ok,
            "artistic_quality":"needs_human_review",
            "virality":"not_measured",
            "limitations":["perspective is 2.5D, not a 3D mesh", "museum environment is scenic reconstruction",
                           "automated metrics do not assess emotion or facial fidelity"]}


def create_social(out: Path, rec: dict, mode: str):
    title=rec.get("title","Untitled")
    artist=rec.get("artistDisplayName") or "Unknown artist"
    year=rec.get("objectDate") or "Date unknown"
    statements={
        "FACEBOOK.txt":f"{title} — {artist}. Un dettaglio d'arte che diventa spazio. Un piccolo viaggio visivo, non una ricostruzione storica. {year}. Quale particolare ti ha colpito di più? #ArtVision #ArtHistory",
        "INSTAGRAM.txt":f"Una tela. Una prospettiva inattesa. ✨ {title} · {artist}. Immagine originale: The Metropolitan Museum of Art, Open Access (CC0). #ArtVision #MuseumArt",
        "TIKTOK.txt":f"Quando un dipinto sembra avere profondità. {title} — {artist}. Esperimento cinematografico 2.5D con opera autentica. #ArtVision #Art",
        "YOUTUBE.txt":f"{title} | {artist} ({year})\n\nInterpretazione visiva sperimentale 2.5D dell'opera autentica. Non è una mesh tridimensionale né una ripresa reale di museo.\nFonte: {rec.get('objectURL','')} · The Metropolitan Museum of Art, Open Access, CC0.\nEffetto: {mode}.",
    }
    for filename,description in statements.items():
        (out/filename).write_text(description+"\n",encoding="utf-8")


def run(args):
    conf=read_config(ROOT/"config.json")
    if not conf["enabled"]:
        print("WOW_LAB_DISABLED: no production requested")
        return 0
    stamp=slot_id(args.slot)
    label=PREFIX+stamp
    out=Path(args.out).resolve()
    sandbox = (ROOT / "runs").resolve()
    if out == sandbox or sandbox not in out.parents:
        raise ValueError("Output must stay inside wow_lab/runs/<unique-slot>")
    out.mkdir(parents=True,exist_ok=True)
    past=recent_history()
    rec=select_artwork(conf, stamp, past, args.test_source_id)
    source,url,source_sha=save_original(rec,out,conf)
    modes=list(SAFE_MODES)
    latest_modes=[x.get("technique") for x in past[:2]]
    rng=random.Random(stamp+str(rec["objectID"]))
    rng.shuffle(modes)
    modes.sort(key=lambda mode:(mode in latest_modes,mode==latest_modes[0] if latest_modes else False))
    mode=modes[0]
    duration=int(conf["duration_seconds"])+rng.randrange(0,4)
    fps=int(conf["fps"]); W,H=map(int,conf["size"])
    panel=prepare_panel(source,int(W*.85),int(H*.67),mode)
    panel_bgra=cv2.cvtColor(np.asarray(panel),cv2.COLOR_RGBA2BGRA)
    colors=mood_colors(source)
    title=rec["title"];artist=rec.get("artistDisplayName") or "Artist unknown"
    year=rec.get("objectDate") or ""
    original_sound(out/"ORIGINAL_AUDIO.wav",duration,rec["objectID"])
    tmpvideo=out/"WOW_LAB_PREVIEW.mp4"
    cmd=["ffmpeg","-nostdin","-y","-hide_banner","-loglevel","error",
         "-f","rawvideo","-pixel_format","rgb24",
         "-video_size",f"{W}x{H}","-framerate",str(fps),"-i","pipe:0",
         "-i",str(out/"ORIGINAL_AUDIO.wav"),"-c:v","libx264","-preset","veryfast",
         "-crf","23","-pix_fmt","yuv420p","-c:a","aac","-b:a","96k",
         "-movflags","+faststart","-shortest",str(tmpvideo)]
    process=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    samples=[]
    try:
        count=duration*fps
        for idx in range(count):
            p=idx/max(count-1,1)
            frame=draw_video_frame(panel_bgra,W,H,p,mode,colors,title,artist,year)
            if idx in (0, count//2, count-1):
                samples.append(frame.copy())
            process.stdin.write(frame.tobytes())
        process.stdin.close()
        err=process.stderr.read().decode(errors="replace")
        result=process.wait()
        if result:
            raise RuntimeError("FFmpeg render failed: "+err[-900:])
    except Exception:
        process.kill()
        raise
    Image.fromarray(samples[0]).save(out/"OPENING.jpg",quality=89)
    Image.fromarray(samples[1]).save(out/"COVER.jpg",quality=92)
    Image.fromarray(samples[2]).save(out/"ENDING.jpg",quality=89)
    q=qa(tmpvideo,conf,samples)
    report={
        "schema":SCHEMA,"tag":label,"slot_utc":stamp,"group":"WOW_LAB_ISOLATED",
        "status":"needs_human_review" if q["technical_pass"] else "technical_reject",
        "object_id":rec["objectID"],"title":title,"artist":artist,"date":year,
        "museum_url":rec.get("objectURL"),"image_url":url,"source_sha256":source_sha,
        "source_license":"The Metropolitan Museum of Art · Open Access · CC0",
        "is_public_domain":bool(rec["isPublicDomain"]),"commercial_use":True,
        "technique":mode,"reconstructed_3d_mesh":False,
        "audio":"original procedural synthesis","duration_seconds":duration,
        "fps":fps,"size":[W,H],"qa":q,"previous_techniques":latest_modes,
        "artistic_approval":False,"social_publication":False,"paid_api_cost":0,
        "generation_system":"CPU Pillow OpenCV FFmpeg, isolated wow_lab/",
    }
    if not q["technical_pass"]:
        (out/"REJECTED_REPORT.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        print(json.dumps({"status":"technical_reject","qa":q},ensure_ascii=False))
        return 2
    create_social(out,rec,mode)
    (out/"MANIFEST.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (out/"RIGHTS.txt").write_text(
        f"Title: {title}\nArtist: {artist}\nDate: {year}\n"
        f"Source museum: {rec.get('objectURL')}\nSource URL: {url}\n"
        f"Source SHA-256: {source_sha}\nRights: Met Open Access, CC0, verified isPublicDomain=true\n"
        "The virtual gallery is a fictional visualization. This is NOT a genuine 3D reconstruction.\n"
        "Video and soundtrack created independently, no paid third-party API.\n"
        "Result needs artistic review before social publication.\n",encoding="utf-8")
    meta={"schema":SCHEMA,"slot":stamp,"object_id":rec["objectID"],"technique":mode,
          "source_sha256":source_sha,"artistic_approval":False}
    (out/"RELEASE_NOTES.md").write_text(
        f"ArtVision WOW LAB · autonomous visual experiment for **{title}** by {artist}.\n\n"
        f"**Status: needs_human_review**. Preview only, not an approved master or commercial publication.\n\n"
        f"Original source: {rec.get('objectURL')}. Open Access / CC0 verified.\n\n"
        f"Technique: **{mode}**, cinematic 2.5D (NOT true 3D). Standalone experimental engine.\n\n"
        f"Technical QA: H264+AAC, full decode, frame-difference check, SHA256 in MANIFEST.json.\n"
        f"No social autopublication, Vidu, other paid API, or original ArtVision workflow triggered.\n\n"
        "<!-- WOWLAB_META "+json.dumps(meta,ensure_ascii=False,separators=(",",":"))+" -->\n",
        encoding="utf-8")
    (out/"FILES_SHA256.txt").write_text(
        "".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n" for p in sorted(out.iterdir())
                if p.is_file() and p.name!="FILES_SHA256.txt"),encoding="utf-8")
    zipname=out/f"WOW_LAB_ANDROID_{stamp}.zip"
    with zipfile.ZipFile(zipname,"w",zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(out.iterdir()):
            if p.is_file() and p.name not in (zipname.name,"ORIGINAL_AUDIO.wav"):
                z.write(p,p.name)
    with zipfile.ZipFile(zipname) as z:
        if z.testzip():
            raise RuntimeError("ZIP CRC failure")
    print(json.dumps({"tag":label,"status":report["status"],"title":title,"mode":mode,
                      "mp4":str(tmpvideo),"zip":str(zipname),
                      "source":rec.get("objectURL"),"qa":q},ensure_ascii=False))
    return 0


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True)
    p.add_argument("--slot",default=None)
    p.add_argument("--test-source-id",type=int,default=None)
    args=p.parse_args()
    try:
        return run(args)
    except Exception as err:
        print(f"WOW_LAB_FAIL_CLOSED: {err}",file=sys.stderr)
        return 1


if __name__=="__main__":
    raise SystemExit(main())
