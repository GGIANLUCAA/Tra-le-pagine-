#!/usr/bin/env python3
"""Social reel renderer V4 — directed edit (mixed shot grammar + carrellate).

Why V4: V3 was clean but flat — the same "gallery plate" for every work, no
direction. A professional edit uses a MIX of shots and moves:

  * HOOK: extreme close-up (brushwork) full-bleed, name slams in.
  * FULL-BLEED: cinematic cover-crop push / pan on iconic works.
  * DETAIL: extreme close-ups that punch-in on the beat (texture / emotion).
  * CARRELLATA: a real dolly sweeping along a "museum wall" of paintings.
  * GALLERY PLATE: the whole painting, calmly, so nothing is ever lost.
  * CLIMAX: darker, harder push on the last, most intense work.

Transitions are directed too: cross-dissolve, push/slide (whip feel) and a
snap zoom — chosen per cut. No per-beat brightness flash (no "palpiti").
The whole painting is still shown; the mix is what makes it feel authored.

1080x1920, 30 fps, music only, English captions.
"""
import math, os, subprocess
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30

ARTIST = "Vincent van Gogh"
DATES = "1853 – 1890"
COUNTRY = "Netherlands"
KICKER = "MASTERPIECES IN MOTION"
CTA = "FOLLOW FOR ONE MASTERPIECE A DAY"

# (file, title, year)
WORKS = [
    ("Starry_Night.jpg",          "The Starry Night",          1889),
    ("Wheatfield_Cypresses.jpg",  "Wheatfield with Cypresses", 1889),
    ("Sunflowers.jpg",            "Sunflowers",                1888),
    ("Irises.jpg",                "Irises",                    1889),
    ("Almond_Blossoms.jpg",       "Almond Blossom",            1890),
    ("The_Sower.jpg",             "The Sower",                 1888),
    ("Cafe_Terras.jpg",           "Café Terrace at Night",     1888),
    ("Yellow_House.jpg",          "The Yellow House",          1888),
    ("Bedroom_Arles.jpg",         "The Bedroom",               1888),
    ("Potato_Eaters.jpg",         "The Potato Eaters",         1885),
    ("Self_Portrait.jpg",         "Self-Portrait",             1889),
    ("Wheatfield_Crows.jpg",      "Wheatfield with Crows",     1890),
]
SN, WC, SF, IR, AB, SO, CT, YH, BR, PE, SP, WCR = range(12)

IMG_DIR = Path("/tmp/vangogh")
MUSIC = Path("/tmp/reel_music.mp3")
OUT = Path("/workspace/output/social_vangogh_v4")

SERIF_BOLD = "/usr/share/fonts/opentype/urw-base35/P052-Bold.otf"
SERIF_R = "/usr/share/fonts/opentype/urw-base35/P052-Roman.otf"
SANS = "/usr/share/fonts/opentype/urw-base35/NimbusSans-Regular.otf"
SANS_BOLD = "/usr/share/fonts/opentype/urw-base35/NimbusSans-Bold.otf"
FALLBACK = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"

IVORY = (244, 239, 230, 255)
IVORY_SOFT = (222, 214, 199, 255)
GOLD = (232, 199, 132, 255)

# gallery plate
PBOX_W, PBOX_H = 880, 1035
PCY = 786

FADE_IN, FADE_OUT = 0.5, 1.4


# ---------------------------------------------------------------- helpers
def _font(path, size):
    for p in (path, FALLBACK):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def smooth(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def tracked(d, cx, y, text, font, fill, tracking, stroke_w=0, stroke_fill=None):
    widths = [d.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        d.text((x, y), ch, font=font, fill=fill,
               stroke_width=stroke_w, stroke_fill=stroke_fill or (0, 0, 0, 0))
        x += w + tracking
    return total


def load_art(path):
    im = Image.open(path).convert("RGB")
    if max(im.size) > 2600:
        s = 2600 / max(im.size)
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    return np.array(im)


def cover_crop(art, z, cxf, cyf):
    """full-bleed 1080x1920 cover-crop -> float 0..1"""
    ah, aw = art.shape[:2]
    fr = W / H
    ar = aw / ah
    if ar >= fr:
        ch0, cw0 = ah, ah * fr
    else:
        cw0, ch0 = aw, aw / fr
    vw, vh = cw0 / z, ch0 / z
    cx = vw / 2 + (aw - vw) * cxf
    cy = vh / 2 + (ah - vh) * cyf
    iw, ih = int(round(vw)), int(round(vh))
    x0 = max(0, min(aw - iw, int(round(cx - vw / 2))))
    y0 = max(0, min(ah - ih, int(round(cy - vh / 2))))
    crop = art[y0:y0 + ih, x0:x0 + iw]
    interp = cv2.INTER_AREA if iw >= W else cv2.INTER_LINEAR
    return cv2.resize(crop, (W, H), interpolation=interp).astype(np.float32) / 255.0


# ---------------------------------------------------------------- gallery plate
def ambient_bg(art):
    ah, aw = art.shape[:2]
    sc = max(W / aw, H / ah)
    r = cv2.resize(art, (round(aw * sc), round(ah * sc)), interpolation=cv2.INTER_AREA)
    bg = r[(r.shape[0] - H) // 2:(r.shape[0] - H) // 2 + H,
           (r.shape[1] - W) // 2:(r.shape[1] - W) // 2 + W].astype(np.float32)
    bg = cv2.GaussianBlur(bg, (0, 0), 58)
    lum = bg.mean(axis=2, keepdims=True)
    bg = bg * 0.86 + lum * 0.14
    bg = bg * 0.38 + 9.0
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    rad = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - PCY) / (H * 0.42)) ** 2)
    bg += (np.clip(1 - rad, 0, 1) ** 2 * 26)[..., None]
    return np.clip(bg, 0, 255) / 255.0


def make_card(art):
    ah, aw = art.shape[:2]
    sc = min(PBOX_W / aw, PBOX_H / ah)
    pw, ph = int(round(aw * sc)), int(round(ah * sc))
    p = cv2.resize(art, (pw, ph), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
    mat, PAD = 6, 64
    cw, ch = pw + 2 * mat + 2 * PAD, ph + 2 * mat + 2 * PAD
    rgb = np.zeros((ch, cw, 3), np.float32)
    sh = np.zeros((ch, cw), np.float32)
    sh[PAD - 7:PAD + ph + 2 * mat + 7, PAD - 7:PAD + pw + 2 * mat + 7] = 1.0
    alpha = cv2.GaussianBlur(sh, (0, 0), 22) * 0.55
    m0, m1 = PAD, PAD + ph + 2 * mat
    n0, n1 = PAD, PAD + pw + 2 * mat
    rgb[m0:m1, n0:n1] = 0.92
    rgb[m0 + mat:m1 - mat, n0 + mat:n1 - mat] = p
    alpha[m0:m1, n0:n1] = 1.0
    return np.concatenate([rgb * alpha[..., None], alpha[..., None]], axis=2).astype(np.float32)


def plate_frame(card, bg, tl, dur, box_cy=PCY, zoom=0.035, drift=9.0):
    p = min(1.0, max(0.0, tl / dur))
    s = 1.0 + zoom * (0.5 - 0.5 * math.cos(2 * math.pi * p))
    dy = drift * math.sin(2 * math.pi * p)
    cw, ch = card.shape[1], card.shape[0]
    M = np.float32([[s, 0, W / 2 - s * cw / 2], [0, s, box_cy + dy - s * ch / 2]])
    w = cv2.warpAffine(card, M, (W, H), flags=cv2.INTER_LINEAR,
                       borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    a = w[..., 3:4]
    return bg * (1 - a) + w[..., :3]          # premultiplied rgb over the wall


# ---------------------------------------------------------------- carrellata
def build_strip(idxs, arts, ph=1150, gap=150, cy=880):
    margin = int(W * 0.42)
    widths = [int(round(ph * arts[i].shape[1] / arts[i].shape[0])) for i in idxs]
    sw = sum(widths) + gap * (len(idxs) - 1) + 2 * margin
    yy = np.arange(H)[:, None].astype(np.float32) / (H - 1)
    mid = np.clip(1 - np.abs(yy - 0.46) / 0.46, 0, 1) ** 1.3
    wall = np.zeros((H, sw, 3), np.float32)
    wall[..., 0] = 15 + 30 * mid
    wall[..., 1] = 13 + 26 * mid
    wall[..., 2] = 12 + 22 * mid
    xx = np.arange(sw)[None, :, None].astype(np.float32) / (sw - 1)
    wall *= (1 - 0.28 * np.abs(xx - 0.5) * 2)
    x = margin
    y0 = cy - ph // 2
    for i, wd in zip(idxs, widths):
        p = cv2.resize(arts[i], (wd, ph), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
        mask = np.zeros((H, sw), np.float32)
        mask[y0 + 12:y0 + ph + 12, x + 14:x + wd + 14] = 1.0
        wall *= (1 - cv2.GaussianBlur(mask, (0, 0), 26)[..., None] * 0.5)
        wall[y0 - 3:y0 + ph + 3, x - 3:x + wd + 3] = 0.60
        wall[y0:y0 + ph, x:x + wd] = p
        x += wd + gap
    return wall, margin, widths


def dolly_frame(strip, margin, widths, tl, dur, direction):
    sw = strip.shape[1]
    p = min(1.0, max(0.0, tl / dur))
    ps = smooth(p)
    start = max(0, margin - int(W * 0.30))
    end = min(sw - W, margin + sum(widths) + 150 * (len(widths) - 1) + int(W * 0.30) - W)
    end = max(start + 1, end)
    x0 = start + (end - start) * ps if direction == "right" else end - (end - start) * ps
    z = 1.0 + 0.06 * (0.5 - 0.5 * math.cos(2 * math.pi * p))
    hh, ww = int(H / z), int(W / z)
    y0 = (H - hh) // 2
    x0 = int(max(0, min(sw - ww, x0)))
    win = strip[y0:y0 + hh, x0:x0 + ww]
    return cv2.resize(win, (W, H), interpolation=cv2.INTER_LINEAR)


# ---------------------------------------------------------------- grade
def _vignette():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    return np.clip(1 - 0.20 * np.clip((r - 0.58) / 0.75, 0, 1), 0, 1)[..., None].astype(np.float32)


VIGNETTE = _vignette()
GRAIN = [np.random.normal(0, 1.9 / 255.0, (H, W, 1)).astype(np.float32) for _ in range(8)]


def grade(x, dark=1.0):
    x = np.clip((x - 0.5) * 1.07 + 0.5, 0, 1)
    luma = (0.2126 * x[..., 0] + 0.7152 * x[..., 1] + 0.0722 * x[..., 2])
    l = luma[..., None]
    x = np.clip(l + (x - l) * 1.12, 0, 1)
    d = l - 0.5
    x[..., 0] = np.clip(x[..., 0] + 0.04 * d[..., 0], 0, 1)
    x[..., 2] = np.clip(x[..., 2] - 0.04 * d[..., 0], 0, 1)
    return x * VIGNETTE * dark


# ---------------------------------------------------------------- overlays
def _grad(top_frac, amax):
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    y0 = int(H * top_frac)
    for y in range(y0, H):
        gd.line([(0, y), (W, y)], fill=(0, 0, 0, int(amax * ((y - y0) / (H - y0)) ** 1.15)))
    return g


def build_hook():
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ov = Image.alpha_composite(ov, _grad(0.58, 245))
    d = ImageDraw.Draw(ov)
    tracked(d, W / 2, 196, KICKER, _font(SANS, 34), GOLD, 9, 1, (0, 0, 0, 190))
    ny = H * 0.70
    tracked(d, W / 2, ny, ARTIST.upper(), _font(SERIF_BOLD, 104), IVORY, 3, 3, (0, 0, 0, 225))
    d.line([(W / 2 - W * 0.11, ny + 150), (W / 2 + W * 0.11, ny + 150)],
           fill=(224, 205, 172, 235), width=3)
    tracked(d, W / 2, ny + 176, DATES, _font(SANS, 36), IVORY_SOFT, 5, 1, (0, 0, 0, 190))
    return np.array(ov)


def build_end():
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ov = Image.alpha_composite(ov, _grad(0.52, 250))
    d = ImageDraw.Draw(ov)
    ny = H * 0.665
    tracked(d, W / 2, 210, KICKER, _font(SANS, 32), GOLD, 9, 1, (0, 0, 0, 185))
    tracked(d, W / 2, ny, ARTIST.upper(), _font(SERIF_BOLD, 92), IVORY, 3, 3, (0, 0, 0, 225))
    d.line([(W / 2 - W * 0.10, ny + 132), (W / 2 + W * 0.10, ny + 132)],
           fill=(224, 205, 172, 235), width=3)
    tracked(d, W / 2, ny + 158, DATES, _font(SANS, 34), IVORY_SOFT, 5, 1, (0, 0, 0, 190))
    tracked(d, W / 2, ny + 232, CTA, _font(SANS_BOLD, 36), GOLD, 6, 1, (0, 0, 0, 190))
    return np.array(ov)


def build_caption(title, year):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ov = Image.alpha_composite(ov, _grad(0.70, 210))
    d = ImageDraw.Draw(ov)
    ty = H * 0.745
    tracked(d, W / 2, ty, title, _font(SERIF_R, 54), IVORY, 1, 2, (0, 0, 0, 205))
    tracked(d, W / 2, ty + 78, str(year), _font(SANS, 30), GOLD, 8, 1, (0, 0, 0, 185))
    return np.array(ov)


def blend(frame, ov, alpha):
    if alpha <= 0.001:
        return frame
    a = (ov[..., 3:4].astype(np.float32) / 255.0) * alpha
    return frame * (1 - a) + (ov[..., :3].astype(np.float32) / 255.0) * a


# ---------------------------------------------------------------- transitions
def shift_x(f, dx):
    out = np.zeros_like(f)
    if dx == 0:
        return f
    if abs(dx) >= W:
        return out
    if dx > 0:
        out[:, dx:] = f[:, :W - dx]
    else:
        out[:, :W + dx] = f[:, -dx:]
    return out


def push(prev, cur, p, direction):
    p = smooth(p)
    dx = int(p * W)
    out = np.zeros_like(prev)
    if direction == "l":                      # cur enters from the right
        out[:, :W - dx] = prev[:, dx:]
        out[:, W - dx:] = cur[:, :dx]
    else:                                     # cur enters from the left
        out[:, dx:] = prev[:, :W - dx]
        out[:, :dx] = cur[:, W - dx:]
    return out


def snap_zoom(prev, cur, p):
    p = smooth(p)
    z = 1.14 - 0.14 * p
    cu = cv2.warpAffine(cur, np.float32([[z, 0, W / 2 - z * W / 2], [0, z, H / 2 - z * H / 2]]),
                        (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    return prev * (1 - p) + cu * p


# ---------------------------------------------------------------- beats
def load_beats(audio_path):
    wav = "/tmp/_reel_audio_v4.wav"
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-i", str(audio_path), "-ar", "22050", "-ac", "1", wav], check=True)
    from scipy.io import wavfile
    from scipy.signal import stft, find_peaks
    from scipy.ndimage import uniform_filter1d
    sr, data = wavfile.read(wav)
    data = data.astype(np.float32) / 32768.0
    hop, n_fft = 512, 2048
    _, _, Z = stft(data, fs=sr, nperseg=n_fft, noverlap=n_fft - hop)
    flux = np.maximum(0, np.diff(np.abs(Z), axis=1)).sum(axis=0)
    flux = uniform_filter1d(flux, size=3)
    flux = flux / (flux.max() + 1e-9)
    peaks, _ = find_peaks(flux, distance=int(0.3 * sr / hop), prominence=0.04)
    return peaks * hop / sr


# ---------------------------------------------------------------- shot list
# Each shot: (kind, beats, tin, tkind, params)
#   kind: plate / full / detail / dolly
#   tin : duration of the incoming transition (s)
#   tkind: dis / pushl / pushr / zoom
SHOTS = [
    dict(kind="detail", beats=4, tin=0.0,  tk="dis",
         art=SN, z=(2.60, 2.35), c=(.46, .33), cap=None),
    dict(kind="plate",  beats=5, tin=0.55, tk="zoom", art=SN, cap=None),
    dict(kind="dolly",  beats=9, tin=0.45, tk="pushr", wall=[WC, SF, IR], dir="right", cap=None),
    dict(kind="plate",  beats=4, tin=0.40, tk="pushr", art=AB, cap=("Almond Blossom", 1890)),
    dict(kind="detail", beats=4, tin=0.40, tk="dis",
         art=CT, z=(2.05, 1.85), c=(.50, .44), cap=None),
    dict(kind="dolly",  beats=9, tin=0.45, tk="pushl", wall=[SO, YH, BR], dir="left", cap=None),
    dict(kind="plate",  beats=4, tin=0.35, tk="pushl", art=PE, cap=("The Potato Eaters", 1885)),
    dict(kind="detail", beats=3, tin=0.40, tk="zoom",
         art=SF, z=(2.25, 2.00), c=(.50, .40), cap=None),
    dict(kind="full",   beats=5, tin=0.45, tk="dis",
         art=SP, z=(1.06, 1.20), c=(.50, .42), cap=("Self-Portrait", 1889)),
    dict(kind="plate",  beats=4, tin=0.45, tk="dis",
         art=WC, cap=("Wheatfield with Cypresses", 1889)),
    dict(kind="full",   beats=6, tin=0.50, tk="zoom",
         art=WCR, z=(1.02, 1.24), c=(.50, .56), dark=0.86, cap=None),
    dict(kind="plate",  beats=9, tin=0.60, tk="dis", art=WCR, cap=None, end=True),
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    beats = load_beats(MUSIC)
    ibi = float(np.median(np.diff(beats)))
    print(f"beats {len(beats)}, interval {ibi:.3f}s (~{60/ibi:.0f} BPM)")

    def snap(b):
        return max(1, round(b)) * ibi
    t0 = float(beats[np.searchsorted(beats, 1.0)])

    durs = [snap(s["beats"]) for s in SHOTS]
    bnd = [t0]
    for d in durs:
        bnd.append(bnd[-1] + d)
    video_dur = bnd[-1] - t0
    print(f"{len(SHOTS)} shots, total {video_dur:.1f}s")

    arts = [load_art(IMG_DIR / fn) for fn, _, _ in WORKS]
    cards = [make_card(a) for a in arts]
    bgs = [ambient_bg(a) for a in arts]

    # precompute per-shot static assets
    for s in SHOTS:
        if s["kind"] == "plate":
            s["card"] = cards[s["art"]]
            s["bg"] = bgs[s["art"]]
        elif s["kind"] == "dolly":
            s["strip"], s["margin"], s["widths"] = build_strip(s["wall"], arts)

    caps = {id(s): build_caption(*s["cap"]) for s in SHOTS if s.get("cap")}
    hook_ov, end_ov = build_hook(), build_end()

    def base(s, i, tl):
        d = durs[i]
        if s["kind"] == "plate":
            return plate_frame(s["card"], s["bg"], tl, d)
        if s["kind"] in ("full", "detail"):
            p = smooth(min(1.0, max(0.0, tl / d)))
            z = s["z"][0] + (s["z"][1] - s["z"][0]) * p
            return cover_crop(arts[s["art"]], z, s["c"][0], s["c"][1])
        return dolly_frame(s["strip"], s["margin"], s["widths"], tl, d, s["dir"])

    # cover
    cov = grade(blend(base(SHOTS[1], 1, durs[1] * 0.7), hook_ov, 1.0))
    Image.fromarray((np.clip(cov, 0, 1) * 255).astype(np.uint8)).save(
        str(OUT / "COPERTINA.jpg"), quality=95)

    raw = OUT / "raw_v4.mp4"
    ff = subprocess.Popen(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-c:v", "libx264", "-preset", "medium", "-crf", "24", "-maxrate", "5M", "-bufsize", "10M",
         "-profile:v", "high", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(raw)],
        stdin=subprocess.PIPE)

    total = int(math.ceil(video_dur * FPS))
    print(f"rendering {total} frames")
    for f in range(total):
        t = t0 + f / FPS
        tv = f / FPS
        i = min(len(SHOTS) - 1, max(0, np.searchsorted(bnd, t, side="right") - 1))
        s, tl = SHOTS[i], t - bnd[i]
        canvas = base(s, i, tl)
        if i > 0 and tl < s["tin"] and s["tin"] > 0:
            prev = base(SHOTS[i - 1], i - 1, durs[i - 1])
            p = tl / s["tin"]
            if s["tk"] == "dis":
                canvas = prev * (1 - smooth(p)) + canvas * smooth(p)
            elif s["tk"] == "pushr":
                canvas = push(prev, canvas, p, "r")
            elif s["tk"] == "pushl":
                canvas = push(prev, canvas, p, "l")
            else:
                canvas = snap_zoom(prev, canvas, p)

        canvas = grade(canvas, s.get("dark", 1.0)) + GRAIN[f % len(GRAIN)]

        # captions (plate / full shots, not the very first or the end card)
        key = id(s)
        if s.get("cap") and 0 < i < len(SHOTS) - 1:
            ai = smooth((tl - 0.30) / 0.55)
            ao = 1.0 - smooth((tl - (durs[i] - 0.75)) / 0.5)
            canvas = blend(canvas, caps[key], max(0.0, min(ai, ao)))

        if i == 0 or i == 1:                     # hook across the opening two shots
            hook_end = bnd[2] - t0
            ai = smooth(tv / 0.55)
            ao = 1.0 - smooth((tv - (hook_end - 0.7)) / 0.5)
            canvas = blend(canvas, hook_ov, max(0.0, min(ai, ao)))
        if s.get("end"):
            canvas = blend(canvas, end_ov, smooth((tl - (durs[i] - 2.0)) / 0.9))

        k = 1.0
        if tv < FADE_IN:
            k = min(k, tv / FADE_IN)
        if tv > video_dur - FADE_OUT:
            k = min(k, max(0.0, (video_dur - tv) / FADE_OUT))
        if k < 1.0:
            canvas = canvas * k

        ff.stdin.write((np.clip(canvas, 0, 1) * 255).astype(np.uint8).tobytes())
        if f % 200 == 0:
            print(f"  frame {f}/{total}")

    ff.stdin.close()
    ff.wait()
    print("raw written")

    seg = OUT / "music_seg.m4a"
    fo = max(0.0, video_dur - FADE_OUT)
    af = (f"afade=t=in:st=0:d=0.8,afade=t=out:st={fo:.2f}:d={FADE_OUT:.2f},"
          "loudnorm=I=-14:TP=-1.5:LRA=11")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-ss", f"{t0:.3f}", "-i", str(MUSIC), "-t", f"{video_dur:.3f}",
                    "-map", "0:a:0", "-vn", "-af", af, "-c:a", "aac", "-b:a", "192k", str(seg)],
                   check=True)

    master = OUT / "REEL_VANGOGH_V4.mp4"
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-i", str(raw), "-i", str(seg),
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "copy", str(master)],
                   check=True)
    raw.unlink(missing_ok=True)
    seg.unlink(missing_ok=True)
    print(f"MASTER: {master} ({master.stat().st_size/1e6:.1f} MB)")

    (OUT / "DIRITTI_E_FONTI.txt").write_text(
        f"Artista: {ARTIST} ({DATES}, {COUNTRY})\n"
        f"Musica: Dreamy Flashback - Kevin MacLeod (CC BY 4.0)\n"
        f"Opere: Wikimedia Commons (pubblico dominio)\n"
        f"Formato: reel verticale 1080x1920, montaggio misto "
        f"(dettagli + campo intero + carrellate + galleria), {video_dur:.0f}s, inglese\n",
        encoding="utf-8")
    print("done")


if __name__ == "__main__":
    main()
