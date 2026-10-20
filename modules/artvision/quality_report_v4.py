#!/usr/bin/env python3
"""Make a director-facing visual contact sheet and non-subjective media QA from a finished ArtVision V4."""
import argparse,json,subprocess,collections
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps

def ff(*args):
    x=subprocess.run(["ffprobe","-v","error",*args],capture_output=True,text=True,check=True)
    return x.stdout

def grab(path,seconds,width=190,height=338):
    command=["ffmpeg","-hide_banner","-loglevel","error","-ss",f"{seconds:.3f}","-i",str(path),
             "-frames:v","1","-vf",f"scale={width}:{height}:flags=lanczos",
             "-f","image2pipe","-vcodec","mjpeg","-"]
    p=subprocess.run(command,capture_output=True)
    if p.returncode:raise RuntimeError(p.stderr.decode(errors="ignore")[-500:])
    from io import BytesIO
    return Image.open(BytesIO(p.stdout)).convert("RGB")

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--out",default="output/artvision")
    args=a.parse_args()
    out=Path(args.out)
    video=out/"ARTVISION_VIDEO.mp4"
    storyboard=json.loads((out/"STORYBOARD_REGIA.json").read_text(encoding="utf8"))
    metadata=json.loads((out/"OPERE_FONTI_E_DIRITTI.json").read_text(encoding="utf8"))
    music=json.loads((out/"MUSICA_LICENZA_E_CREDITI.json").read_text(encoding="utf8"))
    technical=json.loads(ff("-show_entries","format=duration,size:stream=codec_type,codec_name,width,height","-of","json",str(video)))
    video_stream=next(x for x in technical["streams"] if x["codec_type"]=="video")
    assert video_stream["width"]==1080 and video_stream["height"]==1920,"V4 expected Full HD vertical"
    assert video_stream["codec_name"]=="h264","H264 output required"
    assert any(x["codec_type"]=="audio" for x in technical["streams"]),"Audio missing"
    assert len(storyboard)>=9,"Too few curated artworks"
    counts=collections.Counter(part["kind"] for scene in storyboard for part in scene["parts"])
    assert counts["whole"]>=8 and counts["detail"]>=8, "Missing variety of details and complete artworks"
    assert any(s["parts"][0]["kind"]=="whole" for s in storyboard) and any(s["parts"][0]["kind"]=="detail" for s in storyboard)
    assert sum(sum(p["kind"]=="detail" for p in scene["parts"])>=3 for scene in storyboard)>=2
    sheet=Image.new("RGB",(4*212, len(storyboard)*382),(15,17,20))
    d=ImageDraw.Draw(sheet)
    font="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    f=ImageFont.truetype(font,13)
    for j,scene in enumerate(storyboard):
        spans=scene["parts"]
        indices=sorted(set([0,len(spans)//2,len(spans)-1]))
        ts=[];at=scene["start"]
        for part in spans:
            ts.append((at+part["duration"]*.48,part["kind"]))
            at+=part["duration"]
        for k,i in enumerate(indices):
            seconds,kind=ts[i]
            shot=grab(video,seconds)
            x=k*212+10;y=j*382+11
            sheet.paste(shot,(x,y))
            d.text((x,y+341),f"{seconds:.1f}s · {kind}",font=f,fill=(242,239,224))
        x=3*212+8;y=j*382+20
        title=scene["title"]
        pieces=[title[i:i+22] for i in range(0,min(len(title),90),22)]
        for k,line in enumerate(pieces):d.text((x,y+k*18),line,font=f,fill=(236,232,218))
        d.text((x,y+118),"+".join(p["kind"] for p in spans),font=f,fill=(180,193,193))
    sheet.save(out/"CONTATTO_REGIA_V4.jpg",quality=87,optimize=True)
    summary={
      "status":"technical_pass; aesthetics_require_editorial_review",
      "dimensions":[video_stream["width"],video_stream["height"]],
      "runtime":float(technical["format"]["duration"]),
      "artworks":len(storyboard),"shots":sum(counts.values()),
      "shot_mode_counts":dict(counts),
      "multi_detail_artworks":sum(sum(p["kind"]=="detail" for p in s["parts"])>=2 for s in storyboard),
      "3_detail_artworks":sum(sum(p["kind"]=="detail" for p in s["parts"])>=3 for s in storyboard),
      "whole_first_artworks":sum(s["parts"][0]["kind"]=="whole" for s in storyboard),
      "music":music["title"],"author":music["author"],"license":music["license"],
      "rights_record_count":len(metadata["works"]),
      "review_notes":"Visually inspect contact sheet for real subject focus, color fidelity, legibility of credit and transitions. Passing this script does not prove artistic quality."
    }
    (out/"CONTROLLO_ATELIER_V4.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf8")
    print("ATELIER V4 QA",json.dumps(summary,ensure_ascii=False))

if __name__=="__main__":main()
