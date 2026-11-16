#!/usr/bin/env python3
"""Sandro Botticelli, La nascita di Venere (Uffizi, c. 1485)
ArtVision Cinema (silenzioso) — UN video, revisione privata dell'owner.
Regia "più tesa e ritmata" scelta dall'utente il 2026-11-16.

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

PROJECT = ROOT / "output" / "artvision_botticelli_venere"
PROJECT.mkdir(parents=True, exist_ok=True)
OUT = PROJECT

ARTIST = "Sandro Botticelli"
COMPOSER = "Kevin MacLeod"
TITLE_EN = "The Birth of Venus"
TITLE_IT = "La nascita di Venere"
YEAR = "c. 1485"
MUSEUM = "Galleria degli Uffizi, Firenze"
INVENTORY = "inv. 1890 n. 878"
COMMONS_PAGE = ("https://commons.wikimedia.org/wiki/File:"
                "Sandro_Botticelli_-_La_nascita_di_Venere_-_Google_Art_ProjectFXD.jpg")
COMMONS_KEY = "Sandro Botticelli - La nascita di Venere - Google Art ProjectFXD.jpg"

# --- Fonte autentica: SHA256 verificato in locale (Google Art Project, PD) ---
ART_SHA256 = "a0f521d7fd623dbab97a2fb16cfc22655d86953c7291a6197e167ae45105040c"
ART_PIXELS = (6000, 3768)

# --- Musica: registrazione reale sotto licenza, verificata con ffprobe in locale ---
MUSIC_TITLE = "Ancient Rite"
MUSIC_LICENSE = "CC BY 4.0"
MUSIC_SOURCE = "https://commons.wikimedia.org/wiki/File:Ancient_Rite_by_Kevin_MacLeod.ogg"
MUSIC_URL = "https://upload.wikimedia.org/wikipedia/commons/b/b7/Ancient_Rite_by_Kevin_MacLeod.ogg"
MUSIC_SHA256 = "f7766ca703fbcb62533e42fa4d85cadaa8d7a00dc1697bf030ff16d60a22c600"
MUSIC_BYTES = 2386208
MUSIC_DURATION_S = 113.214694
MUSIC_OFFSET_S = 8.0

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
    auth = lock.get("authorized_botticelli_venere_cinema_20261116", {})
    if not (auth.get("enabled") is True
            and auth.get("allowed_title") == TITLE_EN
            and auth.get("allowed_artist") == ARTIST
            and auth.get("no_paid_video_ai") is True
            and auth.get("no_social_auto_publish") is True
            and auth.get("museum_slots_authorized") is False):
        raise RuntimeError("PILOT LOCK: Botticelli Cinema non autorizzato o scope incompatibile")
    return auth


def fetch(url: str, dest: Path, ua: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    with urllib.request.urlopen(req, timeout=110) as f:
        data = f.read()
    dest.write_bytes(data)
    return data


def resolve_artwork() -> tuple[Path, str]:
    """Usa l'asset locale se l'hash combacia; altrimenti scarica l'originale esatto da Commons."""
    local = PROJECT / "assets" / "venere_botticelli_full.jpg"
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
    env = os.environ.get("ARTVISION_MUSIC_OGG")
    if env:
        candidates.append(Path(env))
    candidates.append(PROJECT / "assets" / "music_ancient_rite.ogg")
    for c in candidates:
        if Path(c).exists() and sha256(c) == MUSIC_SHA256:
            print("LOCAL_EXACT_MUSIC_VERIFIED", MUSIC_SHA256, flush=True)
            return Path(c)
    dest = OUT / "ORIGINAL_MUSIC.ogg"
    fetch(MUSIC_URL, dest, "ArtVisionOwnerPrivateReview/1.0")
    got = sha256(dest)
    if got != MUSIC_SHA256:
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
    wide1 = background.copy()
    full_w = min(W - 42, int((H - 300) * aw / ah))
    full_h = round(full_w * ah / aw)
    fx0 = (W - full_w) // 2
    fy0 = (H - full_h) // 2
    wide1[fy0:fy0 + full_h, fx0:fx0 + full_w] = cv2.resize(src, (full_w, full_h), interpolation=cv2.INTER_AREA)

    def wide(s: float) -> np.ndarray:
        """Opera intera incorniciata; s>1 = vista ravvicinata (per rivelazioni/allontanamenti fluidi)."""
        s = max(1.0, float(s))
        sw = max(2, round(W / s))
        sh = max(2, round(H / s))
        x = (W - sw) // 2
        y = (H - sh) // 2
        return cv2.resize(wide1[y:y + sh, x:x + sw], (W, H), interpolation=cv2.INTER_AREA)

    def detail(p) -> np.ndarray:
        cx, cy, hfrac = p
        hh = min(ah, max(180, round(ah * hfrac)))
        ww = min(aw, max(100, round(hh * W / H)))
        x = max(0, min(aw - ww, round(cx * aw - ww / 2)))
        y = max(0, min(ah - hh, round(cy * ah - hh / 2)))
        return cv2.resize(src[y:y + hh, x:x + ww], (W, H), interpolation=cv2.INTER_AREA)

    # 16 inquadrature, ritmo teso: una sola intenzione di regia per inquadratura, sempre nello stesso verso.
    #   kind "wide" -> opera intera incorniciata, rivelazione (s0 -> s1) con un solo movimento lento.
    #   kind "move" -> carrello lento e continuo su un dettaglio (from -> to).
    #   kind "card" -> opera intera tenuta, con la firma V6 in dissolvenza (chiusura).
    # xf = dissolvenza in apertura di scena (frame); 0 = stacco netto, usato come accento ritmico.
    shots: list = [
        {"label": "RIVELAZIONE: VENERE EMERGE DAL BUIO", "dur": 4.5,
         "kind": "wide", "s0": 1.14, "s1": 1.00, "xf": 0},
        {"label": "LE DUE ALI DEL VENTO: ZEFIRO E AURA", "dur": 3.5,
         "kind": "move", "from": (0.12, 0.42, 0.62), "to": (0.12, 0.42, 0.48), "xf": 8},
        {"label": "IL SOFFIO: VOLTO DI ZEFIRO (AVVICINAMENTO)", "dur": 3.0,
         "kind": "move", "from": (0.08, 0.40, 0.40), "to": (0.08, 0.40, 0.30), "xf": 6},
        {"label": "AURA ABBRACCIATA (AVVICINAMENTO)", "dur": 3.0,
         "kind": "move", "from": (0.17, 0.42, 0.38), "to": (0.17, 0.42, 0.30), "xf": 6},
        {"label": "LE ROSE CHE CADONO (STACCO NETTO)", "dur": 2.8,
         "kind": "move", "from": (0.33, 0.17, 0.34), "to": (0.33, 0.17, 0.26), "xf": 0},
        {"label": "VOLTO DI VENERE: LA MUSA DEL MARE", "dur": 3.2,
         "kind": "move", "from": (0.50, 0.18, 0.30), "to": (0.50, 0.18, 0.22), "xf": 8},
        {"label": "I CAPELLI AL VENTO (CARRELLO)", "dur": 3.0,
         "kind": "move", "from": (0.47, 0.30, 0.34), "to": (0.58, 0.34, 0.30), "xf": 6},
        {"label": "IL CORPO E IL GESTO DI PUDORE", "dur": 3.2,
         "kind": "move", "from": (0.53, 0.40, 0.34), "to": (0.53, 0.42, 0.26), "xf": 6},
        {"label": "LA CONCHIGLIA E L'ONDA (CULMINE, STACCO NETTO)", "dur": 3.0,
         "kind": "move", "from": (0.50, 0.82, 0.40), "to": (0.50, 0.84, 0.30), "xf": 0},
        {"label": "L'ORA CHE TENDE IL MANTELLO", "dur": 3.0,
         "kind": "move", "from": (0.86, 0.55, 0.42), "to": (0.86, 0.58, 0.32), "xf": 6},
        {"label": "IL VOLTO DELL'ORA (AVVICINAMENTO)", "dur": 3.0,
         "kind": "move", "from": (0.86, 0.34, 0.30), "to": (0.86, 0.34, 0.22), "xf": 6},
        {"label": "IL FIORE NEL MANTELLO (STACCO NETTO)", "dur": 2.8,
         "kind": "move", "from": (0.80, 0.47, 0.26), "to": (0.80, 0.47, 0.18), "xf": 0},
        {"label": "VENERE INTERA (ALLONTANAMENTO)", "dur": 4.0,
         "kind": "move", "from": (0.50, 0.45, 0.55), "to": (0.50, 0.45, 0.78), "xf": 8},
        {"label": "IL MARE E LA RIVA (AVVICINAMENTO)", "dur": 3.0,
         "kind": "move", "from": (0.82, 0.90, 0.30), "to": (0.82, 0.92, 0.22), "xf": 6},
        {"label": "RITORNO ALL'OPERA: IL RESPIRO", "dur": 4.5,
         "kind": "wide", "s0": 1.12, "s1": 1.00, "xf": 14},
        {"label": "TENUTA FINALE: FIRMA DELLA SERIE, DISSOLVENZA IN NERO", "dur": 5.0,
         "kind": "card", "s0": 1.00, "s1": 1.00, "xf": 14},
    ]
    assert len(shots) == 16, len(shots)
    frame_counts = [round(s["dur"] * FPS) for s in shots]
    N = sum(frame_counts)
    DURATION = N / FPS
    assert 50.0 < DURATION < 60.0, DURATION
    last = len(shots) - 1

    def ease(u: float) -> float:
        u = max(0.0, min(1.0, u))
        return u * u * (3 - 2 * u)

    def shot_frame(k: int, u: float) -> np.ndarray:
        s = shots[k]
        e = ease(u)
        if s["kind"] == "move":
            a, b = s["from"], s["to"]
            return detail(tuple(a[j] + (b[j] - a[j]) * e for j in range(3)))
        return wide(s["s0"] + (s["s1"] - s["s0"]) * e)

    # Copertina = volto di Venere in luce, con la stessa identità V6 della serie.
    cover_frame = cover(detail((0.50, 0.18, 0.30)), ARTIST, COMPOSER)
    cv2.imwrite(str(OUT / "COVER.jpg"), cover_frame, [cv2.IMWRITE_JPEG_QUALITY, 92])

    # Segmento musicale con licenza: taglio + dissolvenze, salvato per provenienza.
    segment = OUT / "LICENSED_MUSIC_SEGMENT.m4a"
    run(["ffmpeg", "-y", "-v", "error", "-ss", f"{MUSIC_OFFSET_S}",
         "-t", f"{DURATION + 0.6:.3f}", "-i", music_src,
         "-af", f"afade=t=in:st=0:d=1.5,afade=t=out:st={DURATION - 2.5:.3f}:d=2.5",
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
    fade_in_frames = round(0.8 * FPS)
    fade_out_frames = round(1.5 * FPS)
    try:
        prev_last: np.ndarray | None = None
        for k, s in enumerate(shots):
            count = frame_counts[k]
            xf = s["xf"] if prev_last is not None else 0
            for i in range(count):
                u = i / max(1, count - 1)
                frame = shot_frame(k, u)
                if k == 0:  # Venere emerge dal nero
                    frame = cv2.convertScaleAbs(frame, alpha=min(1.0, (i + 1) / fade_in_frames))
                if k == last:  # la firma V6 entra in dissolvenza, poi si spegne nel nero
                    a = min(1.0, (i + 1) / (1.0 * FPS))
                    sig = signature(frame, 0.0, ARTIST, COMPOSER, force_visible=True)
                    frame = cv2.addWeighted(frame, 1 - a, sig, a, 0)
                    if i >= count - fade_out_frames:
                        frame = cv2.convertScaleAbs(
                            frame, alpha=max(0.0, (count - i) / fade_out_frames))
                if xf > 0 and i < xf:  # dissolvenza in apertura di scena
                    e = ease((i + 1) / (xf + 1))
                    frame = cv2.addWeighted(prev_last, 1 - e, frame, e, 0)
                proc.stdin.write(np.ascontiguousarray(frame).tobytes())
                if i == count // 2:
                    contact.append((cursor + i / FPS, cv2.resize(frame, (216, 384))))
            prev_last = shot_frame(k, 1.0)
            story.append({"scene": k + 1, "subject": s["label"], "kind": s["kind"],
                          "start_s": round(cursor, 3), "duration_s": round(count / FPS, 3),
                          "opens_with": ("fade_from_black" if k == 0 else
                                         ("hard_cut" if xf == 0 else f"dissolve_{xf}f")),
                          "semantic_qa": "PENDING"})
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
        "dimensions_note": "Olio su tela, cm 172,5 x 278,9 (Galleria degli Uffizi, inv. 1890 n. 878).",
        "painting_public_domain": True,
        "original_file_page": COMMONS_PAGE, "url_used": art_url,
        "source_sha256": sha256(art_path), "source_bytes": art_path.stat().st_size, "source_pixels": list(ART_PIXELS),
        "commons_license": "Public domain (riproduzione fedele di opera 2D in pubblico dominio, PD-Art)",
        "credit": (f"{ARTIST}, {TITLE_IT} ({YEAR}), {MUSEUM}. Riproduzione PD via Wikimedia Commons / "
                   "Google Art Project. Inquadrature cinematografiche mobili."),
        "music": {
            "title": MUSIC_TITLE, "composer": COMPOSER, "license": MUSIC_LICENSE,
            "source": MUSIC_SOURCE, "download_url": MUSIC_URL,
            "recording_sha256": MUSIC_SHA256, "recording_bytes": MUSIC_BYTES,
            "recording_duration_seconds": MUSIC_DURATION_S,
            "license_url": "https://creativecommons.org/licenses/by/4.0/",
            "attribution_required": ('Kevin MacLeod, "Ancient Rite" (incompetech.com), licenza CC BY 4.0: '
                                     "https://creativecommons.org/licenses/by/4.0/"),
            "used_segment_seconds": round(DURATION, 3),
        },
        "human_review": "PENDING", "not_gold": True, "not_published": True, "paid_api_calls": 0,
        "gallery_or_frame": "NESSUNO: solo Cinema Standard, non Museum",
    }
    (OUT / "SOURCES_RIGHTS.json").write_text(json.dumps(rights, indent=2, ensure_ascii=False) + "\n")

    (OUT / "STORYBOARD.json").write_text(json.dumps({
        "duration_s": round(DURATION, 3), "scene_count": len(story), "direction": "piu_tesa_e_ritmata",
        "shots": story, "human_artistic_qa": "PENDING", "no_generated_painting_details": True,
    }, indent=2, ensure_ascii=False) + "\n")

    qa = {
        "work_id": "botticelli_birth_of_venus_uffizi_1890_878", "variant": "cinema_silent_owner_single",
        "source_sha256": sha256(art_path), "mp4_sha256": sha256(mp4), "mp4_bytes": mp4.stat().st_size,
        "android_mp4_sha256": sha256(mobile), "android_mp4_bytes": mobile.stat().st_size,
        "duration_seconds": round(DURATION, 3), "fps": FPS, "frame_count": N, "resolution": [W, H],
        "scene_count": len(story), "all_streams_ffmpeg_full_decode": "PASS",
        "artistic_qa": "PENDING", "territorial_rights": "PENDING", "gold": False, "published": False,
        "paid_api_calls": 0, "music_recording_sha256": MUSIC_SHA256,
    }
    (OUT / "QA_TECHNICAL.json").write_text(json.dumps(qa, indent=2) + "\n")

    (OUT / "README_FIRST.md").write_text(
        "UN solo video ArtVision Cinema silenzioso (1080x1920) per Sandro Botticelli, "
        "La nascita di Venere (Uffizi, c. 1485). Regia piu' tesa e ritmata. Nessuno slot Museum, "
        "nessun Critico, nessun Gold, nessuna pubblicazione. Fonte autentica verificata per SHA256 "
        "prima del render; musica sotto licenza CC BY 4.0 con attribuzione completa in SOURCES_RIGHTS.json. "
        "Verifica artistica e territoriale PENDENTE.\n")

    zipf = OUT / "ANDROID_REVIEW_PACKAGE.zip"
    members = [mobile, OUT / "COVER.jpg", OUT / "CONTACT_SHEET.jpg", OUT / "SOURCES_RIGHTS.json",
               OUT / "STORYBOARD.json", OUT / "QA_TECHNICAL.json", OUT / "README_FIRST.md"]
    with zipfile.ZipFile(zipf, "w", zipfile.ZIP_DEFLATED, compresslevel=2) as z:
        for f in members:
            z.write(f, f.name)
    with zipfile.ZipFile(zipf) as z:
        assert z.testzip() is None
        assert hashlib.sha256(z.read(mobile.name)).hexdigest() == qa["android_mp4_sha256"]

    print("NEW_BOTTICELLI_PRIVATE_CINEMA", json.dumps({
        "mp4_sha256": qa["mp4_sha256"], "android_sha256": qa["android_mp4_sha256"],
        "zip_sha256": sha256(zipf), "duration_s": qa["duration_seconds"], "frame_count": N,
        "full_decode": "PASS", "crc": "PASS", "gold": False, "published": False, "paid_calls": 0,
    }, indent=2), flush=True)


if __name__ == "__main__":
    main()
