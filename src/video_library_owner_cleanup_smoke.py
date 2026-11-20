#!/usr/bin/env python3
"""Live public catalogue smoke after exact owner rejection, read-only."""
import json
from pathlib import Path
import urllib.parse
import requests

BASE="https://video-library-studio.600led.workers.dev"
MANIFEST=Path("reports/video_library_owner_discard_20261116.json")
TARGETS=[i["key"] for i in json.loads(MANIFEST.read_text())["files"]]


def main():
    sess=requests.Session()
    r=sess.get(BASE+"/api/catalog",timeout=45,headers={"Cache-Control":"no-cache"})
    r.raise_for_status()
    c=r.json()
    assert c.get("admin") is False, "Guest must not have admin access"
    items=c.get("items",[])
    assert isinstance(items,list) and len(items)>0
    visible={x["key"]:x for x in items}
    rejected=[key for key in TARGETS if key in visible or "gpt:"+key in visible]
    assert not rejected, "Previously deleted or ghost video still public: "+repr(rejected)
    short=[x["key"] for x in items if x.get("available") is True
           and isinstance(x.get("duration"),(float,int))
           and 0<float(x["duration"])<=9]
    assert not short, "Short technical source clips remain in gallery: "+repr(short[:12])
    assert c.get("available",0)<730, "Expected cleaned MP4 gallery"
    # Check deleted file route; not an artifact import, not a server write.
    for name in ("glow.mp4","01_fur_elise.mp4",
                 "HYPERLUMEN_MOZART_1080_SOCIAL(1).mp4"):
        with sess.get(BASE+"/media/"+urllib.parse.quote(name,safe=""),
                      timeout=25,headers={"Range":"bytes=0-1023"},stream=True) as resp:
            assert resp.status_code==404, (name,resp.status_code)
    # Ensure a recent real ArtVision master still plays with HTTP Range.
    keeper="ARTVISION_BRUEGEL_PROVERBI.mp4"
    with sess.get(BASE+"/media/"+urllib.parse.quote(keeper,safe=""),
                  timeout=30,headers={"Range":"bytes=0-1023"},stream=True) as resp:
        assert resp.status_code==206,(keeper,resp.status_code)
        assert resp.headers.get("content-range","").startswith("bytes 0-1023/")
        assert int(resp.headers["content-length"])==1024
    print(json.dumps({"liveGuestCatalog":True,"available":c.get("available"),
                     "visibleEntries":len(items),"deletedAndGhostAbsent":len(TARGETS),
                     "shortIncompleteVisible":0,"bruegelRange206":True},indent=2))


if __name__=="__main__":
    main()
