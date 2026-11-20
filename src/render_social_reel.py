"""Social reel renderer: one artist, many artworks, cut to the beat.
Vertical 1080x1920 full-bleed, dynamic camera (push / pan / tilt / diagonal),
music-synced hard cuts, minimal English text (name + dates), no voice.
Proper ending: fade to black + audio fade-out.
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

# (filename, display_title — title kept for rights/summary only)
WORKS = [
    ("Starry_Night.jpg", "Starry Night"),
    ("Sunflowers.jpg", "Sunflowers"),
    ("The_Sower.jpg", "The Sower"),
    ("Irises.jpg", "Irises"),
    ("Almond_Blossoms.jpg", "Almond Blossoms"),
    ("Wheatfield_Cypresses.jpg", "Wheatfield with Cypresses"),
    ("Cafe_Terras.jpg", "Café Terrace at Night"),
    ("Bedroom_Arles.jpg", "Bedroom in Arles"),
    ("Yellow_House.jpg", "The Yellow House"),
    ("Potato_Eaters.jpg", "The Potato Eaters"),
    ("Self_Portrait.jpg", "Self-Portrait"),
    ("Wheatfield_Crows.jpg", "Wheatfield with Crows"),
]

IMG_DIR = Path("/tmp/vangogh")
MUSIC = Path("/tmp/carefree.mp3")
OUT = Path("/workspace/output/social_vangogh")
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- motion plans
def _m(z0, z1, cx0, cx1, cy0, cy1):
    return dict(z0=z0, z1=z1, cx0=cx0, cx1=cx1, cy0=cy0, cy1=cy1)

# Landscape artworks: push / horizontal pan / diagonal
LAND = [
    _m(1.00, 1.28, .50, .50, .50, .50),   # push in
    _m(1.20, 1.20, .00, 1.0, .50, .50),   # pan right
    _m(1.20, 1.20, 1.0, .00, .50, .50),   # pan left
    _m(1.28, 1.02, .50, .50, .50, .50),   # push out
    _m(1.12, 1.30, .00, 1.0, .30, .70),   # diagonal lr
    _m(1.06, 1.30, .15, .50, .50, .50),   # push in from left
    _m(1.20, 1.20, .00, 1.0, .50, .50),   # pan right
    _m(1.30, 1.04, .50, .50, .58, .45),   # push out low
    _m(1.30, 1.12, 1.0, .00, .70, .30),   # diagonal rl
    _m(1.20, 1.20, 1.0, .00, .50, .50),   # pan left
    _m(1.00, 1.30, .50, .50, .50, .50),   # push in strong
    _m(1.26, 1.06, .55, .45, .50, .50),   # pull back
    _m(1.20, 1.20, .00, 1.0, .55, .45),   # pan right slight tilt
    _m(1.04, 1.22, .50, .50, .50, .50),   # slow push
]

# Portrait artworks: push / vertical tilt / diagonal
PORT = [
    _m(1.00, 1.28, .50, .50, .50, .50),   # push in
    _m(1.20, 1.20, .50, .50, .00, 1.0),   # tilt down
    _m(1.20, 1.20, .50, .50, 1.0, .00),   # tilt up
    _m(1.28, 1.02, .50, .50, .50, .50),   # push out
    _m(1.12, 1.30, .50, .50, .00, 1.0),   # diagonal top->bottom
    _m(1.06, 1.30, .50, .50, .15, .50),   # push in from top
    _m(1.20, 1.20, .50, .50, .00, 1.0),   # tilt down
    _m(1.30, 1.04, .50, .50, .42, .55),   # push out upper
    _m(1.30, 1.12, .50, .50, 1.0, .00),   # diagonal bottom->top
    _m(1.20, 1.20, .50, .50, 1.0, .00),   # tilt up
    _m(1.00, 1.30, .50, .50, .50, .50),   # push in strong
    _m(1.26, 1.06, .42, .52, .50, .50),   # pull back
    _m(1.20, 1.20, .55, .45, .00, 1.0),   # tilt down slight
    _m(1.04, 1.22, .50, .50, .50, .50),   # slow push
]


def smooth(x):
    return x * x * (3 - 2 * x)


def load_beats(audio_path):
    """Detect beats via spectral flux, return beat times in seconds."""
    wav = "/tmp/_reel_audio.wav"
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
    min_dist = int(0.3 * sr / hop)
    peaks, _ = find_peaks(flux, distance=min_dist, prominence=0.04)
    return peaks * hop / sr


def _font(size, bold=False):
    cand = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
            else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    for p in cand:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def _fit_font(text, max_width, start_size, min_size, bold=False):
    tmp = Image.new("RGB", (10, 10))
    d = ImageDraw.Draw(tmp)
    for size in range(start_size, min_size - 1, -2):
        f = _font(size, bold)
        if d.textlength(text, font=f) <= max_width:
            return f
    return _font(min_size, bold)


def load_art(path):
    """Load artwork, downscale large sources for fast per-frame crops."""
    im = Image.open(path).convert("RGB")
    if max(im.size) > 2600:
        s = 2600 / max(im.size)
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    return np.array(im)


def camera_crop(arr, z, cxf, cyf):
    """Full-bleed camera: crop a moving/zooming window and resize to WxH."""
    ah, aw = arr.shape[:2]
    fr = W / H
    ar = aw / ah
    if ar >= fr:                      # wide art -> cover by full height
        ch0 = ah; cw0 = ah * fr
    else:                             # tall art -> cover by full width
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


def build_overlay(tagline, name, dates, text_base=0.63):
    """Text plate (RGBA): tagline + big name + dates over a bottom gradient."""
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    grad = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    top = int(H * 0.40)
    for y in range(top, H):
        a = int(215 * ((y - top) / (H - top)) ** 1.15)
        gd.line([(0, y), (W, y)], fill=(0, 0, 0, a))
    ov = Image.alpha_composite(ov, grad)
    d = ImageDraw.Draw(ov)
    base = H * text_base
    f_tag = _fit_font(tagline.upper(), 840, 46, 30)
    tw = d.textlength(tagline.upper(), font=f_tag)
    d.text(((W - tw) / 2, base), tagline.upper(), font=f_tag,
           fill=(255, 214, 150, 255), stroke_width=2, stroke_fill=(0, 0, 0, 220))
    f_name = _fit_font(name.upper(), 960, 110, 54, bold=True)
    nw = d.textlength(name.upper(), font=f_name)
    d.text(((W - nw) / 2, base + H * 0.055), name.upper(), font=f_name,
           fill=(255, 255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0, 235))
    f_d = _font(46)
    dw = d.textlength(dates, font=f_d)
    d.text(((W - dw) / 2, base + H * 0.155), dates, font=f_d,
           fill=(228, 218, 196, 255), stroke_width=2, stroke_fill=(0, 0, 0, 220))
    return np.array(ov)


def main():
    beats = load_beats(MUSIC)
    print(f"beats: {len(beats)}, first={beats[0]:.2f} last={beats[-1]:.2f}")

    # detected ~184 (eighths) -> cut every 8 = ~2.5s per artwork
    cuts = beats[::8]
    start_idx = next((i for i, b in enumerate(cuts) if b > 3.0), 0)
    cuts = cuts[start_idx:]

    seg_count = 14                      # 2 hook + 10 middle + 2 outro
    seg_cuts = list(cuts[:seg_count + 1])
    if len(seg_cuts) < seg_count + 1:
        interval = (cuts[-1] - cuts[-2]) if len(cuts) > 1 else 0.65
        while len(seg_cuts) < seg_count + 1:
            seg_cuts.append(seg_cuts[-1] + interval)
    seg_starts = seg_cuts[:-1]
    seg_ends = seg_cuts[1:]
    total_dur = float(seg_ends[-1])
    print(f"segments: {seg_count}, total {total_dur:.1f}s")

    seg_work = [0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 11]
    HOOK = (0, 1)
    OUTRO = (12, 13)

    t0 = float(seg_starts[0])           # first frame's position in the song
    video_dur = total_dur - t0

    arts = [load_art(IMG_DIR / fn) for fn, _ in WORKS]
    for (fn, _), a in zip(WORKS, arts):
        print(f"loaded {fn}: {a.shape[1]}x{a.shape[0]}")

    overlay = build_overlay(TAGLINE, ARTIST, DATES)
    black_fade = 1.3                    # seconds of fade to black at the very end

    # ---- cover image (hook composition on artwork 0) ------------------------
    cov = camera_crop(arts[0], 1.06, 0.5, 0.5)
    a = (overlay[..., 3:4].astype(np.float32) / 255.0)
    cov = (cov.astype(np.float32) * (1 - a) + overlay[..., :3].astype(np.float32) * a).astype(np.uint8)
    Image.fromarray(cov).save(str(OUT / "COPERTINA.jpg"), quality=95)
    print("cover saved")

    # ---- render frames ------------------------------------------------------
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
        ar = art.shape[1] / art.shape[0]
        spec = (LAND if ar >= W / H else PORT)[seg_i]
        f0, f1 = int(s_start * FPS), int(s_end * FPS)
        for f in range(f0, f1):
            p = smooth(min(1.0, max(0.0, (f - f0) / max(1, f1 - f0))))
            z = spec["z0"] + (spec["z1"] - spec["z0"]) * p
            cxf = spec["cx0"] + (spec["cx1"] - spec["cx0"]) * p
            cyf = spec["cy0"] + (spec["cy1"] - spec["cy0"]) * p
            frame = camera_crop(art, z, cxf, cyf).astype(np.float32)

            tv = f / FPS - t0                # video-relative time
            # text overlay on hook + outro with fades
            alpha = 0.0
            if seg_i in HOOK:
                alpha = max(0.0, min(1.0, tv / 0.6, (seg_ends[1] - t0 - tv) / 0.6))
            elif seg_i in OUTRO:
                alpha = max(0.0, min(1.0, (tv - (seg_starts[12] - t0)) / 0.6))
            if alpha > 0:
                a4 = (overlay[..., 3:4].astype(np.float32) / 255.0) * alpha
                frame = frame * (1 - a4) + overlay[..., :3].astype(np.float32) * a4

            # fade in from black at very start, fade to black at very end
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

    # ---- audio: same musical segment + fade in/out --------------------------
    music_seg = OUT / "music_seg.m4a"
    af = f"afade=t=in:st=0:d=0.7,afade=t=out:st={max(0.0, video_dur - black_fade):.2f}:d={black_fade:.2f}"
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-ss", f"{t0:.3f}", "-i", str(MUSIC),
                    "-t", f"{video_dur:.3f}", "-af", af, "-c:a", "aac", "-b:a", "192k",
                    str(music_seg)], check=True)

    # ---- mux ----------------------------------------------------------------
    master = OUT / "REEL_VANGOGH_STARRY_SKIES.mp4"
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-i", str(raw), "-i", str(music_seg),
                    "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "copy",
                    str(master)], check=True)
    raw.unlink(missing_ok=True)
    music_seg.unlink(missing_ok=True)
    print(f"MASTER: {master}")

    (OUT / "DIRITTI_E_FONTI.txt").write_text(
        f"Artista: {ARTIST} ({DATES}, {COUNTRY})\n"
        f"Musica: Carefree - Kevin MacLeod (CC BY 4.0)\n"
        f"Opere: Wikimedia Commons (pubblico dominio)\n"
        f"Formato: reel social verticale full-bleed 1080x1920, {video_dur:.0f}s, inglese\n",
        encoding="utf-8")
    print("done")


if __name__ == "__main__":
    main()
