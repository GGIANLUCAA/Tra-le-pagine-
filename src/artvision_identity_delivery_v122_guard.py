#!/usr/bin/env python3
"""Fail-closed ArtVision 4x1 final-handoff checks; no render or publication.

This does NOT recognize images or certify aesthetics. It requires a reviewer
to attest to the actual MP4/cover/post hashes, with concrete observations.
Review-only packages remain possible without these claims.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = {
    "cinema_standard": "modules/artvision/IDENTITA_VISIVA_FISSA_V6.json",
    "cinema_museum": "modules/artvision/IDENTITA_VISIVA_FISSA_V6.json",
    "critico_standard": "modules/artvision_critico/GUIDA_STILE_PERMANENTE_SERIE.md",
    "critico_museum": "modules/artvision_critico/GUIDA_STILE_PERMANENTE_SERIE.md",
}
SOCIAL = ("facebook", "instagram", "tiktok", "youtube")
REQUIRED_TRUE = (
    "english_title_readable_in_actual_video",
    "cover_matches_frozen_series_reference",
    "title_typography_matches_frozen_series_reference",
    "four_social_captions_checked_for_this_artwork",
)
MUSEUM_TRUE = (
    "artwork_remains_inside_frame_at_gallery_shots",
    "frame_only_at_museum_entry_and_exit",
    "physical_artwork_scale_verified",
    "same_room_and_frame_in_final_return",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_final_handoff(recipe: dict, review: dict, video_hash: str,
                        cover_hash: str, social_hashes: dict) -> list[str]:
    """Validate traceable attestations; never infer real visual quality from booleans."""
    errors = []
    if not isinstance(recipe, dict):
        return ["V122: ricetta di produzione JSON mancante"]
    variant = recipe.get("variant")
    if variant not in TEMPLATES:
        return ["V122: variante ArtVision non identificata"]
    title = recipe.get("title_en") or recipe.get("title")
    if not isinstance(title, str) or len(title.strip()) < 3:
        errors.append("V122: titolo inglese dell'opera mancante nella ricetta")
    if not isinstance(review, dict):
        return errors + ["V122: verifica editoriale/visiva vincolata agli hash mancante"]
    expected_template = TEMPLATES[variant]
    template_file = ROOT / expected_template
    if not template_file.is_file():
        errors.append("V122: riferimento grafico fisso non disponibile")
    elif review.get("template_sha256") != sha256(template_file):
        errors.append("V122: riferimento grafico non corrisponde al preset approvato")
    if review.get("template_path") != expected_template:
        errors.append("V122: template non è quello fisso della serie")
    if review.get("video_sha256") != video_hash:
        errors.append("V122: controllo non riferito al vero MP4")
    if review.get("cover_sha256") != cover_hash:
        errors.append("V122: copertina non verificata rispetto al JPEG reale")
    if review.get("social_sha256") != social_hashes:
        errors.append("V122: post social mancanti, cambiati o non verificati")
    if review.get("artwork_title_en") != title or review.get("title_language") != "en":
        errors.append("V122: titolo inglese diverso da quello documentato")
    if review.get("reviewer") not in ("human", "agent"):
        errors.append("V122: revisore visivo/editoriale non identificato")
    note = review.get("specific_visual_observation")
    if not isinstance(note, str) or len(note.strip()) < 45:
        errors.append("V122: osservazione visiva concreta non documentata")
    social_note = review.get("specific_social_observation")
    if not isinstance(social_note, str) or len(social_note.strip()) < 35:
        errors.append("V122: revisione reale dei quattro testi social non documentata")
    frames = review.get("reviewed_video_timecodes_seconds")
    if (not isinstance(frames, list) or len(frames) < 3
            or any(type(x) not in (int, float) or x < 0 for x in frames)):
        errors.append("V122: mancano almeno tre momenti del video effettivamente visionati")
    for field in REQUIRED_TRUE:
        if review.get(field) is not True:
            errors.append("V122: controllo mancante " + field)
    if variant.endswith("_museum"):
        for field in MUSEUM_TRUE:
            if review.get(field) is not True:
                errors.append("V122: Museum non verificato " + field)
    return errors
