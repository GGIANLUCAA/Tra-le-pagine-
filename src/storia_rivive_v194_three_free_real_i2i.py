#!/usr/bin/env python3
"""V194: free, anonymous, source SHA-locked REAL I2I for three V191 film scenes.

Every submission is recorded BEFORE its single request, with NO retry.
Not a final historic documentary; face/object faithfulness always needs visual QA.
"""
import argparse, hashlib, json
from pathlib import Path
from PIL import Image
import numpy as np

SPACE = "JEYASEKHAR/QWEN_EDIT_IMAGE"
FILM_SHA="eacbb947105f9143632e3d4e933ee5e200ba98f5d588c11c552dfb94787de1d9"
SCENES=(1,2,4)
GUIDANCE=1.0
OUTPUT_LONG_SIDE=1024
PROMPTS={
1:"Reconstruct the EXACT same early 1900s black and white silent-film office still as a lifelike color documentary photograph. Maintain EVERY person at precisely the same place and scale, preserve faces, hair, suits, hands and hand gestures. Same desk, furniture, wall and camera viewpoint, same background geometry. Restore photographic textures and natural period-appropriate color only; do not replace faces, objects, crop, camera angle, setting, perspective or people. Detailed but historically conservative natural photorealism. No orange cast, no invented persons, no distorted hands, no CGI or painting.",
2:"Restore the EXACT same black and white 1909 stock-exchange film frame as a high-quality natural-color photographic reconstruction. Same tightly packed crowds of men in Edwardian suits and hats, same raised arms, expressions and faces in the SAME positions, identical architecture and original perspective. No missing or extra figures, no invented hands, fingers, hats, signage or text. Accurate natural subdued colors and believable skin, fabric and wood textures with restrained contrast. Preserve the original composition exactly, no sepia or illustration.",
4:"Photorealistic, faithful historical restoration of THIS precise frame of a 1909 silent movie depicting rural farm workers in traditional period clothing. SAME exact people, postures, faces, hats, hands and items in their hands; identical backgrounds, trees, floor, composition, camera and framing. Only gently recover film detail and introduce subtle believable daylight colors, fine skin and worn cotton textures; never invent facial features, clothing, items, people or scenic geometry, never use cartoonish or over-saturated styling."
}

def sha(b):
    return hashlib.sha256(b).hexdigest()

def verify_handoff(root):
    root=Path(root)
    m=json.loads((root/"V191_PRODUCTION_HANDOFF.json").read_text())
    if m.get("version")!="V191_TRUE_PHOTOGRAPHIC_I2I_PREPARATION" or m.get("film_source_sha256")!=FILM_SHA or m.get("i2i_generated")!=0 or m.get("vidu_generated")!=0 or m.get("publish_permitted") is not False:
        raise ValueError("V191_HANDOFF_INVALID")
    entries={x["scene"]:x for x in m["photo_i2i_jobs"]}
    for scene in SCENES:
        entry=entries[scene]
        src=root/entry["source_file"]
        if src.is_symlink() or src.parent!=root or not src.is_file():
            raise ValueError("MISSING_UNTRUSTED_ORIGINAL_FRAME")
        if sha(src.read_bytes())!=entry["source_sha256"]:
            raise ValueError("SOURCE_SHA_MISMATCH")
        with Image.open(src) as im:
            im.verify()
        with Image.open(src) as im:
            if im.size!=(720,1280):
                raise ValueError("NOT_EXACT_ORIGINAL_SOURCE_RASTER")
    return entries

def assess(original, generated):
    with Image.open(original) as im:
        a=im.convert("RGB").resize((120,214))
    with Image.open(generated) as im:
        b=im.convert("RGB").resize((120,214))
    x=np.asarray(a.convert("L"),dtype=np.float32).ravel()
    y=np.asarray(b.convert("L"),dtype=np.float32).ravel()
    corr=float(np.corrcoef(x,y)[0,1]) if x.std()>1 and y.std()>1 else 0
    sat=float(np.array(b.convert("HSV"))[:,:,1].mean())
    return {"coarse_luma_correlation":round(corr,4),"mean_saturation":round(sat,1),
            "scene_identity_visual_qa_approved":False,
            "candidate_structure_suspect":corr < 0.70}

def run(root,out):
    root,out=Path(root),Path(out)
    if out.exists() or any(p.is_symlink() for p in out.parents):
        raise ValueError("OUTPUT_EXISTS_OR_SYMLINK_PARENT")
    entries=verify_handoff(root)
    out.mkdir()
    report={"version":"V194","source_film_sha256":FILM_SHA,"space":SPACE,
            "status":"FREE_I2I_ATTEMPTING_REAL_BYTES","scenes":[],
            "total_anonymous_provider_attempts":0,"paid_calls":0,"credits_spent":0,
            "human_approved":False,"four_approved_restorations":0,
            "vidu_clip_generated":False,"final_mp4_produced":False,
            "publish_permitted":False}
    def save():
        (out/"V194_I2I_REAL_RESULTS.json").write_text(json.dumps(report,indent=2)+"\n")
    save()
    try:
        from gradio_client import Client,handle_file
        client=Client(SPACE,verbose=False)
    except Exception as exc:
        report["status"]="SPACE_UNAVAILABLE_NO_REQUEST"
        report["error_type"]=type(exc).__name__
        save();return report
    for scene in SCENES:
        e=entries[scene];src=root/e["source_file"]
        row={"scene":scene,"original_source_file":src.name,
             "original_sha256":e["source_sha256"],"status":"IN_PROGRESS",
             "free_provider_attempts":1,"real_i2i_generated":False,"face_and_hand_qa":False,
             "photo_file":None}
        report["scenes"].append(row)
        report["total_anonymous_provider_attempts"]+=1
        save() # before one external POST
        try:
            result=client.predict(image=handle_file(str(src)),prompt=PROMPTS[scene],
                lora_adapter="",image2=None,seed=194+scene,
                randomize_seed=False,guidance_scale=GUIDANCE,steps=4,
                preserve_identity=True,identity_strength=90,output_size=OUTPUT_LONG_SIDE,
                fix_hands=False,api_name="/edit")
            target=result[0] if isinstance(result,(list,tuple)) else result
            if isinstance(target,dict):target=target.get("path")
            path=Path(target)
            if not path.is_file() or path.stat().st_size<15000:
                raise ValueError("GENERATOR_NO_REAL_IMAGE")
            with Image.open(path) as im:
                im.verify()
            with Image.open(path) as im:
                if max(im.size)<900 or min(im.size)<512:
                    raise ValueError("GENERATED_IMAGE_INVALID_DIMENSIONS")
                name=f"SCENE{scene:02}_REAL_GENERATIVE_I2I_CANDIDATE.png"
                dst=out/name
                im.convert("RGB").save(dst)
            row["photo_file"]=name;row["photo_sha256"]=sha(dst.read_bytes())
            row["real_i2i_generated"]=True
            row["assessment"]=assess(src,dst)
            row["status"]="REAL_I2I_GENERATED_VISUAL_QA_PENDING"
            left=Image.open(src).convert("RGB").resize((360,640))
            right=Image.open(dst).convert("RGB").resize((360,640))
            sheet=Image.new("RGB",(720,640))
            sheet.paste(left,(0,0));sheet.paste(right,(360,0))
            sheet.save(out/f"SCENE{scene:02}_ORIGINAL_VS_I2I.jpg",quality=90)
            save()
        except Exception as exc:
            row["status"]="FREE_PROVIDER_ERROR_NO_RETRY"
            row["error_type"]=type(exc).__name__
            row["error_summary"]=str(exc)[:190]
            report["status"]="PARTIAL_OR_BLOCKED"
            save()
            break # quota/errors: do not spam the public service
    if len(report["scenes"])==3 and all(s["real_i2i_generated"] for s in report["scenes"]):
        report["status"]="THREE_REAL_I2I_CREATED_NEEDS_HUMAN_QA"
    else:
        report["status"]="PARTIAL_OR_BLOCKED"
    save();return report

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--sources",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    d=run(args.sources,args.out)
    print("V194",d["status"],"attempts",d["total_anonymous_provider_attempts"],
          "images",sum(x["real_i2i_generated"] for x in d["scenes"]),
          "paid",0,"publish",False)

if __name__=="__main__":
    main()
