#!/usr/bin/env python3
"""Artemisia Gentileschi, Giuditta che decapita Oloferne (Uffizi, c. 1620)
ArtVision Cinema (silenzioso) — UN video, revisione privata dell'owner.

Regole rispettate:
  - nessuna chiamata API a pagamento, nessun TTS, nessun Vidu;
  - nessuno slot Museum, nessun Critico, nessun Gold, nessuna pubblicazione;
  - un solo MP4 Cinema da 1080x1920 con musica sotto licenza CC BY 4.0;
  - fonte autentica verificata via SHA256 prima del render (fail-closed);
  - firma fissa della serie ArtVision V6 (solo nome artista + MUSIC BY).

Lo script è determinista: stesso input -> stesso output.
"""
from __future__ import annotations
import hashlib
import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "modules" / "artvision"))
from identita_visiva_v6 import cover, signature  # identità grafica FISSA della serie

PROJECT = ROOT / "output" / "artvision_artemisia_giuditta"
PROJECT.mkdir(parents=True, exist_ok=True)
OUT = PROJECT

ARTIST = "Artemisia Gentileschi"
COMPOSER = "Kevin MacLeod"
TITLE_EN = "Judith Slaying Holofernes"
TITLE_IT = "Giuditta che decapita Oloferne"
YEAR = "c. 1620"
MUSEUM = "Galleria degli Uffizi, Firenze"
INVENTORY = "sala 90, inv. 1567"
COMMONS_PAGE = ("https://commons.wikimedia.org/wiki/File:"
                "Artemisia_Gentileschi_-_Giuditta_decapita_Oloferne_-_Google_Art_Project-Adjust.jpg")
COMMONS_KEY = "Artemisia Gentileschi - Giuditta decapita Oloferne - Google Art Project-Adjust.jpg"

# --- Fonte autentica: SHA256 già verificato in locale (dossier V13) ---
ART_SHA256 = "22952779803e03f1c3e289fc5ce894e6c1f37967f5172c143b924d388301c920"
ART_PIXELS = (2685, 3301)

# --- Musica: registrazione reale sotto licenza, verificata con ffprobe in locale ---
MUSIC_TITLE = "Ever Mindful"
MUSIC_ISRC = "USUAN1700033"
MUSIC_LICENSE = "CC BY 4.0"
MUSIC_SOURCE = "https://incompetech.com/music/royalty-free/?isrc=USUAN1700033"
MUSIC_MP3_URL = "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Ever%20Mindful.mp3"
MUSIC_MP3_SHA256 = "d09c03710d225e0978015cc62eed56cfa7405f589474ebd17f1591b152f1ad9a"
MUSIC_MP3_BYTES = 51172130
MUSIC_OFFSET_S = 20.0

FPS = 24
W, H = 1080, 1920


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(args, **kw):
    r = subprocess.run([str(x) for x in args], capture_output=True, **kw)
    if r.returncode:
        raise RuntimeError(r.stderr.decode(errors="replace")[-2000:])
    return r.stdout


def assert_owner_unlocked() -> dict:
    """Fail-closed: il render parte solo con lo sblocco esplicito registrato nel pilot lock."""
    lock = json.loads((ROOT / "config" / "artvision_pilot_lock_v58.json").read_text(encoding="utf-8"))
    if lock.get("schema") != "artvision-pilot-lock-v58" or lock.get("active") is not True:
        raise RuntimeError("PILOT LOCK assente o non attivo: render rifiutato")
    auth = lock.get("authorized_gentileschi_cinema_20261116", {})
    if not (auth.get("enabled") is True
            and auth.get("allowed_title") == TITLE_EN
            and auth.get("allowed_artist") == ARTIST
            and auth.get("no_paid_video_ai") is True
            and auth.get("no_social_auto_publish") is True
            and auth.get("museum_slots_authorized") is False):
        raise RuntimeError("PILOT LOCK: Gentileschi Cinema non autorizzato o scope incompatibile")
    return auth


def fetch(url: str, dest: Path, ua: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    with urllib.request.urlopen(req, timeout=110) as f:
        data = f.read()
    dest.write_bytes(data)
    return data


def resolve_artwork() -> tuple[Path, str]:
    """Usa l'asset locale se l'hash combacia; altrimenti scarica l'originale esatto da Commons."""
    local = PROJECT / "assets" / "giuditta_uffizi_full.jpg"
    if local.exists() and sha256(local) == ART_SHA256:
        with Image.open(local) as im:
            assert im.size == ART_PIXELS, f"pixel inattesi: {im.size}"
        print("LOCAL_EXACT_ARTWORK_VERIFIED", ART_SHA256, flush=True)
        return local, str(local)
    dest = OUT / "ORIGINAL_ARTWORK.jpg"
    key = COMMONS_KEY.replace(" ", "_")
    md5 = hashlib.md5(key.encode()).hexdigest()
    urls = [
        "https://upload.wikimedia.org/wikipedia/commons/" + md5[0] + "/" + md5[:2] + "/" + urllib.parse.quote(key, safe="._-"),
        "https://commons.wikimedia.org/wiki/Special:Redirect/file/" + urllib.parse.quote(key, safe="._-"),
    ]
    ua = "ArtVisionOwnerPrivateReview/1.0 (https://github.com/GGIANLUCAA/Tra-le-pagine-)"
    for url in urls:
        try:
            fetch(url, dest, ua)
            if sha256(dest) == ART_SHA256 and Image.open(dest).size == ART_PIXELS:
                print("DOWNLOADED_EXACT_ARTWORK_VERIFIED", ART_SHA256, flush=True)
                return dest, url
            print("ARTWORK_ATTEMPT_HASH_MISMATCH", url, flush=True)
        except Exception as e:  # noqa: BLE001
            print("ARTWORK_ATTEMPT_FAILED", type(e).__name__, str(e)[:160], flush=True)
    raise RuntimeError("FONTE AUTENTICA NON DISPONIBILE; NESSUN VIDEO PRODOTTO")


def resolve_music() -> Path:
    """Usa la registrazione reale: env, poi asset locale, poi download; sempre SHA256 verificato."""
    candidates = []
    env = os.environ.get("ARTVISION_MUSIC_MP3")
    if env:
        candidates.append(Path(env))
    candidates.append(PROJECT / "assets" / "music_ever_mindful.mp3")
    for c in candidates:
        if Path(c).exists() and sha256(c) == MUSIC_MP3_SHA256:
            print("LOCAL_EXACT_MUSIC_VERIFIED", MUSIC_MP3_SHA256, flush=True)
            return Path(c)
    dest = OUT / "ORIGINAL_MUSIC.mp3"
    fetch(MUSIC_MP3_URL, dest, "ArtVisionOwnerPrivateReview/1.0")
    got = sha256(dest)
    if got != MUSIC_MP3_SHA256:
        raise RuntimeError(f"registrazione non corrispondente all'hash verificato: {got}")
    print("DOWNLOADED_EXACT_MUSIC_VERIFIED", got, flush=True)
    return dest


def main() -> None:
    assert_owner_unlocked()
    art_path, art_url = resolve_artwork()
    music_src = resolve_music()

    src_img = Image.open(art_path).convert("RGB")
    src = np.asarray(src_img)[:, :, ::-1].copy()
    ah, aw = src.shape[:2]

    background = cv2.GaussianBlur(cv2.resize(src, (W, H), interpolation=cv2.INTER_AREA), (0, 0), 51)
    background = cv2.convertScaleAbs(background, alpha=0.30)
    wide = background.copy()
    full_w = min(W - 42, int((H - 300) * aw / ah))
    full_h = round(full_w * ah / aw)
    x0 = (W - full_w) // 2
    y0 = (H - full_h) // 2
    wide[y0:y0 + full_h, x0:x0 + full_w] = cv2.resize(src, (full_w, full_h), interpolation=cv2.INTER_AREA)

    def detail(p) -> np.ndarray:
        cx, cy, hfrac = p
        hh = min(ah, max(180, round(ah * hfrac)))
        ww = min(aw, max(100, round(hh * W / H)))
        x = max(0, min(aw - ww, round(cx * aw - ww / 2)))
        y = max(0, min(ah - hh, round(cy * ah - hh / 2)))
        return cv2.resize(src[y:y + hh, x:x + ww], (W, H), interpolation=cv2.INTER_AREA)

    # 14 inquadrature dagli stessi 14 punti del dossier V13. None = opera intera.
    # (etichetta, durata, crop iniziale, crop finale)  crop=(cx,cy,hfrac)
    shots: list = [
        ("FIRMA: NOME ARTISTA E MUSIC BY", 5.5, "SIGNATURE", None),
        ("OPERA INTERA: DUE DONNE, UN UOMO", 5.0, None, None),
        ("LENZUOLO BIANCO E SANGUE", 4.5, (0.27, 0.68, 0.34), (0.25, 0.70, 0.24)),
        ("VOLTO DI OLOFERNE: COSCIENTE, INERME", 4.0, (0.52, 0.43, 0.20), (0.52, 0.43, 0.20)),
        ("GETTO DI SANGUE DAL COLLO", 4.5, (0.62, 0.36, 0.30), (0.60, 0.37, 0.20)),
        ("VOLTO DI GIUDITTA: FERMEZZA E DISGUSTO", 5.0, (0.84, 0.41, 0.24), (0.84, 0.41, 0.24)),
        ("BRACCIO DESTRO E TORSIONE DEL BUSTO", 4.5, (0.71, 0.55, 0.38), (0.71, 0.57, 0.27)),
        ("LA SPADA LUNGA E LA MANO", 4.0, (0.63, 0.42, 0.30), (0.63, 0.42, 0.30)),
        ("VOLTO DELL'ANCELLA: CALMO", 5.0, (0.15, 0.40, 0.24), (0.15, 0.40, 0.24)),
        ("BRACCIALE IN ORO CON CAMMEI", 4.5, (0.74, 0.58, 0.22), (0.74, 0.59, 0.15)),
        ("VESTE IN DAMASCO GIALLO E MERLETTO", 4.5, (0.72, 0.73, 0.22), (0.72, 0.73, 0.33)),
        ("PIEGHE DEL VELLUTO ROSSO E FRANGE", 4.5, (0.30, 0.61, 0.36), (0.30, 0.62, 0.26)),
        ("RITORNO ALL'OPERA INTERA", 5.5, None, None),
        ("TENUTA FINALE, DISSOLVENZA IN NERO", 5.0, None, None),
    ]
    frame_counts = [round(s[1] * FPS) for s in shots]
    N = sum(frame_counts)
    DURATION = N / FPS
    assert len(shots) == 14 and 64.0 < DURATION < 68.0, DURATION
    last = len(shots) - 1

    # Copertina = volto di Giuditta in luce, con la stessa identità V6 della serie.
    cover_frame = cover(detail((0.83, 0.42, 0.30)), ARTIST, COMPOSER)
    cv2.imwrite(str(OUT / "COVER.jpg"), cover_frame, [cv2.IMWRITE_JPEG_QUALITY, 92])

    # Segmento musicale con licenza: taglio + dissolvenze, salvato per provenienza.
    segment = OUT / "LICENSED_MUSIC_SEGMENT.m4a"
    run(["ffmpeg", "-y", "-v", "error", "-ss", f"{MUSIC_OFFSET_S}",
         "-t", f"{DURATION + 0.6:.3f}", "-i", music_src,
         "-af", f"afade=t=in:st=0:d=2.0,afade=t=out:st={DURATION - 2.5:.3f}:d=2.5",
         "-c:a", "aac", "-b:a", "168k", segment])

    mp4 = OUT / "VIDEO_REVIEW.mp4"
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "pipe:0",
           "-i", str(segment), "-map", "0:v:0", "-map", "1:a:0",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "168k", "-shortest", "-movflags", "+faststart", str(mp4)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    contact: list = []
    story: list = []
    cursor = 0.0
    fade_frames = round(1.6 * FPS)
    try:
        for k, ((label, duration, frm, to), count) in enumerate(zip(shots, frame_counts)):
            for i in range(count):
                q = i / max(1, count - 1)
                s = q * q * (3 - 2 * q)
                if k == 0:
                    frame = background.copy()
                    frame = signature(frame, i / FPS, ARTIST, COMPOSER)
                elif frm is None:
                    frame = wide.copy()
                else:
                    frame = detail(tuple(frm[j] + (to[j] - frm[j]) * s for j in range(3)))
                # Rampa di continuità all'ingresso della scena (un solo movimento per volta).
                prev = shots[k - 1][3] if k > 0 else None
                ramp = min(count // 3, round(0.70 * FPS))
                if k > 1 and i < ramp and frm is not None and prev is not None:
                    e = i / max(1, ramp - 1)
                    e = e * e * (3 - 2 * e)
                    p = tuple(prev[j] + (frm[j] - prev[j]) * e for j in range(3))
                    frame = detail(p)
                elif k > 0 and i < ramp and frm is None and prev is not None:
                    e = i / max(1, ramp - 1)
                    e = e * e * (3 - 2 * e)
                    frame = cv2.addWeighted(detail(prev), 1 - e, wide, e, 0)
                if k == last and i >= count - fade_frames:
                    f = (count - i) / fade_frames
                    frame = cv2.convertScaleAbs(frame, alpha=max(0.0, f))
                proc.stdin.write(np.ascontiguousarray(frame).tobytes())
                if i == count // 2:
                    contact.append((cursor + i / FPS, cv2.resize(frame, (216, 384))))
            story.append({"scene": k + 1, "subject": label, "start_s": round(cursor, 3),
                          "duration_s": round(count / FPS, 3), "semantic_qa": "PENDING"})
            cursor += count / FPS
        proc.stdin.close()
        err = proc.stderr.read()
        if proc.wait() != 0:
            raise RuntimeError(err.decode(errors="replace")[-1500:])
    except Exception:
        proc.kill()
        raise

    sheet = np.full((4 * 410, 4 * 228, 3), 18, np.uint8)
    for k, (sec, f) in enumerate(contact[:16]):
        x = k % 4 * 228 + 6
        y = k // 4 * 410 + 6
        sheet[y:y + 384, x:x + 216] = f
        cv2.putText(sheet, f"{sec:.1f}s", (x + 8, y + 401), cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                    (220, 215, 198), 1, cv2.LINE_AA)
    cv2.imwrite(str(OUT / "CONTACT_SHEET.jpg"), sheet)

    mobile = OUT / "VIDEO_ANDROID_720_REVIEW.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-i", mp4, "-vf", "scale=720:1280:flags=lanczos",
         "-map", "0:v:0", "-map", "0:a:0", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
         "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", str(mobile)])
    for f in (mp4, mobile):
        run(["ffmpeg", "-v", "error", "-xerror", "-i", f, "-map", "0", "-f", "null", "-"])
    probe = json.loads(run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", mp4]))
    v = [x for x in probe["streams"] if x.get("codec_type") == "video"]
    a = [x for x in probe["streams"] if x.get("codec_type") == "audio"]
    assert len(v) == 1 and v[0]["codec_name"] == "h264" and v[0]["width"] == W and v[0]["height"] == H
    assert len(a) == 1 and a[0]["codec_name"] == "aac"
    (OUT / "FFPROBE.json").write_text(json.dumps(probe, indent=2) + "\n")

    rights = {
        "title": TITLE_EN, "title_it": TITLE_IT, "artist": ARTIST, "year": YEAR,
        "museum": MUSEUM, "inventory": INVENTORY,
        "dimensions_note": "Fonti discordanti: it.wikipedia 146,5x108 cm; en.wikipedia 6'6\"x5'4\" (~198x162,5 cm) e Commons ~199x162,5 cm. Da sciogliere alla fonte museale.",
        "painting_public_domain": True,
        "original_file_page": COMMONS_PAGE, "url_used": art_url,
        "source_sha256": sha256(art_path), "source_bytes": art_path.stat().st_size, "source_pixels": list(ART_PIXELS),
        "commons_license": "Public Domain Mark (riproduzione fedele di opera 2D in pubblico dominio, PD-Art)",
        "license_url": "https://creativecommons.org/publicdomain/mark/1.0/",
        "credit": (f"{ARTIST}, {TITLE_IT} ({YEAR}), {MUSEUM}. Riproduzione PD-Art via Wikimedia Commons / "
                   "Google Art Project. Inquadrature cinematografiche mobili."),
        "music": {
            "title": MUSIC_TITLE, "composer": COMPOSER, "license": MUSIC_LICENSE, "isrc": MUSIC_ISRC,
            "source": MUSIC_SOURCE, "download_url": MUSIC_MP3_URL,
            "recording_sha256": MUSIC_MP3_SHA256, "recording_bytes": MUSIC_MP3_BYTES,
            "license_url": "https://creativecommons.org/licenses/by/4.0/",
            "attribution_required": ('Kevin MacLeod, "Ever Mindful" (incompetech.com), licenza CC BY 4.0: '
                                     "https://creativecommons.org/licenses/by/4.0/"),
            "used_segment_seconds": round(DURATION, 3),
        },
        "human_review": "PENDING", "not_gold": True, "not_published": True, "paid_api_calls": 0,
        "gallery_or_frame": "NESSUNO: solo Cinema Standard, non Museum",
    }
    (OUT / "SOURCES_RIGHTS.json").write_text(json.dumps(rights, indent=2, ensure_ascii=False) + "\n")

    (OUT / "STORYBOARD.json").write_text(json.dumps({
        "duration_s": round(DURATION, 3), "scene_count": len(story), "shots": story,
        "human_artistic_qa": "PENDING", "no_generated_painting_details": True,
    }, indent=2, ensure_ascii=False) + "\n")

    qa = {
        "work_id": "gentileschi_giuditta_uffizi_1567_1620", "variant": "cinema_silent_owner_single",
        "source_sha256": sha256(art_path), "mp4_sha256": sha256(mp4), "mp4_bytes": mp4.stat().st_size,
        "android_mp4_sha256": sha256(mobile), "android_mp4_bytes": mobile.stat().st_size,
        "duration_seconds": round(DURATION, 3), "fps": FPS, "frame_count": N, "resolution": [W, H],
        "scene_count": len(story), "all_streams_ffmpeg_full_decode": "PASS",
        "artistic_qa": "PENDING", "territorial_rights": "PENDING", "gold": False, "published": False,
        "paid_api_calls": 0, "music_recording_sha256": MUSIC_MP3_SHA256,
    }
    (OUT / "QA_TECHNICAL.json").write_text(json.dumps(qa, indent=2) + "\n")

    (OUT / "README_FIRST.md").write_text(
        "UN solo video ArtVision Cinema silenzioso (1080x1920) per Artemisia Gentileschi, "
        "Giuditta che decapita Oloferne (Uffizi, c. 1620). Nessuno slot Museum, nessun Critico, "
        "nessun Gold, nessuna pubblicazione. Fonte autentica verificata per SHA256 prima del render; "
        "musica sotto licenza CC BY 4.0 con attribuzione completa in SOURCES_RIGHTS.json. "
        "Verifica artistica e territoriale a piena velocita' PENDENTE.\n")

    posts = [OUT / f"POST_{k}.txt" for k in ("FACEBOOK", "INSTAGRAM", "TIKTOK", "YOUTUBE")]
    zipf = OUT / "ANDROID_REVIEW_PACKAGE.zip"
    members = [mobile, OUT / "COVER.jpg", OUT / "CONTACT_SHEET.jpg", OUT / "SOURCES_RIGHTS.json",
               OUT / "STORYBOARD.json", OUT / "QA_TECHNICAL.json", OUT / "README_FIRST.md"] + \
              [p for p in posts if p.exists()]
    with zipfile.ZipFile(zipf, "w", zipfile.ZIP_DEFLATED, compresslevel=2) as z:
        for f in members:
            z.write(f, f.name)
    with zipfile.ZipFile(zipf) as z:
        assert z.testzip() is None
        assert hashlib.sha256(z.read(mobile.name)).hexdigest() == qa["android_mp4_sha256"]

    print("NEW_GENTILESCHI_PRIVATE_CINEMA", json.dumps({
        "mp4_sha256": qa["mp4_sha256"], "android_sha256": qa["android_mp4_sha256"],
        "zip_sha256": sha256(zipf), "duration_s": qa["duration_seconds"], "frame_count": N,
        "full_decode": "PASS", "crc": "PASS", "gold": False, "published": False, "paid_calls": 0,
    }, indent=2), flush=True)


if __name__ == "__main__":
    main()
