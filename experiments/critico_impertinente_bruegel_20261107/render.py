#!/usr/bin/env python3
"""Standalone factual satire about Bruegel's original 1559 painting.
No fake artworks, no paid APIs, no silent placeholders; deliver only after full decode QA.
"""
import asyncio, hashlib, json, math, os, random, shutil, subprocess, time
from pathlib import Path
import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont
from pydub import AudioSegment
import soundfile as sf
import edge_tts

ROOT=Path("output/critico_impertinente_bruegel")
TMP=ROOT/"build"
ROOT.mkdir(parents=True,exist_ok=True); TMP.mkdir(parents=True,exist_ok=True)
OUT=ROOT/"BRUEGEL_THE_FIGHT_BETWEEN_CARNIVAL_AND_LENT_CRITICO_COMICO.mp4"
W,H,FPS=720,1280,24
BEATS=[
 {"voice":"Nel 1559, Bruegel dipinge una battaglia. Non tra re: tra Carnevale e Quaresima. E il livello delle armi è preoccupante.","label":"IL DUELLO PIÙ IMPROBABILE","focus":"wide"},
 {"voice":"A sinistra, Carnevale. Cavalca una botte e impugna uno spiedo con la carne. Un guerriero che non combatte per la gloria: combatte per il bis.","label":"CARNEVALE: ARMATO DI ARROSTO","focus":(.36,.77,.18)},
 {"voice":"A destra, Quaresima. Magrissima. Viaggia su un carretto e risponde con una pala da forno... e due aringhe. Due! La seconda è probabilmente di riserva.","label":"QUARESIMA: DUE ARINGHE","focus":(.67,.79,.19)},
 {"voice":"È tutto vero, nel senso che Bruegel lo ha dipinto davvero: a sinistra la festa e i banchetti, a destra il digiuno che precede la Pasqua.","label":"FESTA CONTRO DIGIUNO","focus":(.50,.71,.33)},
 {"voice":"Qui c'è l'osteria. Là c'è la chiesa. Nel mezzo, una piazza piena di gente che prende decisioni discutibili da quasi cinquecento anni.","label":"OSTERIA O CHIESA?","focus":"duo"},
 {"voice":"E guardate il buffone al centro. Ha una torcia accesa in pieno giorno! Non è un effetto speciale: è proprio nel quadro. Pioniere dell'illuminazione inutile.","label":"LA TORCIA. DI GIORNO.","focus":(.45,.52,.23)},
 {"voice":"La cosa geniale è che Bruegel ci mostra tutti dall'alto: una città di piccoli drammi, piccole vanità e grandi appetiti. Il social network del Cinquecento, senza Wi-Fi.","label":"IL FEED DEL CINQUECENTO","focus":"wide"},
 {"voice":"Non incorona un vincitore. Mette in scena gli eccessi e le contraddizioni dell'umanità. Una satira che prima fa sorridere... e poi ti fa riconoscere.","label":"RIDERE, POI RICONOSCERSI","focus":(.50,.73,.36)},
 {"voice":"E allora chi vince? Se vi siete messi a guardarlo mentre cercavate uno spuntino... Bruegel ha già la sua risposta.","label":"IL VERDETTO? HO FAME.","focus":"wide"}
]
SRC="https://commons.wikimedia.org/wiki/File:The_Fight_Between_Carnival_and_Lent.jpg"
URLS=[
"https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/The_Fight_Between_Carnival_and_Lent.jpg/3840px-The_Fight_Between_Carnival_and_Lent.jpg",
"https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/The_Fight_Between_Carnival_and_Lent.jpg/2560px-The_Fight_Between_Carnival_and_Lent.jpg",
"https://commons.wikimedia.org/wiki/Special:Redirect/file/The_Fight_Between_Carnival_and_Lent.jpg?width=3840",
]
def cmd(args):
    subprocess.run(args,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
def get_img():
    p=TMP/"painting.jpg"
    errors=[]
    for u in URLS:
        try:
            with requests.get(u,headers={"User-Agent":"ArtCriticSocialFilm/1.0 (editorial public-domain Wikimedia source)"},timeout=70,stream=True) as r:
                r.raise_for_status()
                with p.open("wb") as f:
                    for c in r.iter_content(1024*256):
                        if c:f.write(c)
            im=Image.open(p); im.load()
            if im.width < 2300 or im.height < 1600: raise ValueError("Insufficient genuine source resolution "+str(im.size))
            return im.convert("RGB"),u,hashlib.sha256(p.read_bytes()).hexdigest()
        except Exception as e:
            errors.append(str(e)[:250])
            if p.exists():p.unlink()
    raise RuntimeError("Authentic painting source unavailable; no fabricated substitution. "+repr(errors))
def font(sz,bold=False,serif=False):
    paths=(
       ["/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"] if serif else
       ["/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"] if bold else
       ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    )
    for p in paths:
        if Path(p).exists():return ImageFont.truetype(p,sz)
    return ImageFont.load_default()
def matte(base, label, idx):
    d=ImageDraw.Draw(base,"RGBA")
    # restrained dark gradient, directly over historical painting
    for y in range(0,156,3):
        a=int(170*(1-y/190))
        d.rectangle((0,y,W,y+3),fill=(14,12,14,max(0,a)))
    for y in range(998,H,3):
        a=min(215,int((y-960)*0.80))
        d.rectangle((0,y,W,y+3),fill=(12,10,14,a))
    d.text((36,43),"PIETER BRUEGEL  ·  1559",font=font(23,True),fill=(231,208,155,255),stroke_width=0)
    d.line((36,88,216,88),fill=(231,208,155,200),width=2)
    # The artwork remains visible; the punchline strip never occupies the central detail
    txt=label
    f=font(32,True)
    while d.textbbox((0,0),txt,font=f)[2] > W-74:
        f=font(f.size-1,True)
    d.text((36,1110),txt,font=f,fill=(255,247,225,255),stroke_width=1,stroke_fill=(17,15,16,180))
    d.text((36,1174),"THE FIGHT BETWEEN CARNIVAL AND LENT",font=font(17,False),fill=(215,194,158,255))
    d.text((W-68,43),f"{idx+1:02d}",font=font(23,True),fill=(236,220,189,255))
    return base
def scene_image(src, beat, idx):
    iw,ih=src.size
    f=beat["focus"]
    if f=="wide":
        bg=ImageEnhance.Brightness(src.resize((820,615))).enhance(.65).resize((W,H)).filter(ImageFilter.GaussianBlur(27))
        fit=src.copy();fit.thumbnail((W-12,900),Image.Resampling.LANCZOS)
        bg.paste(fit,((W-fit.width)//2,(H-fit.height)//2-35))
    elif f=="duo":
        # two REAL, unaltered crops from the original painting, side by side
        bg=Image.new("RGB",(W,H),(28,24,25))
        for x0,x1,xc,yc in ((0,W//2,.23,.36),(W//2,W,.83,.35)):
            sw=int(iw*.20);sh=int(sw*1280/(W/2))
            sh=min(sh,ih);sw=int(sh*(W/2)/1280)
            cx=int(xc*iw);cy=int(yc*ih)
            left=max(0,min(iw-sw,cx-sw//2)); top=max(0,min(ih-sh,cy-sh//2))
            cr=src.crop((left,top,left+sw,top+sh)).resize((x1-x0,H),Image.Resampling.LANCZOS)
            bg.paste(cr,(x0,0))
        dr=ImageDraw.Draw(bg); dr.line((W//2,110,W//2,H-150),fill=(238,209,141),width=3)
    else:
        x,y,scale=f
        sw=int(iw*scale); sh=int(sw*(H/W))
        if sh>ih:
            sh=ih;sw=int(sh*(W/H))
        left=max(0,min(iw-sw,int(x*iw-sw/2)))
        top=max(0,min(ih-sh,int(y*ih-sh/2)))
        bg=src.crop((left,top,left+sw,top+sh)).resize((W,H),Image.Resampling.LANCZOS)
    bg=ImageEnhance.Contrast(bg).enhance(1.04)
    bg=ImageEnhance.Brightness(bg).enhance(1.07)
    return matte(bg,beat["label"],idx)
async def speech_all():
    full=AudioSegment.silent(duration=250)
    spans=[]
    for i,beat in enumerate(BEATS):
        mp3=TMP/f"voice_{i:02d}.mp3"
        last=None
        for voice in ("it-IT-DiegoNeural","it-IT-GiuseppeNeural"):
            try:
                await edge_tts.Communicate(beat["voice"],voice=voice,rate="+8%",pitch="-3Hz").save(str(mp3))
                if mp3.stat().st_size<2000: raise RuntimeError("voice too short")
                last=None;break
            except Exception as e:last=str(e);time.sleep(1)
        if last:raise RuntimeError(f"Natural Italian voice not available on beat {i}: "+last)
        part=AudioSegment.from_file(mp3)
        # Each scene lasts as long as the actual voice plus a small comic pause
        gap=AudioSegment.silent(duration=350 if i in (1,2,5,7) else 230)
        dur=(len(part)+len(gap))/1000
        spans.append(dur)
        full += part + gap
    full.export(TMP/"voice.wav",format="wav")
    return spans, len(full)/1000
def soundtrack(seconds):
    # Fresh, original unobtrusive chamber pizzicato — never a licensed track.
    sr=22050
    n=int((seconds+1)*sr); a=np.zeros(n,np.float32)
    notes=[196,246.94,293.66,392.0,293.66,246.94,220,261.63,329.63,440,329.63,261.63]
    rng=np.random.default_rng(1559)
    t0=0.; i=0
    while t0<seconds:
        hz=notes[i%len(notes)]; start=int(sr*t0); dur=int(sr*.27)
        t=np.arange(min(dur,n-start),dtype=np.float32)/sr
        if not len(t):break
        env=(1-np.exp(-t*120))*np.exp(-t*12)
        pluck=(np.sin(2*np.pi*hz*t)+.24*np.sin(2*np.pi*2*hz*t))*.17*env
        a[start:start+len(t)]+=pluck
        if i%4==0:
            dt=np.arange(min(int(sr*.10),n-start),dtype=np.float32)/sr
            a[start:start+len(dt)]+=.027*np.sin(2*np.pi*93*dt)*np.exp(-dt*48)
        i+=1;t0+=.40
    a+=rng.normal(0,.00016,size=n).astype(np.float32)
    fade=min(int(sr*1.5),n//6)
    a[:fade]*=np.linspace(0,1,fade)
    a[-fade:]*=np.linspace(1,0,fade)
    sf.write(TMP/"original_music.wav",np.clip(a,-1,1),sr)
def make_clip(imgpath,idx,seconds):
    outfile=TMP/f"scene_{idx:02d}.mp4"
    frames=int(math.ceil(seconds*FPS))
    # slow floating camera on actual painting; no AI alterations
    vf=f"zoompan=z='min(zoom+0.00021,1.052)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS},format=yuv420p"
    cmd(["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y","-loop","1","-framerate",str(FPS),"-i",str(imgpath),"-vf",vf,"-frames:v",str(frames),"-c:v","libx264","-threads","2","-preset","veryfast","-crf","20","-pix_fmt","yuv420p","-r",str(FPS),"-movflags","+faststart",str(outfile)])
    return outfile,frames
def probe(p):
    import av
    with av.open(str(p)) as c:
        streams=[]
        for s in c.streams:
            z={"codec_type":s.type,"codec_name":s.codec_context.name}
            if s.type=="video":z.update(width=s.codec_context.width,height=s.codec_context.height)
            streams.append(z)
        return {"streams":streams,"format":{"duration":str(c.duration/av.time_base),"size":str(p.stat().st_size)}}
def main():
    original,url,source_sha=get_img()
    print("SOURCE",original.size,url,source_sha,flush=True)
    spans,seconds=asyncio.run(speech_all())
    soundtrack(seconds)
    scene_files=[]
    total_frames=0
    for i,(beat,dur) in enumerate(zip(BEATS,spans)):
        p=TMP/f"card_{i:02d}.jpg"
        scene_image(original,beat,i).save(p,quality=94,optimize=True,subsampling=0)
        file,nframes=make_clip(p,i,dur)
        scene_files.append(file);total_frames+=nframes
        print("SCENE",i,round(dur,2),nframes,flush=True)
    cover=scene_image(original,{"label":"UNA BATTAGLIA MOLTO... PARTICOLARE","focus":"wide"},0)
    cover.save(ROOT/"COPERTINA.jpg",quality=94,optimize=True)
    concat=TMP/"scenes.txt"
    concat.write_text("".join(f"file '{p.resolve()}'\n" for p in scene_files))
    stitched=TMP/"silent_video.mp4"
    cmd(["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0","-i",str(concat),"-c","copy",str(stitched)])
    cmd(["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y","-i",str(stitched),"-i",str(TMP/"voice.wav"),"-i",str(TMP/"original_music.wav"),"-filter_complex","[1:a]volume=1.18,highpass=f=90,lowpass=f=11500[v];[2:a]volume=0.14[m];[v][m]amix=inputs=2:duration=first:dropout_transition=0,alimiter=limit=0.94[a]","-map","0:v:0","-map","[a]","-c:v","copy","-c:a","aac","-b:a","192k","-ar","44100","-movflags","+faststart","-shortest",str(OUT)])
    # Independent full decode + data QA. Do not claim video ready if this fails.
    p=probe(OUT)
    assert any(s.get("codec_type")=="audio" and s.get("codec_name")=="aac" for s in p["streams"]),p
    assert any(s.get("codec_type")=="video" and s.get("width")==W and s.get("height")==H for s in p["streams"]),p
    duration=float(p["format"]["duration"])
    assert 45<duration<120,duration
    assert OUT.stat().st_size>1000000,OUT.stat().st_size
    cmd(["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-xerror","-i",str(OUT),"-f","null","-"])
    (ROOT/"COPIONE_E_FONTI.txt").write_text(
        "CRITICO IMPERTINENTE — IL CARNEVALE CONTRO LA QUARESIMA\n\n"+
        "\n\n".join(b["voice"] for b in BEATS)+
        "\n\nFATTI VERIFICATI: Pieter Bruegel il Vecchio, 1559, olio su tavola, 118×164,5 cm, Kunsthistorisches Museum Vienna. "
        "Carnevale cavalca una botte e brandisce carne allo spiedo; Quaresima avanza su carretto con pala e pesci. "
        "Il buffone centrale tiene una torcia accesa in pieno giorno. Le battute e i paragoni moderni sono ironia autoriale, "
        "non asserzioni storiche.\n\nFONTE IMMAGINE: "+SRC+"\nDownload effettivo: "+url+
        "\nLicenza: Public Domain Mark (fotografia fedele dell'opera bidimensionale).\n"+
        "Fonti descrittive: https://bruegel.at/en/carnival-vs-lent/ ; https://www.wga.hu/html_m/b/bruegel/pieter_e/04/01carniva.html ; https://www.wga.hu/html_m/b/bruegel/pieter_e/04/05carniva.html\n"+
        "Voce italiana sintetica neurale: Microsoft Edge TTS (servizio pubblico). Musica: composizione originale generata localmente.\n"+
        "Nessuna pubblicazione automatica, nessuna API a pagamento invocata.\n",encoding="utf-8")
    manifest={"status":"FINISHED_MP4_TECHNICAL_QA_PASS_REVIEW_NOT_SOCIAL_PUBLISHED","video":OUT.name,"bytes":OUT.stat().st_size,
      "sha256":hashlib.sha256(OUT.read_bytes()).hexdigest(),"duration_seconds":round(duration,3),"resolution":[W,H],
      "audio":"real Italian neural voice + original background music","source":url,"source_sha256":source_sha,
      "scene_count":len(BEATS),"full_decode":"PASS","social_published":False,"human_artist_review":"NOT_PERFORMED"}
    (ROOT/"QA.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    print("DELIVERED",json.dumps(manifest,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
