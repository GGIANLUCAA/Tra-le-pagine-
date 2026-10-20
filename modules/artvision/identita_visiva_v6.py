#!/usr/bin/env python3
"""ArtVision Cinema V6 — identità grafica FISSA per ogni nuovo artista.

STILE BLOCCATO dalla coppia di film approvati (Van Gogh/Caravaggio, 20-10-2026).
Stessi caratteri, colore, fascia, linea, dimensioni di partenza, posizione e fade.
Cambiano SOLO nome artista, autore musica e immagine dell'opera.
Non sostituisce né modifica i file MP4 già approvati.
"""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
MAIN_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SECONDARY_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
MAIN_SIZE = 62
SECONDARY_SIZE = 21
# Coordinate e palette bloccate a 1080x1920 per coerenza dell'intera serie.
BAND = (56, H - 580, W - 56, H - 330)
BAND_RADIUS = 10
BAND_RGBA = (5, 8, 13, 190)
ARTIST_Y = H - 533
DIVIDER = (130, H - 425, W - 130, H - 425)
DIVIDER_RGBA = (218, 198, 168, 186)
MUSIC_Y = H - 399
ARTIST_RGBA = (255, 251, 243, 255)
MUSIC_RGBA = (218, 208, 192, 246)
TEXT_SIDE_MARGIN = 100
FADE_START = 2.9
FADE_DURATION = 0.55


@lru_cache(maxsize=32)
def _font(file: str, points: int):
    if not Path(file).is_file():
        raise FileNotFoundError("Font di progetto mancante: " + file)
    return ImageFont.truetype(file, points)


def _fitted(draw: ImageDraw.ImageDraw, label: str, face: str, size: int, allowed: int):
    """Riduci SOLO la dimensione se il nome è lungo; conserva sempre la famiglia tipografica."""
    points = size
    while points > 14:
        ft = _font(face, points)
        rect = draw.textbbox((0, 0), label, font=ft)
        if rect[2] - rect[0] <= allowed:
            return ft
        points -= 1
    raise ValueError("Etichetta troppo lunga per l'identità visiva ArtVision V6")


def signature(frame: np.ndarray, t: float, artist: str, composer: str,
              *, force_visible: bool = False) -> np.ndarray:
    """Ritorna frame BGR con apertura fissa. Per copertina usa force_visible=True."""
    if frame.shape[:2] != (H, W) or frame.dtype != np.uint8 or frame.shape[2] != 3:
        raise ValueError("La firma ArtVision richiede un frame 1080x1920 BGR uint8")
    alpha = 1.0 if force_visible else max(0.0, min(1.0, 1.0 - max(0.0, t - FADE_START) / FADE_DURATION))
    if alpha <= 0:
        return frame
    name = " ".join(artist.strip().upper().split())
    music = "MUSIC BY " + " ".join(composer.strip().upper().split())
    if not name or music == "MUSIC BY ":
        raise ValueError("Nome artista e compositore devono essere presenti")
    base = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.rounded_rectangle(BAND, radius=BAND_RADIUS,
                        fill=(*BAND_RGBA[:3], round(BAND_RGBA[3] * alpha)))
    name_font = _fitted(d, name, MAIN_FONT, MAIN_SIZE, W - 2 * TEXT_SIDE_MARGIN)
    name_w = d.textbbox((0, 0), name, font=name_font)[2]
    d.text(((W - name_w) / 2, ARTIST_Y), name, font=name_font,
           fill=(*ARTIST_RGBA[:3], round(ARTIST_RGBA[3] * alpha)))
    music_font = _fitted(d, music, SECONDARY_FONT, SECONDARY_SIZE, W - 2 * TEXT_SIDE_MARGIN)
    music_w = d.textbbox((0, 0), music, font=music_font)[2]
    d.text(((W - music_w) / 2, MUSIC_Y), music, font=music_font,
           fill=(*MUSIC_RGBA[:3], round(MUSIC_RGBA[3] * alpha)))
    d.line(DIVIDER, fill=(*DIVIDER_RGBA[:3], round(DIVIDER_RGBA[3] * alpha)), width=2)
    return cv2.cvtColor(np.asarray(Image.alpha_composite(base, overlay).convert("RGB")),
                        cv2.COLOR_RGB2BGR)


def cover(frame: np.ndarray, artist: str, composer: str) -> np.ndarray:
    """Stessa identica tipografia anche per il JPG di copertina."""
    return signature(frame, 0.0, artist, composer, force_visible=True)
