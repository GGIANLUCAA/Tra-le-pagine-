#!/usr/bin/env python3
"""Tra le Pagine: audio italiano + illustrazioni + sottotitoli + MP4 verticale."""
import argparse, json, math, re, subprocess, tempfile, shutil
from pathlib import Path
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont
RATE=24000; FPS=24; W=720; H=1280
def run(*args):
    print("+", " ".join(str(x) for x in args)[:240],flush=True)
    subprocess.run([str(x) for x in args],check=True)
def font(size):
    file="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(file,size)
def draw_scene(num,kind,where):
    """Disegni originali noir: non dipendono da API, stock o crediti."""
    y,x=np.mgrid[0:H,0:W]
    rgb=np.stack([12+9*(1-y/H)+0*x,32+31*(1-y/H)+0*x,41+30*(1-y/H)+0*x],axis=-1)
    im=Image.fromarray(np.uint8(rgb.clip(0,255)),"RGB")
    d=ImageDraw.Draw(im,"RGBA")
    rng=np.random.default_rng(99+num)
    d.ellipse((-210,-220,850,790), fill=(199,149,83,20))
    for _ in range(125):
        a=int(rng.integers(0,W));b=int(rng.integers(0,H))
        d.ellipse((a,b,a+2,b+2),fill=(235,196,123,55))
    if kind in ("ship","sea","deck","ending"):
        for j in range(22):
            yy=740+23*j
            d.arc((-100,yy,820,yy+110),0,165,fill=(123,179,172,80),width=3)
        if kind=="ship":
            d.polygon([(55,690),(660,690),(565,880),(172,880)],fill=(5,18,30,250),outline=(219,172,101,230))
            d.rectangle((190,522,540,690),fill=(22,48,59,255),outline=(221,181,111,230),width=4)
            d.rectangle((310,426,395,522),fill=(8,22,34,255),outline=(203,162,98,230),width=3)
            for xx in range(216,525,65):
                d.ellipse((xx,572,xx+29,601),fill=(237,193,116,230))
        if kind in ("deck","ending"):
            for yy in [720,780]:d.line((0,yy,W,yy),fill=(223,183,113,170),width=6)
            for xx in [60,210,385,550,690]:d.line((xx,692,xx,980),fill=(212,177,114,135),width=7)
        if kind=="ending": d.ellipse((190,276,540,626),fill=(235,187,103,100))
    elif kind in ("prison","isolation","memory","corridor","delay"):
        d.polygon([(0,0),(150,245),(150,960),(0,H)],fill=(4,15,27,255))
        d.polygon([(W,0),(570,245),(570,960),(W,H)],fill=(4,15,27,255))
        d.rectangle((185,280,540,1000),outline=(207,171,113,180),width=5)
        d.rectangle((245,366,472,870),fill=(209,164,90,45))
        for xx in (264,350,442):d.line((xx,375,xx,870),fill=(7,29,39,230),width=17)
        if kind=="delay":
            d.ellipse((232,176,488,432),outline=(228,191,119,235),width=9)
            d.line((360,305,360,213),fill=(240,219,178,230),width=7)
            d.line((360,305,427,334),fill=(240,219,178,230),width=7)
    elif kind in ("book","study","secret"):
        d.polygon([(110,505),(358,440),(616,536),(361,608)],fill=(157,109,62,255),outline=(228,187,109,250))
        d.polygon([(110,505),(115,845),(361,926),(361,608)],fill=(32,24,30,255),outline=(216,179,108,240))
        d.polygon([(361,608),(616,536),(611,862),(361,926)],fill=(85,60,51,255),outline=(219,183,113,230))
        for yy in range(630,860,27):d.line((406,yy,572,yy-40),fill=(233,200,144,140),width=3)
    else:
        for row in range(8):
            for col in range(8):
                x0=97+col*66; y0=473+row*66
                color=(210,166,98,210) if (row+col)%2==0 else (7,26,40,235)
                d.rectangle((x0,y0,x0+66,y0+66),fill=color,outline=(241,210,149,80))
        d.ellipse((290,240,432,382),fill=(222,180,100,250))
        d.polygon([(330,367),(395,367),(453,475),(275,475)],fill=(221,184,109,240))
        d.rectangle((280,463,447,500),fill=(231,193,117,255))
    if kind in ("prison","isolation","memory","corridor","ending","deck"):
        d.ellipse((299,674,421,799),fill=(5,15,24,255),outline=(228,177,106,150),width=3)
        d.polygon([(307,794),(415,794),(490,1120),(215,1120)],fill=(7,18,29,255),outline=(210,170,100,110))
    title="TRA LE PAGINE";f=font(29);bounds=d.textbbox((0,0),title,font=f)
    d.text(((W-(bounds[2]-bounds[0]))/2,100),title,font=f,fill=(238,205,144,245))
    d.line((170,155,550,155),fill=(215,174,105,160),width=2)
    im.save(where,quality=89,optimize=True)
def sentences(s):
    return [x.strip() for x in re.split(r'(?<=[.!?])\s+(?=[A-ZÀ-ÙÈÉ«“])',re.sub(r'\s+',' ',s.strip())) if x.strip()]
def speak(sentences,engine):
    if engine=="kokoro":
        from kokoro import KPipeline
        model=KPipeline(lang_code="i")
        output=[]
        for i,s in enumerate(sentences):
            blocks=[]
            for _,_,a in model(s,voice="im_nicola",speed=0.96):
                if hasattr(a,"detach"):a=a.detach().cpu().numpy()
                blocks.append(np.asarray(a,dtype=np.float32).reshape(-1))
            if not blocks:raise RuntimeError("TTS non riuscito alla frase "+str(i+1))
            output.append(np.concatenate(blocks))
            print("Voce",i+1,"/",len(sentences),flush=True)
        return output
    from scipy.signal import resample_poly
    audios=[]
    with tempfile.TemporaryDirectory() as tmp:
        for i,s in enumerate(sentences):
            path=Path(tmp)/(str(i)+".wav")
            run("espeak-ng","-v","it","-s","140","-w",path,s)
            x,sr=sf.read(path,dtype="float32")
            if x.ndim>1:x=x.mean(axis=1)
            gcd=math.gcd(RATE,sr)
            audios.append(resample_poly(x,RATE//gcd,sr//gcd).astype(np.float32))
    return audios
def srt_time(t):
    m=round(t*1000);h,m=divmod(m,3600000);mi,m=divmod(m,60000);s,m=divmod(m,1000)
    return f"{h:02}:{mi:02}:{s:02},{m:03}"
def ass_time(t):
    m=round(t*100);h,m=divmod(m,360000);mi,m=divmod(m,6000);s,m=divmod(m,100)
    return f"{h}:{mi:02}:{s:02}.{m:02}"
def subtitles(segments,dest):
    cues=[]
    for sentence,start,end in segments:
        blocks=[];current=""
        for w in sentence.split():
            if len((current+" "+w).strip())>37 and current:
                blocks.append(current);current=w
            else:current=(current+" "+w).strip()
        if current:blocks.append(current)
        total=sum(len(b) for b in blocks);cursor=start
        for i,b in enumerate(blocks):
            stop=end if i==len(blocks)-1 else cursor+(end-start)*len(b)/total
            cues.append((cursor,stop,b));cursor=stop
    (dest/"SOTTOTITOLI.srt").write_text("".join(
        f"{i}\n{srt_time(a)} --> {srt_time(b)}\n{t}\n\n"
        for i,(a,b,t) in enumerate(cues,1)),encoding="utf-8")
    ass="""[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Narr,DejaVu Sans,43,&H00FFFFFF,&H00D3B47E,&H00000000,&H70000000,0,0,0,0,100,100,0,0,1,3.2,0.7,2,56,56,115,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    for a,b,t in cues:
        t=t.replace("\\","").replace("{","(").replace("}",")")
        ass+=f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Narr,,0,0,0,,{t}\n"
    (dest/"captions.ass").write_text(ass,encoding="utf-8")
def music(path,length):
    n=int(RATE*(length+.2));x=np.arange(n,dtype=np.float32)/RATE
    left=np.zeros(n,dtype=np.float32);right=left.copy()
    for j,f in enumerate((110,164.81,220,261.63)):
        amp=.038/(j+1)
        left+=amp*np.sin(2*np.pi*f*x+.1*np.sin(x*.27+j))
        right+=amp*np.sin(2*np.pi*f*x+.3+.1*np.sin(x*.23+j))
    fade=np.minimum(1,x/2)*np.minimum(1,np.maximum(0,length-x)/3)
    sf.write(path,np.stack([left*fade,right*fade],axis=1),RATE)
def make_video(images,duration,tmp,starts=None):
    total=math.ceil(duration*FPS)
    if starts is not None:
        if len(starts)!=len(images):raise ValueError("Le scene e i punti della narrazione non corrispondono")
        limits=[round(float(t)*FPS) for t in starts]+[total]
        if limits[0]!=0:limits[0]=0
        if any(limits[i]>=limits[i+1] for i in range(len(limits)-1)):
            raise ValueError("I cambi di scena devono essere in ordine crescente")
        counts=[limits[i+1]-limits[i] for i in range(len(images))]
    else:
        counts=[total//len(images)+(i<total%len(images)) for i in range(len(images))]
    clips=[]
    for i,(picture,num) in enumerate(zip(images,counts)):
        path=tmp/f"clip_{i:02}.mp4";secs=num/FPS
        ratio=f"min(t/{secs:.4f}\\,1)"
        pos=f"(in_w-out_w)*{ratio}" if i%2 else f"(in_w-out_w)*(1-{ratio})"
        flt=f"scale=780:1388,crop=720:1280:{pos}:(in_h-out_h)/2,format=yuv420p"
        run("ffmpeg","-hide_banner","-loglevel","error","-y","-loop","1",
            "-framerate",FPS,"-i",picture,"-vf",flt,"-frames:v",num,
            "-c:v","libx264","-preset","veryfast","-crf",25,"-pix_fmt","yuv420p",path)
        clips.append(path)
    listing=tmp/"clips.txt"
    listing.write_text("".join("file '"+str(p)+"'\n" for p in clips))
    out=tmp/"scene_montage.mp4"
    run("ffmpeg","-hide_banner","-loglevel","error","-y",
        "-f","concat","-safe","0","-i",listing,"-c","copy",out)
    return out
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--episode",default="episodes/01_scacchi")
    p.add_argument("--engine",choices=["kokoro","espeak"],default="kokoro")
    p.add_argument("--out",default="output")
    a=p.parse_args()
    ep=Path(a.episode);out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    meta=json.loads((ep/"metadata.json").read_text(encoding="utf-8"))
    phrases=sentences((ep/"testo.txt").read_text(encoding="utf-8"))
    print(meta["title"],len(phrases),"frasi",flush=True)
    audio=speak(phrases,a.engine)
    quiet=np.zeros(round(.18*RATE),dtype=np.float32);parts=[];timed=[];cursor=0
    for phrase,clip in zip(phrases,audio):
        start=cursor/RATE;cursor+=len(clip);end=cursor/RATE
        timed.append((phrase,start,end));parts.extend([clip,quiet]);cursor+=len(quiet)
    voice=np.concatenate(parts);peak=float(np.max(np.abs(voice)))
    sf.write(out/"VOCE.wav",voice/max(1,peak/.91),RATE)
    duration=len(voice)/RATE
    subtitles(timed,out);music(out/"MUSICA_ORIGINALE.wav",duration)
    with tempfile.TemporaryDirectory() as tmpname:
        tmp=Path(tmpname)
        cue_file=ep/"scene_cues.json"
        starts=None
        placeholder=False
        if cue_file.exists():
            cues=json.loads(cue_file.read_text(encoding="utf-8"))
            if cues[0]["start_sentence"]!=0:
                raise ValueError("La prima scena deve iniziare dalla frase 0")
            fallback_motifs=["isolation","chess","ship","chess","chess","corridor","book","memory","chess","delay","memory","sea"]
            images=[]
            starts=[]
            for cue in cues:
                ix=cue["start_sentence"]
                asset=cue["asset"]
                picture=ep/"images"/f"scena_{asset:02}.jpg"
                if not picture.exists():
                    placeholder=True
                    picture=tmp/f"placeholder_{asset:02}.jpg"
                    if not picture.exists():
                        draw_scene(asset,fallback_motifs[(asset-1)%len(fallback_motifs)],picture)
                images.append(picture)
                starts.append(timed[ix][1])
            (out/"SEQUENZA_SCENE.txt").write_text(
                "\n".join(f"{starts[i]:6.2f}s  {cue['description']}  (immagine {cue['asset']:02})"
                         for i,cue in enumerate(cues)),encoding="utf-8")
        else:
            images=sorted((ep/"images").glob("scena_*.jpg")) if (ep/"images").exists() else []
            if not images:
                placeholder=True
                scenes=json.loads((ep/"scenes.json").read_text(encoding="utf-8"))
                for i,scene in enumerate(scenes):
                    picture=tmp/f"scena_{i+1:02}.jpg"
                    draw_scene(i,scene["motif"],picture);images.append(picture)
        shutil.copy2(images[0],out/"COPERTINA.jpg")
        (out/"STATO_IMMAGINI.txt").write_text(
            "ANTEPRIMA TECNICA: alcune immagini sono provvisorie, NON pubblicare.\n"
            if placeholder else "IMMAGINI ESTERNE PRESENTI: controllare il risultato prima di pubblicare.\n",
            encoding="utf-8")
        montage=make_video(images,duration,tmp,starts)
        run("ffmpeg","-hide_banner","-loglevel","error","-y",
            "-i",montage,"-i",out/"VOCE.wav","-i",out/"MUSICA_ORIGINALE.wav",
            "-filter_complex","[1:a]volume=1.0[v];[2:a]volume=.40[m];[v][m]amix=inputs=2:duration=first:normalize=0[a]",
            "-vf","ass="+str(out/"captions.ass"),"-map","0:v:0","-map","[a]",
            "-c:v","libx264","-preset","veryfast","-crf","23","-pix_fmt","yuv420p",
            "-c:a","aac","-b:a","160k","-shortest","-movflags","+faststart",out/"TRA_LE_PAGINE_EP01.mp4")
    shutil.copy2(ep/"DESCRIZIONE_SOCIAL.txt",out/"DESCRIZIONE_SOCIAL.txt")
    shutil.copy2(ep/"testo.txt",out/"COPIONE.txt")
    (out/"INFO.txt").write_text(
        meta["title"]+"\nDurata: "+str(round(duration,1))+" secondi\n"
        "Voce: "+a.engine+"\nRivedere audio e sottotitoli prima di pubblicare.\n",encoding="utf-8")
    print("VIDEO COMPLETO:",out/"TRA_LE_PAGINE_EP01.mp4",flush=True)
if __name__=="__main__":main()
