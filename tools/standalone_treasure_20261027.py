#!/usr/bin/env python3
"""One-off production: Treasure Island; premium archival N.C. Wyeth illustrations, Gemini Gacrux, checked delivery."""
import os, sys, json, re, hashlib, subprocess, urllib.request, urllib.parse, time, shutil, zipfile, math
from pathlib import Path
from PIL import Image, ImageOps, ImageFilter, ImageDraw, ImageFont, ImageEnhance
import numpy as np
import soundfile as sf
sys.path.insert(0, str(Path.cwd()/"src"))
from gemini_voice import synthesize

ROOT=Path("episodes/isola_tesoro_20261027")
OUT=Path("output/isola_tesoro_20261027")
OUT.mkdir(parents=True,exist_ok=True)
FILES=[
"TI-billy.jpg",
"TI-BlackDog.jpg",
"TI-JimHawkins.jpg",
"TI-blindpew.jpg",
"TI-BlackSpot.jpg",
"TI-PreparingFormutiny.jpg",
"TI-JimLJParr.jpg",
"TI-parrot.jpg",
"TI-Smollett (restored).jpg",
"TI-Smollett.jpg",
"TI-Gunn.jpg",
"TI-stockade.jpg",
"TI-Israel.jpg",
"TI-knife.jpg",
"TI-treasure.jpg",
"N. C. Wyeth - Treasure Island - Jim Hawkins leaves home.jpg",
]
FPS=24
def cmd(*args):
    subprocess.run([str(a) for a in args],check=True)

ARCHIVE_PDF="https://archive.org/download/treasureisland00steviala/treasureisland00steviala.pdf"
def retrieve_archive_plates():
    """Download one authoritative 1911 scan; inspect color plates locally, not 16 rate-limited image requests."""
    import fitz
    request=urllib.request.Request(ARCHIVE_PDF,headers={"User-Agent":"TraLePagine-PublicDomainBookFilm/1.0"})
    with urllib.request.urlopen(request,timeout=110) as response:
        pdf_bytes=response.read(35_000_000)
    if not pdf_bytes.startswith(b"%PDF"):raise RuntimeError("1911 archive PDF not returned")
    doc=fitz.open(stream=pdf_bytes,filetype="pdf")
    if len(doc)<200:raise RuntimeError("Scan incomplete")
    scored=[]
    for pg in range(len(doc)):
        pix=doc[pg].get_pixmap(matrix=fitz.Matrix(.30,.30),colorspace=fitz.csRGB,alpha=False)
        arr=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,3).astype(np.float32)
        diff=arr.max(axis=2)-arr.min(axis=2)
        vivid=float((diff>35).mean())
        saturation=float(diff.mean())
        # Colored paintings have vivid pigments in a significant part of the page.
        score=.85*vivid*100+.15*saturation
        if vivid>.11 and saturation>11:scored.append((score,pg))
    scored.sort(reverse=True)
    selected=[]
    for score,pg in scored:
        if all(abs(pg-other)>3 for other in selected):
            selected.append(pg)
        if len(selected)>=16:break
    if len(selected)<12:
        raise RuntimeError(f"Only {len(selected)} confidently colored distinct illustrations in scan; no geometry fallback")
    selected.sort()
    raw=OUT/"ILLUSTRAZIONI_WYETH";raw.mkdir(exist_ok=True)
    imgs=[]
    for i,pg in enumerate(selected):
        pix=doc[pg].get_pixmap(matrix=fitz.Matrix(1.55,1.55),colorspace=fitz.csRGB,alpha=False)
        im=Image.frombytes("RGB",(pix.width,pix.height),pix.samples)
        # Trim near-white page margins, keeping painted subject visible.
        arr=np.asarray(im)
        mask=(arr.min(axis=2)<205)&((arr.max(axis=2)-arr.min(axis=2))>30)
        yy,xx=np.where(mask)
        if len(xx)>10000:
            x0=max(0,int(np.percentile(xx,1))-16)
            x1=min(im.width,int(np.percentile(xx,99))+16)
            y0=max(0,int(np.percentile(yy,1))-16)
            y1=min(im.height,int(np.percentile(yy,99))+16)
            if x1-x0>im.width*.48 and y1-y0>im.height*.42:
                im=im.crop((x0,y0,x1,y1))
        out=raw/f"plate_{i+1:02}.jpg";im.save(out,quality=92)
        imgs.append((out,pg+1))
        print("SELECTED PD COLOR PLATE",pg+1,round(next((s for s,p in scored if p==pg),0),2),flush=True)
    (OUT/"SCAN_LICENSE.txt").write_text(
      "Original: Robert Louis Stevenson, Treasure Island (1883), Scribner edition 1911 illustrated by N. C. Wyeth. "+
      "Scan identifier: treasureisland00steviala. Public domain in USA and Italy (Wyeth d. 1945). "+
      "PDF: "+ARCHIVE_PDF+"\\nSelection: vivid-pigment pixel analysis from the one digitized volume. "+
      "Illustrations remain original artwork, not AI. Human visual selection still required.\\n")
    return imgs

def cinematic_frame(source,dest):
    im=Image.open(source).convert("RGB")
    # Same-illustration ambience behind complete unclipped painting; no double-exposure across scenes.
    base=ImageOps.fit(im,(720,1280),method=Image.Resampling.LANCZOS,centering=(.5,.5)).filter(ImageFilter.GaussianBlur(32))
    base=Image.blend(base,Image.new("RGB",(720,1280),(7,24,32)),.52)
    paint=ImageOps.contain(im,(696,1242),method=Image.Resampling.LANCZOS)
    x=(720-paint.width)//2;y=(1280-paint.height)//2
    # Soft shadow and uncut image. Crucial figure/face regions remain within the frame.
    layer=Image.new("RGB",(paint.width+14,paint.height+14),(11,22,26))
    base.paste(layer,(x-7,y-7))
    base.paste(paint,(x,y))
    base=ImageEnhance.Contrast(base).enhance(1.055)
    base.save(dest,quality=91,optimize=True)
def make_score(seconds,dest):
    rate=24000
    n=int((seconds+.4)*rate)
    t=np.arange(n,dtype=np.float64)/rate
    left=np.zeros(n,dtype=np.float64);right=np.zeros(n,dtype=np.float64)
    # Original gently changing harmonic score, created locally without copyrighted recording.
    progressions=[(110,164.8138,220,329.628),(87.307,130.813,174.614,261.626),
                  (73.416,110,146.832,220),(82.407,123.471,164.813,246.942)]
    duration=seconds
    for j,chord in enumerate(progressions):
        a=duration*j/4;b=duration*(j+1)/4
        gate=np.clip((t-a)/3,0,1)*np.clip((b-t)/3,0,1)
        for k,f in enumerate(chord):
            amp=.011/(1+.35*k)
            drift=.08*np.sin(.21*t+2*k+j)
            wave=np.sin(2*np.pi*f*t+drift)+.19*np.sin(2*np.pi*2*f*t+.1*k)
            left+=amp*gate*wave
            right+=amp*gate*(np.sin(2*np.pi*f*t+drift+.2)+.18*np.sin(2*np.pi*2*f*t))
    # A lightly pulsing sea-wind bed, not synthetic spoken words.
    rng=np.random.default_rng(20261027)
    noise=rng.standard_normal(n)
    kernel=np.ones(1900,dtype=np.float64)/1900
    smooth=np.convolve(noise,kernel,mode="same") if n<600_000 else None
    if smooth is None:
        from scipy.signal import lfilter
        smooth=lfilter([1/1800],[1,-1799/1800],noise)
    swell=(.0038 + .003*np.sin(2*np.pi*.11*t)**2)*smooth
    left+=swell;right+=swell*.85
    fade=np.clip(t/2,0,1)*np.clip((seconds-t)/4,0,1)
    audio=np.stack([left*fade,right*fade],axis=1)
    maxpeak=np.max(np.abs(audio))
    if maxpeak>.70:audio*=.70/maxpeak
    sf.write(dest,audio,rate)
def produce():
    script=(ROOT/"testo.txt").read_text(encoding="utf-8")
    cues=json.loads((ROOT/"scene_cues.json").read_text())
    assert 230<len(script.split())<700
    assert len(cues)==len(FILES)==16
    originals=retrieve_archive_plates()
    frames=OUT/"SCENE";frames.mkdir(exist_ok=True)
    records=[]
    for i,cue in enumerate(cues,1):
        # Narrative order follows the 1911 illustration sequence; edge repeats are deliberate.
        j=round((i-1)*(len(originals)-1)/(len(cues)-1))
        path,pagenum=originals[j]
        frame=frames/f"scena_{i:02}.jpg"
        cinematic_frame(path,frame)
        records.append({"asset_id":f"scena_{i:02}","edition":"Treasure Island Scribner 1911",
           "author":"N. C. Wyeth","year":1911,"source_kind":"public_domain_original_book_illustration",
           "provider":"Internet Archive", "page_in_pdf":pagenum,
           "source_reference":ARCHIVE_PDF+"#page="+str(pagenum),
           "license_review":"PD 1911 edition; illustrator died 1945; public domain US / life+70 Italy",
           "scene_relevance":cue["description"],"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
           "visual_check":"Verified nonempty painted image; needs full artistic review",
           "reuse_reason":"Narrative bookend/match cut" if any(r.get("page_in_pdf")==pagenum for r in records) else ""})
        print("PREPARED",i,"from scan page",pagenum,flush=True)
    (OUT/"FONTI_ASSET.json").write_text(json.dumps(records,indent=2,ensure_ascii=False),encoding="utf-8")
    # All visuals are validated and acquired BEFORE the single allowed Gemini request.
    if not os.environ.get("GEMINI_API_KEY"):raise RuntimeError("GEMINI_API_KEY unavailable; no silent alternative")
    VOICE=OUT/"AUDIO"
    voice,timed=synthesize(script,VOICE)
    duration=len(voice)/24000
    if not 120<=duration<=250:raise RuntimeError(f"Unexpected voice duration {duration}")
    if not timed or len(timed)<len(cues):raise RuntimeError("No sentence alignment")
    bounds=[round(float(timed[x["start_sentence"]][1])*FPS) for x in cues]
    total=round(duration*FPS)
    bounds[0]=0;bounds.append(total)
    if any(a>=b for a,b in zip(bounds,bounds[1:])):raise RuntimeError("Scene timing nonmonotonic")
    clips=[]
    starts=[]
    for i,cue in enumerate(cues):
        frames_count=bounds[i+1]-bounds[i]
        seconds=frames_count/FPS
        fade=min(.26,max(.10,seconds*.085))
        startfade=max(.0,seconds-fade)
        frame=frames/f"scena_{i+1:02}.jpg"
        out=OUT/f"part_{i+1:02}.mp4"
        # A dark-colour dip, never a transparent xfade or ghosting of two artworks.
        direction="t/%0.4f"%seconds if i%3==0 else "(1-t/%0.4f)"%seconds
        cropx=f"(in_w-out_w)*min(1,max(0,{direction}))"
        vf=(f"scale=758:1348,crop=720:1280:{cropx}:(in_h-out_h)/2,"
            f"fade=t=in:st=0:d={fade:.3f}:color=0x0e2530,"
            f"fade=t=out:st={startfade:.3f}:d={fade:.3f}:color=0x0e2530,"
            "format=yuv420p")
        cmd("ffmpeg","-hide_banner","-loglevel","error","-y","-loop","1","-framerate",str(FPS),
            "-i",str(frame),"-vf",vf,"-frames:v",str(frames_count),
            "-c:v","libx264","-preset","veryfast","-crf","22","-pix_fmt","yuv420p",str(out))
        clips.append(out)
        starts.append({"start":bounds[i]/FPS,"end":bounds[i+1]/FPS,"scene":cue["description"],"file":frame.name})
    (OUT/"ALLINEAMENTO_SCENE.json").write_text(json.dumps(starts,ensure_ascii=False,indent=2))
    manifest=OUT/"parts.txt"
    manifest.write_text("".join("file '"+str(x.resolve())+"'\n" for x in clips))
    montage=OUT/"MONTAGGIO_SENZA_AUDIO.mp4"
    cmd("ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0","-i",str(manifest),
        "-c","copy",str(montage))
    music=OUT/"MUSICA_ORIGINALE.wav";make_score(duration,music)
    target=OUT/"TRA_LE_PAGINE_L_ISOLA_DEL_TESORO.mp4"
    cmd("ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(montage),
        "-i",str(VOICE/"VOCE.wav"),"-i",str(music),
        "-filter_complex","[1:a]volume=1.0[v];[2:a]volume=0.35[m];[v][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.94[a]",
        "-map","0:v:0","-map","[a]","-sn","-c:v","copy",
        "-c:a","aac","-b:a","160k","-movflags","+faststart","-shortest",str(target))
    meta=json.loads((ROOT/"metadata.json").read_text(encoding="utf-8"))
    cover=Image.open(frames/"scena_07.jpg").convert("RGB").resize((720,1280))
    # Controlled series branding, not drawn as unreviewed AI lettering.
    overlay=Image.new("RGBA",(720,1280),(0,0,0,0));d=ImageDraw.Draw(overlay)
    for y in range(750,1280):
        alpha=int(230*(y-750)/530)
        d.line((0,y,720,y),fill=(5,21,31,alpha))
    fonts="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
    d.text((360,830),"TRA LE PAGINE",anchor="mm",font=ImageFont.truetype(fonts,29),fill=(220,184,123,255))
    d.text((360,955),"L'ISOLA DEL",anchor="mm",font=ImageFont.truetype(fonts,51),fill=(248,241,226,255))
    d.text((360,1027),"TESORO",anchor="mm",font=ImageFont.truetype(fonts,74),fill=(250,225,176,255))
    d.text((360,1145),"ROBERT LOUIS STEVENSON",anchor="mm",font=ImageFont.truetype(fonts,24),fill=(225,195,145,255))
    Image.alpha_composite(cover.convert("RGBA"),overlay).convert("RGB").save(OUT/"COPERTINA_SERIE.jpg",quality=94)
    (OUT/"COPIONE.txt").write_text(script,encoding="utf-8")
    (OUT/"DESCRIZIONE_SOCIAL.txt").write_text((ROOT/"DESCRIZIONE_SOCIAL.txt").read_text(encoding="utf-8"),encoding="utf-8")
    info=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries",
             "stream=codec_type,codec_name,width,height:format=duration,size","-of","json",str(target)]))
    streams=info["streams"]
    assert any(s.get("codec_type")=="video" and s.get("width")==720 and s.get("height")==1280 for s in streams)
    assert any(s.get("codec_type")=="audio" and s.get("codec_name")=="aac" for s in streams)
    assert not any(s.get("codec_type")=="subtitle" for s in streams)
    cmd("ffmpeg","-v","error","-xerror","-i",str(target),"-f","null","-")
    report={"master":target.name,"sha256":hashlib.sha256(target.read_bytes()).hexdigest(),
         "duration":float(info["format"]["duration"]),"size_bytes":int(info["format"]["size"]),
         "images":len(records),"music":"original synthesized score","voice":"Gemini Gacrux actual WAV",
         "ffmpeg_full_decode":"passed","status":"rendered_needs_review",
         "note":"Mechanical QA passed; artistic approval only after watching complete file"}
    (OUT/"QA_VERIFICATO.json").write_text(json.dumps(report,indent=2,ensure_ascii=False))
    with zipfile.ZipFile(OUT/"SOLO_VIDEO_V36.zip","w",compression=zipfile.ZIP_STORED) as z:
        z.write(target,target.name)
    kitfiles=[target,OUT/"COPERTINA_SERIE.jpg",OUT/"COPIONE.txt",OUT/"DESCRIZIONE_SOCIAL.txt",
              OUT/"FONTI_ASSET.json",OUT/"ALLINEAMENTO_SCENE.json",OUT/"QA_VERIFICATO.json",
              VOICE/"VOCE.wav",music]
    with zipfile.ZipFile(OUT/"KIT_COMPLETO.zip","w",compression=zipfile.ZIP_DEFLATED,compresslevel=3) as z:
        for f in kitfiles:z.write(f,f.name)
        for f in sorted(frames.glob("*.jpg")):z.write(f,"SCENE/"+f.name)
    print("DELIVERY VERIFIED",json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":produce()
