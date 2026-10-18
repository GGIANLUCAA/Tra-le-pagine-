#!/usr/bin/env python3
"""Small offline test: use existing illustrated episode 01, never call any TTS/API."""
import json
import subprocess
import tempfile
import zipfile
from pathlib import Path

from PIL import Image
from effetti_v4 import render_montage, pick_settings


def ffprobe(path):
    r=subprocess.run([
        "ffprobe","-v","error","-show_entries",
        "format=duration:stream=codec_type,width,height,nb_frames",
        "-of","json",str(path)],
        capture_output=True,text=True,check=True)
    return json.loads(r.stdout)


def main():
    out=Path("output_v4")
    out.mkdir(exist_ok=True)
    source=Path("episodes/01_scacchi/scene_premium.zip")
    if not source.is_file():
        raise RuntimeError("Il test richiede immagini premium EP01 esistenti")
    with tempfile.TemporaryDirectory() as td:
        work=Path(td)
        images=[]
        with zipfile.ZipFile(source) as z:
            for i in (1,2,3):
                name=f"scena_{i:02d}.jpg"
                matches=[m for m in z.namelist() if Path(m).name==name]
                if not matches:raise RuntimeError("Manca "+name)
                path=work/name
                path.write_bytes(z.read(matches[0]))
                Image.open(path).verify()
                images.append(path)
        settings={"scenes":[
            {"cue":0,"effect":"sketch_paint","seconds":1.5,"mood":"warm","postfx":"soft_bloom"},
            {"cue":1,"effect":"brush_reveal","seconds":1.4,"mood":"cool"},
            {"cue":2,"effect":"light_atmosphere","mood":"warm"}]}
        config=work/"direzione.json"
        config.write_text(json.dumps(settings),encoding="utf-8")
        if pick_settings(config,0,"",3)[0]!="sketch_paint":
            raise AssertionError("Preset non caricato")
        try:
            pick_settings(work/"missing.json",0,"",3)
            pick_settings(config,1,"",3)
        except Exception:
            raise AssertionError("Validazione preset non riuscita")
        montage=render_montage(images,8.5,work,
                    starts=[0.,3.3,5.9],config_path=config,
                    output_manifest=out/"REGIA_TEST.json",
                    fps=24,w=720,h=1280)
        result=out/"PROVINO_V4_SENZA_API.mp4"
        result.write_bytes(montage.read_bytes())
    info=ffprobe(result)
    duration=float(info["format"]["duration"])
    video=next((s for s in info["streams"] if s.get("codec_type")=="video"),None)
    assert 8.0 < duration < 9.3, f"Durata errata: {duration}"
    assert video and video["width"]==720 and video["height"]==1280
    assert result.stat().st_size>20000
    entries=json.loads((out/"REGIA_TEST.json").read_text())
    assert len(entries)==3
    assert entries[0]["reveal_sec"]>0
    assert entries[1]["reveal_sec"]>0
    assert entries[2]["effect"]=="light_atmosphere"
    assert entries[0]["postfx"]=="soft_bloom"
    assert entries[1]["postfx"] is None
    assert entries[2]["postfx"] is None
    print("PASS: V4 offline, 3 effetti, 8.5 s, video valido; ZERO API",flush=True)


if __name__=="__main__":
    main()
