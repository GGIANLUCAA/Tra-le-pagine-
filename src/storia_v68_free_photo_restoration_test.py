#!/usr/bin/env python3
"""V68: free public ZeroGPU trials using the SAME actual Paris 1918 archive-derived still.
No credit card, no paid API token, and no fabricated text-only alternative.
"""
import io, json, shutil, zipfile, hashlib, urllib.request
from pathlib import Path
from PIL import Image,ImageEnhance
from gradio_client import Client,handle_file
OUT=Path("output/storia_v68_oneframe");OUT.mkdir(parents=True,exist_ok=True)
SRC="https://github.com/GGIANLUCAA/Tra-le-pagine-/releases/download/storia-rivive-parigi-1918-photo-freeze-v65/PARIGI_1918_VIDEO_E_FOTO_V65.zip"
req=urllib.request.Request(SRC,headers={"User-Agent":"Tra-le-Pagine/0.68"})
print("DOWNLOADING_ARCHIVE",flush=True)
with urllib.request.urlopen(req,timeout=100) as r:data=r.read()
with zipfile.ZipFile(io.BytesIO(data)) as z:
    print("ARCHIVE_FILES",z.namelist()[:12],flush=True)
    image_data=z.read("FOTO_RESTAURATA_01.jpg")
    original=Image.open(io.BytesIO(image_data)).convert("RGB")
    original.save(OUT/"BASE_V65_AUTENTICA.jpg",quality=93)
    # Mild chromatic neutralization prevents pink skin from driving generative texture further.
    img=ImageEnhance.Color(original).enhance(.88)
    w,h=img.size
    img=img.resize((round(w*.50),round(h*.50)),Image.Resampling.LANCZOS)
    img.save(OUT/"BASE_PER_AI.jpg",quality=96)
    print("SOURCE_RENDERED",w,h,"AIINPUT",img.size,flush=True)
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
results=[]
prompt="Sharp true-to-life historic color photograph Paris 1918 newspaper vendor, realistic facial pores and eyes, expressive subtle face details with human natural skin, individual hair strands, natural woven wool and linen fabric, newspaper print texture, limestone architectural details, authentic camera lens optical sharpness, rich midtones, preserve exact existing identities and locations and framing of ALL original people, no reframing, photorealistic restored frame"
negative="different people, changing face or pose, added objects, invented street, fake signage, glam fashion, big facial changes, plastic skin, waxy skin, painting, illustration, smearing, excessive grain, halo, red magenta cast, double pupils, extra hands"
cl=Client("finegrain/finegrain-image-enhancer",verbose=False)
for name,denoise,control,seed in (("PRECISA",.48,1.16,69),("FORTE",.64,1.30,149)):
    try:
        print("START_VARIANT",name,denoise,control,flush=True)
        v=cl.predict(handle_file(str(OUT/"BASE_PER_AI.jpg")),
            prompt,negative,seed,2,control,.96,6,112,144,denoise,20,"DDIM",api_name="/process")
        generated=v[1] if isinstance(v,(tuple,list)) else v
        if isinstance(generated,dict):generated=generated.get("path")
        if not generated or not Path(str(generated)).is_file():raise ValueError("Missing actual output")
        dest=OUT/f"FOTO_GENERATIVA_{name}.png"
        Image.open(generated).convert("RGB").save(dest)
        results.append({"model":"finegrain","mode":name,"denoise":denoise,"controlnet":control,"image":dest.name,
                        "sha256":digest(dest),"size":Image.open(dest).size})
        print("REAL_IMAGE_GENERATED",name,dest.stat().st_size,flush=True)
    except Exception as e:
        print("MODEL_UNAVAILABLE",name,type(e).__name__,str(e)[:1200],flush=True)
(OUT/"RESULTS.json").write_text(json.dumps({"source":"actual CC0 1918 Paris historical video frame, V65 colorization",
 "base_sha256":digest(OUT/"BASE_V65_AUTENTICA.jpg"),"zero_paid_credits":True,
 "results":results,"visual_identity_review_required":True},ensure_ascii=False,indent=2))
if not results:raise RuntimeError("Generative restoration failed; no dummy output.")
print("V68_IMPROVED_GENERATIVE_RESTORATION",json.dumps(results,ensure_ascii=False),flush=True)
