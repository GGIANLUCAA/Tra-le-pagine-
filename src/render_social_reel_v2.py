"""Social reel renderer V2 — emotion-first, cinema look, beat-locked.

Improvements over V1:
  - Emotional arc: works are ordered to build wonder -> warmth -> intimacy ->
    tragedy (climax) instead of an arbitrary sequence.
  - Cinematic grade: gentle S-curve contrast, saturation lift, warm highlights /
    cool shadows (split-tone), vignette and fine film grain.
  - Beat feel: every cut lands on the beat AND the image "breathes" with a
    micro zoom/brightness pulse that decays after each beat + a soft impact
    flash right after every cut.
  - Kinetic typography: elegant serif (Palatino) with letter-spacing, name +
    tagline that rise and fade in; hook plate and an end-card call-to-action.
  - Safe zones: text kept clear of the bottom UI area of TikTok / Reels.
  - Loop-friendly: fade from black at the start and to black at the end so the
    reel can replay seamlessly.

Vertical 1080x1920 full-bleed, dynamic camera, no voice (music only), English.
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
TAGLINE = "The Painter of Starry Skies"
CTA = "FOLLOW FOR ONE MASTERPIECE A DAY"

# Emotional arc: wonder -> wind/energy -> warmth -> delicacy -> hope -> work ->
# night colour -> the dream of home -> intimacy -> hardship -> the man -> tragedy
WORKS = [
    ("Starry_Night.jpg", "Starry Night"),
    ("Wheatfield_Cypresses.jpg", "Wheatfield with Cypresses"),
    ("Sunflowers.jpg", "Sunflowers"),
    ("Irises.jpg", "Irises"),
    ("Almond_Blossoms.jpg", "Almond Blossoms"),
    ("The_Sower.jpg", "The Sower"),
    ("Cafe_Terras.jpg", "Café Terrace at Night"),
    ("Yellow_House.jpg", "The Yellow House"),
    ("Bedroom_Arles.jpg", "Bedroom in Arles"),
    ("Potato_Eaters.jpg", "The Potato Eaters"),
    ("Self_Portrait.jpg", "Self-Portrait"),
    ("Wheatfield_Crows.jpg", "Wheatfield with Crows"),
]

IMG_DIR = Path("/tmp/vangogh")
MUSIC = Path("/tmp/reel_music.mp3")
OUT = Path("/workspace/output/social_vangogh_v2")
OUT.mkdir(parents=True, exist_ok=True)

# fonts — elegant, gallery-like
SERIF_BOLD = "/usr/share/fonts/opentype/urw-base35/P052-Bold.otf"      # Palatino
SERIF_R = "/usr/share/fonts/opentype/urw-base35/P052-Roman.otf"
SANS = "/usr/share/fonts/opentype/urw-base35/NimbusSans-Regular.otf"
SANS_BOLD = "/usr/share/fonts/opentype/urw-base35/NimbusSans-Bold.otf"
FALLBACK = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"


def _font(path, size):
    for p in (path, FALLBACK):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


# ---------------------------------------------------------------- motion plans
def _m(z0, z1, cx0, cx1, cy0, cy1):
    return dict(z0=z0, z1=z1, cx0=cx0, cx1=cx1, cy0=cy0, cy1=cy1)


LAND = [
    _m(1.02, 1.20, .50, .50, .50, .50),   # push in
    _m(1.18, 1.18, .00, 1.0, .50, .50),   # pan right
    _m(1.18, 1.18, 1.0, .00, .50, .50),   # pan left
    _m(1.24, 1.06, .50, .50, .50, .50),   # pull back
    _m(1.10, 1.24, .00, 1.0, .35, .65),   # diagonal lr
    _m(1.06, 1.22, .15, .50, .50, .50),   # push in from left
    _m(1.18, 1.18, .00, 1.0, .50, .50),   # pan right
    _m(1.26, 1.08, .50, .50, .58, .45),   # push out low
    _m(1.24, 1.12, 1.0, .00, .65, .35),   # diagonal rl
    _m(1.18, 1.18, 1.0, .00, .50, .50),   # pan left
    _m(1.02, 1.24, .50, .50, .50, .50),   # push in strong
    _m(1.22, 1.08, .55, .45, .50, .50),   # pull back
    _m(1.18, 1.18, .00, 1.0, .55, .45),   # pan right slight tilt
    _m(1.05, 1.18, .50, .50, .50, .50),   # slow push
]

PORT = [
    _m(1.02, 1.20, .50, .50, .50, .50),
    _m(1.18, 1.18, .50, .50, .00, 1.0),   # tilt down
    _m(1.18, 1.18, .50, .50, 1.0, .00),   # tilt up
    _m(1.24, 1.06, .50, .50, .50, .50),
    _m(1.10, 1.24, .50, .50, .00, 1.0),
    _m(1.06, 1.22, .50, .50, .15, .50),
    _m(1.18, 1.18, .50, .50, .00, 1.0),
    _m(1.26, 1.08, .50, .50, .42, .55),
    _m(1.24, 1.12, .50, .50, 1.0, .00),
    _m(1.18, 1.18, .50, .50, 1.0, .00),
    _m(1.02, 1.24, .50, .50, .50, .50),
    _m(1.22, 1.08, .42, .52, .50, .50),
    _m(1.18, 1.18, .55, .45, .00, 1.0),
    _m(1.05, 1.18, .50, .50, .50, .50),
]


def smooth(x):
    return x * x * (3 - 2 * x)


def load_beats(audio_path):
    wav = "/tmp/_reel_audio_v2.wav"
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-i", str(audio_path), "-ar", "22050", "-ac", "1", wav], check=True)
    from scipy.io import wavfile
    from scipy.signal import stft, find_peaks
    from scipy.ndimage import uniform_filter1d
    sr, data = wavfile.read(wav)
    data = data.astype(np.float32) / 32768.0
    hop, n_fft = 512, 2048
    _, _, Zxx = stft(data, fs=sr, nperseg=n_fft, noverlap=n_fft - hop)
    mag = np.abs(Zxx)
    flux = np.maximum(0, np.diff(mag, axis=1)).sum(axis=0)
    flux = uniform_filter1d(flux, size=3)
    flux = flux / (flux.max() + 1e-9)
    peaks, _ = find_peaks(flux, distance=int(0.3 * sr / hop), prominence=0.04)
    return peaks * hop / sr


def load_art(path):
    im = Image.open(path).convert("RGB")
    if max(im.size) > 2600:
        s = 2600 / max(im.size)
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    return np.array(im)


def camera_crop(arr, z, cxf, cyf):
    ah, aw = arr.shape[:2]
    fr = W / H
    ar = aw / ah
    if ar >= fr:
        ch0 = ah; cw0 = ah * fr
    else:
        cw0 = aw; ch0 = aw / fr
    vw = cw0 / z
    vh = ch0 / z
    cx = vw / 2 + (aw - vw) * cxf
    cy = vh / 2 + (ah - vh) * cyf
    iw, ih = int(round(vw)), int(round(vh))
    x0 = max(0, min(aw - iw, int(round(cx - vw / 2))))
    y0 = max(0, min(ah - ih, int(round(cy - vh / 2))))
    crop = arr[y0:y0 + ih, x0:x0 + iw]
    interp = cv2.INTER_AREA if iw >= W else cv2.INTER_LINEAR
    return cv2.resize(crop, (W, H), interpolation=interp)


# ---------------------------------------------------------------- type & plates
def tracked(d, cx, y, text, font, fill, tracking, stroke_w=0, stroke_fill=None):
    """Draw letter-spaced text centred on cx at top y. Returns drawn width."""
    widths = [d.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        d.text((x, y), ch, font=font, fill=fill,
               stroke_width=stroke_w, stroke_fill=stroke_fill or (0, 0, 0, 0))
        x += w + tracking
    return total


def _grad(top):
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    y0 = int(H * top)
    for y in range(y0, H):
        a = int(230 * ((y - y0) / (H - y0)) ** 1.2)
        gd.line([(0, y), (W, y)], fill=(0, 0, 0, a))
    return g


def build_hook_plate():
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ov = Image.alpha_composite(ov, _grad(0.40))
    d = ImageDraw.Draw(ov)
    base = H * 0.60
    f_tag = _font(SANS, 40)
    tracked(d, W / 2, base, TAGLINE.upper(), f_tag, (247, 205, 138, 255), 7,
            stroke_w=2, stroke_fill=(0, 0, 0, 220))
    f_name = _font(SERIF_BOLD, 116)
    name = ARTIST.upper()
    tracked(d, W / 2, base + H * 0.035, name, f_name, (255, 255, 255, 255), 3,
            stroke_w=3, stroke_fill=(0, 0, 0, 235))
    # thin gold rule
    rw = W * 0.20
    d.line([(W / 2 - rw / 2, base + H * 0.170), (W / 2 + rw / 2, base + H * 0.170)],
           fill=(218, 198, 168, 230), width=3)
    f_d = _font(SERIF_R, 46)
    tracked(d, W / 2, base + H * 0.192, DATES, f_d, (228, 218, 196, 255), 4,
            stroke_w=2, stroke_fill=(0, 0, 0, 210))
    return np.array(ov)


def build_end_plate():
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # darker plate for the end card
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    for y in range(0, H):
        a = int(150 * (1 - abs(y - H * 0.5) / (H * 0.6)) ** 1.0) if abs(y - H * 0.5) < H * 0.6 else 0
        gd.line([(0, y), (W, y)], fill=(0, 0, 0, max(0, a)))
    ov = Image.alpha_composite(ov, g)
    d = ImageDraw.Draw(ov)
    f_name = _font(SERIF_BOLD, 96)
    tracked(d, W / 2, H * 0.40, ARTIST.upper(), f_name, (255, 255, 255, 255), 3,
            stroke_w=3, stroke_fill=(0, 0, 0, 235))
    f_d = _font(SERIF_R, 44)
    tracked(d, W / 2, H * 0.475, DATES, f_d, (230, 220, 198, 255), 4,
            stroke_w=2, stroke_fill=(0, 0, 0, 210))
    rw = W * 0.18
    d.line([(W / 2 - rw / 2, H * 0.545), (W / 2 + rw / 2, H * 0.545)],
           fill=(218, 198, 168, 230), width=3)
    f_cta = _font(SANS_BOLD, 40)
    tracked(d, W / 2, H * 0.575, CTA, f_cta, (247, 205, 138, 255), 6,
            stroke_w=2, stroke_fill=(0, 0, 0, 220))
    return np.array(ov)


# ---------------------------------------------------------------- colour grade
def _vignette():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    return np.clip(1 - 0.30 * np.clip((r - 0.55) / 0.75, 0, 1), 0, 1)[..., None].astype(np.float32)


VIGNETTE = _vignette()


def grade(frame):
    """frame float32 0..255 -> cinematic graded float32 0..255."""
    x = frame / 255.0
    x = np.clip((x - 0.5) * 1.13 + 0.5, 0, 1)                      # contrast S-ish
    luma = (0.2126 * x[..., 0] + 0.7152 * x[..., 1] + 0.0722 * x[..., 2])
    x = np.clip(luma[..., None] + (x - luma[..., None]) * 1.15, 0, 1)  # saturation
    l = luma[..., None] - 0.5
    x[..., 0] = np.clip(x[..., 0] + 0.05 * l[..., 0], 0, 1)        # warm highlights
    x[..., 2] = np.clip(x[..., 2] - 0.05 * l[..., 0], 0, 1)        # cool shadows
    out = x * 255.0 * VIGNETTE
    out += np.random.normal(0, 2.6, (H, W, 1)).astype(np.float32)  # film grain
    return out


def blend_overlay(frame, ov_rgba, alpha, dy=0):
    if alpha <= 0:
        return frame
    o = ov_rgba
    if dy:
        o = np.roll(o, dy, axis=0)
    a = (o[..., 3:4].astype(np.float32) / 255.0) * alpha
    return frame * (1 - a) + o[..., :3].astype(np.float32) * a


def main():
    beats = load_beats(MUSIC)
    print(f"beats: {len(beats)}, first={beats[0]:.2f} last={beats[-1]:.2f}")

    # dreamy cinematic track ~112 BPM -> cut every 4 beats (~2.1s per artwork)
    cuts = beats[::4]
    cuts = cuts[next((i for i, b in enumerate(cuts) if b > 3.0), 0):]

    seg_count = 14
    seg_cuts = list(cuts[:seg_count + 1])
    if len(seg_cuts) < seg_count + 1:
        interval = (cuts[-1] - cuts[-2]) if len(cuts) > 1 else 1.0
        while len(seg_cuts) < seg_count + 1:
            seg_cuts.append(seg_cuts[-1] + interval)
    seg_starts, seg_ends = seg_cuts[:-1], seg_cuts[1:]
    total_dur = float(seg_ends[-1])
    print(f"segments: {seg_count}, total {total_dur:.1f}s")

    seg_work = [0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 11]
    HOOK = (0, 1)
    OUTRO = (12, 13)

    t0 = float(seg_starts[0])
    video_dur = total_dur - t0

    arts = [load_art(IMG_DIR / fn) for fn, _ in WORKS]
    for (fn, _), a in zip(WORKS, arts):
        print(f"loaded {fn}: {a.shape[1]}x{a.shape[0]}")

    hook_ov = build_hook_plate()
    end_ov = build_end_plate()
    black_fade = 1.2

    # hook cover
    cov = camera_crop(arts[0], 1.06, 0.5, 0.5).astype(np.float32)
    cov = grade(cov)
    cov = blend_overlay(cov, hook_ov, 1.0)
    Image.fromarray(np.clip(cov, 0, 255).astype(np.uint8)).save(str(OUT / "COPERTINA.jpg"), quality=95)
    print("cover saved")

    raw = OUT / "raw.mp4"
    ff = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
        "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(raw)],
        stdin=subprocess.PIPE)

    total_frames = int(math.ceil(video_dur * FPS))
    print(f"rendering {total_frames} frames ({video_dur:.1f}s)")

    for seg_i, (s_start, s_end) in enumerate(zip(seg_starts, seg_ends)):
        widx = seg_work[seg_i]
        art = arts[widx]
        spec = (LAND if art.shape[1] / art.shape[0] >= W / H else PORT)[seg_i]
        f0, f1 = int(s_start * FPS), int(s_end * FPS)
        for f in range(f0, f1):
            p = smooth(min(1.0, max(0.0, (f - f0) / max(1, f1 - f0))))
            z = spec["z0"] + (spec["z1"] - spec["z0"]) * p
            cxf = spec["cx0"] + (spec["cx1"] - spec["cx0"]) * p
            cyf = spec["cy0"] + (spec["cy1"] - spec["cy0"]) * p
            t_abs = f / FPS

            # beat pulse: micro zoom + brightness that decays after each beat
            bi = int(np.searchsorted(beats, t_abs)) - 1
            pulse = 0.0
            if bi >= 0:
                dt = t_abs - beats[bi]
                if 0 <= dt < 1.0:
                    pulse = 0.013 * math.exp(-dt / 0.13)
            z *= (1 + pulse)

            frame = camera_crop(art, z, cxf, cyf).astype(np.float32)
            frame = grade(frame)
            frame *= (1 + 0.5 * pulse)

            # cut impact flash (soft)
            dtc = t_abs - s_start
            if 0 <= dtc < 0.35:
                frame += 26 * math.exp(-dtc / 0.10)

            tv = t_abs - t0
            # kinetic text
            if seg_i in HOOK:
                a_in = min(1.0, max(0.0, tv / 0.5))
                a_out = min(1.0, max(0.0, (seg_ends[1] - t0 - tv) / 0.5))
                alpha = max(0.0, min(a_in, a_out))
                dy = int(24 * (1 - smooth(a_in)))
                frame = blend_overlay(frame, hook_ov, alpha, dy)
            elif seg_i in OUTRO:
                alpha = min(1.0, max(0.0, (tv - (seg_starts[12] - t0)) / 0.6))
                frame = blend_overlay(frame, end_ov, alpha)

            # loop-friendly opening/closing fades
            k = 1.0
            if tv < 0.4:
                k = min(k, max(0.0, tv / 0.4))
            if tv > video_dur - black_fade:
                k = min(k, max(0.0, (video_dur - tv) / black_fade))
            if k < 1.0:
                frame = frame * k

            ff.stdin.write(np.clip(frame, 0, 255).astype(np.uint8).tobytes())
        print(f"  seg {seg_i+1}/{seg_count} ({s_start:.1f}-{s_end:.1f}s) z={spec['z0']:.2f}->{spec['z1']:.2f}")

    ff.stdin.close()
    ff.wait()
    print(f"raw video written: {raw}")

    music_seg = OUT / "music_seg.m4a"
    af = f"afade=t=in:st=0:d=0.7,afade=t=out:st={max(0.0, video_dur - black_fade):.2f}:d={black_fade:.2f}"
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-ss", f"{t0:.3f}", "-i", str(MUSIC),
                    "-t", f"{video_dur:.3f}", "-map", "0:a:0", "-vn", "-af", af,
                    "-c:a", "aac", "-b:a", "192k",
                    str(music_seg)], check=True)

    master = OUT / "REEL_VANGOGH_V2.mp4"
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-i", str(raw), "-i", str(music_seg),
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "copy",
                    str(master)], check=True)
    raw.unlink(missing_ok=True)
    music_seg.unlink(missing_ok=True)
    print(f"MASTER: {master}")

    (OUT / "DIRITTI_E_FONTI.txt").write_text(
        f"Artista: {ARTIST} ({DATES}, {COUNTRY})\n"
        f"Musica: Dreamy Flashback - Kevin MacLeod (CC BY 4.0)\n"
        f"Opere: Wikimedia Commons (pubblico dominio)\n"
        f"Formato: reel social verticale full-bleed 1080x1920, {video_dur:.0f}s, inglese\n",
        encoding="utf-8")
    print("done")


if __name__ == "__main__":
    main()
