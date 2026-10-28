#!/usr/bin/env python3
"""V61: real black/white moving archive -> freeze -> color AI photo -> hold -> next shot.

This compositor DOES NOT generate AI photos. It needs real image-to-image restored
still files, exact archive timecodes, rights and QA checks. Test-only files can be
synthetic; the output is explicitly not eligible for final release.
"""
import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path

import cv2
import numpy as np

ALLOWED_SOURCE_LICENSES = {"CC0", "CC0 1.0", "PUBLIC_DOMAIN", "PDM"}
ALLOWED_RESOLUTIONS = {(360, 640), (720, 1280), (1080, 1920)}


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def dimensions(filepath):
    im = cv2.imread(str(filepath))
    return im.shape[1::-1] if im is not None else (0, 0)


def validate(plan):
    errors = []
    def require(condition, message):
        if not condition:
            errors.append(message)
    width, height, fps = plan.get("width"), plan.get("height"), plan.get("fps", 30)
    test = plan.get("test_only") is True
    require((width, height) in ALLOWED_RESOLUTIONS, "Risoluzione verticale non consentita")
    require((width, height) != (360, 640) or test, "360x640 solo test tecnico")
    require(fps == 30, "V61 30fps fissati come nei riferimenti finche' non si testa altra frequenza")
    require(not plan.get("social_autopublish"), "Autopubblicazione vietata")
    require(not plan.get("allow_paid_generation"), "Spese e crediti non autorizzati nel montatore")
    shots = plan.get("shots", [])
    require(isinstance(shots, list) and 1 <= len(shots) <= 12, "Servono 1-12 scene reali diverse")
    total = 0.0
    source_ranges = {}
    if not isinstance(shots, list):
        shots = []
    for i, s in enumerate(shots):
        label = "Scena %d: " % (i + 1)
        video, photo = s.get("archive_video"), s.get("ai_photo")
        require(video and Path(video).is_file(), label + "video B/N originale mancante")
        require(photo and Path(photo).is_file(), label + "fotografia a colori AI mancante")
        license_name = s.get("archive_license", "")
        require(license_name in ALLOWED_SOURCE_LICENSES, label + "originale non CC0/PD")
        require(bool(s.get("source_page", "").startswith("https://")),
                label + "pagina fonte mancante")
        require(s.get("rights_checked") is True, label + "diritti non verificati")
        if license_name in ("PUBLIC_DOMAIN", "PDM"):
            require(s.get("jurisdiction_reviewed") is True,
                    label + "status PD non verificato in Italia e paese originale")
        for key, low, high in (("start_s", 0, 7200), ("motion_s", .4, 15),
                               ("transition_s", .12, .95), ("photo_hold_s", .5, 6)):
            value = s.get(key)
            require(isinstance(value, (int, float)) and low <= value <= high,
                    label + key + " fuori intervallo")
        if all(isinstance(s.get(key), (int, float))
               for key in ("motion_s", "transition_s", "photo_hold_s")):
            total += s["motion_s"] + s["transition_s"] + s["photo_hold_s"]
        require(s.get("framing") in ("contain", "reviewed_safe_crop"),
                label + "scelta inquadratura non valida")
        require(s.get("crop_faces_reviewed") is True,
                label + "visibilita' persone/crop non revisionata")
        if not test:
            require(s.get("photo_generated_with_ai") is True,
                    label + "fotografia non ricostruita con AI")
            require(len(str(s.get("ai_model", ""))) > 3,
                    label + "modello AI della fotografia assente")
            require(len(str(s.get("ai_photo_prompt_or_recipe", ""))) > 15,
                    label + "ricetta foto AI assente")
            require(s.get("same_people_pose_objects_reviewed") is True,
                    label + "persone/pose/oggetti non confrontati con fotogramma")
            require(s.get("photo_visual_approved") is True,
                    label + "risultato fotografico non approvato")
            require(s.get("source_frame_timecode_reviewed") is True,
                    label + "fotogramma origine e tempo non verificati")
            require(s.get("photo_historical_reconstruction_disclosed") is True,
                    label + "ricostruzione AI non dichiarata")
            if photo and Path(photo).is_file():
                w, h = dimensions(photo)
                require(w >= width and h >= height,
                        label + "fotografia AI sotto risoluzione export (no fake upscale)")
                require(s.get("ai_photo_sha256") == sha256(photo),
                        label + "SHA256 foto AI discordante")
            if video and Path(video).is_file():
                require(s.get("source_video_sha256") == sha256(video),
                        label + "SHA256 video archivio discordante")
        if video and Path(video).is_file():
            cap = cv2.VideoCapture(str(video))
            if cap.isOpened():
                fr, count = cap.get(cv2.CAP_PROP_FPS), cap.get(cv2.CAP_PROP_FRAME_COUNT)
                duration = count/fr if fr else 0
                if isinstance(s.get("start_s"), (int, float)) and isinstance(s.get("motion_s"), (int, float)):
                    require(s["start_s"]+s["motion_s"] <= duration-.04,
                            label + "clip oltre la durata originale")
                cap.release()
            else:
                require(False, label + "clip non decodificabile")
        # Prevent reusing same historical shot under a new title to fill the montage.
        key = str(video or "")
        if isinstance(s.get("start_s"), (int, float)) and isinstance(s.get("motion_s"), (int, float)):
            start, end = s["start_s"], s["start_s"] + s["motion_s"]
            for prior_start, prior_end in source_ranges.get(key, []):
                require(end <= prior_start or start >= prior_end,
                        label + "tempo sorgente sovrapposto a clip precedente")
            source_ranges.setdefault(key, []).append((start, end))
    require(.5 < total <= 60, "Durata totale non idonea")
    audio=plan.get("audio") or {}
    if audio.get("music_file"):
        require(Path(audio["music_file"]).is_file() and audio.get("rights_checked") is True,
                "Audio non disponibile o diritti musicali non verificati")
    return errors, round(total, 3)


def fit(frame, target_w, target_h, framing):
    h, w = frame.shape[:2]
    if framing == "reviewed_safe_crop":
        scale = max(target_w/w, target_h/h)
        resized=cv2.resize(frame,(math.ceil(w*scale),math.ceil(h*scale)),
                           interpolation=cv2.INTER_CUBIC)
        rh,rw=resized.shape[:2]
        x=(rw-target_w)//2; y=(rh-target_h)//2
        return resized[y:y+target_h,x:x+target_w].copy()
    scale=min(target_w/w,target_h/h)
    resized=cv2.resize(frame,(round(w*scale),round(h*scale)),interpolation=cv2.INTER_AREA)
    output=np.zeros((target_h,target_w,3),dtype=np.uint8)
    rh,rw=resized.shape[:2]
    x=(target_w-rw)//2;y=(target_h-rh)//2
    output[y:y+rh,x:x+rw]=resized
    return output


def read_motion(s, fps, width, height):
    cap=cv2.VideoCapture(str(s["archive_video"]))
    cap.set(cv2.CAP_PROP_POS_MSEC,float(s["start_s"])*1000)
    n=max(1,round(s["motion_s"]*fps))
    source_fps=cap.get(cv2.CAP_PROP_FPS)
    if source_fps < 1:
        cap.release()
        raise ValueError("FPS originale assente")
    frames=[]
    for i in range(n):
        # Seeking by timestamp matters when source fps is not 30.
        cap.set(cv2.CAP_PROP_POS_MSEC,(s["start_s"]+i/fps)*1000)
        ok,frame=cap.read()
        if not ok:
            break
        gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        gray_bgr=cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR)
        frames.append(fit(gray_bgr,width,height,s["framing"]))
    cap.release()
    if len(frames) != n:
        raise ValueError("B/N incompleto: attesi %d, ottenuti %d frame" % (n,len(frames)))
    return frames


def photo_frames(s, freeze, fps, width, height):
    still=cv2.imread(str(s["ai_photo"]),cv2.IMREAD_COLOR)
    if still is None:
        raise ValueError("Foto AI non decodificabile")
    still=fit(still,width,height,s["framing"])
    # Simple frame-to-photo transformation; matching geometry must be reviewed.
    ntransition=max(1,round(s["transition_s"]*fps))
    nhold=max(1,round(s["photo_hold_s"]*fps))
    for i in range(ntransition):
        a=(i+1)/ntransition
        smooth=a*a*(3-2*a)
        yield cv2.addWeighted(freeze,1-smooth,still,smooth,0)
    zoom=float(s.get("virtual_photo_zoom", 0))
    if not 0 <= zoom <= .012:
        raise ValueError("Zoom virtuale massimo 1.2%, nessuna fake animazione")
    for i in range(nhold):
        if zoom == 0:
            yield still
        else:
            f=i/max(nhold-1,1)
            fac=1+zoom*f
            resized=cv2.resize(still,(math.ceil(width*fac),math.ceil(height*fac)))
            yy=(resized.shape[0]-height)//2;xx=(resized.shape[1]-width)//2
            yield resized[yy:yy+height,xx:xx+width]


def render(plan, outfile):
    errors,duration=validate(plan)
    if errors:raise ValueError("\n".join(errors))
    out=Path(outfile)
    if out.exists():raise ValueError("Non sovrascrivere master precedente")
    out.parent.mkdir(parents=True,exist_ok=True)
    width,height,fps=plan["width"],plan["height"],plan.get("fps",30)
    raw=out.with_suffix(".video_only.mp4")
    process=subprocess.Popen(["ffmpeg","-nostdin","-y","-hide_banner","-loglevel","error",
          "-f","rawvideo","-pix_fmt","bgr24","-s",f"{width}x{height}","-r",str(fps),
          "-i","-","-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt",
          "yuv420p",str(raw)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    scenes=[]
    total_frames=0
    try:
        for i,s in enumerate(plan["shots"]):
            motion=read_motion(s,fps,width,height)
            for frame in motion:
                process.stdin.write(frame.tobytes());total_frames+=1
            frozen=motion[-1]
            tframes=round(s["transition_s"]*fps)
            hframes=round(s["photo_hold_s"]*fps)
            for frame in photo_frames(s,frozen,fps,width,height):
                process.stdin.write(frame.tobytes());total_frames+=1
            scenes.append({"index":i+1,"archive_source":s["source_page"],
                           "ai_photo":str(s["ai_photo"]), "motion_frames":len(motion),
                           "transition_frames":tframes,"hold_frames":hframes,
                           "real_ai_photo":not plan.get("test_only",False)})
    finally:
        process.stdin.close()
    msg=process.stderr.read().decode(errors="ignore")
    if process.wait()!=0:
        raise RuntimeError("ffmpeg render: "+msg[-600:])
    audio=plan.get("audio") or {}
    if audio.get("music_file"):
        aud=["-stream_loop","-1","-i",str(audio["music_file"])]
    else:
        aud=["-f","lavfi","-i","anullsrc=channel_layout=stereo:sample_rate=44100"]
    proc=subprocess.run(["ffmpeg","-nostdin","-y","-loglevel","error","-i",str(raw)]
        +aud+["-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a",
             "128k","-t",str(total_frames/fps),"-movflags","+faststart",str(out)],
        capture_output=True,timeout=120)
    raw.unlink(missing_ok=True)
    if proc.returncode:
        raise RuntimeError("ffmpeg mux: "+proc.stderr.decode(errors="ignore")[-600:])
    decoded=subprocess.run(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(out),"-f","null","-"],
                           capture_output=True,timeout=120)
    if decoded.returncode:
        raise RuntimeError("Output non decodificabile")
    qa={"format":"storia_rivive_photo_freeze_v61","test_only":plan.get("test_only") is True,
        "output":str(out),"sha256":sha256(out),"duration_s":round(total_frames/fps,3),
        "no_generative_inference_in_compositor":True,"scenes":scenes,
        "quality_status":"TEST_ONLY_NO_AI" if plan.get("test_only") else "PENDING_HUMAN_ARTISTIC_REVIEW_AND_V55",
        "site_uploaded":False,"no_vidu_spend":True}
    Path(str(out)+".qa.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    return qa


def main():
    p=argparse.ArgumentParser(description="V61 archive motion -> frozen AI photo")
    p.add_argument("--plan",required=True)
    p.add_argument("--check",action="store_true")
    p.add_argument("--out")
    a=p.parse_args()
    plan=json.loads(Path(a.plan).read_text(encoding="utf8"))
    errors,total=validate(plan)
    if errors:
        print(json.dumps({"ok":False,"errors":errors},ensure_ascii=False,indent=2))
        return 2
    if a.check:
        print(json.dumps({"ok":True,"duration":total}))
        return 0
    if not a.out:p.error("--out required for render")
    print(json.dumps(render(plan,a.out),ensure_ascii=False,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
