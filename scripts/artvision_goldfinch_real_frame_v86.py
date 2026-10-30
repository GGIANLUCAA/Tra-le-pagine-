#!/usr/bin/env python3
"""Fabritius V86: ONE Cinema Museum review revision, not a new fifth slot.
Single continuous optical path, real frame photo by Sailko CC BY 3.0.
No TTS, no video AI, no social publication, no fake human Gold review.
"""
import hashlib, io, json, math, os, pathlib, subprocess, zipfile
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
OUT=pathlib.Path("output/artvision-fabritius-v86")
OUT.mkdir(parents=True,exist_ok=True)
PHOTO="https://commons.wikimedia.org/wiki/Special:Redirect/file/Carel%20fabritius%2C%20il%20cardellino%2C%201654%2C%2001.jpg"
ALT="https://upload.wikimedia.org/wikipedia/commons/9/9e/Carel_fabritius%2C_il_cardellino%2C_1654%2C_01.jpg"
MUSIC="https://incompetech.com/music/royalty-free/mp3-royaltyfree/Water%20Lily.mp3"
FPS=20; W=720; H=1280; DURATION=44; N=FPS*DURATION
SHA=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def download(urls,path,min_bytes,kind):
    errors=[]
    for url in urls:
        try:
            with requests.get(url,timeout=75,stream=True,headers={"User-Agent":"ArtVisionBot/1.0 (Wikimedia historical art research; https://github.com/GGIANLUCAA/Tra-le-pagine-)"}) as r:
                if r.status_code in (429,404):
                    errors.append(f"{r.status_code}: {url}"); continue
                r.raise_for_status()
                t=r.headers.get("content-type","").lower()
                if kind=="image" and "image" not in t and "octet-stream" not in t:
                    raise ValueError("IMAGE_BAD_MIME "+t)
                if kind=="audio" and not any(x in t for x in ("mpeg","audio","octet-stream")):
                    raise ValueError("AUDIO_BAD_MIME "+t)
                with open(path,"wb") as f:
                    for block in r.iter_content(1024*512):
                        if block:f.write(block)
                if pathlib.Path(path).stat().st_size<min_bytes:raise ValueError("too small")
                return url
        except Exception as e:errors.append(f"{type(e).__name__}: {str(e)[:120]}")
    raise RuntimeError(kind+"_SOURCE_UNAVAILABLE: "+" | ".join(errors))
def smooth(x):return x*x*(3-2*x)
KEYS=[(0,1.0,.50,.50),(4,1.28,.51,.48),(10,1.78,.54,.43),
      (17,2.22,.55,.47),(25,2.23,.49,.57),(33,1.78,.50,.52),(44,1.0,.50,.50)]
def pose(t):
    for a,b in zip(KEYS,KEYS[1:]):
        if a[0]<=t<=b[0]:
            u=smooth((t-a[0])/(b[0]-a[0]))
            return tuple(a[i]+(b[i]-a[i])*u for i in (1,2,3))
    return (1.,.5,.5)
def text_face(path,size):
    return ImageFont.truetype(path,size)
def main():
    photo=OUT/"FRAME_PHOTO_SAILKO_CC_BY3.jpg"
    source=download([PHOTO,ALT],photo,900000,"image")
    raw=Image.open(photo).convert("RGB")
    assert raw.width>=2000 and raw.height>=3000,("PHOTO_NOT_HIRES",raw.size)
    music=OUT/"WATER_LILY_ORIGINAL_CC_BY4.mp3"
    download([MUSIC],music,100000,"audio")
    # Actual photograph of the exact painting in its frame; backdrop created
    # from the SAME photograph, not an invented official museum installation.
    cw,ch=1440,2560
    back=raw.resize((cw,ch),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(50))
    back=ImageEnhance.Brightness(back).enhance(.51)
    fw=1150;fh=int(raw.height*fw/raw.width)
    sharp=raw.resize((fw,fh),Image.Resampling.LANCZOS)
    back.paste(sharp,((cw-fw)//2,(ch-fh)//2))
    photo_canvas=back
    title=text_face("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",35)
    artist=text_face("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",17)
    movie=OUT/"FABRITIUS_GOLDFINCH_CINEMA_MUSEUM_V86_REVIEW.mp4"
    cmd=["ffmpeg","-hide_banner","-loglevel","error","-y","-f","rawvideo","-pix_fmt","rgb24",
         "-s",f"{W}x{H}","-r",str(FPS),"-i","pipe:0","-c:v","libx264",
         "-preset","veryfast","-crf","19","-pix_fmt","yuv420p","-movflags","+faststart",
         str(OUT/"SILENT.mp4")]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    prev=None;peak=0;above=0
    moments={0,3,7,12,18,25,34,43}
    for n in range(N):
        t=n/FPS
        z,x,y=pose(t)
        aw=round(cw/z); ah=round(ch/z)
        x0=max(0,min(cw-aw,round(x*cw-aw/2)))
        y0=max(0,min(ch-ah,round(y*ch-ah/2)))
        frame=photo_canvas.crop((x0,y0,x0+aw,y0+ah)).resize((W,H),Image.Resampling.BICUBIC)
        if t<3.6:
            overlay=Image.new("RGBA",(W,H)); d=ImageDraw.Draw(overlay)
            alpha=225 if t<2.8 else round(225*(3.6-t)/.8)
            d.rounded_rectangle((33,938,687,1090),radius=10,fill=(8,10,15,alpha))
            d.text((W//2,963),"THE GOLDFINCH",font=title,anchor="ma",fill=(255,250,235,alpha))
            d.text((W//2,1031),"CAREL FABRITIUS · 1654",font=artist,anchor="ma",fill=(225,212,186,alpha))
            frame=Image.alpha_composite(frame.convert("RGBA"),overlay).convert("RGB")
        if n==0:frame.save(OUT/"COVER.jpg",quality=94)
        if n%FPS==0 and n//FPS in moments:
            frame.save(OUT/f"QA_{n//FPS:02}.jpg",quality=87)
        gray=np.asarray(frame.resize((90,160),Image.Resampling.BILINEAR).convert("L"),dtype=np.int16)
        if prev is not None:
            mad=float(np.abs(gray-prev).mean());peak=max(peak,mad);above+=(mad>35)
        prev=gray
        proc.stdin.write(frame.tobytes())
    proc.stdin.close()
    code=proc.wait()
    assert code==0,("VIDEO_FFMPEG_ERROR",code)
    # Source recording starts with silence: shift 2.2s, fade gently at end.
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",
       "-i",str(OUT/"SILENT.mp4"),"-ss","2.2","-i",str(music),
       "-map","0:v","-map","1:a:0","-t",str(DURATION),
       "-af",f"volume=1.15,afade=t=out:st={DURATION-2}:d=2",
       "-c:v","copy","-c:a","aac","-b:a","160k","-movflags","+faststart",str(movie)],check=True)
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-xerror","-i",str(movie),"-f","null","-"],check=True)
    probe=json.loads(subprocess.check_output(["ffprobe","-v","error","-of","json",
           "-show_entries","format=duration,size:stream=codec_name,codec_type,width,height,r_frame_rate",str(movie)]))
    vs=[s for s in probe["streams"] if s["codec_type"]=="video"][0]
    assert vs["codec_name"]=="h264" and (vs["width"],vs["height"])==(720,1280)
    assert any(s["codec_name"]=="aac" for s in probe["streams"])
    assert 43.9<float(probe["format"]["duration"])<44.2
    qa={"slot":"cinema_museum","version":"V86 REVIEW alternative to V50, NOT fifth variant",
        "human_v25_approval":False,"full_speed_human_review":"pending",
        "museum_room":"Photo-based artistic layout; NOT a photograph of the current museum gallery",
        "frame":"Exact painting in Sailko 2017 photograph, CC BY 3.0",
        "film_sha256":SHA(movie),"film_bytes":movie.stat().st_size,
        "actual_frame_photo_sha256":SHA(photo),"music_recording_sha256":SHA(music),
        "photo_origin_url":source,"duration_seconds":float(probe["format"]["duration"]),
        "v57_peak_grayscale_MAD":peak,"v57_over_35":above,"full_decode_pass":True}
    (OUT/"QA_V86.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n")
    assert above==0,("V57_BROKEN_CAMERA",peak,above)
    (OUT/"SOURCES_RIGHTS.md").write_text(
      "Artwork: Carel Fabritius, The Goldfinch, 1654, Mauritshuis inv. 605, 33.5×22.8 cm.\n"
      "Museum https://www.mauritshuis.nl/en/our-collection/artworks/605-the-goldfinch\n"
      "Exact painting/frame photograph by Sailko, 2017, CC BY 3.0. Photo may have been optically cropped/animated.\n"
      "https://commons.wikimedia.org/wiki/File:Carel_fabritius,_il_cardellino,_1654,_01.jpg\n"
      "https://creativecommons.org/licenses/by/3.0/\n"
      "Musica: Water Lily — Kevin MacLeod (incompetech.com), CC BY 4.0.\n"
      "https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1400035\n"
      "https://creativecommons.org/licenses/by/4.0/\n"
      "This film shows a real documentary frame PHOTO, but background is digitally transformed from that photo.\n"
      "Not presented as Mauritshuis actual room. No voice and no paid video AI.\n",encoding="utf8")
    posts=[
      ("FACEBOOK","Un cardellino, una catena quasi invisibile: scopri il dettaglio che cambia la lettura di questo piccolo capolavoro del 1654."),
      ("INSTAGRAM","Sembra vivo. Poi noti quella sottilissima catena. Il Cardellino di Fabritius, visto da vicino."),
      ("TIKTOK","Prima guarda gli occhi. Poi cerca la catena. Nel 1654 Fabritius ha dipinto un'illusione che inquieta ancora."),
      ("YOUTUBE","The Goldfinch — il dettaglio della catena e il virtuosismo pittorico di Carel Fabritius nel Mauritshuis.") ]
    credits="\n\nFoto cornice esatta: Sailko (2017), CC BY 3.0; inquadratura modificata. Opera PD, Mauritshuis inv. 605. Musica Water Lily — Kevin MacLeod, CC BY 4.0 (incompetech.com). Sala attorno al quadro: trattamento digitale, non documentazione museale."
    for platform,copy in posts:
        (OUT/f"POST_{platform}.txt").write_text(copy+credits+"\n",encoding="utf8")
    for name,include in [
       ("FABRITIUS_GOLDFINCH_CINEMA_MUSEUM_V86_ANDROID.zip",[movie,OUT/"QA_V86.json",OUT/"SOURCES_RIGHTS.md"]),
       ("FABRITIUS_GOLDFINCH_CINEMA_MUSEUM_V86_COMPLETO.zip",[movie,photo,music,OUT/"COVER.jpg",OUT/"QA_V86.json",OUT/"SOURCES_RIGHTS.md"]+
          list(OUT.glob("POST_*.txt"))+list(OUT.glob("QA_??.jpg")))]:
        zp=OUT/name
        with zipfile.ZipFile(zp,"w",allowZip64=True) as zf:
            for p in include:zf.write(p,arcname=p.name)
        with zipfile.ZipFile(zp) as zf:assert zf.testzip() is None
        qa[name]={"sha256":SHA(zp),"bytes":zp.stat().st_size}
    (OUT/"QA_V86.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n")
    (OUT/"SILENT.mp4").unlink(missing_ok=True)
    print("ARTVISION_GOLDFINCH_V86_REAL_MP4_QA_PASS",json.dumps(qa),flush=True)
if __name__=="__main__":main()
