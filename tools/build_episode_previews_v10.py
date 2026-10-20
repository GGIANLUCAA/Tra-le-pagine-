#!/usr/bin/env python3
"""Create small honest episode posters from images already in the public repository.
No image generation, network, TTS, or MP4 rendering; never publishes private videos.
"""
from __future__ import annotations
import io
import json
import re
import zipfile
from pathlib import Path
from PIL import Image, ImageOps, UnidentifiedImageError

SAFE_SLUG = re.compile(r"^[0-9]{2}_[a-z0-9_]+$")
SAFE_IMAGE = re.compile(r"^scena_[0-9]{2}\.(?:jpg|jpeg|png|webp)$", re.I)
MAX_BYTES = 12_000_000
MAX_FRAME = 5


def prepare_image(raw, dest, max_size=(700, 1050)):
    if len(raw) > MAX_BYTES:
        raise ValueError("Image over limit")
    with Image.open(io.BytesIO(raw)) as src:
        src.verify()
    with Image.open(io.BytesIO(raw)) as src:
        if src.width < 250 or src.height < 250:
            raise ValueError("Image too small")
        picture = ImageOps.exif_transpose(src).convert("RGB")
        picture.thumbnail(max_size, Image.Resampling.LANCZOS)
        dest.parent.mkdir(parents=True, exist_ok=True)
        picture.save(dest, "JPEG", quality=79, optimize=True)
        return {"file": dest.name, "width": picture.width, "height": picture.height}


def zip_images(path):
    with zipfile.ZipFile(path) as archive:
        # Pillow may decode only approved small images to protect runner resource usage.
        entries = []
        for item in archive.infolist():
            name = Path(item.filename).name.lower()
            if item.is_dir() or not (SAFE_IMAGE.match(name) or name == "copertina.jpg"):
                continue
            if item.file_size > MAX_BYTES or item.compress_size > MAX_BYTES:
                continue
            entries.append((name, item))
        entries.sort(key=lambda i: (i[0] != "copertina.jpg", i[0]))
        for name, entry in entries[:MAX_FRAME+1]:
            yield name, archive.read(entry)


def find_images(episode):
    zip_path = episode/"scene_premium.zip"
    if zip_path.is_file():
        return list(zip_images(zip_path))
    root = episode/"images"
    if root.is_dir():
        out=[]
        for p in sorted(root.iterdir()):
            if p.is_file() and SAFE_IMAGE.match(p.name) and p.stat().st_size<=MAX_BYTES:
                out.append((p.name.lower(), p.read_bytes()))
            if len(out)>=MAX_FRAME+1:break
        return out
    return []


def build(repo_root):
    root=Path(repo_root)
    ep_dir=root/"episodes"
    dest=root/"docs"/"previews"
    dest.mkdir(parents=True,exist_ok=True)
    gallery={}
    for episode in sorted(ep_dir.iterdir()):
        if not episode.is_dir() or not SAFE_SLUG.fullmatch(episode.name):
            continue
        meta_file=episode/"metadata.json"
        if not meta_file.is_file():
            continue
        meta=json.loads(meta_file.read_text(encoding="utf-8"))
        item={
            "title":str(meta.get("title",episode.name))[:130],
            "author":str(meta.get("author",""))[:90],
            "poster":None,"frames":[],"visual_status":"missing",
            "video_url":None, "public_video":False
        }
        sources=find_images(episode)
        selected=0
        for name,raw in sources:
            if selected >= MAX_FRAME:break
            output=dest/episode.name/("cover.jpg" if selected == 0 else f"frame_{selected+1:02}.jpg")
            try:
                result=prepare_image(raw,output)
            except (ValueError, UnidentifiedImageError, OSError, SyntaxError):
                continue
            webpath="previews/"+episode.name+"/"+result["file"]
            if selected==0:
                item["poster"]=webpath
            item["frames"].append({"src":webpath,"original_name":name})
            selected+=1
        if selected:
            item["visual_status"]="real_episode_images"
        # No automatic publication of MP4 from Actions artifacts.
        # Future video URLs may only be manually whitelisted with explicit consent.
        gallery[episode.name]=item
    (dest/"catalog.json").write_text(
        json.dumps({"version":10,"generated_from":"repository-existing-media",
                    "videos_published_automatically":False,"episodes":gallery},
                   ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("EPISODE POSTERS:",len(gallery),"episodes,",
          sum(bool(v["poster"]) for v in gallery.values()),"with real images.")


if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--repo",default=".")
    args=p.parse_args()
    build(args.repo)
