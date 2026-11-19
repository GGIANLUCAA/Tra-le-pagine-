#!/usr/bin/env python3
"""Nuova selezione 30 — opera #1, versione Cinema. Revisione privata.
Nessuna pubblicazione, nessun Gold, nessuna API a pagamento, nessuna voce."""
import hashlib, json, subprocess, urllib.request, wave
from pathlib import Path
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont

out = Path("output/owner-paton-quarrel-cinema-v1")
out.mkdir(parents=True, exist_ok=True)
source = out / "ORIGINAL_ARTWORK.jpg"
page = "https://commons.wikimedia.org/wiki/File:Sir_Joseph_Noel_Paton_-_The_Quarrel_of_Oberon_and_Titania_-_Google_Art_Project.jpg"
original = "https://upload.wikimedia.org/wikipedia/commons/f/f2/Sir_Joseph_Noel_Paton_-_The_Quarrel_of_Oberon_and_Titania_-_Google_Art_Project.jpg"
fallback = "https://commons.wikimedia.org/wiki/Special:Redirect/file/Sir_Joseph_Noel_Paton_-_The_Quarrel_of_Oberon_and_Titania_-_Google_Art_Project.jpg"
sha1_expected = "110a416fe89aa28937506aaea96726a009671af1"
source_url = None
for url in (original, fallback):
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "ArtVisionPrivateReview/1.0 (https://github.com/GGIANLUCAA/Tra-le-pagine-)"})
        with urllib.request.urlopen(req, timeout=95) as res:
            data = res.read(60_000_000)
        if hashlib.sha1(data).hexdigest() != sha1_expected:
            raise ValueError("Commons original SHA1 mismatch")
        source.write_bytes(data)
        with Image.open(source) as img:
            assert img.format == "JPEG"
            img.verify()
        source_url = url
        break
    except Exception as e:
        print("SOURCE_ATTEMPT_FAILED", type(e).__name__, str(e)[:150], flush=True)
if not source_url:
    raise RuntimeError("Original source unavailable, source gate failed: no render")
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
print("ORIGINAL_VERIFIED", source.stat().st_size, sha(source), flush=True)

# Inquadrature registiche, tutte ricavate dal dipinto autentico. camera=(cx,cy,altezza_frac)
shots = [
    ("APERTURA",      4.0, None,                 None),
    ("COURT",         4.2, (.42, .46, .52),      (.40, .45, .46)),
    ("OBERON",        4.4, (.33, .40, .40),      (.36, .41, .35)),
    ("TITANIA",       4.4, (.55, .42, .40),      (.52, .42, .34)),
    ("SCONTRO",       4.6, (.44, .44, .34),      (.46, .44, .30)),
    ("FOLLA_SINISTRA",4.2, (.16, .62, .52),      (.20, .60, .46)),
    ("FOLLA_DESTRA",  4.2, (.82, .58, .52),      (.78, .57, .46)),
    ("DANZATRICI",    4.3, (.63, .68, .40),      (.60, .67, .35)),
    ("CREATURE",      4.1, (.24, .74, .40),      (.27, .73, .35)),
    ("FLORA",         4.2, (.50, .84, .36),      (.48, .83, .31)),
    ("MUSICI",        4.1, (.72, .72, .34),      (.70, .71, .30)),
    ("ONDA",          4.3, (.90, .50, .42),      (.88, .50, .37)),
    ("CENTRO",        4.6, (.40, .52, .46),      (.42, .52, .40)),
    ("VOLTI",         4.2, (.47, .38, .30),      (.45, .38, .27)),
    ("REGINA",        4.3, (.56, .46, .30),      (.54, .46, .27)),
    ("INTERO",        5.4, None,                 None),
]
W, H, FPS = 1080, 1920, 20
duration = sum(s[1] for s in shots)

# Partitura originale sintetizzata localmente: nessuna registrazione di terzi.
sr = 22050
n = int((duration + .15) * sr)
t = np.arange(n) / sr
audio = np.zeros(n, dtype=np.float64)
chords = [(65.41, 98.00, 130.81), (73.42, 110.00, 146.83),
          (55.00, 82.41, 110.00), (61.74, 92.50, 123.47)]
for idx, start in enumerate(np.arange(0, duration, 7.5)):
    end = min(duration + .1, start + 8.9)
    a, b = int(start * sr), min(n, int(end * sr))
    u = t[a:b] - start
    env = np.minimum(1, u / 1.35) * np.maximum(0, np.minimum(1, (end - start - u) / 1.45))
    for j, freq in enumerate(chords[idx % 4]):
        audio[a:b] += .035 / (1 + j * .32) * env * (np.sin(2 * np.pi * freq * u) + .2 * np.sin(4 * np.pi * freq * u))
    for off in (0, 3.75):
        pos = int((start + off) * sr)
        if pos >= n:
            continue
        length = min(n - pos, int(.75 * sr))
        z = np.arange(length) / sr
        audio[pos:pos + length] += .065 * np.exp(-5 * z) * np.sin(2 * np.pi * (52 - 16 * z) * z)
audio += .013 * np.sin(2 * np.pi * 49 * t)
audio *= np.minimum(1, t / 1.5) * np.clip((duration - t) / 2.4, 0, 1)
with wave.open(str(out / "SCORE_ORIGINALE.wav"), "wb") as wav:
    wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(sr)
    wav.writeframes((np.tanh(audio * 1.5) * 32767).astype("<i2").tobytes())

img = cv2.imread(str(source), cv2.IMREAD_COLOR)
assert img is not None
oh, ow = img.shape[:2]
img = cv2.resize(img, (4200, round(oh * 4200 / ow)), interpolation=cv2.INTER_AREA)
oh, ow = img.shape[:2]
blur = cv2.GaussianBlur(cv2.resize(img, (W, H)), (0, 0), 42)
whole = cv2.convertScaleAbs(blur, alpha=.4, beta=0)
hh = round(W * oh / ow); yy = (H - hh) // 2
whole[yy:yy + hh] = cv2.resize(img, (W, hh), interpolation=cv2.INTER_AREA)

cover = Image.new("RGB", (1080, 1920), (12, 14, 17))
art = Image.open(source).convert("RGB"); art.thumbnail((1080, 1460), Image.Resampling.LANCZOS)
cover.paste(art, ((1080 - art.width) // 2, (1920 - art.height) // 2))
d = ImageDraw.Draw(cover)
d.text((540, 172), "OBERON & TITANIA", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 70), anchor="mm", fill=(237, 229, 210))
d.text((540, 1755), "JOSEPH NOEL PATON  ·  1849", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 31), anchor="mm", fill=(237, 229, 210))
cover.save(out / "COPERTINA.jpg", quality=92)

cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "rawvideo",
       "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "pipe:0",
       "-i", str(out / "SCORE_ORIGINALE.wav"), "-c:v", "libx264", "-preset", "veryfast",
       "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
       "-shortest", "-movflags", "+faststart", str(out / "VIDEO_REVIEW.mp4")]
proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
contact = []; timeline = []
for idx, (name, seconds, a, b) in enumerate(shots):
    count = round(seconds * FPS)
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
        if idx == 0 and k < int(2.5 * FPS):
            a1 = min(.68, k / (FPS * .5) * .68)
            dark = np.zeros_like(frame)
            cv2.rectangle(dark, (0, 85), (W, 270), (17, 17, 20), -1)
            frame = cv2.addWeighted(frame, 1 - a1, dark, a1, 0)
            cv2.putText(frame, "OBERON & TITANIA", (62, 159), cv2.FONT_HERSHEY_SIMPLEX, 1.15, (239, 230, 215), 2, cv2.LINE_AA)
            cv2.putText(frame, "JOSEPH NOEL PATON  |  1849", (64, 209), cv2.FONT_HERSHEY_SIMPLEX, .62, (219, 209, 192), 1, cv2.LINE_AA)
        proc.stdin.write(frame.tobytes())
        if k == count // 2:
            contact.append(cv2.resize(frame, (216, 384), interpolation=cv2.INTER_AREA))
    timeline.append({"subject_for_human_review": name, "seconds": seconds, "camera_from": a, "camera_to": b})
proc.stdin.close()
if proc.wait() != 0:
    raise RuntimeError("FFmpeg rendering failed")

sheet = np.full((4 * 384, 4 * 216, 3), 19, dtype=np.uint8)
for idx, frame in enumerate(contact):
    row, col = divmod(idx, 4)
    sheet[row * 384:(row + 1) * 384, col * 216:(col + 1) * 216] = frame
cv2.imwrite(str(out / "CONTATTO_REGIA.jpg"), sheet)

rights = {
    "work": "The Quarrel of Oberon and Titania", "artist": "Sir Joseph Noel Paton", "year": 1849,
    "collection": "National Galleries of Scotland", "inventory": "NG 293",
    "height_cm": 99.0, "width_cm": 152.0,
    "museum_object": "https://www.nationalgalleries.org/art-and-artists/5264",
    "source_page": page, "source_url": source_url,
    "original_source_sha1": sha1_expected, "original_source_sha256": sha(source),
    "original_source_bytes": source.stat().st_size, "source_pixels": [4001, 2600],
    "license_claim": "Wikimedia Commons Public Domain / Google Art Project (PD-Art)",
    "italian_territorial_commercial_review": "PENDING",
    "publication_allowed": False,
    "museum_reconstruction": "none",
    "audio": "original locally synthesized score",
}
(out / "FONTI_E_DIRITTI.json").write_text(json.dumps(rights, ensure_ascii=False, indent=2), encoding="utf8")
(out / "STORYBOARD_REGIA.json").write_text(json.dumps({
    "variant": "cinema_standard", "total_s": duration, "shots": timeline,
    "human_visual_review": "PENDING", "semantic_crop_review": "PENDING",
    "uses_actual_painting": True}, indent=2), encoding="utf8")
posts = {
    "public_title": "The Quarrel of Oberon and Titania — Joseph Noel Paton (1849)",
    "facebook": "Due sovrani fatati si contendono un regno invisibile, circondati da centinaia di creature. Joseph Noel Paton dipinge nel 1849 The Quarrel of Oberon and Titania, ispirato al Sogno di una notte di mezza estate. #ArtHistory #Paton",
    "instagram": "Oberon e Titania, e attorno a loro un mondo intero di folletti, danzatrici e musici. Paton, 1849. Ogni angolo del quadro nasconde una figura diversa. #Painting #ArtHistory",
    "tiktok": "Guarda bene: questo quadro contiene centinaia di creature. E quasi nessuno le vede tutte. Paton, 1849. #ArtTok #History",
    "youtube_shorts": "The Quarrel of Oberon and Titania (1849): Sir Joseph Noel Paton popola la scena di figure fatate. Scene ricavate dall'opera autentica.",
    "credits": "Sir Joseph Noel Paton, The Quarrel of Oberon and Titania, 1849, National Galleries of Scotland NG 293; faithful Commons reproduction, pubblico dominio. Verifica diritti territoriali in corso. Colonna sonora originale.",
}
(out / "SOCIAL_POSTS.json").write_text(json.dumps(posts, ensure_ascii=False, indent=2), encoding="utf8")
(out / "ISTRUZIONI.md").write_text(
    "Revisione tecnica privata. Solo dipinto originale e partitura originale. "
    "Revisione umana artistica/semantica e verifica diritti commerciali territoriali PENDING. "
    "Nessun Gold, nessuna pubblicazione, nessuna modifica ai master. "
    "Nuova selezione 30 — opera #1 (versione Cinema).\n", encoding="utf8")
print("MP4_RENDERED", sha(out / "VIDEO_REVIEW.mp4"), flush=True)
