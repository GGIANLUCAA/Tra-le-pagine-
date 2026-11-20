#!/usr/bin/env python3
"""ARTVISION — Nuova selezione 30, opera #2 Medea, versione SOCIAL finale.

Video verticale 1080x1920, testo a schermo (hook-first) + musica originale sintetizzata
localmente. Nessuna voce (Gacrux non disponibile in questo ambiente). Nessun asset di
terzi: dipinto di pubblico dominio (Sandys) + colonna sonora generata qui.
"""
import hashlib
import json
import subprocess
import wave
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SRC = Path("deliverables/cinema-nuova-selezione-30-20261119/owner-medea-sandys-cinema-v1")
OUT = Path("deliverables/social-publish-ready-20261120/medea-sandys-social-v1")
OUT.mkdir(parents=True, exist_ok=True)

source = OUT / "ORIGINAL_ARTWORK.jpg"
source.write_bytes((SRC / "ORIGINAL_ARTWORK.jpg").read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
print("SOURCE", source.stat().st_size, sha(source), flush=True)

def pick(*paths):
    for p in paths:
        if Path(p).exists():
            return p
    raise FileNotFoundError(paths)

SERIF_B = pick("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf")
SERIF = pick("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf")
SANS_B = pick("/usr/share/fonts/truetype/lato/Lato-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
SANS = pick("/usr/share/fonts/truetype/lato/Lato-Medium.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")

SHOTS = [
    ("APERTURA",        4.0, None,                None,                "Sta lanciando un incantesimo mortale contro la sua rivale."),
    ("MANI",            4.2, (.45, .65, .30),     (.43, .65, .27),     "Guarda le sue mani e gli ingredienti magici sul tavolo."),
    ("VOLTO",           4.4, (.50, .30, .35),     (.52, .32, .32),     "È Medea, maga e principessa tradita da Giasone."),
    ("COLLANA",         4.6, (.45, .45, .25),     (.47, .47, .22),     "Mentre l'odio vince, si strappa dal collo la collana di corallo..."),
    ("BARCA",           4.2, (.80, .15, .20),     (.78, .15, .17),     "...mentre sullo sfondo la barca del marito si allontana."),
    ("ROSPI",           4.0, (.20, .90, .25),     (.22, .90, .22),     "In basso, due rospi alludono all'infedeltà coniugale."),
    ("SFONDO_ORO",      4.4, (.80, .40, .30),     (.78, .42, .27),     "Il fondo d'oro non è un cielo, ma un intricato schermo..."),
    ("DRAGO",           4.0, (.80, .50, .25),     (.82, .48, .22),     "...che fonde motivi greci, cinesi ed egiziani."),
    ("INTERO",          4.0, None,                None,                "Rifiutato dalla Royal Academy, oggi è un capolavoro a Birmingham."),
    ("REVEAL",          5.6, None,                None,                "@REVEAL"),
]
W, H, FPS = 1080, 1920, 30
duration = sum(s[1] for s in SHOTS)

CREAM = (243, 235, 221)

sr = 22050
n = int((duration + .2) * sr)
t = np.arange(n) / sr
audio = np.zeros(n, dtype=np.float64)
# Tensione magica (Medea): minor chords
chords = [(58.27, 69.30, 87.31), (65.41, 77.78, 98.00), (55.00, 65.41, 82.41), (61.74, 73.42, 92.50)]
for idx, start in enumerate(np.arange(0, duration, 7.5)):
    end = min(duration + .15, start + 8.9)
    a, b = int(start * sr), min(n, int(end * sr))
    u = t[a:b] - start
    env = np.minimum(1, u / 1.35) * np.maximum(0, np.minimum(1, (end - start - u) / 1.45))
    for j, freq in enumerate(chords[idx % 4]):
        audio[a:b] += .035 / (1 + j * .32) * env * (np.sin(2 * np.pi * freq * u) + .2 * np.sin(4 * np.pi * freq * u))
    for off in (0, 3.75):
        pos = int((start + off) * sr)
        if pos >= n: continue
        length = min(n - pos, int(.75 * sr))
        z = np.arange(length) / sr
        audio[pos:pos + length] += .065 * np.exp(-5 * z) * np.sin(2 * np.pi * (52 - 16 * z) * z)
audio += .013 * np.sin(2 * np.pi * 49 * t)
audio *= np.minimum(1, t / 1.6) * np.clip((duration - t) / 2.6, 0, 1)
with wave.open(str(OUT / "SCORE_ORIGINALE.wav"), "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes((np.tanh(audio * 1.5) * 32767).astype("<i2").tobytes())

img = cv2.imread(str(source), cv2.IMREAD_COLOR)
assert img is not None
oh0, ow0 = img.shape[:2]
TARGET_W = min(2160, ow0)
img = cv2.resize(img, (TARGET_W, round(oh0 * TARGET_W / ow0)), interpolation=cv2.INTER_AREA)
oh, ow = img.shape[:2]
blur = cv2.GaussianBlur(cv2.resize(img, (W, H)), (0, 0), 46)
whole = cv2.convertScaleAbs(blur, alpha=.38, beta=0)
hh = round(W * oh / ow)
if hh <= H:
    yy = (H - hh) // 2
    whole[yy:yy + hh] = cv2.resize(img, (W, hh), interpolation=cv2.INTER_AREA)
else:
    ww = round(H * ow / oh)
    xx = (W - ww) // 2
    whole[:, xx:xx + ww] = cv2.resize(img, (ww, H), interpolation=cv2.INTER_AREA)

def layer(): return Image.new("RGBA", (W, H), (0, 0, 0, 0))
def wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        tst = (cur + " " + wd).strip()
        if draw.textlength(tst, font=font) <= max_w or not cur: cur = tst
        else: lines.append(cur); cur = wd
    if cur: lines.append(cur)
    return lines
def block(draw, lines, font, cx, top, lh, fill=CREAM):
    for i, ln in enumerate(lines):
        draw.text((cx, top + i * lh), ln, font=font, anchor="ma", fill=fill)
def to_arrays(lp):
    a = np.array(lp)
    return a[..., :3].astype(np.float32), a[..., 3].astype(np.float32) / 255.0

brand = layer(); bd = ImageDraw.Draw(brand)
bd.text((W // 2, 92), "A R T V I S I O N", font=ImageFont.truetype(SANS_B, 36), anchor="mm", fill=(238, 230, 214, 235))
bd.line([(W // 2 - 96, 128), (W // 2 + 96, 128)], fill=(238, 230, 214, 120), width=2)

hook = layer(); hd = ImageDraw.Draw(hook)
hfont = ImageFont.truetype(SERIF_B, 68)
hl = wrap(hd, "Sta lanciando un incantesimo mortale contro la sua rivale.", hfont, 880)
bh = 96 + len(hl) * 92
hd.rectangle([0, 250, W, 250 + bh], fill=(10, 9, 8, 205))
block(hd, hl, hfont, W // 2, 300, 92, fill=(247, 240, 226))
hd.text((W // 2, 250 + bh + 54), "05 / 2026", font=ImageFont.truetype(SANS, 34), anchor="mm", fill=(226, 217, 200, 220))

reveal = layer(); rd = ImageDraw.Draw(reveal)
rd.rectangle([0, 0, W, H], fill=(8, 8, 10, 232))
rt = ImageFont.truetype(SERIF_B, 66); rs = ImageFont.truetype(SANS, 40)
rlines = wrap(rd, "Medea", rt, 900)
top = 700
block(rd, rlines, rt, W // 2, top, 84, fill=(247, 240, 226))
rd.line([(W // 2 - 120, top + len(rlines) * 84 + 34), (W // 2 + 120, top + len(rlines) * 84 + 34)], fill=(238, 230, 214, 150), width=2)
block(rd, ["Frederick Sandys", "1866-1868"], rs, W // 2, top + len(rlines) * 84 + 96, 56, fill=(234, 226, 210))
rd.text((W // 2, top + len(rlines) * 84 + 240), "Birmingham Museum and Art Gallery", font=ImageFont.truetype(SANS, 34), anchor="mm", fill=(206, 198, 182))
rd.text((W // 2, top + len(rlines) * 84 + 322), "Fonte: Birmingham Museums Trust", font=ImageFont.truetype(SANS, 30), anchor="mm", fill=(176, 169, 156))
rd.text((W // 2, 1560), "Conoscevi questo mito?", font=ImageFont.truetype(SANS_B, 46), anchor="mm", fill=(243, 235, 221))

caps = []; cfont = ImageFont.truetype(SANS, 52)
for _, _, _, _, cap in SHOTS:
    lp = layer(); cd = ImageDraw.Draw(lp)
    if cap and cap != "@REVEAL":
        lines = wrap(cd, cap, cfont, 900)
        bh = 46 + len(lines) * 68; y0 = 1430 - bh
        cd.rounded_rectangle([70, y0, W - 70, y0 + bh], radius=26, fill=(10, 9, 8, 176))
        for i, ln in enumerate(lines): cd.text((W // 2, y0 + 30 + i * 68), ln, font=cfont, anchor="ma", fill=(247, 240, 226))
    caps.append(to_arrays(lp))

brand_rgb, brand_a = to_arrays(brand)
hook_rgb, hook_a = to_arrays(hook)
reveal_rgb, reveal_a = to_arrays(reveal)

out_mp4 = OUT / "FINAL_1080x1920.mp4"
cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "rawvideo",
       "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "pipe:0",
       "-i", str(OUT / "SCORE_ORIGINALE.wav"), "-c:v", "libx264", "-preset", "medium",
       "-crf", "20", "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.1",
       "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-shortest", "-movflags", "+faststart", str(out_mp4)]
proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
contact, timeline = [], []
def blend(buf, rgb, alpha, fade):
    a = (alpha * fade)[..., None]
    return buf * (1.0 - a) + rgb * a

for idx, (name, seconds, a, b, cap) in enumerate(SHOTS):
    count = round(seconds * FPS)
    cap_rgb, cap_a = caps[idx]
    for k in range(count):
        z = k / max(1, count - 1); e = z * z * (3 - 2 * z)
        if a is None:
            frame = whole.copy()
        else:
            cx, cy, height = [a[v] * (1 - e) + b[v] * e for v in range(3)]
            ch = min(oh, max(80, round(oh * height)))
            cw = min(ow, max(80, round(ch * W / H)))
            x = max(0, min(ow - cw, round(cx * ow - cw / 2)))
            y = max(0, min(oh - ch, round(cy * oh - ch / 2)))
            frame = cv2.resize(img[y:y + ch, x:x + cw], (W, H), interpolation=cv2.INTER_AREA)
        buf = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).astype(np.float32)
        ff = min(1.0, k / (FPS * .4)) * min(1.0, (count - 1 - k) / (FPS * .4))
        buf = blend(buf, cap_rgb, cap_a, ff)
        buf = blend(buf, brand_rgb, brand_a, min(1.0, k / (FPS * .6)))
        if idx == 0:
            fh = min(1.0, k / (FPS * .5))
            buf = blend(buf, hook_rgb, hook_a, fh)
        if cap == "@REVEAL":
            fr = min(1.0, k / (FPS * .6))
            buf = blend(buf, reveal_rgb, reveal_a, fr)
        proc.stdin.write(np.clip(buf, 0, 255).astype(np.uint8).tobytes())
        if k == count // 2:
            contact.append(cv2.resize(cv2.cvtColor(np.clip(buf, 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR), (216, 384), interpolation=cv2.INTER_AREA))
    timeline.append({"subject_for_human_review": name, "seconds": seconds, "camera_from": a, "camera_to": b, "caption": cap})
proc.stdin.close()
if proc.wait() != 0: raise RuntimeError("FFmpeg rendering failed")
print("MP4_RENDERED", out_mp4.stat().st_size, sha(out_mp4), flush=True)

rows = (len(contact) + 3) // 4
sheet = np.full((rows * 384, 4 * 216, 3), 19, dtype=np.uint8)
for i, fr in enumerate(contact):
    r, c = divmod(i, 4)
    sheet[r * 384:(r + 1) * 384, c * 216:(c + 1) * 216] = fr
cv2.imwrite(str(OUT / "CONTATTO_REGIA.jpg"), sheet)

art = Image.open(source).convert("RGB")
cw, ch = art.size
tw = min(cw, int(ch * 1080 / 1920))
left = max(0, (cw - tw) // 2)
cover = art.crop((left, 0, left + tw, ch)).resize((1080, 1920), Image.LANCZOS)
ov = layer(); cd = ImageDraw.Draw(ov)
cd.rectangle([0, 0, 1080, 470], fill=(10, 9, 8, 210))
cd.rectangle([0, 1620, 1080, 1920], fill=(10, 9, 8, 210))
cd.text((540, 120), "STA LANCIANDO UN", font=ImageFont.truetype(SANS_B, 50), anchor="ma", fill=(240, 232, 216))
cd.text((540, 210), "INCANTESIMO", font=ImageFont.truetype(SERIF_B, 120), anchor="ma", fill=(247, 240, 226))
cd.text((540, 372), "CONTRO LA RIVALE", font=ImageFont.truetype(SANS_B, 54), anchor="ma", fill=(240, 232, 216))
cd.text((540, 1720), "ARTVISION · STORIE NELL'ARTE", font=ImageFont.truetype(SANS, 38), anchor="mm", fill=(236, 228, 212))
cd.text((540, 1790), "F. Sandys · 1866 · Birmingham Museum", font=ImageFont.truetype(SANS, 30), anchor="mm", fill=(206, 198, 182))
cover = Image.alpha_composite(cover.convert("RGBA"), ov).convert("RGB")
cover.save(OUT / "COPERTINA_SOCIAL.jpg", quality=92)

(OUT / "FONTI_E_DIRITTI.json").write_text(json.dumps({
    "work": "Medea", "artist": "Frederick Sandys",
    "year": "1866-1868", "collection": "Birmingham Museum and Art Gallery",
    "artwork_copyright": "Pubblico dominio; riproduzione fedele PD-Art",
    "audio_copyright": "Colonna sonora originale", "third_party_assets": "none",
    "voice": "none (versione senza voce narrante)", "publication_allowed": True,
    "environment_note": "Prodotto in ambiente senza GEMINI_API_KEY: versione senza voce."
}, ensure_ascii=False, indent=2), encoding="utf8")

(OUT / "SOCIAL_POSTS.json").write_text(json.dumps({
    "facebook": "Sta lanciando un incantesimo mortale contro la sua rivale. Medea, maga e principessa tradita, si strappa la collana di corallo mentre la barca di Giasone si allontana.\n\nFrederick Sandys, Medea, 1866-1868. Birmingham Museum and Art Gallery.",
    "instagram": "Sta lanciando un incantesimo mortale. Guarda le mani e gli ingredienti sul tavolo. Medea è la principessa tradita da Giasone, pronta alla vendetta.\n\nFrederick Sandys, Medea. Birmingham Museum and Art Gallery. #ArtHistory #Medea",
    "tiktok": "Un incantesimo mortale dipinto nel dettaglio. Cosa noti nel fondo dorato? Sandys, Medea. #Arte #Mito",
    "youtube_shorts": "Medea lancia un incantesimo contro la nuova sposa di Giasone. Un'opera carica di dettagli simbolici. Frederick Sandys, Medea (1866-1868). #ArtHistory",
}, ensure_ascii=False, indent=2), encoding="utf8")

(OUT / "STORYBOARD.json").write_text(json.dumps({"variant": "social_final_vertical_no_voice", "fps": FPS, "resolution": [W, H], "total_s": duration, "shots": timeline, "uses_actual_painting": True}, ensure_ascii=False, indent=2), encoding="utf8")

(OUT / "LEGGIMI.md").write_text("# Medea — versione social finale\nVideo verticale 1080x1920, 30 fps, testo a schermo. Nessuna voce narrante (GEMINI_API_KEY mancante).\n", encoding="utf8")
print("DONE", OUT, flush=True)
