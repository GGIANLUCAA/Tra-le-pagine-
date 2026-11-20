#!/usr/bin/env python3
"""Social reel renderer V3 — gallery style, fluid, no strobing.

Fixes over V2 (based on the feedback "i palpiti sono orribili" / "non si vedono
quadri per intero"):

  * NO beat pulse and NO impact flash -> the strobing ("palpiti") is gone.
  * PAINTINGS SHOWN WHOLE: every artwork is fitted (contain) inside an elegant
    gallery plate instead of being cropped full-bleed to 9:16. You always see
    the entire painting.
  * FLUID motion: a slow "breathing" zoom + a gentle drift that stays inside the
    margins, so the artwork is never cut.
  * Soft CROSS-DISSOLVES between works (still timed on the musical beat), so the
    flow feels smooth instead of hard-cut.
  * Refined typography: hook (artist), a discreet caption under each work, and
    an end card with a call to action. All text stays inside the safe zones of
    Shorts / Reels.
  * Slightly longer, loop-friendly (fade in from black, fade out to black).

Vertical 1080x1920, 30 fps, music only (no voice), captions in English.
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

# Emotional arc, each entry: (file, title, year)
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

IMG_DIR = Path("/tmp/vangogh")
MUSIC = Path("/tmp/reel_music.mp3")
OUT = Path("/workspace/output/social_vangogh_v3")

# fonts — elegant, gallery-like (Palatino / Nimbus Sans)
SERIF_BOLD = "/usr/share/fonts/opentype/urw-base35/P052-Bold.otf"
SERIF_R = "/usr/share/fonts/opentype/urw-base35/P052-Roman.otf"
SERIF_I = "/usr/share/fonts/opentype/urw-base35/P052-Italic.otf"
SANS = "/usr/share/fonts/opentype/urw-base35/NimbusSans-Regular.otf"
SANS_BOLD = "/usr/share/fonts/opentype/urw-base35/NimbusSans-Bold.otf"
FALLBACK = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"

IVORY = (244, 239, 230, 255)
IVORY_SOFT = (222, 214, 199, 255)
GOLD = (232, 199, 132, 255)

# layout
BOX_W, BOX_H = 880, 1055      # max box the whole painting must fit into
CY = 792                      # vertical centre of the painting
PAD = 64                      # room around the painting for the soft shadow

# motion / timing
ZOOM = 0.035                  # breathing zoom (never crops: stays in the margin)
DRIFT = 9.0                   # gentle vertical drift (px)
DISS = 0.70                   # cross-dissolve between works (s)
FADE_IN = 0.6
FADE_OUT = 1.4


def _font(path, size):
    for p in (path, FALLBACK):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def smooth(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def tracked(d, cx, y, text, font, fill, tracking, stroke_w=0, stroke_fill=None):
    """Draw letter-spaced text centred on cx, top at y. Returns width."""
    widths = [d.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        d.text((x, y), ch, font=font, fill=fill,
               stroke_width=stroke_w, stroke_fill=stroke_fill or (0, 0, 0, 0))
        x += w + tracking
    return total


# ---------------------------------------------------------------- assets
def load_art(path):
    im = Image.open(path).convert("RGB")
    if max(im.size) > 2600:
        s = 2600 / max(im.size)
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    return np.array(im)


def ambient_bg(art):
    """Deep museum-wall backdrop: the painting itself, blurred & darkened."""
    ah, aw = art.shape[:2]
    sc = max(W / aw, H / ah)
    r = cv2.resize(art, (round(aw * sc), round(ah * sc)), interpolation=cv2.INTER_AREA)
    x0 = (r.shape[1] - W) // 2
    y0 = (r.shape[0] - H) // 2
    bg = r[y0:y0 + H, x0:x0 + W].astype(np.float32)
    bg = cv2.GaussianBlur(bg, (0, 0), 58)
    lum = bg.mean(axis=2, keepdims=True)
    bg = bg * 0.86 + lum * 0.14          # slight desaturate
    bg = bg * 0.40 + 10.0                # darken to a wall
    # soft light behind the painting (radial)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    rad = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - CY) / (H * 0.42)) ** 2)
    glow = np.clip(1 - rad, 0, 1) ** 2
    bg += (glow * 26)[..., None]
    return np.clip(bg, 0, 255) / 255.0


def make_card(art):
    """Painting (whole, fitted) + thin mat + soft drop shadow, as premultiplied
    RGBA float in 0..1 (channels 0:3 = rgb*alpha, 3 = alpha)."""
    ah, aw = art.shape[:2]
    sc = min(BOX_W / aw, BOX_H / ah)
    pw, ph = int(round(aw * sc)), int(round(ah * sc))
    p = cv2.resize(art, (pw, ph), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0

    mat = 6                                        # thin ivory mat around the work
    cw, ch = pw + 2 * mat + 2 * PAD, ph + 2 * mat + 2 * PAD
    rgb = np.zeros((ch, cw, 3), np.float32)
    alpha = np.zeros((ch, cw), np.float32)

    # soft shadow: blurred rectangle, offset a little downward
    sy0, sy1 = PAD - 7, PAD + ph + 2 * mat + 7
    sx0, sx1 = PAD - 7, PAD + pw + 2 * mat + 7
    sh = np.zeros((ch, cw), np.float32)
    sh[sy0:sy1, sx0:sx1] = 1.0
    sh = cv2.GaussianBlur(sh, (0, 0), 22) * 0.55
    alpha = np.maximum(alpha, sh)
    rgb[:] = 0.0                                   # shadow is pure black

    # the mat + painting
    m0, m1 = PAD, PAD + ph + 2 * mat
    n0, n1 = PAD, PAD + pw + 2 * mat
    rgb[m0:m1, n0:n1] = 0.92                       # ivory mat
    rgb[m0 + mat:m1 - mat, n0 + mat:n1 - mat] = p
    alpha[m0:m1, n0:n1] = 1.0

    card = np.concatenate([rgb * alpha[..., None], alpha[..., None]], axis=2)
    return card.astype(np.float32)


# ---------------------------------------------------------------- grade
def _vignette():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    return np.clip(1 - 0.18 * np.clip((r - 0.60) / 0.75, 0, 1), 0, 1)[..., None].astype(np.float32)


VIGNETTE = _vignette()
GRAIN_TILES = [np.random.normal(0, 1.9 / 255.0, (H, W, 1)).astype(np.float32) for _ in range(8)]


def grade(x):
    """x float 0..1 -> elegant cinematic grade (gentle, no strobing)."""
    x = np.clip((x - 0.5) * 1.06 + 0.5, 0, 1)                       # soft contrast
    luma = (0.2126 * x[..., 0] + 0.7152 * x[..., 1] + 0.0722 * x[..., 2])
    l = luma[..., None]
    x = np.clip(l + (x - l) * 1.10, 0, 1)                           # saturation
    d = l - 0.5
    x[..., 0] = np.clip(x[..., 0] + 0.035 * d[..., 0], 0, 1)        # warm highlights
    x[..., 2] = np.clip(x[..., 2] - 0.035 * d[..., 0], 0, 1)        # cool shadows
    return x * VIGNETTE


# ---------------------------------------------------------------- overlays
def _grad(top_frac, amax):
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    y0 = int(H * top_frac)
    for y in range(y0, H):
        a = int(amax * ((y - y0) / (H - y0)) ** 1.15)
        gd.line([(0, y), (W, y)], fill=(0, 0, 0, a))
    return g


def build_hook():
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ov = Image.alpha_composite(ov, _grad(0.60, 245))
    d = ImageDraw.Draw(ov)
    tracked(d, W / 2, 196, KICKER, _font(SANS, 34), GOLD, 9, 1, (0, 0, 0, 190))
    ny = H * 0.695
    tracked(d, W / 2, ny, ARTIST.upper(), _font(SERIF_BOLD, 104), IVORY, 3, 3, (0, 0, 0, 225))
    rw = W * 0.22
    d.line([(W / 2 - rw / 2, ny + 150), (W / 2 + rw / 2, ny + 150)],
           fill=(224, 205, 172, 235), width=3)
    tracked(d, W / 2, ny + 176, DATES, _font(SANS, 36), IVORY_SOFT, 5, 1, (0, 0, 0, 190))
    return np.array(ov)


def build_end():
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ov = Image.alpha_composite(ov, _grad(0.52, 250))
    d = ImageDraw.Draw(ov)
    ny = H * 0.665
    tracked(d, W / 2, ny, ARTIST.upper(), _font(SERIF_BOLD, 92), IVORY, 3, 3, (0, 0, 0, 225))
    d.line([(W / 2 - W * 0.10, ny + 132), (W / 2 + W * 0.10, ny + 132)],
           fill=(224, 205, 172, 235), width=3)
    tracked(d, W / 2, ny + 158, DATES, _font(SANS, 34), IVORY_SOFT, 5, 1, (0, 0, 0, 190))
    tracked(d, W / 2, ny + 232, CTA, _font(SANS_BOLD, 36), GOLD, 6, 1, (0, 0, 0, 190))
    return np.array(ov)


def build_caption(title, year):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ov = Image.alpha_composite(ov, _grad(0.70, 215))
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


# ---------------------------------------------------------------- beats
def load_beats(audio_path):
    wav = "/tmp/_reel_audio_v3.wav"
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


# ---------------------------------------------------------------- render
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    beats = load_beats(MUSIC)
    ibi = float(np.median(np.diff(beats)))
    print(f"beats: {len(beats)}, median interval {ibi:.3f}s (~{60/ibi:.0f} BPM)")

    def snap(d):
        return max(1, round(d / ibi)) * ibi

    t0 = float(beats[np.searchsorted(beats, 1.0)])
    n = len(WORKS)
    durs = [snap(4.8)] + [snap(2.8)] * (n - 2) + [snap(4.8)]
    bounds = [t0]
    for d in durs:
        bounds.append(bounds[-1] + d)
    video_dur = bounds[-1] - t0
    print(f"{n} works, total {video_dur:.1f}s")

    arts = [load_art(IMG_DIR / fn) for fn, _, _ in WORKS]
    bgs = [ambient_bg(a) for a in arts]
    cards = [make_card(a) for a in arts]
    for (fn, _, _), a in zip(WORKS, arts):
        print(f"  {fn}: {a.shape[1]}x{a.shape[0]}")

    hook_ov, end_ov = build_hook(), build_end()
    caps = [build_caption(t, y) for _, t, y in WORKS]
    cap_idx = set(range(1, n - 1))          # caption on every work except hook/outro

    def plate(i, tl):
        card = cards[i]
        p = min(1.0, max(0.0, tl / durs[i]))
        s = 1.0 + ZOOM * (0.5 - 0.5 * math.cos(2 * math.pi * p))
        dy = DRIFT * math.sin(2 * math.pi * p)
        cw, ch = card.shape[1], card.shape[0]
        M = np.float32([[s, 0, W / 2 - s * cw / 2], [0, s, CY + dy - s * ch / 2]])
        w = cv2.warpAffine(card, M, (W, H), flags=cv2.INTER_LINEAR,
                           borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
        a = w[..., 3:4]
        return bgs[i] * (1 - a) + w[..., :3]

    # cover image
    cov = grade(blend(plate(0, durs[0] * 0.55), hook_ov, 1.0))
    Image.fromarray((np.clip(cov, 0, 1) * 255).astype(np.uint8)).save(
        str(OUT / "COPERTINA.jpg"), quality=95)
    print("cover saved")

    raw = OUT / "raw_v3.mp4"
    ff = subprocess.Popen(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-c:v", "libx264", "-preset", "medium", "-crf", "24", "-maxrate", "5M", "-bufsize", "10M",
         "-profile:v", "high", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(raw)],
        stdin=subprocess.PIPE)

    total_frames = int(math.ceil(video_dur * FPS))
    print(f"rendering {total_frames} frames")

    for f in range(total_frames):
        t = t0 + f / FPS
        tv = f / FPS
        i = min(n - 1, max(0, np.searchsorted(bounds, t, side="right") - 1))
        tl = t - bounds[i]

        canvas = plate(i, tl)
        # cross-dissolve with the previous work at the start of this one
        if i > 0 and tl < DISS:
            a = smooth(tl / DISS)
            canvas = plate(i - 1, durs[i - 1]) * (1 - a) + canvas * a
            if i - 1 in cap_idx:
                ao = 1.0 - a
                canvas = blend(canvas, caps[i - 1], ao)

        canvas = grade(canvas)
        canvas = canvas + GRAIN_TILES[f % len(GRAIN_TILES)]

        # per-work caption
        if i in cap_idx:
            ai = smooth((tl - 0.30) / 0.55)
            ao = 1.0 - smooth((tl - (durs[i] - 0.75)) / 0.5)
            canvas = blend(canvas, caps[i], max(0.0, min(ai, ao)))

        # hook (first work) / end card (last work)
        if i == 0:
            ai = smooth(tv / 0.6)
            ao = 1.0 - smooth((tl - (durs[0] - 0.7)) / 0.5)
            canvas = blend(canvas, hook_ov, max(0.0, min(ai, ao)))
        if i == n - 1:
            a = smooth((tl - (durs[i] - 1.7)) / 0.9)
            canvas = blend(canvas, end_ov, a)

        # loop-friendly fades
        k = 1.0
        if tv < FADE_IN:
            k = min(k, tv / FADE_IN)
        if tv > video_dur - FADE_OUT:
            k = min(k, max(0.0, (video_dur - tv) / FADE_OUT))
        if k < 1.0:
            canvas = canvas * k

        ff.stdin.write((np.clip(canvas, 0, 1) * 255).astype(np.uint8).tobytes())
        if f % 150 == 0:
            print(f"  frame {f}/{total_frames}")

    ff.stdin.close()
    ff.wait()
    print("raw video written")

    seg = OUT / "music_seg.m4a"
    fade_out_at = max(0.0, video_dur - FADE_OUT)
    af = (f"afade=t=in:st=0:d=0.8,afade=t=out:st={fade_out_at:.2f}:d={FADE_OUT:.2f},"
          "loudnorm=I=-14:TP=-1.5:LRA=11")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-ss", f"{t0:.3f}", "-i", str(MUSIC), "-t", f"{video_dur:.3f}",
                    "-map", "0:a:0", "-vn", "-af", af, "-c:a", "aac", "-b:a", "192k", str(seg)],
                   check=True)

    master = OUT / "REEL_VANGOGH_V3.mp4"
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
        f"Formato: reel verticale 1080x1920 stile galleria, quadri interi, "
        f"dissolvenze fluide, {video_dur:.0f}s, inglese\n",
        encoding="utf-8")
    print("done")


if __name__ == "__main__":
    main()
