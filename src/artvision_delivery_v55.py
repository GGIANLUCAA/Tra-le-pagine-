#!/usr/bin/env python3
"""ArtVision V55: verified local delivery bundle and independent archive checks.

No AI calls, publication or site upload. Never claims ChatGPT sandbox links work.
Creates one MP4+cover+4 social posts+sources+recipe+ZIP per actual film.
The live Video Library sync/import process remains separate and must be verified.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import subprocess
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

SITE = "https://video-library-studio.600led.workers.dev"
SOCIAL = ("facebook", "instagram", "tiktok", "youtube")
SCHEMA = "artvision-delivery-v55"
JPEG = ("jpg", "jpeg")
FIRST_SECONDS = (0.10, 1.0, 3.0, 5.0, 7.0)
CAPTION_OUTPUTS = {
    "facebook": "POST_FACEBOOK.txt",
    "instagram": "POST_INSTAGRAM.txt",
    "tiktok": "POST_TIKTOK.txt",
    "youtube": "POST_YOUTUBE.txt",
}


def filehash(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def name_slug(value):
    safe = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", safe).strip("_")
    if not safe:
        raise ValueError("Titolo privo di un identificativo valido")
    return safe[:85]


def require_file(path, endings=None):
    p = Path(path).resolve()
    if not p.is_file() or p.stat().st_size == 0:
        raise ValueError("File inesistente o vuoto: " + str(p))
    if endings and p.suffix.lower().lstrip(".") not in endings:
        raise ValueError("Estensione non ammessa: " + str(p))
    return p


def execute(args, timeout=120):
    return subprocess.run(args, check=True, timeout=timeout,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True).stdout


def inspect_video(video):
    result = json.loads(execute([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration:stream=codec_type,codec_name,width,height",
        "-of", "json", str(video)]))
    streams = result.get("streams", [])
    v = next((x for x in streams if x.get("codec_type") == "video"), None)
    a = next((x for x in streams if x.get("codec_type") == "audio"), None)
    duration = float(result.get("format", {}).get("duration") or 0)
    if not v or not a or not math.isfinite(duration) or duration <= 7.5:
        raise ValueError("ArtVision richiede MP4 con audio, video e almeno 7.5 secondi")
    if v.get("codec_name") != "h264" or a.get("codec_name") != "aac":
        raise ValueError("MP4 richiesto in H264/AAC")
    width, height = v.get("width", 0), v.get("height", 0)
    if not (width > 0 and height > width and abs(width / height - 9 / 16) < 0.035):
        raise ValueError("ArtVision richiede video verticale 9:16")
    if any(x.get("codec_type") == "subtitle" for x in streams):
        raise ValueError("Sottotitoli non ammessi dal preset ArtVision attivo")
    execute(["ffmpeg", "-nostdin", "-hide_banner", "-v", "error", "-xerror",
             "-i", str(video), "-f", "null", "-"], timeout=600)
    return {"duration": round(duration, 3), "width": width, "height": height,
            "video_codec": "h264", "audio_codec": "aac",
            "full_decode": "passed"}


def validate_social(posts):
    seen, contents = set(), {}
    for key in SOCIAL:
        p = require_file(posts[key], ("txt",))
        body = p.read_text(encoding="utf-8").strip()
        if len(body) < 45:
            raise ValueError("Testo social vuoto o troppo breve: " + key)
        norm = " ".join(body.casefold().split())
        if norm in seen:
            raise ValueError("Post duplicati: " + key)
        seen.add(norm)
        contents[key] = body
    return contents


def check_cover(cover):
    """Checks JPEG content is readable, not branding or artistic quality."""
    from PIL import Image
    with Image.open(cover) as im:
        im.verify()
    with Image.open(cover) as im:
        w, h = im.size
    if w < 320 or h < 500 or h <= w:
        raise ValueError("Copertina JPEG verticale troppo piccola o non valida")
    return {"width": w, "height": h}


def opening_frames(video, folder, duration):
    """Extract real frames, never infer that they are compelling or on-brand."""
    from PIL import Image, ImageDraw, ImageOps
    folder.mkdir(parents=True, exist_ok=True)
    shots = []
    for second in FIRST_SECONDS:
        if second >= duration - .1:
            continue
        path = folder / ("FRAME_%04dms.jpg" % round(second * 1000))
        execute(["ffmpeg", "-nostdin", "-hide_banner", "-v", "error", "-y",
                 "-ss", str(second), "-i", str(video), "-frames:v", "1",
                 "-vf", "scale=360:-2", "-q:v", "3", str(path)], timeout=70)
        require_file(path, JPEG)
        shots.append((second, path))
    if len(shots) != len(FIRST_SECONDS):
        raise ValueError("Non è stato possibile ispezionare tutti i primi 7 secondi")
    canvas = Image.new("RGB", (180 * len(shots), 360), (15, 20, 26))
    draw = ImageDraw.Draw(canvas)
    for i, (t, path) in enumerate(shots):
        with Image.open(path) as img:
            thumb = ImageOps.contain(img.convert("RGB"), (172, 325))
        canvas.paste(thumb, (i * 180 + (180 - thumb.width) // 2, 0))
        draw.text((i * 180 + 6, 331), f"{t:g} sec", fill=(245, 245, 245))
    contact = folder / "APERTURA_PRIMI_7_SECONDI.jpg"
    canvas.save(contact, quality=90)
    return [{"second": s, "frame": f"05_PRIMI_7_SECONDI/{p.name}",
             "sha256": filehash(p)} for s, p in shots]


def validate_opening_review(review, video_hash):
    """Human/agent visual attestation must match the *exact* video hash."""
    fields = ("watched_first_7_seconds", "title_and_artist_legible",
              "mobile_safe_composition", "authentic_specific_visual_hook",
              "no_accidental_black_frames", "voice_or_music_starts_appropriately")
    if not isinstance(review, dict) or review.get("video_sha256") != video_hash:
        return ["Apertura: revisione non presente o riferita a un altro MP4"]
    issues = []
    if review.get("reviewer") not in ("agent", "human"):
        issues.append("Apertura: revisore non dichiarato")
    if not isinstance(review.get("specific_observation"), str) or len(review["specific_observation"].strip()) < 40:
        issues.append("Apertura: manca osservazione concreta sul quadro e sui primi secondi")
    for field in fields:
        if review.get(field) is not True:
            issues.append("Apertura: non verificato " + field)
    return issues


def pack(video, cover, posts, rights, recipe, out, opening_review=None, release_contract=None):
    video = require_file(video, ("mp4",))
    cover = require_file(cover, JPEG)
    rights = require_file(rights, ("md", "txt"))
    recipe = require_file(recipe, ("json", "md", "txt"))
    info = inspect_video(video)
    cover_info = check_cover(cover)
    captions = validate_social(posts)
    out = Path(out).resolve()
    if out.exists() and any(out.iterdir()):
        raise ValueError("Destinazione non vuota: usare una nuova cartella, senza sovrascrivere")
    out.mkdir(parents=True, exist_ok=True)
    stem = name_slug(video.stem)
    stage = out / "PACCHETTO"
    (stage / "01_VIDEO").mkdir(parents=True)
    (stage / "02_COPERTINA").mkdir()
    (stage / "03_POST_SOCIAL").mkdir()
    (stage / "04_FONTI_E_RICETTA").mkdir()
    shutil.copy2(video, stage / "01_VIDEO" / (stem + ".mp4"))
    shutil.copy2(cover, stage / "02_COPERTINA" / "COPERTINA.jpg")
    for key, body in captions.items():
        (stage / "03_POST_SOCIAL" / CAPTION_OUTPUTS[key]).write_text(body + "\n", encoding="utf-8")
    shutil.copy2(rights, stage / "04_FONTI_E_RICETTA" / ("FONTI_E_DIRITTI" + rights.suffix))
    shutil.copy2(recipe, stage / "04_FONTI_E_RICETTA" / ("RICETTA" + recipe.suffix))
    frames = opening_frames(video, stage / "05_PRIMI_7_SECONDI", info["duration"])
    sha = filehash(video)
    # Existing V25 importer is fail-closed: an archive import cannot happen
    # without a review contract approved against the exact video SHA.
    if release_contract is not None:
        release_path = require_file(release_contract, ("json",))
        contract = json.loads(release_path.read_text(encoding="utf-8"))
        expected_reviews = ("opening", "visual", "cover", "music", "rights",
                            "full_watch", "replicability")
        checks = contract.get("reviews") if isinstance(contract, dict) else {}
        if (not isinstance(contract, dict)
                or contract.get("review_video_sha256") != sha
                or not isinstance(checks, dict)
                or any(not isinstance(checks.get(key), dict)
                       or checks[key].get("passed") is not True for key in expected_reviews)):
            raise ValueError("V25: contratto non approvato per SHA256 esatto del master")
        shutil.copy2(release_path, stage / "ARTVISION_CONTRACT_V25.json")
    if opening_review:
        review = json.loads(require_file(opening_review, ("json",)).read_text(encoding="utf-8"))
    else:
        review = None
    blockers = validate_opening_review(review, sha)
    if review is not None:
        (stage / "05_PRIMI_7_SECONDI" / "REVIEW_APERTURA.json").write_text(
            json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "schema": SCHEMA,
        "video_sha256": sha,
        "video_name": video.name,
        "video_info": info,
        "cover": {"sha256": filehash(cover), **cover_info},
        "first_seconds": {"actual_frames_extracted": frames,
                          "human_or_agent_visual_review": "pending" if blockers else "self_attested",
                          "opening_issues": blockers,
                          "note": "Frame extraction and self-attestation do not certify artistic merit."},
        "social_files": list(CAPTION_OUTPUTS.values()),
        "local_verified": True,
        "delivery": {
            "site_import_V25_contract": "exact_sha_review_verified" if release_contract else "missing_or_not_provided",
            "chatgpt_mp4_link": "not_tested_by_host",
            "chatgpt_zip_link": "not_tested_by_host",
            "archive_video": "not_checked",
            "archive_cover": "not_checked",
            "archive_social": "not_checked",
            "archive_zip": "not_checked",
            "complete_across_channels": False,
        },
        "release_gate": {
            "status": "packaged_needs_review_or_import" if blockers else "package_technically_verified",
            "opening_blockers": blockers,
            "artistic_approval": "not_certified",
            "rights_approval": "not_certified",
        },
    }
    (stage / "DELIVERY_MANIFEST_V55.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    zip_path = out / (stem + "_COMPLETO.zip")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED,
                         compresslevel=3, allowZip64=True) as archive:
        for member in sorted(p for p in stage.rglob("*") if p.is_file()):
            archive.write(member, member.relative_to(stage).as_posix())
    with zipfile.ZipFile(zip_path) as archive:
        if archive.testzip() is not None:
            raise ValueError("ZIP danneggiato")
        zhash = hashlib.sha256()
        with archive.open("01_VIDEO/" + stem + ".mp4") as member:
            for block in iter(lambda: member.read(1024 * 1024), b""):
                zhash.update(block)
        if zhash.hexdigest() != sha:
            raise ValueError("ZIP e MP4 originali non corrispondono")
        for key in SOCIAL:
            if "03_POST_SOCIAL/" + CAPTION_OUTPUTS[key] not in archive.namelist():
                raise ValueError("ZIP privo del post " + key)
    # Portable standalone files for ChatGPT handoff; platform links remain unverified.
    shutil.copy2(video, out / (stem + ".mp4"))
    shutil.copy2(cover, out / (stem + "_COPERTINA.jpg"))
    manifest["local_files"] = {
        "mp4": stem + ".mp4", "cover": stem + "_COPERTINA.jpg",
        "zip": zip_path.name, "sha256_zip": filehash(zip_path),
    }
    (out / "DELIVERY_STATUS_V55.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def check_site(video_key, timeout=25):
    """Check public catalog and byte-range playback only. No private admin assertions."""
    if (not isinstance(video_key, str) or "/" in video_key or "\\" in video_key
            or not re.fullmatch(r"[\w ().-]{1,190}\.mp4", video_key, re.I)):
        raise ValueError("Nome MP4 di archivio non valido")
    request = urllib.request.Request(SITE + "/api/catalog",
                                     headers={"User-Agent": "ArtVisionV55/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        catalog = json.load(response)
    item = next((x for x in catalog.get("items", []) if x.get("key") == video_key), None)
    outcome = {
        "schema": "artvision-site-check-v55", "site": SITE, "video_key": video_key,
        "catalog_visible": bool(item),
        "catalog_available": bool(item and item.get("available") is not False),
        "cover_referenced": bool(item and item.get("cover")),
        "playback_range_verified": False,
        "post_social_saved_verified": False,
        "zip_site_verified": False,
        "note": "Catalog playback check does not verify private dossier/ZIP or exact remote SHA256.",
    }
    if item and item.get("available") is not False:
        path = SITE + "/media/" + urllib.parse.quote(video_key, safe="")
        req = urllib.request.Request(path, headers={
            "User-Agent": "ArtVisionV55/1.0", "Range": "bytes=0-1"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                outcome["playback_range_verified"] = (
                    response.status == 206 and len(response.read(2)) == 2)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
            pass
    return outcome


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)
    b = sub.add_parser("pack", help="Create local verified video/social ZIP; no upload")
    for key in ("video", "cover", "facebook", "instagram", "tiktok", "youtube",
                "rights", "recipe", "out"):
        b.add_argument("--" + key, required=True)
    b.add_argument("--opening-review", help="Exact-sha visual opening review JSON")
    b.add_argument("--release-contract", help="Already-approved V25 JSON required for private R2 artifact import")
    s = sub.add_parser("site-check", help="Verify catalog and range playback, not private social dossier")
    s.add_argument("--key", required=True)
    args = ap.parse_args()
    if args.command == "pack":
        data = pack(args.video, args.cover,
                    {key: getattr(args, key) for key in SOCIAL},
                    args.rights, args.recipe, args.out, args.opening_review, args.release_contract)
    else:
        data = check_site(args.key)
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
