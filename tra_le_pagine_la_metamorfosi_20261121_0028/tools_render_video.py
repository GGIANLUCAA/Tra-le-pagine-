#!/usr/bin/env python3
"""Tra le Pagine - montaggio e render MP4 verticale (La metamorfosi).
Ken Burns vario, transizioni differenti con compensazione dei tempi a frame
interi, sottotitoli .ass burn-in (allineati a Whisper), musica discreta."""
import json, os, subprocess, shutil

D = "/workspace/tra_le_pagine_la_metamorfosi_20261121_0028"
FPS = 30
W, H = 1080, 1920
BRAND_DUR = 4.0
OUT_MP4 = "/workspace/tra_le_pagine_la_metamorfosi_20261121_0028.mp4"
TMP = "/tmp/tlp_render"

SC_1080 = f"{D}/scene_1080"
ILL = f"{D}/illustrazioni"

timing = json.load(open(f"{D}/audio/timing.json", encoding="utf-8"))
cues = json.load(open(f"{D}/scene_cues.json", encoding="utf-8"))
by_scene = {c["scene"]: c for c in cues}
audio_end = timing["audio_end"]
shots = timing["scene_times"]

os.makedirs(TMP, exist_ok=True)


def resolve(asset, src=None):
    a = src or asset
    if a == "brand_card":
        return f"{D}/brand_card.png"
    for base in (SC_1080, ILL, D):
        p = f"{base}/{a}.png"
        if os.path.exists(p):
            return p
        pj = f"{base}/{a}.jpg"
        if os.path.exists(pj):
            return pj
    raise SystemExit(f"immagine non trovata per asset: {a}")


files, moves = [], []
for s in shots:
    c = by_scene.get(s["scene"], {})
    files.append(resolve(s["asset"], c.get("src")))
    moves.append(c.get("move", "in"))
N = len(files)  # 23 (l'ultima e' la card di brand, gia' in scene_times)
assert files[-1].endswith("brand_card.png"), "l'ultima inquadratura deve essere la card di brand"
starts = [s["start"] for s in shots] + [audio_end]  # starts[i] = T_{i+1}

# ---- transizioni tra inquadrature (diverse, non uguali ovunque) ----
trans = {k: ("fade", 0.12) for k in range(1, N)}  # default: taglio pulito
trans[1] = ("fade", 0.50)        # gancio -> titolo
trans[4] = ("dissolve", 0.55)    # famiglia -> violino
trans[10] = ("fade", 0.55)       # ferita -> perdita di tutto
trans[14] = ("dissolve", 0.60)   # ritratto / memoria
trans[18] = ("fade", 0.50)       # condanna di Grete
trans[19] = ("fadeblack", 0.70)  # morte
trans[21] = ("dissolve", 0.60)   # chiusura -> riflessione
trans[22] = ("fadewhite", 0.60)  # -> brand card

DkF = {k: max(int(round(trans[k][1] * FPS)), 2) for k in range(1, N)}
C = {k: int(round(starts[k] * FPS)) for k in range(0, N)}  # C[k] = frame di T_{k+1}
E, G = {0: 0}, {}
for k in range(1, N):
    E[k] = C[k] + DkF[k] // 2
for k in range(1, N):
    G[k] = E[k] - E[k - 1] + (DkF[k - 1] if k - 1 >= 1 else 0)
G[N] = int(round(BRAND_DUR * FPS))
off = {k: E[k] - DkF[k] for k in range(1, N)}
total_frames = sum(G[k] for k in range(1, N + 1)) - sum(DkF[k] for k in range(1, N))
total = total_frames / FPS
print(f"shots={N}  durata_video={total:.2f}s  audio_end={audio_end:.2f}s")
assert all(G[k] > DkF.get(k, 0) for k in range(1, N)), "segmento piu corto della transizione"
assert all(G[k] > DkF.get(k - 1, 0) for k in range(1, N + 1)), "clipping transizione"


def zexpr(move, F):
    p = f"on/{max(F-1,1)}"
    return {
        "in":    f"z='1.03+0.09*{p}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2'",
        "out":   f"z='1.12-0.09*{p}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2'",
        "left":  f"z='1.08':x='(iw-iw/zoom)*(1-{p})':y='(ih-ih/zoom)/2'",
        "right": f"z='1.08':x='(iw-iw/zoom)*({p})':y='(ih-ih/zoom)/2'",
        "up":    f"z='1.08':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)*(1-{p})'",
        "down":  f"z='1.08':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)*({p})'",
    }.get(move, "z='1.0':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2'")


for k in range(1, N + 1):
    F = G[k]
    vf = (f"scale={W*2}:{H*2}:flags=lanczos,setsar=1,"
          f"zoompan={zexpr(moves[k-1], F)}:d={F}:s={W}x{H}:fps={FPS}")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", files[k - 1],
                    "-vf", vf, "-frames:v", str(F), "-r", str(FPS),
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
                    "-pix_fmt", "yuv420p", f"{TMP}/seg_{k:02d}.mp4"], check=True)
    print(f"seg {k:02d} {os.path.basename(files[k-1])} {F}fr {moves[k-1]}")

inputs = []
for k in range(1, N + 1):
    inputs += ["-i", f"{TMP}/seg_{k:02d}.mp4"]
fc, prev = [], "[0:v]"
for k in range(1, N):
    t, _ = trans[k]
    fc.append(f"{prev}[{k}:v]xfade=transition={t}:duration={DkF[k]/FPS:.3f}"
              f":offset={off[k]/FPS:.3f}[x{k}]")
    prev = f"[x{k}]"
fc.append(f"{prev}ass=filename={D}/subtitles/sottotitoli.ass[vout]")
raw = f"{TMP}/video_raw.mp4"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs,
                "-filter_complex", ";".join(fc), "-map", "[vout]",
                "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                "-pix_fmt", "yuv420p", "-r", str(FPS), raw], check=True)
print("video_raw OK")

fout = max(total - 3.5, 0.1)
fc2 = (f"[1:a]aresample=48000,apad[nar];"
       f"[2:a]aresample=48000,volume=0.15,afade=t=in:st=0:d=1.5,"
       f"afade=t=out:st={fout:.2f}:d=3.5[mus];"
       f"[nar][mus]amix=inputs=2:duration=shortest:normalize=0[aout]")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw,
                "-i", f"{D}/audio/narrazione.wav", "-i", f"{D}/musica/bed.wav",
                "-filter_complex", fc2, "-map", "0:v", "-map", "[aout]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                "-shortest", "-movflags", "+faststart", OUT_MP4], check=True)
print("MP4:", OUT_MP4, "| durata", round(total, 2), "s")
shutil.rmtree(TMP, ignore_errors=True)
