#!/usr/bin/env python3
"""ARTVISION — Nuova selezione 30, opera #1 Paton, versione SOCIAL finale.

Video verticale 1080x1920, testo a schermo (hook-first) + musica originale sintetizzata
localmente. Nessuna voce (Gacrux non disponibile in questo ambiente). Nessun asset di
terzi: dipinto di pubblico dominio (Paton, 1901) + colonna sonora generata qui.
Destinazione: revisione privata pronta alla pubblicazione, nessun upload automatico.
"""
import hashlib
import json
import subprocess
import wave
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SRC = Path("deliverables/cinema-nuova-selezione-30-20261119/owner-paton-quarrel-cinema-v1")
OUT = Path("deliverables/social-publish-ready-20261120/paton-quarrel-social-v1")
OUT.mkdir(parents=True, exist_ok=True)

source = OUT / "ORIGINAL_ARTWORK.jpg"
source.write_bytes((SRC / "ORIGINAL_ARTWORK.jpg").read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
print("SOURCE", source.stat().st_size, sha(source), flush=True)

# --- Fonts -------------------------------------------------------------------
def pick(*paths):
    for p in paths:
        if Path(p).exists():
            return p
    raise FileNotFoundError(paths)

SERIF_B = pick("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
               "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf")
SERIF = pick("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf")
SANS_B = pick("/usr/share/fonts/truetype/lato/Lato-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
SANS = pick("/usr/share/fonts/truetype/lato/Lato-Medium.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")

# --- Inquadrature (dal dipinto autentico) + didascalie verificate -------------
# camera = (cx, cy, altezza_frac);  None = tela intera
SHOTS = [
    ("APERTURA",        4.6, None,                None,                "Lewis Carroll contò 165 fate in questo quadro."),
    ("CORTE",           4.2, (.42, .46, .52),     (.40, .45, .46),     "Al centro, Oberon e Titania: re e regina delle fate."),
    ("OBERON",          4.4, (.33, .40, .40),     (.36, .41, .35),     "Si contendono un bambino umano: il changeling."),
    ("TITANIA",         4.4, (.55, .42, .40),     (.52, .42, .34),     "La scena nasce dal «Sogno di una notte di mezza estate»."),
    ("SCONTRO",         4.6, (.44, .44, .34),     (.46, .44, .30),     "Tutt'intorno, Paton popola la tela di creature minuscole."),
    ("FOLLA_SINISTRA",  4.2, (.16, .62, .52),     (.20, .60, .46),     "Alcune bellissime, altre grottesche."),
    ("FOLLA_DESTRA",    4.2, (.82, .58, .52),     (.78, .57, .46),     "Il museo le descrive come un mondo soprannaturale."),
    ("DANZATRICI",      4.4, (.63, .68, .40),     (.60, .67, .35),     "Danzatrici, musici, folletti: ogni angolo ha una figura."),
    ("CREATURE",        4.0, (.24, .74, .40),     (.27, .73, .35),     ""),
    ("FLORA",           4.0, (.50, .84, .36),     (.48, .83, .31),     ""),
    ("MUSICI",          4.2, (.72, .72, .34),     (.70, .71, .30),     "Nel 1850, a Edimburgo, fu «picture of the season»."),
    ("ONDA",            4.2, (.90, .50, .42),     (.88, .50, .37),     ""),
    ("CENTRO",          4.6, (.40, .52, .46),     (.42, .52, .40),     "Il conteggio di Carroll: 165 fate in un solo dipinto."),
    ("VOLTI",           4.0, (.47, .38, .30),     (.45, .38, .27),     ""),
    ("REGINA",          4.6, (.56, .46, .30),     (.54, .46, .27),     "Prova tu: quante riesci a vederne?"),
    ("INTERO",          5.6, None,                None,                "@REVEAL"),
]
W, H, FPS = 1080, 1920, 30
duration = sum(s[1] for s in SHOTS)

CREAM = (243, 235, 221)
BAND = (10, 9, 8)

# --- Colonna sonora originale (nessuna registrazione di terzi) ----------------
sr = 22050
n = int((duration + .2) * sr)
t = np.arange(n) / sr
audio = np.zeros(n, dtype=np.float64)
chords = [(65.41, 98.00, 130.81), (73.42, 110.00, 146.83),
          (55.00, 82.41, 110.00), (61.74, 92.50, 123.47)]
for idx, start in enumerate(np.arange(0, duration, 7.5)):
    end = min(duration + .15, start + 8.9)
    a, b = int(start * sr), min(n, int(end * sr))
    u = t[a:b] - start
    env = np.minimum(1, u / 1.35) * np.maximum(0, np.minimum(1, (end - start - u) / 1.45))
    for j, freq in enumerate(chords[idx % 4]):
        audio[a:b] += .035 / (1 + j * .32) * env * (
            np.sin(2 * np.pi * freq * u) + .2 * np.sin(4 * np.pi * freq * u))
    for off in (0, 3.75):
        pos = int((start + off) * sr)
        if pos >= n:
            continue
        length = min(n - pos, int(.75 * sr))
        z = np.arange(length) / sr
        audio[pos:pos + length] += .065 * np.exp(-5 * z) * np.sin(2 * np.pi * (52 - 16 * z) * z)
audio += .013 * np.sin(2 * np.pi * 49 * t)
audio *= np.minimum(1, t / 1.6) * np.clip((duration - t) / 2.6, 0, 1)
with wave.open(str(OUT / "SCORE_ORIGINALE.wav"), "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes((np.tanh(audio * 1.5) * 32767).astype("<i2").tobytes())

# --- Immagine sorgente + tela intera sfumata ---------------------------------
img = cv2.imread(str(source), cv2.IMREAD_COLOR)
assert img is not None
oh0, ow0 = img.shape[:2]
TARGET_W = 4320
img = cv2.resize(img, (TARGET_W, round(oh0 * TARGET_W / ow0)), interpolation=cv2.INTER_AREA)
oh, ow = img.shape[:2]
blur = cv2.GaussianBlur(cv2.resize(img, (W, H)), (0, 0), 46)
whole = cv2.convertScaleAbs(blur, alpha=.38, beta=0)
hh = round(W * oh / ow); yy = (H - hh) // 2
whole[yy:yy + hh] = cv2.resize(img, (W, hh), interpolation=cv2.INTER_AREA)

# --- Livelli di testo pre-renderizzati (RGBA) --------------------------------
def layer():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))

def wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        tst = (cur + " " + wd).strip()
        if draw.textlength(tst, font=font) <= max_w or not cur:
            cur = tst
        else:
            lines.append(cur); cur = wd
    if cur:
        lines.append(cur)
    return lines

def block(draw, lines, font, cx, top, lh, fill=CREAM):
    for i, ln in enumerate(lines):
        draw.text((cx, top + i * lh), ln, font=font, anchor="ma", fill=fill)

def to_arrays(lp):
    a = np.array(lp)
    return a[..., :3].astype(np.float32), a[..., 3].astype(np.float32) / 255.0

# brand fisso in alto
brand = layer(); bd = ImageDraw.Draw(brand)
bd.text((W // 2, 92), "A R T V I S I O N", font=ImageFont.truetype(SANS_B, 36),
        anchor="mm", fill=(238, 230, 214, 235))
bd.line([(W // 2 - 96, 128), (W // 2 + 96, 128)], fill=(238, 230, 214, 120), width=2)

# hook (prima inquadratura)
hook = layer(); hd = ImageDraw.Draw(hook)
hfont = ImageFont.truetype(SERIF_B, 68)
hl = wrap(hd, "Lewis Carroll contò 165 fate in questo quadro.", hfont, 880)
bh = 96 + len(hl) * 92
hd.rectangle([0, 250, W, 250 + bh], fill=(10, 9, 8, 205))
block(hd, hl, hfont, W // 2, 300, 92, fill=(247, 240, 226))
hd.text((W // 2, 250 + bh + 54), "05 / 2026", font=ImageFont.truetype(SANS, 34),
        anchor="mm", fill=(226, 217, 200, 220))

# reveal finale
reveal = layer(); rd = ImageDraw.Draw(reveal)
rd.rectangle([0, 0, W, H], fill=(8, 8, 10, 232))
rt = ImageFont.truetype(SERIF_B, 66)
rs = ImageFont.truetype(SANS, 40)
rlines = wrap(rd, "The Quarrel of Oberon and Titania", rt, 900)
top = 700
block(rd, rlines, rt, W // 2, top, 84, fill=(247, 240, 226))
rd.line([(W // 2 - 120, top + len(rlines) * 84 + 34), (W // 2 + 120, top + len(rlines) * 84 + 34)],
        fill=(238, 230, 214, 150), width=2)
block(rd, ["Sir Joseph Noel Paton", "1849"], rs, W // 2, top + len(rlines) * 84 + 96, 56,
      fill=(234, 226, 210))
rd.text((W // 2, top + len(rlines) * 84 + 240), "Scottish National Gallery · NG 293",
        font=ImageFont.truetype(SANS, 34), anchor="mm", fill=(206, 198, 182))
rd.text((W // 2, top + len(rlines) * 84 + 322), "Fonte: National Galleries of Scotland",
        font=ImageFont.truetype(SANS, 30), anchor="mm", fill=(176, 169, 156))
rd.text((W // 2, 1560), "Quante fate hai trovato?", font=ImageFont.truetype(SANS_B, 46),
        anchor="mm", fill=(243, 235, 221))

# didascalie per inquadratura
caps = []
cfont = ImageFont.truetype(SANS, 52)
for _, _, _, _, cap in SHOTS:
    lp = layer(); cd = ImageDraw.Draw(lp)
    if cap and cap != "@REVEAL":
        lines = wrap(cd, cap, cfont, 900)
        bh = 46 + len(lines) * 68
        y0 = 1430 - bh
        cd.rounded_rectangle([70, y0, W - 70, y0 + bh], radius=26, fill=(10, 9, 8, 176))
        for i, ln in enumerate(lines):
            cd.text((W // 2, y0 + 30 + i * 68), ln, font=cfont, anchor="ma", fill=(247, 240, 226))
    caps.append(to_arrays(lp))

brand_rgb, brand_a = to_arrays(brand)
hook_rgb, hook_a = to_arrays(hook)
reveal_rgb, reveal_a = to_arrays(reveal)

# --- Render ------------------------------------------------------------------
out_mp4 = OUT / "FINAL_1080x1920.mp4"
cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "rawvideo",
       "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "pipe:0",
       "-i", str(OUT / "SCORE_ORIGINALE.wav"), "-c:v", "libx264", "-preset", "medium",
       "-crf", "20", "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.1",
       "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-shortest",
       "-movflags", "+faststart", str(out_mp4)]
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

        # fade didascalia (0.4s in/out)
        ff = min(1.0, k / (FPS * .4)) * min(1.0, (count - 1 - k) / (FPS * .4))
        buf = blend(buf, cap_rgb, cap_a, ff)
        # brand sempre visibile
        buf = blend(buf, brand_rgb, brand_a, min(1.0, k / (FPS * .6)))

        if idx == 0:
            fh = min(1.0, k / (FPS * .5))
            buf = blend(buf, hook_rgb, hook_a, fh)
        if cap == "@REVEAL":
            fr = min(1.0, k / (FPS * .6))
            buf = blend(buf, reveal_rgb, reveal_a, fr)

        proc.stdin.write(np.clip(buf, 0, 255).astype(np.uint8).tobytes())
        if k == count // 2:
            contact.append(cv2.resize(cv2.cvtColor(np.clip(buf, 0, 255).astype(np.uint8),
                                                   cv2.COLOR_RGB2BGR), (216, 384),
                                     interpolation=cv2.INTER_AREA))
    timeline.append({"subject_for_human_review": name, "seconds": seconds,
                     "camera_from": a, "camera_to": b, "caption": cap})
proc.stdin.close()
if proc.wait() != 0:
    raise RuntimeError("FFmpeg rendering failed")
print("MP4_RENDERED", out_mp4.stat().st_size, sha(out_mp4), flush=True)

# --- Contact sheet -----------------------------------------------------------
rows = (len(contact) + 3) // 4
sheet = np.full((rows * 384, 4 * 216, 3), 19, dtype=np.uint8)
for i, fr in enumerate(contact):
    r, c = divmod(i, 4)
    sheet[r * 384:(r + 1) * 384, c * 216:(c + 1) * 216] = fr
cv2.imwrite(str(OUT / "CONTATTO_REGIA.jpg"), sheet)

# --- Copertina social (concept hook) -----------------------------------------
art = Image.open(source).convert("RGB")
cw, ch = art.size
# crop verticale centrato sul cuore della scena
tw = int(ch * 1080 / 1920)
left = max(0, (cw - tw) // 2)
cover = art.crop((left, 0, left + tw, ch)).resize((1080, 1920), Image.LANCZOS)
ov = layer(); cd = ImageDraw.Draw(ov)
cd.rectangle([0, 0, 1080, 470], fill=(10, 9, 8, 210))
cd.rectangle([0, 1620, 1080, 1920], fill=(10, 9, 8, 210))
cd.text((540, 120), "LEWIS CARROLL NE CONTÒ", font=ImageFont.truetype(SANS_B, 50),
        anchor="ma", fill=(240, 232, 216))
cd.text((540, 210), "165", font=ImageFont.truetype(SERIF_B, 150), anchor="ma", fill=(247, 240, 226))
cd.text((540, 372), "TU QUANTE NE VEDI?", font=ImageFont.truetype(SANS_B, 54),
        anchor="ma", fill=(240, 232, 216))
cd.text((540, 1720), "ARTVISION · STORIE NELL'ARTE", font=ImageFont.truetype(SANS, 38),
        anchor="mm", fill=(236, 228, 212))
cd.text((540, 1790), "Sir J. N. Paton · 1849 · Scottish National Gallery", font=ImageFont.truetype(SANS, 30),
        anchor="mm", fill=(206, 198, 182))
cover = Image.alpha_composite(cover.convert("RGBA"), ov).convert("RGB")
cover.save(OUT / "COPERTINA_SOCIAL.jpg", quality=92)

# --- Dossier + note ----------------------------------------------------------
(OUT / "FONTI_E_DIRITTI.json").write_text(json.dumps({
    "work": "The Quarrel of Oberon and Titania", "artist": "Sir Joseph Noel Paton",
    "year": 1849, "collection": "National Galleries of Scotland", "inventory": "NG 293",
    "dimensions_cm": {"height": 99.0, "width": 152.0},
    "museum_object": "https://www.nationalgalleries.org/art-and-artists/5264",
    "source_page": "https://commons.wikimedia.org/wiki/File:Sir_Joseph_Noel_Paton_-_The_Quarrel_of_Oberon_and_Titania_-_Google_Art_Project.jpg",
    "source_url": "https://upload.wikimedia.org/wikipedia/commons/f/f2/Sir_Joseph_Noel_Paton_-_The_Quarrel_of_Oberon_and_Titania_-_Google_Art_Project.jpg",
    "source_sha256": sha(source), "source_pixels": [4001, 2600],
    "artwork_copyright": "Pubblico dominio (autore deceduto 1901); riproduzione fedele PD-Art",
    "audio_copyright": "Colonna sonora originale sintetizzata localmente — nessun diritto di terzi",
    "third_party_assets": "none",
    "voice": "none (versione senza voce narrante)",
    "publication_allowed": True,
    "environment_note": "Prodotto in ambiente senza GEMINI_API_KEY: versione senza voce.",
    "crop_review": "PENDING (gradita una verifica umana del taglio, non bloccante)"
}, ensure_ascii=False, indent=2), encoding="utf8")

(OUT / "SOCIAL_POSTS.json").write_text(json.dumps({
    "public_title": "Lewis Carroll contò 165 fate in questo quadro. Tu quante ne vedi?",
    "facebook": "Lewis Carroll contò 165 fate in questo dipinto. La sfida è provarci anche solo per qualche istante: parti da Oberon e Titania, poi segui la folla di figure che riempie la scena.\n\nLa National Galleries of Scotland identifica il soggetto come la contesa tra i due sovrani per un changeling, un bambino umano portato nel regno delle fate. Esposto a Edimburgo nel 1850, il dipinto fu definito «picture of the season».\n\nThe Quarrel of Oberon and Titania, Sir Joseph Noel Paton, 1849. Scottish National Gallery, NG 293. Fonte: National Galleries of Scotland.\n\nQuante fate riesci a trovare?",
    "instagram": "Lewis Carroll ne contò 165. Tu quante ne trovi?\n\nOberon e Titania sono al centro; intorno, una scena ispirata a Shakespeare si riempie di creature minuscole. Un invito a guardare una seconda volta, senza perdere di vista il dipinto autentico.\n\nSir Joseph Noel Paton, The Quarrel of Oberon and Titania, 1849. Scottish National Gallery, NG 293.\n\nFonte: National Galleries of Scotland. #ArtHistory #JosephNoelPaton #NationalGalleriesOfScotland",
    "tiktok": "165 fate in un solo quadro. Quante ne vedi tu? Scrivi il tuo numero. Sir Joseph Noel Paton, The Quarrel of Oberon and Titania, 1849. Fonte: National Galleries of Scotland, NG 293. #Arte #StoriaDellArte #ArtTok",
    "youtube_shorts": "Lewis Carroll contò 165 fate in The Quarrel of Oberon and Titania. Al centro, Oberon e Titania si contendono il changeling; intorno, Paton riempie la scena di creature fatate. Quante riesci a individuarne?\n\nOpera: The Quarrel of Oberon and Titania (1849)\nArtista: Sir Joseph Noel Paton\nCollezione: Scottish National Gallery, Edimburgo\nInventario: NG 293\nFonti: National Galleries of Scotland.\n\n#JosephNoelPaton #ArtHistory #NationalGalleriesOfScotland",
    "credits": "Sir Joseph Noel Paton, The Quarrel of Oberon and Titania, 1849, Scottish National Gallery, NG 293. Riproduzione di pubblico dominio. Colonna sonora originale."
}, ensure_ascii=False, indent=2), encoding="utf8")

(OUT / "STORYBOARD.json").write_text(json.dumps({
    "variant": "social_final_vertical_no_voice", "fps": FPS, "resolution": [W, H],
    "total_s": duration, "shots": timeline, "uses_actual_painting": True
}, ensure_ascii=False, indent=2), encoding="utf8")

(OUT / "LEGGIMI.md").write_text(
    "# Paton — versione social finale (pronta alla pubblicazione)\n\n"
    "Video verticale 1080x1920, 30 fps, testo a schermo hook-first, didascalie, musica originale.\n"
    "Nessuna voce narrante: l'ambiente non dispone di GEMINI_API_KEY (voce Gacrux).\n\n"
    "- FINAL_1080x1920.mp4 — il file da pubblicare\n"
    "- COPERTINA_SOCIAL.jpg — copertina 1080x1920\n"
    "- SCORE_ORIGINALE.wav — colonna sonora originale\n"
    "- FONTI_E_DIRITTI.json — fonti, licenze, note\n"
    "- SOCIAL_POSTS.json — testi per Facebook / Instagram / TikTok / YouTube\n"
    "- CONTATTO_REGIA.jpg, STORYBOARD.json — regia e controllo\n\n"
    "Diritti: dipinto di pubblico dominio + audio originale. Nessun asset di terzi.\n"
    "Nessun upload automatico: la pubblicazione resta una decisione umana.\n", encoding="utf8")

print("DONE works_dir", OUT, "duration_s", round(duration, 2), flush=True)
