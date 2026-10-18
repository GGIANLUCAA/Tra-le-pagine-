#!/usr/bin/env python3
"""Full-length OFFLINE V4+frei0r remix using an existing approved Gemini narration.

No generative model, API secret or new image credits required. Ensures the new
plugin-based look survives 2+ minutes, keeps captions/voice, and passes ffprobe.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

import soundfile as sf

from effetti_v4 import render_montage


def run(*args):
    subprocess.run([str(x) for x in args],check=True)


def probe(path):
    result=subprocess.run(["ffprobe","-v","error","-of","json",
                           "-show_entries","format=duration:stream=codec_type,width,height",
                           str(path)],capture_output=True,text=True,check=True)
    return json.loads(result.stdout)


def main():
    old=Path("output_precedente")
    out=Path("output_v4_integrale")
    out.mkdir(exist_ok=True)
    ep=Path("episodes/01_scacchi")
    for name in ("VOCE.wav","MUSICA_ORIGINALE.wav","captions.ass","SEQUENZA_SCENE.txt"):
        if not (old/name).is_file():
            raise FileNotFoundError(old/name)
    lines=(old/"SEQUENZA_SCENE.txt").read_text(encoding="utf-8").splitlines()
    scenes=[]
    for line in lines:
        match=re.search(r"([0-9.]+)s\s+.+\(immagine\s+(\d+)\)",line)
        if match:
            scenes.append((float(match.group(1)),int(match.group(2))))
    if len(scenes)<10:
        raise ValueError(f"Esportazione cue errata: solo {len(scenes)} scene")
    if scenes[0][0]!=0:
        raise ValueError("Primo cue non parte da zero")

    with tempfile.TemporaryDirectory() as tmpdir:
        work=Path(tmpdir)
        paths=[]
        with zipfile.ZipFile(ep/"scene_premium.zip") as archive:
            name_map={Path(m).name.lower():m for m in archive.namelist()}
            for idx,(start,num) in enumerate(scenes):
                fname=f"scena_{num:02}.jpg"
                if fname not in name_map:
                    raise ValueError(f"Immagine premium mancante: {fname}")
                p=work/f"clip_image_{idx:02d}.jpg"
                p.write_bytes(archive.read(name_map[fname]))
                paths.append(p)
        seconds=sf.info(str(old/"VOCE.wav")).duration
        montage=render_montage(paths,seconds,work,
             starts=[start for start,num in scenes],
             config_path=ep/"effetti_v4.json",
             output_manifest=out/"REGIA_V4_FREI0R.json",
             fps=24,w=720,h=1280)
        mp4=out/"COLLAUDO_INTEGRALE_V4_FREI0R_EP01.mp4"
        run("ffmpeg","-hide_banner","-loglevel","error","-y",
            "-i",montage,"-i",old/"VOCE.wav",
            "-i",old/"MUSICA_ORIGINALE.wav",
            "-filter_complex",
            "[1:a]volume=1.0[v];[2:a]volume=0.40[m];"
            "[v][m]amix=inputs=2:duration=first:normalize=0[a]",
            "-vf","ass="+str((old/"captions.ass").resolve()),
            "-map","0:v:0","-map","[a]",
            "-c:v","libx264","-preset","veryfast","-crf","23",
            "-pix_fmt","yuv420p","-c:a","aac","-b:a","160k",
            "-shortest","-movflags","+faststart",mp4)

    info=probe(mp4)
    length=float(info["format"]["duration"])
    video=next((s for s in info["streams"] if s["codec_type"]=="video"),None)
    audio=next((s for s in info["streams"] if s["codec_type"]=="audio"),None)
    if not (118<=length<=145 and video and audio):
        raise RuntimeError("Collaudo incompleto: durata/audio/video")
    if (video.get("width"),video.get("height"))!=(720,1280):
        raise RuntimeError("Formato video errato")
    fx=json.loads((out/"REGIA_V4_FREI0R.json").read_text(encoding="utf-8"))
    if not any(row["postfx"] for row in fx):
        raise RuntimeError("Nessun plugin frei0r applicato nel video")
    shutil.copy2(old/"SOTTOTITOLI.srt",out/"SOTTOTITOLI.srt")
    (out/"COLLAUDO_LEGGIMI.txt").write_text(
        "COLLAUDO V4+FREI0R, NON UN NUOVO EPISODIO.\n"
        "Stesso audio Gemini e immagini dell'episodio 01 approvato; nuovi effetti.\n"
        f"Durata: {length:.1f}s, scene: {len(fx)}, "
        f"effetti frei0r applicati: {sum(bool(row['postfx']) for row in fx)}.\n"
        "Voce e sottotitoli originali, nessuna API chiamata.\n"
        "Il risultato richiede ancora valutazione artistica dell'utente.\n",
        encoding="utf-8")
    print("PASS COLL. INTEGRALE:",mp4,length,"secondi, effetti V4+frei0r",
          flush=True)


if __name__=="__main__":
    main()
