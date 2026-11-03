#!/usr/bin/env python3
"""V251: export actual SHA-bound Fiesole frames for the next four real I2I.
Produces an offline, reviewable photo-input ZIP and fifth Vidu reference.
No generation, no approvals, no paid calls, no finished video.
"""
from __future__ import annotations
import argparse,hashlib,io,json,zipfile
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
from storia_rivive_v249_fiesole_short_motion_selection import FILM_SHA,sha

def export(selection:Path,alignment:Path,frames:Path,out:Path)->dict:
    s=json.loads(selection.read_text())
    checks=json.loads(alignment.read_text()).get("checks")
    rows=s.get("preselected")
    times=s.get("candidate_segment_times_s")
    if (s.get("status")!="FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW"
        or not all(isinstance(v,list) and len(v)==5 for v in (checks,rows,times))):
        raise ValueError("FIVE_REAL_V249_SOURCE_SHOTS_REQUIRED")
    out.mkdir(parents=True,exist_ok=True)
    manifest={"version":"V251_FIESOLE_SOURCE_LOCKED_PHOTO_HANDOFF",
      "source_film_sha256":FILM_SHA,"episode":"fiesole_straw_hats_1912_v220",
      "status":"SOURCE_FRAMES_FOR_FOUR_I2I_AND_ONE_VIDU_NOT_FINAL",
      "four_i2i_real_outputs":0,"vidu_real_outputs":0,
      "italian_rights_approved":False,"artistic_approval":False,
      "publish_allowed":False,"new_final_episodes_delivered":0,"shots":[]}
    names=set()
    sheet=Image.new("RGB",(1500,5*400),"#181818")
    d=ImageDraw.Draw(sheet)
    payload=[]
    for i,(row,t,check) in enumerate(zip(rows,times,checks),1):
        name=row.get("filename")
        if not isinstance(name,str) or name in names or "/" in name or "\\" in name:
            raise ValueError("DUPLICATE_OR_UNSAFE_FRAME_NAME")
        names.add(name)
        p=frames/name
        if p.is_symlink() or not p.is_file() or sha(p)!=check.get("source_frame_sha256"):
            raise ValueError("SOURCE_IMAGE_HASH_MISMATCH")
        if name!=check.get("source_frame") or abs(float(t)-float(check.get("selected_timecode_s",-1)))>.002:
            raise ValueError("SOURCE_FRAME_TIMECODE_MISMATCH")
        if check.get("endpoint_visually_aligned") is not True:
            raise ValueError("SOURCE_ENDPOINT_NOT_ALIGNED")
        with Image.open(p) as img:
            if img.format!="PNG" or min(img.size)<720:raise ValueError("LOW_QUALITY_SOURCE_IMAGE")
            picture=ImageOps.contain(img.convert("RGB"),(1100,380))
            sheet.paste(picture,(380+(1100-picture.width)//2, i*400-400+(380-picture.height)//2))
            d.text((18,(i-1)*400+45),f"SHOT {i}: "+("I2I" if i<5 else "VIDU"),fill="white")
            d.text((18,(i-1)*400+75),f"t={float(t):.3f}s",fill="white")
            d.text((18,(i-1)*400+105),name,fill="white")
        entry=f"original_shot_{i:02d}_{name}"
        payload.append((entry,p.read_bytes()))
        manifest["shots"].append({"shot":i,"role":"I2I_PHOTO_SOURCE" if i<5 else "VIDU_SOURCE_FRAME",
          "archive_filename":entry,"original_frame":name,"original_sha256":sha(p),
          "source_time_s":float(t),"source_frame_locked":True,
          "actual_i2i_generated":False,"actual_vidu_generated":False})
    buf=io.BytesIO()
    sheet.save(buf,format="PNG")
    payload.append(("FIESOLE_V251_FIVE_SHOT_REVIEW_CONTACT_SHEET.png",buf.getvalue()))
    payload.append(("V251_SOURCE_MANIFEST_NOT_FINAL.json",json.dumps(manifest,indent=2).encode()))
    zip_path=out/"FIESOLE_V251_FIVE_AUTHENTIC_SOURCE_FRAMES_NOT_FINAL.zip"
    with zipfile.ZipFile(zip_path,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for name,data in payload:z.writestr(name,data)
    with zipfile.ZipFile(zip_path) as z:
        if z.testzip() is not None:raise ValueError("ZIP_CORRUPTED")
        if len(z.namelist())!=7:raise ValueError("ZIP_ENTRY_COUNT_WRONG")
    (out/"V251_SOURCE_MANIFEST_NOT_FINAL.json").write_text(json.dumps(manifest,indent=2)+"\n")
    (out/"FIESOLE_V251_FIVE_SHOT_REVIEW_CONTACT_SHEET.png").write_bytes(buf.getvalue())
    return manifest

if __name__=="__main__":
    a=argparse.ArgumentParser()
    for name in ("selection","alignment","frames","out"):a.add_argument("--"+name,type=Path,required=True)
    args=a.parse_args()
    result=export(args.selection,args.alignment,args.frames,args.out)
    print(result["status"],"SHOTS",len(result["shots"]),"FINAL_0_OF_4")
