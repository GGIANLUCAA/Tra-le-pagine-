#!/usr/bin/env python3
"""V240: five original 9:16 source crops for artistic review; no I2I or Vidu."""
import argparse, hashlib, json, re
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw

def make_sheet(selection_path, frames_dir, output_dir):
    selection=json.loads(Path(selection_path).read_text(encoding="utf-8"))
    if selection.get("status")!="FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW":
        raise ValueError("SOURCE_SELECTION_NOT_READY")
    rows=selection.get("preselected")
    if not isinstance(rows,list) or len(rows)!=5 or any(not isinstance(r,dict) for r in rows):
        raise ValueError("FIVE_FRAMES_REQUIRED")
    names=[r.get("filename") for r in rows]
    if len(set(names))!=5: raise ValueError("DUPLICATE_FRAMES")
    sheet=Image.new("RGB",(1440,600),"#202020")
    draw=ImageDraw.Draw(sheet)
    evidence=[]
    for i,name in enumerate(names):
        if not isinstance(name,str) or not re.fullmatch(r"frame_\d{2}\.png",name):
            raise ValueError("UNSAFE_FRAME_NAME")
        frame=Path(frames_dir)/name
        if frame.is_symlink() or not frame.is_file(): raise ValueError("MISSING_SOURCE_FRAME")
        with Image.open(frame) as im:
            if im.format!="PNG" or min(im.size)<240: raise ValueError("INVALID_SOURCE")
            crop=ImageOps.fit(im.convert("RGB"),(270,480),method=Image.Resampling.LANCZOS)
            dimensions=list(im.size)
        sheet.paste(crop,(i*288+9,55))
        draw.text((i*288+9,20),f"{i+1}. {name}",fill="white")
        draw.text((i*288+9,550),f"{dimensions[0]}x{dimensions[1]} source",fill="white")
        evidence.append({"filename":name,"source_sha256":hashlib.sha256(frame.read_bytes()).hexdigest(),
                         "native_raster":dimensions,"i2i_generated":False,"artistically_approved":False})
    out=Path(output_dir)
    out.mkdir(parents=True,exist_ok=True)
    sheet.save(out/"FIVE_PORTRAIT_SOURCE_CROPS_V240.jpg",quality=93)
    (out/"FIVE_PORTRAIT_SOURCE_CROPS_V240.json").write_text(json.dumps({
        "status":"SOURCE_CROPS_ONLY_NOT_FINAL","frames":evidence,
        "rights_approved":False,"vidu_generated":False},indent=2)+"\n",encoding="utf-8")
    return evidence

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--selection",required=True)
    p.add_argument("--frames",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    print("V240_SOURCE_CROPS_READY",len(make_sheet(a.selection,a.frames,a.out)))
