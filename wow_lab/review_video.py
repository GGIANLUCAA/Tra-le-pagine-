"""WOW LAB independent post-render QA. Never publishes or grants artistic approval.

Usage: python wow_lab/review_video.py wow_lab/runs/SLOT/WOW_LAB_PREVIEW.mp4
Outputs next to video: VIDEO_REVIEW.json and VIDEO_CONTACT_SHEET.jpg.
"""
from __future__ import annotations
import argparse
import json
import subprocess
from pathlib import Path
import cv2
from PIL import Image, ImageDraw

def review(video: Path) -> dict:
    video=video.resolve()
    if not video.is_file() or video.stat().st_size == 0:
        raise ValueError("missing_or_empty_video")
    root=Path(__file__).resolve().parent
    if root not in video.parents or (root/"runs") not in video.parents:
        raise ValueError("video_must_be_inside_wow_lab_runs")
    probe=json.loads(subprocess.check_output([
        "ffprobe","-v","error","-show_streams","-show_format",
        "-of","json",str(video)],text=True,timeout=30))
    streams=probe.get("streams",[])
    v=next((s for s in streams if s.get("codec_type")=="video"),None)
    a=next((s for s in streams if s.get("codec_type")=="audio"),None)
    duration=float(probe.get("format",{}).get("duration",0))
    decode=subprocess.run(["ffmpeg","-nostdin","-v","error","-xerror",
                           "-i",str(video),"-f","null","-"],
                          capture_output=True,text=True,timeout=180)
    capture=cv2.VideoCapture(str(video))
    if not capture.isOpened():
        raise RuntimeError("cannot_open_video_frames")
    fps=capture.get(cv2.CAP_PROP_FPS)
    count=capture.get(cv2.CAP_PROP_FRAME_COUNT)
    target=[.02,.14,.28,.42,.56,.70,.84,.97]
    stills=[]
    for fraction in target:
        capture.set(cv2.CAP_PROP_POS_MSEC, max(0,duration*fraction*1000))
        ok,frame=capture.read()
        if not ok:
            stills.append(None)
            continue
        rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        stills.append(Image.fromarray(rgb))
    capture.release()
    thumb_w,thumb_h=270,480
    sheet=Image.new("RGB",(thumb_w*4, (thumb_h+42)*2),(22,22,22))
    draw=ImageDraw.Draw(sheet)
    for idx,still in enumerate(stills):
        x=(idx%4)*thumb_w
        y=(idx//4)*(thumb_h+42)
        if still is not None:
            still.thumbnail((thumb_w,thumb_h))
            sheet.paste(still,(x+(thumb_w-still.width)//2,y))
        draw.text((x+8,y+thumb_h+8),f"{target[idx]*100:.0f}% / {duration*target[idx]:.1f}s",fill="white")
    sheet.save(video.parent/"VIDEO_CONTACT_SHEET.jpg",quality=90)
    passed=bool(v and a and v.get("codec_name")=="h264"
                and a.get("codec_name")=="aac"
                and duration>=8 and decode.returncode==0
                and all(frame is not None for frame in stills))
    result={
        "technical_pass":passed,
        "video_codec":v.get("codec_name") if v else None,
        "audio_codec":a.get("codec_name") if a else None,
        "duration_seconds":duration,
        "fps":fps,"frame_count":count,
        "full_decode_pass":decode.returncode==0,
        "decode_errors":decode.stderr[-2000:],
        "sampled_frames":len([f for f in stills if f is not None]),
        "contact_sheet":"VIDEO_CONTACT_SHEET.jpg",
        "mask_semantics_verified":False,
        "artistic_approval":False,
        "publishable_master":False,
        "required_manual_review":[
            "mask matches one complete authentic subject without background",
            "opening and final composition visually coherent",
            "subject crosses frame with credible shadow and parallax",
            "compare with last six WOW LAB subjects and previous failures"],
    }
    (video.parent/"VIDEO_REVIEW.json").write_text(
        json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return result

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("video",type=Path)
    args=parser.parse_args()
    result=review(args.video)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(0 if result["technical_pass"] else 2)
