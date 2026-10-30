#!/usr/bin/env python3
"""V101: bounded archival film scout. No image-generation or paid providers.
Media, copyright and identity require independent review before production.
"""
import argparse,hashlib,json,subprocess
from pathlib import Path
from urllib.parse import urlparse,unquote,urlencode
from urllib.request import urlopen,Request

MAX_BYTES=160*1024*1024
USER_AGENT="LaStoriaRiviveHistoricalResearch/1.0 (GitHub GGIANLUCAA/Tra-le-pagine-)"
def metadata(page):
    u=urlparse(page)
    if u.scheme!="https" or u.netloc!="commons.wikimedia.org" or not u.path.startswith("/wiki/File:"):
        raise ValueError("Only Commons file pages are allowed")
    title=unquote(u.path[len("/wiki/"):]).replace("_"," ")
    uri="https://commons.wikimedia.org/w/api.php?"+urlencode({
        "action":"query","format":"json","formatversion":"2","titles":title,
        "prop":"imageinfo","iiprop":"url|size|extmetadata"})
    with urlopen(Request(uri,headers={"User-Agent":USER_AGENT}),timeout=30) as response:
        data=json.load(response)
    pages=data.get("query",{}).get("pages",[])
    if not pages or not pages[0].get("imageinfo"):raise ValueError("Missing archival file metadata")
    info=pages[0]["imageinfo"][0];link=info.get("url","")
    v=urlparse(link)
    if v.scheme!="https" or v.netloc!="upload.wikimedia.org" or not link.lower().endswith((".webm",".ogv",".mp4",".mov")):
        raise ValueError("Unapproved archive video URL")
    return {"source_page":page,"filename":title,"download_url":link,
            "size_bytes":info.get("size"),
            "license_metadata":info.get("extmetadata",{}).get("LicenseShortName",{}).get("value","UNKNOWN"),
            "historical_rights_italy_approved":False,"social_publish_permitted":False}

def inspect(page,outdir):
    outdir.mkdir(parents=True,exist_ok=True)
    m=metadata(page)
    size=m["size_bytes"]
    if not isinstance(size,int) or size<=0 or size>MAX_BYTES:
        m["status"]="MANUAL_ACQUISITION_REQUIRED_SIZE_LIMIT";return m
    film=outdir/"ORIGINAL_ARCHIVE.webm"
    with urlopen(Request(m["download_url"],headers={"User-Agent":USER_AGENT}),timeout=60) as src,film.open("wb") as target:
        n=0;h=hashlib.sha256()
        while True:
            buf=src.read(1024*1024)
            if not buf:break
            n+=len(buf)
            if n>MAX_BYTES:raise ValueError("Download byte cap exceeded")
            h.update(buf);target.write(buf)
    if n!=size:raise ValueError("Source media length mismatch")
    m["original_sha256"]=h.hexdigest()
    probe=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","json",str(film)],
                         capture_output=True,text=True,timeout=35,check=True)
    duration=float(json.loads(probe.stdout)["format"]["duration"])
    if not 1<=duration<=10000:raise ValueError("Source duration suspicious")
    m["duration_s"]=duration
    frames=outdir/"original_frames";frames.mkdir(exist_ok=True)
    period=max(1.0,duration/12)
    subprocess.run(["ffmpeg","-nostdin","-y","-v","error","-i",str(film),
                    "-vf","fps=1/"+str(round(period,4)),
                    "-frames:v","12",str(frames/"frame_%02d.png")],timeout=150,check=True)
    files=sorted(frames.glob("frame_*.png"))
    if len(files)<3:raise ValueError("Not enough real film frames")
    from PIL import Image,ImageDraw
    board=Image.new("RGB",(1440,792),(18,18,18));draw=ImageDraw.Draw(board)
    for k,p in enumerate(files[:12]):
        im=Image.open(p).convert("RGB");im.thumbnail((350,236))
        x=(k%4)*360+4;y=(k//4)*264+4
        board.paste(im,(x,y+23))
        draw.text((x,y+3),"ORIGINAL t~"+str(round(k*period,1))+"s",fill=(240,240,240))
    board.save(outdir/"ORIGINAL_FILM_CONTACT_SHEET.jpg",quality=90)
    m["source_frames_extracted"]=len(files)
    m["status"]="REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW"
    return m

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--order",required=True);p.add_argument("--out",required=True)
    a=p.parse_args();dir=Path(a.out);dir.mkdir(parents=True,exist_ok=True)
    order=json.loads(Path(a.order).read_text(encoding="utf-8"))
    try:report=inspect(order["source_page"],dir)
    except Exception as e:
        print("SOURCE_SCOUT_ERROR",type(e).__name__,str(e)[:300])
        report={"status":"SOURCE_SCOUT_BLOCKED_NO_PRODUCTION","error_type":type(e).__name__,
                "reason":str(e)[:300],"social_publish_permitted":False}
    (dir/"SCOUT_REPORT.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":report["status"],"paid_api_calls":0,"published":False}))

if __name__=="__main__":main()
