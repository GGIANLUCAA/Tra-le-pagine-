#!/usr/bin/env python3
"""Owner-selected Rembrandt Night Watch: one authentic Cinema Standard review MP4.
No paid APIs, no fake museum, no invented voice or historical reconstruction.
One-shot production; NOT a 4x1 set, not owner-approved Gold.
"""
import hashlib, json, math, os, subprocess, urllib.request, wave
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont, ImageOps
import numpy as np

Image.MAX_IMAGE_PIXELS = 250_000_000
ROOT = Path("output/nightwatch_v132")
ROOT.mkdir(parents=True, exist_ok=True)
SOURCE = "https://upload.wikimedia.org/wikipedia/commons/9/94/The_Nightwatch_by_Rembrandt_-_Rijksmuseum.jpg"
SOURCE_PAGE = "https://commons.wikimedia.org/wiki/File:The_Nightwatch_by_Rembrandt_-_Rijksmuseum.jpg"
EXPECTED_SHA1 = "53db595a5a1bca243b152b175d65f0f2f1ab1ff8"
W,H,FPS = 720,1280,24

def checkrun(cmd):
    p=subprocess.run(list(map(str,cmd)),capture_output=True,text=True)
    if p.returncode: raise RuntimeError("Command failed: "+" ".join(map(str,cmd[:4]))+" "+p.stderr[-1600:])
    return p.stdout

def digest(path,alg="sha256"):
    h=hashlib.new(alg)
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()

def source():
    p=ROOT/"REMBRANDT_NIGHT_WATCH_ORIGINAL_RIJKSMUSEUM.jpg"
    if not p.exists():
        req=urllib.request.Request(SOURCE,headers={"User-Agent":"ArtVision-TraLePagine/1.0 (museum open-access research)"})
        with urllib.request.urlopen(req,timeout=100) as resp,open(p,"wb") as dst:
            assert "image" in resp.headers.get("content-type",""),"Invalid original source"
            while True:
                b=resp.read(1024*1024)
                if not b:break
                dst.write(b)
                assert dst.tell()<50_000_000,"Source size unexpected"
    assert digest(p,"sha1")==EXPECTED_SHA1,"Wrong file/version; refuse render"
    with Image.open(p) as img:
        assert img.size==(14168,11528),"Original dimensions changed"
        img.draft("RGB",(5400,5400))
        art=ImageOps.exif_transpose(img).convert("RGB")
        art.thumbnail((5200,5200),Image.Resampling.LANCZOS)
        return art, {"source_url":SOURCE,"file_page":SOURCE_PAGE,"sha1":EXPECTED_SHA1,"sha256":digest(p),"pixels":[14168,11528],"rights":"Wikimedia Commons PD-Art / Public Domain Mark, Rijksmuseum SK-C-5; territorial and distribution checks still required"}

def font(sz,serif=True):
    path="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf" if serif else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    try:return ImageFont.truetype(path,sz)
    except OSError:return ImageFont.load_default()

def whole(img):
    bg=img.resize((W,H),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(44))
    bg=ImageEnhance.Brightness(bg).enhance(.27)
    fg=img.copy();fg.thumbnail((W-24,H-220),Image.Resampling.LANCZOS)
    bg.paste(fg,((W-fg.width)//2,(H-fg.height)//2))
    return bg

def detail(img,fx,fy,height_frac):
    iw,ih=img.size
    crop_h=round(ih*height_frac)
    crop_w=round(crop_h*W/H)
    left=max(0,min(iw-crop_w,round(fx*iw-crop_w/2)))
    top=max(0,min(ih-crop_h,round(fy*ih-crop_h/2)))
    return img.crop((left,top,left+crop_w,top+crop_h)).resize((W,H),Image.Resampling.LANCZOS)

def title_card(img):
    im=whole(img);d=ImageDraw.Draw(im,"RGBA")
    d.rectangle((0,0,W,260),fill=(9,11,15,240))
    d.line((66,240,W-66,240),fill=(204,169,107,220),width=3)
    d.text((W//2,81),"THE NIGHT WATCH",font=font(43),anchor="mm",fill=(246,237,216))
    d.text((W//2,150),"REMBRANDT VAN RIJN",font=font(23,False),anchor="mm",fill=(214,204,183))
    d.text((W//2,200),"1642  •  RIJKSMUSEUM",font=font(16,False),anchor="mm",fill=(198,189,171))
    return im

# Different semantic camera targets; coordinates are painting-relative.
# Holds differ by content, no invented detail or AI outpainting.
SHOTS=[
 ("cover",2.6,None),
 ("captain_red",5.1,(.47,.61,.51)),
 ("lieutenant_gold",5.7,(.61,.66,.44)),
 ("girl_in_light",5.4,(.30,.65,.36)),
 ("command_and_gesture",5.2,(.46,.48,.62)),
 ("musket_and_men",4.9,(.68,.42,.57)),
 ("drummer_right",5.0,(.90,.67,.49)),
 ("crowd_left",4.6,(.19,.57,.53)),
 ("two_officers",5.4,(.55,.63,.63)),
 ("whole",6.3,None)
]

def make_still(img,key,coords):
    if key=="cover":return title_card(img)
    if key=="whole":return whole(img)
    return detail(img,*coords)

def original_music(path,total):
    # Original ambient cinematic score, rendered locally, no copyrighted samples/API.
    rate=32000
    n=math.ceil(total*rate)
    t=np.arange(n,dtype=np.float32)/rate
    a=np.zeros(n,dtype=np.float32)
    phases=[(0,[110,164.81,220]),(total*.25,[98,146.83,196]),(total*.5,[82.41,123.47,164.81]),(total*.75,[110,164.81,220])]
    for i,(start,notes) in enumerate(phases):
        end=phases[i+1][0] if i+1<len(phases) else total
        mask=(t>=start)&(t<end)
        local=t[mask]-start
        for k,freq in enumerate(notes):
            a[mask]+=np.float32(.085/(k+1))*np.sin(np.float32(2*math.pi*freq)*local+np.float32(.25)*np.sin(np.float32(.11*2*math.pi)*local))
    for onset in np.arange(1.5,total-2,4.8):
        j=np.arange(int(onset*rate),min(n,int((onset+2.3)*rate)))
        x=j/rate-onset
        a[j]+=(.075*np.exp(-2.5*x)*np.sin(2*math.pi*55*x)).astype(np.float32)
    envelope=np.clip(np.minimum(np.minimum(t/1.5,(total-t)/2.3),1),0,1)
    pcm=(32760*np.tanh(a*2.4)*envelope*.84).astype("<i2")
    with wave.open(str(path),"wb") as out:
        out.setnchannels(1);out.setsampwidth(2);out.setframerate(rate);out.writeframes(pcm.tobytes())

def main():
    artwork,src=source()
    cards=ROOT/"frames";cards.mkdir(exist_ok=True)
    durations=[round(s*FPS)/FPS for _,s,_ in SHOTS]
    total=sum(durations)
    pieces=[]
    for idx,((key,seconds,coords),duration) in enumerate(zip(SHOTS,durations)):
        still=make_still(artwork,key,coords)
        stillpath=cards/f"{idx:02d}_{key}.jpg"
        still.save(stillpath,quality=92,subsampling=0)
        frames=round(duration*FPS)
        if key=="cover":pan="zoompan=z=1:d="+str(frames)+":s=720x1280:fps=24"
        elif key=="whole":pan="zoompan=z='min(1.015+on*0.00009,1.05)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d="+str(frames)+":s=720x1280:fps=24"
        elif idx%3==0:pan="zoompan=z=1.09:x='(iw-iw/zoom)*(on/"+str(frames)+")':y='ih/2-ih/zoom/2':d="+str(frames)+":s=720x1280:fps=24"
        elif idx%3==1:pan="zoompan=z='min(1+on*0.00038,1.07)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d="+str(frames)+":s=720x1280:fps=24"
        else:pan="zoompan=z=1.08:x='(iw-iw/zoom)*(1-on/"+str(frames)+")':y='ih/2-ih/zoom/2':d="+str(frames)+":s=720x1280:fps=24"
        part=ROOT/f"scene_{idx:02d}.mp4"
        checkrun(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",stillpath,"-vf",pan+",format=yuv420p","-frames:v",frames,"-an","-c:v","libx264","-preset","veryfast","-crf","20","-r",FPS,part])
        pieces.append(part)
    lst=ROOT/"concat.txt";lst.write_text("".join("file '"+p.resolve().as_posix()+"'\n" for p in pieces))
    silent=ROOT/"silent.mp4"
    checkrun(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0","-i",lst,"-c","copy",silent])
    wav=ROOT/"original_score.wav";original_music(wav,total)
    result=ROOT/"THE_NIGHT_WATCH_CINEMA_STANDARD_V132_REVIEW.mp4"
    checkrun(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",silent,"-i",wav,"-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","160k","-shortest","-movflags","+faststart","-metadata","comment","ArtVision Cinema Standard review, Rembrandt Rijksmuseum SK-C-5, public-domain painting, original music, no paid APIs",result])
    checkrun(["ffmpeg","-hide_banner","-loglevel","error","-xerror","-i",result,"-f","null","-"])
    summary=json.loads(checkrun(["ffprobe","-v","error","-show_entries","format=duration,size:stream=codec_name,width,height","-of","json",result]))
    assert len(summary["streams"])>=2
    assert int(summary["format"]["size"])>400000
    qa={"title":"The Night Watch","artist":"Rembrandt van Rijn","museum":"Rijksmuseum","inventory":"SK-C-5","role":"cinema_standard","version":"V132",
        "status":"rendered_needs_human_review_NOT_V25_Gold_NOT_4x1",
        "source":src,"source_no_ai_reconstruction":True,"music":"Original synthesized cinematic score in this script; no external audio sources, no API calls",
        "shots":[{"key":k,"seconds":d,"coordinates":c} for (k,_,c),d in zip(SHOTS,durations)],
        "duration_target_seconds":total,"result_file":result.name,"result_bytes":result.stat().st_size,"result_sha256":digest(result),
        "ffmpeg_full_decode":"PASS","ffprobe":summary,"copyright_publication_review_pending":True,"museum_produced":False,"critico_produced":False,
        "legacy_master_overwritten":False,"spent_api_credits":0,"social_published":False,"Gold_V25":False}
    (ROOT/"QA_NIGHT_WATCH_V132.json").write_text(json.dumps(qa,indent=2,ensure_ascii=False))
    # Keep deliverable small; remove only transient render intermediates.
    for p in pieces+[silent,wav,lst]:p.unlink()
    print(json.dumps({"status":"DONE_ONE_REVIEW_MP4","video":result.name,"sha256":qa["result_sha256"],"bytes":qa["result_bytes"],"seconds":summary["format"]["duration"]}))
if __name__=="__main__":main()
