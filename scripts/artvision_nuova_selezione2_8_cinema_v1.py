#!/usr/bin/env python3
"""Nuova selezione 30 - opere #2-#8, versioni Cinema (revisione privata).
Nessuna pubblicazione, nessun Gold, nessuna API a pagamento, nessuna voce."""
import hashlib, json, subprocess, urllib.parse, urllib.request, wave
from pathlib import Path
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont

UA = {"User-Agent": "ArtVisionPrivateReview/1.0 (https://github.com/GGIANLUCAA/Tra-le-pagine-)"}
def wm(name):
    return "https://commons.wikimedia.org/wiki/Special:Redirect/file/" + urllib.parse.quote(name)

WORKS = [
 dict(order=2, slug="medea-sandys", title="Medea", artist="Frederick Sandys", year="1866/1868",
      collection="Birmingham Museums Trust", inventory="1925P105", h_cm=61.0, w_cm=46.0,
      museum_object="https://artsandculture.google.com/asset/medea/KgFfi1wPKa6Bmg",
      source_url=wm("Medea - Frederick Sandys - Google Cultural Institute.jpg"),
      source_sha1="eacdb97bd39b174c946fbf44a60ea85c0bbf34ac", source_pixels=[4698, 6287],
      screen_title="MEDEA", screen_sub="FREDERICK SANDYS  |  1868", tscale=1.30,
      shots=[("APERTURA",4.2,None,None),("CAPELLI",4.0,(.60,.20,.42),(.58,.20,.36)),
             ("VOLTO",4.4,(.52,.30,.32),(.50,.30,.27)),("FILTRO",4.4,(.46,.58,.34),(.48,.58,.28)),
             ("ABITO",4.0,(.62,.64,.40),(.60,.64,.34)),("MONILI",3.9,(.66,.46,.30),(.64,.46,.26)),
             ("CREATURE",4.2,(.28,.90,.34),(.30,.90,.29)),("MARE",4.0,(.18,.42,.42),(.20,.42,.36)),
             ("PROFILO",4.5,(.50,.40,.40),(.50,.40,.34)),("INTERO",5.6,None,None)]),
 dict(order=3, slug="fairy-tale-of-the-kings", title="Fairy Tale of the Kings", artist="Mikalojus Konstantinas Ciurlionis",
      year="1909", collection="M. K. Ciurlionis National Museum of Art, Kaunas", inventory="Ct 35", h_cm=70.2, w_cm=75.3,
      museum_object="https://ciurlionis.eu/en/content/karaliu-pasaka-35",
      source_url=wm("Mikalojus Konstantinas Ciurlionis - FAIRY TALE (FAIRY TALE OF KINGS) - 1909.jpg"),
      source_sha1="92f77154c3a9e3f02c445b20dcfdb8175722623f", source_pixels=[2309, 2167],
      screen_title="FAIRY TALE OF THE KINGS", screen_sub="M. K. CIURLIONIS  |  1909", tscale=0.82,
      shots=[("APERTURA",4.2,None,None),("CIELO",4.2,(.50,.16,.36),(.48,.16,.31)),
             ("REGNO_SIN",4.4,(.26,.42,.42),(.29,.42,.36)),("REGNO_DES",4.4,(.74,.42,.42),(.71,.42,.36)),
             ("FIGURE",4.4,(.50,.52,.34),(.50,.52,.29)),("PONTE",4.1,(.50,.66,.36),(.48,.66,.30)),
             ("TERRA",4.1,(.42,.82,.36),(.44,.82,.30)),("INTERO",5.6,None,None)]),
 dict(order=4, slug="sonata-of-the-sea-finale", title="Sonata of the Sea: Finale", artist="Mikalojus Konstantinas Ciurlionis",
      year="1908", collection="M. K. Ciurlionis National Museum of Art, Kaunas", inventory="Ct 14", h_cm=73.2, w_cm=63.0,
      museum_object="https://ciurlionis.eu/en/content/sonata-5-finale",
      source_url="https://lh3.googleusercontent.com/ci/AL18g_TIXkoHxMN6nTBHlGubknvWQtGHSY7MXDigVUPECPCS98TOWJRIdF_k6YcpiOmEkBq6GMrZdWgh=w2400",
      source_sha1=None, source_pixels=[1025, 1200],
      screen_title="SONATA OF THE SEA", screen_sub="M. K. CIURLIONIS  |  1908", tscale=0.92,
      shots=[("APERTURA",4.2,None,None),("ONDA",4.4,(.48,.22,.40),(.50,.22,.34)),
             ("LUCE",4.2,(.44,.40,.34),(.46,.40,.29)),("STRUTTURA",4.3,(.60,.34,.36),(.58,.34,.31)),
             ("MARE",4.1,(.50,.72,.36),(.50,.72,.30)),("BARCA",4.6,(.52,.86,.28),(.52,.86,.24)),
             ("INTERO",5.6,None,None)]),
 dict(order=5, slug="iron-rolling-mill", title="The Iron Rolling Mill", artist="Adolph Menzel", year="1872-75",
      collection="Alte Nationalgalerie, Staatliche Museen zu Berlin", inventory="A I 201", h_cm=158.0, w_cm=254.0,
      museum_object="https://id.smb.museum/object/958605",
      source_url=wm("Adolph Menzel - Eisenwalzwerk - Google Art Project.jpg"),
      source_sha1="c08a3929ebc67533e7857b94f4d4a4cc19e51216", source_pixels=[3543, 2199],
      screen_title="THE IRON ROLLING MILL", screen_sub="ADOLPH MENZEL  |  1872-75", tscale=0.82,
      shots=[("APERTURA",4.2,None,None),("FORNO",4.4,(.30,.48,.44),(.33,.48,.38)),
             ("GETTATA",4.4,(.36,.62,.36),(.38,.62,.31)),("OPERAI",4.4,(.30,.74,.40),(.30,.74,.34)),
             ("VOLTI",4.1,(.46,.72,.32),(.45,.72,.27)),("MACCHINE",4.3,(.76,.58,.42),(.74,.58,.36)),
             ("SCINTILLE",4.0,(.60,.40,.32),(.58,.40,.27)),("SALA",4.4,(.50,.60,.52),(.50,.60,.46)),
             ("INTERO",5.6,None,None)]),
 dict(order=6, slug="defense-of-the-sampo", title="The Defense of the Sampo", artist="Akseli Gallen-Kallela", year="1896",
      collection="Turku Art Museum, Turku", inventory="66", h_cm=122.0, w_cm=125.0,
      museum_object="https://fi.wikipedia.org/wiki/Sammon_puolustus",
      source_url=wm("Sammon puolustus.jpg"),
      source_sha1="3188f6de70201eada5a21c33508b58588ccf16ef", source_pixels=[1788, 1758],
      screen_title="THE DEFENSE OF THE SAMPO", screen_sub="GALLEN-KALLELA  |  1896", tscale=0.74,
      shots=[("APERTURA",4.2,None,None),("SAMPO",4.4,(.46,.52,.34),(.48,.52,.29)),
             ("CANTO",4.4,(.58,.46,.36),(.56,.46,.31)),("PRUA",4.1,(.28,.56,.36),(.30,.56,.30)),
             ("ACQUA",4.1,(.50,.78,.36),(.50,.78,.30)),("CIELO",4.1,(.46,.20,.36),(.46,.20,.30)),
             ("FIGURE",4.3,(.60,.60,.34),(.58,.60,.29)),("INTERO",5.6,None,None)]),
 dict(order=7, slug="lemminkainen-mother", title="Lemminkainen's Mother", artist="Akseli Gallen-Kallela", year="1897",
      collection="Ateneum Art Museum, Finnish National Gallery, Helsinki", inventory="A I 640", h_cm=85.5, w_cm=108.5,
      museum_object="https://kokoelma.kansallisgalleria.fi/en/object/398211",
      source_url=wm("Akseli Gallen-Kallela - Lemminkäinen's Mother - Google Art Project.jpg"),
      source_sha1="710c9589b9e1820b2d34174c4190530e8531b02d", source_pixels=[4001, 3147],
      screen_title="LEMMINKAINEN'S MOTHER", screen_sub="GALLEN-KALLELA  |  1897", tscale=0.80,
      shots=[("APERTURA",4.2,None,None),("MADRE",4.4,(.58,.42,.40),(.57,.42,.34)),
             ("VOLTO",4.1,(.58,.34,.28),(.57,.34,.24)),("FIGLIO",4.4,(.50,.72,.36),(.50,.72,.30)),
             ("RASTRELLO",4.1,(.20,.86,.32),(.22,.86,.27)),("CIGNO",4.1,(.74,.40,.36),(.72,.40,.30)),
             ("LAGO",4.2,(.80,.24,.40),(.78,.24,.34)),("PINO",4.0,(.14,.40,.42),(.16,.40,.36)),
             ("INTERO",5.6,None,None)]),
 dict(order=8, slug="architects-dream", title="The Architect's Dream", artist="Thomas Cole", year="1840",
      collection="Toledo Museum of Art", inventory="1949.162", h_cm=134.7, w_cm=213.6,
      museum_object="https://www.toledomuseum.org/",
      source_url=wm("Thomas Cole - Architect’s Dream - Google Art Project.jpg"),
      source_sha1="b958fe829e43954922bfbc9d29198282ae168238", source_pixels=[7615, 4679],
      screen_title="THE ARCHITECT'S DREAM", screen_sub="THOMAS COLE  |  1840", tscale=0.82,
      shots=[("APERTURA",4.2,None,None),("EGITTO",4.4,(.18,.52,.44),(.21,.52,.38)),
             ("GRECIA",4.4,(.46,.50,.42),(.46,.50,.36)),("GOTICO",4.4,(.78,.46,.44),(.76,.46,.38)),
             ("ARCHITETTO",4.4,(.14,.82,.40),(.16,.82,.34)),("LUCE",4.1,(.50,.36,.38),(.50,.36,.32)),
             ("COLONNA",4.0,(.34,.80,.34),(.35,.80,.29)),("MONUMENTI",4.3,(.50,.52,.52),(.50,.52,.46)),
             ("INTERO",5.6,None,None)]),
]
W, H, FPS, RATE = 1080, 1920, 20, 22050

def score(duration, outdir):
    sr = RATE; n = int((duration + .15) * sr); t = np.arange(n) / sr
    audio = np.zeros(n, dtype=np.float64)
    chords = [(65.41, 98.00, 130.81), (73.42, 110.00, 146.83), (55.00, 82.41, 110.00), (61.74, 92.50, 123.47)]
    for idx, start in enumerate(np.arange(0, duration, 7.5)):
        end = min(duration + .1, start + 8.9); a, b = int(start * sr), min(n, int(end * sr)); u = t[a:b] - start
        env = np.minimum(1, u / 1.35) * np.maximum(0, np.minimum(1, (end - start - u) / 1.45))
        for j, freq in enumerate(chords[idx % 4]):
            audio[a:b] += .035 / (1 + j * .32) * env * (np.sin(2 * np.pi * freq * u) + .2 * np.sin(4 * np.pi * freq * u))
        for off in (0, 3.75):
            pos = int((start + off) * sr)
            if pos >= n: continue
            length = min(n - pos, int(.75 * sr)); z = np.arange(length) / sr
            audio[pos:pos + length] += .065 * np.exp(-5 * z) * np.sin(2 * np.pi * (52 - 16 * z) * z)
    audio += .013 * np.sin(2 * np.pi * 49 * t)
    audio *= np.minimum(1, t / 1.5) * np.clip((duration - t) / 2.4, 0, 1)
    with wave.open(str(outdir / "SCORE_ORIGINALE.wav"), "wb") as wav:
        wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(sr)
        wav.writeframes((np.tanh(audio * 1.5) * 32767).astype("<i2").tobytes())

def fit_font(text, max_w, path, start):
    size = start
    while size > 20:
        f = ImageFont.truetype(path, size)
        if f.getbbox(text)[2] <= max_w: return f
        size -= 2
    return ImageFont.truetype(path, 20)

results = {}
for wk in WORKS:
    slug = wk["slug"]
    out = Path(f"output/owner-{slug}-cinema-v1"); out.mkdir(parents=True, exist_ok=True)
    source = out / "ORIGINAL_ARTWORK.jpg"
    got = False
    try:
        req = urllib.request.Request(wk["source_url"], headers=UA)
        with urllib.request.urlopen(req, timeout=95) as res:
            data = res.read(90_000_000)
        if wk["source_sha1"] and hashlib.sha1(data).hexdigest() != wk["source_sha1"]:
            raise ValueError("source SHA1 mismatch")
        source.write_bytes(data)
        with Image.open(source) as im:
            assert im.format == "JPEG"; im.verify()
        got = True
    except Exception as e:
        print("SOURCE_FAILED", slug, type(e).__name__, str(e)[:140], flush=True)
    if not got:
        results[slug] = "SOURCE_GATE_FAILED"; continue
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

    shots = wk["shots"]; duration = sum(s[1] for s in shots)
    score(duration, out)
    img = cv2.imread(str(source), cv2.IMREAD_COLOR); assert img is not None
    oh, ow = img.shape[:2]
    tw = min(4200, ow)
    img = cv2.resize(img, (tw, round(oh * tw / ow)), interpolation=cv2.INTER_AREA); oh, ow = img.shape[:2]
    blur = cv2.GaussianBlur(cv2.resize(img, (W, H)), (0, 0), 42)
    whole = cv2.convertScaleAbs(blur, alpha=.4, beta=0)
    hh = round(W * oh / ow); yy = (H - hh) // 2
    whole[yy:yy + hh] = cv2.resize(img, (W, hh), interpolation=cv2.INTER_AREA)

    cover = Image.new("RGB", (1080, 1920), (12, 14, 17))
    art = Image.open(source).convert("RGB"); art.thumbnail((1080, 1460), Image.Resampling.LANCZOS)
    cover.paste(art, ((1080 - art.width) // 2, (1920 - art.height) // 2))
    d = ImageDraw.Draw(cover)
    serif = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
    sans = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    d.text((540, 172), wk["screen_title"], font=fit_font(wk["screen_title"], 940, serif, 70), anchor="mm", fill=(237, 229, 210))
    d.text((540, 1755), wk["screen_sub"], font=fit_font(wk["screen_sub"], 940, sans, 33), anchor="mm", fill=(237, 229, 210))
    cover.save(out / "COPERTINA.jpg", quality=92)

    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "pipe:0", "-i", str(out / "SCORE_ORIGINALE.wav"),
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", str(out / "VIDEO_REVIEW.mp4")]
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
                ch = min(oh, max(80, round(oh * height))); cw = min(ow, max(80, round(ch * W / H)))
                x = max(0, min(ow - cw, round(cx * ow - cw / 2))); y = max(0, min(oh - ch, round(cy * oh - ch / 2)))
                frame = cv2.resize(img[y:y + ch, x:x + cw], (W, H), interpolation=cv2.INTER_AREA)
            if idx == 0 and k < int(2.5 * FPS):
                a1 = min(.68, k / (FPS * .5) * .68); dark = np.zeros_like(frame)
                cv2.rectangle(dark, (0, 85), (W, 270), (17, 17, 20), -1)
                frame = cv2.addWeighted(frame, 1 - a1, dark, a1, 0)
                cv2.putText(frame, wk["screen_title"], (62, 159), cv2.FONT_HERSHEY_SIMPLEX, wk["tscale"], (239, 230, 215), 2, cv2.LINE_AA)
                cv2.putText(frame, wk["screen_sub"], (64, 209), cv2.FONT_HERSHEY_SIMPLEX, wk["tscale"] * .55, (219, 209, 192), 1, cv2.LINE_AA)
            proc.stdin.write(frame.tobytes())
            if k == count // 2:
                contact.append(cv2.resize(frame, (216, 384), interpolation=cv2.INTER_AREA))
        timeline.append({"subject_for_human_review": name, "seconds": seconds, "camera_from": a, "camera_to": b})
    proc.stdin.close()
    if proc.wait() != 0:
        results[slug] = "FFMPEG_FAILED"; continue
    cols = 4; rows = (len(contact) + cols - 1) // cols
    sheet = np.full((rows * 384, cols * 216, 3), 19, dtype=np.uint8)
    for idx, frame in enumerate(contact):
        r, col = divmod(idx, cols)
        sheet[r * 384:(r + 1) * 384, col * 216:(col + 1) * 216] = frame
    cv2.imwrite(str(out / "CONTATTO_REGIA.jpg"), sheet)

    rights = {"work": wk["title"], "artist": wk["artist"], "year": wk["year"],
              "collection": wk["collection"], "inventory": wk["inventory"],
              "height_cm": wk["h_cm"], "width_cm": wk["w_cm"], "museum_object": wk["museum_object"],
              "source_url": wk["source_url"], "original_source_sha1": wk["source_sha1"],
              "original_source_sha256": sha(source), "original_source_bytes": source.stat().st_size,
              "source_pixels": wk["source_pixels"],
              "license_claim": "Wikimedia Commons Public Domain (PD-Art) / GAC museum image, PD artist",
              "italian_territorial_commercial_review": "PENDING", "publication_allowed": False,
              "museum_reconstruction": "none", "audio": "original locally synthesized score"}
    (out / "FONTI_E_DIRITTI.json").write_text(json.dumps(rights, ensure_ascii=False, indent=2), encoding="utf8")
    (out / "STORYBOARD_REGIA.json").write_text(json.dumps({
        "variant": "cinema_standard", "total_s": duration, "shots": timeline,
        "human_visual_review": "PENDING", "semantic_crop_review": "PENDING",
        "uses_actual_painting": True}, indent=2), encoding="utf8")
    (out / "SOCIAL_POSTS.json").write_text(json.dumps({
        "public_title": f"{wk['title']} - {wk['artist']} ({wk['year'].split('/')[0]})",
        "note": "Bozze da revisione umana; crediti museali nel piede.",
        "credits": f"{wk['artist']}, {wk['title']}, {wk['year']}, {wk['collection']} {wk['inventory']}; riproduzione fedele pubblico dominio. Verifica diritti territoriali in corso. Colonna sonora originale."},
        ensure_ascii=False, indent=2), encoding="utf8")
    (out / "ISTRUZIONI.md").write_text(
        "Revisione tecnica privata. Solo dipinto originale e partitura originale. "
        "Revisione umana artistica/semantica e verifica diritti commerciali territoriali PENDING. "
        "Nessun Gold, nessuna pubblicazione. Nuova selezione 30 - versione Cinema.\n", encoding="utf8")
    results[slug] = "OK " + sha(out / "VIDEO_REVIEW.mp4")[:16]
    print("DONE", slug, results[slug], flush=True)

print("SUMMARY", json.dumps(results, ensure_ascii=False), flush=True)
