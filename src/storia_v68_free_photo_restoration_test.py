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
try:
    print("STARTING_FINEGRAIN_GENERATIVE",flush=True)
    cl=Client("finegrain/finegrain-image-enhancer",verbose=False)
    v=cl.predict(handle_file(str(OUT/"BASE_PER_AI.jpg")),
        "A genuine candid documentary photograph of Paris in 1918, lifelike eyes, skin, clothing seams, fine newspaper details and stonework, preserving exactly the original persons, faces, pose, hats, tabletop, street, and camera view. Highly realistic restored photographic texture, true-to-source perspective, neutral natural skin tones.",
        "extra people, altered faces, glamour makeup, cartoon, oil painting, overly saturated colors, modern cars, made-up storefront, new pose, inaccurate hands, excessive fake texture, plastic skin",
        42, 2, 1.05, .95, 5, 112, 144, .30, 15, "DDIM",api_name="/process")
    print("FINEGRAIN_RETURN",repr(v)[:800],flush=True)
    # Slider returns pair (original, processed).
    generated=v[1] if isinstance(v,(list,tuple)) else v
    if isinstance(generated,dict):generated=generated.get("path")
    if not generated or not Path(str(generated)).is_file():raise ValueError("Missing generative resulting image")
    dest=OUT/"FINEGRAIN_PHOTOGRAPHIC_RESTORATION.png"
    Image.open(generated).convert("RGB").save(dest)
    results.append({"model":"finegrain", "image":dest.name,"sha256":digest(dest),"size":Image.open(dest).size})
    print("REAL_FINEGRAIN_COMPLETE",dest.stat().st_size,flush=True)
except Exception as e:
    print("FINEGRAIN_NOT_AVAILABLE",type(e).__name__,str(e)[:1200],flush=True)
try:
    print("STARTING_CODEFORMER_FACE",flush=True)
    cl=Client("sczhou/CodeFormer",verbose=False)
    v=cl.predict(handle_file(str(OUT/"BASE_V65_AUTENTICA.jpg")),
        False,False,False,2,.76,api_name="/inference")
    print("CODEFORMER_RETURN",repr(v)[:800],flush=True)
    generated=v[0] if isinstance(v,(list,tuple)) else v
    if isinstance(generated,dict):generated=generated.get("path")
    if not generated or not Path(str(generated)).is_file():raise ValueError("Missing CodeFormer resulting image")
    dest=OUT/"CODEFORMER_FACE_RESTORATION.png"
    Image.open(generated).convert("RGB").save(dest)
    results.append({"model":"CodeFormer","image":dest.name,"sha256":digest(dest),"size":Image.open(dest).size})
    print("REAL_CODEFORMER_COMPLETE",dest.stat().st_size,flush=True)
except Exception as e:
    print("CODEFORMER_NOT_AVAILABLE",type(e).__name__,str(e)[:1200],flush=True)
(OUT/"RESULTS.json").write_text(json.dumps({"source":"authentic archived Paris 1918 frame transformed using DDColor/RealESRGAN V65",
 "input_sha256":digest(OUT/"BASE_V65_AUTENTICA.jpg"),
 "free_zero_gpu_public_demos_no_paid_tokens":True,
 "results":results,"identity_historical_accuracy_not_certified":True},ensure_ascii=False,indent=2))
if not results:raise RuntimeError("No genuinely AI-enhanced photograph could be produced; NO fake result.")
print("V68_ACTUAL_PHOTOGRAPH_RESULTS",json.dumps(results,ensure_ascii=False),flush=True)
