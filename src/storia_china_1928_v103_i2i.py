#!/usr/bin/env python3
"""V103: make actual I2I photographic candidates for real China archival shots.

Uses a public Hugging Face Gradio Space without paid API credentials or Vidu.
Never declares human identity/period authenticity. Individual failures are preserved.
"""
from __future__ import annotations
import hashlib, json, math, shutil, time
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT=Path("output/storia_china_1928_v103")
MODEL="finegrain/finegrain-image-enhancer"
NEG=("fake faces, invented people, morphing cars, extra hands, extra limbs, "
    "extra passengers, new architecture, changed geometry, text inventions, "
    "plastic skin, cartoon, watercolor, painting, AI artifacts, heavy orange tint, "
    "anachronistic clothes, oversaturated, beauty filter")
PROMPT=("Restore this exact REAL 1920s China archival black-and-white footage frame "
        "as a sharp vivid but natural PHOTOGRAPH IN COLOR, as if a modern documentary "
        "camera captured the very same instant. Preserve EXACT existing people, pose, "
        "face contour only when truly identifiable, costume, street, stalls, signs, "
        "background, architecture, object counts, framing and natural perspective. "
        "Realistic historical material colors and lifelike photography. "
        "Never invent a person's eyes or features not present in the source. "
        "NO sepia, NO black and white, not an illustration.")
def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()
def image_corr(original,generated):
    def low(a):
        gray=cv2.cvtColor(cv2.resize(a,(90,160)),cv2.COLOR_BGR2GRAY)
        return cv2.GaussianBlur(gray,(9,9),0).astype(np.float32).ravel()
    a=low(original);b=low(generated)
    if a.std()<1 or b.std()<1:return 0.0
    return float(np.corrcoef(a,b)[0,1])
def restore():
    source=json.loads((ROOT/"SOURCE_MANIFEST.json").read_text())
    if source.get("version")!="V103_CHINA_1920S_SOURCE_SELECT" or len(source.get("scenes",[]))!=5:
        raise RuntimeError("Missing five genuine archival source frames")
    from gradio_client import Client,handle_file
    cli=Client(MODEL,verbose=False)
    log={"version":"V103_REAL_GENERATIVE_PHOTOGRAPHY",
         "source_film_sha256":source["original_film_sha256"],
         "provider_space":MODEL,"paid_provider_credentials_used":False,
         "credit_spend":0,"requests_sent":0,"photos_succeeded_automated":0,
         "photo_human_approvals":0,"vidu_requests_sent":0,"items":[]}
    contact=Image.new("RGB",(5*240,2*430),(17,18,24))
    brush=ImageDraw.Draw(contact)
    for scene in source["scenes"]:
        n=scene["scene"];original=ROOT/scene["source_exact_frame_file"]
        entry={"scene":n,"source_sha256":sha(original),
               "source_verified_sha":scene["source_exact_frame_sha256"],
               "human_facial_identity_approved":False,"source_scene_approved":False}
        if entry["source_sha256"]!=entry["source_verified_sha"]:
            entry.update({"status":"SOURCE_CHANGED_FAIL_CLOSED"})
            log["items"].append(entry);continue
        src=cv2.imread(str(original))
        if src is None:entry["status"]="SOURCE_DECODE_FAILURE";log["items"].append(entry);continue
        rgb=cv2.cvtColor(src,cv2.COLOR_BGR2RGB)
        contact.paste(Image.fromarray(rgb).resize((235,416)),((n-1)*240+2,23))
        brush.text(((n-1)*240+5,4),f"SCENE {n} B/W",fill=(245,245,245))
        # Single attempt only: public free Space; failures never auto-retry.
        try:
            log["requests_sent"]+=1
            returned=cli.predict(handle_file(str(original)),PROMPT,NEG,
                1928+n,2,1.14,0.97,6,112,144,0.45,18,"DDIM",api_name="/process")
            obj=returned[1] if isinstance(returned,(list,tuple)) and len(returned)>1 else returned
            if isinstance(obj,dict):obj=obj.get("path")
            if not obj or not Path(str(obj)).is_file():raise RuntimeError("I2I API returned no image")
            image=cv2.imread(str(obj))
            if image is None:raise RuntimeError("I2I output unreadable")
            image=cv2.resize(image,(720,1280),interpolation=cv2.INTER_LANCZOS4)
            correlation=image_corr(src,image)
            sat=float(cv2.cvtColor(image,cv2.COLOR_BGR2HSV)[:,:,1].mean())
            bgr=ROOT/f"SCENE_{n:02d}_I2I_CANDIDATE.jpg"
            cv2.imwrite(str(bgr),image,[cv2.IMWRITE_JPEG_QUALITY,95])
            passed=correlation>=.87 and 14<sat<170
            entry.update({"status":"PHOTO_TECHNICAL_CANDIDATE_NEEDS_HUMAN_QA" if passed else "REJECT_PHOTO_MISMATCH_OR_NOT_COLOR",
              "generated_image":bgr.name,"generated_sha256":sha(bgr),
              "source_geometry_gray_correlation":round(correlation,4),
              "color_saturation_mean":round(sat,2),"real_i2i_generated":True,
              "auto_geometry_color_gate_pass":passed,"photo_human_approval":False})
            # Show rejected candidates as well, so defects are inspectable.
            contact.paste(Image.fromarray(cv2.cvtColor(image,cv2.COLOR_BGR2RGB)).resize((235,416)),
                ((n-1)*240+2,453))
            brush.text(((n-1)*240+5,434),f"REAL I2I {n} "+("QA?" if passed else "REJECT"),fill=(235,220,195))
            if passed:log["photos_succeeded_automated"]+=1
        except Exception as exc:
            entry.update({"status":"I2I_SERVICE_FAILURE","error_type":type(exc).__name__,
                         "error":str(exc)[:280],"real_i2i_generated":False})
            print("V103_I2I_FAILURE",n,type(exc).__name__,str(exc)[:150],flush=True)
        log["items"].append(entry)
        (ROOT/"I2I_STATUS.json").write_text(json.dumps(log,ensure_ascii=False,indent=2)+"\n")
        print("V103_IMAGE",n,entry["status"],"count",log["photos_succeeded_automated"],flush=True)
    contact.save(ROOT/"CHINA_V103_REAL_SOURCE_VS_REAL_I2I.jpg",quality=92)
    if log["photos_succeeded_automated"]<4:
        log["render_ready"]=False
        log["status"]="FOUR_REAL_I2I_PHOTOGRAPHS_NOT_AVAILABLE_REVIEW_ONLY"
    else:
        log["render_ready"]=True
        log["status"]="REAL_I2I_TECHNICAL_IMAGES_AVAILABLE_HUMAN_QA_PENDING"
    (ROOT/"I2I_STATUS.json").write_text(json.dumps(log,ensure_ascii=False,indent=2)+"\n")
    print("V103_SOURCE_LOCKED_PHOTO_STAGE",log["status"],flush=True)

if __name__=="__main__":restore()
