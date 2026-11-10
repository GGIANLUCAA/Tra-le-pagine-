#!/usr/bin/env python3
"""Experimental, deterministic camera directing with actual WAV chapter intervals.

No scene invention: ONLY uses recipe camera anchors already declared by its author.
The progression changes from mechanical continuous zoom to justified locked holds
and bounded, one-direction moves. Can only be used for a separate review render.
This is not human artwork/subject approval.
"""
from __future__ import annotations
import json
import math
from pathlib import Path

MODES = ("locked", "hold_push", "hold_pull", "hold_pan_left", "hold_pan_right")
# Chosen from the declared nine source focus targets (not semantic AI detection).
# V144 chapter IDs 1-9; the three global overviews are handled by the renderer.
BRUEGEL_MODES = {
    0: "hold_push", 1: "locked", 2: "hold_push", 3: "hold_pan_left",
    4: "locked", 5: "hold_pull", 6: "hold_push", 7: "hold_pan_right",
    8: "locked"
}


def number(value):
    return type(value) in (float, int) and math.isfinite(value)


def smooth_progress(u, start=.24, finish=.77):
    """Cubic smoothstep; truly locked before/after movement."""
    if not number(u) or not (0 <= start < finish <= 1):
        raise ValueError("Invalid camera progress")
    z = max(0., min(1., (u-start)/(finish-start)))
    return z*z*(3-2*z)


def crop_camera(recipe, progress, image_width, image_height, frame_width, frame_height,
                mode, *, pixel_scale_limit=1.55):
    """Return raw image crop at a verified recipe anchor; never stretch or pan outside image.

    "Verified recipe" refers to the preexisting camera target, not proof that
    the painting actually contains the subject described in a script.
    """
    if mode not in MODES:
        raise ValueError("Unsupported camera movement")
    if not number(progress) or not 0 <= progress <= 1:
        raise ValueError("Progress out of bounds")
    if not all(type(x) is int and x > 0 for x in
               (image_width,image_height,frame_width,frame_height)):
        raise ValueError("Invalid image dimensions")
    x, y, h = recipe["cx"], recipe["cy"], recipe["crop_height_px"]
    if not (number(x) and number(y) and number(h) and 0 <= x <= 1 and 0 <= y <= 1 and h > 0):
        raise ValueError("Camera anchor invalid")
    if not number(pixel_scale_limit) or pixel_scale_limit < 1:
        raise ValueError("Invalid pixel scale budget")

    # Explicitly allow a little upscaling; don't describe it as native 4K.
    min_height = max(frame_height / pixel_scale_limit,
                     (frame_width / pixel_scale_limit) * frame_height / frame_width)
    base_height = max(float(h), min_height)
    if base_height > image_height or base_height * frame_width / frame_height > image_width:
        raise ValueError("Cannot make a readable output crop from source pixels")
    p = smooth_progress(progress)
    if mode == "locked":
        scale = 1.
    elif mode == "hold_push":
        scale = 1.0 - .038*p
    elif mode == "hold_pull":
        scale = .962 + .038*p
    else:
        scale = 1.
    crop_height = int(round(max(min_height, base_height*scale)))
    crop_width = int(round(crop_height*frame_width/frame_height))
    if crop_width > image_width:
        raise ValueError("Crop out of bounds horizontally")
    pan = .014*p if mode == "hold_pan_right" else (-.014*p if mode == "hold_pan_left" else 0.)
    cx = int(round(image_width*(x+pan)))
    cy = int(round(image_height*y))
    x0 = max(0, min(image_width-crop_width, cx-crop_width//2))
    y0 = max(0, min(image_height-crop_height, cy-crop_height//2))
    return (x0, y0, x0+crop_width, y0+crop_height)


def chapter_plan(chapters, chapter_ends_s, *, voice_offset_s, wav_sha256,
                 source_sha256, modes=None):
    """Actual chapter ends from ASR-aligned existing WAV, never word-rate guesses."""
    modes = BRUEGEL_MODES if modes is None else modes
    if not isinstance(chapters, list) or not chapters:
        raise ValueError("Missing chapter descriptions")
    if (not isinstance(chapter_ends_s, list) or len(chapter_ends_s)!=len(chapters)
            or not number(voice_offset_s) or voice_offset_s < 0):
        raise ValueError("Real ASR-aligned chapter times required")
    if not all(isinstance(x, str) and len(x)==64 and
               set(x).issubset(set("0123456789abcdef")) for x in (wav_sha256,source_sha256)):
        raise ValueError("Verified source and voice SHA256 required")
    prev = 0.
    shots=[]
    for idx,(ch,end) in enumerate(zip(chapters,chapter_ends_s)):
        if not number(end) or end<=prev or not isinstance(ch,dict):
            raise ValueError("Invalid ordered chapter time")
        mode=modes.get(idx)
        if mode not in MODES:
            raise ValueError("Missing directed mode")
        if not isinstance(ch.get("focus"),str) or not ch["focus"].strip():
            raise ValueError("Missing actual recipe focus reason")
        shots.append({
            "chapter_index":idx,
            "start_s":round(voice_offset_s+prev,4),
            "end_s":round(voice_offset_s+end,4),
            "focus_from_original_recipe":ch["focus"],
            "mode":mode,
            "motion": "one_direction_smoothstep_hold" if mode!="locked" else "locked",
            "semantic_subject_verified_from_real_frame":False,
            "movie_artistic_review": "PENDING"
        })
        prev=end
    return {
        "schema":"artvision-critico-directed-camera-trial-v2",
        "voice_sha256":wav_sha256, "artwork_sha256":source_sha256,
        "source_timing":"asr_aligned_existing_wav",
        "chapters":shots,
        "output":"SEPARATE_TEST_ONLY",
        "changes_narration":False,"edits_previous_mp4":False,
        "can_publish":False,"artistic_approved":False
    }
