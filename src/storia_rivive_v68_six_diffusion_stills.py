#!/usr/bin/env python3
"""V68 FREE public ZeroGPU: six archival-photo-consistent high-detail diffusion restorations.
No paid HF Jobs, no Vidu, no generated unrelated historical scenes.
Candidate photos only; documentary source is exact CC0 Paris 1918 V65 archival movie.
"""
import json, shutil, time, zipfile
from pathlib import Path
from urllib.request import urlopen,Request
from gradio_client import Client,handle_file
import cv2,numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT=Path("output/storia_rivive_v68_generativa_sei")
OUT.mkdir(parents=True,exist_ok=True)
url="https://github.com/GGIANLUCAA/Tra-le-pagine-/releases/download/storia-rivive-parigi-1918-photo-freeze-v65/PARIGI_1918_VIDEO_E_FOTO_V65.zip"
archive_path=OUT/"original_pack_v65.zip"
with urlopen(Request(url,headers={"User-Agent":"TraLePagineArtVision/0.8"}),timeout=80) as r,archive_path.open("wb") as f:
    shutil.copyfileobj(r,f)
archive=zipfile.ZipFile(archive_path)
if archive.testzip():raise ValueError("Original source package CRC failed")
SHOTS=[
 ("La venditrice", "authentic 1918 Paris newspaper seller in an Edwardian brown overcoat with black feathered hat, male and female customers in vintage hats at a small newspaper table in Paris, piles of newspapers and wall posters, all subjects and garments SAME as photo"),
 ("I viaggiatori", "authentic Paris 1918 Gare de Lyon station porters and passengers near a train, prominent grey long-coat man wearing a hat, other pedestrians in red and neutral historic clothing, same exact faces and spatial arrangements as original photo"),
 ("Il cinema", "authentic 1918 Paris cinema exterior with dramatic period advertisements and a crowd of people wearing wool coats and hats, authentic printed signage in background, strict source perspective and architecture, details on stone and clothing"),
 ("Il tram", "authentic 1918 Paris blue-grey electric street tram passing in front of Parisian people in wool clothing, passengers visible in windows, period hats, exact same street, vehicle and people positions"),
 ("Il boulevard", "authentic 1918 Paris lively boulevard people shopping and talking near La Revue newspaper signs, women in period dresses and elaborate hats, several men, realistic delicate faces and period fabric, same perspective and positions"),
 ("La Senna", "authentic 1918 Paris river crowd on embankment and balustrade, people in period elegant clothing observing the water, trees, architectural promenade, realistic individuals same number and positions as archive frame")
]
globalprompt="Natural present-day photorealistic documentary quality rendering from one AUTHENTIC 1918 Paris archival frame, clear lifelike skin eyes hair and textiles, plausible accurate early 20th century materials, sharp small details, natural skin tones, accurate lighting, neutral white balance, documentary photo. Preserve original camera, exact people count, pose, hats, facial proportions and background objects. "
negative="Rome, Colosseum, changed country, different people, new objects, added people, added hands, modern clothing, changed poses, beauty portrait, glamour, plastic skin, cartoon, painting, false letters, face swap, deformed faces, unrealistic eyes, stylized colors, neon red, artificial oversharpen, halo, watermark"

client=Client("finegrain/finegrain-image-enhancer",verbose=False,httpx_kwargs={"timeout":40})
qa=[]
for i,(name,details) in enumerate(SHOTS,1):
    name_file=f"FOTO_RESTAURATA_{i:02d}.jpg"
    source_image=Image.open(__import__('io').BytesIO(archive.read(name_file))).convert("RGB")
    assert source_image.size==(1080,1920)
    small=source_image.resize((486,864),Image.Resampling.LANCZOS)
    f=OUT/f"INPUT_{i:02d}.png";small.save(f)
    start=time.time()
    result=client.predict(
       input_image=handle_file(str(f)),
       prompt=globalprompt+details,
       negative_prompt=negative,
       seed=103+i*7,
       upscale_factor=2,
       controlnet_scale=1.25,
       controlnet_decay=1,
       condition_scale=4.5,
       tile_width=96,
       tile_height=128,
       denoise_strength=.40,
       num_inference_steps=17,
       solver="DDIM",
       api_name="/process")
    if not isinstance(result,(list,tuple)) or len(result)<2 or not result[1] or not Path(result[1]).is_file():
        raise RuntimeError(f"No real diffusion restoration output for scene {i}")
    output=OUT/f"GENERATIVA_{i:02d}.png"
    shutil.copyfile(result[1],output)
    gen=Image.open(output).convert("RGB")
    if gen.size[0]<950 or gen.size[1]<1700:raise RuntimeError("Restoration produced tiny image "+str(gen.size))
    # Pixel-level source continuity gate: smooth macrostructure should track the original.
    a=np.array(small.convert("L")).astype(np.float32)
    b=np.array(gen.convert("L").resize(small.size)).astype(np.float32)
    a=cv2.GaussianBlur(a,(33,33),0).ravel()
    b=cv2.GaussianBlur(b,(33,33),0).ravel()
    corr=float(np.corrcoef(a,b)[0,1])
    if corr<.70:raise RuntimeError(f"Source geometry not preserved for scene {i}: {corr}")
    lap1=float(cv2.Laplacian(np.array(small.convert("L")),cv2.CV_32F).var())
    lap2=float(cv2.Laplacian(np.array(gen.convert("L").resize(small.size)),cv2.CV_32F).var())
    qa.append({"i":i,"name":name,"source":"CC0 Paris 1918 frame, V65 color photo",
              "geometric_correlation":round(corr,4),"normalized_sharpness_source":round(lap1,1),
              "normalized_sharpness_ai":round(lap2,1),"elapsed_s":round(time.time()-start,2),
              "ai_output":output.name,"cost":"Free public ZeroGPU, no paid GPU/API"})
    print("GENUINE_DIFFUSION_PHOTO",json.dumps(qa[-1],ensure_ascii=False),flush=True)
    (OUT/"PROGRESS.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding="utf8")

board=Image.new("RGB",(6*236,2*438),(22,22,22))
d=ImageDraw.Draw(board)
for i,(name,_) in enumerate(SHOTS,1):
    original=Image.open(OUT/f"INPUT_{i:02d}.png").convert("RGB")
    new=Image.open(OUT/f"GENERATIVA_{i:02d}.png").convert("RGB")
    for row,src in enumerate((original,new)):
        tile=src.resize((224,396),Image.Resampling.LANCZOS)
        board.paste(tile,((i-1)*236+6,row*438+28))
    d.text(((i-1)*236+7,6),name,fill=(250,245,236))
    d.text(((i-1)*236+7,438+7),"DIFFUSION AI",fill=(246,245,236))
board.save(OUT/"SEI_RESTAURI_GENERATIVI_V68_PRIMA_DOPO.jpg",quality=92)
(OUT/"QA_COMPLETO.json").write_text(json.dumps({
"status":"six real diffusion images generated on free public ZeroGPU",
"historical_source":"Museum Albert Kahn, Paris 1918, Wikimedia CC0",
"ai_disclosure":"Generated reconstruction; newly inferred facial microdetail and colors may not match actual history",
"photo_approval":"PENDING HUMAN AESTHETIC INSPECTION",
"monetization":False,"paid_calls":0,"scene_tests":qa},ensure_ascii=False,indent=2),encoding="utf8")
print("GENERATION_OF_SIX_DIFFUSION_STILLS_DONE",flush=True)
