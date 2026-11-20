#!/usr/bin/env python3
import concurrent.futures,requests,urllib.parse,json
from pathlib import Path
TRACKS=["Eternal Hope","Serene","At Rest","Evening Fall (Piano)","Dreams Become Real","Ever Mindful","Calmant"]
BASE="https://incompetech.com/music/royalty-free/mp3-royaltyfree/"
def check(name):
    variants=[BASE+urllib.parse.quote(name,safe="")+".mp3",
              "https://www.incompetech.com/music/royalty-free/mp3-royaltyfree/"+urllib.parse.quote(name,safe="")+".mp3"]
    if name=="Eternal Hope":variants.insert(0,"https://upload.wikimedia.org/wikipedia/commons/5/54/Eternal_Hope_%28ISRC_USUAN1100238%29.mp3")
    errors=[]
    for url in variants:
        try:
            x=requests.get(url,timeout=45,stream=True,headers={"User-Agent":"ArtVision-Research/1.0"})
            x.raise_for_status()
            buf=b""
            for ch in x.iter_content(65536):
                buf+=ch
                if len(buf)>=327680:break
            if buf.startswith(b"ID3") or buf[:2]==bytes.fromhex("fffb") or b"\xff\xfb" in buf[:100]:
                x.close()
                out={"title":name,"download_url":url,"status":"PROBE_OK","content_type":x.headers.get("Content-Type"),"first_bytes":len(buf)}
                print("MUSIC_PROBE "+json.dumps(out),flush=True)
                return out
            errors.append(f"Not MP3 {url}: {buf[:20]!r}")
        except Exception as e: errors.append(f"{str(e)[:130]}")
    out={"title":name,"status":"FAILED","errors":errors}
    print("MUSIC_PROBE "+json.dumps(out),flush=True)
    return out
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:rows=list(pool.map(check,TRACKS))
p=Path("output/artvision_10_preflight/music_probe.json");p.parent.mkdir(parents=True,exist_ok=True)
p.write_text(json.dumps(rows,indent=2))
print("MUSIC_READY",sum(x["status"]=="PROBE_OK" for x in rows),"OF",len(TRACKS),flush=True)
