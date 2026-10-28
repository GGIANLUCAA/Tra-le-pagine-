#!/usr/bin/env python3
"""ArtVision 4x1 offline storyboard preflight (no render, providers, or spending).

Validates a *plan*, never its artistic merit. A passing plan is not a
completed video, reviewed MP4, or an approval to publish.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

SCHEMA = "artvision-4x1-v1"
VARIANTS = {
    "critico_standard": ("critico", "standard"),
    "critico_museum": ("critico", "museum"),
    "cinema_standard": ("cinema", "standard"),
    "cinema_museum": ("cinema", "museum"),
}
GALLERY_KINDS = {"gallery_entry", "gallery_exit"}
PLACEHOLDERS = {"", "todo", "tbd", "unknown", "n/a", "zoom", "wow", "epico", "placeholder"}


def meaningful(value, min_length=6):
    return (isinstance(value, str) and len(value.strip()) >= min_length
            and value.strip().lower() not in PLACEHOLDERS)


def positive_number(value):
    return (not isinstance(value, bool) and isinstance(value, (float, int))
            and math.isfinite(value) and value > 0)


def new_plan(topic, artist):
    """Make a blank dossier, never fabricated research or approvals."""
    if not meaningful(topic, 2) or not meaningful(artist, 2):
        raise ValueError("Opera e artista obbligatori")
    variants = {}
    for name, (fmt, mode) in VARIANTS.items():
        variants[name] = {
            "format": fmt, "mode": mode, "variation_reason": "",
            "scenes": [], "status": "planned",
            "opening_0_7": {
                "first_frame_title_artist": "",
                "first_frame_visual": "",
                "first_3_seconds_hook": "",
                "seconds_3_to_7_reveal": "",
                "detail_id": "",
                "mobile_composition_reason": "",
                "audio_or_voice_cue": "",
                "qa_status": "pending_visual_review",
            },
        }
        if mode == "museum":
            variants[name]["museum"] = {
                "width_cm": None, "height_cm": None, "dimensions_source": "",
                "frame_status": "", "gallery_id": "", "entrance_plan": "",
                "exit_same_gallery_plan": "", "scene_is_reconstruction": True,
            }
    return {
        "schema": SCHEMA, "topic": topic.strip(), "artist": artist.strip(),
        "research_status": "pending",
        "emotional_direction": {
            "central_tension": "", "intended_feeling": [],
            "evidence_details": [], "reveal_order": [],
            "opening_hook": "", "closing_payoff": "",
            "wow_justification": "",
        },
        "variants": variants,
        "learning": {
            "previous_reference": "", "experiment_variable": "",
            "expected_improvement": "", "post_render_review": "pending",
        },
        "approval": {"artistic_status": "pending", "user_approval": False},
    }


def validate(plan):
    """Return blockers; never mark a video approved or claim it was watched."""
    errors = []

    def need(ok, message):
        if not ok:
            errors.append(message)

    if not isinstance(plan, dict):
        return ["Il piano 4x1 deve essere un oggetto JSON"]
    need(plan.get("schema") == SCHEMA, f"schema richiesto: {SCHEMA}")
    for field in ("topic", "artist"):
        need(meaningful(plan.get(field), 2), f"Opera: {field} mancante")
    d = plan.get("emotional_direction")
    if not isinstance(d, dict):
        d = {}
        errors.append("emotional_direction mancante")
    need(meaningful(d.get("central_tension"), 20),
         "Definire tensione centrale concreta del quadro")
    feelings = d.get("intended_feeling")
    need(isinstance(feelings, list) and 1 <= len(feelings) <= 2
         and all(meaningful(x, 3) for x in feelings)
         and len(set(feelings)) == len(feelings),
         "Indicare una o due emozioni distinte e motivate")
    details = d.get("evidence_details")
    if not isinstance(details, list):
        details = []
    need(len(details) >= 3, "Servono almeno tre particolari specifici dell'opera")
    ids = set()
    for i, detail in enumerate(details, 1):
        item = detail if isinstance(detail, dict) else {}
        ident = item.get("id")
        need(isinstance(ident, str) and meaningful(ident, 1),
             f"Dettaglio {i}: id mancante")
        if isinstance(ident, str) and ident.strip():
            need(ident not in ids, f"Dettaglio {i}: id duplicato {ident}")
            ids.add(ident)
        for field, minlen in (("location", 6), ("observation", 12),
                              ("significance", 20), ("image_source", 8)):
            need(meaningful(item.get(field), minlen),
                 f"Dettaglio {i}: {field} non documentato")
        need(item.get("claim_type") in ("documented", "interpretation"),
             f"Dettaglio {i}: distinguere documentazione e interpretazione")
    order = d.get("reveal_order")
    need(isinstance(order, list) and len(order) >= 3
         and all(isinstance(x, str) and x in ids for x in order)
         and len(set(x for x in order if isinstance(x, str))) == len(order),
         "reveal_order: almeno tre dettagli validi, diversi, in ordine motivato")
    for field in ("opening_hook", "closing_payoff", "wow_justification"):
        need(meaningful(d.get(field), 20), f"Direzione emotiva: {field} insufficiente")
    variants = plan.get("variants")
    if not isinstance(variants, dict):
        variants = {}
        errors.append("variants deve essere un oggetto")
    need(set(variants) == set(VARIANTS),
         "Esattamente quattro varianti ArtVision, senza aggiunte o omissioni")
    spoken_sequences = {}
    for name, (fmt, mode) in VARIANTS.items():
        variant = variants.get(name)
        if not isinstance(variant, dict):
            errors.append(f"{name}: variante mancante")
            continue
        need(variant.get("format") == fmt and variant.get("mode") == mode,
             f"{name}: formato o tipo ingresso errato")
        need(meaningful(variant.get("variation_reason"), 20),
             f"{name}: motivare la differenza artistica")
        # V55: the first seven seconds must have a meaningful artwork-specific
        # visual hook. This is a storyboard gate, NOT video/image recognition.
        opening = variant.get("opening_0_7")
        if not isinstance(opening, dict):
            opening = {}
        for field, minimum in (
            ("first_frame_title_artist", 8),
            ("first_frame_visual", 20),
            ("first_3_seconds_hook", 20),
            ("seconds_3_to_7_reveal", 20),
            ("mobile_composition_reason", 18),
            ("audio_or_voice_cue", 18),
        ):
            need(meaningful(opening.get(field), minimum),
                 f"{name}: opening_0_7 {field} non studiato")
        need(opening.get("detail_id") in ids if isinstance(opening.get("detail_id"), str) else False,
             f"{name}: opening_0_7 deve usare un dettaglio autentico del quadro")
        need(opening.get("qa_status", "pending_visual_review") in
             ("pending_visual_review", "reviewed_on_real_frames"),
             f"{name}: stato revisione apertura non valido")
        scenes = variant.get("scenes")
        if not isinstance(scenes, list):
            scenes = []
        need(len(scenes) >= 3, f"{name}: almeno tre scene significative")
        scene_details, spoken = [], []
        gallery_events = []
        for i, scene in enumerate(scenes, 1):
            if not isinstance(scene, dict):
                errors.append(f"{name} scena {i}: oggetto non valido")
                continue
            kind = scene.get("kind", "detail")
            if kind in GALLERY_KINDS:
                gallery_events.append((i, kind))
                need(mode == "museum",
                     f"{name} scena {i}: ingresso/uscita museo nel formato Standard")
            else:
                ref = scene.get("detail_id")
                need(isinstance(ref, str) and ref in ids,
                     f"{name} scena {i}: dettaglio non presente nella ricerca")
                if isinstance(ref, str):
                    scene_details.append(ref)
            for field, minlen in (("purpose", 18), ("movement", 8),
                                  ("emotional_effect", 12)):
                need(meaningful(scene.get(field), minlen),
                     f"{name} scena {i}: {field} troppo generico")
            need(positive_number(scene.get("duration_seconds")),
                 f"{name} scena {i}: durata positiva e motivata obbligatoria")
            if fmt == "critico":
                line = scene.get("spoken_line")
                if kind not in GALLERY_KINDS:
                    need(meaningful(line, 12),
                         f"{name} scena {i}: frase reale del critico mancante")
                if isinstance(line, str) and line.strip():
                    spoken.append(line.strip())
            else:
                need(not scene.get("spoken_line"),
                     f"{name} scena {i}: Cinema deve restare senza voce")
        need(len(set(scene_details)) >= 3,
             f"{name}: mostrare almeno tre dettagli realmente differenti")
        if fmt == "critico":
            spoken_sequences[name] = spoken
        if mode == "museum":
            kinds = [k for _, k in gallery_events]
            need(kinds == ["gallery_entry", "gallery_exit"],
                 f"{name}: serve ingresso e ritorno finale allo stesso museo")
            if gallery_events and scenes:
                need(gallery_events[0][0] == 1
                     and gallery_events[-1][0] == len(scenes),
                     f"{name}: ingresso iniziale e uscita finale richiesti")
            m = variant.get("museum")
            if not isinstance(m, dict):
                m = {}
            for field in ("dimensions_source", "frame_status", "gallery_id",
                          "entrance_plan", "exit_same_gallery_plan"):
                need(meaningful(m.get(field), 8),
                     f"{name}: dati Museum {field} mancanti")
            for field in ("width_cm", "height_cm"):
                need(positive_number(m.get(field)),
                     f"{name}: {field} misura museale verificata mancante")
            need(m.get("scene_is_reconstruction") in (True, False),
                 f"{name}: dichiarare se sala ricostruita")
        else:
            need(not gallery_events, f"{name}: scene museo nel formato Standard")
    a = spoken_sequences.get("critico_standard")
    b = spoken_sequences.get("critico_museum")
    if a is not None and b is not None:
        need(bool(a) and a == b,
             "I due Critico devono usare lo stesso identico testo narrato")
    # Ensure no false finality is accidentally encoded at the planning stage.
    for name, variant in variants.items():
        if isinstance(variant, dict):
            need(variant.get("status", "planned") in
                 ("planned", "blocked", "rendered_needs_review", "approved_for_final_delivery"),
                 f"{name}: stato non riconosciuto")
            if variant.get("status") == "approved_for_final_delivery":
                need(bool(variant.get("reviewed_mp4_sha256"))
                     and variant.get("human_artistic_approval") is True,
                     f"{name}: nessuna approvazione finale senza revisione umana del file")
    return errors


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    commands = ap.add_subparsers(dest="command")
    init = commands.add_parser("init", help="Create a blank 4x1 dossier, no fake research")
    init.add_argument("--topic", required=True)
    init.add_argument("--artist", required=True)
    init.add_argument("--out", required=True, type=Path)
    check = commands.add_parser("check", help="Structural pre-render gate")
    check.add_argument("plan", type=Path)
    # Accept historical call style: python file.py PLAN.json
    argv = sys.argv[1:]
    if argv and argv[0] not in ("init", "check", "-h", "--help"):
        argv = ["check"] + argv
    args = ap.parse_args(argv)
    if args.command == "init":
        if args.out.exists():
            ap.error("Destinazione già esistente: non sovrascrivere")
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(new_plan(args.topic, args.artist),
                                       ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(str(args.out))
        return
    target = args.plan
    errors = validate(json.loads(target.read_text(encoding="utf-8")))
    print(json.dumps({"schema": "artvision-4x1-preflight-v1",
                      "passed": not errors, "blockers": errors,
                      "artistic_quality_certified": False,
                      "rendered_video_verified": False},
                     ensure_ascii=False, indent=2))
    raise SystemExit(2 if errors else 0)


if __name__ == "__main__":
    main()
