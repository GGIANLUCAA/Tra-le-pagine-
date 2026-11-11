#!/usr/bin/env python3
"""Safe CLI asset selector for Android GitHub Actions.

Accepted:
* a direct image under episodes/
* a scene_premium.zip under episodes/, selecting only scena_NN image.
Never extracts arbitrary archive paths or overwrites user sources.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import zipfile
from pathlib import Path


def prepare_asset(path_text: str, scene_number: int, output_dir: Path) -> Path:
    if not (1 <= scene_number <= 35):
        raise ValueError("scene_number deve essere 1..35")
    if not re.fullmatch(r"[A-Za-z0-9._/-]+", path_text):
        raise ValueError("Percorso consentito: lettere, numeri, punto, underscore, - e /")
    relative = Path(path_text)
    if relative.is_absolute() or ".." in relative.parts or len(relative.parts) < 3 or relative.parts[0] != "episodes":
        raise ValueError("File consentiti esclusivamente nella cartella episodes/")
    if not relative.is_file():
        raise ValueError(f"Immagine o archivio assente dal repository: {relative}")
    extensions = {".jpg", ".jpeg", ".png", ".webp"}
    if relative.suffix.lower() in extensions:
        if relative.stat().st_size > 12_000_000:
            raise ValueError("Immagine troppo grande")
        return relative
    if relative.name != "scene_premium.zip":
        raise ValueError("Archivio supportato: soltanto scene_premium.zip")
    with zipfile.ZipFile(relative) as z:
        choices = [entry for entry in z.infolist()
                   if not entry.is_dir()
                   and re.fullmatch(rf"scena_{scene_number:02}\.(jpg|jpeg|png|webp)",
                                    Path(entry.filename).name, re.IGNORECASE)]
        if len(choices) != 1:
            raise ValueError("Archivio: manca scena richiesta o nome ambiguo")
        entry = choices[0]
        if not 0 < entry.file_size <= 12_000_000:
            raise ValueError("Dimensioni immagine sospette")
        output_dir.mkdir(parents=True, exist_ok=True)
        output = output_dir / Path(entry.filename).name
        if output.exists():
            raise ValueError("File estratto gia presente: evitare sovrascrittura")
        with z.open(entry) as src, output.open("xb") as dst:
            import shutil
            shutil.copyfileobj(src, dst, length=1 << 20)
    return output


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True)
    ap.add_argument("--scene-number", type=int, default=1)
    ap.add_argument("--out-dir", type=Path, default=Path("output"))
    args = ap.parse_args()
    image = prepare_asset(args.input, args.scene_number, args.out_dir)
    print("IMMAGINE PRONTA:", image)
    env_path = os.getenv("GITHUB_ENV")
    if env_path:
        with open(env_path, "a", encoding="utf-8") as f:
            f.write(f"CLIP_IMAGE={image}\n")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, zipfile.BadZipFile) as exc:
        print("ERRORE INPUT V39:", exc, file=sys.stderr)
        raise SystemExit(2)
