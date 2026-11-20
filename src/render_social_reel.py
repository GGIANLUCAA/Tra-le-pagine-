"""Social reel renderer: one artist, many artworks, cut to the beat.
Vertical 1080x1920, music-synced, English text overlays, no voice.
"""
import json, math, os, subprocess
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30

ARTIST = "Vincent van Gogh"
COUNTRY = "Netherlands"
FLAG = "🇳🇱"
TAGLINE = "The Painter of Starry Skies"

# (filename, display_title)
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
    beats = peaks * hop / sr
    return beats


def cover_image(art, tagline, artist, country):
    """Social cover: artwork background + strong text overlay."""
    bg = _fit_cover(art)
    # dark vignette
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for i in range(60):
        a = int(120 * (i / 60) ** 1.5)
        d.rectangle([i, i, W - i, H - i], outline=(0, 0, 0, a))
    # gradient bottom
    grad = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    for y in range(H // 2, H):
        a = int(220 * ((y - H // 2) / (H // 2)) ** 1.2)
        gd.line([(0, y), (W, y)], fill=(0, 0, 0, a))
    bg = Image.alpha_composite(bg.convert("RGBA"), overlay)
    bg = Image.alpha_composite(bg, grad)
    d = ImageDraw.Draw(bg)
    # tagline (wrap to fit width)
    tag = tagline.upper()
    font_tag = _fit_font(tag, 600, 64, 38)
    font_art = _font(56)
    font_country = _font(42)
    tw = d.textlength(tag, font=font_tag)
    d.text(((W - tw) / 2, H * 0.52), tag, fill=(255, 240, 210, 255), font=font_tag,
           stroke_width=3, stroke_fill=(0, 0, 0, 255))
    # artist name
    aw = d.textlength(artist, font=font_art)
    d.text(((W - aw) / 2, H * 0.66), artist, fill=(255, 255, 255, 255), font=font_art,
           stroke_width=2, stroke_fill=(0, 0, 0, 255))
    # country
    cw = d.textlength(country, font=font_country)
    d.text(((W - cw) / 2, H * 0.74), country, fill=(220, 210, 190, 255), font=font_country,
           stroke_width=2, stroke_fill=(0, 0, 0, 255))
    return bg.convert("RGB")


def _fit_cover(art):
    """Fit artwork to full 1080x1920 cover (cover crop)."""
    ar = art.width / art.height
    tar = W / H
    if ar > tar:
        nh = H
        nw = int(nh * ar)
    else:
        nw = W
        nh = int(nw / ar)
    resized = art.resize((nw, nh), Image.LANCZOS)
    left = (nw - W) // 2
    top = (nh - H) // 2
    return resized.crop((left, top, left + W, top + H))


def _font(size):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def _fit_font(text, max_width, start_size, min_size):
    """Pick the largest font size where text fits max_width."""
    for size in range(start_size, min_size - 1, -2):
        f = _font(size)
        tmp = Image.new("RGB", (10, 10))
        d = ImageDraw.Draw(tmp)
        if d.textlength(text, font=f) <= max_width:
            return f
    return _font(min_size)


def frame_artwork(art, progress, zoom_dir, show_title, title):
    """One artwork frame: subtle Ken Burns zoom + optional title."""
    # zoom 1.0 -> 1.12 over the segment
    z = 1.0 + 0.12 * progress if zoom_dir == "in" else 1.12 - 0.12 * progress
    ar = art.width / art.height
    # fit into frame preserving aspect, centered, with margin
    margin = 60
    avail_w = W - 2 * margin
    avail_h = H - 2 * margin
    tar = avail_w / avail_h
    if ar > tar:
        pw = int(avail_w * z)
        ph = int(pw / ar)
    else:
        ph = int(avail_h * z)
        pw = int(ph * ar)
    resized = art.resize((pw, ph), Image.LANCZOS)
    # background: blurred dark version of artwork
    bg = art.resize((W, H), Image.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(40))
    bg = bg.point(lambda p: int(p * 0.35))
    canvas = bg.copy()
    x = (W - pw) // 2
    y = (H - ph) // 2
    canvas.paste(resized, (x, y))
    # subtle border
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([x - 4, y - 4, x + pw + 4, y + ph + 4], outline=(218, 198, 168), width=3)
    if show_title:
        font = _font(52)
        tw = draw.textlength(title, font=font)
        tx = (W - tw) / 2
        ty = H - 200
        # backdrop pill
        pad_x, pad_y = 36, 16
        draw.rounded_rectangle([tx - pad_x, ty - pad_y, tx + tw + pad_x, ty + 52 + pad_y],
                               radius=30, fill=(0, 0, 0, 180))
        draw.text((tx, ty), title, fill=(255, 245, 225), font=font)
    return canvas


# need PIL ImageFilter
from PIL import ImageFilter


def main():
    beats = load_beats(MUSIC)
    print(f"beats: {len(beats)}, first={beats[0]:.2f} last={beats[-1]:.2f}")
    # real tempo ~92 BPM, detected at 184 (eighth). Cut every 8 detected beats = 2 measures.
    cuts = beats[::8]
    # choose a clean segment: start a bit into the song (skip soft intro)
    # find first beat after 4s
    start_idx = 0
    for i, b in enumerate(cuts):
        if b > 3.0:
            start_idx = i
            break
    cuts = cuts[start_idx:]
    # we need 12 segments. Each segment = interval between 2 cuts.
    # Use 12 segments: 2 for hook, 10 for middle, but we have 12 works.
    # Plan: work 0 = hook (2 segments), works 1-10 = 1 segment each, work 11 = outro (2 segments)
    # That's 2 + 10 + 2 = 14 segments.
    seg_count = 14
    seg_cuts = cuts[:seg_count + 1]
    if len(seg_cuts) < seg_count + 1:
        # pad with last interval
        interval = cuts[-1] - cuts[-2] if len(cuts) > 1 else 0.65
        while len(seg_cuts) < seg_count + 1:
            seg_cuts = np.append(seg_cuts, seg_cuts[-1] + interval)
    seg_starts = seg_cuts[:-1]
    seg_ends = seg_cuts[1:]
    total_dur = float(seg_ends[-1])
    print(f"segments: {seg_count}, total {total_dur:.1f}s")

    # artwork index per segment
    # hook: work 0 for segs 0,1
    # segs 2..11: works 1..10
    # outro: work 11 for segs 12,13  (but we have 12 works, indices 0..11)
    # Actually: seg 0,1 -> work 0 (Starry Night, hook)
    # seg 2 -> work 1, seg 3 -> work 2, ... seg 11 -> work 10
    # seg 12,13 -> work 11 (Wheatfield with Crows, outro)
    seg_work = [0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 11]

    arts = []
    for fn, _ in WORKS:
        im = Image.open(IMG_DIR / fn).convert("RGB")
        arts.append(im)
        print(f"loaded {fn}: {im.size}")

    # cover = first frame (hook with text)
    cov = cover_image(arts[0], TAGLINE, ARTIST, COUNTRY)
    cov.save(str(OUT / "COPERTINA.jpg"), quality=95)
    print("cover saved")

    # build video
    raw = OUT / "raw.mp4"
    ff = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS),
        "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(raw)],
        stdin=subprocess.PIPE)

    total_frames = int(math.ceil(total_dur * FPS))
    print(f"rendering {total_frames} frames ({total_dur:.1f}s)")

    for seg_i, (s_start, s_end) in enumerate(zip(seg_starts, seg_ends)):
        widx = seg_work[seg_i]
        art = arts[widx]
        title = WORKS[widx][1]
        f0 = int(s_start * FPS)
        f1 = int(s_end * FPS)
        # hook (0,1) and outro (12,13) have their own big text overlays
        show_title = seg_i not in (0, 1, 12, 13)
        zoom_dir = "in" if widx % 2 == 0 else "out"
        for f in range(f0, f1):
            p = (f - f0) / max(1, f1 - f0)
            # slight ease
            pe = p * p * (3 - 2 * p)
            show = seg_i not in (0, 1)  # hook has cover text instead
            frame = frame_artwork(art, pe, zoom_dir, show, title)
            # for hook segments, overlay tagline text
            if seg_i in (0, 1):
                ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                od = ImageDraw.Draw(ov)
                # fade in first 0.5s, out last 0.5s of hook
                hook_fade = 1.0
                if f < f0 + int(0.5 * FPS):
                    hook_fade = (f - f0) / (0.5 * FPS)
                elif f > f1 - int(0.5 * FPS):
                    hook_fade = (f1 - f) / (0.5 * FPS)
                a = int(255 * max(0, min(1, hook_fade)))
                tag = TAGLINE.upper()
                font_tag = _fit_font(tag, 600, 64, 38)
                font_art = _font(50)
                tw = od.textlength(tag, font=font_tag)
                od.text(((W - tw) / 2, H * 0.62), tag, fill=(255, 240, 210, a), font=font_tag,
                        stroke_width=3, stroke_fill=(0, 0, 0, a))
                aw = od.textlength(ARTIST, font=font_art)
                od.text(((W - aw) / 2, H * 0.75), ARTIST, fill=(255, 255, 255, a), font=font_art,
                        stroke_width=2, stroke_fill=(0, 0, 0, a))
                frame = Image.alpha_composite(frame.convert("RGBA"), ov).convert("RGB")
            # outro text
            if seg_i in (12, 13):
                ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                od = ImageDraw.Draw(ov)
                out_fade = 1.0
                if f > f1 - int(0.8 * FPS):
                    out_fade = (f1 - f) / (0.8 * FPS)
                a = int(255 * max(0, min(1, out_fade)))
                tag = TAGLINE.upper()
                font_tag = _fit_font(tag, 600, 60, 36)
                font_art = _font(52)
                font_country = _font(40)
                tw = od.textlength(tag, font=font_tag)
                od.text(((W - tw) / 2, H * 0.58), tag, fill=(255, 240, 210, a), font=font_tag,
                        stroke_width=3, stroke_fill=(0, 0, 0, a))
                aw = od.textlength(ARTIST, font=font_art)
                od.text(((W - aw) / 2, H * 0.70), ARTIST, fill=(255, 255, 255, a), font=font_art,
                        stroke_width=2, stroke_fill=(0, 0, 0, a))
                cw = od.textlength(COUNTRY, font=font_country)
                od.text(((W - cw) / 2, H * 0.78), COUNTRY, fill=(220, 210, 190, a), font=font_country,
                        stroke_width=2, stroke_fill=(0, 0, 0, a))
                frame = Image.alpha_composite(frame.convert("RGBA"), ov).convert("RGB")
            bgr = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
            ff.stdin.write(bgr.tobytes())
        print(f"  seg {seg_i+1}/{seg_count} ({s_start:.1f}-{s_end:.1f}s) work={title}")

    ff.stdin.close()
    ff.wait()
    print(f"raw video written: {raw}")

    # trim music to exactly the segment we used
    music_seg = OUT / "music_seg.m4a"
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-ss", str(float(seg_starts[0])), "-i", str(MUSIC),
                    "-t", str(total_dur), "-c:a", "aac", "-b:a", "192k",
                    str(music_seg)], check=True)

    # mux video + trimmed music
    master = OUT / "REEL_VANGOGH_STARRY_SKIES.mp4"
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-i", str(raw), "-i", str(music_seg),
                    "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "copy",
                    "-shortest", str(master)], check=True)
    raw.unlink(missing_ok=True)
    music_seg.unlink(missing_ok=True)
    print(f"MASTER: {master}")

    # rights
    (OUT / "DIRITTI_E_FONTI.txt").write_text(
        f"Artista: {ARTIST} ({COUNTRY})\n"
        f"Musica: Carefree - Kevin MacLeod (CC BY 4.0)\n"
        f"Opere: Wikimedia Commons (pubblico dominio)\n"
        f"Formato: reel social verticale 1080x1920, {total_dur:.0f}s, inglese\n",
        encoding="utf-8")
    print("done")


if __name__ == "__main__":
    main()
