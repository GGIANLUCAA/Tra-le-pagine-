#!/usr/bin/env python3
"""V278 Delhi 1910: four REAL DDColor->Finegrain I2I shots, identical to V98.

DDColor is a neural color BASE only; final photos must come from new Finegrain
/process calls to the free public ZeroGPU Space. Source frames are four exact
V272 SHA-locked originals. Scene 5 remains reserved for source-matched Vidu,
not faked. One attempt per scene, never auto-retry ambiguous provider tasks.
No paid Vidu, social publication, rights or artistic approval.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageEnhance

FILM_SHA="0a0de7b032cdb19e34d4dac5a6efca02dfa4b00260411aa82290c54b2899f278"
PAGE="https://commons.wikimedia.org/wiki/File:Ruins_of_Delhi_(1910).webm"
EPISODE="delhi_ruins_1910_v217"
SHOTS=[
    (1,"frame_01.png","1b6464e8566ba5c292b59f4d5aa1c3f01de767f0feb58f0ad5cd10de744157fc",
     "The authentic Delhi 1910 road, riders and animals walking below tall trees. Existing people and horses and the exact wooded road remain unchanged."),
    (2,"frame_04.png","8771b50f5a26b3e27eadf00ad085f998bfe2d552daa7f8492027a4c40c6c2a71",
     "A 1910 Delhi bridge seen along its intricate iron lattice, with the real man riding the existing pack animal. Keep bridge, animal anatomy, rider, original proportions and perspective."),
    (3,"frame_06.png","d6a6f21789093f971cff0adfa4259511a24875eb73753b8c7f177b882762f16e",
     "Real carved sandstone columns and ruins of Delhi India in 1910, existing people passing by in period garments; preserve ancient architecture, faces, original number of people."),
    (4,"frame_11.png","05e8e7d2c0134ecb4c9f31dbc469c31fc68981379513aa3bdb85694bc4d0a0f6",
     "Workers in traditional clothing amid real Delhi 1910 stone ruins, original work tools and architecture, believable natural cloth and natural stone textures; preserve exact figures and hands.")
]
VIDU_ANCHOR=(5,"frame_12.png","28a71dff0d65a4529a946fbe1d531626c70dca389d344e4d17f7646022fc8ca2")
PROMPT=(
    "High-quality modern documentary COLOR PHOTOGRAPH restored from exactly "
    "the same historical 1910 Delhi India camera frame. Preserve each existing "
    "person, animal, carved stone, garment, hand, limb, object and camera angle "
    "in the source without hallucinations. Natural period-consistent colors, "
    "clear fine photographic texture, authentic stone/beige, blue sky, natural "
    "green foliage, sunlit light, realistic skin and woven cloth. "
    "No orange sepia tint, no painting, no invented architecture. Scene: "
)
NEG="new people, new animals, changed architecture, extra hands, missing fingers, face swap, modern clothes, plastic face, lettering, stylized illustration, vivid orange monochrome, dark sepia, fake historical objects"
MODEL="finegrain/finegrain-image-enhancer"
REPORT="V278_DELHI_FOUR_REAL_I2I_QA_NOT_FINAL.json"

def digest(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1<<20),b""):h.update(block)
    return h.hexdigest()

def verify_sources(source_dir:Path,scout:Path,selection:Path)->dict:
    metadata=json.loads(scout.read_text(encoding="utf-8"))
    chosen=json.loads(selection.read_text(encoding="utf-8"))
    if (metadata.get("status")!="REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW"
        or metadata.get("source_page")!=PAGE
        or metadata.get("original_sha256")!=FILM_SHA
        or chosen.get("status")!="FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW"
        or chosen.get("approved_restored_photos")!=0
        or chosen.get("publish_permitted") is not False
        or [x.get("filename") for x in chosen.get("preselected",[])]!=[s[1] for s in SHOTS]+[VIDU_ANCHOR[1]]):
        raise ValueError("V278_WRONG_ARCHIVAL_FILM_OR_SELECTION")
    import PIL
    for _,name,expected,*_ in [*SHOTS,VIDU_ANCHOR]:
        path=source_dir/name
        if not path.is_file() or path.is_symlink() or digest(path)!=expected:
            raise ValueError("V278_ARCHIVAL_FRAME_SHA_CHANGED_"+name)
        with Image.open(path) as im:
            if im.format!="PNG" or im.size!=(1920,1080):
                raise ValueError("V278_INVALID_ORIGINAL_FRAME_DIMENSIONS")
            im.verify()
    return {"original_film_sha256":FILM_SHA,"verified_unique_frames":5,
            "source_and_reserved_vidu_original_shas":[s[2] for s in SHOTS]+[VIDU_ANCHOR[2]]}

def ddcolor_base(source:Path,dest:Path,dd,session)->None:
    import cv2,numpy as np
    native=cv2.imread(str(source))
    if native is None or native.shape[:2]!=(1080,1920):
        raise ValueError("V278_SOURCE_FRAME_NOT_DECODABLE")
    reduced=cv2.resize(native,(720,576),interpolation=cv2.INTER_AREA)
    ab_small=dd.infer_ab(session,reduced)
    lab_l=dd.l_channel(native)
    ab=cv2.resize(ab_small,(1920,1080),interpolation=cv2.INTER_CUBIC)
    img=np.clip(cv2.cvtColor(np.dstack((lab_l,np.clip(ab*1.09,-110,110))).astype(np.float32),cv2.COLOR_LAB2RGB)*255,0,255).astype(np.uint8)
    # 9:16 exact center crop (608 original pixels) used by source V272.
    portrait=Image.fromarray(img[:,656:1264]).resize((540,960),Image.Resampling.LANCZOS)
    portrait=ImageEnhance.Color(portrait).enhance(.90)
    portrait.save(dest,format="PNG")

def genuine_finegrain(base:Path,prompt:str,seed:int)->Path:
    from gradio_client import Client,handle_file
    client=Client(MODEL,verbose=False)
    raw=client.predict(handle_file(str(base)),prompt,NEG,
                       seed,2,1.21,.97,6,112,144,.55,18,"DDIM",
                       api_name="/process")
    item=raw[1] if isinstance(raw,(list,tuple)) and len(raw)>1 else raw
    if isinstance(item,dict):item=item.get("path")
    item=Path(str(item))
    if not item.is_file():raise ValueError("V278_FINEGRAIN_NO_OUTPUT")
    return item

def photo_stats(source:Path,photo:Path)->dict:
    import cv2,numpy as np
    with Image.open(source) as i,Image.open(photo) as o:
        g0=np.asarray(ImageOps.grayscale(ImageOps.fit(i,(90,160)))).astype("float32").reshape(-1)
        g1=np.asarray(ImageOps.grayscale(ImageOps.fit(o,(90,160)))).astype("float32").reshape(-1)
        correlation=float(np.corrcoef(g0,g1)[0,1])
        saturation=float(np.asarray(o.convert("HSV"))[:,:,1].mean())
    return {"real_i2i_sha256":digest(photo),"real_i2i_pixel_size":[720,1280],
            "source_geometry_corr":round(correlation,4),
            "saturation_mean":round(saturation,2),
            "auto_preflight_passed":bool(correlation>=.86 and 18<saturation<175)}

def run(original:Path,scout:Path,selection:Path,out:Path,offline=False,
        model_predict=None,make_base=None)->dict:
    verified=verify_sources(original,scout,selection)
    out.mkdir(parents=True,exist_ok=True)
    report={"version":"V278_FOUR_AUTHENTIC_DELHI_FINEGRAIN_PHOTOS_NOT_FINAL",
        "episode":EPISODE,"source_identity":verified,
        "provider":MODEL,"method":"DDColor ONNX base then actual Finegrain image-to-image",
        "real_photo_files":[],"finegrain_provider_attempts":0,
        "accepted_i2i_count":0,"vidu_scene5_generated":False,
        "vidu_credits_used":0,"italian_rights_verified":False,
        "artistic_approval":False,"final_mp4":False,"final_zip":False,
        "new_final_episodes_delivered":0,"publish_allowed":False,
        "status":"SOURCE_LOCKED_FOUR_PHOTOS_PENDING"}
    rp=out/REPORT
    rp.write_text(json.dumps(report,indent=2)+"\n")
    if offline:return report
    dd=None;session=None
    try:
        if make_base is None:
            import storia_rivive_real_ai_v60 as dd
            session,model_meta=dd.download_model()
            report["ddcolor_model"]=model_meta
        for idx,name,expected,scene in SHOTS:
            src=original/name
            base=out/f"DELHI_SHOT_{idx:02d}_DDCOLOR_BASE_NOT_FINAL.png"
            dest=out/f"DELHI_SHOT_{idx:02d}_FINEGRAIN_REAL_I2I_NOT_APPROVED.jpg"
            (make_base or (lambda s,b: ddcolor_base(s,b,dd,session)))(src,base)
            with Image.open(base) as im:
                if im.size!=(540,960):raise ValueError("V278_WRONG_DDCOLOR_BASE_DIMENSIONS")
            prompt=PROMPT+scene
            report["finegrain_provider_attempts"]+=1
            rp.write_text(json.dumps(report,indent=2)+"\n")
            candidate=(model_predict or genuine_finegrain)(base,prompt,1910+idx)
            with Image.open(candidate) as im:
                restored=ImageOps.fit(im.convert("RGB"),(720,1280),Image.Resampling.LANCZOS)
                restored.save(dest,format="JPEG",quality=95,subsampling=0)
            if dest.stat().st_size<18000:
                raise ValueError("V278_I2I_PHOTO_TOO_SMALL")
            stats=photo_stats(src,dest)
            record={"shot":idx,"original":name,"source_frame_sha256":expected,
                    "ddcolor_base_filename":base.name,
                    "ddcolor_base_sha256":digest(base),
                    "actual_finegrain_photo_filename":dest.name,
                    "prompt_sha256":hashlib.sha256(prompt.encode()).hexdigest(),
                    **stats,"artistically_approved":False}
            report["real_photo_files"].append(record)
            if not stats["auto_preflight_passed"]:
                report["status"]="GENERATED_PHOTO_FAILED_TECHNICAL_QA"
                break
            report["status"]=f"REAL_FINEGRAIN_PHOTOS_{len(report['real_photo_files'])}_OF_4_NEED_ARTISTIC_QA"
            rp.write_text(json.dumps(report,indent=2)+"\n")
        # Source -> DDColor (not final) -> NEW Finegrain I2I visual evidence.
        n=len(report["real_photo_files"])
        if n:
            board=Image.new("RGB",(n*290,3*535),(18,22,26));draw=ImageDraw.Draw(board)
            for j,entry in enumerate(report["real_photo_files"]):
                names=(original/entry["original"],out/entry["ddcolor_base_filename"],
                       out/entry["actual_finegrain_photo_filename"])
                for row,p in enumerate(names):
                    with Image.open(p) as im:
                        board.paste(ImageOps.fit(im.convert("RGB"),(282,492)),(j*290+4,row*535+35))
                    draw.text((j*290+6,row*535+10),f"SHOT {entry['shot']} "+("ORIGINAL BW","DDCOLOR BASE","TRUE FINEGRAIN I2I")[row],fill="white")
            board.save(out/"V278_FOUR_SHOTS_SOURCE_DDCOLOR_FINEGRAIN_QA.jpg",quality=90)
    except Exception as exc:
        report["status"]="V278_FREE_METHOD_FAILED_OR_QUOTA_NOT_FINAL"
        report["error_type"]=type(exc).__name__
        raise
    finally:
        rp.write_text(json.dumps(report,indent=2)+"\n")
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original-frames",required=True,type=Path)
    p.add_argument("--scout",required=True,type=Path)
    p.add_argument("--selection",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--offline",action="store_true")
    a=p.parse_args()
    r=run(a.original_frames,a.scout,a.selection,a.out,a.offline)
    print(r["status"],"Genuine I2I generated",len(r["real_photo_files"]),"NEW FINAL 0/4")
