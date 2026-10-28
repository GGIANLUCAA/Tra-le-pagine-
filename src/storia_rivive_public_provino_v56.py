#!/usr/bin/env python3
"""V56: crea il provino CC0 Beirut 1919 in un ambiente GitHub Actions.
Solo filmato archivistico originale, viraggio monocromatico (NON colorizzazione AI).
Nessun servizio a pagamento o pubblicazione social.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import subprocess
import wave
import zipfile
from pathlib import Path

def run(*args):
    subprocess.run([str(x) for x in args], check=True)

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def music_original(out, duration=13, sr=32000):
    """Breve melodia nuova, generata offline; nessuna registrazione preesistente."""
    import array
    n=int(duration*sr)
    outarr=array.array("h")
    notes=[
        (0.0,146.83,3.8,0.11),(0.1,220,3.2,0.04),
        (0.3,293.66,1.3,0.12),(1.9,349.23,1.4,0.10),
        (3.4,392.0,1.5,0.09),(4.0,174.61,3.4,0.1),
        (5.1,440.0,1.7,0.10),(6.8,349.23,1.7,0.09),
        (8.1,261.63,3.5,0.08),(8.7,329.63,1.5,0.08),
        (10.3,293.66,2.5,0.13)
    ]
    for i in range(n):
        t=i/sr
        y=0.
        for st,f,length,volume in notes:
            dt=t-st
            if dt<0 or dt>=length: continue
            envelope=min(1.,dt/0.025)*math.exp(-dt/(length*.52))*min(1.,(length-dt)/0.2)
            y+=volume*envelope*(math.sin(2*math.pi*f*dt)+.16*math.sin(4*math.pi*f*dt)*math.exp(-dt*2))
        fade=min(1.,t/.8,(duration-t)/1.0)
        y*=max(0,fade)
        outarr.append(max(-32768,min(32767,round(y*26000))))
    with wave.open(str(out),"wb") as wav:
        wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(sr);wav.writeframes(outarr.tobytes())

def export(source, output):
    output.mkdir(parents=True,exist_ok=True)
    video=output/"BEIRUT_1919_VIDEO.mp4"
    music=output/"MUSICA_CREATA_PER_PROVINO.wav"
    music_original(music)
    filter_complex=(
      "[0:v]fps=24,scale=720:1280:force_original_aspect_ratio=increase,"
      "crop=720:1280:(iw-ow)/2:(ih-oh)/2,setsar=1,format=yuv420p,split=2[bw0][col0];"
      "[bw0]hue=s=0[bw];"
      "[col0]hue=s=0,colorchannelmixer=rr=0.95:rg=0.08:rb=0.02:"
      "gr=0.02:gg=0.86:gb=0.02:br=0.00:bg=0.03:bb=0.67[col];"
      "[bw][col]blend=all_expr='A*(1-clip((T-4)/2.5,0,1))+B*clip((T-4)/2.5,0,1)'[merged];"
      "[merged]drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
      "text='BEIRUT 1919':fontcolor=white:fontsize=43:borderw=2:"
      "bordercolor=black@0.65:x=(w-text_w)/2:y=110:enable='lt(t,3.3)'[vout]"
    )
    run("ffmpeg","-nostdin","-y","-v","error","-ss","137","-t","13",
        "-i",source,"-i",music,"-filter_complex",filter_complex,
        "-map","[vout]","-map","1:a:0","-c:v","libx264","-preset","veryfast",
        "-crf","20","-pix_fmt","yuv420p","-r","24","-c:a","aac",
        "-b:a","128k","-af","volume=0.28,afade=t=in:st=0:d=0.8,afade=t=out:st=11.8:d=1.1",
        "-t","13","-movflags","+faststart",video)
    run("ffmpeg","-nostdin","-hide_banner","-v","error","-xerror","-i",video,"-f","null","-")
    result=subprocess.run(["ffprobe","-v","error","-show_entries",
                           "format=duration:stream=codec_type,codec_name,width,height",
                           "-of","json",str(video)],check=True,capture_output=True,text=True)
    meta=json.loads(result.stdout)
    v=next(s for s in meta["streams"] if s.get("codec_type")=="video")
    a=next(s for s in meta["streams"] if s.get("codec_type")=="audio")
    assert (v["width"],v["height"],v["codec_name"],a["codec_name"]) == (720,1280,"h264","aac")
    run("ffmpeg","-nostdin","-y","-v","error","-ss","7.0","-i",video,
        "-frames:v","1",output/"FRAME_ORIGINALE_DAL_VIDEO.jpg")
    from PIL import Image,ImageDraw,ImageFont
    cover=Image.open(output/"FRAME_ORIGINALE_DAL_VIDEO.jpg").convert("RGB")
    w,h=cover.size
    draw=ImageDraw.Draw(cover)
    font="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    for y,t,size,fill in [(92,"LA STORIA RIVIVE",30,"#EFCF9E"),
                          (165,"BEIRUT",83,"white"),(260,"1919",65,"#EFCF9E")]:
        draw.text((w/2,y),t,font=ImageFont.truetype(font,size),anchor="mt",
                  fill=fill,stroke_width=3,stroke_fill="#111111")
    cover.save(output/"COVER.jpg",quality=91)
    texts={
    "FACEBOOK":"Beirut, 1919. Una strada percorsa da passanti e animali da trasporto: attimi quotidiani davanti a una cinepresa di oltre un secolo fa. Sono immagini autentiche del Musée Albert-Kahn. Il tono caldo è una rielaborazione digitale moderna, non il colore originale. Fonte: Lucien Le Saint, Scènes de rue AI13347, Wikimedia Commons, CC0. #Storia #Beirut #FilmatiStorici",
    "INSTAGRAM":"Una strada di Beirut nel 1919. Un cammello attraversa la scena, le persone proseguono la giornata: non sono comparse generate, ma figure riprese in un filmato d’archivio. Il viraggio caldo non è una vera colorizzazione storica. Fonte: Musée Albert-Kahn / Lucien Le Saint, CC0. #LaStoriaRivive #Beirut1919 #ArchivioStorico",
    "TIKTOK":"Guarda cosa passava per questa strada di Beirut nel 1919: il cammello e le persone provengono dalla vera ripresa storica, non da un video generato. Il colore seppia è un effetto moderno, non un restauro AI. Filmato AI13347, Lucien Le Saint, Musée Albert-Kahn (CC0). #StoriaVera #Beirut #1919",
    "YOUTUBE":"BEIRUT 1919 — Uno scorcio di vita quotidiana | La Storia Rivive\n\nUn estratto autentico del filmato Scènes de rue (AI13347) del Musée Albert-Kahn, attribuito a Lucien Le Saint. Il video originale mostra passanti e animali da trasporto per strada. Il nostro provino mantiene i fotogrammi originali e applica un semplice viraggio monocromatico: NON una vera colorizzazione AI. Fonte e licenza: https://commons.wikimedia.org/wiki/File:Sc%C3%A8nes_de_rue_-_AI13347.webm (CC0)."
    }
    for platform,copy in texts.items():
        (output/f"POST_{platform}.txt").write_text(copy+"\n",encoding="utf-8")
    rights={"original_source":"https://commons.wikimedia.org/wiki/File:Sc%C3%A8nes_de_rue_-_AI13347.webm",
            "institution":"Musée Albert-Kahn","archive_label":"Beirut, 1919",
            "operator_attributed":"Lucien Le Saint","license_declared":"CC0 1.0 on Commons",
            "license_check_before_social_publication":"required",
            "original_file_sha256":sha256(source),"video_sha256":sha256(video),
            "effect":"Sepia tint only; no AI colorization","music":"Original synthetic instrumental produced locally; no original historic audio",
            "video_status":"PROVINO, not Gold Master",
            "social_published":False,"private_video_library_verified":False}
    (output/"FONTI_DIRITTI.json").write_text(json.dumps(rights,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (output/"RICETTA.json").write_text(json.dumps({
        "render":"ffmpeg from actual Commons source, 137-150s, 720x1280, H264/AAC, 24fps",
        "tint":"same-source, same-frame B/W to monochrome warm tint between 4-6.5s",
        "colorization_ai":False,"credits_vidu_used":0,
        "full_decode_checked":True,
        "source_file_sha256":sha256(source),"video_file_sha256":sha256(video)},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (output/"QA.json").write_text(json.dumps({
        "status":"technical_pass_artistic_review_pending",
        "ffprobe":meta,"full_decode":"passed",
        "video_hash_sha256":sha256(video),
        "download_from_android":"unverified",
        "archive_sync":"pending",
        "social_publication":"no"},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    with zipfile.ZipFile(output/"BEIRUT_1919_COMPLETO.zip","w",compression=zipfile.ZIP_DEFLATED) as z:
        for file in [video,output/"COVER.jpg",output/"FONTI_DIRITTI.json",output/"RICETTA.json",output/"QA.json",*sorted(output.glob("POST_*.txt"))]:
            z.write(file,arcname=file.name)
    with zipfile.ZipFile(output/"BEIRUT_1919_COMPLETO.zip") as z:
        assert z.testzip() is None
    with zipfile.ZipFile(output/"BEIRUT_1919_SOLO_VIDEO.zip","w",compression=zipfile.ZIP_STORED) as z:
        z.write(video,arcname=video.name)
    print(json.dumps({"video":str(video),"zip":str(output/"BEIRUT_1919_COMPLETO.zip"),"sha":sha256(video),"duration":meta["format"]["duration"]}))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    if not a.source.is_file(): raise FileNotFoundError(a.source)
    export(a.source,a.out)
if __name__=="__main__": main()
