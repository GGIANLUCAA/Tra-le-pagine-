#!/usr/bin/env python3
"""Tra le Pagine - asset grafici di serie (copertina, card titolo, card brand).
Testi e grafiche originali; nessuna copertina editoriale protetta."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

D = "/workspace/tra_le_pagine_la_metamorfosi_20261121_0028"
ILL = f"{D}/illustrazioni"
W, H = 1080, 1920
PETROLIO = (12, 42, 53)
ORO = (200, 164, 106)
AVORIO = (246, 241, 230)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def fit_cover(img, w=W, h=H):
    iw, ih = img.size
    s = max(w / iw, h / ih)
    img = img.resize((int(iw * s + 1), int(ih * s + 1)), Image.LANCZOS)
    iw, ih = img.size
    left = (iw - w) // 2
    top = (ih - h) // 2
    return img.crop((left, top, left + w, top + h))


def tracked_text(draw, cx, y, text, fnt, fill, tracking, anchor="ma", shadow=True):
    widths = [draw.textlength(c, font=fnt) for c in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for c, w in zip(text, widths):
        if shadow:
            draw.text((x + 2, y + 2), c, font=fnt, fill=(0, 0, 0, 160))
        draw.text((x, y), c, font=fnt, fill=fill)
        x += w + tracking


def vignette_panel(size, box, color=(6, 22, 29), alpha=190, radius=0):
    lay = Image.new("L", size, 0)
    dr = ImageDraw.Draw(lay)
    dr.rectangle(box, fill=alpha)
    return lay


# ---------------- COPERTINA ----------------
base = fit_cover(Image.open(f"{D}/copertina_illustrazione.jpg").convert("RGB"))
grad = Image.new("RGBA", (W, H), (0, 0, 0, 0))
# darken top and bottom bands for legibility
top = Image.new("L", (W, H), 0)
td = ImageDraw.Draw(top)
for y in range(0, 520):
    td.line([(0, y), (W, y)], fill=int(200 * (1 - y / 520)))
for y in range(H - 640, H):
    td.line([(0, y), (W, y)], fill=int(215 * min(1, (y - (H - 640)) / 300)))
base = Image.composite(Image.new("RGB", (W, H), PETROLIO), base, top)

cov = base.convert("RGBA")
dr = ImageDraw.Draw(cov)
# top brand
tracked_text(dr, W // 2, 118, "T R A   L E   P A G I N E", font(SANS_B, 44), ORO, 2)
dr.line([(W // 2 - 150, 190), (W // 2 + 150, 190)], fill=ORO, width=3)
dr.text((W // 2, 210), "una storia alla volta", font=font(SANS, 34), fill=AVORIO, anchor="ma")
# title
tracked_text(dr, W // 2, 1180, "LA METAMORFOSI", font(SERIF_B, 118), AVORIO, 3)
dr.line([(W // 2 - 260, 1360), (W // 2 + 260, 1360)], fill=ORO, width=4)
dr.text((W // 2, 1390), "Franz Kafka", font=font(SERIF_B, 66), fill=ORO, anchor="ma")
dr.text((W // 2, 1810), "TRA LE PAGINE · Episodio", font=font(SANS, 30), fill=(220, 214, 200), anchor="ma")
cov.convert("RGB").save(f"{D}/COPERTINA.jpg", quality=92)
cov.convert("RGB").save(f"{D}/copertina.png")
print("copertina OK")

# ---------------- CARD TITOLO (integrazione su scena 02) ----------------
ti = fit_cover(Image.open(f"{ILL}/scena_02_praga.jpg").convert("RGB")).convert("RGBA")
band = Image.new("L", (W, H), 0)
bd = ImageDraw.Draw(band)
for y in range(560, 1180):
    bd.line([(0, y), (W, y)], fill=170)
ti = Image.composite(Image.new("RGB", (W, H), PETROLIO), ti.convert("RGB"), band).convert("RGBA")
dr = ImageDraw.Draw(ti)
dr.text((W // 2, 690), "TRA LE PAGINE", font=font(SANS_B, 40), fill=ORO, anchor="ma")
tracked_text(dr, W // 2, 780, "LA METAMORFOSI", font(SERIF_B, 108), AVORIO, 3)
dr.line([(W // 2 - 200, 940), (W // 2 + 200, 940)], fill=ORO, width=4)
dr.text((W // 2, 975), "Franz Kafka · 1915", font=font(SERIF_B, 56), fill=ORO, anchor="ma")
ti.convert("RGB").save(f"{D}/illustrazioni/_titolo_scena_02.png")
print("titolo card OK")

# ---------------- BRAND CARD ----------------
brand = Image.new("RGB", (W, H), PETROLIO)
dr = ImageDraw.Draw(brand)
for i in range(6):
    off = 60 + i * 10
    dr.rectangle([off, off, W - off, H - off], outline=(20, 55, 66), width=2)
dr.rectangle([80, 80, W - 80, H - 80], outline=ORO, width=3)
dr.line([(W // 2 - 220, 900), (W // 2 + 220, 900)], fill=ORO, width=3)
tracked_text(dr, W // 2, 800, "TRA LE PAGINE", font(SERIF_B, 96), AVORIO, 6)
dr.text((W // 2, 960), "una storia alla volta", font=font(SANS, 46), fill=ORO, anchor="ma")
dr.text((W // 2, 1720), "Illustrazioni e narrazione realizzate con supporto AI;",
        font=font(SANS, 26), fill=(150, 165, 170), anchor="ma")
dr.text((W // 2, 1760), "selezione e supervisione editoriale.",
        font=font(SANS, 26), fill=(150, 165, 170), anchor="ma")
brand.save(f"{D}/brand_card.png")
print("brand card OK")

# ---------------- SCENE PRONTE 1080x1920 ----------------
os.makedirs(f"{D}/scene_1080", exist_ok=True)
scenes = [f"scena_{i:02d}_" for i in range(1, 20)]
import glob
files = sorted(glob.glob(f"{ILL}/scena_*.jpg"))
from PIL import ImageEnhance
for f in files:
    name = os.path.basename(f)[:-4]
    im = fit_cover(Image.open(f).convert("RGB"))
    im = ImageEnhance.Brightness(im).enhance(1.06)
    im = ImageEnhance.Color(im).enhance(1.05)
    im.save(f"{D}/scene_1080/{name}.png")
print("scene_1080:", len(files))
