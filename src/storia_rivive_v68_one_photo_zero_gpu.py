#!/usr/bin/env python3
"""V68 one authentic photo test through free public ZeroGPU. NO Jobs, paid GPU, Vidu.
The input is one truly colorized still from CC0 Parigi 1918 source.
Output is a candidate only, never the source-of-truth or master until inspected.
"""
import json, shutil, subprocess, time, zipfile
from pathlib import Path
from urllib.request import urlopen,Request
import cv2, numpy as np
from PIL import Image
from gradio_client import Client,handle_file
OUT=Path("output/storia_rivive_v68_generativa")
OUT.mkdir(parents=True,exist_ok=True)
URL="https://github.com/GGIANLUCAA/Tra-le-pagine-/releases/download/storia-rivive-parigi-1918-photo-freeze-v65/PARIGI_1918_VIDEO_E_FOTO_V65.zip"
req=Request(URL,headers={"User-Agent":"TraLePagineVideoRestoration/0.1"})
zipfile_path=OUT/"v65_archive.zip"
with urlopen(req,timeout=90) as fd,open(zipfile_path,"wb") as out:
    shutil.copyfileobj(fd,out)
with zipfile.ZipFile(zipfile_path) as archive:
    assert archive.testzip() is None
    photo_bytes=archive.read("FOTO_RESTAURATA_01.jpg")
seed=OUT/"SOURCE_COLOR_CC0_01.jpg"
seed.write_bytes(photo_bytes)
im=Image.open(seed).convert("RGB")
assert im.size==(1080,1920),im.size
# Pixel area and compute capped for free public shared GPU demo.
reduced=im.resize((486,864),Image.Resampling.LANCZOS)
infile=OUT/"SOURCE_FOR_GENERATIVE_486x864.png"
reduced.save(infile)
prompt=(
"Historic Paris 1918 authentic candid documentary PHOTOGRAPH, a female newspaper "
"seller in dark Edwardian coat and broad black hat standing at a small newspaper stand, "
"three adult customers in period wool clothing behind her, hanging printed paper advertisements "
"and Paris street facade in the background, SAME individuals, same gestures, same positions, "
"same environment and perspective as the image. Contemporary photographic definition, "
"believable individual eyes, human skin microtexture, natural realistic faces, legible fabric weave, "
"realistic paper fibers, detailed but unexaggerated colors, cinematic natural light."
)
negative=(
"different city, Rome, Colosseum, different people, invented people, new objects, "
"changed faces, different camera position, plastic skin, doll face, deformed hands, "
"extra limbs, unrealistic eyes, digital painting, illustration, cartoon, CGI, "
"oversaturated colors, halos, watermarks, double faces"
)
t0=time.time()
try:
    client=Client("finegrain/finegrain-image-enhancer",verbose=False,httpx_kwargs={"timeout":40})
    result=client.predict(
      input_image=handle_file(str(infile)),
      prompt=prompt,
      negative_prompt=negative,
      seed=21,
      upscale_factor=2,
      controlnet_scale=1.2,
      controlnet_decay=1.0,
      condition_scale=4.5,
      tile_width=96,
      tile_height=128,
      denoise_strength=0.30,
      num_inference_steps=14,
      solver="DDIM",
      api_name="/process",
    )
    print("FREE_ZERO_GPU_RESULT",repr(result)[:900],flush=True)
    if isinstance(result,(list,tuple)) and len(result)>=2:
        path=result[1]
    else: raise ValueError("Demo returned invalid result")
    if not path or not Path(path).is_file():raise ValueError("No actual generated image produced")
    output=OUT/"GENERATIVE_01_FROM_SAME_FRAME.png"
    shutil.copyfile(path,output)
    generated=Image.open(output).convert("RGB")
    print("GENERATIVE_IMAGE_PRODUCED",generated.size,"bytes",output.stat().st_size,flush=True)
    assert min(generated.size)>=900
    b=np.asarray(reduced.convert("L"))
    g=np.asarray(generated.convert("L").resize(reduced.size))
    # Coarse structural geometry check: high-frequency appearance can change, layout should not.
    b=cv2.GaussianBlur(b,(31,31),0).astype("float32").ravel()
    g=cv2.GaussianBlur(g,(31,31),0).astype("float32").ravel()
    corr=float(np.corrcoef(b,g)[0,1])
    print("STRUCTURAL_FIDELITY_SCORE",corr,flush=True)
    if corr < .58:raise ValueError("Not faithful to historical source scene")
    pair=Image.new("RGB",(972,864),(20,22,25))
    pair.paste(reduced,(0,0))
    pair.paste(generated.resize((486,864)),(486,0))
    pair.save(OUT/"V68_REVIEW_BEFORE_AFTER.jpg",quality=91)
    (OUT/"QA.json").write_text(json.dumps({
      "source_archive":"Musée Albert-Kahn / Wikimedia Commons CC0 Parigi 1918",
      "source_original_timecode_s":265.0,
      "source_photo_reference":"V65 FOTO_RESTAURATA_01.jpg",
      "model":"finegrain/finegrain-image-enhancer public ZeroGPU diffusion ControlNet tile",
      "paid_api_calls":0,"requires_human_artistic_review":True,
      "structural_fidelity_score":corr,"seconds":round(time.time()-t0,1),
      "note":"This is a generative reconstruction: face and fine-details are plausible, not historically certain."
    },indent=2))
except Exception as exc:
    (OUT/"FAILED_GENERATION.txt").write_text(type(exc).__name__+": "+str(exc))
    print("GENERATIVE_TEST_FAILED",type(exc).__name__,str(exc)[:1100],flush=True)
    raise
