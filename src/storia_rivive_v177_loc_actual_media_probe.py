#!/usr/bin/env python3
"""V177: inspect REAL exact LOC film bytes, not metadata/ProRes file extensions.

Actual item: A Corner in Wheat (1909), https://www.loc.gov/item/2012600307/.
URLs were discovered and verified against LOC ?fo=json in V175.
Do not rediscover item repeatedly: LOC API rate limited the unrelated V98 control.
MP4 <=100 MiB: SHA256 whole file + ffprobe + five original decoded frames.
MOV: HEAD + bounded first 64 KiB sample only (never assert full-resolution),
and full inspection only if <=100 MiB to avoid huge ProRes copies.
No social use; staged narrative, not candid street documentary; Italian rights pending.
"""
from __future__ import annotations
import argparse,hashlib,json,re,subprocess
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlparse

ITEM="2012600307"
ARCHIVE_PAGE="https://www.loc.gov/item/"+ITEM+"/"
MP4="https://tile.loc.gov/storage-services/service/mbrs/ntscrm/00047539/00047539.mp4"
MOV="https://tile.loc.gov/storage-services/service/mbrs/ntscrm/00047539/00047539.mov"
ALLOWED_HOST="tile.loc.gov"
UA="LaStoriaRiviveRealMediaQuality/1.0 (GGIANLUCAA/Tra-le-pagine-)"
DOWNLOAD_CAP=100*1024*1024
HEADER_CAP=65536


def ensure_url(s:str)->str:
    p=urlparse(s)
    if p.scheme!="https" or p.hostname!=ALLOWED_HOST or p.username or p.password or p.port not in (None,443):
        raise ValueError("UNTRUSTED_MEDIA_ORIGIN")
    if s not in (MP4,MOV):
        raise ValueError("SOURCE_NOT_V175_FROZEN_ITEM")
    return s


def probe_remote_headers(url:str)->dict:
    url=ensure_url(url)
    req=Request(url,headers={"User-Agent":UA},method="HEAD")
    with urlopen(req,timeout=25) as f:
        length=f.headers.get("Content-Length")
        total=int(length) if length and re.fullmatch(r"[0-9]+",length) else None
        return {"status_code":f.status,"content_length_bytes":total,
               "content_type":str(f.headers.get("Content-Type",""))[:100],
               "accept_ranges":str(f.headers.get("Accept-Ranges",""))[:40]}


def short_range(url:str)->dict:
    url=ensure_url(url)
    req=Request(url,headers={"User-Agent":UA,"Range":"bytes=0-65535"})
    with urlopen(req,timeout=30) as response:
        part=response.read(HEADER_CAP)
        if len(part)<32: raise ValueError("TRUNCATED_VIDEO_HEADER")
        return {"status_code":response.status,"read_bytes":len(part),
                "range_honored":response.status==206,
                "sha256_first_64k":hashlib.sha256(part).hexdigest(),
                "looks_like_iso_bmff":b"ftyp" in part[:32],
                "note":"First 64KiB alone DO NOT establish native/encoded raster; no full media decode"}


def stream_exact(url:str,out:Path,claimed_size:int)->dict:
    url=ensure_url(url)
    if claimed_size<=0 or claimed_size>DOWNLOAD_CAP:
        raise ValueError("REFUSE_FULL_DOWNLOAD_OVER_BYTE_CAP")
    out.parent.mkdir(parents=True,exist_ok=True)
    h=hashlib.sha256();n=0
    try:
        with urlopen(Request(url,headers={"User-Agent":UA}),timeout=75) as src,out.open("wb") as dst:
            while True:
                data=src.read(min(1024*1024,DOWNLOAD_CAP-n+1))
                if not data:break
                n+=len(data)
                if n>DOWNLOAD_CAP:raise ValueError("LIVE_DOWNLOAD_EXCEEDED_CAP")
                dst.write(data);h.update(data)
        if n != claimed_size:raise ValueError("VIDEO_BYTE_LENGTH_MISMATCH")
        return {"exact_download_bytes":n,"sha256":h.hexdigest()}
    except Exception:
        out.unlink(missing_ok=True)
        raise


def ffprobe(path:Path)->dict:
    p=subprocess.run(["ffprobe","-v","error","-show_entries",
       "stream=codec_type,codec_name,width,height,sample_aspect_ratio:format=duration",
       "-of","json",str(path)],capture_output=True,text=True,timeout=45,check=True)
    doc=json.loads(p.stdout)
    video=next((s for s in doc.get("streams",[]) if s.get("codec_type")=="video"),None)
    if not video:raise ValueError("FULL_FILE_HAS_NO_VIDEO")
    w,h=int(video["width"]),int(video["height"])
    dur=float(doc["format"]["duration"])
    if not 160<=w<=8000 or not 120<=h<=6000 or not 10<=dur<=3600:
        raise ValueError("VIDEO_RASTER_OR_DURATION_INVALID")
    cropw=min(w,round(h*9/16))
    native_9x16_ratio=(cropw*h)/(720*1280)
    # This measures actual *encoded pixels*, not whether a 35mm film was optically
    # rescanned, interpolated, or already upscaled.
    return {"encoded_width":w,"encoded_height":h,"encoded_video_codec":video.get("codec_name"),
            "encoded_sample_aspect_ratio":video.get("sample_aspect_ratio"),
            "duration_seconds":round(dur,4),"portrait_crop_source_pixels":[cropw,h],
            "native_encoded_crop_area_ratio_to_720x1280":round(native_9x16_ratio,4),
            "passes_V176_minimum_encoded_pixel_screen":h>=1000 and native_9x16_ratio>=.64,
            "optical_film_scan_native_hd_verified":False,
            "photoreal_human_faces_verified":False}


def real_frames(path:Path,duration:float,out:Path)->dict:
    from PIL import Image,ImageDraw
    out.mkdir(parents=True,exist_ok=True)
    board=Image.new("RGB",(5*300,360),(19,19,19));draw=ImageDraw.Draw(board)
    frame_info=[]
    for i,fraction in enumerate((.1,.28,.46,.64,.82),1):
        sec=round(duration*fraction,2)
        image_path=out/f"LOC_ORIGINAL_REAL_FRAME_{i:02}.png"
        subprocess.run(["ffmpeg","-nostdin","-v","error","-y","-ss",str(sec),
          "-i",str(path),"-frames:v","1",str(image_path)],check=True,timeout=50)
        if not image_path.is_file() or image_path.stat().st_size<1000:
            raise ValueError("DECODED_SOURCE_FRAME_MISSING")
        with Image.open(image_path) as p:im=p.convert("RGB")
        im.thumbnail((292,320))
        board.paste(im,((i-1)*300+(300-im.width)//2,33+(320-im.height)//2))
        draw.text(((i-1)*300+7,5),f"1909 source {sec:.1f}s",fill="white")
        frame_info.append({"pts_s":sec,"file":image_path.name,
                           "sha256":hashlib.sha256(image_path.read_bytes()).hexdigest()})
    board.save(out/"LOC_FIVE_UNRETOUCHED_FRAMES_PRIVATE.jpg",quality=90)
    return {"five_original_png_decoded":True,
            "five_distinct_movie_camera_shots_artistically_verified":False,
            "sampled_actual_frames":frame_info}


def execute(out:Path)->dict:
    out.mkdir(parents=True,exist_ok=True)
    result={"version":"V177","loc_item":ITEM,"source_page":ARCHIVE_PAGE,
      "source_kind":"STAGED_1909_FICTION_NOT_CANDID_REAL_STREET_DOCUMENTARY",
      "only_exact_LOC_discovered_urls":True,
      "rights_italy":"PENDING_NOT_CLEARED",
      "no_paid_provider_requests":True,"vidu_credits_spent":0,
      "not_final_video":True,"auto_social_publish":False,
      "human_artist_quality_approved":False,"candidate_rejected_or_needs_review":True,
      "formats":{}}
    try:
        for label,uri in (("mp4",MP4),("mov",MOV)):
            state={"url":uri,"download_full_media_allowed":False,"native_hd_verified":False}
            try:
                state["head"]=probe_remote_headers(uri)
                state["header_sample"]=short_range(uri)
                total=state["head"]["content_length_bytes"]
                if total is None:
                    state["status"]="UNKNOWN_CONTENT_LENGTH_NO_FULL_DOWNLOAD"
                elif total>DOWNLOAD_CAP:
                    state["status"]="TOO_LARGE_FULL_DOWNLOAD_SKIPPED_ONLY_64K_PROBE"
                elif total<100000:
                    state["status"]="SUSPICIOUSLY_SMALL_MEDIA_NO_FULL_DOWNLOAD"
                elif label=="mov":
                    # If MOV is small enough, run a real sample; never claim resolution
                    # from an extension. No advantage over MP4 if both raster equal.
                    state["status"]="MOV_METADATA_ONLY_FULL_DOWNLOAD_NOT_REQUIRED"
                else:
                    state["download_full_media_allowed"]=True
                    target=out/"TEMP_LOC_RESEARCH_SOURCE.mp4"
                    try:
                        state["byte_verified"]=stream_exact(uri,target,total)
                        state["real_ffprobe"]=ffprobe(target)
                        state.update(real_frames(target,state["real_ffprobe"]["duration_seconds"],out))
                        state["status"]="REAL_MP4_ENCODED_RASTER_VERIFIED_REVIEW_REQUIRED"
                    finally:
                        target.unlink(missing_ok=True)
            except Exception as e:
                state["status"]="LOC_DOWNLOAD_OR_INSPECTION_BLOCKED"
                state["error_type"]=type(e).__name__
                state["error_summary"]=str(e)[:180]
            result["formats"][label]=state
        result["status"]="SCOUT_COMPLETE_NO_MASTER" if any(
          x["status"]!="LOC_DOWNLOAD_OR_INSPECTION_BLOCKED" for x in result["formats"].values()
        ) else "SCOUT_BLOCKED_LOC_MEDIA_ENDPOINTS"
    except Exception as exc:
        result["status"]="SCOUT_BLOCKED_NO_PRODUCTION"
        result["error_type"]=type(exc).__name__
    finally:
        for p in out.glob("TEMP_LOC_RESEARCH_SOURCE.*"):
            p.unlink(missing_ok=True)
        (out/"V177_REAL_LOC_FILM_BYTE_QA.json").write_text(
           json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return result


def main()->None:
    a=argparse.ArgumentParser()
    a.add_argument("--out",type=Path,required=True)
    cfg=a.parse_args()
    result=execute(cfg.out)
    print(json.dumps({"status":result["status"],"item":ITEM,
      "mp4_status":result["formats"].get("mp4",{}).get("status"),
      "mp4_encoded_raster":result["formats"].get("mp4",{}).get("real_ffprobe"),
      "mov_status":result["formats"].get("mov",{}).get("status"),
      "credits":0,"published":False}))


if __name__=="__main__":main()
